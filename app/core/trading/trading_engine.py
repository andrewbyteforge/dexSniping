"""
Trading Engine - Core Automation System
File: app/core/trading/trading_engine.py

Main trading engine that coordinates wallet management, DEX integration,
risk management, and automated trading strategies for profit generation.
"""

import asyncio
import json
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from app.utils.logger import setup_logger
from app.core.wallet.wallet_manager import WalletManager, NetworkType
from app.core.dex.dex_integration import DEXIntegration, DEXProtocol, SwapQuote
from app.core.trading.risk_manager import RiskManager, RiskLevel
from app.core.portfolio.portfolio_manager import PortfolioManager
from app.core.exceptions import (
    TradingError,
    InsufficientFundsError,
    RiskLimitExceededError,
    StrategyError
)

logger = setup_logger(__name__)


class TradingMode(str, Enum):
    """Trading mode enumeration."""
    MANUAL = "manual"
    SEMI_AUTOMATED = "semi_automated"
    FULLY_AUTOMATED = "fully_automated"
    SIMULATION = "simulation"


class StrategyType(str, Enum):
    """Trading strategy types."""
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    GRID_TRADING = "grid_trading"
    DCA = "dca"
    SCALPING = "scalping"


class OrderIntent(str, Enum):
    """Order intent enumeration."""
    BUY = "buy"
    SELL = "sell"
    CLOSE_POSITION = "close_position"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


@dataclass
class TradingSignal:
    """Trading signal data structure."""
    signal_id: str
    strategy_type: StrategyType
    token_address: str
    symbol: str
    intent: OrderIntent
    confidence: float
    suggested_amount: Decimal
    target_price: Optional[Decimal]
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    reasoning: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """Check if signal has expired."""
        return datetime.utcnow() > self.expires_at


@dataclass
class TradingConfiguration:
    """Trading engine configuration."""
    trading_mode: TradingMode
    max_position_size: Decimal
    max_daily_loss: Decimal
    max_slippage: Decimal
    default_slippage: Decimal
    auto_approve_threshold: Decimal
    risk_tolerance: RiskLevel
    enabled_strategies: List[StrategyType]
    preferred_dexes: List[DEXProtocol]
    gas_price_limit: int
    confirmation_blocks: int
    
    @classmethod
    def default(cls) -> 'TradingConfiguration':
        """Create default trading configuration."""
        return cls(
            trading_mode=TradingMode.SEMI_AUTOMATED,
            max_position_size=Decimal("1000"),
            max_daily_loss=Decimal("100"),
            max_slippage=Decimal("0.05"),
            default_slippage=Decimal("0.01"),
            auto_approve_threshold=Decimal("50"),
            risk_tolerance=RiskLevel.MEDIUM,
            enabled_strategies=[StrategyType.ARBITRAGE, StrategyType.TREND_FOLLOWING],
            preferred_dexes=[DEXProtocol.UNISWAP_V2, DEXProtocol.SUSHISWAP],
            gas_price_limit=50,  # gwei
            confirmation_blocks=3
        )


