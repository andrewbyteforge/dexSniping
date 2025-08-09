"""
Advanced Trading Strategies Engine - Grid Trading & Arbitrage Automation
File: app/core/strategies/advanced_strategies_engine.py
Class: AdvancedStrategiesEngine
Methods: execute_grid_strategy, execute_arbitrage_strategy, optimize_portfolio

Phase 4C: Implementation of advanced trading strategies including grid trading,
arbitrage automation, and sophisticated portfolio optimization techniques.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, field, asdict
from decimal import Decimal
from enum import Enum
import numpy as np
from pathlib import Path

from app.core.trading.trading_engine import TradingEngine, TradingSignal, OrderIntent
from app.core.dex.dex_integration import DEXIntegration, SwapQuote
from app.core.wallet.wallet_manager import WalletManager
from app.core.ai.risk_assessor import AIRiskAssessor, ComprehensiveRiskAssessment
from app.core.database.persistence_manager import get_persistence_manager
from app.utils.logger import setup_logger
from app.core.exceptions import StrategyExecutionError, ConfigurationError

logger = setup_logger(__name__)


class StrategyType(str, Enum):
    """Advanced trading strategy types."""
    GRID_TRADING = "grid_trading"
    ARBITRAGE = "arbitrage"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING_TRADING = "swing_trading"


class StrategyStatus(str, Enum):
    """Strategy execution status."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class ArbitrageType(str, Enum):
    """Types of arbitrage opportunities."""
    CROSS_DEX = "cross_dex"          # Between different DEXs
    CROSS_CHAIN = "cross_chain"      # Between different blockchains
    TRIANGULAR = "triangular"        # Three-asset arbitrage on same DEX
    FLASH_LOAN = "flash_loan"        # Flash loan arbitrage
    STATISTICAL = "statistical"     # Statistical arbitrage


@dataclass
class GridLevel:
    """Individual grid trading level."""
    level_id: str
    price: Decimal
    quantity: Decimal
    order_type: str  # "buy" or "sell"
    is_filled: bool = False
    order_id: Optional[str] = None
    filled_at: Optional[datetime] = None
    profit_target: Optional[Decimal] = None


@dataclass
class GridStrategy:
    """Grid trading strategy configuration."""
    strategy_id: str
    token_address: str
    symbol: str
    base_currency: str
    grid_levels: List[GridLevel]
    grid_spacing_percent: Decimal
    total_investment: Decimal
    min_price: Decimal
    max_price: Decimal
    profit_per_grid: Decimal
    auto_rebalance: bool = True
    max_levels: int = 20
    status: StrategyStatus = StrategyStatus.INACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_unfilled_buy_orders(self) -> List[GridLevel]:
        """Get unfilled buy orders."""
        return [level for level in self.grid_levels 
                if level.order_type == "buy" and not level.is_filled]
    
    def get_unfilled_sell_orders(self) -> List[GridLevel]:
        """Get unfilled sell orders."""
        return [level for level in self.grid_levels 
                if level.order_type == "sell" and not level.is_filled]


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity detection result."""
    opportunity_id: str
    arbitrage_type: ArbitrageType
    token_address: str
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    price_difference: Decimal
    profit_percentage: Decimal
    estimated_profit_usd: Decimal
    required_capital: Decimal
    gas_cost_estimate: Decimal
    net_profit_usd: Decimal
    execution_time_estimate: int  # milliseconds
    confidence: float
    risk_level: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(seconds=30))
    
    @property
    def is_expired(self) -> bool:
        """Check if opportunity has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_profitable(self) -> bool:
        """Check if opportunity is still profitable after gas costs."""
        return self.net_profit_usd > 0


