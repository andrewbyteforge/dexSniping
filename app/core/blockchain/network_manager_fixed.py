"""
Network Manager - Fixed RPC Authentication
File: app/core/blockchain/network_manager_fixed.py

Professional blockchain network manager with proper RPC fallback handling.
Fixes authentication issues by prioritizing public endpoints when API keys unavailable.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

try:
    from web3 import AsyncWeb3
    from web3.providers.async_rpc import AsyncHTTPProvider
    from web3.middleware import geth_poa_middleware
    WEB3_AVAILABLE = True
except ImportError:
    # Fallback for development without Web3
    WEB3_AVAILABLE = False
    AsyncWeb3 = None
    AsyncHTTPProvider = None
    geth_poa_middleware = None

from app.utils.logger import setup_logger
from app.core.exceptions import NetworkError, ConnectionError, RPCError

logger = setup_logger(__name__)


class NetworkType(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"


class ProviderType(str, Enum):
    """RPC provider types."""
    INFURA = "infura"
    ALCHEMY = "alchemy"
    QUICKNODE = "quicknode"
    MORALIS = "moralis"
    PUBLIC = "public"


@dataclass
class NetworkConfig:
    """Network configuration with RPC endpoints."""
    network_type: NetworkType
    name: str
    chain_id: int
    native_currency: str
    currency_symbol: str
    currency_decimals: int
    
    # Public RPC URLs (no API key required) - PRIORITIZE THESE
    public_rpc_urls: List[str]
    
    # Private RPC URLs (require API keys) - fallback only
    private_rpc_urls: List[str]
    
    explorer_url: str
    max_gas_price_gwei: float
    block_time_seconds: float


@dataclass
class NetworkStatus:
    """Network connection status."""
    network_type: NetworkType
    is_connected: bool
    latest_block: int = 0
    gas_price_gwei: float = 0.0
    response_time_ms: float = 0.0
    provider_url: str = ""
    last_checked: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class NetworkManagerFixed:
    """
    Fixed Network Manager with proper RPC fallback handling.
    
    Prioritizes public RPC endpoints to avoid authentication issues,
    only uses private endpoints when API keys are properly configured.
    """
    
    def __init__(self):
        """Initialize the network manager with proper fallback handling."""
        self.connections: Dict[NetworkType, AsyncWeb3] = {}
        self.network_configs: Dict[NetworkType, NetworkConfig] = {}
        self.network_status: Dict[NetworkType, NetworkStatus] = {}
        self.api_keys: Dict[ProviderType, Optional[str]] = {}
        
        # Initialize network configurations
        self._setup_network_configs()
        
        # Load API keys (optional)
        self._load_api_keys()
        
        logger.info("🔗 Network Manager initialized with public RPC priority")
    
    def _setup_network_configs(self) -> None:
        """Setup network configurations with public RPC priority."""
        self.network_configs = {
            NetworkType.ETHEREUM: NetworkConfig(
                network_type=NetworkType.ETHEREUM,
                name="Ethereum Mainnet",
                chain_id=1,
                native_currency="Ethereum",
                currency_symbol="ETH",  
                currency_decimals=18,
                # PUBLIC RPC URLs - NO API KEY REQUIRED (PRIORITY)
                public_rpc_urls=[
                    "https://eth.llamarpc.com",
                    "https://ethereum.publicnode.com",
                    "https://rpc.ankr.com/eth",
                    "https://eth-mainnet.public.blastapi.io",
                    "https://ethereum-rpc.publicnode.com",
                    "https://1rpc.io/eth",
                    "https://rpc.payload.de"
                ],
                # PRIVATE RPC URLs - REQUIRE API KEYS (FALLBACK ONLY)
                private_rpc_urls=[
                    "https://mainnet.infura.io/v3/{infura_key}",
                    "https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}",
                    "https://rpc.quicknode.pro/{quicknode_key}"
                ],
                explorer_url="https://etherscan.io",
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
                # PUBLIC RPC URLs - NO API KEY REQUIRED (PRIORITY)
                public_rpc_urls=[
                    "https://polygon-rpc.com",
                    "https://rpc-mainnet.matic.network",
                    "https://matic-mainnet.chainstacklabs.com",
                    "https://rpc-mainnet.maticvigil.com",
                    "https://polygon-mainnet.public.blastapi.io",
                    "https://polygon.llamarpc.com",
                    "https://1rpc.io/matic"
                ],
                # PRIVATE RPC URLs - REQUIRE API KEYS (FALLBACK ONLY) 
                private_rpc_urls=[
                    "https://polygon-mainnet.infura.io/v3/{infura_key}",
                    "https://polygon-mainnet.g.alchemy.com/v2/{alchemy_key}"
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
                # PUBLIC RPC URLs - NO API KEY REQUIRED (PRIORITY)
                public_rpc_urls=[
                    "https://bsc-dataseed.binance.org",
                    "https://bsc-dataseed1.defibit.io",
                    "https://bsc-dataseed1.ninicoin.io",
                    "https://bsc.publicnode.com",
                    "https://bsc-mainnet.public.blastapi.io",
                    "https://1rpc.io/bnb",
                    "https://bsc.rpc.blxrbdn.com"
                ],
                # PRIVATE RPC URLs - REQUIRE API KEYS (FALLBACK ONLY)
                private_rpc_urls=[
                    "https://proud-silent-river.bsc.quiknode.pro/{quicknode_key}/"
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
                # PUBLIC RPC URLs - NO API KEY REQUIRED (PRIORITY)
                public_rpc_urls=[
                    "https://arb1.arbitrum.io/rpc",
                    "https://arbitrum.publicnode.com",
                    "https://arbitrum-one.public.blastapi.io",
                    "https://1rpc.io/arb",
                    "https://arbitrum.llamarpc.com",
                    "https://rpc.arb1.arbitrum.gateway.fm"
                ],
                # PRIVATE RPC URLs - REQUIRE API KEYS (FALLBACK ONLY)
                private_rpc_urls=[
                    "https://arbitrum-mainnet.infura.io/v3/{infura_key}",
                    "https://arb-mainnet.g.alchemy.com/v2/{alchemy_key}"
                ],
                explorer_url="https://arbiscan.io",
                max_gas_price_gwei=5,
                block_time_seconds=0.25
            )
        }
    
    def _load_api_keys(self) -> None:
        """Load API keys from environment variables (optional)."""
        self.api_keys = {
            ProviderType.INFURA: os.getenv("INFURA_API_KEY"),
            ProviderType.ALCHEMY: os.getenv("ALCHEMY_API_KEY"),
            ProviderType.QUICKNODE: os.getenv("QUICKNODE_API_KEY"),
            ProviderType.MORALIS: os.getenv("MORALIS_API_KEY")
        }
        
        # Log available API keys (without exposing the keys)
        available_keys = [
            provider.value for provider, key in self.api_keys.items() 
            if key is not None and len(key) > 0
        ]
        
        if available_keys:
            logger.info(f"🔑 API keys available for: {available_keys}")
        else:
            logger.info("🔓 No API keys configured - using public RPC endpoints only")
    
    async def connect_to_network(self, network_type) -> bool:
        """
        Connect to a blockchain network with proper fallback handling.
        
        Args:
            network_type: The network to connect to (NetworkType enum or string)
            
        Returns:
            bool: True if connection successful
        """
        try:
            if not WEB3_AVAILABLE:
                logger.warning(f"⚠️ Web3 not available - cannot connect to {network_type}")
                return False
            
            # Handle string network types by trying to convert to enum
            if isinstance(network_type, str):
                try:
                    # Try to find matching NetworkType
                    network_type = NetworkType(network_type.lower())
                except ValueError:
                    logger.warning(f"⚠️ Unsupported network type: {network_type}")
                    return False
            
            # Validate that we have a proper NetworkType
            if not isinstance(network_type, NetworkType):
                logger.warning(f"⚠️ Invalid network type: {type(network_type)} - {network_type}")
                return False
            
            logger.info(f"🔗 Connecting to {network_type.value}...")
            
            config = self.network_configs.get(network_type)
            if not config:
                logger.warning(f"⚠️ No configuration found for network: {network_type.value}")
                return False
            
            # Try to establish connection with proper fallback
            connection = await self._establish_connection_with_fallback(config)
            
            if connection:
                self.connections[network_type] = connection
                await self._update_network_status(network_type, True, connection)
                logger.info(f"✅ Successfully connected to {network_type.value}")
                return True
            else:
                await self._update_network_status(network_type, False, None, "No working RPC endpoints")
                logger.warning(f"⚠️ Failed to connect to {network_type.value} - no working endpoints")
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"⚠️ Connection to {network_type} failed: {error_msg}")
            
            # Try to update status if we have a valid network type
            try:
                if isinstance(network_type, NetworkType):
                    await self._update_network_status(network_type, False, None, error_msg)
            except:
                pass  # Don't let status update failures break the method
                
            return False
    
    async def _establish_connection_with_fallback(self, config: NetworkConfig) -> Optional[AsyncWeb3]:
        """
        Establish connection with proper fallback priority.
        
        Tries public RPC endpoints first, then private endpoints with API keys.
        
        Args:
            config: Network configuration
            
        Returns:
            AsyncWeb3 connection or None
        """
        # PRIORITY 1: Try public RPC endpoints first (no authentication required)
        logger.info(f"🔓 Trying public RPC endpoints for {config.name}...")
        
        for i, rpc_url in enumerate(config.public_rpc_urls):
            try:
                logger.info(f"🔄 Testing public RPC #{i+1}: {rpc_url[:50]}...")
                
                connection = await self._test_rpc_connection(rpc_url, config)
                if connection:
                    logger.info(f"✅ Connected via public RPC: {rpc_url[:50]}...")
                    return connection
                    
            except Exception as e:
                logger.warning(f"⚠️ Public RPC #{i+1} failed: {str(e)[:100]}")
                continue
        
        # PRIORITY 2: Try private RPC endpoints with API keys (if available)
        if any(self.api_keys.values()):
            logger.info(f"🔑 Trying private RPC endpoints for {config.name}...")
            
            private_urls = self._build_private_rpc_urls(config.private_rpc_urls)
            
            for i, rpc_url in enumerate(private_urls):
                try:
                    logger.info(f"🔄 Testing private RPC #{i+1}: {rpc_url[:50]}...")
                    
                    connection = await self._test_rpc_connection(rpc_url, config)
                    if connection:
                        logger.info(f"✅ Connected via private RPC: {rpc_url[:50]}...")
                        return connection
                        
                except Exception as e:
                    logger.warning(f"⚠️ Private RPC #{i+1} failed: {str(e)[:100]}")
                    continue
        else:
            logger.info("🔓 No API keys available - skipping private RPC endpoints")
        
        # No working endpoints found
        logger.error(f"❌ No working RPC endpoints found for {config.name}")
        return None
    
    def _build_private_rpc_urls(self, url_templates: List[str]) -> List[str]:
        """Build private RPC URLs with API keys."""
        urls = []
        
        for template in url_templates:
            # Replace API key placeholders
            url = template
            
            if "{infura_key}" in url and self.api_keys.get(ProviderType.INFURA):
                urls.append(url.replace("{infura_key}", self.api_keys[ProviderType.INFURA]))
            
            if "{alchemy_key}" in url and self.api_keys.get(ProviderType.ALCHEMY):
                urls.append(url.replace("{alchemy_key}", self.api_keys[ProviderType.ALCHEMY]))
            
            if "{quicknode_key}" in url and self.api_keys.get(ProviderType.QUICKNODE):
                urls.append(url.replace("{quicknode_key}", self.api_keys[ProviderType.QUICKNODE]))
            
            if "{moralis_key}" in url and self.api_keys.get(ProviderType.MORALIS):
                urls.append(url.replace("{moralis_key}", self.api_keys[ProviderType.MORALIS]))
        
        return urls
    
    async def _test_rpc_connection(self, rpc_url: str, config: NetworkConfig) -> Optional[AsyncWeb3]:
        """
        Test a single RPC connection.
        
        Args:
            rpc_url: RPC endpoint URL
            config: Network configuration
            
        Returns:
            AsyncWeb3 connection if successful, None otherwise
        """
        try:
            # Create Web3 instance with timeout
            provider = AsyncHTTPProvider(rpc_url, request_kwargs={'timeout': 10})
            web3 = AsyncWeb3(provider)
            
            # Add PoA middleware for networks that need it
            if config.network_type in [NetworkType.BSC, NetworkType.POLYGON]:
                web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Test connection by getting latest block
            latest_block = await asyncio.wait_for(web3.eth.block_number, timeout=10)
            
            if latest_block > 0:
                # Verify chain ID matches
                chain_id = await asyncio.wait_for(web3.eth.chain_id, timeout=5)
                if chain_id == config.chain_id:
                    return web3
                else:
                    logger.warning(f"⚠️ Chain ID mismatch: expected {config.chain_id}, got {chain_id}")
                    return None
            else:
                logger.warning(f"⚠️ Invalid block number: {latest_block}")
                return None
                
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ RPC timeout: {rpc_url[:50]}...")
            return None
        except Exception as e:
            logger.warning(f"⚠️ RPC connection failed: {str(e)[:100]}")
            return None
    
    async def _update_network_status(
        self, 
        network_type: NetworkType, 
        is_connected: bool,
        connection: Optional[AsyncWeb3] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update network status information."""
        try:
            if is_connected and connection:
                # Get current block and other metrics
                latest_block = await connection.eth.block_number
                
                # Try to get gas price (may not be available on all networks)
                try:
                    gas_price_wei = await connection.eth.gas_price
                    gas_price_gwei = float(gas_price_wei) / 1e9
                except:
                    gas_price_gwei = 0.0
                
                self.network_status[network_type] = NetworkStatus(
                    network_type=network_type,
                    is_connected=True,
                    latest_block=latest_block,
                    gas_price_gwei=gas_price_gwei,
                    response_time_ms=0.0,  # TODO: Implement response time measurement
                    provider_url="connected",
                    last_checked=datetime.utcnow(),
                    error_message=None
                )
            else:
                self.network_status[network_type] = NetworkStatus(
                    network_type=network_type,
                    is_connected=False,
                    latest_block=0,
                    gas_price_gwei=0.0,
                    response_time_ms=0.0,
                    provider_url="none",
                    last_checked=datetime.utcnow(),
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to update network status: {e}")
    
    async def get_web3_instance(self, network_type: NetworkType) -> Optional[AsyncWeb3]:
        """
        Get Web3 instance for a network.
        
        Args:
            network_type: Network to get instance for
            
        Returns:
            AsyncWeb3 instance or None
        """
        return self.connections.get(network_type)
    
    async def disconnect_all(self) -> None:
        """Disconnect from all networks."""
        try:
            logger.info("🔌 Disconnecting from all networks...")
            
            for network_type in list(self.connections.keys()):
                try:
                    # Clean shutdown of connection
                    if self.connections[network_type]:
                        # AsyncWeb3 connections don't need explicit closing
                        pass
                    
                    del self.connections[network_type]
                    
                    # Update status
                    self.network_status[network_type] = NetworkStatus(
                        network_type=network_type,
                        is_connected=False,
                        last_checked=datetime.utcnow(),
                        error_message="Disconnected"
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Error disconnecting from {network_type.value}: {e}")
            
            logger.info("✅ Disconnected from all networks")
            
        except Exception as e:
            logger.error(f"❌ Error during disconnect_all: {e}")
    
    def get_network_status(self, network_type: NetworkType) -> Optional[NetworkStatus]:
        """Get status for a specific network."""
        return self.network_status.get(network_type)
    
    def get_all_network_status(self) -> Dict[NetworkType, NetworkStatus]:
        """Get status for all networks."""
        return self.network_status.copy()
    
    def is_connected(self, network_type: NetworkType) -> bool:
        """Check if connected to a specific network."""
        status = self.network_status.get(network_type)
        return status is not None and status.is_connected


# Global instance for the application
network_manager_instance: Optional[NetworkManagerFixed] = None


def get_network_manager() -> NetworkManagerFixed:
    """Get the global network manager instance."""
    global network_manager_instance
    
    if network_manager_instance is None:
        network_manager_instance = NetworkManagerFixed()
    
    return network_manager_instance


async def initialize_network_manager() -> bool:
    """Initialize the global network manager."""
    try:
        manager = get_network_manager()
        logger.info("✅ Network manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize network manager: {e}")
        return False


# Export commonly used components
__all__ = [
    "NetworkManagerFixed",
    "NetworkType", 
    "NetworkConfig",
    "NetworkStatus",
    "ProviderType",
    "get_network_manager",
    "initialize_network_manager"
]