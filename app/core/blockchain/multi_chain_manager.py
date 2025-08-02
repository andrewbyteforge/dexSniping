"""
Multi-chain manager for coordinating operations across multiple blockchain networks.
Handles chain initialization, health monitoring, and cross-chain operations.
"""

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from app.core.blockchain.base_chain import BaseChain, TokenInfo
from app.core.blockchain.chain_factory import ChainFactory, initialize_chain_factory
from app.core.blockchain.network_config import NetworkConfig
from app.utils.exceptions import ChainConnectionException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChainStatus(Enum):
    """Enumeration of chain connection statuses."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class ChainHealth:
    """Data class for chain health information."""
    network_name: str
    status: ChainStatus
    latest_block: Optional[int]
    last_checked: float
    error_message: Optional[str] = None


class MultiChainManager:
    """Multi-chain manager for coordinating blockchain operations."""
    
    def __init__(self):
        """Initialize the multi-chain manager."""
        self.chains: Dict[str, BaseChain] = {}
        self.chain_health: Dict[str, ChainHealth] = {}
        self.enabled_networks: Set[str] = set()
        self._shutdown = False
    
    async def initialize(self, networks: Optional[List[str]] = None) -> None:
        """Initialize chain connections."""
        logger.info("Initializing Multi-Chain Manager...")
        
        # Initialize chain factory
        initialize_chain_factory()
        
        # Determine which networks to initialize
        if networks is None:
            networks = NetworkConfig.get_all_networks()
        
        # Initialize chains
        successful = 0
        for network_name in networks:
            try:
                await self._initialize_chain(network_name)
                self.enabled_networks.add(network_name)
                successful += 1
            except Exception as e:
                logger.error(f"Failed to initialize {network_name}: {e}")
                self.chain_health[network_name] = ChainHealth(
                    network_name=network_name,
                    status=ChainStatus.ERROR,
                    latest_block=None,
                    last_checked=asyncio.get_event_loop().time(),
                    error_message=str(e)
                )
        
        logger.info(f"Successfully initialized {successful}/{len(networks)} chains")
    
    async def _initialize_chain(self, network_name: str) -> None:
        """Initialize a single chain connection."""
        try:
            logger.info(f"Initializing {network_name}...")
            
            # Update status to initializing
            self.chain_health[network_name] = ChainHealth(
                network_name=network_name,
                status=ChainStatus.INITIALIZING,
                latest_block=None,
                last_checked=asyncio.get_event_loop().time()
            )
            
            # Get network configuration
            network_config = NetworkConfig.get_network_config(network_name)
            
            # Create chain instance
            chain = await ChainFactory.create_chain(network_name, network_config)
            
            # Connect to the chain
            connected = await chain.connect()
            if not connected:
                raise ChainConnectionException(f"Failed to connect to {network_name}")
            
            # Store chain instance
            self.chains[network_name] = chain
            
            # Update health status
            latest_block = await chain.get_latest_block_number()
            self.chain_health[network_name] = ChainHealth(
                network_name=network_name,
                status=ChainStatus.CONNECTED,
                latest_block=latest_block,
                last_checked=asyncio.get_event_loop().time()
            )
            
            logger.info(f"Successfully initialized {network_name} (Block: {latest_block})")
            
        except Exception as e:
            logger.error(f"Failed to initialize {network_name}: {e}")
            raise
    
    async def get_chain(self, network_name: str) -> Optional[BaseChain]:
        """Get a chain instance by network name."""
        return self.chains.get(network_name)
    
    async def get_enabled_networks(self) -> Set[str]:
        """Get set of enabled network names."""
        return self.enabled_networks.copy()
    
    async def scan_all_chains_for_new_tokens(
        self,
        from_block_offset: int = 10
    ) -> Dict[str, List[TokenInfo]]:
        """Scan all enabled chains for new tokens."""
        all_new_tokens = {}
        
        for network_name in self.enabled_networks:
            chain = self.chains.get(network_name)
            if chain and chain.is_connected:
                try:
                    latest_block = await chain.get_latest_block_number()
                    from_block = max(0, latest_block - from_block_offset)
                    new_tokens = await chain.scan_new_tokens(from_block, latest_block)
                    all_new_tokens[network_name] = new_tokens
                    logger.info(f"Found {len(new_tokens)} new tokens on {network_name}")
                except Exception as e:
                    logger.error(f"Token scan failed for {network_name}: {e}")
                    all_new_tokens[network_name] = []
        
        total_tokens = sum(len(tokens) for tokens in all_new_tokens.values())
        logger.info(f"Found {total_tokens} new tokens across all chains")
        return all_new_tokens
    
    async def get_health_status(self) -> Dict[str, ChainHealth]:
        """Get health status of all chains."""
        return self.chain_health.copy()
    
    async def close(self) -> None:
        """Close all chain connections."""
        logger.info("Shutting down Multi-Chain Manager...")
        
        for chain in self.chains.values():
            try:
                await chain.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting chain: {e}")
        
        self.chains.clear()
        self.enabled_networks.clear()
        logger.info("Multi-Chain Manager shutdown complete")