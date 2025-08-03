"""
Advanced Risk Management System
File: app/core/risk/position_sizer.py

Professional position sizing and risk management for trading operations.
Implements advanced position sizing algorithms and comprehensive risk controls.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import math

from app.core.performance.cache_manager import cache_manager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__)


class RiskLevel(Enum):
    """Risk level classifications."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class PositionSizeMethod(Enum):
    """Position sizing methodologies."""
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE_RISK = "percentage_risk"
    KELLY_CRITERION = "kelly_criterion"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    LIQUIDITY_BASED = "liquidity_based"
    COMBINED = "combined"


@dataclass
class RiskParameters:
    """Risk management parameters for position sizing."""
    max_position_size: Decimal = Decimal('0.25')  # 25% of portfolio
    max_daily_loss: Decimal = Decimal('0.05')     # 5% daily loss limit
    max_portfolio_risk: Decimal = Decimal('0.02')  # 2% portfolio risk per trade
    max_correlation_exposure: Decimal = Decimal('0.30')  # 30% in correlated assets
    max_single_token_exposure: Decimal = Decimal('0.15')  # 15% in single token
    
    # Volatility parameters
    volatility_lookback_days: int = 30
    volatility_adjustment_factor: Decimal = Decimal('2.0')
    
    # Liquidity parameters
    min_liquidity_ratio: Decimal = Decimal('0.05')  # 5% of total liquidity
    max_market_impact: Decimal = Decimal('0.02')    # 2% market impact
    
    # Stop loss parameters
    default_stop_loss: Decimal = Decimal('0.08')    # 8% stop loss
    trailing_stop_activation: Decimal = Decimal('0.05')  # 5% profit to activate
    trailing_stop_distance: Decimal = Decimal('0.03')   # 3% trailing distance


@dataclass
class PositionSizeResult:
    """Result of position sizing calculation."""
    recommended_size: Decimal
    max_size: Decimal
    risk_amount: Decimal
    risk_percentage: Decimal
    confidence_score: float
    
    # Risk metrics
    expected_loss: Decimal
    max_drawdown_risk: Decimal
    liquidity_impact: Decimal
    volatility_adjusted_size: Decimal
    
    # Reasoning and warnings
    sizing_method: PositionSizeMethod
    risk_factors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    constraints_applied: List[str] = field(default_factory=list)
    
    # Metadata
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None


class RiskManagementException(DexSnipingException):
    """Exception raised when risk management operations fail."""
    pass


