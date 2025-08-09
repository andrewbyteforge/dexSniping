"""
Blockchain Network Manager
File: app/core/blockchain/network_manager.py
Class: NetworkManager
Methods: connect_to_network, get_network_config, check_network_health, switch_network

Live blockchain integration for connecting to real Ethereum/Polygon/BSC nodes.
This replaces the mock data from Phase 4A with real blockchain connectivity.
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager

from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider, WebsocketProvider
from web3.exceptions import Web3Exception
import requests

from app.utils.logger import setup_logger
from app.core.exceptions import (
    TradingError, 
    NetworkError, 
    ConnectionError, 
    InsufficientFundsError
)

logger = setup_logger(__name__, "application")


class NetworkType(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon" 
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    BASE = "base"


class ProviderType(str, Enum):
    """Provider types for blockchain connection."""
    INFURA = "infura"
    ALCHEMY = "alchemy"
    QUICKNODE = "quicknode"
    MORALIS = "moralis"
    PUBLIC_RPC = "public_rpc"
    LOCAL_NODE = "local_node"


@dataclass
class NetworkConfig:
    """Network configuration data structure."""
    network_type: NetworkType
    name: str
    chain_id: int
    native_currency: str
    currency_symbol: str
    currency_decimals: int
    rpc_urls: List[str]
    websocket_urls: List[str]
    explorer_url: str
    is_testnet: bool = False
    gas_price_oracle_url: Optional[str] = None
    max_gas_price_gwei: int = 100
    block_time_seconds: float = 12.0
    
    @property
    def is_layer2(self) -> bool:
        """Check if this is a Layer 2 network."""
        return self.network_type in [
            NetworkType.POLYGON, 
            NetworkType.ARBITRUM, 
            NetworkType.OPTIMISM,
            NetworkType.BASE
        ]


@dataclass 
class NetworkStatus:
    """Network health and status information."""
    network_type: NetworkType
    is_connected: bool
    latest_block: int
    gas_price_gwei: float
    response_time_ms: float
    provider_type: ProviderType
    last_checked: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class NetworkManager:
    """
    Manages blockchain network connections and interactions.
    
    Provides connection to multiple blockchain networks with automatic
    failover, health monitoring, and optimized RPC endpoint selection.
    """
    
    def __init__(self):
        """Initialize the network manager."""
        self.connections: Dict[NetworkType, AsyncWeb3] = {}
        self.network_configs: Dict[NetworkType, NetworkConfig] = {}
        self.network_status: Dict[NetworkType, NetworkStatus] = {}
        self.primary_providers: Dict[NetworkType, str] = {}
        self.backup_providers: Dict[NetworkType, List[str]] = {}
        self._health_check_interval = 30  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Initialize network configurations
        self._setup_network_configs()
        
        # Load API keys from environment
        self._load_api_keys()
    
    def _setup_network_configs(self) -> None:
        """Set up network configurations for all supported chains."""
        self.network_configs = {
            NetworkType.ETHEREUM: NetworkConfig(
                network_type=NetworkType.ETHEREUM,
                name="Ethereum Mainnet",
                chain_id=1,
                native_currency="Ethereum",
                currency_symbol="ETH",
                currency_decimals=18,
                rpc_urls=[
                    "https://mainnet.infura.io/v3/{api_key}",
                    "https://eth-mainnet.alchemyapi.io/v2/{api_key}",
                    "https://eth-mainnet.g.alchemy.com/v2/{api_key}",
                    "https://eth.llamarpc.com",
                    "https://ethereum.publicnode.com"
                ],
                websocket_urls=[
                    "wss://mainnet.infura.io/ws/v3/{api_key}",
                    "wss://eth-mainnet.alchemyapi.io/v2/{api_key}"
                ],
                explorer_url="https://etherscan.io",
                gas_price_oracle_url="https://ethgasstation.info/json/ethgasAPI.json",
                max_gas_price_gwei=200,
                block_time_seconds=12.0
            ),
            
            NetworkType.POLYGON: NetworkConfig(
                network_type=NetworkType.POLYGON,
                name="Polygon Mainnet",
                chain_id=137,
                native_currency="Polygon",
                currency_symbol="MATIC",
                currency_decimals=18,
                rpc_urls=[
                    "https://polygon-mainnet.infura.io/v3/{api_key}",
                    "https://polygon-mainnet.g.alchemy.com/v2/{api_key}",
                    "https://polygon-rpc.com",
                    "https://rpc-mainnet.matic.network",
                    "https://matic-mainnet.chainstacklabs.com"
                ],
                websocket_urls=[
                    "wss://polygon-mainnet.infura.io/ws/v3/{api_key}",
                    "wss://polygon-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                explorer_url="https://polygonscan.com",
                max_gas_price_gwei=500,
                block_time_seconds=2.0
            ),
            
            NetworkType.BSC: NetworkConfig(
                network_type=NetworkType.BSC,
                name="Binance Smart Chain",
                chain_id=56,
                native_currency="Binance Coin",
                currency_symbol="BNB",
                currency_decimals=18,
                rpc_urls=[
                    "https://bsc-dataseed.binance.org",
                    "https://bsc-dataseed1.defibit.io",
                    "https://bsc-dataseed1.ninicoin.io",
                    "https://bsc.publicnode.com"
                ],
                websocket_urls=[
                    "wss://bsc-ws-node.nariox.org:443"
                ],
                explorer_url="https://bscscan.com",
                max_gas_price_gwei=20,
                block_time_seconds=3.0
            ),
            
            NetworkType.ARBITRUM: NetworkConfig(
                network_type=NetworkType.ARBITRUM,
                name="Arbitrum One",
                chain_id=42161,
                native_currency="Ethereum",
                currency_symbol="ETH",
                currency_decimals=18,
                rpc_urls=[
                    "https://arbitrum-mainnet.infura.io/v3/{api_key}",
                    "https://arb-mainnet.g.alchemy.com/v2/{api_key}",
                    "https://arb1.arbitrum.io/rpc",
                    "https://arbitrum.publicnode.com"
                ],
                websocket_urls=[
                    "wss://arbitrum-mainnet.infura.io/ws/v3/{api_key}"
                ],
                explorer_url="https://arbiscan.io",
                max_gas_price_gwei=5,
                block_time_seconds=0.25
            )
        }
    
    def _load_api_keys(self) -> None:
        """Load API keys from environment variables."""
        self.api_keys = {
            ProviderType.INFURA: os.getenv("INFURA_API_KEY"),
            ProviderType.ALCHEMY: os.getenv("ALCHEMY_API_KEY"),
            ProviderType.QUICKNODE: os.getenv("QUICKNODE_API_KEY"),
            ProviderType.MORALIS: os.getenv("MORALIS_API_KEY")
        }
        
        # Log available providers
        available_providers = [
            provider.value for provider, key in self.api_keys.items() 
            if key is not None
        ]
        logger.info(f"🔗 Available API providers: {available_providers}")
    
    async def connect_to_network(
        self, 
        network_type: NetworkType,
        preferred_provider: Optional[ProviderType] = None
    ) -> bool:
        """
        Connect to a specific blockchain network.
        
        Args:
            network_type: The network to connect to
            preferred_provider: Preferred RPC provider
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If unable to connect to any provider
        """
        try:
            logger.info(f"🔗 Connecting to {network_type.value}")
            
            config = self.network_configs.get(network_type)
            if not config:
                raise ConnectionError(f"Unsupported network: {network_type}")
            
            # Try to connect using available providers
            connection = await self._establish_connection(config, preferred_provider)
            
            if connection:
                self.connections[network_type] = connection
                await self._update_network_status(network_type, True)
                logger.info(f"✅ Connected to {network_type.value}")
                return True
            else:
                await self._update_network_status(network_type, False, "No providers available")
                raise ConnectionError(f"Failed to connect to {network_type.value}")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to {network_type.value}: {e}")
            await self._update_network_status(network_type, False, str(e))
            raise ConnectionError(f"Network connection failed: {e}")
    
    async def _establish_connection(
        self, 
        config: NetworkConfig,
        preferred_provider: Optional[ProviderType] = None
    ) -> Optional[AsyncWeb3]:
        """Establish connection with provider fallback."""
        # Build list of RPC URLs with API keys
        rpc_urls = []
        
        # Add provider-specific URLs first if we have API keys
        if preferred_provider and self.api_keys.get(preferred_provider):
            for url in config.rpc_urls:
                if "{api_key}" in url:
                    formatted_url = url.format(api_key=self.api_keys[preferred_provider])
                    rpc_urls.append(formatted_url)
        
        # Add all other provider URLs
        for provider, api_key in self.api_keys.items():
            if provider != preferred_provider and api_key:
                for url in config.rpc_urls:
                    if "{api_key}" in url:
                        formatted_url = url.format(api_key=api_key)
                        rpc_urls.append(formatted_url)
        
        # Add public RPC URLs as fallback
        for url in config.rpc_urls:
            if "{api_key}" not in url:
                rpc_urls.append(url)
        
        # Try each URL until one works
        for rpc_url in rpc_urls:
            try:
                logger.info(f"🔄 Trying RPC: {rpc_url[:50]}...")
                
                # Create Web3 instance
                provider = HTTPProvider(rpc_url, request_kwargs={'timeout': 10})
                web3 = AsyncWeb3(provider)
                
                # Add PoA middleware for networks that need it
                if config.network_type in [NetworkType.BSC, NetworkType.POLYGON]:
                    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                # Test connection
                latest_block = await web3.eth.block_number
                if latest_block > 0:
                    logger.info(f"✅ Connected via {rpc_url[:50]}... (block: {latest_block})")
                    return web3
                    
            except Exception as e:
                logger.warning(f"⚠️ RPC failed {rpc_url[:50]}...: {e}")
                continue
        
        return None
    
    async def _update_network_status(
        self, 
        network_type: NetworkType, 
        is_connected: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Update network status information."""
        try:
            latest_block = 0
            gas_price_gwei = 0.0
            response_time_ms = 0.0
            provider_type = ProviderType.PUBLIC_RPC
            
            if is_connected and network_type in self.connections:
                start_time = datetime.utcnow()
                web3 = self.connections[network_type]
                
                # Get latest block
                latest_block = await web3.eth.block_number
                
                # Get gas price
                gas_price_wei = await web3.eth.gas_price
                gas_price_gwei = float(web3.from_wei(gas_price_wei, 'gwei'))
                
                # Calculate response time
                end_time = datetime.utcnow()
                response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            self.network_status[network_type] = NetworkStatus(
                network_type=network_type,
                is_connected=is_connected,
                latest_block=latest_block,
                gas_price_gwei=gas_price_gwei,
                response_time_ms=response_time_ms,
                provider_type=provider_type,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to update network status for {network_type}: {e}")
    
    async def get_network_config(self, network_type: NetworkType) -> NetworkConfig:
        """Get network configuration."""
        config = self.network_configs.get(network_type)
        if not config:
            raise TradingError(f"Network {network_type} not supported")
        return config
    
    async def check_network_health(self, network_type: NetworkType) -> NetworkStatus:
        """Check health of a specific network."""
        if network_type not in self.connections:
            raise TradingError(f"Not connected to {network_type}")
        
        await self._update_network_status(network_type, True)
        return self.network_status[network_type]
    
    async def switch_network(self, network_type: NetworkType) -> bool:
        """Switch to a different network."""
        try:
            if network_type not in self.connections:
                success = await self.connect_to_network(network_type)
                if not success:
                    return False
            
            # Verify connection is still good
            web3 = self.connections[network_type]
            latest_block = await web3.eth.block_number
            
            if latest_block > 0:
                logger.info(f"🔄 Switched to {network_type.value} (block: {latest_block})")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to switch to {network_type}: {e}")
            return False
    
    async def get_web3_instance(self, network_type: NetworkType) -> AsyncWeb3:
        """Get Web3 instance for a network."""
        if network_type not in self.connections:
            success = await self.connect_to_network(network_type)
            if not success:
                raise ConnectionError(f"Unable to connect to {network_type}")
        
        return self.connections[network_type]
    
    async def get_native_balance(
        self, 
        network_type: NetworkType, 
        address: str
    ) -> Decimal:
        """Get native token balance for an address."""
        try:
            web3 = await self.get_web3_instance(network_type)
            balance_wei = await web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_eth))
            
        except Exception as e:
            logger.error(f"❌ Failed to get balance for {address}: {e}")
            raise TradingError(f"Balance check failed: {e}")
    
    async def get_token_balance(
        self, 
        network_type: NetworkType,
        token_address: str,
        wallet_address: str
    ) -> Decimal:
        """Get ERC20 token balance."""
        try:
            web3 = await self.get_web3_instance(network_type)
            
            # ERC20 balanceOf function signature
            balance_of_abi = [{
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }]
            
            contract = web3.eth.contract(
                address=web3.to_checksum_address(token_address),
                abi=balance_of_abi
            )
            
            balance = await contract.functions.balanceOf(
                web3.to_checksum_address(wallet_address)
            ).call()
            
            return Decimal(str(balance))
            
        except Exception as e:
            logger.error(f"❌ Failed to get token balance: {e}")
            raise TradingError(f"Token balance check failed: {e}")
    
    async def estimate_gas_price(self, network_type: NetworkType) -> Dict[str, int]:
        """Get current gas price estimates."""
        try:
            web3 = await self.get_web3_instance(network_type)
            current_gas_price = await web3.eth.gas_price
            current_gwei = int(web3.from_wei(current_gas_price, 'gwei'))
            
            # Provide fast/standard/safe options
            return {
                "fast": current_gwei + 5,
                "standard": current_gwei,
                "safe": max(1, current_gwei - 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate gas price: {e}")
            return {"fast": 20, "standard": 15, "safe": 10}
    
    async def start_health_monitoring(self) -> None:
        """Start periodic health check monitoring."""
        if self._health_check_task and not self._health_check_task.done():
            return  # Already running
        
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("🏥 Started network health monitoring")
    
    async def stop_health_monitoring(self) -> None:
        """Stop health check monitoring."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Stopped network health monitoring")
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while True:
            try:
                for network_type in self.connections.keys():
                    await self.check_network_health(network_type)
                
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def get_all_network_status(self) -> Dict[str, NetworkStatus]:
        """Get status of all networks."""
        return {
            network_type.value: status 
            for network_type, status in self.network_status.items()
        }
    
    async def disconnect_all(self) -> None:
        """Disconnect from all networks."""
        await self.stop_health_monitoring()
        
        for network_type in list(self.connections.keys()):
            try:
                # Close any active connections if needed
                del self.connections[network_type]
                logger.info(f"🔌 Disconnected from {network_type.value}")
            except Exception as e:
                logger.error(f"❌ Error disconnecting from {network_type}: {e}")
        
        self.connections.clear()
        self.network_status.clear()
        logger.info("🔌 Disconnected from all networks")


# Global network manager instance
_network_manager: Optional[NetworkManager] = None


def get_network_manager() -> NetworkManager:
    """Get the global network manager instance."""
    global _network_manager
    if _network_manager is None:
        _network_manager = NetworkManager()
    return _network_manager


# Context manager for network connections
@asynccontextmanager
async def network_connection(network_type: NetworkType):
    """Context manager for network connections."""
    manager = get_network_manager()
    try:
        await manager.connect_to_network(network_type)
        yield manager
    finally:
        # Connection cleanup is handled by the manager
        pass