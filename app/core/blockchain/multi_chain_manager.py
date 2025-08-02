"""
File: app/core/blockchain/multi_chain_manager.py

Multi-chain manager for coordinating operations across multiple blockchain networks.
Handles chain initialization, health monitoring, and cross-chain operations.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from app.core.blockchain.base_chain import BaseChain, TokenInfo, LiquidityInfo
from app.core.blockchain.chain_factory import ChainFactory, initialize_chain_factory
from app.config import NetworkConfig, settings
from app.utils.exceptions import (
    ChainConnectionException, ChainNotSupportedException
)
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
    gas_price: Optional[float]
    rpc_url: Optional[str]
    last_checked: float
    error_message: Optional[str] = None


@dataclass
class CrossChainOpportunity:
    """Data class for cross-chain arbitrage opportunities."""
    token_address: str
    source_chain: str
    target_chain: str
    source_price: float
    target_price: float
    profit_percentage: float
    liquidity_usd: float
    gas_cost_estimate: float


class MultiChainManager:
    """
    Multi-chain manager for coordinating blockchain operations.
    
    Manages connections to multiple blockchain networks, monitors their health,
    and provides unified interfaces for cross-chain operations.
    """
    
    def __init__(self):
        """Initialize the multi-chain manager."""
        self.chains: Dict[str, BaseChain] = {}
        self.chain_health: Dict[str, ChainHealth] = {}
        self.enabled_networks: Set[str] = set()
        self.health_check_interval = 60  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        self._shutdown = False
    
    async def initialize(self, networks: Optional[List[str]] = None) -> None:
        """
        Initialize chain connections.
        
        Args:
            networks: List of networks to initialize (all if None)
        """
        logger.info("Initializing Multi-Chain Manager...")
        
        # Initialize chain factory
        initialize_chain_factory()
        
        # Determine which networks to initialize
        if networks is None:
            networks = NetworkConfig.get_all_networks()
        
        # Initialize chains
        initialization_tasks = []
        for network_name in networks:
            task = self._initialize_chain(network_name)
            initialization_tasks.append(task)
        
        # Wait for all initializations to complete
        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        # Process results
        successful = 0
        for network_name, result in zip(networks, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to initialize {network_name}: {result}")
                self.chain_health[network_name] = ChainHealth(
                    network_name=network_name,
                    status=ChainStatus.ERROR,
                    latest_block=None,
                    gas_price=None,
                    rpc_url=None,
                    last_checked=asyncio.get_event_loop().time(),
                    error_message=str(result)
                )
            else:
                successful += 1
                self.enabled_networks.add(network_name)
        
        logger.info(f"Successfully initialized {successful}/{len(networks)} chains")
        
        # Start health monitoring
        await self._start_health_monitoring()
    
    async def _initialize_chain(self, network_name: str) -> None:
        """
        Initialize a single chain connection.
        
        Args:
            network_name: Name of the network to initialize
        """
        try:
            logger.info(f"Initializing {network_name}...")
            
            # Update status to initializing
            self.chain_health[network_name] = ChainHealth(
                network_name=network_name,
                status=ChainStatus.INITIALIZING,
                latest_block=None,
                gas_price=None,
                rpc_url=None,
                last_checked=asyncio.get_event_loop().time()
            )
            
            # Create chain instance
            chain = await ChainFactory.create_chain(network_name)
            
            # Connect to the chain
            connected = await chain.connect()
            if not connected:
                raise ChainConnectionException(f"Failed to connect to {network_name}")
            
            # Store chain instance
            self.chains[network_name] = chain
            
            # Update health status
            health_info = await chain.health_check()
            self.chain_health[network_name] = ChainHealth(
                network_name=network_name,
                status=ChainStatus.CONNECTED,
                latest_block=health_info.get('latest_block'),
                gas_price=health_info.get('gas_price'),
                rpc_url=health_info.get('rpc_url'),
                last_checked=asyncio.get_event_loop().time()
            )
            
            logger.info(f"Successfully initialized {network_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize {network_name}: {e}")
            raise
    
    async def get_chain(self, network_name: str) -> Optional[BaseChain]:
        """
        Get a chain instance by network name.
        
        Args:
            network_name: Name of the network
            
        Returns:
            Chain instance or None if not available
        """
        return self.chains.get(network_name)
    
    async def get_all_chains(self) -> Dict[str, BaseChain]:
        """
        Get all available chain instances.
        
        Returns:
            Dictionary of network name to chain instance
        """
        return self.chains.copy()
    
    async def get_enabled_networks(self) -> Set[str]:
        """
        Get set of enabled network names.
        
        Returns:
            Set of enabled network names
        """
        return self.enabled_networks.copy()
    
    async def enable_network(self, network_name: str) -> bool:
        """
        Enable a specific network.
        
        Args:
            network_name: Name of the network to enable
            
        Returns:
            True if successfully enabled, False otherwise
        """
        if network_name in self.chains:
            self.enabled_networks.add(network_name)
            logger.info(f"Enabled network: {network_name}")
            return True
        
        try:
            await self._initialize_chain(network_name)
            self.enabled_networks.add(network_name)
            logger.info(f"Initialized and enabled network: {network_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable network {network_name}: {e}")
            return False
    
    async def disable_network(self, network_name: str) -> bool:
        """
        Disable a specific network.
        
        Args:
            network_name: Name of the network to disable
            
        Returns:
            True if successfully disabled, False otherwise
        """
        if network_name in self.enabled_networks:
            self.enabled_networks.discard(network_name)
            logger.info(f"Disabled network: {network_name}")
            return True
        return False
    
    async def scan_all_chains_for_new_tokens(
        self,
        from_block_offset: int = 10
    ) -> Dict[str, List[TokenInfo]]:
        """
        Scan all enabled chains for new tokens.
        
        Args:
            from_block_offset: Number of blocks back to scan from latest
            
        Returns:
            Dictionary of network name to list of new tokens
        """
        scan_tasks = []
        enabled_chains = []
        
        for network_name in self.enabled_networks:
            chain = self.chains.get(network_name)
            if chain and chain.is_connected:
                enabled_chains.append(network_name)
                task = self._scan_chain_for_tokens(chain, from_block_offset)
                scan_tasks.append(task)
        
        if not scan_tasks:
            logger.warning("No chains available for token scanning")
            return {}
        
        results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        all_new_tokens = {}
        for network_name, result in zip(enabled_chains, results):
            if isinstance(result, Exception):
                logger.error(f"Token scan failed for {network_name}: {result}")
                all_new_tokens[network_name] = []
            else:
                all_new_tokens[network_name] = result
        
        total_tokens = sum(len(tokens) for tokens in all_new_tokens.values())
        logger.info(f"Found {total_tokens} new tokens across all chains")
        
        return all_new_tokens
    
    async def _scan_chain_for_tokens(
        self,
        chain: BaseChain,
        from_block_offset: int
    ) -> List[TokenInfo]:
        """
        Scan a single chain for new tokens.
        
        Args:
            chain: Chain instance to scan
            from_block_offset: Number of blocks back to scan
            
        Returns:
            List of new tokens found
        """
        try:
            latest_block = await chain.get_latest_block_number()
            from_block = max(0, latest_block - from_block_offset)
            
            new_tokens = await chain.scan_new_tokens(from_block, latest_block)
            logger.info(f"Found {len(new_tokens)} new tokens on {chain.network_name}")
            
            return new_tokens
            
        except Exception as e:
            logger.error(f"Failed to scan {chain.network_name} for tokens: {e}")
            return []
    
    async def get_cross_chain_prices(self, token_addresses: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get prices for tokens across all chains.
        
        Args:
            token_addresses: List of token addresses to check
            
        Returns:
            Dictionary of token -> network -> price
        """
        price_tasks = []
        enabled_chains = []
        
        for network_name in self.enabled_networks:
            chain = self.chains.get(network_name)
            if chain and chain.is_connected:
                enabled_chains.append(network_name)
                task = self._get_chain_prices(chain, token_addresses)
                price_tasks.append(task)
        
        if not price_tasks:
            return {}
        
        results = await asyncio.gather(*price_tasks, return_exceptions=True)
        
        cross_chain_prices = {}
        for token_address in token_addresses:
            cross_chain_prices[token_address] = {}
        
        for network_name, result in zip(enabled_chains, results):
            if isinstance(result, Exception):
                logger.error(f"Price fetch failed for {network_name}: {result}")
                continue
            
            for token_address, price in result.items():
                if price is not None:
                    cross_chain_prices[token_address][network_name] = float(price)
        
        return cross_chain_prices
    
    async def _get_chain_prices(
        self,
        chain: BaseChain,
        token_addresses: List[str]
    ) -> Dict[str, Optional[float]]:
        """
        Get token prices on a single chain.
        
        Args:
            chain: Chain instance
            token_addresses: List of token addresses
            
        Returns:
            Dictionary of token address to price
        """
        prices = {}
        
        for token_address in token_addresses:
            try:
                price = await chain.get_token_price(token_address)
                prices[token_address] = float(price) if price else None
            except Exception as e:
                logger.error(f"Failed to get price for {token_address} on {chain.network_name}: {e}")
                prices[token_address] = None
        
        return prices
    
    async def find_arbitrage_opportunities(
        self,
        token_addresses: List[str],
        min_profit_percentage: float = 2.0
    ) -> List[CrossChainOpportunity]:
        """
        Find cross-chain arbitrage opportunities.
        
        Args:
            token_addresses: List of tokens to check
            min_profit_percentage: Minimum profit percentage to consider
            
        Returns:
            List of arbitrage opportunities
        """
        # Get prices across all chains
        cross_chain_prices = await self.get_cross_chain_prices(token_addresses)
        
        opportunities = []
        
        for token_address, chain_prices in cross_chain_prices.items():
            if len(chain_prices) < 2:
                continue  # Need at least 2 chains for arbitrage
            
            # Find highest and lowest prices
            sorted_prices = sorted(chain_prices.items(), key=lambda x: x[1])
            
            for i, (source_chain, source_price) in enumerate(sorted_prices[:-1]):
                for target_chain, target_price in sorted_prices[i+1:]:
                    profit_percentage = ((target_price - source_price) / source_price) * 100
                    
                    if profit_percentage >= min_profit_percentage:
                        # Get liquidity information
                        source_chain_obj = self.chains.get(source_chain)
                        if source_chain_obj:
                            liquidity_info = await source_chain_obj.get_token_liquidity(token_address)
                            total_liquidity = sum(
                                float(li.total_liquidity_usd) for li in liquidity_info
                            ) if liquidity_info else 0
                        else:
                            total_liquidity = 0
                        
                        opportunity = CrossChainOpportunity(
                            token_address=token_address,
                            source_chain=source_chain,
                            target_chain=target_chain,
                            source_price=source_price,
                            target_price=target_price,
                            profit_percentage=profit_percentage,
                            liquidity_usd=total_liquidity,
                            gas_cost_estimate=0  # Would calculate based on gas prices
                        )
                        opportunities.append(opportunity)
        
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        logger.info(f"Found {len(opportunities)} arbitrage opportunities")
        return opportunities
    
    async def get_health_status(self) -> Dict[str, ChainHealth]:
        """
        Get health status of all chains.
        
        Returns:
            Dictionary of network name to health status
        """
        return self.chain_health.copy()
    
    async def _start_health_monitoring(self) -> None:
        """Start background health monitoring task."""
        if self.health_check_task is None or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(self._health_monitor_loop())
            logger.info("Started health monitoring")
    
    async def _health_monitor_loop(self) -> None:
        """Background loop for monitoring chain health."""
        while not self._shutdown:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)  # Shorter delay on error
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all chains."""
        health_tasks = []
        
        for network_name, chain in self.chains.items():
            task = self._check_chain_health(network_name, chain)
            health_tasks.append(task)
        
        if health_tasks:
            await asyncio.gather(*health_tasks, return_exceptions=True)
    
    async def _check_chain_health(self, network_name: str, chain: BaseChain) -> None:
        """
        Check health of a single chain.
        
        Args:
            network_name: Name of the network
            chain: Chain instance
        """
        try:
            health_info = await chain.health_check()
            
            if health_info.get('status') == 'healthy':
                status = ChainStatus.CONNECTED
                error_message = None
            else:
                status = ChainStatus.ERROR
                error_message = health_info.get('error')
            
            self.chain_health[network_name] = ChainHealth(
                network_name=network_name,
                status=status,
                latest_block=health_info.get('latest_block'),
                gas_price=health_info.get('gas_price'),
                rpc_url=health_info.get('rpc_url'),
                last_checked=asyncio.get_event_loop().time(),
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Health check failed for {network_name}: {e}")
            self.chain_health[network_name] = ChainHealth(
                network_name=network_name,
                status=ChainStatus.ERROR,
                latest_block=None,
                gas_price=None,
                rpc_url=None,
                last_checked=asyncio.get_event_loop().time(),
                error_message=str(e)
            )
    
    async def close(self) -> None:
        """Close all chain connections and stop monitoring."""
        logger.info("Shutting down Multi-Chain Manager...")
        
        self._shutdown = True
        
        # Cancel health monitoring
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect all chains
        disconnect_tasks = []
        for chain in self.chains.values():
            task = chain.disconnect()
            disconnect_tasks.append(task)
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        self.chains.clear()
        self.enabled_networks.clear()
        
        logger.info("Multi-Chain Manager shutdown complete")