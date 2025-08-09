"""
Enhanced Blockchain Network Manager
File: app/core/blockchain/network_manager.py

Professional multi-chain network management system combining real Web3 connectivity
with advanced monitoring, failover, connection pooling, and health tracking.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from web3.providers import HTTPProvider, WebsocketProvider
from web3.exceptions import Web3Exception
import requests
import aiohttp

from app.utils.logger import setup_logger
from app.core.exceptions import (
    TradingError, 
    NetworkError, 
    ConnectionError, 
    InsufficientFundsError,
    RPCError
)

logger = setup_logger(__name__)


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
    ANKR = "ankr"
    PUBLIC_RPC = "public_rpc"
    LOCAL_NODE = "local_node"


class ConnectionStatus(Enum):
    """Network connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RECONNECTING = "reconnecting"


@dataclass
class NetworkConfig:
    """Comprehensive network configuration data structure."""
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
    
    @property
    def supports_eip1559(self) -> bool:
        """Check if network supports EIP-1559."""
        return self.network_type in [
            NetworkType.ETHEREUM,
            NetworkType.POLYGON,
            NetworkType.ARBITRUM,
            NetworkType.OPTIMISM,
            NetworkType.BASE
        ]


@dataclass 
class NetworkStatus:
    """Enhanced network health and status information."""
    network_type: NetworkType
    status: ConnectionStatus
    is_connected: bool
    latest_block: int
    gas_price_gwei: float
    response_time_ms: float
    provider_type: ProviderType
    current_rpc_url: str
    connection_time: datetime = field(default_factory=datetime.utcnow)
    last_ping: Optional[datetime] = None
    error_count: int = 0
    error_message: Optional[str] = None
    total_requests: int = 0
    failed_requests: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate connection success rate."""
        if self.total_requests == 0:
            return 1.0
        return (self.total_requests - self.failed_requests) / self.total_requests
    
    @property
    def health_score(self) -> float:
        """Calculate overall health score (0-1)."""
        if not self.is_connected:
            return 0.0
        
        # Factors: success rate, response time, error count
        success_factor = self.success_rate
        
        # Response time factor (good if < 1000ms)
        response_factor = max(0, min(1, (2000 - self.response_time_ms) / 2000))
        
        # Error count factor (good if < 5 errors)
        error_factor = max(0, min(1, (10 - self.error_count) / 10))
        
        return (success_factor * 0.5 + response_factor * 0.3 + error_factor * 0.2)


@dataclass
class NetworkConnection:
    """Enhanced network connection information."""
    network_type: NetworkType
    config: NetworkConfig
    web3_instance: Optional[AsyncWeb3]
    status: ConnectionStatus
    current_rpc_url: str
    provider_type: ProviderType
    connection_attempts: int = 0
    last_successful_call: Optional[datetime] = None
    circuit_breaker_until: Optional[datetime] = None
    
    @property
    def is_circuit_breaker_active(self) -> bool:
        """Check if circuit breaker is active."""
        if not self.circuit_breaker_until:
            return False
        return datetime.utcnow() < self.circuit_breaker_until
    
    def activate_circuit_breaker(self, duration_minutes: int = 5) -> None:
        """Activate circuit breaker for specified duration."""
        self.circuit_breaker_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.status = ConnectionStatus.ERROR


class EnhancedNetworkManager:
    """
    Enhanced blockchain network manager with comprehensive multi-chain support.
    
    Features:
    - Real Web3 connectivity with multiple provider support
    - Automatic failover and load balancing
    - Circuit breaker pattern for failing endpoints
    - Health monitoring and connection pooling
    - Gas price tracking and optimization
    - EIP-1559 support with legacy fallback
    - Connection state persistence
    - Comprehensive error handling and retry logic
    """
    
    def __init__(self):
        """Initialize the enhanced network manager."""
        self.connections: Dict[NetworkType, NetworkConnection] = {}
        self.network_configs: Dict[NetworkType, NetworkConfig] = {}
        self.network_status: Dict[NetworkType, NetworkStatus] = {}
        self.api_keys: Dict[ProviderType, Optional[str]] = {}
        
        # Connection management
        self.connection_pool_size = 5
        self.max_retries = 3
        self.retry_delay = 1.0
        self.health_check_interval = 30
        self.circuit_breaker_threshold = 5  # failures before circuit breaker
        
        # Monitoring
        self.is_monitoring = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Request tracking
        self.request_history: Dict[NetworkType, List[Dict[str, Any]]] = {}
        
        # Initialize configurations
        self._setup_network_configs()
        self._load_api_keys()
        
        logger.info("🌐 Enhanced NetworkManager initialized with multi-chain support")
    
    def _setup_network_configs(self) -> None:
        """Set up comprehensive network configurations for all supported chains."""
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
                    "https://eth-mainnet.g.alchemy.com/v2/{api_key}",
                    "https://rpc.ankr.com/eth",
                    "https://eth.llamarpc.com",
                    "https://ethereum.publicnode.com",
                    "https://rpc.payload.de",
                    "https://api.mycryptoapi.com/eth"
                ],
                websocket_urls=[
                    "wss://mainnet.infura.io/ws/v3/{api_key}",
                    "wss://eth-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                explorer_url="https://etherscan.io",
                gas_price_oracle_url="https://ethgasstation.info/json/ethgasAPI.json",
                max_gas_price_gwei=500,
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
                    "https://rpc.ankr.com/polygon",
                    "https://polygon-rpc.com",
                    "https://rpc-mainnet.matic.network",
                    "https://matic-mainnet.chainstacklabs.com",
                    "https://polygon.llamarpc.com"
                ],
                websocket_urls=[
                    "wss://polygon-mainnet.infura.io/ws/v3/{api_key}",
                    "wss://polygon-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                explorer_url="https://polygonscan.com",
                max_gas_price_gwei=1000,
                block_time_seconds=2.0
            ),
            
            NetworkType.BSC: NetworkConfig(
                network_type=NetworkType.BSC,
                name="BNB Smart Chain",
                chain_id=56,
                native_currency="Binance Coin",
                currency_symbol="BNB",
                currency_decimals=18,
                rpc_urls=[
                    "https://bsc-dataseed.binance.org",
                    "https://bsc-dataseed1.defibit.io",
                    "https://bsc-dataseed1.ninicoin.io",
                    "https://rpc.ankr.com/bsc",
                    "https://bsc.publicnode.com",
                    "https://bsc-dataseed2.binance.org",
                    "https://bsc-dataseed3.binance.org"
                ],
                websocket_urls=[
                    "wss://bsc-ws-node.nariox.org:443"
                ],
                explorer_url="https://bscscan.com",
                max_gas_price_gwei=50,
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
                    "https://rpc.ankr.com/arbitrum",
                    "https://arb1.arbitrum.io/rpc",
                    "https://arbitrum.publicnode.com",
                    "https://arbitrum-one.public.blastapi.io"
                ],
                websocket_urls=[
                    "wss://arbitrum-mainnet.infura.io/ws/v3/{api_key}",
                    "wss://arb-mainnet.g.alchemy.com/v2/{api_key}"
                ],
                explorer_url="https://arbiscan.io",
                max_gas_price_gwei=10,
                block_time_seconds=0.25
            ),
            
            NetworkType.OPTIMISM: NetworkConfig(
                network_type=NetworkType.OPTIMISM,
                name="Optimism",
                chain_id=10,
                native_currency="Ethereum",
                currency_symbol="ETH",
                currency_decimals=18,
                rpc_urls=[
                    "https://optimism-mainnet.infura.io/v3/{api_key}",
                    "https://opt-mainnet.g.alchemy.com/v2/{api_key}",
                    "https://rpc.ankr.com/optimism",
                    "https://mainnet.optimism.io",
                    "https://optimism.publicnode.com"
                ],
                websocket_urls=[
                    "wss://optimism-mainnet.infura.io/ws/v3/{api_key}"
                ],
                explorer_url="https://optimistic.etherscan.io",
                max_gas_price_gwei=10,
                block_time_seconds=2.0
            ),
            
            NetworkType.AVALANCHE: NetworkConfig(
                network_type=NetworkType.AVALANCHE,
                name="Avalanche C-Chain",
                chain_id=43114,
                native_currency="Avalanche",
                currency_symbol="AVAX",
                currency_decimals=18,
                rpc_urls=[
                    "https://rpc.ankr.com/avalanche",
                    "https://api.avax.network/ext/bc/C/rpc",
                    "https://avalanche.publicnode.com",
                    "https://avax-mainnet.gateway.pokt.network/v1/lb/605238bf6b986eea7cf36d5e/ext/bc/C/rpc"
                ],
                websocket_urls=[],
                explorer_url="https://snowtrace.io",
                max_gas_price_gwei=50,
                block_time_seconds=2.0
            ),
            
            NetworkType.BASE: NetworkConfig(
                network_type=NetworkType.BASE,
                name="Base",
                chain_id=8453,
                native_currency="Ethereum",
                currency_symbol="ETH",
                currency_decimals=18,
                rpc_urls=[
                    "https://mainnet.base.org",
                    "https://rpc.ankr.com/base",
                    "https://base.publicnode.com"
                ],
                websocket_urls=[],
                explorer_url="https://basescan.org",
                max_gas_price_gwei=10,
                block_time_seconds=2.0
            ),
            
            NetworkType.FANTOM: NetworkConfig(
                network_type=NetworkType.FANTOM,
                name="Fantom Opera",
                chain_id=250,
                native_currency="Fantom",
                currency_symbol="FTM",
                currency_decimals=18,
                rpc_urls=[
                    "https://rpc.ftm.tools",
                    "https://rpc.ankr.com/fantom",
                    "https://fantom.publicnode.com"
                ],
                websocket_urls=[],
                explorer_url="https://ftmscan.com",
                max_gas_price_gwei=500,
                block_time_seconds=1.0
            )
        }
    
    def _load_api_keys(self) -> None:
        """Load API keys from environment variables."""
        self.api_keys = {
            ProviderType.INFURA: os.getenv("INFURA_API_KEY"),
            ProviderType.ALCHEMY: os.getenv("ALCHEMY_API_KEY"),
            ProviderType.QUICKNODE: os.getenv("QUICKNODE_API_KEY"),
            ProviderType.MORALIS: os.getenv("MORALIS_API_KEY"),
            ProviderType.ANKR: os.getenv("ANKR_API_KEY")
        }
        
        # Log available providers
        available_providers = [
            provider.value for provider, key in self.api_keys.items() 
            if key is not None
        ]
        if available_providers:
            logger.info(f"🔑 Available API providers: {available_providers}")
        else:
            logger.warning("⚠️ No API keys found - using public RPC endpoints only")
    
    async def connect_to_network(
        self, 
        network_type: Union[NetworkType, str],
        preferred_provider: Optional[ProviderType] = None,
        force_reconnect: bool = False
    ) -> bool:
        """
        Connect to a specific blockchain network with enhanced error handling.
        
        Args:
            network_type: The network to connect to
            preferred_provider: Preferred RPC provider
            force_reconnect: Force reconnection even if already connected
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If unable to connect to any provider
        """
        try:
            # Handle string input
            if isinstance(network_type, str):
                network_type = NetworkType(network_type.lower())
            
            # Check if already connected and not forcing reconnect
            if not force_reconnect and network_type in self.connections:
                connection = self.connections[network_type]
                if connection.status == ConnectionStatus.CONNECTED and not connection.is_circuit_breaker_active:
                    logger.debug(f"🔗 Already connected to {network_type.value}")
                    return True
            
            logger.info(f"🔌 Connecting to {network_type.value}...")
            
            config = self.network_configs.get(network_type)
            if not config:
                raise ConnectionError(f"Unsupported network: {network_type}")
            
            # Create connection with failover
            connection = await self._establish_connection_with_failover(config, preferred_provider)
            
            if connection:
                self.connections[network_type] = connection
                await self._update_network_status(network_type, connection)
                logger.info(f"✅ Connected to {network_type.value} via {connection.provider_type.value}")
                return True
            else:
                await self._update_network_status(network_type, None, "No providers available")
                raise ConnectionError(f"Failed to connect to {network_type.value}")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to {network_type.value}: {e}")
            await self._update_network_status(network_type, None, str(e))
            raise ConnectionError(f"Network connection failed: {e}")
    
    async def _establish_connection_with_failover(
        self, 
        config: NetworkConfig,
        preferred_provider: Optional[ProviderType] = None
    ) -> Optional[NetworkConnection]:
        """Establish connection with intelligent provider failover."""
        # Build prioritized list of RPC URLs
        rpc_urls = self._build_prioritized_rpc_list(config, preferred_provider)
        
        # Try each URL with retry logic
        for rpc_url, provider_type in rpc_urls:
            try:
                logger.debug(f"🔄 Trying {provider_type.value}: {rpc_url[:50]}...")
                
                # Create Web3 instance with retry logic
                web3_instance = await self._create_web3_instance(rpc_url, config)
                
                if web3_instance:
                    # Test connection thoroughly
                    if await self._test_connection_comprehensive(web3_instance, config):
                        return NetworkConnection(
                            network_type=config.network_type,
                            config=config,
                            web3_instance=web3_instance,
                            status=ConnectionStatus.CONNECTED,
                            current_rpc_url=rpc_url,
                            provider_type=provider_type,
                            connection_attempts=1
                        )
                
            except Exception as e:
                logger.debug(f"⚠️ Provider {provider_type.value} failed: {e}")
                continue
        
        return None
    
    def _build_prioritized_rpc_list(
        self, 
        config: NetworkConfig, 
        preferred_provider: Optional[ProviderType]
    ) -> List[tuple[str, ProviderType]]:
        """Build prioritized list of RPC URLs with provider types."""
        rpc_urls = []
        
        # Add preferred provider URLs first
        if preferred_provider and self.api_keys.get(preferred_provider):
            for url in config.rpc_urls:
                if "{api_key}" in url:
                    formatted_url = url.format(api_key=self.api_keys[preferred_provider])
                    rpc_urls.append((formatted_url, preferred_provider))
        
        # Add other provider URLs with API keys
        for provider, api_key in self.api_keys.items():
            if provider != preferred_provider and api_key:
                for url in config.rpc_urls:
                    if "{api_key}" in url and provider.value in url.lower():
                        formatted_url = url.format(api_key=api_key)
                        rpc_urls.append((formatted_url, provider))
        
        # Add public RPC URLs as fallback
        for url in config.rpc_urls:
            if "{api_key}" not in url:
                # Determine provider type from URL
                provider_type = ProviderType.PUBLIC_RPC
                if "ankr" in url.lower():
                    provider_type = ProviderType.ANKR
                
                rpc_urls.append((url, provider_type))
        
        return rpc_urls
    
    async def _create_web3_instance(self, rpc_url: str, config: NetworkConfig) -> Optional[AsyncWeb3]:
        """Create and configure Web3 instance."""
        try:
            # Create provider with timeout settings
            provider = HTTPProvider(
                rpc_url, 
                request_kwargs={
                    'timeout': 30,
                    'headers': {
                        'User-Agent': 'Enhanced-Network-Manager/1.0'
                    }
                }
            )
            
            # Create Web3 instance
            web3 = AsyncWeb3(provider)
            
            # Add PoA middleware for networks that need it
            if config.network_type in [NetworkType.BSC, NetworkType.POLYGON]:
                web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            return web3
            
        except Exception as e:
            logger.debug(f"Failed to create Web3 instance: {e}")
            return None
    
    async def _test_connection_comprehensive(self, web3: AsyncWeb3, config: NetworkConfig) -> bool:
        """Perform comprehensive connection testing."""
        try:
            # Test 1: Check if Web3 is connected
            if not await web3.is_connected():
                return False
            
            # Test 2: Get chain ID and verify
            chain_id = await web3.eth.chain_id
            if chain_id != config.chain_id:
                logger.warning(f"Chain ID mismatch: expected {config.chain_id}, got {chain_id}")
                return False
            
            # Test 3: Get latest block number
            latest_block = await web3.eth.block_number
            if latest_block <= 0:
                return False
            
            # Test 4: Get gas price
            gas_price = await web3.eth.gas_price
            if gas_price <= 0:
                return False
            
            # Test 5: Get network version
            network_version = await web3.net.version
            if not network_version:
                return False
            
            logger.debug(f"✅ Connection test passed: block {latest_block}, gas {web3.from_wei(gas_price, 'gwei')} gwei")
            return True
            
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False
    
    async def _update_network_status(
        self, 
        network_type: NetworkType, 
        connection: Optional[NetworkConnection],
        error_message: Optional[str] = None
    ) -> None:
        """Update comprehensive network status information."""
        try:
            latest_block = 0
            gas_price_gwei = 0.0
            response_time_ms = 0.0
            provider_type = ProviderType.PUBLIC_RPC
            current_rpc_url = ""
            status = ConnectionStatus.DISCONNECTED
            
            if connection and connection.web3_instance:
                start_time = datetime.utcnow()
                
                try:
                    # Get network information
                    latest_block = await connection.web3_instance.eth.block_number
                    gas_price_wei = await connection.web3_instance.eth.gas_price
                    gas_price_gwei = float(connection.web3_instance.from_wei(gas_price_wei, 'gwei'))
                    
                    # Calculate response time
                    end_time = datetime.utcnow()
                    response_time_ms = (end_time - start_time).total_seconds() * 1000
                    
                    provider_type = connection.provider_type
                    current_rpc_url = connection.current_rpc_url
                    status = connection.status
                    
                    # Update request tracking
                    self._track_request(network_type, True, response_time_ms)
                    
                except Exception as e:
                    logger.debug(f"Failed to get network stats: {e}")
                    self._track_request(network_type, False, 0)
                    error_message = str(e)
            
            # Get existing status for historical data
            existing_status = self.network_status.get(network_type)
            total_requests = existing_status.total_requests if existing_status else 0
            failed_requests = existing_status.failed_requests if existing_status else 0
            error_count = existing_status.error_count if existing_status else 0
            
            # Update error count
            if error_message:
                error_count += 1
            elif connection and connection.status == ConnectionStatus.CONNECTED:
                error_count = 0
            
            self.network_status[network_type] = NetworkStatus(
                network_type=network_type,
                status=status,
                is_connected=connection is not None and connection.status == ConnectionStatus.CONNECTED,
                latest_block=latest_block,
                gas_price_gwei=gas_price_gwei,
                response_time_ms=response_time_ms,
                provider_type=provider_type,
                current_rpc_url=current_rpc_url,
                error_count=error_count,
                error_message=error_message,
                total_requests=total_requests,
                failed_requests=failed_requests
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to update network status for {network_type}: {e}")
    
    def _track_request(self, network_type: NetworkType, success: bool, response_time_ms: float) -> None:
        """Track request statistics for network monitoring."""
        if network_type not in self.request_history:
            self.request_history[network_type] = []
        
        request_data = {
            'timestamp': datetime.utcnow(),
            'success': success,
            'response_time_ms': response_time_ms
        }
        
        self.request_history[network_type].append(request_data)
        
        # Keep only recent history (last 100 requests)
        if len(self.request_history[network_type]) > 100:
            self.request_history[network_type] = self.request_history[network_type][-100:]
        
        # Update status counters
        if network_type in self.network_status:
            self.network_status[network_type].total_requests += 1
            if not success:
                self.network_status[network_type].failed_requests += 1
    
    async def disconnect_from_network(self, network_type: NetworkType) -> bool:
        """Disconnect from a specific network."""
        try:
            if network_type in self.connections:
                connection = self.connections[network_type]
                connection.status = ConnectionStatus.DISCONNECTED
                
                # Close Web3 connection if needed
                if connection.web3_instance:
                    # AsyncWeb3 doesn't have explicit close method, just remove reference
                    connection.web3_instance = None
                
                del self.connections[network_type]
                await self._update_network_status(network_type, None)
                
                logger.info(f"🔌 Disconnected from {network_type.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to disconnect from {network_type}: {e}")
            return False
    
    async def get_web3_instance(self, network_type: NetworkType) -> AsyncWeb3:
        """Get Web3 instance for a network with automatic connection."""
        if network_type not in self.connections:
            success = await self.connect_to_network(network_type)
            if not success:
                raise ConnectionError(f"Unable to connect to {network_type}")
        
        connection = self.connections[network_type]
        
        # Check if connection is healthy
        if connection.is_circuit_breaker_active:
            raise ConnectionError(f"Circuit breaker active for {network_type}")
        
        if not connection.web3_instance:
            raise ConnectionError(f"No Web3 instance for {network_type}")
        
        return connection.web3_instance
    
    async def get_native_balance(
        self, 
        network_type: NetworkType, 
        address: str
    ) -> Decimal:
        """Get native token balance for an address."""
        try:
            web3 = await self.get_web3_instance(network_type)
            balance_wei = await web3.eth.get_balance(web3.to_checksum_address(address))
            balance_eth = web3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_eth))
            
        except Exception as e:
            logger.error(f"❌ Failed to get balance for {address}: {e}")
            raise TradingError(f"Balance check failed: {e}")
    
    async def get_token_balance(
        self, 
        network_type: NetworkType,
        token_address: str,
        wallet_address: str,
        decimals: int = 18
    ) -> Decimal:
        """Get ERC20 token balance with custom decimals."""
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
            
            # Convert from token units to decimal
            balance_decimal = Decimal(str(balance)) / Decimal(10 ** decimals)
            return balance_decimal
            
        except Exception as e:
            logger.error(f"❌ Failed to get token balance: {e}")
            raise TradingError(f"Token balance check failed: {e}")
    
    async def estimate_gas_price(self, network_type: NetworkType) -> Dict[str, Any]:
        """Get comprehensive gas price estimates."""
        try:
            web3 = await self.get_web3_instance(network_type)
            config = self.network_configs[network_type]
            
            # Get current gas price
            current_gas_price = await web3.eth.gas_price
            current_gwei = int(web3.from_wei(current_gas_price, 'gwei'))
            
            # For EIP-1559 networks, get fee history
            if config.supports_eip1559:
                try:
                    fee_history = await web3.eth.fee_history(20, 'latest', [10, 50, 90])
                    
                    base_fee = fee_history['baseFeePerGas'][-1] if fee_history['baseFeePerGas'] else current_gas_price
                    base_fee_gwei = int(web3.from_wei(base_fee, 'gwei'))
                    
                    # Calculate priority fees from percentiles
                    reward_percentiles = fee_history.get('reward', [])
                    if reward_percentiles:
                        priority_fees = []
                        for rewards in reward_percentiles:
                            if rewards:
                                priority_fees.extend([int(web3.from_wei(r, 'gwei')) for r in rewards])
                        
                        if priority_fees:
                            slow_priority = max(1, int(sorted(priority_fees)[len(priority_fees)//4]))
                            standard_priority = max(2, int(sorted(priority_fees)[len(priority_fees)//2]))
                            fast_priority = max(3, int(sorted(priority_fees)[3*len(priority_fees)//4]))
                        else:
                            slow_priority, standard_priority, fast_priority = 1, 2, 3
                    else:
                        slow_priority, standard_priority, fast_priority = 1, 2, 3
                    
                    return {
                        "type": "eip1559",
                        "base_fee_gwei": base_fee_gwei,
                        "slow": {
                            "max_fee": base_fee_gwei + slow_priority,
                            "priority_fee": slow_priority
                        },
                        "standard": {
                            "max_fee": base_fee_gwei + standard_priority,
                            "priority_fee": standard_priority
                        },
                        "fast": {
                            "max_fee": base_fee_gwei + fast_priority,
                            "priority_fee": fast_priority
                        }
                    }
                    
                except Exception as e:
                    logger.debug(f"EIP-1559 fee estimation failed, falling back to legacy: {e}")
            
            # Legacy gas pricing
            return {
                "type": "legacy",
                "slow": max(1, current_gwei - 2),
                "standard": current_gwei,
                "fast": current_gwei + 5,
                "fastest": current_gwei + 10
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate gas price: {e}")
            # Return safe fallback values
            return {
                "type": "legacy",
                "slow": 10,
                "standard": 20,
                "fast": 30,
                "fastest": 50
            }
    
    async def get_network_config(self, network_type: NetworkType) -> NetworkConfig:
        """Get network configuration."""
        config = self.network_configs.get(network_type)
        if not config:
            raise TradingError(f"Network {network_type} not supported")
        return config
    
    async def get_network_status(self, network_type: NetworkType) -> Dict[str, Any]:
        """Get detailed network status."""
        try:
            status = self.network_status.get(network_type)
            if not status:
                return {
                    "network": network_type.value,
                    "status": ConnectionStatus.DISCONNECTED.value,
                    "connected": False,
                    "message": "Network not initialized"
                }
            
            return {
                "network": network_type.value,
                "status": status.status.value,
                "connected": status.is_connected,
                "latest_block": status.latest_block,
                "gas_price_gwei": status.gas_price_gwei,
                "response_time_ms": status.response_time_ms,
                "provider_type": status.provider_type.value,
                "current_rpc_url": status.current_rpc_url[:50] + "..." if len(status.current_rpc_url) > 50 else status.current_rpc_url,
                "error_count": status.error_count,
                "error_message": status.error_message,
                "success_rate": status.success_rate,
                "health_score": status.health_score,
                "last_ping": status.last_ping.isoformat() if status.last_ping else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get network status: {e}")
            return {"error": str(e)}
    
    async def get_all_network_status(self) -> Dict[str, Any]:
        """Get status of all configured networks."""
        try:
            network_statuses = {}
            
            for network_type in NetworkType:
                network_statuses[network_type.value] = await self.get_network_status(network_type)
            
            # Calculate overall statistics
            connected_count = sum(1 for status in network_statuses.values() if status.get('connected', False))
            total_networks = len(NetworkType)
            
            return {
                "networks": network_statuses,
                "summary": {
                    "total_networks": total_networks,
                    "connected_networks": connected_count,
                    "connection_rate": connected_count / total_networks if total_networks > 0 else 0,
                    "monitoring_active": self.is_monitoring
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get all network status: {e}")
            return {"error": str(e)}
    
    async def start_monitoring(self) -> None:
        """Start comprehensive network health monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("📊 Started enhanced network monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop network health monitoring."""
        self.is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("⏹️ Stopped network monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Enhanced monitoring loop with circuit breaker logic."""
        while self.is_monitoring:
            try:
                for network_type, connection in list(self.connections.items()):
                    await self._monitor_connection_health(network_type, connection)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while self.is_monitoring:
            try:
                for network_type in list(self.connections.keys()):
                    await self._perform_health_check(network_type)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_connection_health(self, network_type: NetworkType, connection: NetworkConnection) -> None:
        """Monitor individual connection health with circuit breaker."""
        try:
            # Skip if circuit breaker is active
            if connection.is_circuit_breaker_active:
                return
            
            # Test connection
            if connection.web3_instance:
                start_time = datetime.utcnow()
                
                try:
                    # Quick health check
                    latest_block = await connection.web3_instance.eth.block_number
                    
                    if latest_block > 0:
                        # Connection is healthy
                        connection.last_successful_call = datetime.utcnow()
                        connection.status = ConnectionStatus.CONNECTED
                        
                        # Update response time
                        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                        self._track_request(network_type, True, response_time)
                        
                        return
                        
                except Exception as e:
                    logger.debug(f"Health check failed for {network_type}: {e}")
                    self._track_request(network_type, False, 0)
            
            # Connection failed - increment error count
            if network_type in self.network_status:
                self.network_status[network_type].error_count += 1
                
                # Activate circuit breaker if too many failures
                if self.network_status[network_type].error_count >= self.circuit_breaker_threshold:
                    connection.activate_circuit_breaker(5)  # 5 minutes
                    logger.warning(f"🔴 Circuit breaker activated for {network_type.value}")
            
        except Exception as e:
            logger.error(f"❌ Connection monitoring failed for {network_type}: {e}")
    
    async def _perform_health_check(self, network_type: NetworkType) -> None:
        """Perform comprehensive health check."""
        try:
            connection = self.connections.get(network_type)
            if not connection or not connection.web3_instance:
                return
            
            # Comprehensive health checks
            checks = {
                'connectivity': False,
                'block_sync': False,
                'gas_price': False,
                'chain_id': False
            }
            
            start_time = datetime.utcnow()
            
            try:
                # Check 1: Basic connectivity
                if await connection.web3_instance.is_connected():
                    checks['connectivity'] = True
                
                # Check 2: Block synchronization
                latest_block = await connection.web3_instance.eth.block_number
                if latest_block > 0:
                    checks['block_sync'] = True
                
                # Check 3: Gas price availability
                gas_price = await connection.web3_instance.eth.gas_price
                if gas_price > 0:
                    checks['gas_price'] = True
                
                # Check 4: Chain ID verification
                chain_id = await connection.web3_instance.eth.chain_id
                if chain_id == connection.config.chain_id:
                    checks['chain_id'] = True
                
            except Exception as e:
                logger.debug(f"Health check component failed: {e}")
            
            # Calculate health score
            passed_checks = sum(1 for check in checks.values() if check)
            health_score = passed_checks / len(checks)
            
            # Update status based on health score
            if health_score >= 0.75:
                connection.status = ConnectionStatus.CONNECTED
                connection.last_successful_call = datetime.utcnow()
            elif health_score >= 0.5:
                connection.status = ConnectionStatus.ERROR
            else:
                connection.status = ConnectionStatus.DISCONNECTED
            
            # Track performance
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._track_request(network_type, health_score >= 0.75, response_time)
            
            logger.debug(f"Health check {network_type.value}: {health_score:.2f} score, {response_time:.1f}ms")
            
        except Exception as e:
            logger.error(f"❌ Health check failed for {network_type}: {e}")
    
    async def switch_network(self, network_type: NetworkType) -> bool:
        """Switch to a different network with validation."""
        try:
            # Connect if not already connected
            if network_type not in self.connections:
                return await self.connect_to_network(network_type)
            
            # Verify existing connection is healthy
            connection = self.connections[network_type]
            if connection.status != ConnectionStatus.CONNECTED or connection.is_circuit_breaker_active:
                return await self.connect_to_network(network_type, force_reconnect=True)
            
            # Test connection
            if connection.web3_instance:
                latest_block = await connection.web3_instance.eth.block_number
                if latest_block > 0:
                    logger.info(f"🔄 Switched to {network_type.value} (block: {latest_block})")
                    return True
            
            # Connection test failed, reconnect
            return await self.connect_to_network(network_type, force_reconnect=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to switch to {network_type}: {e}")
            return False
    
    async def disconnect_all(self) -> None:
        """Disconnect from all networks and cleanup."""
        try:
            await self.stop_monitoring()
            
            for network_type in list(self.connections.keys()):
                await self.disconnect_from_network(network_type)
            
            # Clear all data structures
            self.connections.clear()
            self.network_status.clear()
            self.request_history.clear()
            
            logger.info("🔌 Disconnected from all networks")
            
        except Exception as e:
            logger.error(f"❌ Error during disconnect all: {e}")


# Global network manager instance
_network_manager: Optional[EnhancedNetworkManager] = None


def get_network_manager() -> EnhancedNetworkManager:
    """Get the global enhanced network manager instance."""
    global _network_manager
    if _network_manager is None:
        _network_manager = EnhancedNetworkManager()
    return _network_manager


# Context manager for network connections
@asynccontextmanager
async def network_connection(network_type: Union[NetworkType, str]):
    """Context manager for network connections with automatic cleanup."""
    manager = get_network_manager()
    try:
        # Ensure connection
        await manager.connect_to_network(network_type)
        yield manager
    except Exception as e:
        logger.error(f"Network connection context error: {e}")
        raise
    finally:
        # Connection cleanup is handled by the manager's monitoring
        pass


# Legacy compatibility alias
NetworkManager = EnhancedNetworkManager


# Export main classes and functions
__all__ = [
    "EnhancedNetworkManager",
    "NetworkManager",  # Legacy compatibility
    "NetworkType",
    "NetworkConfig",
    "NetworkStatus",
    "NetworkConnection", 
    "ProviderType",
    "ConnectionStatus",
    "get_network_manager",
    "network_connection"
]