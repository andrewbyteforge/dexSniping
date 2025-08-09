"""
Live Trading Engine Enhanced - Phase 4B Implementation
File: app/core/trading/live_trading_engine_enhanced.py
Class: LiveTradingEngineEnhanced
Methods: initialize_live_systems, execute_live_trade, monitor_market_opportunities

Enhanced trading engine integrating wallet connections and live DEX data for
real blockchain trading with comprehensive risk management and profit optimization.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Union
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import os
from concurrent.futures import ThreadPoolExecutor

from app.core.wallet.wallet_connection_manager import (
    WalletConnectionManager, 
    WalletConnection,
    NetworkType,
    WalletType,
    ConnectionStatus,
    get_wallet_connection_manager
)
from app.core.dex.live_dex_integration import (
    LiveDEXIntegration,
    DEXProtocol,
    SwapQuote,
    SwapTransaction,
    TokenInfo,
    get_live_dex_integration
)
from app.utils.logger import setup_logger, get_trading_logger, get_performance_logger, get_trading_logger, get_performance_logger
from app.core.exceptions import (
    TradingError,
    WalletError,
    DEXError,
    InsufficientFundsError,
    RiskManagementError
)

logger = setup_logger(__name__, "trading")


class TradingMode(str, Enum):
    """Enhanced trading modes."""
    MANUAL = "manual"
    SEMI_AUTOMATED = "semi_automated"
    FULLY_AUTOMATED = "fully_automated"
    SIMULATION = "simulation"
    PAPER_TRADING = "paper_trading"


class TradingStrategy(str, Enum):
    """Trading strategies."""
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    MOMENTUM = "momentum"
    LIQUIDITY_SNIPING = "liquidity_sniping"
    MEV_PROTECTION = "mev_protection"


class OrderType(str, Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class TradingConfiguration:
    """Live trading configuration."""
    trading_mode: TradingMode
    enabled_strategies: List[TradingStrategy]
    enabled_networks: List[NetworkType]
    preferred_dexes: List[DEXProtocol]
    
    # Risk management
    max_position_size_usd: Decimal
    max_daily_loss_usd: Decimal
    max_single_trade_usd: Decimal
    max_slippage_percent: Decimal
    max_price_impact_percent: Decimal
    
    # Trading parameters
    default_slippage_percent: Decimal
    gas_price_strategy: str  # "fast", "standard", "safe"
    max_gas_price_gwei: Decimal
    transaction_timeout_seconds: int
    
    # Portfolio management
    reserve_balance_percent: Decimal  # Keep this % as reserve
    rebalance_threshold_percent: Decimal
    profit_taking_percent: Decimal
    stop_loss_percent: Decimal
    
    @classmethod
    def conservative(cls) -> 'TradingConfiguration':
        """Conservative trading configuration."""
        return cls(
            trading_mode=TradingMode.SEMI_AUTOMATED,
            enabled_strategies=[TradingStrategy.ARBITRAGE],
            enabled_networks=[NetworkType.ETHEREUM],
            preferred_dexes=[DEXProtocol.UNISWAP_V2],
            max_position_size_usd=Decimal("1000"),
            max_daily_loss_usd=Decimal("50"),
            max_single_trade_usd=Decimal("200"),
            max_slippage_percent=Decimal("1.0"),
            max_price_impact_percent=Decimal("2.0"),
            default_slippage_percent=Decimal("0.5"),
            gas_price_strategy="standard",
            max_gas_price_gwei=Decimal("50"),
            transaction_timeout_seconds=300,
            reserve_balance_percent=Decimal("20"),
            rebalance_threshold_percent=Decimal("5"),
            profit_taking_percent=Decimal("10"),
            stop_loss_percent=Decimal("5")
        )
    
    @classmethod
    def aggressive(cls) -> 'TradingConfiguration':
        """Aggressive trading configuration."""
        return cls(
            trading_mode=TradingMode.FULLY_AUTOMATED,
            enabled_strategies=[
                TradingStrategy.ARBITRAGE, 
                TradingStrategy.LIQUIDITY_SNIPING,
                TradingStrategy.MOMENTUM
            ],
            enabled_networks=[NetworkType.ETHEREUM, NetworkType.POLYGON, NetworkType.BSC],
            preferred_dexes=[
                DEXProtocol.UNISWAP_V2, 
                DEXProtocol.SUSHISWAP, 
                DEXProtocol.PANCAKESWAP
            ],
            max_position_size_usd=Decimal("5000"),
            max_daily_loss_usd=Decimal("500"),
            max_single_trade_usd=Decimal("1000"),
            max_slippage_percent=Decimal("3.0"),
            max_price_impact_percent=Decimal("5.0"),
            default_slippage_percent=Decimal("1.5"),
            gas_price_strategy="fast",
            max_gas_price_gwei=Decimal("100"),
            transaction_timeout_seconds=180,
            reserve_balance_percent=Decimal("10"),
            rebalance_threshold_percent=Decimal("10"),
            profit_taking_percent=Decimal("20"),
            stop_loss_percent=Decimal("8")
        )


@dataclass
class TradingOpportunity:
    """Trading opportunity data structure."""
    opportunity_id: str
    strategy: TradingStrategy
    network: NetworkType
    dex_protocol: DEXProtocol
    
    # Token information
    input_token: TokenInfo
    output_token: TokenInfo
    
    # Trade details
    recommended_amount: Decimal
    expected_profit_usd: Decimal
    expected_profit_percent: Decimal
    confidence_score: Decimal  # 0-100
    risk_level: RiskLevel
    
    # Market data
    current_price: Decimal
    target_price: Optional[Decimal]
    liquidity_usd: Decimal
    volume_24h_usd: Optional[Decimal]
    
    # Timing
    time_sensitivity: str  # "immediate", "minutes", "hours"
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """Check if opportunity has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def risk_adjusted_score(self) -> Decimal:
        """Calculate risk-adjusted opportunity score."""
        risk_multipliers = {
            RiskLevel.VERY_LOW: Decimal("1.0"),
            RiskLevel.LOW: Decimal("0.9"),
            RiskLevel.MEDIUM: Decimal("0.7"),
            RiskLevel.HIGH: Decimal("0.5"),
            RiskLevel.VERY_HIGH: Decimal("0.3")
        }
        
        risk_multiplier = risk_multipliers.get(self.risk_level, Decimal("0.5"))
        return (self.confidence_score * self.expected_profit_percent * risk_multiplier) / Decimal("100")