@dataclass
class ExecutionResult:
    """Trade execution result."""
    trade_id: str
    success: bool
    transaction_hash: Optional[str]
    executed_amount: Decimal
    execution_price: Decimal
    gas_used: int
    fees_paid: Decimal
    slippage: Decimal
    profit_loss: Decimal
    execution_time: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class TradingEngine:
    """
    Main trading engine for automated profit generation.
    
    Coordinates all trading operations including signal generation,
    risk management, order execution, and portfolio tracking.
    """
    
    def __init__(self, network: NetworkType = NetworkType.ETHEREUM):
        """Initialize trading engine."""
        self.network = network
        self.is_running = False
        self.config: Optional[TradingConfiguration] = None
        
        # Core components
        self.wallet_manager: Optional[WalletManager] = None
        self.dex_integration: Optional[DEXIntegration] = None
        self.risk_manager: Optional[RiskManager] = None
        self.portfolio_manager: Optional[PortfolioManager] = None
        
        # Trading state
        self.active_signals: List[TradingSignal] = []
        self.pending_orders: Dict[str, Dict[str, Any]] = {}
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.daily_pnl = Decimal("0")
        self.total_trades = 0
        self.successful_trades = 0
        self.last_reset_date = datetime.utcnow().date()
        
        # Signal callbacks
        self.signal_callbacks: List[Callable[[TradingSignal], None]] = []
        
        logger.info(f"🤖 Trading Engine initialized for {network.value}")
    
    async def initialize(
        self,
        config: Optional[TradingConfiguration] = None,
        wallet_manager: Optional[WalletManager] = None
    ) -> None:
        """
        Initialize trading engine components.
        
        Args:
            config: Trading configuration (uses default if None)
            wallet_manager: Wallet manager instance (creates new if None)
        """
        try:
            # Set configuration
            self.config = config or TradingConfiguration.default()
            
            # Initialize wallet manager
            if wallet_manager:
                self.wallet_manager = wallet_manager
            else:
                self.wallet_manager = WalletManager(self.network)
            
            # Initialize DEX integration
            # Note: In production, you'd pass actual Web3 instance
            self.dex_integration = DEXIntegration(
                web3=None,  # Mock for now
                network=self.network.value
            )
            
            # Initialize risk manager
            self.risk_manager = RiskManager()
            
            # Initialize portfolio manager
            self.portfolio_manager = PortfolioManager()
            
            # Start background tasks
            asyncio.create_task(self._signal_processor())
            asyncio.create_task(self._execution_processor())
            asyncio.create_task(self._daily_reset_task())
            
            logger.info("✅ Trading Engine components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Trading Engine initialization failed: {e}")
            raise TradingError(f"Initialization failed: {e}")
    
    async def start_trading(self, wallet_address: str) -> Dict[str, Any]:
        """
        Start automated trading for a wallet.
        
        Args:
            wallet_address: Wallet address to trade with
            
        Returns:
            Status information
        """
        try:
            if self.is_running:
                return {
                    "success": False,
                    "message": "Trading is already running"
                }
            
            # Verify wallet is connected
            if not self.wallet_manager.is_wallet_connected(wallet_address):
                raise TradingError(f"Wallet {wallet_address} is not connected")
            
            # Verify sufficient balance
            balance = await self.wallet_manager.get_wallet_balance(wallet_address)
            if balance.native_balance < self.config.max_position_size:
                logger.warning(
                    f"⚠️ Low balance: {balance.native_balance} < "
                    f"{self.config.max_position_size}"
                )
            
            # Start trading
            self.is_running = True
            
            # Start strategy generators
            asyncio.create_task(self._run_strategies(wallet_address))
            
            logger.info(f"🚀 Trading started for wallet {wallet_address[:10]}...")
            
            return {
                "success": True,
                "message": "Trading started successfully",
                "config": {
                    "mode": self.config.trading_mode.value,
                    "max_position": str(self.config.max_position_size),
                    "strategies": [s.value for s in self.config.enabled_strategies]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start trading: {e}")
            raise TradingError(f"Trading start failed: {e}")
    
    async def stop_trading(self) -> Dict[str, Any]:
        """Stop automated trading."""
        try:
            if not self.is_running:
                return {
                    "success": False,
                    "message": "Trading is not running"
                }
            
            self.is_running = False
            
            # Cancel pending orders
            cancelled_orders = await self._cancel_all_pending_orders()
            
            logger.info(f"🛑 Trading stopped - {cancelled_orders} orders cancelled")
            
            return {
                "success": True,
                "message": f"Trading stopped successfully - {cancelled_orders} orders cancelled",
                "final_stats": await self._get_session_stats()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to stop trading: {e}")
            raise TradingError(f"Trading stop failed: {e}")
    
    async def execute_manual_trade(
        self,
        wallet_address: str,
        token_address: str,
        intent: OrderIntent,
        amount: Decimal,
        slippage_tolerance: Optional[Decimal] = None
    ) -> ExecutionResult:
        """
        Execute a manual trade.
        
        Args:
            wallet_address: Wallet to trade from
            token_address: Token to trade
            intent: Buy or sell intent
            amount: Amount to trade
            slippage_tolerance: Maximum slippage (uses default if None)
            
        Returns:
            Execution result
        """
        try:
            start_time = datetime.utcnow()
            
            # Use default slippage if not provided
            slippage = slippage_tolerance or self.config.default_slippage
            
            # Risk check
            risk_result = await self.risk_manager.assess_trade_risk(
                wallet_address, token_address, amount, intent.value
            )
            
            if not risk_result.can_trade:
                raise RiskLimitExceededError(
                    f"Trade rejected by risk manager: {risk_result.warnings}"
                )
            
            # Get quotes
            if intent == OrderIntent.BUY:
                # Buying token with ETH
                input_token = "0x0000000000000000000000000000000000000000"  # ETH
                output_token = token_address
            else:
                # Selling token for ETH
                input_token = token_address
                output_token = "0x0000000000000000000000000000000000000000"  # ETH
            
            quotes = await self.dex_integration.get_swap_quote(
                input_token=input_token,
                output_token=output_token,
                input_amount=amount,
                slippage_tolerance=slippage,
                protocols=self.config.preferred_dexes
            )
            
            if not quotes:
                raise TradingError("No quotes available for this trade")
            
            # Use best quote
            best_quote = quotes[0]
            
            # Execute swap
            swap_result = await self.dex_integration.execute_swap(
                quote=best_quote,
                wallet_address=wallet_address
            )
            
            # Calculate metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            actual_slippage = abs(
                (swap_result.output_amount - best_quote.expected_output) 
                / best_quote.expected_output
            )
            
            # Update portfolio
            await self.portfolio_manager.record_trade(
                wallet_address=wallet_address,
                token_address=token_address,
                side=intent.value,
                amount=amount,
                price=swap_result.output_amount / amount,
                transaction_hash=swap_result.transaction_hash
            )
            
            # Update stats
            self.total_trades += 1
            self.successful_trades += 1
            
            result = ExecutionResult(
                trade_id=str(uuid.uuid4()),
                success=True,
                transaction_hash=swap_result.transaction_hash,
                executed_amount=amount,
                execution_price=swap_result.output_amount / amount,
                gas_used=swap_result.gas_used,
                fees_paid=Decimal(swap_result.gas_used * swap_result.effective_gas_price) / 10**18,
                slippage=actual_slippage,
                profit_loss=Decimal("0"),  # Calculate based on position
                execution_time=execution_time
            )
            
            logger.info(
                f"✅ Manual trade executed: {intent.value} {amount} tokens "
                f"- TX: {swap_result.transaction_hash[:10]}..."
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Manual trade failed: {e}")
            
            # Update failed trade stats
            self.total_trades += 1
            
            return ExecutionResult(
                trade_id=str(uuid.uuid4()),
                success=False,
                transaction_hash=None,
                executed_amount=Decimal("0"),
                execution_price=Decimal("0"),
                gas_used=0,
                fees_paid=Decimal("0"),
                slippage=Decimal("0"),
                profit_loss=Decimal("0"),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def generate_trading_signal(
        self,
        strategy_type: StrategyType,
        token_address: str,
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """
        Generate trading signal based on strategy and market data.
        
        Args:
            strategy_type: Type of strategy to use
            token_address: Token to analyze
            market_data: Current market data
            
        Returns:
            Trading signal if conditions are met
        """
        try:
            if strategy_type == StrategyType.ARBITRAGE:
                return await self._generate_arbitrage_signal(token_address, market_data)
            elif strategy_type == StrategyType.TREND_FOLLOWING:
                return await self._generate_trend_signal(token_address, market_data)
            elif strategy_type == StrategyType.MOMENTUM:
                return await self._generate_momentum_signal(token_address, market_data)
            else:
                logger.warning(f"⚠️ Unsupported strategy: {strategy_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Signal generation failed for {strategy_type.value}: {e}")
            return None
    
    async def _generate_arbitrage_signal(
        self, 
        token_address: str, 
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Generate arbitrage trading signal."""
        try:
            # Get quotes from multiple DEXes
            quotes = await self.dex_integration.get_swap_quote(
                input_token="0x0000000000000000000000000000000000000000",  # ETH
                output_token=token_address,
                input_amount=Decimal("1"),  # 1 ETH worth
                protocols=self.config.preferred_dexes
            )
            
            if len(quotes) < 2:
                return None
            
            # Sort by price (highest output = best buy price)
            quotes.sort(key=lambda q: q.output_amount, reverse=True)
            best_buy = quotes[0]
            worst_buy = quotes[-1]
            
            # Calculate potential profit
            price_difference = (best_buy.output_amount - worst_buy.output_amount)
            profit_percentage = (price_difference / worst_buy.output_amount) * 100
            
            # Check if arbitrage opportunity exists (minimum 0.5% profit)
            if profit_percentage >= Decimal("0.5"):
                return TradingSignal(
                    signal_id=str(uuid.uuid4()),
                    strategy_type=StrategyType.ARBITRAGE,
                    token_address=token_address,
                    symbol=market_data.get("symbol", "UNKNOWN"),
                    intent=OrderIntent.BUY,
                    confidence=min(float(profit_percentage) / 5.0, 1.0),
                    suggested_amount=Decimal("100"),  # $100 worth
                    target_price=best_buy.price_per_token,
                    stop_loss=None,
                    take_profit=None,
                    reasoning=f"Arbitrage opportunity: {profit_percentage:.2f}% profit potential between DEXes",
                    expires_at=datetime.utcnow() + timedelta(minutes=5)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Arbitrage signal generation failed: {e}")
            return None
    
    async def _generate_trend_signal(
        self, 
        token_address: str, 
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Generate trend following signal."""
        try:
            # Get price history and calculate trend
            price_history = market_data.get("price_history", [])
            current_price = market_data.get("current_price", 0)
            
            if len(price_history) < 10:
                return None
            
            # Simple trend calculation (moving averages)
            short_ma = sum(price_history[-5:]) / 5
            long_ma = sum(price_history[-10:]) / 10
            
            # Trend strength
            trend_strength = abs(short_ma - long_ma) / long_ma
            
            # Generate signal based on trend
            if short_ma > long_ma * 1.02 and trend_strength > 0.03:  # Uptrend
                return TradingSignal(
                    signal_id=str(uuid.uuid4()),
                    strategy_type=StrategyType.TREND_FOLLOWING,
                    token_address=token_address,
                    symbol=market_data.get("symbol", "UNKNOWN"),
                    intent=OrderIntent.BUY,
                    confidence=min(float(trend_strength * 10), 1.0),
                    suggested_amount=Decimal("50"),
                    target_price=Decimal(str(current_price * 1.05)),
                    stop_loss=Decimal(str(current_price * 0.95)),
                    take_profit=Decimal(str(current_price * 1.15)),
                    reasoning=f"Strong uptrend detected: {trend_strength:.2f} strength",
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
            elif short_ma < long_ma * 0.98 and trend_strength > 0.03:  # Downtrend
                return TradingSignal(
                    signal_id=str(uuid.uuid4()),
                    strategy_type=StrategyType.TREND_FOLLOWING,
                    token_address=token_address,
                    symbol=market_data.get("symbol", "UNKNOWN"),
                    intent=OrderIntent.SELL,
                    confidence=min(float(trend_strength * 10), 1.0),
                    suggested_amount=Decimal("50"),
                    target_price=Decimal(str(current_price * 0.95)),
                    stop_loss=Decimal(str(current_price * 1.05)),
                    take_profit=Decimal(str(current_price * 0.85)),
                    reasoning=f"Strong downtrend detected: {trend_strength:.2f} strength",
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Trend signal generation failed: {e}")
            return None
    
    async def _generate_momentum_signal(
        self, 
        token_address: str, 
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Generate momentum trading signal."""
        try:
            volume_24h = market_data.get("volume_24h", 0)
            price_change_24h = market_data.get("price_change_24h", 0)
            current_price = market_data.get("current_price", 0)
            
            # Check for momentum conditions
            high_volume = volume_24h > market_data.get("avg_volume", 0) * 2
            significant_price_move = abs(price_change_24h) > 10  # 10%+ move
            
            if high_volume and significant_price_move:
                intent = OrderIntent.BUY if price_change_24h > 0 else OrderIntent.SELL
                confidence = min(abs(price_change_24h) / 50.0, 1.0)
                
                return TradingSignal(
                    signal_id=str(uuid.uuid4()),
                    strategy_type=StrategyType.MOMENTUM,
                    token_address=token_address,
                    symbol=market_data.get("symbol", "UNKNOWN"),
                    intent=intent,
                    confidence=confidence,
                    suggested_amount=Decimal("75"),
                    target_price=None,
                    stop_loss=None,
                    take_profit=None,
                    reasoning=f"High momentum: {price_change_24h:.1f}% price change with {volume_24h:.0f} volume",
                    expires_at=datetime.utcnow() + timedelta(minutes=30)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Momentum signal generation failed: {e}")
            return None
    
    async def _signal_processor(self) -> None:
        """Background task to process trading signals."""
        while True:
            try:
                if not self.is_running:
                    await asyncio.sleep(1)
                    continue
                
                # Clean up expired signals
                self.active_signals = [
                    signal for signal in self.active_signals 
                    if not signal.is_expired
                ]
                
                # Process active signals
                for signal in self.active_signals:
                    if signal.confidence >= 0.7 and self.config.trading_mode == TradingMode.FULLY_AUTOMATED:
                        # Auto-execute high confidence signals
                        await self.execution_queue.put({
                            "type": "signal_execution",
                            "signal": signal,
                            "auto_execute": True
                        })
                    elif signal.confidence >= 0.5:
                        # Notify for manual review
                        for callback in self.signal_callbacks:
                            callback(signal)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Signal processor error: {e}")
                await asyncio.sleep(30)
    
    async def _execution_processor(self) -> None:
        """Background task to process trade executions."""
        while True:
            try:
                if not self.is_running:
                    await asyncio.sleep(1)
                    continue
                
                # Get execution request from queue
                try:
                    execution_request = await asyncio.wait_for(
                        self.execution_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process execution request
                if execution_request["type"] == "signal_execution":
                    await self._execute_signal(execution_request["signal"])
                elif execution_request["type"] == "manual_order":
                    await self._execute_manual_order(execution_request["order"])
                
            except Exception as e:
                logger.error(f"❌ Execution processor error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_signal(self, signal: TradingSignal) -> None:
        """Execute a trading signal."""
        try:
            logger.info(f"🎯 Executing signal: {signal.intent.value} {signal.symbol}")
            
            # Get connected wallets (use first available)
            connected_wallets = self.wallet_manager.get_connected_wallets()
            if not connected_wallets:
                logger.warning("⚠️ No wallets connected for signal execution")
                return
            
            wallet_address = connected_wallets[0]["address"]
            
            # Execute trade
            result = await self.execute_manual_trade(
                wallet_address=wallet_address,
                token_address=signal.token_address,
                intent=signal.intent,
                amount=signal.suggested_amount
            )
            
            if result.success:
                logger.info(f"✅ Signal executed successfully: {result.trade_id}")
                self.active_signals.remove(signal)
            else:
                logger.error(f"❌ Signal execution failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"❌ Signal execution error: {e}")
    
    async def _run_strategies(self, wallet_address: str) -> None:
        """Run enabled trading strategies."""
        while self.is_running:
            try:
                # Mock market data - in production, get from real data sources
                mock_tokens = [
                    {
                        "address": "0xa0b86a33e6441d8a5a8e6e6f7b8e9e9e9e9e9e9e",
                        "symbol": "MOCK1",
                        "current_price": 1.5,
                        "price_change_24h": 15.5,
                        "volume_24h": 1000000,
                        "avg_volume": 500000,
                        "price_history": [1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.48, 1.52, 1.55]
                    }
                ]
                
                for token_data in mock_tokens:
                    for strategy in self.config.enabled_strategies:
                        signal = await self.generate_trading_signal(
                            strategy_type=strategy,
                            token_address=token_data["address"],
                            market_data=token_data
                        )
                        
                        if signal and signal not in self.active_signals:
                            self.active_signals.append(signal)
                            logger.info(
                                f"📈 New signal: {signal.strategy_type.value} "
                                f"{signal.intent.value} {signal.symbol} "
                                f"(confidence: {signal.confidence:.2f})"
                            )
                
                await asyncio.sleep(60)  # Run strategies every minute
                
            except Exception as e:
                logger.error(f"❌ Strategy runner error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _cancel_all_pending_orders(self) -> int:
        """Cancel all pending orders."""
        cancelled_count = 0
        for order_id in list(self.pending_orders.keys()):
            try:
                # Cancel order logic here
                del self.pending_orders[order_id]
                cancelled_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to cancel order {order_id}: {e}")
        
        return cancelled_count
    
    async def _daily_reset_task(self) -> None:
        """Daily reset task for P&L and limits."""
        while True:
            try:
                current_date = datetime.utcnow().date()
                if current_date > self.last_reset_date:
                    # Reset daily metrics
                    self.daily_pnl = Decimal("0")
                    self.last_reset_date = current_date
                    logger.info("🔄 Daily metrics reset")
                
                # Wait until next day
                tomorrow = datetime.combine(current_date + timedelta(days=1), datetime.min.time())
                wait_seconds = (tomorrow - datetime.utcnow()).total_seconds()
                await asyncio.sleep(wait_seconds)
                
            except Exception as e:
                logger.error(f"❌ Daily reset task error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        win_rate = (
            (self.successful_trades / self.total_trades * 100) 
            if self.total_trades > 0 else 0
        )
        
        return {
            "total_trades": self.total_trades,
            "successful_trades": self.successful_trades,
            "win_rate": f"{win_rate:.1f}%",
            "daily_pnl": str(self.daily_pnl),
            "active_signals": len(self.active_signals),
            "pending_orders": len(self.pending_orders)
        }
    
    def add_signal_callback(self, callback: Callable[[TradingSignal], None]) -> None:
        """Add callback for signal notifications."""
        self.signal_callbacks.append(callback)
    
    def remove_signal_callback(self, callback: Callable[[TradingSignal], None]) -> None:
        """Remove signal callback."""
        if callback in self.signal_callbacks:
            self.signal_callbacks.remove(callback)
    
    async def get_active_signals(self) -> List[Dict[str, Any]]:
        """Get list of active trading signals."""
        return [
            {
                "signal_id": signal.signal_id,
                "strategy": signal.strategy_type.value,
                "symbol": signal.symbol,
                "intent": signal.intent.value,
                "confidence": signal.confidence,
                "suggested_amount": str(signal.suggested_amount),
                "reasoning": signal.reasoning,
                "expires_at": signal.expires_at.isoformat(),
                "created_at": signal.created_at.isoformat()
            }
            for signal in self.active_signals
        ]
    
    async def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading engine status."""
        return {
            "is_running": self.is_running,
            "trading_mode": self.config.trading_mode.value if self.config else None,
            "network": self.network.value,
            "stats": await self._get_session_stats(),
            "config": {
                "max_position_size": str(self.config.max_position_size) if self.config else None,
                "risk_tolerance": self.config.risk_tolerance.value if self.config else None,
                "enabled_strategies": [s.value for s in self.config.enabled_strategies] if self.config else []
            }
        }
    
    async def update_configuration(self, new_config: TradingConfiguration) -> Dict[str, Any]:
        """Update trading configuration."""
        try:
            old_mode = self.config.trading_mode if self.config else None
            self.config = new_config
            
            logger.info(f"⚙️ Configuration updated - Mode: {new_config.trading_mode.value}")
            
            return {
                "success": True,
                "message": "Configuration updated successfully",
                "changes": {
                    "old_mode": old_mode.value if old_mode else None,
                    "new_mode": new_config.trading_mode.value
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Configuration update failed: {e}")
            raise TradingError(f"Configuration update failed: {e}")
    
    async def force_execute_signal(self, signal_id: str) -> ExecutionResult:
        """Force execute a specific signal."""
        try:
            # Find signal
            signal = None
            for s in self.active_signals:
                if s.signal_id == signal_id:
                    signal = s
                    break
            
            if not signal:
                raise TradingError(f"Signal {signal_id} not found")
            
            # Get connected wallet
            connected_wallets = self.wallet_manager.get_connected_wallets()
            if not connected_wallets:
                raise TradingError("No wallets connected")
            
            wallet_address = connected_wallets[0]["address"]
            
            # Execute trade
            result = await self.execute_manual_trade(
                wallet_address=wallet_address,
                token_address=signal.token_address,
                intent=signal.intent,
                amount=signal.suggested_amount
            )
            
            # Remove signal if successful
            if result.success:
                self.active_signals.remove(signal)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Force execution failed: {e}")
            raise TradingError(f"Force execution failed: {e}")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown trading engine."""
        try:
            logger.info("🛑 Shutting down Trading Engine...")
            
            # Stop trading
            if self.is_running:
                await self.stop_trading()
            
            # Cancel all pending orders
            await self._cancel_all_pending_orders()
            
            # Clear state
            self.active_signals.clear()
            self.signal_callbacks.clear()
            
            logger.info("✅ Trading Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")
            raise TradingError(f"Shutdown failed: {e}")