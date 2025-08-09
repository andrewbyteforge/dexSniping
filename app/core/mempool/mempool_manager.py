"""
File: app/core/mempool/mempool_manager.py

Multi-network mempool monitoring and sniping coordination.
Manages mempool scanners and block zero snipers across multiple chains.
Implements strategic partnerships and community features.
"""

import asyncio
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from app.core.mempool.mempool_scanner import MempoolScanner, LiquidityAddEvent
from app.core.sniping.block_zero_sniper import BlockZeroSniper, SnipeResult
from app.core.blockchain.multi_chain_manager import MultiChainManager
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__, "application")


class MempoolManagerError(DexSnipingException):
    """Exception raised when mempool manager operations fail."""
    pass


@dataclass
class PartnershipConfig:
    """Configuration for strategic partnerships."""
    flashbots_enabled: bool = True
    alchemy_premium: bool = False
    infura_addon: bool = False
    dedicated_nodes: List[str] = field(default_factory=list)
    mev_protection_level: str = 'standard'  # 'basic', 'standard', 'premium'


@dataclass
class CommunityFeatures:
    """Configuration for community building features."""
    open_source_contributions: bool = True
    developer_api_access: bool = True
    trader_feedback_system: bool = True
    content_creator_tools: bool = True
    educational_resources: bool = True
    community_alerts: bool = True


@dataclass
class MonetizationTiers:
    """Optional monetization tier configurations."""
    free_tier: Dict[str, Any] = field(default_factory=lambda: {
        'max_snipes_per_hour': 10,
        'networks': ['ethereum', 'polygon'],
        'basic_analytics': True,
        'community_support': True
    })
    
    premium_tier: Dict[str, Any] = field(default_factory=lambda: {
        'max_snipes_per_hour': 100,
        'networks': 'all',
        'advanced_analytics': True,
        'priority_execution': True,
        'dedicated_support': True,
        'cost_usd_monthly': 29
    })
    
    enterprise_tier: Dict[str, Any] = field(default_factory=lambda: {
        'unlimited_snipes': True,
        'custom_networks': True,
        'white_label_option': True,
        'dedicated_infrastructure': True,
        'custom_integrations': True,
        'cost_usd_monthly': 299
    })


