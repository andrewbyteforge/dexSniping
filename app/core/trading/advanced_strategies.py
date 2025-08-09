"""
Advanced Trading Strategies System - Phase 4C Implementation
File: app/core/trading/advanced_strategies.py
Class: AdvancedTradingStrategies
Methods: grid_trading_strategy, arbitrage_strategy, momentum_strategy, mean_reversion_strategy

Professional implementation of advanced trading strategies with AI integration,
risk management, and performance optimization for maximum profit generation.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from app.utils.logger import setup_logger
from app.core.exceptions import (
    TradingError,
    InsufficientFundsError,
    RiskManagementError
)

logger = setup_logger(__name__)


class StrategyType(str, Enum):
    """Advanced trading strategy types."""
    GRID_TRADING = "grid_trading"
    ARBITRAGE = "arbitrage"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    LIQUIDITY_SNIPING = "liquidity_sniping"
    MEV_PROTECTION = "mev_protection"
    SWING_TRADING = "swing_trading"
    SCALPING = "scalping"


class TradingSignal(str, Enum):
    """Trading signal types."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    HOLD = "hold"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class StrategyConfiguration:
    """Strategy configuration parameters."""
    strategy_type: StrategyType
    enabled: bool = True
    allocation_percentage: float = 10.0  # % of portfolio to allocate
    max_position_size: float = 1000.0   # Maximum position size in USD
    stop_loss_percentage: float = 5.0    # Stop loss threshold
    take_profit_percentage: float = 15.0 # Take profit threshold
    max_slippage: float = 1.0           # Maximum acceptable slippage
    min_liquidity_usd: float = 50000.0  # Minimum liquidity requirement
    confidence_threshold: float = 0.7   # Minimum confidence for execution
    risk_level: RiskLevel = RiskLevel.MEDIUM
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradingOpportunity:
    """Identified trading opportunity."""
    opportunity_id: str
    strategy_type: StrategyType
    token_address: str
    token_symbol: str
    network: str
    signal: TradingSignal
    confidence: float
    expected_profit: float
    risk_score: float
    entry_price: float
    target_price: float
    stop_loss_price: float
    position_size: float
    max_slippage: float
    reasoning: str
    metadata: Dict[str, Any]
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if opportunity has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio."""
        if self.entry_price == 0:
            return 0.0
        
        potential_loss = abs(self.entry_price - self.stop_loss_price)
        potential_gain = abs(self.target_price - self.entry_price)
        
        if potential_loss == 0:
            return float('inf')
        
        return potential_gain / potential_loss


@dataclass
class GridTradingConfig:
    """Grid trading strategy configuration."""
    grid_levels: int = 10
    grid_spacing_percentage: float = 2.0
    total_investment: float = 1000.0
    rebalance_threshold: float = 10.0
    min_profit_per_trade: float = 0.5
    max_grid_deviation: float = 20.0


@dataclass
class ArbitrageConfig:
    """Arbitrage strategy configuration."""
    min_price_difference: float = 0.5  # Minimum price difference %
    max_execution_time: int = 30       # Max execution time in seconds
    gas_cost_threshold: float = 10.0   # Max gas cost in USD
    dex_pairs: List[str] = field(default_factory=lambda: ["uniswap_v2", "sushiswap"])
    min_volume_24h: float = 100000.0   # Minimum 24h volume


@dataclass
class MomentumConfig:
    """Momentum strategy configuration."""
    lookback_period: int = 24          # Hours to look back
    momentum_threshold: float = 5.0    # Minimum momentum %
    volume_surge_multiplier: float = 2.0
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    macd_signal_threshold: float = 0.0


@dataclass
class StrategyPerformance:
    """Strategy performance metrics."""
    strategy_type: StrategyType
    total_trades: int = 0
    profitable_trades: int = 0
    total_profit_loss: float = 0.0
    average_profit_per_trade: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    risk_adjusted_return: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class AdvancedTradingStrategies:
    """
    Advanced Trading Strategies System
    
    Professional implementation of sophisticated trading strategies with AI integration,
    risk management, and performance optimization. Designed to compete with and exceed
    paid trading bot applications.
    
    Features:
    - Grid Trading: Automated buy/sell orders at predefined price levels
    - Arbitrage: Cross-DEX price difference exploitation
    - Momentum: Trend-following with technical indicators
    - Mean Reversion: Statistical arbitrage and counter-trend trading
    - Liquidity Sniping: Early detection of new liquidity pools
    - MEV Protection: Front-running and sandwich attack mitigation
    """
    
    def __init__(self):
        """Initialize advanced trading strategies system."""
        self.strategies: Dict[StrategyType, StrategyConfiguration] = {}
        self.active_opportunities: Dict[str, TradingOpportunity] = {}
        self.performance_metrics: Dict[StrategyType, StrategyPerformance] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Strategy states
        self.grid_positions: Dict[str, Dict] = {}
        self.arbitrage_monitoring: Dict[str, Dict] = {}
        self.momentum_indicators: Dict[str, Dict] = {}
        
        # Performance tracking
        self.total_opportunities_identified = 0
        self.total_profits_generated = 0.0
        self.system_start_time = datetime.utcnow()
        
        # Initialize default configurations
        self._initialize_default_strategies()
        
        logger.info("🧠 Advanced Trading Strategies System initialized")
    
    def _initialize_default_strategies(self) -> None:
        """Initialize default strategy configurations."""
        try:
            # Grid Trading Strategy
            self.strategies[StrategyType.GRID_TRADING] = StrategyConfiguration(
                strategy_type=StrategyType.GRID_TRADING,
                allocation_percentage=20.0,
                max_position_size=2000.0,
                stop_loss_percentage=10.0,
                take_profit_percentage=20.0,
                confidence_threshold=0.8,
                risk_level=RiskLevel.MEDIUM,
                parameters={
                    "grid_levels": 15,
                    "grid_spacing": 1.5,
                    "rebalance_threshold": 8.0
                }
            )
            
            # Arbitrage Strategy
            self.strategies[StrategyType.ARBITRAGE] = StrategyConfiguration(
                strategy_type=StrategyType.ARBITRAGE,
                allocation_percentage=15.0,
                max_position_size=5000.0,
                stop_loss_percentage=2.0,
                take_profit_percentage=3.0,
                confidence_threshold=0.9,
                risk_level=RiskLevel.LOW,
                parameters={
                    "min_price_diff": 0.3,
                    "max_execution_time": 20,
                    "gas_threshold": 15.0
                }
            )
            
            # Momentum Strategy
            self.strategies[StrategyType.MOMENTUM] = StrategyConfiguration(
                strategy_type=StrategyType.MOMENTUM,
                allocation_percentage=25.0,
                max_position_size=3000.0,
                stop_loss_percentage=7.0,
                take_profit_percentage=25.0,
                confidence_threshold=0.75,
                risk_level=RiskLevel.HIGH,
                parameters={
                    "lookback_hours": 12,
                    "momentum_threshold": 8.0,
                    "volume_multiplier": 3.0
                }
            )
            
            # Mean Reversion Strategy
            self.strategies[StrategyType.MEAN_REVERSION] = StrategyConfiguration(
                strategy_type=StrategyType.MEAN_REVERSION,
                allocation_percentage=20.0,
                max_position_size=1500.0,
                stop_loss_percentage=5.0,
                take_profit_percentage=12.0,
                confidence_threshold=0.7,
                risk_level=RiskLevel.MEDIUM,
                parameters={
                    "deviation_threshold": 2.0,
                    "reversion_period": 6,
                    "volatility_filter": 15.0
                }
            )
            
            # Initialize performance tracking
            for strategy_type in self.strategies.keys():
                self.performance_metrics[strategy_type] = StrategyPerformance(
                    strategy_type=strategy_type
                )
            
            logger.info("✅ Default trading strategies configured")
            
        except Exception as e:
            logger.error(f"❌ Error initializing default strategies: {e}")
            raise TradingError(f"Strategy initialization failed: {e}")
    
    async def grid_trading_strategy(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        current_price: float,
        liquidity_usd: float,
        config: Optional[GridTradingConfig] = None
    ) -> Optional[TradingOpportunity]:
        """
        Grid Trading Strategy Implementation
        
        Creates buy and sell orders at predetermined price levels to profit
        from market volatility and sideways movement.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            current_price: Current token price
            liquidity_usd: Available liquidity in USD
            config: Grid trading configuration
            
        Returns:
            TradingOpportunity if suitable for grid trading
        """
        try:
            config = config or GridTradingConfig()
            strategy_config = self.strategies[StrategyType.GRID_TRADING]
            
            if not strategy_config.enabled:
                return None
            
            # Check liquidity requirements
            if liquidity_usd < strategy_config.min_liquidity_usd:
                return None
            
            # Calculate grid levels
            grid_spacing = current_price * (config.grid_spacing_percentage / 100)
            grid_levels = []
            
            # Create buy levels below current price
            for i in range(1, config.grid_levels // 2 + 1):
                buy_price = current_price - (grid_spacing * i)
                if buy_price > 0:
                    grid_levels.append({
                        "price": buy_price,
                        "action": "buy",
                        "size": config.total_investment / config.grid_levels
                    })
            
            # Create sell levels above current price
            for i in range(1, config.grid_levels // 2 + 1):
                sell_price = current_price + (grid_spacing * i)
                grid_levels.append({
                    "price": sell_price,
                    "action": "sell",
                    "size": config.total_investment / config.grid_levels
                })
            
            # Calculate expected profit
            expected_profit = await self._calculate_grid_profit_potential(
                grid_levels, current_price, config
            )
            
            # Risk assessment
            risk_score = await self._assess_grid_trading_risk(
                token_address, current_price, liquidity_usd, config
            )
            
            # Generate confidence score
            confidence = await self._calculate_grid_confidence(
                token_address, current_price, liquidity_usd, grid_levels
            )
            
            if confidence < strategy_config.confidence_threshold:
                return None
            
            # Create trading opportunity
            opportunity = TradingOpportunity(
                opportunity_id=str(uuid.uuid4()),
                strategy_type=StrategyType.GRID_TRADING,
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                signal=TradingSignal.BUY if expected_profit > 10 else TradingSignal.HOLD,
                confidence=confidence,
                expected_profit=expected_profit,
                risk_score=risk_score,
                entry_price=current_price,
                target_price=current_price * 1.15,  # 15% target
                stop_loss_price=current_price * 0.90,  # 10% stop loss
                position_size=min(config.total_investment, strategy_config.max_position_size),
                max_slippage=strategy_config.max_slippage,
                reasoning=f"Grid trading opportunity with {len(grid_levels)} levels, "
                         f"expected profit: {expected_profit:.2f}%",
                metadata={
                    "grid_levels": grid_levels,
                    "grid_spacing": grid_spacing,
                    "total_levels": len(grid_levels),
                    "strategy_config": config.__dict__
                },
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            self.active_opportunities[opportunity.opportunity_id] = opportunity
            self.total_opportunities_identified += 1
            
            logger.info(f"🔲 Grid trading opportunity identified: {token_symbol} "
                       f"({confidence:.2f} confidence, {expected_profit:.2f}% profit)")
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Grid trading strategy error: {e}")
            return None
    
    async def arbitrage_strategy(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        dex_prices: Dict[str, float],
        liquidity_data: Dict[str, float],
        config: Optional[ArbitrageConfig] = None
    ) -> Optional[TradingOpportunity]:
        """
        Arbitrage Strategy Implementation
        
        Identifies and exploits price differences across multiple DEXes
        for risk-free profit opportunities.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            dex_prices: Prices across different DEXes
            liquidity_data: Liquidity data for each DEX
            config: Arbitrage configuration
            
        Returns:
            TradingOpportunity if arbitrage opportunity exists
        """
        try:
            config = config or ArbitrageConfig()
            strategy_config = self.strategies[StrategyType.ARBITRAGE]
            
            if not strategy_config.enabled or len(dex_prices) < 2:
                return None
            
            # Find best buy and sell prices
            buy_dex, buy_price = min(dex_prices.items(), key=lambda x: x[1])
            sell_dex, sell_price = max(dex_prices.items(), key=lambda x: x[1])
            
            # Calculate price difference
            price_difference = ((sell_price - buy_price) / buy_price) * 100
            
            if price_difference < config.min_price_difference:
                return None
            
            # Check liquidity requirements
            min_liquidity = min(
                liquidity_data.get(buy_dex, 0),
                liquidity_data.get(sell_dex, 0)
            )
            
            if min_liquidity < strategy_config.min_liquidity_usd:
                return None
            
            # Estimate gas costs
            estimated_gas_cost = await self._estimate_arbitrage_gas_cost(
                token_address, buy_dex, sell_dex, network
            )
            
            if estimated_gas_cost > config.gas_cost_threshold:
                return None
            
            # Calculate optimal position size
            position_size = await self._calculate_arbitrage_position_size(
                price_difference, min_liquidity, estimated_gas_cost, strategy_config
            )
            
            # Calculate net profit
            gross_profit = position_size * (price_difference / 100)
            net_profit = gross_profit - estimated_gas_cost
            net_profit_percentage = (net_profit / position_size) * 100
            
            if net_profit_percentage < 0.5:  # Minimum 0.5% net profit
                return None
            
            # Risk assessment (arbitrage is generally low risk)
            risk_score = await self._assess_arbitrage_risk(
                token_address, buy_dex, sell_dex, price_difference
            )
            
            # High confidence for clear arbitrage opportunities
            confidence = min(0.95, 0.7 + (price_difference / 10))
            
            # Create trading opportunity
            opportunity = TradingOpportunity(
                opportunity_id=str(uuid.uuid4()),
                strategy_type=StrategyType.ARBITRAGE,
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                signal=TradingSignal.STRONG_BUY,
                confidence=confidence,
                expected_profit=net_profit_percentage,
                risk_score=risk_score,
                entry_price=buy_price,
                target_price=sell_price,
                stop_loss_price=buy_price * 0.99,  # Minimal stop loss
                position_size=position_size,
                max_slippage=strategy_config.max_slippage,
                reasoning=f"Arbitrage opportunity: {price_difference:.2f}% price difference "
                         f"between {buy_dex} and {sell_dex}, net profit: {net_profit_percentage:.2f}%",
                metadata={
                    "buy_dex": buy_dex,
                    "sell_dex": sell_dex,
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "price_difference": price_difference,
                    "estimated_gas_cost": estimated_gas_cost,
                    "net_profit": net_profit,
                    "execution_time_limit": config.max_execution_time
                },
                expires_at=datetime.utcnow() + timedelta(seconds=config.max_execution_time)
            )
            
            self.active_opportunities[opportunity.opportunity_id] = opportunity
            self.total_opportunities_identified += 1
            
            logger.info(f"⚡ Arbitrage opportunity identified: {token_symbol} "
                       f"({price_difference:.2f}% difference, {net_profit_percentage:.2f}% net profit)")
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Arbitrage strategy error: {e}")
            return None
    
    async def momentum_strategy(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        price_history: List[Dict[str, Any]],
        volume_history: List[Dict[str, Any]],
        config: Optional[MomentumConfig] = None
    ) -> Optional[TradingOpportunity]:
        """
        Momentum Strategy Implementation
        
        Identifies tokens with strong price momentum and volume surge
        for trend-following trades.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            price_history: Historical price data
            volume_history: Historical volume data
            config: Momentum configuration
            
        Returns:
            TradingOpportunity if momentum signal detected
        """
        try:
            config = config or MomentumConfig()
            strategy_config = self.strategies[StrategyType.MOMENTUM]
            
            if not strategy_config.enabled or len(price_history) < 24:
                return None
            
            # Calculate momentum indicators
            current_price = price_history[-1]['price']
            price_24h_ago = price_history[-24]['price']
            price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            # Volume analysis
            current_volume = volume_history[-1]['volume'] if volume_history else 0
            avg_volume_24h = np.mean([v['volume'] for v in volume_history[-24:]])
            volume_surge = current_volume / avg_volume_24h if avg_volume_24h > 0 else 0
            
            # Technical indicators
            rsi = await self._calculate_rsi(price_history, period=14)
            macd_line, signal_line = await self._calculate_macd(price_history)
            
            # Momentum scoring
            momentum_score = 0
            signals = []
            
            # Price momentum
            if abs(price_change_24h) >= config.momentum_threshold:
                momentum_score += 30
                signals.append(f"Price momentum: {price_change_24h:.2f}%")
            
            # Volume surge
            if volume_surge >= config.volume_surge_multiplier:
                momentum_score += 25
                signals.append(f"Volume surge: {volume_surge:.1f}x")
            
            # RSI conditions
            if price_change_24h > 0 and rsi < config.rsi_overbought:
                momentum_score += 20
                signals.append(f"RSI bullish: {rsi:.1f}")
            elif price_change_24h < 0 and rsi > config.rsi_oversold:
                momentum_score += 15
                signals.append(f"RSI oversold bounce: {rsi:.1f}")
            
            # MACD signal
            if macd_line > signal_line and macd_line > config.macd_signal_threshold:
                momentum_score += 15
                signals.append("MACD bullish crossover")
            
            # Trend confirmation
            sma_20 = np.mean([p['price'] for p in price_history[-20:]])
            sma_50 = np.mean([p['price'] for p in price_history[-50:]]) if len(price_history) >= 50 else sma_20
            
            if current_price > sma_20 > sma_50:
                momentum_score += 10
                signals.append("Trend alignment bullish")
            
            # Determine signal strength
            if momentum_score >= 80:
                signal = TradingSignal.STRONG_BUY
            elif momentum_score >= 60:
                signal = TradingSignal.BUY
            elif momentum_score >= 40:
                signal = TradingSignal.WEAK_BUY
            else:
                return None
            
            # Calculate confidence
            confidence = min(0.95, momentum_score / 100)
            
            if confidence < strategy_config.confidence_threshold:
                return None
            
            # Risk assessment
            risk_score = await self._assess_momentum_risk(
                price_change_24h, volume_surge, rsi, current_price
            )
            
            # Calculate targets
            if price_change_24h > 0:
                target_price = current_price * (1 + strategy_config.take_profit_percentage / 100)
                stop_loss_price = current_price * (1 - strategy_config.stop_loss_percentage / 100)
            else:
                target_price = current_price * (1 - strategy_config.take_profit_percentage / 100)
                stop_loss_price = current_price * (1 + strategy_config.stop_loss_percentage / 100)
            
            # Expected profit calculation
            expected_profit = abs((target_price - current_price) / current_price) * 100
            
            # Create trading opportunity
            opportunity = TradingOpportunity(
                opportunity_id=str(uuid.uuid4()),
                strategy_type=StrategyType.MOMENTUM,
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                signal=signal,
                confidence=confidence,
                expected_profit=expected_profit,
                risk_score=risk_score,
                entry_price=current_price,
                target_price=target_price,
                stop_loss_price=stop_loss_price,
                position_size=min(
                    strategy_config.max_position_size,
                    strategy_config.allocation_percentage * 100  # Simplified calculation
                ),
                max_slippage=strategy_config.max_slippage,
                reasoning=f"Momentum strategy signals: {', '.join(signals)}. "
                         f"Score: {momentum_score}/100",
                metadata={
                    "momentum_score": momentum_score,
                    "price_change_24h": price_change_24h,
                    "volume_surge": volume_surge,
                    "rsi": rsi,
                    "macd_line": macd_line,
                    "signal_line": signal_line,
                    "signals": signals,
                    "trend_direction": "bullish" if price_change_24h > 0 else "bearish"
                },
                expires_at=datetime.utcnow() + timedelta(hours=config.lookback_period)
            )
            
            self.active_opportunities[opportunity.opportunity_id] = opportunity
            self.total_opportunities_identified += 1
            
            logger.info(f"📈 Momentum opportunity identified: {token_symbol} "
                       f"({momentum_score} score, {confidence:.2f} confidence)")
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Momentum strategy error: {e}")
            return None
    
    async def mean_reversion_strategy(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        price_history: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[TradingOpportunity]:
        """
        Mean Reversion Strategy Implementation
        
        Identifies tokens that have deviated significantly from their mean price
        and are likely to revert, creating counter-trend trading opportunities.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            price_history: Historical price data
            config: Mean reversion configuration
            
        Returns:
            TradingOpportunity if mean reversion signal detected
        """
        try:
            strategy_config = self.strategies[StrategyType.MEAN_REVERSION]
            config = config or strategy_config.parameters
            
            if not strategy_config.enabled or len(price_history) < 50:
                return None
            
            # Calculate statistical measures
            prices = [p['price'] for p in price_history]
            current_price = prices[-1]
            
            # Moving averages
            sma_20 = np.mean(prices[-20:])
            sma_50 = np.mean(prices[-50:])
            
            # Standard deviation
            price_std = np.std(prices[-20:])
            
            # Bollinger Bands
            upper_band = sma_20 + (2 * price_std)
            lower_band = sma_20 - (2 * price_std)
            
            # Z-score calculation
            z_score = (current_price - sma_20) / price_std if price_std > 0 else 0
            
            # Deviation from mean
            deviation_from_sma = ((current_price - sma_20) / sma_20) * 100
            
            # Mean reversion signals
            reversion_score = 0
            signals = []
            signal_type = TradingSignal.HOLD
            
            # Oversold conditions (potential buy)
            if current_price <= lower_band:
                reversion_score += 40
                signals.append("Price below lower Bollinger Band")
                signal_type = TradingSignal.BUY
            
            if z_score <= -2:
                reversion_score += 30
                signals.append(f"Strong negative Z-score: {z_score:.2f}")
                signal_type = TradingSignal.BUY
            
            # Overbought conditions (potential sell)
            if current_price >= upper_band:
                reversion_score += 40
                signals.append("Price above upper Bollinger Band")
                signal_type = TradingSignal.SELL
            
            if z_score >= 2:
                reversion_score += 30
                signals.append(f"Strong positive Z-score: {z_score:.2f}")
                signal_type = TradingSignal.SELL
            
            # Additional confirmation signals
            if abs(deviation_from_sma) >= config.get("deviation_threshold", 2.0):
                reversion_score += 20
                signals.append(f"Significant deviation: {deviation_from_sma:.2f}%")
            
            # Volume confirmation
            if len(price_history) > 1:
                recent_volumes = [p.get('volume', 0) for p in price_history[-5:]]
                avg_volume = np.mean(recent_volumes) if recent_volumes else 0
                if avg_volume > np.mean([p.get('volume', 0) for p in price_history[-20:]]):
                    reversion_score += 10
                    signals.append("Volume confirmation")
            
            # RSI confirmation
            rsi = await self._calculate_rsi(price_history, period=14)
            if (signal_type == TradingSignal.BUY and rsi < 30) or \
               (signal_type == TradingSignal.SELL and rsi > 70):
                reversion_score += 15
                signals.append(f"RSI confirmation: {rsi:.1f}")
            
            # Minimum score threshold
            if reversion_score < 50:
                return None
            
            # Calculate confidence
            confidence = min(0.9, reversion_score / 100)
            
            if confidence < strategy_config.confidence_threshold:
                return None
            
            # Risk assessment
            volatility = (price_std / sma_20) * 100
            risk_score = await self._assess_mean_reversion_risk(
                abs(z_score), volatility, abs(deviation_from_sma)
            )
            
            # Calculate targets based on mean reversion
            if signal_type == TradingSignal.BUY:
                target_price = sma_20  # Revert to mean
                stop_loss_price = current_price * (1 - strategy_config.stop_loss_percentage / 100)
            else:  # SELL
                target_price = sma_20  # Revert to mean
                stop_loss_price = current_price * (1 + strategy_config.stop_loss_percentage / 100)
            
            # Expected profit calculation
            expected_profit = abs((target_price - current_price) / current_price) * 100
            
            # Create trading opportunity
            opportunity = TradingOpportunity(
                opportunity_id=str(uuid.uuid4()),
                strategy_type=StrategyType.MEAN_REVERSION,
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                signal=signal_type,
                confidence=confidence,
                expected_profit=expected_profit,
                risk_score=risk_score,
                entry_price=current_price,
                target_price=target_price,
                stop_loss_price=stop_loss_price,
                position_size=min(
                    strategy_config.max_position_size,
                    strategy_config.allocation_percentage * 50  # Conservative sizing
                ),
                max_slippage=strategy_config.max_slippage,
                reasoning=f"Mean reversion signals: {', '.join(signals)}. "
                         f"Score: {reversion_score}/100",
                metadata={
                    "reversion_score": reversion_score,
                    "z_score": z_score,
                    "deviation_from_sma": deviation_from_sma,
                    "sma_20": sma_20,
                    "sma_50": sma_50,
                    "upper_band": upper_band,
                    "lower_band": lower_band,
                    "volatility": volatility,
                    "rsi": rsi,
                    "signals": signals
                },
                expires_at=datetime.utcnow() + timedelta(hours=config.get("reversion_period", 6))
            )
            
            self.active_opportunities[opportunity.opportunity_id] = opportunity
            self.total_opportunities_identified += 1
            
            logger.info(f"🔄 Mean reversion opportunity identified: {token_symbol} "
                       f"({reversion_score} score, {signal_type.value} signal)")
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Mean reversion strategy error: {e}")
            return None
    
    async def get_all_opportunities(
        self,
        min_confidence: float = 0.7,
        max_risk: float = 0.8,
        strategy_filter: Optional[List[StrategyType]] = None
    ) -> List[TradingOpportunity]:
        """
        Get all active trading opportunities with filters.
        
        Args:
            min_confidence: Minimum confidence threshold
            max_risk: Maximum risk threshold
            strategy_filter: Filter by strategy types
            
        Returns:
            List of filtered trading opportunities
        """
        try:
            opportunities = []
            
            for opportunity in self.active_opportunities.values():
                # Skip expired opportunities
                if opportunity.is_expired:
                    continue
                
                # Apply filters
                if opportunity.confidence < min_confidence:
                    continue
                
                if opportunity.risk_score > max_risk:
                    continue
                
                if strategy_filter and opportunity.strategy_type not in strategy_filter:
                    continue
                
                opportunities.append(opportunity)
            
            # Sort by expected profit * confidence
            opportunities.sort(
                key=lambda x: x.expected_profit * x.confidence,
                reverse=True
            )
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Error getting opportunities: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary for all strategies.
        
        Returns:
            Performance summary statistics
        """
        try:
            total_profit = sum(p.total_profit_loss for p in self.performance_metrics.values())
            total_trades = sum(p.total_trades for p in self.performance_metrics.values())
            
            strategy_performance = {}
            for strategy_type, performance in self.performance_metrics.items():
                strategy_performance[strategy_type.value] = {
                    "total_trades": performance.total_trades,
                    "profitable_trades": performance.profitable_trades,
                    "win_rate": performance.win_rate,
                    "total_profit_loss": performance.total_profit_loss,
                    "average_profit_per_trade": performance.average_profit_per_trade,
                    "sharpe_ratio": performance.sharpe_ratio,
                    "max_drawdown": performance.max_drawdown
                }
            
            return {
                "total_opportunities_identified": self.total_opportunities_identified,
                "active_opportunities": len(self.active_opportunities),
                "total_profits_generated": total_profit,
                "total_trades_executed": total_trades,
                "system_uptime_hours": (datetime.utcnow() - self.system_start_time).total_seconds() / 3600,
                "strategy_performance": strategy_performance,
                "enabled_strategies": [s.value for s, c in self.strategies.items() if c.enabled]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance summary: {e}")
            return {}
    
    # Helper methods for calculations
    async def _calculate_grid_profit_potential(
        self,
        grid_levels: List[Dict],
        current_price: float,
        config: GridTradingConfig
    ) -> float:
        """Calculate expected profit from grid trading."""
        try:
            # Simplified profit calculation based on grid spacing and levels
            grid_spacing_percent = config.grid_spacing_percentage
            num_levels = len(grid_levels)
            
            # Estimate profit based on volatility and grid spacing
            expected_profit = (grid_spacing_percent * num_levels * 0.3)  # Conservative estimate
            return min(expected_profit, 25.0)  # Cap at 25%
            
        except Exception:
            return 5.0  # Default conservative estimate
    
    async def _assess_grid_trading_risk(
        self,
        token_address: str,
        current_price: float,
        liquidity_usd: float,
        config: GridTradingConfig
    ) -> float:
        """Assess risk for grid trading strategy."""
        try:
            risk_score = 0.3  # Base risk for grid trading
            
            # Liquidity risk
            if liquidity_usd < 100000:
                risk_score += 0.2
            
            # Price volatility risk (estimated)
            if current_price < 0.001:  # Very low price tokens
                risk_score += 0.2
            
            return min(risk_score, 1.0)
            
        except Exception:
            return 0.6  # Default medium risk
    
    async def _calculate_grid_confidence(
        self,
        token_address: str,
        current_price: float,
        liquidity_usd: float,
        grid_levels: List[Dict]
    ) -> float:
        """Calculate confidence for grid trading opportunity."""
        try:
            confidence = 0.5  # Base confidence
            
            # Liquidity confidence
            if liquidity_usd > 500000:
                confidence += 0.2
            elif liquidity_usd > 100000:
                confidence += 0.1
            
            # Grid setup confidence
            if len(grid_levels) >= 10:
                confidence += 0.1
            
            # Price stability (estimated)
            confidence += 0.15
            
            return min(confidence, 0.95)
            
        except Exception:
            return 0.6
    
    async def _estimate_arbitrage_gas_cost(
        self,
        token_address: str,
        buy_dex: str,
        sell_dex: str,
        network: str
    ) -> float:
        """Estimate gas cost for arbitrage transaction."""
        try:
            # Simplified gas estimation
            base_gas_cost = 5.0 if network == "ethereum" else 0.5  # USD
            return base_gas_cost * 2  # Buy + Sell transactions
            
        except Exception:
            return 10.0  # Conservative estimate
    
    async def _calculate_arbitrage_position_size(
        self,
        price_difference: float,
        min_liquidity: float,
        gas_cost: float,
        strategy_config: StrategyConfiguration
    ) -> float:
        """Calculate optimal position size for arbitrage."""
        try:
            # Conservative position sizing
            max_size_by_liquidity = min_liquidity * 0.1  # Use 10% of available liquidity
            max_size_by_config = strategy_config.max_position_size
            
            # Ensure gas costs are covered
            min_size_for_profit = gas_cost * 20  # Minimum 5% net profit after gas
            
            return min(max_size_by_liquidity, max_size_by_config, min_size_for_profit)
            
        except Exception:
            return 500.0  # Default conservative size
    
    async def _assess_arbitrage_risk(
        self,
        token_address: str,
        buy_dex: str,
        sell_dex: str,
        price_difference: float
    ) -> float:
        """Assess risk for arbitrage opportunity."""
        try:
            # Arbitrage is generally low risk
            risk_score = 0.1
            
            # Higher price differences might indicate higher risk
            if price_difference > 5.0:
                risk_score += 0.1
            
            return min(risk_score, 0.5)
            
        except Exception:
            return 0.2
    
    async def _calculate_rsi(self, price_history: List[Dict], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        try:
            if len(price_history) < period + 1:
                return 50.0  # Neutral RSI
            
            prices = [p['price'] for p in price_history]
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            
            gains = [d if d > 0 else 0 for d in deltas[-period:]]
            losses = [-d if d < 0 else 0 for d in deltas[-period:]]
            
            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception:
            return 50.0
    
    async def _calculate_macd(self, price_history: List[Dict]) -> Tuple[float, float]:
        """Calculate MACD line and signal line."""
        try:
            if len(price_history) < 26:
                return 0.0, 0.0
            
            prices = [p['price'] for p in price_history]
            
            # EMA calculation
            ema_12 = np.mean(prices[-12:])  # Simplified
            ema_26 = np.mean(prices[-26:])  # Simplified
            
            macd_line = ema_12 - ema_26
            signal_line = macd_line * 0.9  # Simplified signal line
            
            return macd_line, signal_line
            
        except Exception:
            return 0.0, 0.0
    
    async def _assess_momentum_risk(
        self,
        price_change: float,
        volume_surge: float,
        rsi: float,
        current_price: float
    ) -> float:
        """Assess risk for momentum strategy."""
        try:
            risk_score = 0.4  # Base risk for momentum trading
            
            # Higher price changes = higher risk
            if abs(price_change) > 20:
                risk_score += 0.2
            
            # Extreme RSI values = higher risk
            if rsi > 80 or rsi < 20:
                risk_score += 0.1
            
            # Very low price tokens = higher risk
            if current_price < 0.001:
                risk_score += 0.2
            
            return min(risk_score, 1.0)
            
        except Exception:
            return 0.6
    
    async def _assess_mean_reversion_risk(
        self,
        z_score: float,
        volatility: float,
        deviation: float
    ) -> float:
        """Assess risk for mean reversion strategy."""
        try:
            risk_score = 0.3  # Base risk for mean reversion
            
            # Higher volatility = higher risk
            if volatility > 20:
                risk_score += 0.2
            
            # Extreme deviations might not revert
            if abs(z_score) > 3:
                risk_score += 0.1
            
            return min(risk_score, 0.8)
            
        except Exception:
            return 0.5