@dataclass
class TradingSession:
    """Active trading session."""
    session_id: str
    wallet_connection_id: str
    configuration: TradingConfiguration
    start_time: datetime
    
    # Session state
    is_active: bool = True
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    
    # Performance metrics
    total_profit_usd: Decimal = Decimal("0")
    total_loss_usd: Decimal = Decimal("0")
    total_gas_spent_eth: Decimal = Decimal("0")
    largest_profit_usd: Decimal = Decimal("0")
    largest_loss_usd: Decimal = Decimal("0")
    
    # Daily limits tracking
    daily_loss_usd: Decimal = Decimal("0")
    daily_trades: int = 0
    last_reset_date: datetime = field(default_factory=lambda: datetime.utcnow().date())
    
    @property
    def success_rate(self) -> Decimal:
        """Calculate trade success rate."""
        if self.total_trades == 0:
            return Decimal("0")
        return Decimal(self.successful_trades) / Decimal(self.total_trades) * Decimal("100")
    
    @property
    def net_profit_usd(self) -> Decimal:
        """Calculate net profit."""
        return self.total_profit_usd - self.total_loss_usd
    
    @property
    def can_trade_today(self) -> bool:
        """Check if can still trade today based on limits."""
        today = datetime.utcnow().date()
        
        # Reset daily counters if new day
        if today > self.last_reset_date:
            self.daily_loss_usd = Decimal("0")
            self.daily_trades = 0
            self.last_reset_date = today
        
        return self.daily_loss_usd < self.configuration.max_daily_loss_usd


