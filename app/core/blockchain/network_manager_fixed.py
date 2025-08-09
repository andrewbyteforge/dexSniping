"""
Network Manager - Fixed RPC Authentication with Enhanced Error Handling
File: app/core/blockchain/network_manager_fixed.py

Professional blockchain network manager with proper RPC fallback handling
and comprehensive error validation to prevent type errors.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
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

logger = setup_logger(__name__, "application")


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
    Fixed Network Manager with enhanced error handling and RPC fallback.
    
    Prioritizes public RPC endpoints to avoid authentication issues,
    includes comprehensive input validation to prevent type errors.
    """
    
    def __init__(self):
        """Initialize the network manager with enhanced error handling."""
        logger.info("[LINK] Initializing NetworkManagerFixed with enhanced validation...")
        
        # Initialize collections
        self.connections: Dict[NetworkType, Optional[AsyncWeb3]] = {}
        self.network_status: Dict[NetworkType, NetworkStatus] = {}
        self.network_configs: Dict[NetworkType, NetworkConfig] = {}
        
        # Setup network configurations
        self._setup_network_configurations()
        
        # Initialize status for all networks
        self._initialize_network_status()
        
        logger.info("[OK] NetworkManagerFixed initialized successfully")
    
    def _setup_network_configurations(self) -> None:
        """Setup configurations for all supported networks."""
        try:
            # Ethereum Mainnet Configuration
            self.network_configs[NetworkType.ETHEREUM] = NetworkConfig(
                network_type=NetworkType.ETHEREUM,
                name="Ethereum Mainnet",
                chain_id=1,
                native_currency="Ether",
                currency_symbol="ETH",
                currency_decimals=18,
                
                # Public RPC endpoints (prioritized)
                public_rpc_urls=[
                    "https://eth.llamarpc.com",
                    "https://rpc.ankr.com/eth",
                    "https://ethereum.publicnode.com",
                    "https://eth-mainnet.public.blastapi.io",
                    "https://rpc.flashbots.net"
                ],
                
                # Private RPC endpoints (require API keys)
                private_rpc_urls=[
                    "https://mainnet.infura.io/v3/{api_key}",
                    "https://eth-mainnet.alchemyapi.io/v2/{api_key}",
                    "https://eth-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                
                explorer_url="https://etherscan.io",
                max_gas_price_gwei=100.0,
                block_time_seconds=12.0
            )
            
            # Polygon Configuration
            self.network_configs[NetworkType.POLYGON] = NetworkConfig(
                network_type=NetworkType.POLYGON,
                name="Polygon Mainnet",
                chain_id=137,
                native_currency="MATIC",
                currency_symbol="MATIC",
                currency_decimals=18,
                
                public_rpc_urls=[
                    "https://polygon-rpc.com",
                    "https://rpc.ankr.com/polygon",
                    "https://polygon.llamarpc.com",
                    "https://polygon.publicnode.com"
                ],
                
                private_rpc_urls=[
                    "https://polygon-mainnet.infura.io/v3/{api_key}",
                    "https://polygon-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                
                explorer_url="https://polygonscan.com",
                max_gas_price_gwei=50.0,
                block_time_seconds=2.0
            )
            
            # Binance Smart Chain Configuration
            self.network_configs[NetworkType.BSC] = NetworkConfig(
                network_type=NetworkType.BSC,
                name="Binance Smart Chain",
                chain_id=56,
                native_currency="BNB",
                currency_symbol="BNB",
                currency_decimals=18,
                
                public_rpc_urls=[
                    "https://bsc-dataseed.binance.org",
                    "https://bsc-dataseed1.defibit.io",
                    "https://bsc-dataseed1.ninicoin.io",
                    "https://rpc.ankr.com/bsc"
                ],
                
                private_rpc_urls=[
                    "https://speedy-nodes-nyc.moralis.io/{api_key}/bsc/mainnet"
                ],
                
                explorer_url="https://bscscan.com",
                max_gas_price_gwei=20.0,
                block_time_seconds=3.0
            )
            
            # Arbitrum Configuration
            self.network_configs[NetworkType.ARBITRUM] = NetworkConfig(
                network_type=NetworkType.ARBITRUM,
                name="Arbitrum One",
                chain_id=42161,
                native_currency="Ether",
                currency_symbol="ETH",
                currency_decimals=18,
                
                public_rpc_urls=[
                    "https://arb1.arbitrum.io/rpc",
                    "https://rpc.ankr.com/arbitrum",
                    "https://arbitrum.llamarpc.com",
                    "https://arbitrum.publicnode.com"
                ],
                
                private_rpc_urls=[
                    "https://arbitrum-mainnet.infura.io/v3/{api_key}",
                    "https://arb-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                
                explorer_url="https://arbiscan.io",
                max_gas_price_gwei=5.0,
                block_time_seconds=0.25
            )
            
            logger.info(f"[OK] Network configurations setup complete: {len(self.network_configs)} networks")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to setup network configurations: {e}")
            raise NetworkError(f"Network configuration setup failed: {e}")
    
    def _initialize_network_status(self) -> None:
        """Initialize status tracking for all networks."""
        try:
            for network_type in self.network_configs:
                self.network_status[network_type] = NetworkStatus(
                    network_type=network_type,
                    is_connected=False,
                    last_checked=datetime.utcnow()
                )
            
            logger.info("[OK] Network status tracking initialized")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize network status: {e}")
    
    def _validate_network_type(self, network_input: Any) -> Optional[NetworkType]:
        """
        Validate and convert network input to NetworkType enum.
        
        Args:
            network_input: Input that should represent a network type
            
        Returns:
            NetworkType if valid, None if invalid
        """
        try:
            # Handle None input
            if network_input is None:
                logger.warning("[WARN] Network type is None")
                return None
            
            # Handle NetworkType enum (already valid)
            if isinstance(network_input, NetworkType):
                return network_input
            
            # Handle string input
            if isinstance(network_input, str):
                try:
                    # Try direct enum conversion
                    return NetworkType(network_input.lower())
                except ValueError:
                    # Try matching by value
                    for network_type in NetworkType:
                        if network_type.value.lower() == network_input.lower():
                            return network_type
                    
                    logger.warning(f"[WARN] Unknown network string: '{network_input}'")
                    return None
            
            # Handle integer input (INVALID - this was causing the error)
            if isinstance(network_input, int):
                logger.warning(f"[WARN] Invalid network type - received integer: {network_input}")
                logger.info("[INFO] Network types must be strings (e.g., 'ethereum') or NetworkType enums")
                return None
            
            # Handle other invalid types
            logger.warning(f"[WARN] Invalid network type - unsupported type: {type(network_input)} - {network_input}")
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Error validating network type: {e}")
            return None
    
    async def connect_to_network(self, network_input: Any) -> bool:
        """
        Connect to a blockchain network with enhanced validation.
        
        Args:
            network_input: The network to connect to (string, NetworkType, or other)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Validate network type first
            network_type = self._validate_network_type(network_input)
            
            if network_type is None:
                logger.warning(f"[WARN] Cannot connect - invalid network type: {network_input}")
                return False
            
            if not WEB3_AVAILABLE:
                logger.warning(f"[WARN] Web3 not available - cannot connect to {network_type.value}")
                return False
            
            logger.info(f"[LINK] Connecting to {network_type.value}...")
            
            config = self.network_configs.get(network_type)
            if not config:
                logger.warning(f"[WARN] No configuration found for network: {network_type.value}")
                return False
            
            # Try to establish connection with proper fallback
            connection = await self._establish_connection_with_fallback(config)
            
            if connection:
                self.connections[network_type] = connection
                await self._update_network_status(network_type, True, connection)
                logger.info(f"[OK] Successfully connected to {network_type.value}")
                return True
            else:
                await self._update_network_status(network_type, False, None, "No working RPC endpoints")
                logger.warning(f"[WARN] Failed to connect to {network_type.value} - no working endpoints")
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"[WARN] Connection to {network_input} failed: {error_msg}")
            
            # Try to update status if we have a valid network type
            if network_type and isinstance(network_type, NetworkType):
                try:
                    await self._update_network_status(network_type, False, None, error_msg)
                except Exception:
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
        try:
            all_endpoints = []
            
            # Prioritize public endpoints (no API key required)
            all_endpoints.extend(config.public_rpc_urls)
            
            # Add private endpoints if API keys are available
            for private_url in config.private_rpc_urls:
                if "{api_key}" in private_url:
                    # Check for API keys in environment variables
                    api_key = None
                    
                    if "infura" in private_url.lower():
                        api_key = os.getenv("INFURA_API_KEY")
                    elif "alchemy" in private_url.lower():
                        api_key = os.getenv("ALCHEMY_API_KEY")
                    elif "moralis" in private_url.lower():
                        api_key = os.getenv("MORALIS_API_KEY")
                    
                    if api_key:
                        all_endpoints.append(private_url.format(api_key=api_key))
                        logger.info(f"[OK] Added private RPC endpoint with API key")
                    else:
                        logger.info(f"ℹ[EMOJI] Skipping private endpoint - no API key available")
                else:
                    all_endpoints.append(private_url)
            
            # Try each endpoint until one works
            for i, rpc_url in enumerate(all_endpoints):
                try:
                    logger.info(f"[UPDATE] Trying RPC endpoint {i+1}/{len(all_endpoints)}: {self._mask_url(rpc_url)}")
                    
                    # Create Web3 instance
                    provider = AsyncHTTPProvider(rpc_url)
                    w3 = AsyncWeb3(provider)
                    
                    # Add middleware for PoA networks if needed
                    if config.network_type in [NetworkType.BSC, NetworkType.POLYGON]:
                        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    # Test connection with timeout
                    is_connected = await asyncio.wait_for(w3.is_connected(), timeout=10.0)
                    
                    if is_connected:
                        # Verify we can get block info
                        latest_block = await asyncio.wait_for(w3.eth.block_number, timeout=10.0)
                        logger.info(f"[OK] Connected to {config.name} (Block: {latest_block})")
                        return w3
                    else:
                        logger.warning(f"[WARN] Connection test failed for: {self._mask_url(rpc_url)}")
                        
                except asyncio.TimeoutError:
                    logger.warning(f"[WARN] Timeout connecting to: {self._mask_url(rpc_url)}")
                except Exception as e:
                    logger.warning(f"[WARN] Error with endpoint {self._mask_url(rpc_url)}: {str(e)[:100]}")
            
            logger.warning(f"[ERROR] All RPC endpoints failed for {config.name}")
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Connection establishment failed: {e}")
            return None
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive information in URLs for logging."""
        try:
            # Replace API keys with asterisks
            import re
            
            # Pattern for API keys (32+ character alphanumeric strings)
            pattern = r'[a-zA-Z0-9]{32,}'
            masked_url = re.sub(pattern, '***API_KEY***', url)
            
            return masked_url
        except Exception:
            return url[:50] + "..." if len(url) > 50 else url
    
    async def _update_network_status(
        self, 
        network_type: NetworkType, 
        is_connected: bool, 
        connection: Optional[AsyncWeb3] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update network status with current information."""
        try:
            status = NetworkStatus(
                network_type=network_type,
                is_connected=is_connected,
                last_checked=datetime.utcnow(),
                error_message=error_message
            )
            
            if is_connected and connection:
                try:
                    # Get additional network info
                    status.latest_block = await connection.eth.block_number
                    gas_price_wei = await connection.eth.gas_price
                    status.gas_price_gwei = float(gas_price_wei) / 10**9
                    
                except Exception as e:
                    logger.warning(f"[WARN] Could not fetch network details: {e}")
            
            self.network_status[network_type] = status
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to update network status: {e}")
    
    async def disconnect_from_network(self, network_input: Any) -> bool:
        """
        Disconnect from a specific network.
        
        Args:
            network_input: Network to disconnect from
            
        Returns:
            bool: True if disconnection successful
        """
        try:
            network_type = self._validate_network_type(network_input)
            
            if network_type is None:
                logger.warning(f"[WARN] Cannot disconnect - invalid network type: {network_input}")
                return False
            
            if network_type in self.connections:
                # Clean up connection
                del self.connections[network_type]
                
                # Update status
                self.network_status[network_type] = NetworkStatus(
                    network_type=network_type,
                    is_connected=False,
                    last_checked=datetime.utcnow(),
                    error_message="Manually disconnected"
                )
                
                logger.info(f"[OK] Disconnected from {network_type.value}")
                return True
            else:
                logger.info(f"ℹ[EMOJI] Not connected to {network_type.value}")
                return True
                
        except Exception as e:
            logger.error(f"[ERROR] Error disconnecting from network: {e}")
            return False
    
    def get_web3_instance(self, network_input: Any) -> Optional[AsyncWeb3]:
        """
        Get Web3 instance for a network.
        
        Args:
            network_input: Network to get instance for
            
        Returns:
            AsyncWeb3 instance or None
        """
        try:
            network_type = self._validate_network_type(network_input)
            
            if network_type is None:
                return None
            
            return self.connections.get(network_type)
            
        except Exception as e:
            logger.error(f"[ERROR] Error getting Web3 instance: {e}")
            return None
    
    async def disconnect_all(self) -> None:
        """Disconnect from all networks."""
        try:
            logger.info("[CONNECT] Disconnecting from all networks...")
            
            for network_type in list(self.connections.keys()):
                try:
                    await self.disconnect_from_network(network_type)
                except Exception as e:
                    logger.error(f"[ERROR] Error disconnecting from {network_type.value}: {e}")
            
            logger.info("[OK] Disconnected from all networks")
            
        except Exception as e:
            logger.error(f"[ERROR] Error during disconnect_all: {e}")
    
    def get_network_status(self, network_input: Any) -> Optional[NetworkStatus]:
        """Get status for a specific network."""
        try:
            network_type = self._validate_network_type(network_input)
            
            if network_type is None:
                return None
            
            return self.network_status.get(network_type)
            
        except Exception as e:
            logger.error(f"[ERROR] Error getting network status: {e}")
            return None
    
    def get_all_network_status(self) -> Dict[NetworkType, NetworkStatus]:
        """Get status for all networks."""
        return self.network_status.copy()
    
    def is_connected(self, network_input: Any) -> bool:
        """Check if connected to a specific network."""
        try:
            status = self.get_network_status(network_input)
            return status is not None and status.is_connected
        except Exception:
            return False
    
    def get_supported_networks(self) -> List[str]:
        """Get list of supported network names."""
        return [network.value for network in NetworkType]
    
    def get_network_config(self, network_input: Any) -> Optional[NetworkConfig]:
        """Get configuration for a specific network."""
        try:
            network_type = self._validate_network_type(network_input)
            
            if network_type is None:
                return None
            
            return self.network_configs.get(network_type)
            
        except Exception as e:
            logger.error(f"[ERROR] Error getting network config: {e}")
            return None


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
        logger.info("[OK] Network manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize network manager: {e}")
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