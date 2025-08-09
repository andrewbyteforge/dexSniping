"""
Wallet Connection Manager - Phase 4B Implementation
File: app/core/wallet/wallet_connection_manager.py
Class: WalletConnectionManager
Methods: connect_metamask, connect_wallet_connect, verify_wallet_access

Professional wallet connectivity system for MetaMask and WalletConnect integration
with comprehensive security validation and multi-network support.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Union
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import os
from pathlib import Path

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    from eth_account import Account
    from eth_utils import is_address, to_checksum_address, to_wei, from_wei
    import aiohttp
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    # Create mock classes for when Web3 is not available
    class Web3:
        class HTTPProvider:
            def __init__(self, url): pass
        def __init__(self, provider): pass
        @property
        def eth(self): return self
        @property
        def middleware_onion(self): return self
        def inject(self, middleware, layer): pass
        def block_number(self): return 0
        def chain_id(self): return 1
        def get_balance(self, address): return 0
    
    class Account:
        pass
    
    def geth_poa_middleware(): pass
    def is_address(address): return len(address) == 42 and address.startswith('0x')
    def to_checksum_address(address): return address.lower()  
    def to_wei(amount, unit): return int(amount * 10**18)
    def from_wei(amount, unit): return float(amount / 10**18)

from app.utils.logger import setup_logger, get_trading_logger, get_performance_logger, get_trading_logger, get_performance_logger
from app.core.exceptions import (
    WalletError, 
    NetworkError, 
    InsufficientFundsError,
    ValidationError
)

logger = setup_logger(__name__, "trading")


class WalletType(str, Enum):
    """Supported wallet types."""
    METAMASK = "metamask"
    WALLET_CONNECT = "wallet_connect"
    COINBASE_WALLET = "coinbase_wallet"
    TRUST_WALLET = "trust_wallet"
    PRIVATE_KEY = "private_key"


class NetworkType(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"


class ConnectionStatus(str, Enum):
    """Wallet connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    UNAUTHORIZED = "unauthorized"
    INSUFFICIENT_FUNDS = "insufficient_funds"


@dataclass
class NetworkConfig:
    """Network configuration data."""
    name: str
    chain_id: int
    rpc_url: str
    explorer_url: str
    native_token: str
    native_decimals: int
    gas_price_api: Optional[str] = None
    supports_eip1559: bool = True
    
    @classmethod
    def get_default_configs(cls) -> Dict[NetworkType, 'NetworkConfig']:
        """Get default network configurations with fallback RPCs."""
        return {
            NetworkType.ETHEREUM: cls(
                name="Ethereum Mainnet",
                chain_id=1,
                rpc_url=os.getenv("ETHEREUM_RPC_URL", "https://rpc.ankr.com/eth"),
                explorer_url="https://etherscan.io",
                native_token="ETH",
                native_decimals=18,
                gas_price_api="https://api.etherscan.io/api?module=gastracker&action=gasoracle",
                supports_eip1559=True
            ),
            NetworkType.POLYGON: cls(
                name="Polygon Mainnet",
                chain_id=137,
                rpc_url=os.getenv("POLYGON_RPC_URL", "https://rpc.ankr.com/polygon"),
                explorer_url="https://polygonscan.com",
                native_token="MATIC",
                native_decimals=18,
                gas_price_api="https://api.polygonscan.com/api?module=gastracker&action=gasoracle",
                supports_eip1559=True
            ),
            NetworkType.BSC: cls(
                name="Binance Smart Chain",
                chain_id=56,
                rpc_url=os.getenv("BSC_RPC_URL", "https://rpc.ankr.com/bsc"),
                explorer_url="https://bscscan.com",
                native_token="BNB",
                native_decimals=18,
                gas_price_api="https://api.bscscan.com/api?module=gastracker&action=gasoracle",
                supports_eip1559=False
            ),
            NetworkType.ARBITRUM: cls(
                name="Arbitrum One",
                chain_id=42161,
                rpc_url=os.getenv("ARBITRUM_RPC_URL", "https://rpc.ankr.com/arbitrum"),
                explorer_url="https://arbiscan.io",
                native_token="ETH",
                native_decimals=18,
                supports_eip1559=True
            )
        }


