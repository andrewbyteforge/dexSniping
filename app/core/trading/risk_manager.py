"""
Risk Management System
File: app/core/trading/risk_manager.py

Comprehensive risk management system with advanced position sizing,
portfolio risk controls, and automated risk monitoring.
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

from app.utils.logger import setup_logger
from app.models.dex.trading_models import (
    TradingPosition, TradingOrder, RiskLimit, PortfolioTransaction,
    OrderSide, OrderType, OrderStatus, PositionStatus, TransactionType
)

logger = setup_logger(__name__)


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PositionSizeMethod(str, Enum):
    """Position sizing method enumeration."""
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE_RISK = "percentage_risk"
    KELLY_CRITERION = "kelly_criterion"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    EQUAL_WEIGHT = "equal_weight"


@dataclass
class RiskMetrics:
    """Risk metrics data structure."""
    portfolio_value: Decimal
    max_position_size: Decimal
    current_exposure: Decimal
    available_capital: Decimal
    risk_score: float
    drawdown_percentage: float
    daily_pnl: Decimal
    open_positions_count: int
    concentration_risk: float
    liquidity_score: float


@dataclass
class PositionSizeResult:
    """Position size calculation result."""
    recommended_size: Decimal
    max_size: Decimal
    risk_adjusted_size: Decimal
    confidence_score: float
    risk_warnings: List[str]
    sizing_method: PositionSizeMethod
    position_percentage: float


@dataclass
class RiskAssessmentResult:
    """Risk assessment result."""
    risk_level: RiskLevel
    risk_score: float
    can_trade: bool
    warnings: List[str]
    recommendations: List[str]
    risk_metrics: RiskMetrics


class RiskManager:
    """
    Advanced risk management system with comprehensive portfolio protection.
    """
    
    def __init__(self, session_factory=None):
        """Initialize risk manager."""
        self.session_factory = session_factory
        self.logger = setup_logger(f"{__name__}.RiskManager")
        
        # Default risk parameters
        self.default_params = {
            'max_position_percentage': Decimal('10.0'),  # 10% of portfolio
            'max_daily_loss_percentage': Decimal('5.0'),  # 5% daily loss limit
            'max_drawdown_percentage': Decimal('20.0'),  # 20% max drawdown
            'min_liquidity_usd': Decimal('10000'),  # $10k minimum liquidity
            'max_risk_score': Decimal('7.0'),  # Maximum risk score 0-10
            'max_open_positions': 20,
            'max_slippage': Decimal('0.05'),  # 5% max slippage
            'kelly_fraction': Decimal('0.25'),  # Conservative Kelly fraction
            'volatility_multiplier': Decimal('2.0'),  # Volatility adjustment factor
        }
    
    async def assess_portfolio_risk(
        self,
        user_wallet: str,
        session=None
    ) -> RiskAssessmentResult:
        """
        Comprehensive portfolio risk assessment.
        
        Args:
            user_wallet: User wallet address
            session: Database session
            
        Returns:
            RiskAssessmentResult with comprehensive risk analysis
        """
        try:
            self.logger.info(f"🔍 Assessing portfolio risk for {user_wallet[:10]}...")
            
            if not session:
                async with self.session_factory() as session:
                    return await self._assess_portfolio_risk_internal(user_wallet, session)
            else:
                return await self._assess_portfolio_risk_internal(user_wallet, session)
                
        except Exception as e:
            self.logger.error(f"❌ Portfolio risk assessment failed: {e}")
            raise Exception(f"Risk assessment failed: {e}")
    
    async def _assess_portfolio_risk_internal(
        self,
        user_wallet: str,
        session
    ) -> RiskAssessmentResult:
        """Internal portfolio risk assessment implementation."""
        warnings = []
        recommendations = []
        
        # Get user risk limits
        risk_limits = await self._get_user_risk_limits(user_wallet, session)
        
        # Get portfolio metrics
        risk_metrics = await self._calculate_risk_metrics(user_wallet, session)
        
        # Calculate overall risk score
        risk_score = await self._calculate_risk_score(risk_metrics, risk_limits)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Check trading eligibility
        can_trade, trade_warnings = await self._check_trading_eligibility(
            user_wallet, risk_metrics, risk_limits, session
        )
        
        warnings.extend(trade_warnings)
        
        # Generate recommendations
        recommendations.extend(
            await self._generate_risk_recommendations(risk_metrics, risk_limits)
        )
        
        # Risk level specific warnings
        if risk_level == RiskLevel.HIGH:
            warnings.append("Portfolio risk is HIGH - Consider reducing position sizes")
        elif risk_level == RiskLevel.CRITICAL:
            warnings.append("Portfolio risk is CRITICAL - Immediate risk reduction recommended")
            recommendations.append("Close some positions to reduce exposure")
            recommendations.append("Implement stricter stop-loss orders")
        
        return RiskAssessmentResult(
            risk_level=risk_level,
            risk_score=risk_score,
            can_trade=can_trade,
            warnings=warnings,
            recommendations=recommendations,
            risk_metrics=risk_metrics
        )
    
    async def calculate_position_size(
        self,
        user_wallet: str,
        token_address: str,
        side: OrderSide,
        entry_price: Decimal,
        stop_loss_price: Optional[Decimal] = None,
        method: PositionSizeMethod = PositionSizeMethod.PERCENTAGE_RISK,
        session=None
    ) -> PositionSizeResult:
        """
        Calculate optimal position size using various methods.
        
        Args:
            user_wallet: User wallet address
            token_address: Token contract address
            side: Order side (buy/sell)
            entry_price: Expected entry price
            stop_loss_price: Stop loss price (optional)
            method: Position sizing method
            session: Database session
            
        Returns:
            PositionSizeResult with optimal position size
        """
        try:
            self.logger.info(f"📊 Calculating position size using {method.value}")
            
            if not session:
                async with self.session_factory() as session:
                    return await self._calculate_position_size_internal(
                        user_wallet, token_address, side, entry_price,
                        stop_loss_price, method, session
                    )
            else:
                return await self._calculate_position_size_internal(
                    user_wallet, token_address, side, entry_price,
                    stop_loss_price, method, session
                )
                
        except Exception as e:
            self.logger.error(f"❌ Position size calculation failed: {e}")
            raise Exception(f"Position size calculation failed: {e}")
    
    async def _calculate_position_size_internal(
        self,
        user_wallet: str,
        token_address: str,
        side: OrderSide,
        entry_price: Decimal,
        stop_loss_price: Optional[Decimal],
        method: PositionSizeMethod,
        session
    ) -> PositionSizeResult:
        """Internal position size calculation implementation."""
        warnings = []
        
        # Get portfolio metrics
        risk_metrics = await self._calculate_risk_metrics(user_wallet, session)
        risk_limits = await self._get_user_risk_limits(user_wallet, session)
        
        # Calculate base position size using selected method
        if method == PositionSizeMethod.FIXED_AMOUNT:
            base_size = await self._calculate_fixed_amount_size(risk_limits)
        elif method == PositionSizeMethod.PERCENTAGE_RISK:
            base_size = await self._calculate_percentage_risk_size(
                risk_metrics, entry_price, stop_loss_price, risk_limits
            )
        elif method == PositionSizeMethod.KELLY_CRITERION:
            base_size = await self._calculate_kelly_criterion_size(
                user_wallet, token_address, risk_metrics, session
            )
        elif method == PositionSizeMethod.VOLATILITY_ADJUSTED:
            base_size = await self._calculate_volatility_adjusted_size(
                token_address, risk_metrics, entry_price
            )
        elif method == PositionSizeMethod.EQUAL_WEIGHT:
            base_size = await self._calculate_equal_weight_size(risk_metrics, risk_limits)
        else:
            raise ValueError(f"Unknown position sizing method: {method}")
        
        # Apply risk adjustments
        risk_adjusted_size = await self._apply_risk_adjustments(
            base_size, risk_metrics, risk_limits, token_address
        )
        
        # Calculate maximum allowed size
        max_size = await self._calculate_max_position_size(
            risk_metrics, risk_limits, token_address
        )
        
        # Final recommended size (minimum of calculated and max allowed)
        recommended_size = min(risk_adjusted_size, max_size)
        
        # Calculate position percentage
        position_percentage = float(
            recommended_size / risk_metrics.portfolio_value * 100
        ) if risk_metrics.portfolio_value > 0 else 0
        
        # Calculate confidence score
        confidence_score = await self._calculate_confidence_score(
            recommended_size, base_size, risk_metrics, token_address
        )
        
        # Generate warnings
        if recommended_size < base_size:
            warnings.append("Position size reduced due to risk constraints")
        if position_percentage > 5:
            warnings.append(f"Large position size ({position_percentage:.1f}% of portfolio)")
        if not stop_loss_price and method == PositionSizeMethod.PERCENTAGE_RISK:
            warnings.append("No stop-loss specified - consider setting one for risk management")
        
        return PositionSizeResult(
            recommended_size=recommended_size,
            max_size=max_size,
            risk_adjusted_size=risk_adjusted_size,
            confidence_score=confidence_score,
            risk_warnings=warnings,
            sizing_method=method,
            position_percentage=position_percentage
        )
    
    async def validate_order_risk(
        self,
        user_wallet: str,
        order_data: Dict[str, Any],
        session=None
    ) -> Tuple[bool, List[str]]:
        """
        Validate order against risk limits.
        
        Args:
            user_wallet: User wallet address
            order_data: Order parameters
            session: Database session
            
        Returns:
            Tuple of (is_valid, warnings)
        """
        try:
            self.logger.info(f"✅ Validating order risk for {user_wallet[:10]}...")
            
            if not session:
                async with self.session_factory() as session:
                    return await self._validate_order_risk_internal(
                        user_wallet, order_data, session
                    )
            else:
                return await self._validate_order_risk_internal(
                    user_wallet, order_data, session
                )
                
        except Exception as e:
            self.logger.error(f"❌ Order risk validation failed: {e}")
            return False, [f"Risk validation failed: {e}"]
    
    async def _validate_order_risk_internal(
        self,
        user_wallet: str,
        order_data: Dict[str, Any],
        session
    ) -> Tuple[bool, List[str]]:
        """Internal order risk validation implementation."""
        warnings = []
        
        # Get risk limits and metrics
        risk_limits = await self._get_user_risk_limits(user_wallet, session)
        risk_metrics = await self._calculate_risk_metrics(user_wallet, session)
        
        # Extract order parameters
        token_address = order_data.get('token_address')
        amount = Decimal(str(order_data.get('amount', 0)))
        price = Decimal(str(order_data.get('price', 0))) if order_data.get('price') else None
        side = OrderSide(order_data.get('side', 'buy'))
        slippage = Decimal(str(order_data.get('slippage_tolerance', 0.01)))
        
        # Calculate position value
        if price and amount:
            position_value = amount * price
        else:
            # For market orders, estimate using current price (would need price feed)
            position_value = amount * Decimal('1')  # Placeholder
        
        # Check position size limits
        max_position_size = risk_limits.get('max_position_size')
        if max_position_size and position_value > max_position_size:
            warnings.append(f"Order exceeds maximum position size: ${position_value}")
            return False, warnings
        
        # Check portfolio percentage limits
        max_position_percentage = risk_limits.get('max_position_percentage', self.default_params['max_position_percentage'])
        position_percentage = position_value / risk_metrics.portfolio_value * 100
        if position_percentage > max_position_percentage:
            warnings.append(f"Order exceeds maximum position percentage: {position_percentage:.1f}%")
            return False, warnings
        
        # Check maximum open positions
        max_open_positions = risk_limits.get('max_open_positions', self.default_params['max_open_positions'])
        if risk_metrics.open_positions_count >= max_open_positions:
            warnings.append(f"Maximum open positions reached: {risk_metrics.open_positions_count}")
            return False, warnings
        
        # Check slippage limits
        max_slippage = risk_limits.get('max_slippage', self.default_params['max_slippage'])
        if slippage > max_slippage:
            warnings.append(f"Slippage tolerance too high: {slippage*100:.1f}%")
            return False, warnings
        
        # Check daily loss limits
        max_daily_loss = risk_limits.get('max_daily_loss')
        if max_daily_loss and risk_metrics.daily_pnl < -max_daily_loss:
            warnings.append("Daily loss limit exceeded - trading restricted")
            return False, warnings
        
        # Check emergency stop
        if risk_limits.get('emergency_stop', False):
            warnings.append("Emergency stop activated - all trading halted")
            return False, warnings
        
        # Check token blacklist
        blacklisted_tokens = risk_limits.get('blacklisted_tokens', [])
        if token_address in blacklisted_tokens:
            warnings.append("Token is blacklisted")
            return False, warnings
        
        # Check token whitelist (if configured)
        whitelisted_tokens = risk_limits.get('whitelisted_tokens')
        if whitelisted_tokens and token_address not in whitelisted_tokens:
            warnings.append("Token not in whitelist")
            return False, warnings
        
        # All checks passed
        if warnings:
            return True, warnings  # Valid but with warnings
        else:
            return True, []
    
    async def monitor_position_risk(
        self,
        position_id: str,
        current_price: Decimal,
        session=None
    ) -> Dict[str, Any]:
        """
        Monitor individual position risk and generate alerts.
        
        Args:
            position_id: Position ID to monitor
            current_price: Current token price
            session: Database session
            
        Returns:
            Dict with risk status and recommended actions
        """
        try:
            self.logger.info(f"📊 Monitoring position risk: {position_id}")
            
            if not session:
                async with self.session_factory() as session:
                    return await self._monitor_position_risk_internal(
                        position_id, current_price, session
                    )
            else:
                return await self._monitor_position_risk_internal(
                    position_id, current_price, session
                )
                
        except Exception as e:
            self.logger.error(f"❌ Position risk monitoring failed: {e}")
            raise Exception(f"Position monitoring failed: {e}")
    
    async def _monitor_position_risk_internal(
        self,
        position_id: str,
        current_price: Decimal,
        session
    ) -> Dict[str, Any]:
        """Internal position risk monitoring implementation."""
        # Get position
        position = await session.query(TradingPosition).filter(
            TradingPosition.position_id == position_id
        ).first()
        
        if not position:
            raise ValueError(f"Position not found: {position_id}")
        
        # Calculate current P&L
        price_change = (current_price - position.average_entry_price) / position.average_entry_price
        current_value = position.remaining_quantity * current_price
        unrealized_pnl = current_value - (position.remaining_quantity * position.average_entry_price)
        
        # Calculate drawdown from peak
        peak_value = max(current_value, position.total_cost)
        drawdown = (peak_value - current_value) / peak_value if peak_value > 0 else 0
        
        # Risk assessment
        risk_alerts = []
        recommended_actions = []
        
        # Check stop-loss
        if position.stop_loss_price and current_price <= position.stop_loss_price:
            risk_alerts.append("CRITICAL: Stop-loss price reached")
            recommended_actions.append("Execute stop-loss order immediately")
        
        # Check take-profit
        if position.take_profit_price and current_price >= position.take_profit_price:
            risk_alerts.append("INFO: Take-profit target reached")
            recommended_actions.append("Consider taking profits")
        
        # Check drawdown
        if drawdown > 0.1:  # 10% drawdown
            risk_alerts.append(f"WARNING: Position drawdown {drawdown*100:.1f}%")
            recommended_actions.append("Consider tightening stop-loss")
        
        # Check position age
        position_age = datetime.utcnow() - position.opened_at.replace(tzinfo=None)
        if position_age.days > 30:
            risk_alerts.append("INFO: Position held for over 30 days")
            recommended_actions.append("Review position and consider exit strategy")
        
        return {
            'position_id': position_id,
            'current_price': str(current_price),
            'entry_price': str(position.average_entry_price),
            'price_change_percentage': float(price_change * 100),
            'unrealized_pnl': str(unrealized_pnl),
            'drawdown_percentage': float(drawdown * 100),
            'risk_alerts': risk_alerts,
            'recommended_actions': recommended_actions,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    # Private helper methods
    
    async def _get_user_risk_limits(self, user_wallet: str, session) -> Dict[str, Any]:
        """Get user risk limits with defaults."""
        risk_limit = await session.query(RiskLimit).filter(
            RiskLimit.user_wallet == user_wallet
        ).first()
        
        if risk_limit:
            return risk_limit.to_dict()
        else:
            # Return default limits
            return {
                'max_position_size': self.default_params['max_position_percentage'],
                'max_position_percentage': self.default_params['max_position_percentage'],
                'max_daily_loss': None,
                'max_drawdown_percentage': self.default_params['max_drawdown_percentage'],
                'max_open_positions': self.default_params['max_open_positions'],
                'max_slippage': self.default_params['max_slippage'],
                'auto_stop_loss': True,
                'emergency_stop': False,
                'blacklisted_tokens': [],
                'whitelisted_tokens': None
            }
    
    async def _calculate_risk_metrics(self, user_wallet: str, session) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        # Get all positions
        positions = await session.query(TradingPosition).filter(
            TradingPosition.user_wallet == user_wallet
        ).all()
        
        # Calculate portfolio value
        portfolio_value = sum(pos.total_cost for pos in positions) or Decimal('1000')  # Default $1000
        
        # Calculate current exposure
        open_positions = [pos for pos in positions if pos.is_open]
        current_exposure = sum(pos.remaining_quantity * pos.average_entry_price for pos in open_positions)
        
        # Calculate available capital
        available_capital = max(Decimal('0'), portfolio_value - current_exposure)
        
        # Calculate daily P&L
        today = datetime.utcnow().date()
        daily_transactions = await session.query(PortfolioTransaction).filter(
            PortfolioTransaction.user_wallet == user_wallet,
            PortfolioTransaction.executed_at >= today
        ).all()
        
        daily_pnl = sum(
            tx.total_value_usd for tx in daily_transactions 
            if tx.total_value_usd and tx.transaction_type in [TransactionType.BUY, TransactionType.SELL]
        ) or Decimal('0')
        
        # Calculate drawdown
        total_pnl = sum(pos.total_pnl for pos in positions)
        drawdown_percentage = max(0, float(-total_pnl / portfolio_value * 100)) if portfolio_value > 0 else 0
        
        # Calculate concentration risk (largest position percentage)
        if open_positions:
            largest_position = max(
                (pos.remaining_quantity * pos.average_entry_price for pos in open_positions),
                default=Decimal('0')
            )
            concentration_risk = float(largest_position / portfolio_value * 100) if portfolio_value > 0 else 0
        else:
            concentration_risk = 0
        
        return RiskMetrics(
            portfolio_value=portfolio_value,
            max_position_size=portfolio_value * self.default_params['max_position_percentage'] / 100,
            current_exposure=current_exposure,
            available_capital=available_capital,
            risk_score=5.0,  # Will be calculated separately
            drawdown_percentage=drawdown_percentage,
            daily_pnl=daily_pnl,
            open_positions_count=len(open_positions),
            concentration_risk=concentration_risk,
            liquidity_score=8.0  # Placeholder - would integrate with liquidity analysis
        )
    
    async def _calculate_risk_score(
        self, 
        risk_metrics: RiskMetrics, 
        risk_limits: Dict[str, Any]
    ) -> float:
        """Calculate overall portfolio risk score (0-10)."""
        score = 0.0
        
        # Exposure risk (0-3 points)
        exposure_ratio = float(risk_metrics.current_exposure / risk_metrics.portfolio_value)
        score += min(3.0, exposure_ratio * 3.0)
        
        # Drawdown risk (0-2 points)
        score += min(2.0, risk_metrics.drawdown_percentage / 10.0)
        
        # Concentration risk (0-2 points)
        score += min(2.0, risk_metrics.concentration_risk / 25.0)
        
        # Position count risk (0-1 point)
        max_positions = risk_limits.get('max_open_positions', 20)
        score += min(1.0, risk_metrics.open_positions_count / max_positions)
        
        # Daily loss risk (0-2 points)
        if risk_metrics.daily_pnl < 0:
            daily_loss_ratio = abs(float(risk_metrics.daily_pnl / risk_metrics.portfolio_value))
            score += min(2.0, daily_loss_ratio * 20)
        
        return min(10.0, score)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score."""
        if risk_score <= 3.0:
            return RiskLevel.LOW
        elif risk_score <= 6.0:
            return RiskLevel.MEDIUM
        elif risk_score <= 8.0:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    async def _check_trading_eligibility(
        self,
        user_wallet: str,
        risk_metrics: RiskMetrics,
        risk_limits: Dict[str, Any],
        session
    ) -> Tuple[bool, List[str]]:
        """Check if user can trade based on risk limits."""
        warnings = []
        
        # Check emergency stop
        if risk_limits.get('emergency_stop', False):
            return False, ["Emergency stop activated"]
        
        # Check daily loss limits
        max_daily_loss = risk_limits.get('max_daily_loss')
        if max_daily_loss and risk_metrics.daily_pnl < -max_daily_loss:
            return False, ["Daily loss limit exceeded"]
        
        # Check maximum drawdown
        max_drawdown = risk_limits.get('max_drawdown_percentage', 20)
        if risk_metrics.drawdown_percentage > max_drawdown:
            return False, ["Maximum drawdown exceeded"]
        
        # Check available capital
        if risk_metrics.available_capital <= 0:
            warnings.append("No available capital for new positions")
        
        # Check concentration risk
        if risk_metrics.concentration_risk > 30:
            warnings.append("High concentration risk - diversify portfolio")
        
        return True, warnings
    
    async def _generate_risk_recommendations(
        self,
        risk_metrics: RiskMetrics,
        risk_limits: Dict[str, Any]
    ) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        
        if risk_metrics.concentration_risk > 20:
            recommendations.append("Reduce concentration risk by diversifying positions")
        
        if risk_metrics.open_positions_count > 15:
            recommendations.append("Consider consolidating positions to reduce management overhead")
        
        if risk_metrics.drawdown_percentage > 10:
            recommendations.append("Implement tighter stop-loss orders to control drawdown")
        
        if float(risk_metrics.current_exposure / risk_metrics.portfolio_value) > 0.8:
            recommendations.append("Reduce overall exposure to maintain adequate reserves")
        
        return recommendations
    
    # Position sizing helper methods
    
    async def _calculate_fixed_amount_size(self, risk_limits: Dict[str, Any]) -> Decimal:
        """Calculate fixed amount position size."""
        return risk_limits.get('max_position_size', Decimal('1000'))
    
    async def _calculate_percentage_risk_size(
        self,
        risk_metrics: RiskMetrics,
        entry_price: Decimal,
        stop_loss_price: Optional[Decimal],
        risk_limits: Dict[str, Any]
    ) -> Decimal:
        """Calculate position size based on percentage risk."""
        risk_percentage = risk_limits.get('max_position_percentage', self.default_params['max_position_percentage'])
        risk_amount = risk_metrics.portfolio_value * risk_percentage / 100
        
        if stop_loss_price and entry_price > stop_loss_price:
            # Calculate position size based on risk per share
            risk_per_share = entry_price - stop_loss_price
            position_size = risk_amount / risk_per_share
        else:
            # Use default percentage of portfolio
            position_size = risk_amount / entry_price
        
        return position_size
    
    async def _calculate_kelly_criterion_size(
        self,
        user_wallet: str,
        token_address: str,
        risk_metrics: RiskMetrics,
        session
    ) -> Decimal:
        """Calculate position size using Kelly Criterion."""
        # Get historical win rate and average win/loss for this token
        # This is a simplified implementation - would need historical trade data
        
        # Placeholder values - would calculate from historical data
        win_rate = Decimal('0.6')  # 60% win rate
        avg_win = Decimal('0.15')  # 15% average win
        avg_loss = Decimal('0.08')  # 8% average loss
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds, p = win probability, q = loss probability
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (b * p - q) / b
        
        # Apply conservative scaling
        conservative_kelly = kelly_fraction * self.default_params['kelly_fraction']
        
        # Calculate position size
        position_size = risk_metrics.portfolio_value * conservative_kelly
        
        return max(Decimal('0'), position_size)
    
    async def _calculate_volatility_adjusted_size(
        self,
        token_address: str,
        risk_metrics: RiskMetrics,
        entry_price: Decimal
    ) -> Decimal:
        """Calculate volatility-adjusted position size."""
        # Placeholder volatility calculation - would integrate with price data
        estimated_volatility = Decimal('0.3')  # 30% volatility
        
        # Adjust position size inversely to volatility
        volatility_adjustment = 1 / (1 + estimated_volatility * self.default_params['volatility_multiplier'])
        
        base_size = risk_metrics.portfolio_value * self.default_params['max_position_percentage'] / 100
        adjusted_size = base_size * Decimal(str(volatility_adjustment))
        
        return adjusted_size / entry_price
    
    async def _calculate_equal_weight_size(
        self,
        risk_metrics: RiskMetrics,
        risk_limits: Dict[str, Any]
    ) -> Decimal:
        """Calculate equal weight position size."""
        max_positions = risk_limits.get('max_open_positions', self.default_params['max_open_positions'])
        target_positions = min(max_positions, 10)  # Max 10 equal positions
        
        return risk_metrics.portfolio_value / target_positions
    
    async def _apply_risk_adjustments(
        self,
        base_size: Decimal,
        risk_metrics: RiskMetrics,
        risk_limits: Dict[str, Any],
        token_address: str
    ) -> Decimal:
        """Apply additional risk adjustments to position size."""
        adjusted_size = base_size
        
        # Reduce size if high concentration risk
        if risk_metrics.concentration_risk > 20:
            adjusted_size *= Decimal('0.8')  # 20% reduction
        
        # Reduce size if many open positions
        if risk_metrics.open_positions_count > 10:
            position_factor = max(Decimal('0.5'), 1 - Decimal(str(risk_metrics.open_positions_count)) / 20)
            adjusted_size *= position_factor
        
        # Reduce size if high drawdown
        if risk_metrics.drawdown_percentage > 10:
            drawdown_factor = max(Decimal('0.5'), 1 - Decimal(str(risk_metrics.drawdown_percentage)) / 100)
            adjusted_size *= drawdown_factor
        
        return adjusted_size
    
    async def _calculate_max_position_size(
        self,
        risk_metrics: RiskMetrics,
        risk_limits: Dict[str, Any],
        token_address: str
    ) -> Decimal:
        """Calculate maximum allowed position size."""
        # Portfolio percentage limit
        max_percentage = risk_limits.get('max_position_percentage', self.default_params['max_position_percentage'])
        percentage_limit = risk_metrics.portfolio_value * max_percentage / 100
        
        # Absolute size limit
        absolute_limit = risk_limits.get('max_position_size', percentage_limit)
        
        # Available capital limit
        capital_limit = risk_metrics.available_capital
        
        return min(percentage_limit, absolute_limit, capital_limit)
    
    async def _calculate_confidence_score(
        self,
        recommended_size: Decimal,
        base_size: Decimal,
        risk_metrics: RiskMetrics,
        token_address: str
    ) -> float:
        """Calculate confidence score for position size recommendation."""
        confidence = 1.0
        
        # Reduce confidence if size was significantly adjusted
        size_ratio = float(recommended_size / base_size) if base_size > 0 else 0
        if size_ratio < 0.8:
            confidence *= 0.8
        elif size_ratio < 0.5:
            confidence *= 0.6
        
        # Reduce confidence if high risk metrics
        if risk_metrics.concentration_risk > 25:
            confidence *= 0.9
        
        if risk_metrics.drawdown_percentage > 15:
            confidence *= 0.8
        
        if risk_metrics.open_positions_count > 15:
            confidence *= 0.9
        
        # Liquidity confidence adjustment
        if risk_metrics.liquidity_score < 5:
            confidence *= 0.7
        
        return max(0.1, min(1.0, confidence))


