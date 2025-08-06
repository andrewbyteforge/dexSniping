"""
AI Risk Assessment System
File: app/core/trading/ai_risk_assessor.py

Advanced AI-powered risk assessment for trading decisions using machine learning
to analyze market conditions, token metrics, and trading patterns.
"""

import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from app.core.config.settings_manager import get_settings
from app.core.database.persistence_manager import get_persistence_manager

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class MarketCondition(Enum):
    """Market condition assessment."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    UNCERTAIN = "uncertain"


@dataclass
class TokenMetrics:
    """Token analysis metrics."""
    symbol: str
    price: float
    volume_24h: float
    market_cap: Optional[float]
    liquidity: float
    price_change_24h: float
    volatility_score: float
    holder_count: Optional[int]
    transaction_count_24h: int
    timestamp: datetime


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result."""
    token_symbol: str
    overall_risk: RiskLevel
    risk_score: float  # 0-100, higher is riskier
    market_condition: MarketCondition
    confidence_level: float  # 0-1
    factors: Dict[str, Any]
    recommendations: List[str]
    max_position_size: float
    stop_loss_percentage: float
    take_profit_percentage: float
    timestamp: datetime


class AIRiskAssessor:
    """
    AI-powered risk assessment system for trading decisions.
    
    Uses multiple analysis techniques including:
    - Technical indicator analysis
    - Market sentiment assessment
    - Liquidity and volume analysis
    - Historical pattern recognition
    - Token fundamental analysis
    """
    
    def __init__(self):
        """Initialize the AI risk assessor."""
        self.settings = get_settings()
        self.assessment_cache = {}
        self.cache_duration = timedelta(minutes=5)
        
        # Risk model parameters
        self.volatility_threshold = 0.15  # 15% daily volatility
        self.liquidity_threshold = 10000  # Min $10k liquidity
        self.volume_threshold = 1000  # Min $1k daily volume
        
        logger.info("AI Risk Assessor initialized")
    
    async def assess_token_risk(
        self, 
        token_symbol: str, 
        token_address: str,
        amount_usd: float
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment for a token trade.
        
        Args:
            token_symbol: Token symbol (e.g., 'ETH')
            token_address: Token contract address
            amount_usd: Trade amount in USD
            
        Returns:
            RiskAssessment: Comprehensive risk analysis
            
        Raises:
            ValueError: If token data is insufficient
            RuntimeError: If assessment fails
        """
        try:
            # Check cache first
            cache_key = f"{token_symbol}_{amount_usd}"
            if self._is_cached_valid(cache_key):
                logger.info(f"Using cached risk assessment for {token_symbol}")
                return self.assessment_cache[cache_key]
            
            # Gather token metrics
            token_metrics = await self._gather_token_metrics(
                token_symbol, token_address
            )
            
            # Analyze market conditions
            market_condition = await self._analyze_market_conditions(token_metrics)
            
            # Calculate technical indicators
            technical_factors = await self._calculate_technical_factors(token_metrics)
            
            # Assess liquidity and volume
            liquidity_factors = self._assess_liquidity_factors(token_metrics)
            
            # Fundamental analysis
            fundamental_factors = await self._analyze_fundamentals(token_metrics)
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(
                technical_factors,
                liquidity_factors,
                fundamental_factors,
                amount_usd
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate trading recommendations
            recommendations = self._generate_recommendations(
                risk_level, market_condition, amount_usd, token_metrics
            )
            
            # Calculate position sizing
            max_position_size = self._calculate_max_position_size(
                risk_score, amount_usd
            )
            
            # Set stop loss and take profit levels
            stop_loss_pct, take_profit_pct = self._calculate_exit_levels(
                risk_level, token_metrics.volatility_score
            )
            
            # Create assessment
            assessment = RiskAssessment(
                token_symbol=token_symbol,
                overall_risk=risk_level,
                risk_score=risk_score,
                market_condition=market_condition,
                confidence_level=self._calculate_confidence_level(token_metrics),
                factors={
                    "technical": technical_factors,
                    "liquidity": liquidity_factors,
                    "fundamental": fundamental_factors,
                    "metrics": {
                        "volatility": token_metrics.volatility_score,
                        "volume_24h": token_metrics.volume_24h,
                        "liquidity": token_metrics.liquidity,
                        "price_change": token_metrics.price_change_24h
                    }
                },
                recommendations=recommendations,
                max_position_size=max_position_size,
                stop_loss_percentage=stop_loss_pct,
                take_profit_percentage=take_profit_pct,
                timestamp=datetime.utcnow()
            )
            
            # Cache the assessment
            self.assessment_cache[cache_key] = assessment
            
            # Log assessment
            logger.info(
                f"Risk assessment for {token_symbol}: "
                f"{risk_level.value} (score: {risk_score:.1f})"
            )
            
            return assessment
            
        except Exception as error:
            logger.error(f"Risk assessment failed for {token_symbol}: {error}")
            raise RuntimeError(f"Risk assessment failed: {error}")
    
    async def _gather_token_metrics(
        self, token_symbol: str, token_address: str
    ) -> TokenMetrics:
        """
        Gather comprehensive token metrics.
        
        Args:
            token_symbol: Token symbol
            token_address: Token contract address
            
        Returns:
            TokenMetrics: Token analysis data
        """
        try:
            # In a real implementation, this would fetch from:
            # - DEXScreener API for price/volume data
            # - Etherscan for transaction counts
            # - DeFiPulse for liquidity data
            # - CoinGecko for market cap data
            
            # Mock data for development (replace with real data sources)
            mock_metrics = TokenMetrics(
                symbol=token_symbol,
                price=100.0,  # Would fetch real price
                volume_24h=50000.0,  # Would fetch real volume
                market_cap=1000000.0,  # Would fetch real market cap
                liquidity=25000.0,  # Would calculate from DEX pools
                price_change_24h=-2.5,  # Would fetch real price change
                volatility_score=0.12,  # Would calculate from price history
                holder_count=1500,  # Would fetch from blockchain
                transaction_count_24h=250,  # Would fetch from blockchain
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"Gathered metrics for {token_symbol}")
            return mock_metrics
            
        except Exception as error:
            logger.error(f"Failed to gather metrics for {token_symbol}: {error}")
            raise ValueError(f"Insufficient token data: {error}")
    
    async def _analyze_market_conditions(
        self, token_metrics: TokenMetrics
    ) -> MarketCondition:
        """
        Analyze current market conditions.
        
        Args:
            token_metrics: Token metrics data
            
        Returns:
            MarketCondition: Market condition assessment
        """
        try:
            # Analyze price action and volume
            price_change = token_metrics.price_change_24h
            volatility = token_metrics.volatility_score
            
            # Determine market condition based on metrics
            if abs(price_change) < 2 and volatility < 0.05:
                return MarketCondition.SIDEWAYS
            elif price_change > 5 and volatility < 0.1:
                return MarketCondition.BULLISH
            elif price_change < -5 and volatility < 0.1:
                return MarketCondition.BEARISH
            elif volatility > 0.2:
                return MarketCondition.VOLATILE
            else:
                return MarketCondition.UNCERTAIN
                
        except Exception as error:
            logger.error(f"Market condition analysis failed: {error}")
            return MarketCondition.UNCERTAIN
    
    async def _calculate_technical_factors(
        self, token_metrics: TokenMetrics
    ) -> Dict[str, float]:
        """
        Calculate technical analysis factors.
        
        Args:
            token_metrics: Token metrics data
            
        Returns:
            Dict[str, float]: Technical factors and scores
        """
        try:
            factors = {
                "momentum_score": self._calculate_momentum_score(token_metrics),
                "trend_strength": self._calculate_trend_strength(token_metrics),
                "support_resistance": self._analyze_support_resistance(token_metrics),
                "volume_profile": self._analyze_volume_profile(token_metrics)
            }
            
            logger.debug(f"Technical factors calculated: {factors}")
            return factors
            
        except Exception as error:
            logger.error(f"Technical factor calculation failed: {error}")
            return {"momentum_score": 0.5, "trend_strength": 0.5, 
                   "support_resistance": 0.5, "volume_profile": 0.5}
    
    def _assess_liquidity_factors(self, token_metrics: TokenMetrics) -> Dict[str, float]:
        """
        Assess liquidity-related risk factors.
        
        Args:
            token_metrics: Token metrics data
            
        Returns:
            Dict[str, float]: Liquidity factors and scores
        """
        try:
            # Calculate liquidity score (0-1, higher is better)
            liquidity_score = min(
                token_metrics.liquidity / self.liquidity_threshold, 1.0
            )
            
            # Calculate volume score (0-1, higher is better)
            volume_score = min(
                token_metrics.volume_24h / self.volume_threshold, 1.0
            )
            
            # Calculate market depth approximation
            market_depth_score = liquidity_score * 0.7 + volume_score * 0.3
            
            factors = {
                "liquidity_score": liquidity_score,
                "volume_score": volume_score,
                "market_depth": market_depth_score,
                "slippage_risk": 1.0 - market_depth_score  # Inverse relationship
            }
            
            logger.debug(f"Liquidity factors assessed: {factors}")
            return factors
            
        except Exception as error:
            logger.error(f"Liquidity assessment failed: {error}")
            return {"liquidity_score": 0.5, "volume_score": 0.5, 
                   "market_depth": 0.5, "slippage_risk": 0.5}
    
    async def _analyze_fundamentals(
        self, token_metrics: TokenMetrics
    ) -> Dict[str, float]:
        """
        Analyze fundamental token factors.
        
        Args:
            token_metrics: Token metrics data
            
        Returns:
            Dict[str, float]: Fundamental factors and scores
        """
        try:
            # Market cap analysis
            market_cap_score = 0.5
            if token_metrics.market_cap:
                if token_metrics.market_cap > 100_000_000:  # > $100M
                    market_cap_score = 0.8
                elif token_metrics.market_cap > 10_000_000:  # > $10M
                    market_cap_score = 0.6
                else:
                    market_cap_score = 0.3
            
            # Holder distribution analysis
            holder_score = 0.5
            if token_metrics.holder_count:
                if token_metrics.holder_count > 10000:
                    holder_score = 0.8
                elif token_metrics.holder_count > 1000:
                    holder_score = 0.6
                else:
                    holder_score = 0.3
            
            # Transaction activity analysis
            activity_score = min(
                token_metrics.transaction_count_24h / 1000, 1.0
            )
            
            factors = {
                "market_cap_score": market_cap_score,
                "holder_distribution": holder_score,
                "transaction_activity": activity_score,
                "fundamental_strength": (
                    market_cap_score * 0.4 + 
                    holder_score * 0.3 + 
                    activity_score * 0.3
                )
            }
            
            logger.debug(f"Fundamental factors analyzed: {factors}")
            return factors
            
        except Exception as error:
            logger.error(f"Fundamental analysis failed: {error}")
            return {"market_cap_score": 0.5, "holder_distribution": 0.5,
                   "transaction_activity": 0.5, "fundamental_strength": 0.5}
    
    def _calculate_risk_score(
        self,
        technical_factors: Dict[str, float],
        liquidity_factors: Dict[str, float],
        fundamental_factors: Dict[str, float],
        amount_usd: float
    ) -> float:
        """
        Calculate overall risk score (0-100).
        
        Args:
            technical_factors: Technical analysis results
            liquidity_factors: Liquidity analysis results
            fundamental_factors: Fundamental analysis results
            amount_usd: Trade amount in USD
            
        Returns:
            float: Risk score (0-100, higher is riskier)
        """
        try:
            # Base risk from technical factors (lower momentum/trend = higher risk)
            technical_risk = (
                (1.0 - technical_factors.get("momentum_score", 0.5)) * 25 +
                (1.0 - technical_factors.get("trend_strength", 0.5)) * 15
            )
            
            # Liquidity risk (lower liquidity = higher risk)
            liquidity_risk = (
                liquidity_factors.get("slippage_risk", 0.5) * 30 +
                (1.0 - liquidity_factors.get("volume_score", 0.5)) * 10
            )
            
            # Fundamental risk (weaker fundamentals = higher risk)
            fundamental_risk = (
                (1.0 - fundamental_factors.get("fundamental_strength", 0.5)) * 20
            )
            
            # Position size risk (larger positions = higher risk)
            position_risk = min(amount_usd / 10000, 1.0) * 10  # Scale with size
            
            # Calculate total risk score
            total_risk = technical_risk + liquidity_risk + fundamental_risk + position_risk
            
            # Ensure score is within bounds
            risk_score = max(0, min(100, total_risk))
            
            logger.debug(f"Risk score calculated: {risk_score:.1f}")
            return risk_score
            
        except Exception as error:
            logger.error(f"Risk score calculation failed: {error}")
            return 50.0  # Default medium risk
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Determine risk level from risk score.
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            RiskLevel: Categorical risk level
        """
        if risk_score <= 15:
            return RiskLevel.VERY_LOW
        elif risk_score <= 30:
            return RiskLevel.LOW
        elif risk_score <= 50:
            return RiskLevel.MEDIUM
        elif risk_score <= 70:
            return RiskLevel.HIGH
        elif risk_score <= 85:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.EXTREME
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        market_condition: MarketCondition,
        amount_usd: float,
        token_metrics: TokenMetrics
    ) -> List[str]:
        """
        Generate trading recommendations based on risk assessment.
        
        Args:
            risk_level: Assessed risk level
            market_condition: Market condition
            amount_usd: Trade amount
            token_metrics: Token metrics
            
        Returns:
            List[str]: Trading recommendations
        """
        recommendations = []
        
        # Risk-based recommendations
        if risk_level in [RiskLevel.VERY_HIGH, RiskLevel.EXTREME]:
            recommendations.append("⚠️ High risk detected - consider avoiding this trade")
            recommendations.append("💰 If trading, use very small position size")
            recommendations.append("🛡️ Set tight stop-loss orders")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("⚡ Moderate risk - trade with caution")
            recommendations.append("📊 Monitor position closely")
        elif risk_level in [RiskLevel.LOW, RiskLevel.VERY_LOW]:
            recommendations.append("✅ Low risk detected - favorable conditions")
        
        # Market condition recommendations
        if market_condition == MarketCondition.VOLATILE:
            recommendations.append("🌊 High volatility - expect price swings")
            recommendations.append("⏰ Consider shorter holding periods")
        elif market_condition == MarketCondition.BULLISH:
            recommendations.append("📈 Bullish trend - favorable for long positions")
        elif market_condition == MarketCondition.BEARISH:
            recommendations.append("📉 Bearish trend - consider short positions or wait")
        
        # Liquidity recommendations
        if token_metrics.liquidity < self.liquidity_threshold:
            recommendations.append("💧 Low liquidity - expect higher slippage")
            recommendations.append("⚡ Use smaller trade sizes")
        
        # Volume recommendations
        if token_metrics.volume_24h < self.volume_threshold:
            recommendations.append("📊 Low volume - limited market activity")
        
        return recommendations
    
    def _calculate_max_position_size(
        self, risk_score: float, requested_amount: float
    ) -> float:
        """
        Calculate maximum recommended position size.
        
        Args:
            risk_score: Risk score (0-100)
            requested_amount: Requested trade amount
            
        Returns:
            float: Maximum recommended position size
        """
        # Scale position size inversely with risk
        risk_multiplier = max(0.1, (100 - risk_score) / 100)
        max_size = requested_amount * risk_multiplier
        
        # Apply absolute limits based on settings
        max_daily_loss = self.settings.trading.max_daily_loss_usd
        absolute_max = max_daily_loss * 0.5  # Max 50% of daily loss limit
        
        return min(max_size, absolute_max)
    
    def _calculate_exit_levels(
        self, risk_level: RiskLevel, volatility: float
    ) -> Tuple[float, float]:
        """
        Calculate stop-loss and take-profit percentages.
        
        Args:
            risk_level: Risk level assessment
            volatility: Token volatility score
            
        Returns:
            Tuple[float, float]: (stop_loss_pct, take_profit_pct)
        """
        # Base levels adjusted for risk and volatility
        base_stop_loss = 5.0  # 5%
        base_take_profit = 10.0  # 10%
        
        # Adjust for risk level
        risk_multipliers = {
            RiskLevel.VERY_LOW: (0.8, 1.2),
            RiskLevel.LOW: (0.9, 1.1),
            RiskLevel.MEDIUM: (1.0, 1.0),
            RiskLevel.HIGH: (1.2, 0.9),
            RiskLevel.VERY_HIGH: (1.5, 0.8),
            RiskLevel.EXTREME: (2.0, 0.7)
        }
        
        stop_mult, profit_mult = risk_multipliers.get(
            risk_level, (1.0, 1.0)
        )
        
        # Adjust for volatility
        volatility_factor = 1 + (volatility * 2)  # Scale with volatility
        
        stop_loss_pct = base_stop_loss * stop_mult * volatility_factor
        take_profit_pct = base_take_profit * profit_mult * volatility_factor
        
        # Apply reasonable bounds
        stop_loss_pct = max(2.0, min(25.0, stop_loss_pct))
        take_profit_pct = max(5.0, min(50.0, take_profit_pct))
        
        return stop_loss_pct, take_profit_pct
    
    def _calculate_confidence_level(self, token_metrics: TokenMetrics) -> float:
        """
        Calculate confidence level in the assessment.
        
        Args:
            token_metrics: Token metrics data
            
        Returns:
            float: Confidence level (0-1)
        """
        confidence_factors = []
        
        # Data completeness
        if token_metrics.market_cap:
            confidence_factors.append(0.2)
        if token_metrics.holder_count:
            confidence_factors.append(0.2)
        if token_metrics.volume_24h > 0:
            confidence_factors.append(0.3)
        if token_metrics.liquidity > 0:
            confidence_factors.append(0.3)
        
        return sum(confidence_factors)
    
    def _calculate_momentum_score(self, token_metrics: TokenMetrics) -> float:
        """Calculate momentum score from price action."""
        # Simplified momentum calculation
        price_momentum = min(abs(token_metrics.price_change_24h) / 10, 1.0)
        return price_momentum if token_metrics.price_change_24h > 0 else 1.0 - price_momentum
    
    def _calculate_trend_strength(self, token_metrics: TokenMetrics) -> float:
        """Calculate trend strength score."""
        # Simplified trend strength based on volume and price change
        volume_factor = min(token_metrics.volume_24h / 10000, 1.0)
        price_factor = min(abs(token_metrics.price_change_24h) / 5, 1.0)
        return (volume_factor + price_factor) / 2
    
    def _analyze_support_resistance(self, token_metrics: TokenMetrics) -> float:
        """Analyze support/resistance levels."""
        # Simplified analysis - would need historical price data
        return 0.5  # Neutral score
    
    def _analyze_volume_profile(self, token_metrics: TokenMetrics) -> float:
        """Analyze volume profile strength."""
        # Score based on 24h volume relative to market cap
        if token_metrics.market_cap and token_metrics.market_cap > 0:
            volume_ratio = token_metrics.volume_24h / token_metrics.market_cap
            return min(volume_ratio * 100, 1.0)  # Scale to 0-1
        return 0.5
    
    def _is_cached_valid(self, cache_key: str) -> bool:
        """Check if cached assessment is still valid."""
        if cache_key not in self.assessment_cache:
            return False
        
        cached_assessment = self.assessment_cache[cache_key]
        age = datetime.utcnow() - cached_assessment.timestamp
        return age < self.cache_duration
    
    async def get_portfolio_risk_summary(self) -> Dict[str, Any]:
        """
        Get overall portfolio risk summary.
        
        Returns:
            Dict[str, Any]: Portfolio risk analysis
        """
        try:
            # Get portfolio positions from database
            pm = await get_persistence_manager()
            # This would fetch actual portfolio data
            
            # Mock portfolio summary
            summary = {
                "overall_risk": RiskLevel.MEDIUM.value,
                "total_positions": 0,
                "high_risk_positions": 0,
                "diversification_score": 0.7,
                "max_drawdown_risk": 15.0,
                "recommended_actions": [
                    "Portfolio appears balanced",
                    "Monitor high-risk positions closely"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as error:
            logger.error(f"Portfolio risk summary failed: {error}")
            return {
                "overall_risk": RiskLevel.MEDIUM.value,
                "error": "Risk analysis temporarily unavailable"
            }


# Global instance
_ai_risk_assessor: Optional[AIRiskAssessor] = None


async def get_ai_risk_assessor() -> AIRiskAssessor:
    """
    Get the global AI risk assessor instance.
    
    Returns:
        AIRiskAssessor: The risk assessor instance
    """
    global _ai_risk_assessor
    
    if _ai_risk_assessor is None:
        _ai_risk_assessor = AIRiskAssessor()
    
    return _ai_risk_assessor


# Export for external use
__all__ = [
    "AIRiskAssessor",
    "RiskAssessment", 
    "RiskLevel",
    "MarketCondition",
    "TokenMetrics",
    "get_ai_risk_assessor"
]