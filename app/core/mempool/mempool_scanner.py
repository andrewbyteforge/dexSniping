"""
File: app/core/mempool/mempool_scanner.py

Real-time mempool monitoring for token launch detection.
Monitors pending transactions to detect liquidity additions before they're mined.
Enables Block 0 token sniping capabilities.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
import websockets
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_abi import decode_abi
import re

from app.core.blockchain.base_chain import BaseChain
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__)


class MempoolScannerError(DexSnipingException):
    """Exception raised when mempool scanning operations fail."""
    pass


@dataclass
class PendingTransaction:
    """Data class for pending transaction information."""
    hash: str
    from_address: str
    to_address: str
    value: int
    gas: int
    gas_price: int
    input_data: str
    timestamp: float
    block_number: Optional[int] = None
    
    @property
    def gas_price_gwei(self) -> float:
        """Get gas price in Gwei."""
        return self.gas_price / 10**9


@dataclass
class LiquidityAddEvent:
    """Data class for detected liquidity addition events."""
    token_address: str
    pair_address: str
    dex: str
    token0: str
    token1: str
    amount0: int
    amount1: int
    liquidity: int
    pending_tx: PendingTransaction
    detected_at: float = field(default_factory=time.time)
    
    @property
    def is_new_token(self) -> bool:
        """Check if this involves a new token (not WETH/stablecoin pair)."""
        weth_addresses = {
            '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
            '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',  # WMATIC
        }
        stablecoin_addresses = {
            '0xA0b86a33E6417c4C79f4765C0a8C1E9D07C82e0e',  # USDC
            '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT
            '0x6B175474E89094C44Da98b954EedeAC495271d0F',  # DAI
        }
        
        known_tokens = weth_addresses | stablecoin_addresses
        return (self.token0 not in known_tokens and 
                self.token1 not in known_tokens and
                self.token0 != self.token1)


@dataclass
class MempoolStats:
    """Statistics for mempool scanning operations."""
    total_transactions_scanned: int = 0
    liquidity_adds_detected: int = 0
    new_tokens_detected: int = 0
    snipe_opportunities: int = 0
    successful_snipes: int = 0
    failed_snipes: int = 0
    average_detection_time_ms: float = 0.0
    websocket_reconnections: int = 0
    last_activity: Optional[datetime] = None


class MempoolScanner:
    """
    Advanced mempool scanner for real-time token launch detection.
    
    Features:
    - WebSocket connections to multiple nodes for redundancy
    - Real-time pending transaction monitoring
    - Liquidity addition detection across major DEXs
    - Block 0 sniping opportunity identification
    - Intelligent filtering and validation
    - Performance monitoring and statistics
    """
    
    def __init__(self, network: str, websocket_urls: List[str]):
        """
        Initialize mempool scanner.
        
        Args:
            network: Network name (ethereum, polygon, etc.)
            websocket_urls: List of WebSocket RPC URLs for redundancy
        """
        self.network = network
        self.websocket_urls = websocket_urls
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.stats = MempoolStats()
        
        # WebSocket connections
        self.websockets: Dict[str, Any] = {}
        self.active_connections: Set[str] = set()
        
        # Event handlers
        self.liquidity_add_handlers: List[Callable] = []
        self.new_token_handlers: List[Callable] = []
        
        # Filtering configuration
        self.min_gas_price_gwei = getattr(settings, 'min_gas_price_gwei', 1)
        self.max_gas_price_gwei = getattr(settings, 'max_gas_price_gwei', 1000)
        self.min_liquidity_value = getattr(settings, 'min_liquidity_usd_int', 1000)
        
        # DEX contract addresses and function signatures
        self.dex_contracts = self._load_dex_contracts()
        self.liquidity_signatures = self._load_liquidity_signatures()
        
        # State tracking
        self._scanning = False
        self._shutdown = False
        
        logger.info(f"MempoolScanner initialized for {network} with {len(websocket_urls)} endpoints")
    
    def _load_dex_contracts(self) -> Dict[str, Dict[str, str]]:
        """Load DEX contract addresses for the network."""
        contracts = {
            'ethereum': {
                'uniswap_v2_router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'uniswap_v3_router': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'sushiswap_router': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
                'uniswap_v2_factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                'uniswap_v3_factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
            },
            'polygon': {
                'quickswap_router': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
                'sushiswap_router': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
                'uniswap_v3_router': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
            },
            'bsc': {
                'pancakeswap_router': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
                'biswap_router': '0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8',
            }
        }
        return contracts.get(self.network, {})
    
    def _load_liquidity_signatures(self) -> Dict[str, str]:
        """Load function signatures for liquidity operations."""
        return {
            # Uniswap V2 style
            'addLiquidity': '0xe8e33700',
            'addLiquidityETH': '0xf305d719',
            
            # Uniswap V3 style
            'mint': '0x6a761202',
            'increaseLiquidity': '0x219f5d17',
            
            # Factory contract
            'createPair': '0xc9c65396',
        }
    
    async def start_scanning(self) -> None:
        """
        Start mempool scanning across all WebSocket connections.
        
        Raises:
            MempoolScannerError: If scanning fails to start
        """
        if self._scanning:
            logger.warning("Mempool scanning already in progress")
            return
        
        try:
            logger.info(f"Starting mempool scanning for {self.network}")
            self._scanning = True
            self._shutdown = False
            
            # Start WebSocket connections
            connection_tasks = []
            for url in self.websocket_urls:
                task = asyncio.create_task(self._maintain_websocket_connection(url))
                connection_tasks.append(task)
            
            # Start monitoring task
            monitoring_task = asyncio.create_task(self._monitor_connections())
            
            # Wait for at least one successful connection
            await asyncio.sleep(2)
            if not self.active_connections:
                raise MempoolScannerError("Failed to establish any WebSocket connections")
            
            logger.info(f"Mempool scanning started with {len(self.active_connections)} active connections")
            
            # Keep all tasks running
            await asyncio.gather(*connection_tasks, monitoring_task, return_exceptions=True)
            
        except Exception as e:
            self._scanning = False
            logger.error(f"Failed to start mempool scanning: {e}")
            raise MempoolScannerError(f"Scanning startup failed: {e}")
    
    async def stop_scanning(self) -> None:
        """Stop mempool scanning and close all connections."""
        logger.info("Stopping mempool scanning...")
        self._shutdown = True
        self._scanning = False
        
        # Close all WebSocket connections
        for url, ws in self.websockets.items():
            try:
                if ws and not ws.closed:
                    await ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket {url}: {e}")
        
        self.websockets.clear()
        self.active_connections.clear()
        logger.info("Mempool scanning stopped")
    
    async def _maintain_websocket_connection(self, url: str) -> None:
        """
        Maintain persistent WebSocket connection with automatic reconnection.
        
        Args:
            url: WebSocket URL to connect to
        """
        reconnect_delay = 1
        max_reconnect_delay = 60
        
        while not self._shutdown:
            try:
                logger.info(f"Connecting to WebSocket: {url}")
                
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    self.websockets[url] = websocket
                    self.active_connections.add(url)
                    reconnect_delay = 1  # Reset delay on successful connection
                    
                    # Subscribe to pending transactions
                    await self._subscribe_to_pending_transactions(websocket)
                    
                    logger.info(f"Successfully connected to {url}")
                    
                    # Listen for messages
                    await self._listen_for_messages(websocket, url)
                    
            except Exception as e:
                logger.error(f"WebSocket connection error for {url}: {e}")
                self.stats.websocket_reconnections += 1
                
                # Remove from active connections
                self.active_connections.discard(url)
                if url in self.websockets:
                    del self.websockets[url]
                
                if not self._shutdown:
                    logger.info(f"Reconnecting to {url} in {reconnect_delay}s...")
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    
    async def _subscribe_to_pending_transactions(self, websocket) -> None:
        """
        Subscribe to pending transaction notifications.
        
        Args:
            websocket: WebSocket connection
        """
        subscription_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions", True]  # Get full transaction objects
        }
        
        await websocket.send(json.dumps(subscription_request))
        
        # Wait for subscription confirmation
        response = await websocket.recv()
        response_data = json.loads(response)
        
        if "result" in response_data:
            logger.info(f"Subscribed to pending transactions: {response_data['result']}")
        else:
            raise MempoolScannerError(f"Failed to subscribe: {response_data}")
    
    async def _listen_for_messages(self, websocket, url: str) -> None:
        """
        Listen for WebSocket messages and process pending transactions.
        
        Args:
            websocket: WebSocket connection
            url: WebSocket URL for identification
        """
        try:
            async for message in websocket:
                if self._shutdown:
                    break
                
                try:
                    data = json.loads(message)
                    await self._process_websocket_message(data, url)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from {url}: {e}")
                except Exception as e:
                    logger.error(f"Error processing message from {url}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"WebSocket connection closed: {url}")
        except Exception as e:
            logger.error(f"Error listening to {url}: {e}")
        finally:
            self.active_connections.discard(url)
    
    async def _process_websocket_message(self, data: Dict[str, Any], url: str) -> None:
        """
        Process incoming WebSocket message.
        
        Args:
            data: Message data
            url: Source WebSocket URL
        """
        # Skip subscription confirmations and errors
        if "method" not in data or data["method"] != "eth_subscription":
            return
        
        # Extract transaction data
        if "params" not in data or "result" not in data["params"]:
            return
        
        tx_data = data["params"]["result"]
        if not isinstance(tx_data, dict):
            return
        
        # Create pending transaction object
        try:
            pending_tx = self._parse_pending_transaction(tx_data)
            if pending_tx:
                await self._analyze_pending_transaction(pending_tx)
                
        except Exception as e:
            logger.warning(f"Error parsing transaction: {e}")
    
    def _parse_pending_transaction(self, tx_data: Dict[str, Any]) -> Optional[PendingTransaction]:
        """
        Parse raw transaction data into PendingTransaction object.
        
        Args:
            tx_data: Raw transaction data from WebSocket
            
        Returns:
            PendingTransaction object or None if invalid
        """
        try:
            # Validate required fields
            required_fields = ['hash', 'from', 'to', 'value', 'gas', 'gasPrice', 'input']
            if not all(field in tx_data for field in required_fields):
                return None
            
            # Convert hex values to integers
            value = int(tx_data['value'], 16) if tx_data['value'] else 0
            gas = int(tx_data['gas'], 16)
            gas_price = int(tx_data['gasPrice'], 16)
            
            # Basic filtering
            if gas_price < self.min_gas_price_gwei * 10**9:
                return None
            if gas_price > self.max_gas_price_gwei * 10**9:
                return None
            
            pending_tx = PendingTransaction(
                hash=tx_data['hash'],
                from_address=tx_data['from'],
                to_address=tx_data['to'] or '',
                value=value,
                gas=gas,
                gas_price=gas_price,
                input_data=tx_data['input'],
                timestamp=time.time()
            )
            
            self.stats.total_transactions_scanned += 1
            return pending_tx
            
        except (ValueError, KeyError) as e:
            logger.debug(f"Error parsing transaction: {e}")
            return None
    
    async def _analyze_pending_transaction(self, pending_tx: PendingTransaction) -> None:
        """
        Analyze pending transaction for liquidity addition patterns.
        
        Args:
            pending_tx: Pending transaction to analyze
        """
        try:
            # Check if transaction is to a known DEX contract
            if pending_tx.to_address.lower() not in [addr.lower() for addr in self.dex_contracts.values()]:
                return
            
            # Check if transaction contains liquidity-related function calls
            if not self._is_liquidity_transaction(pending_tx.input_data):
                return
            
            # Decode and analyze transaction data
            liquidity_event = await self._decode_liquidity_transaction(pending_tx)
            if liquidity_event:
                await self._handle_liquidity_event(liquidity_event)
                
        except Exception as e:
            logger.warning(f"Error analyzing transaction {pending_tx.hash[:10]}: {e}")
    
    def _is_liquidity_transaction(self, input_data: str) -> bool:
        """
        Check if transaction input contains liquidity-related function calls.
        
        Args:
            input_data: Transaction input data
            
        Returns:
            True if this appears to be a liquidity transaction
        """
        if not input_data or len(input_data) < 10:
            return False
        
        # Extract function selector (first 4 bytes)
        function_selector = input_data[:10].lower()
        
        # Check against known liquidity function signatures
        return function_selector in [sig.lower() for sig in self.liquidity_signatures.values()]
    
    async def _decode_liquidity_transaction(self, pending_tx: PendingTransaction) -> Optional[LiquidityAddEvent]:
        """
        Decode liquidity transaction and extract relevant information.
        
        Args:
            pending_tx: Pending transaction to decode
            
        Returns:
            LiquidityAddEvent or None if decoding fails
        """
        try:
            # This is a simplified decoder - in production, you'd use proper ABI decoding
            function_selector = pending_tx.input_data[:10].lower()
            
            # Handle addLiquidityETH (most common for new tokens)
            if function_selector == self.liquidity_signatures['addLiquidityETH'].lower():
                return await self._decode_add_liquidity_eth(pending_tx)
            
            # Handle addLiquidity
            elif function_selector == self.liquidity_signatures['addLiquidity'].lower():
                return await self._decode_add_liquidity(pending_tx)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error decoding liquidity transaction: {e}")
            return None
    
    async def _decode_add_liquidity_eth(self, pending_tx: PendingTransaction) -> Optional[LiquidityAddEvent]:
        """
        Decode addLiquidityETH transaction.
        
        Args:
            pending_tx: Pending transaction
            
        Returns:
            LiquidityAddEvent or None
        """
        try:
            # addLiquidityETH parameters:
            # address token, uint amountTokenDesired, uint amountTokenMin, 
            # uint amountETHMin, address to, uint deadline
            
            input_data = pending_tx.input_data[10:]  # Remove function selector
            
            # Simplified decoding - extract token address (first parameter)
            if len(input_data) >= 64:
                token_address = '0x' + input_data[24:64]  # Extract address from first 32 bytes
                
                # Create liquidity event
                liquidity_event = LiquidityAddEvent(
                    token_address=Web3.toChecksumAddress(token_address),
                    pair_address='',  # Would need to calculate or query
                    dex=self._identify_dex(pending_tx.to_address),
                    token0=token_address,
                    token1='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
                    amount0=0,  # Would decode from parameters
                    amount1=pending_tx.value,  # ETH amount
                    liquidity=0,  # Would calculate
                    pending_tx=pending_tx
                )
                
                return liquidity_event
            
            return None
            
        except Exception as e:
            logger.debug(f"Error decoding addLiquidityETH: {e}")
            return None
    
    async def _decode_add_liquidity(self, pending_tx: PendingTransaction) -> Optional[LiquidityAddEvent]:
        """
        Decode addLiquidity transaction.
        
        Args:
            pending_tx: Pending transaction
            
        Returns:
            LiquidityAddEvent or None
        """
        # Similar to addLiquidityETH but for token-token pairs
        # Implementation would be similar but handle two token addresses
        return None
    
    def _identify_dex(self, contract_address: str) -> str:
        """
        Identify which DEX based on contract address.
        
        Args:
            contract_address: Contract address
            
        Returns:
            DEX name
        """
        address_lower = contract_address.lower()
        
        for dex_name, dex_address in self.dex_contracts.items():
            if dex_address.lower() == address_lower:
                return dex_name.replace('_router', '').replace('_factory', '')
        
        return 'unknown'
    
    async def _handle_liquidity_event(self, liquidity_event: LiquidityAddEvent) -> None:
        """
        Handle detected liquidity addition event.
        
        Args:
            liquidity_event: Detected liquidity event
        """
        try:
            self.stats.liquidity_adds_detected += 1
            self.stats.last_activity = datetime.utcnow()
            
            # Check if this is a new token
            if liquidity_event.is_new_token:
                self.stats.new_tokens_detected += 1
                self.stats.snipe_opportunities += 1
                
                logger.info(
                    f"🚀 NEW TOKEN DETECTED: {liquidity_event.token_address} "
                    f"on {liquidity_event.dex} (Gas: {liquidity_event.pending_tx.gas_price_gwei:.1f} gwei)"
                )
                
                # Cache the opportunity
                await self._cache_snipe_opportunity(liquidity_event)
                
                # Notify handlers
                await self._notify_new_token_handlers(liquidity_event)
            
            # Notify liquidity handlers
            await self._notify_liquidity_handlers(liquidity_event)
            
        except Exception as e:
            logger.error(f"Error handling liquidity event: {e}")
    
    async def _cache_snipe_opportunity(self, liquidity_event: LiquidityAddEvent) -> None:
        """
        Cache snipe opportunity for quick access.
        
        Args:
            liquidity_event: Liquidity event to cache
        """
        try:
            cache_key = f"snipe_opportunity_{liquidity_event.token_address}"
            cache_data = {
                'token_address': liquidity_event.token_address,
                'dex': liquidity_event.dex,
                'detected_at': liquidity_event.detected_at,
                'tx_hash': liquidity_event.pending_tx.hash,
                'gas_price_gwei': liquidity_event.pending_tx.gas_price_gwei,
                'network': self.network
            }
            
            await cache_manager.set(
                cache_key,
                cache_data,
                ttl=300,  # 5 minutes
                namespace='snipe_opportunities'
            )
            
        except Exception as e:
            logger.warning(f"Error caching snipe opportunity: {e}")
    
    async def _notify_liquidity_handlers(self, liquidity_event: LiquidityAddEvent) -> None:
        """Notify all registered liquidity event handlers."""
        for handler in self.liquidity_add_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(liquidity_event)
                else:
                    handler(liquidity_event)
            except Exception as e:
                logger.error(f"Error in liquidity handler: {e}")
    
    async def _notify_new_token_handlers(self, liquidity_event: LiquidityAddEvent) -> None:
        """Notify all registered new token handlers."""
        for handler in self.new_token_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(liquidity_event)
                else:
                    handler(liquidity_event)
            except Exception as e:
                logger.error(f"Error in new token handler: {e}")
    
    async def _monitor_connections(self) -> None:
        """Monitor WebSocket connections and log statistics."""
        while not self._shutdown:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                if self.active_connections:
                    logger.info(
                        f"Mempool Monitor [{self.network}]: "
                        f"{len(self.active_connections)} connections, "
                        f"{self.stats.total_transactions_scanned} txs scanned, "
                        f"{self.stats.new_tokens_detected} new tokens detected"
                    )
                else:
                    logger.warning(f"No active WebSocket connections for {self.network}")
                    
            except Exception as e:
                logger.error(f"Error in connection monitoring: {e}")
    
    def register_liquidity_handler(self, handler: Callable) -> None:
        """
        Register handler for liquidity addition events.
        
        Args:
            handler: Callback function for liquidity events
        """
        self.liquidity_add_handlers.append(handler)
        logger.info(f"Registered liquidity handler: {handler.__name__}")
    
    def register_new_token_handler(self, handler: Callable) -> None:
        """
        Register handler for new token detection events.
        
        Args:
            handler: Callback function for new token events
        """
        self.new_token_handlers.append(handler)
        logger.info(f"Registered new token handler: {handler.__name__}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get mempool scanning statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'network': self.network,
            'active_connections': len(self.active_connections),
            'total_connections': len(self.websocket_urls),
            'total_transactions_scanned': self.stats.total_transactions_scanned,
            'liquidity_adds_detected': self.stats.liquidity_adds_detected,
            'new_tokens_detected': self.stats.new_tokens_detected,
            'snipe_opportunities': self.stats.snipe_opportunities,
            'successful_snipes': self.stats.successful_snipes,
            'failed_snipes': self.stats.failed_snipes,
            'success_rate': (
                self.stats.successful_snipes / max(1, self.stats.snipe_opportunities) * 100
            ),
            'websocket_reconnections': self.stats.websocket_reconnections,
            'last_activity': self.stats.last_activity.isoformat() if self.stats.last_activity else None,
            'scanning_active': self._scanning
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on mempool scanner.
        
        Returns:
            Health status information
        """
        try:
            active_connections = len(self.active_connections)
            total_connections = len(self.websocket_urls)
            
            # Determine health status
            if active_connections == 0:
                status = "unhealthy"
            elif active_connections < total_connections / 2:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                'status': status,
                'network': self.network,
                'active_connections': active_connections,
                'total_connections': total_connections,
                'connection_ratio': active_connections / max(1, total_connections),
                'scanning_active': self._scanning,
                'last_activity': self.stats.last_activity.isoformat() if self.stats.last_activity else None,
                'total_transactions_scanned': self.stats.total_transactions_scanned,
                'new_tokens_detected': self.stats.new_tokens_detected
            }
            
        except Exception as e:
            logger.error(f"Mempool scanner health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'network': self.network
            }