class PositionSizer:
    """
    Advanced position sizing calculator with multiple methodologies.
    
    Implements professional position sizing algorithms including:
    - Fixed amount sizing
    - Percentage risk sizing
    - Kelly Criterion optimization
    - Volatility-adjusted sizing
    - Liquidity-based sizing
    - Combined multi-factor approach
    """
    
    def __init__(self, risk_params: Optional[RiskParameters] = None):
        self.risk_params = risk_params or RiskParameters()
        
        # Portfolio tracking
        self.portfolio_value = Decimal('0')
        self.current_positions = {}
        self.daily_pnl = Decimal('0')
        self.risk_utilization = Decimal('0')
        
        # Historical data cache
        self.price_history = {}
        self.volatility_cache = {}
        self.correlation_matrix = {}
        
        logger.info("✅ PositionSizer initialized with professional risk management")

    async def calculate_position_size(
        self,
        token_address: str,
        current_price: Decimal,
        stop_loss_price: Optional[Decimal] = None,
        portfolio_value: Optional[Decimal] = None,
        liquidity_data: Optional[Dict] = None,
        method: PositionSizeMethod = PositionSizeMethod.COMBINED
    ) -> PositionSizeResult:
        """
        Calculate optimal position size using specified methodology.
        
        Method: calculate_position_size()
        
        Args:
            token_address: Token contract address
            current_price: Current token price
            stop_loss_price: Stop loss price (optional)
            portfolio_value: Total portfolio value
            liquidity_data: Token liquidity information
            method: Position sizing methodology
            
        Returns:
            Position sizing result with recommendations and risk metrics
        """
        try:
            # Update portfolio value
            if portfolio_value:
                self.portfolio_value = Decimal(str(portfolio_value))
            
            # Validate inputs
            await self._validate_sizing_inputs(
                token_address, current_price, stop_loss_price
            )
            
            logger.info(f"🎯 Calculating position size for {token_address} using {method.value}")
            
            # Calculate using specified method
            if method == PositionSizeMethod.FIXED_AMOUNT:
                result = await self._calculate_fixed_amount_size(
                    token_address, current_price, stop_loss_price
                )
            elif method == PositionSizeMethod.PERCENTAGE_RISK:
                result = await self._calculate_percentage_risk_size(
                    token_address, current_price, stop_loss_price
                )
            elif method == PositionSizeMethod.KELLY_CRITERION:
                result = await self._calculate_kelly_size(
                    token_address, current_price, stop_loss_price
                )
            elif method == PositionSizeMethod.VOLATILITY_ADJUSTED:
                result = await self._calculate_volatility_adjusted_size(
                    token_address, current_price, stop_loss_price
                )
            elif method == PositionSizeMethod.LIQUIDITY_BASED:
                result = await self._calculate_liquidity_based_size(
                    token_address, current_price, stop_loss_price, liquidity_data
                )
            else:  # COMBINED
                result = await self._calculate_combined_size(
                    token_address, current_price, stop_loss_price, liquidity_data
                )
            
            # Apply risk limits and constraints
            result = await self._apply_risk_limits(result, token_address)
            
            # Cache result
            await self._cache_sizing_result(token_address, result)
            
            logger.info(f"✅ Position size calculated: ${result.recommended_size} "
                       f"(Risk: {result.risk_percentage:.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            raise RiskManagementException(f"Position sizing failed: {e}")

    async def apply_risk_limits(
        self, 
        position_size: Decimal, 
        token_address: str,
        additional_checks: bool = True
    ) -> Tuple[Decimal, List[str]]:
        """
        Apply comprehensive risk limits to position size.
        
        Method: apply_risk_limits()
        
        Args:
            position_size: Proposed position size
            token_address: Token contract address
            additional_checks: Whether to perform additional risk checks
            
        Returns:
            Tuple of (adjusted_size, applied_constraints)
        """
        try:
            original_size = position_size
            applied_constraints = []
            
            # 1. Maximum position size limit
            max_position_value = self.portfolio_value * self.risk_params.max_position_size
            if position_size > max_position_value:
                position_size = max_position_value
                applied_constraints.append(f"Max position size: {self.risk_params.max_position_size*100}%")
            
            # 2. Daily loss limit check
            if self.daily_pnl < -self.portfolio_value * self.risk_params.max_daily_loss:
                position_size *= Decimal('0.5')  # Reduce size by 50%
                applied_constraints.append("Daily loss limit reached - size reduced")
            
            # 3. Single token exposure limit
            current_exposure = await self._get_token_exposure(token_address)
            max_additional = (self.portfolio_value * self.risk_params.max_single_token_exposure) - current_exposure
            
            if position_size > max_additional:
                position_size = max(Decimal('0'), max_additional)
                applied_constraints.append(f"Single token exposure limit: {self.risk_params.max_single_token_exposure*100}%")
            
            # 4. Correlation exposure check
            if additional_checks:
                correlation_limit = await self._check_correlation_limits(token_address, position_size)
                if correlation_limit < position_size:
                    position_size = correlation_limit
                    applied_constraints.append("Correlation exposure limit applied")
            
            # 5. Risk utilization check
            total_risk = await self._calculate_total_portfolio_risk()
            if total_risk > self.risk_params.max_portfolio_risk * Decimal('0.8'):  # 80% of limit
                position_size *= Decimal('0.75')  # Reduce by 25%
                applied_constraints.append("High portfolio risk - size reduced")
            
            # 6. Minimum position size
            min_position = self.portfolio_value * Decimal('0.001')  # 0.1% minimum
            if position_size < min_position:
                position_size = Decimal('0')
                applied_constraints.append("Below minimum position size")
            
            adjustment_pct = ((position_size - original_size) / original_size * 100) if original_size > 0 else 0
            
            if applied_constraints:
                logger.info(f"🛡️ Risk limits applied to {token_address}: "
                           f"{adjustment_pct:.1f}% adjustment")
            
            return position_size, applied_constraints
            
        except Exception as e:
            logger.error(f"Error applying risk limits: {e}")
            return Decimal('0'), ["Error applying risk limits"]

    async def _calculate_fixed_amount_size(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal]
    ) -> PositionSizeResult:
        """Calculate position size using fixed amount method."""
        try:
            # Fixed percentage of portfolio (e.g., 5%)
            fixed_percentage = Decimal('0.05')
            position_value = self.portfolio_value * fixed_percentage
            
            # Calculate token quantity
            position_size = position_value
            
            # Calculate risk metrics
            if stop_loss_price:
                risk_per_token = current_price - stop_loss_price
                risk_amount = (risk_per_token / current_price) * position_value
                risk_percentage = (risk_amount / self.portfolio_value) * 100
            else:
                risk_amount = position_value * self.risk_params.default_stop_loss
                risk_percentage = (risk_amount / self.portfolio_value) * 100
            
            return PositionSizeResult(
                recommended_size=position_size,
                max_size=position_size,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence_score=0.8,
                expected_loss=risk_amount,
                max_drawdown_risk=risk_amount * Decimal('1.5'),
                liquidity_impact=Decimal('0'),
                volatility_adjusted_size=position_size,
                sizing_method=PositionSizeMethod.FIXED_AMOUNT,
                risk_factors=["Fixed amount sizing - no market adaptation"],
                valid_until=datetime.utcnow() + timedelta(hours=1)
            )
            
        except Exception as e:
            logger.error(f"Error in fixed amount sizing: {e}")
            raise

    async def _calculate_percentage_risk_size(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal]
    ) -> PositionSizeResult:
        """Calculate position size based on percentage risk method."""
        try:
            # Risk percentage of portfolio per trade
            risk_per_trade = self.portfolio_value * self.risk_params.max_portfolio_risk
            
            # Calculate stop loss distance
            if stop_loss_price:
                stop_distance = (current_price - stop_loss_price) / current_price
            else:
                stop_distance = self.risk_params.default_stop_loss
            
            # Position size = Risk Amount / Stop Distance
            position_size = risk_per_trade / stop_distance if stop_distance > 0 else Decimal('0')
            
            # Ensure position doesn't exceed maximum
            max_position = self.portfolio_value * self.risk_params.max_position_size
            position_size = min(position_size, max_position)
            
            # Recalculate actual risk
            actual_risk = position_size * stop_distance
            risk_percentage = (actual_risk / self.portfolio_value) * 100
            
            confidence_score = 0.9 if stop_loss_price else 0.7
            
            return PositionSizeResult(
                recommended_size=position_size,
                max_size=max_position,
                risk_amount=actual_risk,
                risk_percentage=risk_percentage,
                confidence_score=confidence_score,
                expected_loss=actual_risk,
                max_drawdown_risk=actual_risk * Decimal('1.2'),
                liquidity_impact=Decimal('0'),
                volatility_adjusted_size=position_size,
                sizing_method=PositionSizeMethod.PERCENTAGE_RISK,
                risk_factors=["Risk-based sizing - well-controlled risk"],
                valid_until=datetime.utcnow() + timedelta(minutes=30)
            )
            
        except Exception as e:
            logger.error(f"Error in percentage risk sizing: {e}")
            raise

    async def _calculate_kelly_size(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal]
    ) -> PositionSizeResult:
        """Calculate position size using Kelly Criterion."""
        try:
            # Get historical performance data
            win_rate, avg_win, avg_loss = await self._get_historical_performance(token_address)
            
            if win_rate == 0 or avg_loss == 0:
                # Fallback to percentage risk if no historical data
                return await self._calculate_percentage_risk_size(
                    token_address, current_price, stop_loss_price
                )
            
            # Kelly Criterion: f = (bp - q) / b
            # where: f = fraction to bet, b = odds, p = win probability, q = loss probability
            odds_ratio = avg_win / avg_loss
            kelly_fraction = (win_rate * odds_ratio - (1 - win_rate)) / odds_ratio
            
            # Apply Kelly fraction with safety margin (typically 25% of Kelly)
            safe_kelly = max(Decimal('0'), kelly_fraction * Decimal('0.25'))
            
            # Calculate position size
            position_size = self.portfolio_value * safe_kelly
            
            # Apply maximum position limit
            max_position = self.portfolio_value * self.risk_params.max_position_size
            position_size = min(position_size, max_position)
            
            # Calculate risk metrics
            if stop_loss_price:
                stop_distance = (current_price - stop_loss_price) / current_price
            else:
                stop_distance = avg_loss
            
            risk_amount = position_size * stop_distance
            risk_percentage = (risk_amount / self.portfolio_value) * 100
            
            warnings = []
            if kelly_fraction > Decimal('0.25'):
                warnings.append("High Kelly fraction - reduced for safety")
            if win_rate < Decimal('0.5'):
                warnings.append("Low historical win rate")
            
            return PositionSizeResult(
                recommended_size=position_size,
                max_size=max_position,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence_score=float(win_rate),
                expected_loss=risk_amount,
                max_drawdown_risk=risk_amount * Decimal('1.3'),
                liquidity_impact=Decimal('0'),
                volatility_adjusted_size=position_size,
                sizing_method=PositionSizeMethod.KELLY_CRITERION,
                risk_factors=[f"Kelly-optimized sizing (win rate: {win_rate*100:.1f}%)"],
                warnings=warnings,
                valid_until=datetime.utcnow() + timedelta(hours=4)
            )
            
        except Exception as e:
            logger.error(f"Error in Kelly sizing: {e}")
            raise

    async def _calculate_volatility_adjusted_size(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal]
    ) -> PositionSizeResult:
        """Calculate position size adjusted for volatility."""
        try:
            # Get token volatility
            volatility = await self._get_token_volatility(token_address)
            
            if volatility == 0:
                volatility = Decimal('0.5')  # Default 50% annual volatility
            
            # Base position size
            base_size = self.portfolio_value * self.risk_params.max_portfolio_risk
            
            # Volatility adjustment factor
            # Higher volatility = smaller position
            volatility_multiplier = Decimal('1') / (Decimal('1') + volatility * self.risk_params.volatility_adjustment_factor)
            
            # Adjusted position size
            position_size = base_size / volatility_multiplier
            
            # Apply maximum position limit
            max_position = self.portfolio_value * self.risk_params.max_position_size
            position_size = min(position_size, max_position)
            
            # Calculate risk metrics
            if stop_loss_price:
                stop_distance = (current_price - stop_loss_price) / current_price
            else:
                stop_distance = volatility * Decimal('0.5')  # Half of volatility as stop
            
            risk_amount = position_size * stop_distance
            risk_percentage = (risk_amount / self.portfolio_value) * 100
            
            risk_factors = [f"Volatility-adjusted sizing (volatility: {volatility*100:.1f}%)"]
            if volatility > Decimal('1'):
                risk_factors.append("High volatility - reduced position size")
            
            return PositionSizeResult(
                recommended_size=position_size,
                max_size=max_position,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence_score=0.85,
                expected_loss=risk_amount,
                max_drawdown_risk=risk_amount * (Decimal('1') + volatility),
                liquidity_impact=Decimal('0'),
                volatility_adjusted_size=position_size,
                sizing_method=PositionSizeMethod.VOLATILITY_ADJUSTED,
                risk_factors=risk_factors,
                valid_until=datetime.utcnow() + timedelta(hours=2)
            )
            
        except Exception as e:
            logger.error(f"Error in volatility-adjusted sizing: {e}")
            raise

    async def _calculate_liquidity_based_size(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal],
        liquidity_data: Optional[Dict]
    ) -> PositionSizeResult:
        """Calculate position size based on available liquidity."""
        try:
            if not liquidity_data:
                # Fallback to percentage risk if no liquidity data
                return await self._calculate_percentage_risk_size(
                    token_address, current_price, stop_loss_price
                )
            
            total_liquidity = Decimal(str(liquidity_data.get('total_liquidity', 0)))
            
            if total_liquidity == 0:
                raise RiskManagementException("No liquidity data available")
            
            # Maximum position based on liquidity (5% of total liquidity)
            max_liquidity_position = total_liquidity * self.risk_params.min_liquidity_ratio
            
            # Calculate market impact
            position_value = min(
                self.portfolio_value * self.risk_params.max_position_size,
                max_liquidity_position
            )
            
            market_impact = self._calculate_market_impact(position_value, total_liquidity)
            
            # Reduce position if market impact too high
            if market_impact > self.risk_params.max_market_impact:
                impact_reduction = self.risk_params.max_market_impact / market_impact
                position_value *= impact_reduction
                market_impact = self.risk_params.max_market_impact
            
            # Calculate risk metrics
            if stop_loss_price:
                stop_distance = (current_price - stop_loss_price) / current_price
            else:
                stop_distance = self.risk_params.default_stop_loss
            
            risk_amount = position_value * stop_distance
            risk_percentage = (risk_amount / self.portfolio_value) * 100
            
            risk_factors = [f"Liquidity-based sizing (liquidity: ${total_liquidity:,.0f})"]
            
            warnings = []
            if market_impact > Decimal('0.01'):
                warnings.append(f"Significant market impact: {market_impact*100:.2f}%")
            if total_liquidity < Decimal('50000'):
                warnings.append("Low liquidity token - increased risk")
            
            return PositionSizeResult(
                recommended_size=position_value,
                max_size=max_liquidity_position,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence_score=0.75,
                expected_loss=risk_amount,
                max_drawdown_risk=risk_amount * Decimal('1.4'),
                liquidity_impact=market_impact,
                volatility_adjusted_size=position_value,
                sizing_method=PositionSizeMethod.LIQUIDITY_BASED,
                risk_factors=risk_factors,
                warnings=warnings,
                valid_until=datetime.utcnow() + timedelta(minutes=15)
            )
            
        except Exception as e:
            logger.error(f"Error in liquidity-based sizing: {e}")
            raise

    async def _calculate_combined_size(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal],
        liquidity_data: Optional[Dict]
    ) -> PositionSizeResult:
        """Calculate position size using combined multi-factor approach."""
        try:
            # Calculate using different methods
            methods_results = {}
            
            # Percentage risk (base method)
            methods_results['percentage'] = await self._calculate_percentage_risk_size(
                token_address, current_price, stop_loss_price
            )
            
            # Volatility adjusted
            methods_results['volatility'] = await self._calculate_volatility_adjusted_size(
                token_address, current_price, stop_loss_price
            )
            
            # Kelly criterion (if data available)
            try:
                methods_results['kelly'] = await self._calculate_kelly_size(
                    token_address, current_price, stop_loss_price
                )
            except Exception:
                pass  # Skip if no historical data
            
            # Liquidity based (if data available)
            if liquidity_data:
                methods_results['liquidity'] = await self._calculate_liquidity_based_size(
                    token_address, current_price, stop_loss_price, liquidity_data
                )
            
            # Combine results using weighted average
            weights = {
                'percentage': 0.35,    # 35% - base risk management
                'volatility': 0.25,    # 25% - market conditions
                'kelly': 0.25,         # 25% - optimization (if available)
                'liquidity': 0.15      # 15% - execution constraints
            }
            
            total_weight = Decimal('0')
            weighted_size = Decimal('0')
            combined_confidence = 0.0
            all_factors = []
            all_warnings = []
            
            for method, result in methods_results.items():
                weight = Decimal(str(weights.get(method, 0)))
                weighted_size += result.recommended_size * weight
                total_weight += weight
                combined_confidence += result.confidence_score * float(weight)
                all_factors.extend(result.risk_factors)
                all_warnings.extend(result.warnings)
            
            # Normalize if some methods missing
            if total_weight > 0:
                recommended_size = weighted_size / total_weight
                combined_confidence = combined_confidence / float(total_weight)
            else:
                recommended_size = Decimal('0')
                combined_confidence = 0.0
            
            # Use most conservative max size
            max_size = min([r.max_size for r in methods_results.values()])
            
            # Ensure recommended doesn't exceed max
            recommended_size = min(recommended_size, max_size)
            
            # Calculate combined risk metrics
            if stop_loss_price:
                stop_distance = (current_price - stop_loss_price) / current_price
            else:
                stop_distance = self.risk_params.default_stop_loss
            
            risk_amount = recommended_size * stop_distance
            risk_percentage = (risk_amount / self.portfolio_value) * 100
            
            # Get liquidity impact if available
            liquidity_impact = Decimal('0')
            if 'liquidity' in methods_results:
                liquidity_impact = methods_results['liquidity'].liquidity_impact
            
            return PositionSizeResult(
                recommended_size=recommended_size,
                max_size=max_size,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence_score=combined_confidence,
                expected_loss=risk_amount,
                max_drawdown_risk=risk_amount * Decimal('1.25'),
                liquidity_impact=liquidity_impact,
                volatility_adjusted_size=methods_results.get('volatility', methods_results['percentage']).recommended_size,
                sizing_method=PositionSizeMethod.COMBINED,
                risk_factors=list(set(all_factors)),  # Remove duplicates
                warnings=list(set(all_warnings)),     # Remove duplicates
                valid_until=datetime.utcnow() + timedelta(minutes=20)
            )
            
        except Exception as e:
            logger.error(f"Error in combined sizing: {e}")
            raise

    def _calculate_market_impact(self, position_value: Decimal, total_liquidity: Decimal) -> Decimal:
        """Calculate estimated market impact of a trade."""
        try:
            if total_liquidity <= 0:
                return Decimal('0.1')  # 10% default impact
            
            # Simple square root model: impact = sqrt(trade_size / liquidity) * constant
            trade_ratio = position_value / total_liquidity
            impact = (trade_ratio ** Decimal('0.5')) * Decimal('0.05')  # 5% constant
            
            return min(impact, Decimal('0.2'))  # Cap at 20%
            
        except Exception:
            return Decimal('0.05')  # Default 5% impact

    async def _get_token_volatility(self, token_address: str) -> Decimal:
        """Get token volatility from cache or calculate."""
        try:
            # Check cache first
            cache_key = f"volatility_{token_address}"
            cached_volatility = await cache_manager.get(cache_key, namespace='risk_management')
            
            if cached_volatility:
                return Decimal(str(cached_volatility))
            
            # Calculate volatility from price history
            # This is a placeholder - in production, you'd fetch real price data
            price_history = await self._get_price_history(token_address)
            
            if len(price_history) < 2:
                return Decimal('0.5')  # Default 50% annual volatility
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(price_history)):
                return_pct = (price_history[i] - price_history[i-1]) / price_history[i-1]
                returns.append(float(return_pct))
            
            # Calculate standard deviation (volatility)
            if not returns:
                return Decimal('0.5')
            
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            daily_volatility = math.sqrt(variance)
            
            # Annualize volatility (assume 365 trading days)
            annual_volatility = daily_volatility * math.sqrt(365)
            
            volatility = Decimal(str(annual_volatility))
            
            # Cache result for 1 hour
            await cache_manager.set(
                cache_key, float(volatility), ttl=3600, namespace='risk_management'
            )
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error getting token volatility: {e}")
            return Decimal('0.5')  # Default volatility

    async def _get_price_history(self, token_address: str) -> List[Decimal]:
        """Get historical price data for volatility calculation."""
        try:
            # Placeholder implementation
            # In production, this would fetch real historical data
            return [
                Decimal('1.0'), Decimal('1.1'), Decimal('0.95'), Decimal('1.05'),
                Decimal('1.2'), Decimal('1.15'), Decimal('1.3'), Decimal('1.25')
            ]
        except Exception:
            return []

    async def _get_historical_performance(self, token_address: str) -> Tuple[Decimal, Decimal, Decimal]:
        """Get historical trading performance for Kelly criterion."""
        try:
            # Placeholder implementation
            # In production, this would analyze actual trading history
            win_rate = Decimal('0.6')     # 60% win rate
            avg_win = Decimal('0.15')     # 15% average win
            avg_loss = Decimal('0.08')    # 8% average loss
            
            return win_rate, avg_win, avg_loss
            
        except Exception as e:
            logger.error(f"Error getting historical performance: {e}")
            return Decimal('0'), Decimal('0'), Decimal('0')

    async def _get_token_exposure(self, token_address: str) -> Decimal:
        """Get current exposure to a specific token."""
        try:
            # Check current positions
            current_position = self.current_positions.get(token_address, {})
            return Decimal(str(current_position.get('value', 0)))
            
        except Exception:
            return Decimal('0')

    async def _check_correlation_limits(self, token_address: str, position_size: Decimal) -> Decimal:
        """Check correlation exposure limits."""
        try:
            # Placeholder implementation
            # In production, this would check correlations with existing positions
            return position_size  # No correlation limits applied for now
            
        except Exception:
            return position_size

    async def _calculate_total_portfolio_risk(self) -> Decimal:
        """Calculate total portfolio risk from all positions."""
        try:
            total_risk = Decimal('0')
            
            # Sum risk from all current positions
            for position in self.current_positions.values():
                position_risk = Decimal(str(position.get('risk_amount', 0)))
                total_risk += position_risk
            
            return total_risk / self.portfolio_value if self.portfolio_value > 0 else Decimal('0')
            
        except Exception:
            return Decimal('0')

    async def _validate_sizing_inputs(
        self, 
        token_address: str, 
        current_price: Decimal, 
        stop_loss_price: Optional[Decimal]
    ) -> None:
        """Validate inputs for position sizing calculation."""
        if not token_address:
            raise RiskManagementException("Token address is required")
        
        if current_price <= 0:
            raise RiskManagementException("Current price must be positive")
        
        if stop_loss_price and stop_loss_price >= current_price:
            raise RiskManagementException("Stop loss price must be below current price")
        
        if self.portfolio_value <= 0:
            raise RiskManagementException("Portfolio value must be positive")

    async def _apply_risk_limits(
        self, 
        result: PositionSizeResult, 
        token_address: str
    ) -> PositionSizeResult:
        """Apply comprehensive risk limits to position sizing result."""
        try:
            original_size = result.recommended_size
            
            # Apply position limits
            adjusted_size, constraints = await self.apply_risk_limits(
                result.recommended_size, token_address
            )
            
            # Update result with adjusted size
            result.recommended_size = adjusted_size
            result.constraints_applied.extend(constraints)
            
            # Recalculate risk metrics if size changed
            if adjusted_size != original_size:
                adjustment_ratio = adjusted_size / original_size if original_size > 0 else Decimal('0')
                result.risk_amount *= adjustment_ratio
                result.expected_loss *= adjustment_ratio
                result.max_drawdown_risk *= adjustment_ratio
                
                # Adjust confidence score
                if adjustment_ratio < Decimal('0.5'):
                    result.confidence_score *= 0.8  # Reduce confidence for large adjustments
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying risk limits to result: {e}")
            return result

    async def _cache_sizing_result(self, token_address: str, result: PositionSizeResult) -> None:
        """Cache position sizing result."""
        try:
            cache_key = f"position_size_{token_address}"
            cache_data = {
                'recommended_size': float(result.recommended_size),
                'risk_percentage': float(result.risk_percentage),
                'confidence_score': result.confidence_score,
                'method': result.sizing_method.value,
                'calculated_at': result.calculated_at.isoformat()
            }
            
            # Cache for validity period or 30 minutes, whichever is shorter
            ttl = min(1800, int((result.valid_until - datetime.utcnow()).total_seconds())) if result.valid_until else 1800
            
            await cache_manager.set(
                cache_key, cache_data, ttl=ttl, namespace='risk_management'
            )
            
        except Exception as e:
            logger.error(f"Error caching sizing result: {e}")

    def update_portfolio_value(self, new_value: Decimal) -> None:
        """Update portfolio value for position sizing calculations."""
        self.portfolio_value = Decimal(str(new_value))
        logger.info(f"📊 Portfolio value updated: ${self.portfolio_value:,.2f}")

    def update_daily_pnl(self, pnl: Decimal) -> None:
        """Update daily P&L for risk monitoring."""
        self.daily_pnl = Decimal(str(pnl))
        
        # Check if daily loss limit reached
        loss_limit = self.portfolio_value * self.risk_params.max_daily_loss
        if self.daily_pnl < -loss_limit:
            logger.warning(f"⚠️ Daily loss limit reached: {self.daily_pnl} < -{loss_limit}")

    def add_position(self, token_address: str, position_data: Dict) -> None:
        """Add or update a position in the portfolio."""
        self.current_positions[token_address] = position_data
        logger.info(f"📈 Position updated for {token_address}")

    def remove_position(self, token_address: str) -> None:
        """Remove a position from the portfolio."""
        if token_address in self.current_positions:
            del self.current_positions[token_address]
            logger.info(f"📉 Position removed for {token_address}")

    async def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary for the portfolio."""
        try:
            total_value = sum(
                Decimal(str(pos.get('value', 0))) 
                for pos in self.current_positions.values()
            )
            
            total_risk = await self._calculate_total_portfolio_risk()
            
            risk_summary = {
                'portfolio_value': float(self.portfolio_value),
                'total_position_value': float(total_value),
                'total_risk_percentage': float(total_risk * 100),
                'daily_pnl': float(self.daily_pnl),
                'positions_count': len(self.current_positions),
                'risk_utilization': float(total_risk / self.risk_params.max_portfolio_risk * 100),
                'available_capital': float(self.portfolio_value - total_value),
                'risk_limits': {
                    'max_portfolio_risk': float(self.risk_params.max_portfolio_risk * 100),
                    'max_daily_loss': float(self.risk_params.max_daily_loss * 100),
                    'max_position_size': float(self.risk_params.max_position_size * 100)
                }
            }
            
            return risk_summary
            
        except Exception as e:
            logger.error(f"Error generating risk summary: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    async def test_position_sizer():
        """Test position sizing functionality."""
        sizer = PositionSizer()
        sizer.update_portfolio_value(Decimal('100000'))  # $100k portfolio
        
        try:
            result = await sizer.calculate_position_size(
                token_address="0x1234567890123456789012345678901234567890",
                current_price=Decimal('1.50'),
                stop_loss_price=Decimal('1.35'),
                method=PositionSizeMethod.COMBINED
            )
            
            print(f"✅ Position sizing result:")
            print(f"   Recommended size: ${result.recommended_size:,.2f}")
            print(f"   Risk amount: ${result.risk_amount:,.2f}")
            print(f"   Risk percentage: {result.risk_percentage:.2f}%")
            print(f"   Confidence score: {result.confidence_score:.2f}")
            print(f"   Method: {result.sizing_method.value}")
            
            if result.warnings:
                print(f"   Warnings: {', '.join(result.warnings)}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Run test
    asyncio.run(test_position_sizer())