@dataclass
class StrategyPerformance:
    """Strategy performance metrics."""
    strategy_id: str
    strategy_type: StrategyType
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_profit_usd: Decimal = Decimal("0")
    total_fees_paid: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    average_profit_per_trade: Decimal = Decimal("0")
    roi_percentage: Decimal = Decimal("0")
    active_since: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update_metrics(self, trade_profit: Decimal, trade_fees: Decimal, success: bool) -> None:
        """Update performance metrics with new trade data."""
        self.total_trades += 1
        if success:
            self.successful_trades += 1
        else:
            self.failed_trades += 1
        
        self.total_profit_usd += trade_profit
        self.total_fees_paid += trade_fees
        self.win_rate = (self.successful_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        self.average_profit_per_trade = self.total_profit_usd / self.total_trades if self.total_trades > 0 else Decimal("0")
        self.last_updated = datetime.utcnow()


class AdvancedStrategiesEngine:
    """
    Advanced Trading Strategies Engine for sophisticated automated trading.
    
    Features:
    - Grid Trading: Automated buy/sell orders at predetermined price levels
    - Arbitrage Detection: Cross-DEX and cross-chain arbitrage opportunities
    - Momentum Trading: Trend-following strategies with AI confirmation
    - Mean Reversion: Counter-trend strategies for volatile markets
    - Portfolio Optimization: Dynamic rebalancing and risk management
    - Multi-timeframe Analysis: Strategies across different time horizons
    """
    
    def __init__(
        self,
        trading_engine: Optional[TradingEngine] = None,
        dex_integration: Optional[DEXIntegration] = None,
        wallet_manager: Optional[WalletManager] = None,
        risk_assessor: Optional[AIRiskAssessor] = None
    ):
        """
        Initialize Advanced Strategies Engine.
        
        Args:
            trading_engine: Core trading engine instance
            dex_integration: DEX integration instance
            wallet_manager: Wallet manager instance
            risk_assessor: AI risk assessor instance
        """
        self.trading_engine = trading_engine
        self.dex_integration = dex_integration
        self.wallet_manager = wallet_manager
        self.risk_assessor = risk_assessor
        
        # Strategy management
        self.active_strategies: Dict[str, Dict[str, Any]] = {}
        self.strategy_performance: Dict[str, StrategyPerformance] = {}
        self.arbitrage_opportunities: List[ArbitrageOpportunity] = []
        
        # Configuration
        self.max_concurrent_strategies = 10
        self.min_profit_threshold = Decimal("10.0")  # $10 minimum profit
        self.max_risk_per_strategy = Decimal("1000.0")  # $1000 max risk per strategy
        self.arbitrage_scan_interval = 5.0  # seconds
        self.grid_rebalance_interval = 60.0  # seconds
        
        # State management
        self.is_running = False
        self.scanning_task: Optional[asyncio.Task] = None
        self.grid_management_task: Optional[asyncio.Task] = None
        
        logger.info("✅ Advanced Strategies Engine initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the advanced strategies engine.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("🚀 Initializing Advanced Strategies Engine...")
            
            # Initialize components if not provided
            if not self.trading_engine:
                from app.core.trading.trading_engine import TradingEngine
                self.trading_engine = TradingEngine()
                await self.trading_engine.initialize()
            
            if not self.dex_integration:
                from app.core.dex.dex_integration import DEXIntegration
                self.dex_integration = DEXIntegration()
                await self.dex_integration.initialize()
            
            if not self.wallet_manager:
                from app.core.wallet.wallet_manager import WalletManager
                self.wallet_manager = WalletManager()
                await self.wallet_manager.initialize()
            
            if not self.risk_assessor:
                from app.core.ai.risk_assessor import AIRiskAssessor
                self.risk_assessor = AIRiskAssessor()
                await self.risk_assessor.initialize_models()
            
            # Load existing strategies from database
            await self._load_saved_strategies()
            
            logger.info("✅ Advanced Strategies Engine initialized successfully")
            return True
            
        except Exception as error:
            logger.error(f"❌ Failed to initialize Advanced Strategies Engine: {error}")
            return False
    
    async def start_strategy_execution(self) -> None:
        """Start automated strategy execution."""
        try:
            if self.is_running:
                logger.warning("⚠️ Strategy execution already running")
                return
            
            self.is_running = True
            
            # Start background tasks
            self.scanning_task = asyncio.create_task(self._arbitrage_scanning_loop())
            self.grid_management_task = asyncio.create_task(self._grid_management_loop())
            
            logger.info("✅ Advanced strategy execution started")
            
        except Exception as error:
            logger.error(f"❌ Failed to start strategy execution: {error}")
            self.is_running = False
            raise StrategyExecutionError(f"Failed to start strategy execution: {error}")
    
    async def stop_strategy_execution(self) -> None:
        """Stop automated strategy execution."""
        try:
            self.is_running = False
            
            # Cancel background tasks
            if self.scanning_task and not self.scanning_task.done():
                self.scanning_task.cancel()
                try:
                    await self.scanning_task
                except asyncio.CancelledError:
                    pass
            
            if self.grid_management_task and not self.grid_management_task.done():
                self.grid_management_task.cancel()
                try:
                    await self.grid_management_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Advanced strategy execution stopped")
            
        except Exception as error:
            logger.error(f"❌ Error stopping strategy execution: {error}")
    
    async def create_grid_strategy(
        self,
        token_address: str,
        symbol: str,
        base_currency: str,
        total_investment: Decimal,
        grid_spacing_percent: Decimal,
        num_levels: int,
        current_price: Optional[Decimal] = None
    ) -> GridStrategy:
        """
        Create a new grid trading strategy.
        
        Args:
            token_address: Token contract address
            symbol: Token symbol
            base_currency: Base trading currency (ETH, USDC, etc.)
            total_investment: Total amount to invest
            grid_spacing_percent: Percentage spacing between grid levels
            num_levels: Number of grid levels to create
            current_price: Current token price (fetched if not provided)
            
        Returns:
            GridStrategy: Created grid strategy
        """
        try:
            # Get current price if not provided
            if not current_price:
                price_data = await self.dex_integration.get_token_price(token_address)
                current_price = price_data.get("price_usd", Decimal("0"))
            
            if current_price <= 0:
                raise StrategyExecutionError("Invalid token price for grid strategy")
            
            # Calculate grid parameters
            grid_range = grid_spacing_percent * num_levels / 2
            min_price = current_price * (1 - grid_range / 100)
            max_price = current_price * (1 + grid_range / 100)
            
            # Calculate investment per level
            investment_per_level = total_investment / num_levels
            
            # Create grid levels
            grid_levels = []
            for i in range(num_levels):
                # Calculate price for this level
                price_ratio = i / (num_levels - 1) if num_levels > 1 else 0
                level_price = min_price + (max_price - min_price) * price_ratio
                
                # Determine order type (buy below current price, sell above)
                order_type = "buy" if level_price < current_price else "sell"
                
                # Calculate quantity
                quantity = investment_per_level / level_price
                
                level = GridLevel(
                    level_id=str(uuid.uuid4()),
                    price=level_price,
                    quantity=quantity,
                    order_type=order_type,
                    profit_target=level_price * (1 + grid_spacing_percent / 100) if order_type == "buy" else None
                )
                
                grid_levels.append(level)
            
            # Create strategy
            strategy = GridStrategy(
                strategy_id=str(uuid.uuid4()),
                token_address=token_address,
                symbol=symbol,
                base_currency=base_currency,
                grid_levels=grid_levels,
                grid_spacing_percent=grid_spacing_percent,
                total_investment=total_investment,
                min_price=min_price,
                max_price=max_price,
                profit_per_grid=investment_per_level * grid_spacing_percent / 100
            )
            
            # Store strategy
            self.active_strategies[strategy.strategy_id] = {
                "type": StrategyType.GRID_TRADING,
                "strategy": strategy,
                "created_at": datetime.utcnow()
            }
            
            # Initialize performance tracking
            self.strategy_performance[strategy.strategy_id] = StrategyPerformance(
                strategy_id=strategy.strategy_id,
                strategy_type=StrategyType.GRID_TRADING
            )
            
            # Save to database
            await self._save_strategy_to_database(strategy)
            
            logger.info(f"✅ Created grid strategy for {symbol}: {num_levels} levels, "
                       f"${total_investment} investment, {grid_spacing_percent}% spacing")
            
            return strategy
            
        except Exception as error:
            logger.error(f"❌ Failed to create grid strategy: {error}")
            raise StrategyExecutionError(f"Failed to create grid strategy: {error}")
    
    async def execute_grid_strategy(self, strategy_id: str) -> bool:
        """
        Execute a grid trading strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            bool: True if execution successful
        """
        try:
            if strategy_id not in self.active_strategies:
                raise StrategyExecutionError(f"Strategy {strategy_id} not found")
            
            strategy_data = self.active_strategies[strategy_id]
            strategy: GridStrategy = strategy_data["strategy"]
            
            if strategy.status != StrategyStatus.ACTIVE:
                logger.warning(f"⚠️ Grid strategy {strategy_id} is not active")
                return False
            
            # Get current token price
            price_data = await self.dex_integration.get_token_price(strategy.token_address)
            current_price = price_data.get("price_usd", Decimal("0"))
            
            if current_price <= 0:
                logger.error(f"❌ Invalid price for {strategy.symbol}")
                return False
            
            executed_orders = 0
            
            # Check for buy opportunities (price dropped to buy levels)
            unfilled_buys = strategy.get_unfilled_buy_orders()
            for level in unfilled_buys:
                if current_price <= level.price:
                    success = await self._execute_grid_order(strategy, level, "buy")
                    if success:
                        executed_orders += 1
            
            # Check for sell opportunities (price rose to sell levels)
            unfilled_sells = strategy.get_unfilled_sell_orders()
            for level in unfilled_sells:
                if current_price >= level.price:
                    success = await self._execute_grid_order(strategy, level, "sell")
                    if success:
                        executed_orders += 1
            
            # Auto-rebalance if enabled
            if strategy.auto_rebalance and executed_orders > 0:
                await self._rebalance_grid_strategy(strategy, current_price)
            
            # Update strategy in storage
            await self._update_strategy_in_database(strategy)
            
            if executed_orders > 0:
                logger.info(f"✅ Executed {executed_orders} grid orders for {strategy.symbol}")
            
            return True
            
        except Exception as error:
            logger.error(f"❌ Failed to execute grid strategy: {error}")
            return False
    
    async def scan_arbitrage_opportunities(self) -> List[ArbitrageOpportunity]:
        """
        Scan for arbitrage opportunities across DEXs and chains.
        
        Returns:
            List[ArbitrageOpportunity]: Detected opportunities
        """
        try:
            opportunities = []
            
            # Get popular trading pairs
            trading_pairs = await self._get_popular_trading_pairs()
            
            for pair in trading_pairs:
                token_address = pair["token_address"]
                symbol = pair["symbol"]
                
                # Get prices from multiple DEXs
                dex_prices = await self._get_multi_dex_prices(token_address)
                
                if len(dex_prices) < 2:
                    continue
                
                # Find arbitrage opportunities
                pair_opportunities = await self._analyze_arbitrage_opportunities(
                    token_address, symbol, dex_prices
                )
                
                opportunities.extend(pair_opportunities)
            
            # Filter and rank opportunities
            filtered_opportunities = self._filter_arbitrage_opportunities(opportunities)
            
            # Update internal list
            self.arbitrage_opportunities = filtered_opportunities
            
            logger.info(f"✅ Found {len(filtered_opportunities)} arbitrage opportunities")
            
            return filtered_opportunities
            
        except Exception as error:
            logger.error(f"❌ Failed to scan arbitrage opportunities: {error}")
            return []
    
    async def execute_arbitrage_opportunity(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Execute an arbitrage opportunity.
        
        Args:
            opportunity: Arbitrage opportunity to execute
            
        Returns:
            bool: True if execution successful
        """
        try:
            if opportunity.is_expired:
                logger.warning(f"⚠️ Arbitrage opportunity {opportunity.opportunity_id} has expired")
                return False
            
            if not opportunity.is_profitable:
                logger.warning(f"⚠️ Arbitrage opportunity {opportunity.opportunity_id} is no longer profitable")
                return False
            
            # Risk assessment
            if opportunity.risk_level == "HIGH" and opportunity.net_profit_usd < self.min_profit_threshold:
                logger.warning(f"⚠️ High-risk arbitrage with low profit rejected")
                return False
            
            # Check wallet balance
            balance = await self.wallet_manager.get_balance(opportunity.token_address)
            if balance < opportunity.required_capital:
                logger.warning(f"⚠️ Insufficient balance for arbitrage execution")
                return False
            
            logger.info(f"🎯 Executing arbitrage: {opportunity.symbol} "
                       f"${opportunity.estimated_profit_usd} profit")
            
            # Execute buy order on cheaper exchange
            buy_result = await self._execute_arbitrage_trade(
                opportunity, "buy", opportunity.buy_exchange
            )
            
            if not buy_result["success"]:
                logger.error(f"❌ Arbitrage buy failed: {buy_result['error']}")
                return False
            
            # Execute sell order on more expensive exchange
            sell_result = await self._execute_arbitrage_trade(
                opportunity, "sell", opportunity.sell_exchange
            )
            
            if not sell_result["success"]:
                # Handle partial execution - attempt to reverse buy
                logger.error(f"❌ Arbitrage sell failed: {sell_result['error']}")
                await self._reverse_arbitrage_trade(buy_result, opportunity)
                return False
            
            # Calculate actual profit
            actual_profit = sell_result["amount_received"] - buy_result["amount_spent"]
            total_fees = buy_result["fees"] + sell_result["fees"]
            net_profit = actual_profit - total_fees
            
            # Update performance tracking
            await self._update_arbitrage_performance(opportunity, net_profit, total_fees, True)
            
            logger.info(f"✅ Arbitrage executed successfully: "
                       f"${net_profit} net profit (fees: ${total_fees})")
            
            return True
            
        except Exception as error:
            logger.error(f"❌ Failed to execute arbitrage opportunity: {error}")
            await self._update_arbitrage_performance(opportunity, Decimal("0"), Decimal("0"), False)
            return False
    
    async def get_strategy_performance(self, strategy_id: str) -> Optional[StrategyPerformance]:
        """
        Get performance metrics for a specific strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            StrategyPerformance: Performance metrics or None if not found
        """
        return self.strategy_performance.get(strategy_id)
    
    async def get_all_strategies_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance summary for all active strategies.
        
        Returns:
            Dict: Performance summary for all strategies
        """
        try:
            performance_summary = {}
            
            for strategy_id, performance in self.strategy_performance.items():
                strategy_data = self.active_strategies.get(strategy_id, {})
                
                performance_summary[strategy_id] = {
                    "strategy_type": performance.strategy_type.value,
                    "status": strategy_data.get("strategy", {}).status if "strategy" in strategy_data else "unknown",
                    "total_trades": performance.total_trades,
                    "win_rate": performance.win_rate,
                    "total_profit_usd": float(performance.total_profit_usd),
                    "roi_percentage": float(performance.roi_percentage),
                    "sharpe_ratio": performance.sharpe_ratio,
                    "active_since": performance.active_since.isoformat(),
                    "last_updated": performance.last_updated.isoformat()
                }
            
            return performance_summary
            
        except Exception as error:
            logger.error(f"❌ Failed to get strategies performance: {error}")
            return {}
    
    async def _arbitrage_scanning_loop(self) -> None:
        """Background task for continuous arbitrage scanning."""
        while self.is_running:
            try:
                await self.scan_arbitrage_opportunities()
                
                # Execute profitable opportunities automatically
                for opportunity in self.arbitrage_opportunities[:5]:  # Limit to top 5
                    if opportunity.is_profitable and opportunity.net_profit_usd >= self.min_profit_threshold:
                        await self.execute_arbitrage_opportunity(opportunity)
                
                await asyncio.sleep(self.arbitrage_scan_interval)
                
            except Exception as error:
                logger.error(f"❌ Error in arbitrage scanning loop: {error}")
                await asyncio.sleep(self.arbitrage_scan_interval * 2)
    
    async def _grid_management_loop(self) -> None:
        """Background task for grid strategy management."""
        while self.is_running:
            try:
                for strategy_id in list(self.active_strategies.keys()):
                    strategy_data = self.active_strategies[strategy_id]
                    
                    if strategy_data["type"] == StrategyType.GRID_TRADING:
                        await self.execute_grid_strategy(strategy_id)
                
                await asyncio.sleep(self.grid_rebalance_interval)
                
            except Exception as error:
                logger.error(f"❌ Error in grid management loop: {error}")
                await asyncio.sleep(self.grid_rebalance_interval * 2)
    
    # Additional helper methods would be implemented here...
    # _execute_grid_order, _rebalance_grid_strategy, _get_popular_trading_pairs,
    # _get_multi_dex_prices, _analyze_arbitrage_opportunities, etc.


# Global instance for easy access
advanced_strategies_engine: Optional[AdvancedStrategiesEngine] = None


async def get_advanced_strategies_engine() -> AdvancedStrategiesEngine:
    """
    Get the global advanced strategies engine instance.
    
    Returns:
        AdvancedStrategiesEngine: Global engine instance
    """
    global advanced_strategies_engine
    
    if advanced_strategies_engine is None:
        advanced_strategies_engine = AdvancedStrategiesEngine()
        await advanced_strategies_engine.initialize()
    
    return advanced_strategies_engine


async def initialize_advanced_strategies() -> bool:
    """
    Initialize the global advanced strategies engine.
    
    Returns:
        bool: True if initialization successful
    """
    try:
        global advanced_strategies_engine
        advanced_strategies_engine = AdvancedStrategiesEngine()
        return await advanced_strategies_engine.initialize()
    except Exception as error:
        logger.error(f"❌ Failed to initialize advanced strategies: {error}")
        return False