class PortfolioRiskMonitor:
    """
    Real-time portfolio risk monitoring system.
    """
    
    def __init__(self, risk_manager: RiskManager):
        """Initialize portfolio risk monitor."""
        self.risk_manager = risk_manager
        self.logger = setup_logger(f"{__name__}.PortfolioRiskMonitor")
        self.monitoring_active = False
        self.check_interval = 60  # Check every 60 seconds
        
    async def start_monitoring(self, user_wallet: str):
        """Start real-time portfolio monitoring."""
        try:
            self.logger.info(f"🔄 Starting portfolio monitoring for {user_wallet[:10]}...")
            self.monitoring_active = True
            
            while self.monitoring_active:
                try:
                    # Perform risk assessment
                    assessment = await self.risk_manager.assess_portfolio_risk(user_wallet)
                    
                    # Check for critical conditions
                    await self._check_critical_conditions(user_wallet, assessment)
                    
                    # Log status
                    self.logger.info(
                        f"📊 Portfolio Risk: {assessment.risk_level.value.upper()} "
                        f"(Score: {assessment.risk_score:.1f}/10)"
                    )
                    
                    # Wait before next check
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error in monitoring loop: {e}")
                    await asyncio.sleep(self.check_interval)
                    
        except Exception as e:
            self.logger.error(f"❌ Portfolio monitoring failed: {e}")
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop portfolio monitoring."""
        self.logger.info("⏹️ Stopping portfolio monitoring...")
        self.monitoring_active = False
    
    async def _check_critical_conditions(
        self, 
        user_wallet: str, 
        assessment: RiskAssessmentResult
    ):
        """Check for critical risk conditions and trigger alerts."""
        if assessment.risk_level == RiskLevel.CRITICAL:
            await self._trigger_emergency_actions(user_wallet, assessment)
        elif assessment.risk_level == RiskLevel.HIGH:
            await self._trigger_warning_actions(user_wallet, assessment)
    
    async def _trigger_emergency_actions(
        self, 
        user_wallet: str, 
        assessment: RiskAssessmentResult
    ):
        """Trigger emergency risk management actions."""
        self.logger.critical(f"🚨 CRITICAL RISK LEVEL - Emergency actions for {user_wallet[:10]}")
        
        # Log critical alerts
        for warning in assessment.warnings:
            self.logger.critical(f"🚨 {warning}")
        
        # Could implement:
        # - Automatic position closure
        # - Emergency stop activation
        # - Notification system alerts
        # - Risk manager notifications
        
    async def _trigger_warning_actions(
        self, 
        user_wallet: str, 
        assessment: RiskAssessmentResult
    ):
        """Trigger warning-level risk management actions."""
        self.logger.warning(f"⚠️ HIGH RISK LEVEL - Warning actions for {user_wallet[:10]}")
        
        for warning in assessment.warnings:
            self.logger.warning(f"⚠️ {warning}")


class RiskMetricsCalculator:
    """
    Advanced risk metrics calculation utility.
    """
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: List[float], 
        risk_free_rate: float = 0.02
    ) -> float:
        """Calculate Sharpe ratio."""
        if not returns or len(returns) < 2:
            return 0.0
        
        import statistics
        
        avg_return = statistics.mean(returns)
        return_std = statistics.stdev(returns)
        
        if return_std == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / return_std
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """Calculate maximum drawdown from price series."""
        if not prices or len(prices) < 2:
            return 0.0
        
        peak = prices[0]
        max_drawdown = 0.0
        
        for price in prices[1:]:
            if price > peak:
                peak = price
            
            drawdown = (peak - price) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    @staticmethod
    def calculate_value_at_risk(
        returns: List[float], 
        confidence_level: float = 0.95
    ) -> float:
        """Calculate Value at Risk (VaR)."""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
    
    @staticmethod
    def calculate_beta(
        asset_returns: List[float], 
        market_returns: List[float]
    ) -> float:
        """Calculate beta coefficient."""
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 1.0
        
        import statistics
        
        # Calculate covariance and market variance
        asset_mean = statistics.mean(asset_returns)
        market_mean = statistics.mean(market_returns)
        
        covariance = sum(
            (asset_returns[i] - asset_mean) * (market_returns[i] - market_mean)
            for i in range(len(asset_returns))
        ) / (len(asset_returns) - 1)
        
        market_variance = statistics.variance(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance


# Global risk manager instance
risk_manager = None

def get_risk_manager(session_factory=None) -> RiskManager:
    """Get global risk manager instance."""
    global risk_manager
    if risk_manager is None:
        risk_manager = RiskManager(session_factory)
    return risk_manager


# Risk management decorators and utilities

def require_risk_check(func):
    """Decorator to enforce risk checks on trading functions."""
    async def wrapper(*args, **kwargs):
        # Extract user_wallet and order data from function arguments
        user_wallet = kwargs.get('user_wallet') or (args[0] if args else None)
        
        if not user_wallet:
            raise ValueError("User wallet required for risk check")
        
        # Perform risk assessment
        risk_mgr = get_risk_manager()
        assessment = await risk_mgr.assess_portfolio_risk(user_wallet)
        
        if not assessment.can_trade:
            raise Exception(f"Trading blocked due to risk: {'; '.join(assessment.warnings)}")
        
        # Execute original function
        return await func(*args, **kwargs)
    
    return wrapper


async def validate_trade_risk(
    user_wallet: str,
    token_address: str,
    amount: Decimal,
    side: OrderSide,
    session=None
) -> Dict[str, Any]:
    """
    Utility function to validate trade risk.
    
    Args:
        user_wallet: User wallet address
        token_address: Token contract address
        amount: Trade amount
        side: Order side
        session: Database session
        
    Returns:
        Dict with validation result and risk metrics
    """
    try:
        risk_mgr = get_risk_manager()
        
        # Prepare order data
        order_data = {
            'token_address': token_address,
            'amount': str(amount),
            'side': side.value
        }
        
        # Validate order risk
        is_valid, warnings = await risk_mgr.validate_order_risk(
            user_wallet, order_data, session
        )
        
        # Get risk assessment
        assessment = await risk_mgr.assess_portfolio_risk(user_wallet, session)
        
        return {
            'is_valid': is_valid,
            'warnings': warnings,
            'risk_level': assessment.risk_level.value,
            'risk_score': assessment.risk_score,
            'can_trade': assessment.can_trade,
            'recommendations': assessment.recommendations
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'warnings': [f"Risk validation failed: {e}"],
            'risk_level': 'unknown',
            'risk_score': 10.0,
            'can_trade': False,
            'recommendations': ['Fix risk validation system']
        }