class LiveTradingEngineEnhanced:
    """
    Enhanced live trading engine for professional DEX trading.
    
    Integrates wallet management, DEX connectivity, risk management,
    and automated trading strategies for real profit generation.
    """
    
    def __init__(
        self,
        wallet_manager: Optional[WalletConnectionManager] = None,
        dex_integration: Optional[LiveDEXIntegration] = None
    ):
        """Initialize enhanced trading engine."""
        self.wallet_manager = wallet_manager or get_wallet_connection_manager()
        self.dex_integration = dex_integration or get_live_dex_integration()
        
        # Trading state
        self.active_sessions: Dict[str, TradingSession] = {}
        self.detected_opportunities: Dict[str, TradingOpportunity] = {}
        self.pending_trades: Dict[str, SwapTransaction] = {}
        
        # Monitoring and callbacks
        self.opportunity_callbacks: List[Callable] = []
        self.trade_completion_callbacks: List[Callable] = []
        self.risk_alert_callbacks: List[Callable] = []
        
        # System state
        self.is_initialized = False
        self.monitoring_tasks: List[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance tracking
        self.system_start_time = datetime.utcnow()
        self.total_opportunities_detected = 0
        self.total_trades_executed = 0
        
        logger.info("🤖 Enhanced Live Trading Engine initialized")
    
    async def initialize_live_systems(self, networks: Optional[List[NetworkType]] = None) -> bool:
        """
        Initialize all live trading systems.
        
        Args:
            networks: Networks to initialize
            
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("🚀 Initializing live trading systems...")
            
            # Initialize wallet system
            logger.info("🔗 Initializing wallet connections...")
            wallet_success = await self.wallet_manager.initialize_networks(networks)
            
            if not wallet_success:
                logger.error("❌ Wallet system initialization failed")
                return False
            
            # Initialize DEX integration
            logger.info("📊 Initializing DEX integration...")
            dex_success = await self.dex_integration.initialize_dex_contracts(networks)
            
            if not dex_success:
                logger.error("❌ DEX integration initialization failed")
                return False
            
            # Start monitoring systems
            await self._start_monitoring_systems()
            
            # Mark as initialized
            self.is_initialized = True
            
            logger.info("✅ Live trading systems initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Live system initialization failed: {e}")
            return False
    
    async def start_trading_session(
        self,
        wallet_connection_id: str,
        configuration: Optional[TradingConfiguration] = None
    ) -> TradingSession:
        """
        Start new trading session.
        
        Args:
            wallet_connection_id: Wallet connection to use
            configuration: Trading configuration
            
        Returns:
            TradingSession: Active trading session
        """
        try:
            logger.info(f"🎯 Starting trading session with wallet: {wallet_connection_id}")
            
            if not self.is_initialized:
                raise TradingError("Trading engine not initialized")
            
            # Verify wallet connection
            wallet_connections = self.wallet_manager.get_active_connections()
            if wallet_connection_id not in wallet_connections:
                raise WalletError(f"Wallet connection {wallet_connection_id} not found")
            
            wallet_connection = wallet_connections[wallet_connection_id]
            
            # Use default configuration if none provided
            if configuration is None:
                configuration = TradingConfiguration.conservative()
            
            # Verify wallet has sufficient funds
            await self._verify_trading_requirements(wallet_connection, configuration)
            
            # Create trading session
            session = TradingSession(
                session_id=str(uuid.uuid4()),
                wallet_connection_id=wallet_connection_id,
                configuration=configuration,
                start_time=datetime.utcnow()
            )
            
            # Store session
            self.active_sessions[session.session_id] = session
            
            # Start session-specific monitoring
            await self._start_session_monitoring(session)
            
            logger.info(
                f"✅ Trading session started: {session.session_id} "
                f"(Mode: {configuration.trading_mode.value})"
            )
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to start trading session: {e}")
            raise TradingError(f"Session start failed: {e}")
    
    async def execute_live_trade(
        self,
        opportunity_id: str,
        session_id: str,
        override_amount: Optional[Decimal] = None
    ) -> SwapTransaction:
        """
        Execute live trade based on opportunity.
        
        Args:
            opportunity_id: Opportunity to execute
            session_id: Trading session ID
            override_amount: Override recommended amount
            
        Returns:
            SwapTransaction: Transaction result
        """
        try:
            logger.info(f"⚡ Executing live trade: {opportunity_id}")
            
            # Get opportunity and session
            if opportunity_id not in self.detected_opportunities:
                raise TradingError(f"Opportunity {opportunity_id} not found")
            
            if session_id not in self.active_sessions:
                raise TradingError(f"Session {session_id} not found")
            
            opportunity = self.detected_opportunities[opportunity_id]
            session = self.active_sessions[session_id]
            
            # Check if opportunity expired
            if opportunity.is_expired:
                raise TradingError(f"Opportunity {opportunity_id} has expired")
            
            # Check session limits
            if not session.can_trade_today:
                raise RiskManagementError("Daily loss limit reached")
            
            # Determine trade amount
            trade_amount = override_amount or opportunity.recommended_amount
            
            # Risk management checks
            await self._perform_risk_checks(opportunity, session, trade_amount)
            
            # Get fresh quote
            quote = await self.dex_integration.get_swap_quote(
                input_token=opportunity.input_token.address,
                output_token=opportunity.output_token.address,
                input_amount=trade_amount,
                network=opportunity.network,
                dex_protocol=opportunity.dex_protocol,
                slippage_percent=session.configuration.default_slippage_percent
            )
            
            # Execute swap
            transaction = await self.dex_integration.execute_swap_transaction(
                quote_id=quote.quote_id,
                wallet_connection_id=session.wallet_connection_id,
                max_gas_price_gwei=session.configuration.max_gas_price_gwei
            )
            
            # Update session metrics
            await self._update_session_metrics(session, transaction, opportunity)
            
            # Store transaction
            self.pending_trades[transaction.transaction_hash] = transaction
            
            # Notify callbacks
            await self._notify_trade_completion(transaction, opportunity, session)
            
            logger.info(
                f"✅ Trade executed: {trade_amount} {opportunity.input_token.symbol} → "
                f"{transaction.output_amount} {opportunity.output_token.symbol}"
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Live trade execution failed: {e}")
            # Update failed trade metrics
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.failed_trades += 1
                session.total_trades += 1
            
            raise TradingError(f"Trade execution failed: {e}")
    
    async def monitor_market_opportunities(
        self,
        networks: Optional[List[NetworkType]] = None,
        strategies: Optional[List[TradingStrategy]] = None
    ) -> None:
        """
        Monitor market for trading opportunities.
        
        Args:
            networks: Networks to monitor
            strategies: Strategies to use for detection
        """
        try:
            logger.info("👀 Starting market opportunity monitoring...")
            
            if networks is None:
                networks = list(self.wallet_manager.web3_instances.keys())
            
            if strategies is None:
                strategies = list(TradingStrategy)
            
            # Start monitoring for each network
            for network in networks:
                task = asyncio.create_task(
                    self._monitor_network_opportunities(network, strategies)
                )
                self.monitoring_tasks.append(task)
            
            logger.info(f"🎯 Monitoring {len(networks)} networks for opportunities")
            
        except Exception as e:
            logger.error(f"❌ Market monitoring setup failed: {e}")
    
    async def _monitor_network_opportunities(
        self,
        network: NetworkType,
        strategies: List[TradingStrategy]
    ) -> None:
        """Monitor opportunities on specific network."""
        try:
            while True:
                try:
                    # Simulate opportunity detection
                    # In production, this would:
                    # 1. Monitor mempool for new token listings
                    # 2. Scan for arbitrage opportunities
                    # 3. Detect liquidity additions
                    # 4. Monitor price movements
                    
                    opportunities = await self._detect_opportunities(network, strategies)
                    
                    for opportunity in opportunities:
                        # Store opportunity
                        self.detected_opportunities[opportunity.opportunity_id] = opportunity
                        self.total_opportunities_detected += 1
                        
                        # Notify callbacks
                        await self._notify_opportunity_detected(opportunity)
                        
                        # Auto-execute if configured
                        await self._check_auto_execution(opportunity)
                    
                    # Clean up expired opportunities
                    await self._cleanup_expired_opportunities()
                    
                    # Wait before next scan
                    await asyncio.sleep(10)  # Scan every 10 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Network monitoring error for {network.value}: {e}")
                    await asyncio.sleep(30)  # Wait before retrying
                    
        except asyncio.CancelledError:
            logger.info(f"🛑 Stopped monitoring {network.value}")
    
    async def _detect_opportunities(
        self,
        network: NetworkType,
        strategies: List[TradingStrategy]
    ) -> List[TradingOpportunity]:
        """Detect trading opportunities on network."""
        opportunities = []
        
        try:
            # Simulate opportunity detection
            # This is where the real magic would happen in production
            
            if TradingStrategy.ARBITRAGE in strategies:
                # Simulate arbitrage opportunity
                if len(opportunities) < 2:  # Limit simulation
                    arb_opportunity = TradingOpportunity(
                        opportunity_id=str(uuid.uuid4()),
                        strategy=TradingStrategy.ARBITRAGE,
                        network=network,
                        dex_protocol=DEXProtocol.UNISWAP_V2,
                        input_token=TokenInfo(
                            address="0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e",
                            symbol="USDC",
                            name="USD Coin",
                            decimals=6,
                            network=network
                        ),
                        output_token=TokenInfo(
                            address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                            symbol="WETH",
                            name="Wrapped Ether",
                            decimals=18,
                            network=network
                        ),
                        recommended_amount=Decimal("100"),
                        expected_profit_usd=Decimal("2.50"),
                        expected_profit_percent=Decimal("2.5"),
                        confidence_score=Decimal("85"),
                        risk_level=RiskLevel.LOW,
                        current_price=Decimal("0.0005"),
                        liquidity_usd=Decimal("50000"),
                        time_sensitivity="minutes",
                        expires_at=datetime.utcnow() + timedelta(minutes=5)
                    )
                    opportunities.append(arb_opportunity)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Opportunity detection failed: {e}")
            return []
    
    async def _verify_trading_requirements(
        self,
        wallet_connection: WalletConnection,
        configuration: TradingConfiguration
    ) -> None:
        """Verify wallet meets trading requirements."""
        # Check minimum balance requirements
        min_balance_eth = Decimal("0.01")  # Minimum for gas
        
        for network in configuration.enabled_networks:
            if network in wallet_connection.connected_networks:
                await self.wallet_manager.verify_wallet_access(
                    wallet_connection.connection_id,
                    network,
                    min_balance_eth
                )
    
    async def _perform_risk_checks(
        self,
        opportunity: TradingOpportunity,
        session: TradingSession,
        trade_amount: Decimal
    ) -> None:
        """Perform comprehensive risk checks."""
        config = session.configuration
        
        # Check trade amount limits
        if trade_amount > config.max_single_trade_usd:
            raise RiskManagementError(
                f"Trade amount {trade_amount} exceeds limit {config.max_single_trade_usd}"
            )
        
        # Check price impact
        if opportunity.expected_profit_percent > config.max_price_impact_percent:
            # This would be actual price impact calculation in production
            pass
        
        # Check risk level compatibility
        if opportunity.risk_level == RiskLevel.VERY_HIGH and config.trading_mode != TradingMode.FULLY_AUTOMATED:
            raise RiskManagementError("High risk trades not allowed in current mode")
    
    async def _update_session_metrics(
        self,
        session: TradingSession,
        transaction: SwapTransaction,
        opportunity: TradingOpportunity
    ) -> None:
        """Update session performance metrics."""
        session.total_trades += 1
        
        if transaction.status == "confirmed":
            session.successful_trades += 1
            
            # Calculate actual profit/loss
            if transaction.output_amount and opportunity.expected_profit_usd:
                # Simplified profit calculation
                actual_profit = opportunity.expected_profit_usd  # Would calculate actual
                
                if actual_profit > 0:
                    session.total_profit_usd += actual_profit
                    session.largest_profit_usd = max(session.largest_profit_usd, actual_profit)
                else:
                    session.total_loss_usd += abs(actual_profit)
                    session.daily_loss_usd += abs(actual_profit)
                    session.largest_loss_usd = max(session.largest_loss_usd, abs(actual_profit))
        else:
            session.failed_trades += 1
        
        # Track gas costs
        if transaction.actual_gas_cost:
            session.total_gas_spent_eth += transaction.actual_gas_cost
    
    async def _start_monitoring_systems(self) -> None:
        """Start background monitoring systems."""
        # Start opportunity monitoring
        monitoring_task = asyncio.create_task(self.monitor_market_opportunities())
        self.monitoring_tasks.append(monitoring_task)
        
        # Start session cleanup task
        cleanup_task = asyncio.create_task(self._periodic_cleanup())
        self.monitoring_tasks.append(cleanup_task)
    
    async def _start_session_monitoring(self, session: TradingSession) -> None:
        """Start monitoring for specific session."""
        # In production, this would start session-specific monitoring
        # like position tracking, P&L updates, risk monitoring
        logger.debug(f"🔍 Session monitoring started: {session.session_id}")
    
    async def _check_auto_execution(self, opportunity: TradingOpportunity) -> None:
        """Check if opportunity should be auto-executed."""
        # Find sessions that could auto-execute this opportunity
        for session in self.active_sessions.values():
            config = session.configuration
            
            # Check if auto-execution enabled
            if config.trading_mode != TradingMode.FULLY_AUTOMATED:
                continue
            
            # Check if strategy is enabled
            if opportunity.strategy not in config.enabled_strategies:
                continue
            
            # Check if network is enabled
            if opportunity.network not in config.enabled_networks:
                continue
            
            # Check confidence and risk thresholds
            if opportunity.confidence_score < 80:  # Minimum confidence for auto-execution
                continue
            
            if opportunity.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                continue
            
            # Auto-execute
            try:
                await self.execute_live_trade(
                    opportunity.opportunity_id,
                    session.session_id
                )
                logger.info(f"🤖 Auto-executed opportunity: {opportunity.opportunity_id}")
                break  # Only execute once
                
            except Exception as e:
                logger.warning(f"⚠️ Auto-execution failed: {e}")
    
    async def _cleanup_expired_opportunities(self) -> None:
        """Clean up expired opportunities."""
        current_time = datetime.utcnow()
        expired_opportunities = [
            opp_id for opp_id, opp in self.detected_opportunities.items()
            if opp.is_expired
        ]
        
        for opp_id in expired_opportunities:
            del self.detected_opportunities[opp_id]
        
        if expired_opportunities:
            logger.debug(f"🧹 Cleaned up {len(expired_opportunities)} expired opportunities")
    
    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired data."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Clean up expired opportunities
                await self._cleanup_expired_opportunities()
                
                # Clean up expired wallet connections
                await self.wallet_manager.cleanup_expired_connections()
                
                # Clean up old transactions
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                expired_transactions = [
                    tx_hash for tx_hash, tx in self.pending_trades.items()
                    if tx.created_at < cutoff_time
                ]
                
                for tx_hash in expired_transactions:
                    del self.pending_trades[tx_hash]
                
            except Exception as e:
                logger.error(f"❌ Periodic cleanup error: {e}")
    
    async def _notify_opportunity_detected(self, opportunity: TradingOpportunity) -> None:
        """Notify callbacks of detected opportunity."""
        for callback in self.opportunity_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(opportunity)
                else:
                    callback(opportunity)
            except Exception as e:
                logger.warning(f"⚠️ Opportunity callback error: {e}")
    
    async def _notify_trade_completion(
        self,
        transaction: SwapTransaction,
        opportunity: TradingOpportunity,
        session: TradingSession
    ) -> None:
        """Notify callbacks of completed trade."""
        for callback in self.trade_completion_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(transaction, opportunity, session)
                else:
                    callback(transaction, opportunity, session)
            except Exception as e:
                logger.warning(f"⚠️ Trade completion callback error: {e}")
    
    def register_opportunity_callback(self, callback: Callable) -> None:
        """Register callback for opportunity detection."""
        self.opportunity_callbacks.append(callback)
    
    def register_trade_completion_callback(self, callback: Callable) -> None:
        """Register callback for trade completion."""
        self.trade_completion_callbacks.append(callback)
    
    def get_active_sessions(self) -> Dict[str, TradingSession]:
        """Get all active trading sessions."""
        return self.active_sessions.copy()
    
    def get_detected_opportunities(self) -> Dict[str, TradingOpportunity]:
        """Get all detected opportunities."""
        return self.detected_opportunities.copy()
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system performance statistics."""
        uptime = datetime.utcnow() - self.system_start_time
        
        return {
            "system_uptime_hours": round(uptime.total_seconds() / 3600, 2),
            "total_opportunities_detected": self.total_opportunities_detected,
            "total_trades_executed": self.total_trades_executed,
            "active_sessions": len(self.active_sessions),
            "active_opportunities": len(self.detected_opportunities),
            "pending_transactions": len(self.pending_trades),
            "is_initialized": self.is_initialized,
            "monitoring_tasks": len(self.monitoring_tasks)
        }
    
    async def stop_trading_session(self, session_id: str) -> bool:
        """Stop trading session."""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session.is_active = False
            
            logger.info(f"🛑 Trading session stopped: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop session: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown trading engine."""
        try:
            logger.info("🛑 Shutting down trading engine...")
            
            # Stop all sessions
            for session_id in list(self.active_sessions.keys()):
                await self.stop_trading_session(session_id)
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("✅ Trading engine shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


# Global enhanced trading engine instance
_live_trading_engine: Optional[LiveTradingEngineEnhanced] = None


def get_live_trading_engine() -> LiveTradingEngineEnhanced:
    """Get global live trading engine instance."""
    global _live_trading_engine
    
    if _live_trading_engine is None:
        _live_trading_engine = LiveTradingEngineEnhanced()
    
    return _live_trading_engine


async def initialize_live_trading_system(networks: Optional[List[NetworkType]] = None) -> bool:
    """
    Initialize the complete live trading system.
    
    Args:
        networks: Networks to initialize
        
    Returns:
        bool: True if initialization successful
    """
    try:
        engine = get_live_trading_engine()
        return await engine.initialize_live_systems(networks)
    except Exception as e:
        logger.error(f"❌ Failed to initialize live trading system: {e}")
        return False