@dataclass
class WalletBalance:
    """Wallet balance information."""
    network: NetworkType
    native_balance: Decimal
    native_symbol: str
    usd_value: Optional[Decimal] = None
    token_balances: Dict[str, Decimal] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WalletConnection:
    """Wallet connection state."""
    connection_id: str
    wallet_type: WalletType
    wallet_address: str
    connected_networks: Dict[NetworkType, bool]
    balances: Dict[NetworkType, WalletBalance]
    status: ConnectionStatus
    last_activity: datetime
    session_expires: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        """Check if connection is active."""
        if self.status != ConnectionStatus.CONNECTED:
            return False
        if self.session_expires and datetime.utcnow() > self.session_expires:
            return False
        return True


class WalletConnectionManager:
    """
    Professional wallet connection manager for DEX trading bot.
    
    Handles MetaMask, WalletConnect, and other wallet integrations with
    comprehensive security validation and multi-network support.
    """
    
    def __init__(self):
        """Initialize wallet connection manager."""
        self.network_configs = NetworkConfig.get_default_configs()
        self.web3_instances: Dict[NetworkType, Web3] = {}
        self.active_connections: Dict[str, WalletConnection] = {}
        self.connection_callbacks: List[Callable] = []
        self.balance_update_callbacks: List[Callable] = []
        
        # Security settings
        self.max_concurrent_connections = 10
        self.session_timeout_minutes = 30
        self.balance_cache_minutes = 5
        
        logger.info("[EMOJI] Wallet Connection Manager initialized")
    
    async def initialize_networks(self, networks: Optional[List[NetworkType]] = None) -> bool:
        """
        Initialize blockchain network connections.
        
        Args:
            networks: List of networks to initialize (default: all supported)
            
        Returns:
            bool: True if initialization successful
            
        Raises:
            NetworkError: If network initialization fails
        """
        try:
            logger.info("[API] Initializing blockchain network connections...")
            
            if networks is None:
                networks = list(self.network_configs.keys())
            
            initialization_results = []
            
            for network in networks:
                try:
                    result = await self._initialize_single_network(network)
                    initialization_results.append((network, result))
                    
                    if result:
                        logger.info(f"[OK] {network.value} network initialized")
                    else:
                        logger.warning(f"[WARN] {network.value} network initialization failed")
                        
                except Exception as e:
                    logger.error(f"[ERROR] {network.value} network error: {e}")
                    initialization_results.append((network, False))
            
            # Check if at least one network was initialized
            successful_networks = [net for net, success in initialization_results if success]
            
            if not successful_networks:
                raise NetworkError("No networks could be initialized")
            
            logger.info(f"[TARGET] Network initialization complete: {len(successful_networks)}/{len(networks)} networks ready")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Network initialization failed: {e}")
            raise NetworkError(f"Failed to initialize networks: {e}")
    
    async def _initialize_single_network(self, network: NetworkType) -> bool:
        """Initialize a single blockchain network."""
        try:
            config = self.network_configs[network]
            
            # Create Web3 instance with better error handling
            try:
                web3 = Web3(Web3.HTTPProvider(config.rpc_url))
            except Exception as e:
                logger.error(f"[ERROR] Failed to create Web3 instance for {network.value}: {e}")
                return False
            
            # Add PoA middleware for networks that need it
            if network in [NetworkType.BSC, NetworkType.POLYGON]:
                try:
                    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                except Exception as e:
                    logger.warning(f"[WARN] Failed to add PoA middleware for {network.value}: {e}")
            
            # Test connection with timeout and retries
            try:
                # Use async wrapper for Web3 calls
                latest_block = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, lambda: web3.eth.block_number
                    ),
                    timeout=10.0  # 10 second timeout
                )
                
                if latest_block == 0:
                    logger.warning(f"[WARN] {network.value} returned block 0")
                    return False
                
            except asyncio.TimeoutError:
                logger.error(f"[ERROR] {network.value} connection timeout")
                return False
            except Exception as e:
                logger.error(f"[ERROR] {network.value} block number check failed: {e}")
                return False
            
            # Verify chain ID with timeout
            try:
                chain_id = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, lambda: web3.eth.chain_id
                    ),
                    timeout=5.0
                )
                
                if chain_id != config.chain_id:
                    logger.warning(
                        f"[WARN] {network.value} chain ID mismatch: "
                        f"expected {config.chain_id}, got {chain_id}"
                    )
                    return False
                
            except asyncio.TimeoutError:
                logger.error(f"[ERROR] {network.value} chain ID check timeout")
                return False
            except Exception as e:
                logger.error(f"[ERROR] {network.value} chain ID check failed: {e}")
                return False
            
            # Store successful connection
            self.web3_instances[network] = web3
            
            logger.info(
                f"[OK] {network.value} connected - Block: {latest_block}, Chain ID: {chain_id}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize {network.value}: {e}")
            return False
    
    async def connect_metamask(
        self, 
        wallet_address: str,
        requested_networks: Optional[List[NetworkType]] = None
    ) -> WalletConnection:
        """
        Connect MetaMask wallet.
        
        Args:
            wallet_address: The wallet address to connect
            requested_networks: Networks to connect to
            
        Returns:
            WalletConnection: Connection information
            
        Raises:
            WalletError: If connection fails
            ValidationError: If wallet address is invalid
        """
        try:
            logger.info(f"🦊 Connecting MetaMask wallet: {wallet_address[:10]}...")
            
            # Validate wallet address
            if not self._validate_wallet_address(wallet_address):
                raise ValidationError(f"Invalid wallet address: {wallet_address}")
            
            # Check connection limits
            if len(self.active_connections) >= self.max_concurrent_connections:
                raise WalletError("Maximum concurrent connections reached")
            
            # Normalize address
            normalized_address = to_checksum_address(wallet_address)
            
            # Create connection ID
            connection_id = str(uuid.uuid4())
            
            # Set default networks if none specified
            if requested_networks is None:
                requested_networks = [NetworkType.ETHEREUM, NetworkType.POLYGON]
            
            # Verify network availability
            available_networks = {}
            for network in requested_networks:
                if network in self.web3_instances:
                    available_networks[network] = True
                else:
                    logger.warning(f"[WARN] Network {network.value} not available")
                    available_networks[network] = False
            
            # Get wallet balances
            balances = {}
            for network, is_available in available_networks.items():
                if is_available:
                    try:
                        balance = await self._get_wallet_balance(network, normalized_address)
                        balances[network] = balance
                    except Exception as e:
                        logger.warning(f"[WARN] Failed to get {network.value} balance: {e}")
                        balances[network] = WalletBalance(
                            network=network,
                            native_balance=Decimal("0"),
                            native_symbol=self.network_configs[network].native_token
                        )
            
            # Create wallet connection
            connection = WalletConnection(
                connection_id=connection_id,
                wallet_type=WalletType.METAMASK,
                wallet_address=normalized_address,
                connected_networks=available_networks,
                balances=balances,
                status=ConnectionStatus.CONNECTED,
                last_activity=datetime.utcnow(),
                session_expires=datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
            )
            
            # Store connection
            self.active_connections[connection_id] = connection
            
            # Notify callbacks
            await self._notify_connection_callbacks("connected", connection)
            
            logger.info(
                f"[OK] MetaMask connected: {normalized_address[:10]}... "
                f"({len([n for n, a in available_networks.items() if a])} networks)"
            )
            
            return connection
            
        except Exception as e:
            logger.error(f"[ERROR] MetaMask connection failed: {e}")
            raise WalletError(f"Failed to connect MetaMask: {e}")
    
    async def connect_wallet_connect(
        self,
        wallet_address: str,
        session_data: Optional[Dict[str, Any]] = None
    ) -> WalletConnection:
        """
        Connect WalletConnect wallet.
        
        Args:
            wallet_address: The wallet address to connect
            session_data: WalletConnect session data
            
        Returns:
            WalletConnection: Connection information
            
        Raises:
            WalletError: If connection fails
        """
        try:
            logger.info(f"[EMOJI] Connecting WalletConnect wallet: {wallet_address[:10]}...")
            
            # Validate wallet address
            if not self._validate_wallet_address(wallet_address):
                raise ValidationError(f"Invalid wallet address: {wallet_address}")
            
            # Normalize address
            normalized_address = to_checksum_address(wallet_address)
            
            # Create connection ID
            connection_id = str(uuid.uuid4())
            
            # Default to Ethereum for WalletConnect
            requested_networks = [NetworkType.ETHEREUM]
            
            # Get balances
            balances = {}
            for network in requested_networks:
                if network in self.web3_instances:
                    try:
                        balance = await self._get_wallet_balance(network, normalized_address)
                        balances[network] = balance
                    except Exception as e:
                        logger.warning(f"[WARN] Failed to get {network.value} balance: {e}")
            
            # Create connection
            connection = WalletConnection(
                connection_id=connection_id,
                wallet_type=WalletType.WALLET_CONNECT,
                wallet_address=normalized_address,
                connected_networks={net: True for net in requested_networks},
                balances=balances,
                status=ConnectionStatus.CONNECTED,
                last_activity=datetime.utcnow(),
                session_expires=datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
            )
            
            # Store connection
            self.active_connections[connection_id] = connection
            
            # Notify callbacks
            await self._notify_connection_callbacks("connected", connection)
            
            logger.info(f"[OK] WalletConnect connected: {normalized_address[:10]}...")
            return connection
            
        except Exception as e:
            logger.error(f"[ERROR] WalletConnect connection failed: {e}")
            raise WalletError(f"Failed to connect WalletConnect: {e}")
    
    async def disconnect_wallet(self, connection_id: str) -> bool:
        """
        Disconnect a wallet.
        
        Args:
            connection_id: Connection ID to disconnect
            
        Returns:
            bool: True if disconnection successful
        """
        try:
            if connection_id not in self.active_connections:
                logger.warning(f"[WARN] Connection {connection_id} not found")
                return False
            
            connection = self.active_connections[connection_id]
            
            # Update status
            connection.status = ConnectionStatus.DISCONNECTED
            connection.last_activity = datetime.utcnow()
            
            # Notify callbacks
            await self._notify_connection_callbacks("disconnected", connection)
            
            # Remove connection
            del self.active_connections[connection_id]
            
            logger.info(f"[OK] Wallet disconnected: {connection.wallet_address[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Wallet disconnection failed: {e}")
            return False
    
    async def verify_wallet_access(
        self, 
        connection_id: str,
        network: NetworkType,
        required_balance_eth: Optional[Decimal] = None
    ) -> bool:
        """
        Verify wallet access and sufficient funds.
        
        Args:
            connection_id: Connection ID to verify
            network: Network to verify on
            required_balance_eth: Minimum required balance in ETH
            
        Returns:
            bool: True if verification successful
            
        Raises:
            WalletError: If verification fails
        """
        try:
            if connection_id not in self.active_connections:
                raise WalletError(f"Connection {connection_id} not found")
            
            connection = self.active_connections[connection_id]
            
            # Check connection status
            if not connection.is_active:
                raise WalletError("Wallet connection expired or inactive")
            
            # Check network availability
            if network not in connection.connected_networks or not connection.connected_networks[network]:
                raise WalletError(f"Network {network.value} not connected")
            
            # Update balance
            try:
                balance = await self._get_wallet_balance(network, connection.wallet_address)
                connection.balances[network] = balance
                connection.last_activity = datetime.utcnow()
            except Exception as e:
                logger.warning(f"[WARN] Failed to update balance: {e}")
            
            # Check minimum balance if required
            if required_balance_eth:
                current_balance = connection.balances.get(network)
                if not current_balance or current_balance.native_balance < required_balance_eth:
                    raise InsufficientFundsError(
                        f"Insufficient funds: required {required_balance_eth} "
                        f"{self.network_configs[network].native_token}, "
                        f"available {current_balance.native_balance if current_balance else 0}"
                    )
            
            logger.debug(f"[OK] Wallet access verified: {connection.wallet_address[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Wallet verification failed: {e}")
            raise WalletError(f"Wallet verification failed: {e}")
    
    async def _get_wallet_balance(self, network: NetworkType, wallet_address: str) -> WalletBalance:
        """Get wallet balance for a specific network."""
        try:
            if network not in self.web3_instances:
                raise NetworkError(f"Network {network.value} not available")
            
            web3 = self.web3_instances[network]
            config = self.network_configs[network]
            
            # Get native token balance
            balance_wei = await asyncio.get_event_loop().run_in_executor(
                None, web3.eth.get_balance, wallet_address
            )
            
            balance_eth = Decimal(from_wei(balance_wei, 'ether'))
            
            return WalletBalance(
                network=network,
                native_balance=balance_eth,
                native_symbol=config.native_token,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get {network.value} balance: {e}")
            raise WalletError(f"Failed to get balance: {e}")
    
    def _validate_wallet_address(self, address: str) -> bool:
        """Validate Ethereum wallet address format."""
        try:
            return is_address(address)
        except Exception:
            return False
    
    async def _notify_connection_callbacks(self, event: str, connection: WalletConnection) -> None:
        """Notify registered callbacks of connection events."""
        for callback in self.connection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event, connection)
                else:
                    callback(event, connection)
            except Exception as e:
                logger.warning(f"[WARN] Callback error: {e}")
    
    def register_connection_callback(self, callback: Callable) -> None:
        """Register callback for connection events."""
        self.connection_callbacks.append(callback)
    
    def get_active_connections(self) -> Dict[str, WalletConnection]:
        """Get all active wallet connections."""
        # Filter for active connections only
        active = {
            conn_id: conn for conn_id, conn in self.active_connections.items()
            if conn.is_active
        }
        return active
    
    def get_connection_by_address(self, wallet_address: str) -> Optional[WalletConnection]:
        """Get connection by wallet address."""
        normalized_address = to_checksum_address(wallet_address)
        
        for connection in self.active_connections.values():
            if connection.wallet_address == normalized_address and connection.is_active:
                return connection
        
        return None
    
    async def cleanup_expired_connections(self) -> int:
        """Clean up expired wallet connections."""
        expired_connections = []
        
        for conn_id, connection in self.active_connections.items():
            if not connection.is_active:
                expired_connections.append(conn_id)
        
        for conn_id in expired_connections:
            await self.disconnect_wallet(conn_id)
        
        if expired_connections:
            logger.info(f"🧹 Cleaned up {len(expired_connections)} expired connections")
        
        return len(expired_connections)


# Global wallet connection manager instance
_wallet_connection_manager: Optional[WalletConnectionManager] = None


def get_wallet_connection_manager() -> WalletConnectionManager:
    """Get global wallet connection manager instance."""
    global _wallet_connection_manager
    
    if _wallet_connection_manager is None:
        _wallet_connection_manager = WalletConnectionManager()
    
    return _wallet_connection_manager


async def initialize_wallet_system(networks: Optional[List[NetworkType]] = None) -> bool:
    """
    Initialize the wallet connection system.
    
    Args:
        networks: Networks to initialize
        
    Returns:
        bool: True if initialization successful
    """
    try:
        manager = get_wallet_connection_manager()
        return await manager.initialize_networks(networks)
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize wallet system: {e}")
        return False