@dataclass
class GlobalStats:
    """Global statistics across all networks and operations."""
    total_transactions_scanned: int = 0
    total_tokens_discovered: int = 0
    total_snipe_attempts: int = 0
    successful_snipes: int = 0
    failed_snipes: int = 0
    active_networks: Set[str] = field(default_factory=set)
    active_scanners: int = 0
    active_snipers: int = 0
    total_volume_sniped_eth: float = 0.0
    average_execution_time_ms: float = 0.0
    uptime_percentage: float = 100.0
    community_contributors: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class MempoolManager:
    """
    Advanced multi-network mempool monitoring and sniping coordination system.
    
    Features:
    - Multi-chain mempool scanning coordination
    - Automated Block 0 sniping across networks
    - Strategic partnership integrations
    - Community building tools and APIs
    - Optional monetization tiers
    - Real-time performance monitoring
    - Educational platform integration
    """
    
    def __init__(self, multi_chain_manager: MultiChainManager):
        """
        Initialize mempool manager.
        
        Args:
            multi_chain_manager: Multi-chain manager instance
        """
        self.multi_chain_manager = multi_chain_manager
        self.circuit_breaker_manager = CircuitBreakerManager()
        
        # Core components
        self.mempool_scanners: Dict[str, MempoolScanner] = {}
        self.block_zero_snipers: Dict[str, BlockZeroSniper] = {}
        
        # Configuration
        self.partnership_config = PartnershipConfig()
        self.community_features = CommunityFeatures()
        self.monetization_tiers = MonetizationTiers()
        
        # Statistics and monitoring
        self.global_stats = GlobalStats()
        self.network_stats: Dict[str, Dict[str, Any]] = {}
        
        # Event handlers and callbacks
        self.token_discovery_callbacks: List[Callable] = []
        self.snipe_completion_callbacks: List[Callable] = []
        self.community_event_callbacks: List[Callable] = []
        
        # Partnership integrations
        self.flashbots_clients: Dict[str, Any] = {}
        self.premium_node_connections: Dict[str, List[str]] = {}
        
        # State management
        self._running = False
        self._shutdown = False
        
        logger.info("MempoolManager initialized with multi-chain coordination")
    
    async def initialize(self, networks: Optional[List[str]] = None) -> None:
        """
        Initialize mempool monitoring across specified networks.
        
        Args:
            networks: List of networks to monitor (all enabled if None)
            
        Raises:
            MempoolManagerError: If initialization fails
        """
        try:
            logger.info("Initializing MempoolManager across networks...")
            
            # Get target networks
            if networks is None:
                networks = list(await self.multi_chain_manager.get_enabled_networks())
            
            # Initialize partnership integrations
            await self._initialize_partnerships()
            
            # Setup mempool scanners for each network
            for network in networks:
                await self._initialize_network_monitoring(network)
            
            # Start global monitoring and coordination
            await self._start_global_coordination()
            
            # Initialize community features
            await self._initialize_community_features()
            
            self._running = True
            self.global_stats.active_networks = set(networks)
            
            logger.info(
                f"MempoolManager initialized successfully across "
                f"{len(networks)} networks: {', '.join(networks)}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize MempoolManager: {e}")
            raise MempoolManagerError(f"Initialization failed: {e}")
    
    async def _initialize_partnerships(self) -> None:
        """Initialize strategic partnership integrations."""
        try:
            logger.info("Initializing strategic partnership integrations...")
            
            # Flashbots Integration for MEV Protection
            if self.partnership_config.flashbots_enabled:
                await self._setup_flashbots_integration()
            
            # Premium Node Providers (Alchemy, Infura)
            await self._setup_premium_node_access()
            
            # DeFi Protocol Partnerships
            await self._setup_defi_integrations()
            
            logger.info("Partnership integrations initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some partnership integrations failed: {e}")
    
    async def _setup_flashbots_integration(self) -> None:
        """Setup Flashbots integration for MEV protection."""
        try:
            # Initialize Flashbots clients for supported networks
            flashbots_networks = ['ethereum']  # Expand as Flashbots supports more chains
            
            for network in flashbots_networks:
                if hasattr(settings, f'{network}_flashbots_key'):
                    # In production, initialize actual Flashbots client
                    self.flashbots_clients[network] = {
                        'enabled': True,
                        'relay_url': 'https://relay.flashbots.net',
                        'private_key': getattr(settings, f'{network}_flashbots_key', ''),
                        'bundle_submissions': 0
                    }
                    
                    logger.info(f"Flashbots client initialized for {network}")
            
        except Exception as e:
            logger.warning(f"Flashbots integration setup failed: {e}")
    
    async def _setup_premium_node_access(self) -> None:
        """Setup premium node provider access for faster mempool data."""
        try:
            # Alchemy Premium Endpoints
            if self.partnership_config.alchemy_premium:
                alchemy_networks = {
                    'ethereum': f'wss://eth-mainnet.g.alchemy.com/v2/{settings.alchemy_api_key}',
                    'polygon': f'wss://polygon-mainnet.g.alchemy.com/v2/{settings.alchemy_api_key}',
                    'arbitrum': f'wss://arb-mainnet.g.alchemy.com/v2/{settings.alchemy_api_key}',
                }
                
                for network, ws_url in alchemy_networks.items():
                    if network not in self.premium_node_connections:
                        self.premium_node_connections[network] = []
                    self.premium_node_connections[network].append(ws_url)
            
            # Infura Add-on Services
            if self.partnership_config.infura_addon:
                infura_networks = {
                    'ethereum': f'wss://mainnet.infura.io/ws/v3/{settings.infura_api_key}',
                    'polygon': f'wss://polygon-mainnet.infura.io/ws/v3/{settings.infura_api_key}',
                }
                
                for network, ws_url in infura_networks.items():
                    if network not in self.premium_node_connections:
                        self.premium_node_connections[network] = []
                    self.premium_node_connections[network].append(ws_url)
            
            # Dedicated Node Connections
            for node_url in self.partnership_config.dedicated_nodes:
                # Parse and categorize dedicated nodes by network
                pass  # Implementation depends on node URL format
            
            logger.info(f"Premium node access configured for {len(self.premium_node_connections)} networks")
            
        except Exception as e:
            logger.warning(f"Premium node setup failed: {e}")
    
    async def _setup_defi_integrations(self) -> None:
        """Setup direct DeFi protocol integrations."""
        try:
            # Example integrations with major protocols
            defi_integrations = {
                'uniswap': {
                    'factory_events': True,
                    'pool_creation_webhooks': True,
                    'v3_concentrated_liquidity': True
                },
                'sushiswap': {
                    'cross_chain_monitoring': True,
                    'onsen_farms_tracking': True
                },
                'curve': {
                    'new_pool_detection': True,
                    'gauge_creation_monitoring': True
                }
            }
            
            logger.info(f"DeFi integrations configured: {list(defi_integrations.keys())}")
            
        except Exception as e:
            logger.warning(f"DeFi integration setup failed: {e}")
    
    async def _initialize_network_monitoring(self, network: str) -> None:
        """
        Initialize mempool monitoring for a specific network.
        
        Args:
            network: Network name to initialize
        """
        try:
            logger.info(f"Initializing mempool monitoring for {network}")
            
            # Get WebSocket URLs for the network
            websocket_urls = await self._get_websocket_urls(network)
            
            # Create mempool scanner
            scanner = MempoolScanner(network, websocket_urls)
            
            # Register event handlers
            scanner.register_new_token_handler(self._handle_new_token_detected)
            scanner.register_liquidity_handler(self._handle_liquidity_event)
            
            self.mempool_scanners[network] = scanner
            
            # Initialize Block 0 sniper if trading is enabled
            if getattr(settings, 'enable_auto_sniping', True):
                await self._initialize_network_sniper(network)
            
            # Start scanning
            asyncio.create_task(scanner.start_scanning())
            
            # Initialize network statistics
            self.network_stats[network] = {
                'scanner_active': True,
                'sniper_active': network in self.block_zero_snipers,
                'tokens_discovered': 0,
                'snipes_attempted': 0,
                'snipes_successful': 0,
                'last_activity': datetime.utcnow()
            }
            
            self.global_stats.active_scanners += 1
            
            logger.info(f"Network monitoring initialized for {network}")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring for {network}: {e}")
            raise
    
    async def _get_websocket_urls(self, network: str) -> List[str]:
        """
        Get WebSocket URLs for a network including premium endpoints.
        
        Args:
            network: Network name
            
        Returns:
            List of WebSocket URLs
        """
        urls = []
        
        # Add premium node connections if available
        if network in self.premium_node_connections:
            urls.extend(self.premium_node_connections[network])
        
        # Add public endpoints as fallback
        public_endpoints = {
            'ethereum': [
                'wss://ethereum.publicnode.com',
                'wss://eth-mainnet.public.blastapi.io'
            ],
            'polygon': [
                'wss://polygon-bor.publicnode.com',
                'wss://polygon-mainnet.public.blastapi.io'
            ],
            'bsc': [
                'wss://bsc.publicnode.com',
                'wss://bsc-mainnet.public.blastapi.io'
            ]
        }
        
        if network in public_endpoints:
            urls.extend(public_endpoints[network])
        
        return urls if urls else ['wss://ethereum.publicnode.com']  # Fallback
    
    async def _initialize_network_sniper(self, network: str) -> None:
        """
        Initialize Block 0 sniper for a network.
        
        Args:
            network: Network name
        """
        try:
            # Get chain instance and private key
            chain = await self.multi_chain_manager.get_chain(network)
            if not chain or not hasattr(chain, 'w3'):
                logger.warning(f"Cannot initialize sniper for {network}: chain not ready")
                return
            
            # Get trading private key (should be securely managed)
            private_key = getattr(settings, f'{network}_trading_private_key', None)
            if not private_key:
                logger.warning(f"No trading private key configured for {network}")
                return
            
            # Create sniper instance
            sniper = BlockZeroSniper(network, chain.w3, private_key)
            self.block_zero_snipers[network] = sniper
            self.global_stats.active_snipers += 1
            
            logger.info(f"Block 0 sniper initialized for {network}")
            
        except Exception as e:
            logger.error(f"Failed to initialize sniper for {network}: {e}")
    
    async def _start_global_coordination(self) -> None:
        """Start global coordination and monitoring tasks."""
        try:
            # Start global statistics updater
            asyncio.create_task(self._update_global_stats())
            
            # Start cross-chain arbitrage detection
            asyncio.create_task(self._monitor_cross_chain_opportunities())
            
            # Start performance monitoring
            asyncio.create_task(self._monitor_system_performance())
            
            logger.info("Global coordination systems started")
            
        except Exception as e:
            logger.error(f"Failed to start global coordination: {e}")
    
    async def _initialize_community_features(self) -> None:
        """Initialize community building features."""
        try:
            if self.community_features.open_source_contributions:
                await self._setup_contribution_tracking()
            
            if self.community_features.developer_api_access:
                await self._setup_developer_apis()
            
            if self.community_features.educational_resources:
                await self._setup_educational_platform()
            
            logger.info("Community features initialized")
            
        except Exception as e:
            logger.warning(f"Some community features failed to initialize: {e}")
    
    async def _setup_contribution_tracking(self) -> None:
        """Setup tracking for open source contributions."""
        # Track GitHub contributions, documentation updates, etc.
        pass
    
    async def _setup_developer_apis(self) -> None:
        """Setup developer API access and documentation."""
        # Provide APIs for custom integrations
        pass
    
    async def _setup_educational_platform(self) -> None:
        """Setup educational resources and courses."""
        # Create educational content about DEX sniping strategies
        pass
    
    async def _handle_new_token_detected(self, liquidity_event: LiquidityAddEvent) -> None:
        """
        Handle new token detection across all networks.
        
        Args:
            liquidity_event: Detected liquidity addition event
        """
        try:
            network = liquidity_event.pending_tx.transaction_hash[:2]  # Simplified network detection
            
            logger.info(
                f"[START] NEW TOKEN DETECTED: {liquidity_event.token_address} "
                f"on {liquidity_event.dex} ({network})"
            )
            
            # Update statistics
            self.global_stats.total_tokens_discovered += 1
            if network in self.network_stats:
                self.network_stats[network]['tokens_discovered'] += 1
                self.network_stats[network]['last_activity'] = datetime.utcnow()
            
            # Cache discovery for community alerts
            await self._cache_token_discovery(liquidity_event)
            
            # Execute auto-snipe if enabled and conditions met
            if await self._should_auto_snipe(liquidity_event):
                await self._execute_auto_snipe(liquidity_event)
            
            # Notify community
            await self._notify_community_discovery(liquidity_event)
            
            # Call registered callbacks
            for callback in self.token_discovery_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(liquidity_event)
                    else:
                        callback(liquidity_event)
                except Exception as e:
                    logger.error(f"Error in token discovery callback: {e}")
            
        except Exception as e:
            logger.error(f"Error handling new token detection: {e}")
    
    async def _handle_liquidity_event(self, liquidity_event: LiquidityAddEvent) -> None:
        """
        Handle general liquidity events.
        
        Args:
            liquidity_event: Liquidity addition event
        """
        try:
            # Update global statistics
            self.global_stats.total_transactions_scanned += 1
            
            # Analyze for arbitrage opportunities
            await self._analyze_arbitrage_opportunity(liquidity_event)
            
        except Exception as e:
            logger.error(f"Error handling liquidity event: {e}")
    
    async def _should_auto_snipe(self, liquidity_event: LiquidityAddEvent) -> bool:
        """
        Determine if automatic sniping should be executed.
        
        Args:
            liquidity_event: Liquidity event to evaluate
            
        Returns:
            True if auto-sniping should be executed
        """
        try:
            # Check if auto-sniping is enabled
            if not getattr(settings, 'enable_auto_sniping', False):
                return False
            
            # Check if token appears to be legitimate (basic filters)
            if not liquidity_event.is_new_token:
                return False
            
            # Check gas price thresholds
            gas_price_gwei = liquidity_event.pending_tx.gas_price_gwei
            max_gas = getattr(settings, 'max_auto_snipe_gas_gwei', 50)
            if gas_price_gwei > max_gas:
                logger.info(f"Gas price too high for auto-snipe: {gas_price_gwei} gwei")
                return False
            
            # Check minimum liquidity thresholds
            # (This would require additional analysis of the liquidity amounts)
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating auto-snipe conditions: {e}")
            return False
    
    async def _execute_auto_snipe(self, liquidity_event: LiquidityAddEvent) -> None:
        """
        Execute automatic sniping for detected token.
        
        Args:
            liquidity_event: Liquidity event to snipe
        """
        try:
            # Determine network from event
            network = self._get_network_from_event(liquidity_event)
            
            if network not in self.block_zero_snipers:
                logger.warning(f"No sniper available for {network}")
                return
            
            sniper = self.block_zero_snipers[network]
            
            # Get auto-snipe configuration
            eth_amount = getattr(settings, 'auto_snipe_eth_amount', 0.05)
            priority = getattr(settings, 'auto_snipe_priority', 'normal')
            
            logger.info(
                f"[TARGET] Executing auto-snipe for {liquidity_event.token_address} "
                f"with {eth_amount} ETH"
            )
            
            # Execute snipe
            self.global_stats.total_snipe_attempts += 1
            if network in self.network_stats:
                self.network_stats[network]['snipes_attempted'] += 1
            
            snipe_result = await sniper.snipe_token_launch(
                liquidity_event, eth_amount, priority
            )
            
            # Monitor result
            final_result = await sniper.monitor_snipe_result(snipe_result, timeout_seconds=60)
            
            # Update statistics
            if final_result.status == 'confirmed':
                self.global_stats.successful_snipes += 1
                self.global_stats.total_volume_sniped_eth += eth_amount
                if network in self.network_stats:
                    self.network_stats[network]['snipes_successful'] += 1
            else:
                self.global_stats.failed_snipes += 1
            
            # Cache result
            await self._cache_snipe_result(final_result)
            
            # Notify callbacks
            for callback in self.snipe_completion_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(final_result)
                    else:
                        callback(final_result)
                except Exception as e:
                    logger.error(f"Error in snipe completion callback: {e}")
            
            logger.info(
                f"Auto-snipe completed: {final_result.status} "
                f"({final_result.execution_time_ms:.1f}ms)"
            )
            
        except Exception as e:
            logger.error(f"Auto-snipe execution failed: {e}")
            self.global_stats.failed_snipes += 1
    
    def _get_network_from_event(self, liquidity_event: LiquidityAddEvent) -> str:
        """Determine network from liquidity event (simplified)."""
        # In production, this would analyze the transaction details
        # For now, return the first available network
        return next(iter(self.block_zero_snipers.keys()), 'ethereum')
    
    async def _cache_token_discovery(self, liquidity_event: LiquidityAddEvent) -> None:
        """Cache token discovery for community alerts and analytics."""
        try:
            cache_key = f"token_discovery_{liquidity_event.token_address}"
            discovery_data = {
                'token_address': liquidity_event.token_address,
                'dex': liquidity_event.dex,
                'detected_at': liquidity_event.detected_at,
                'gas_price_gwei': liquidity_event.pending_tx.gas_price_gwei,
                'tx_hash': liquidity_event.pending_tx.hash
            }
            
            await cache_manager.set(
                cache_key,
                discovery_data,
                ttl=3600,  # 1 hour
                namespace='discoveries'
            )
            
        except Exception as e:
            logger.warning(f"Error caching token discovery: {e}")
    
    async def _cache_snipe_result(self, snipe_result: SnipeResult) -> None:
        """Cache snipe result for analytics and community features."""
        try:
            cache_key = f"snipe_result_{snipe_result.transaction_hash}"
            result_data = {
                'token_address': snipe_result.token_address,
                'status': snipe_result.status,
                'execution_time_ms': snipe_result.execution_time_ms,
                'block_number': snipe_result.block_number,
                'mev_protection_used': snipe_result.mev_protection_used
            }
            
            await cache_manager.set(
                cache_key,
                result_data,
                ttl=86400,  # 24 hours
                namespace='snipe_results'
            )
            
        except Exception as e:
            logger.warning(f"Error caching snipe result: {e}")
    
    async def _notify_community_discovery(self, liquidity_event: LiquidityAddEvent) -> None:
        """Send community notifications for new token discoveries."""
        if not self.community_features.community_alerts:
            return
        
        try:
            # Implement community notification system
            # Could include Discord webhooks, Telegram alerts, etc.
            pass
            
        except Exception as e:
            logger.warning(f"Error sending community notification: {e}")
    
    async def _analyze_arbitrage_opportunity(self, liquidity_event: LiquidityAddEvent) -> None:
        """Analyze cross-chain arbitrage opportunities."""
        try:
            # Implement cross-chain arbitrage detection
            # Compare prices across networks and DEXs
            pass
            
        except Exception as e:
            logger.debug(f"Error analyzing arbitrage opportunity: {e}")
    
    async def _update_global_stats(self) -> None:
        """Periodically update global statistics."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Update global statistics
                self.global_stats.last_updated = datetime.utcnow()
                
                # Calculate average execution time
                # (This would be based on recent snipe results)
                
                # Update uptime percentage
                # (This would be based on system monitoring)
                
                # Log periodic statistics
                logger.info(
                    f"Global Stats: {self.global_stats.total_tokens_discovered} tokens discovered, "
                    f"{self.global_stats.successful_snipes}/{self.global_stats.total_snipe_attempts} snipes successful"
                )
                
            except Exception as e:
                logger.error(f"Error updating global stats: {e}")
    
    async def _monitor_cross_chain_opportunities(self) -> None:
        """Monitor for cross-chain arbitrage opportunities."""
        while not self._shutdown:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Implement cross-chain monitoring logic
                # Compare token prices across different networks
                
            except Exception as e:
                logger.error(f"Error monitoring cross-chain opportunities: {e}")
    
    async def _monitor_system_performance(self) -> None:
        """Monitor overall system performance and health."""
        while not self._shutdown:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes
                
                # Check scanner health
                unhealthy_scanners = []
                for network, scanner in self.mempool_scanners.items():
                    health = await scanner.health_check()
                    if health['status'] != 'healthy':
                        unhealthy_scanners.append(network)
                
                if unhealthy_scanners:
                    logger.warning(f"Unhealthy scanners detected: {unhealthy_scanners}")
                
                # Check sniper health
                unhealthy_snipers = []
                for network, sniper in self.block_zero_snipers.items():
                    health = await sniper.health_check()
                    if health['status'] not in ['healthy', 'warning']:
                        unhealthy_snipers.append(network)
                
                if unhealthy_snipers:
                    logger.warning(f"Unhealthy snipers detected: {unhealthy_snipers}")
                
            except Exception as e:
                logger.error(f"Error monitoring system performance: {e}")
    
    # Public API Methods
    
    def register_token_discovery_callback(self, callback: Callable) -> None:
        """Register callback for token discovery events."""
        self.token_discovery_callbacks.append(callback)
        logger.info(f"Registered token discovery callback: {callback.__name__}")
    
    def register_snipe_completion_callback(self, callback: Callable) -> None:
        """Register callback for snipe completion events."""
        self.snipe_completion_callbacks.append(callback)
        logger.info(f"Registered snipe completion callback: {callback.__name__}")
    
    async def manual_snipe(
        self,
        token_address: str,
        network: str,
        eth_amount: float,
        priority: str = 'normal'
    ) -> Optional[SnipeResult]:
        """
        Execute manual snipe for specified token.
        
        Args:
            token_address: Token to snipe
            network: Network name
            eth_amount: ETH amount to spend
            priority: Gas priority level
            
        Returns:
            SnipeResult or None if sniper not available
        """
        if network not in self.block_zero_snipers:
            logger.error(f"No sniper available for {network}")
            return None
        
        try:
            sniper = self.block_zero_snipers[network]
            
            # Create mock liquidity event for manual snipe
            from app.core.mempool.mempool_scanner import PendingTransaction, LiquidityAddEvent
            
            mock_tx = PendingTransaction(
                hash='manual_snipe',
                from_address='0x0000000000000000000000000000000000000000',
                to_address='0x0000000000000000000000000000000000000000',
                value=0,
                gas=300000,
                gas_price=20000000000,  # 20 gwei
                input_data='0x',
                timestamp=time.time()
            )
            
            mock_event = LiquidityAddEvent(
                token_address=token_address,
                pair_address='',
                dex='manual',
                token0=token_address,
                token1='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
                amount0=0,
                amount1=0,
                liquidity=0,
                pending_tx=mock_tx
            )
            
            result = await sniper.snipe_token_launch(mock_event, eth_amount, priority)
            return await sniper.monitor_snipe_result(result)
            
        except Exception as e:
            logger.error(f"Manual snipe failed: {e}")
            return None
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get comprehensive global statistics."""
        return {
            'global_stats': {
                'total_transactions_scanned': self.global_stats.total_transactions_scanned,
                'total_tokens_discovered': self.global_stats.total_tokens_discovered,
                'total_snipe_attempts': self.global_stats.total_snipe_attempts,
                'successful_snipes': self.global_stats.successful_snipes,
                'failed_snipes': self.global_stats.failed_snipes,
                'success_rate': (
                    self.global_stats.successful_snipes / 
                    max(1, self.global_stats.total_snipe_attempts) * 100
                ),
                'active_networks': list(self.global_stats.active_networks),
                'active_scanners': self.global_stats.active_scanners,
                'active_snipers': self.global_stats.active_snipers,
                'total_volume_sniped_eth': self.global_stats.total_volume_sniped_eth,
                'last_updated': self.global_stats.last_updated.isoformat()
            },
            'network_stats': self.network_stats,
            'partnership_status': {
                'flashbots_enabled': self.partnership_config.flashbots_enabled,
                'premium_nodes': len(self.premium_node_connections),
                'mev_protection_level': self.partnership_config.mev_protection_level
            },
            'community_features': {
                'open_source_contributions': self.community_features.open_source_contributions,
                'developer_api_access': self.community_features.developer_api_access,
                'educational_resources': self.community_features.educational_resources
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check."""
        try:
            # Check all scanners
            scanner_health = {}
            for network, scanner in self.mempool_scanners.items():
                scanner_health[network] = await scanner.health_check()
            
            # Check all snipers
            sniper_health = {}
            for network, sniper in self.block_zero_snipers.items():
                sniper_health[network] = await sniper.health_check()
            
            # Overall system status
            healthy_scanners = sum(
                1 for health in scanner_health.values() 
                if health['status'] == 'healthy'
            )
            healthy_snipers = sum(
                1 for health in sniper_health.values() 
                if health['status'] in ['healthy', 'warning']
            )
            
            overall_status = 'healthy'
            if healthy_scanners < len(self.mempool_scanners) * 0.5:
                overall_status = 'degraded'
            if healthy_scanners == 0:
                overall_status = 'critical'
            
            return {
                'status': overall_status,
                'running': self._running,
                'total_networks': len(self.global_stats.active_networks),
                'healthy_scanners': healthy_scanners,
                'total_scanners': len(self.mempool_scanners),
                'healthy_snipers': healthy_snipers,
                'total_snipers': len(self.block_zero_snipers),
                'scanner_health': scanner_health,
                'sniper_health': sniper_health,
                'partnerships': {
                    'flashbots_networks': len(self.flashbots_clients),
                    'premium_node_networks': len(self.premium_node_connections)
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'running': self._running
            }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown mempool manager."""
        logger.info("Shutting down MempoolManager...")
        self._shutdown = True
        self._running = False
        
        # Stop all scanners
        for scanner in self.mempool_scanners.values():
            await scanner.stop_scanning()
        
        # Clear all connections
        self.mempool_scanners.clear()
        self.block_zero_snipers.clear()
        
        logger.info("MempoolManager shutdown complete")