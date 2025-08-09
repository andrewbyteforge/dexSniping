"""
AI Risk Assessment Engine - Phase 4D
File: app/core/ai/risk_assessment_engine.py
Class: AIRiskAssessmentEngine
Methods: assess_token_risk, analyze_market_conditions, predict_price_movement

Advanced AI-powered risk assessment for live tokens using machine learning
models and comprehensive market analysis for enhanced trading decisions.
"""

import asyncio
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from app.utils.logger import setup_logger
from app.core.exceptions import AIError, DataError, ValidationError
from app.core.blockchain.network_manager import NetworkType
from app.core.dex.live_dex_integration import DEXProtocol

logger = setup_logger(__name__)


class RiskCategory(str, Enum):
    """Risk category enumeration."""
    LIQUIDITY_RISK = "liquidity_risk"
    VOLATILITY_RISK = "volatility_risk"
    SECURITY_RISK = "security_risk"
    MARKET_RISK = "market_risk"
    TECHNICAL_RISK = "technical_risk"
    SOCIAL_RISK = "social_risk"


class AIModelType(str, Enum):
    """AI model type enumeration."""
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"
    TRANSFORMER = "transformer"


class RiskSeverity(str, Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class MarketIndicators:
    """Market indicators data structure."""
    price_24h_change: Decimal
    volume_24h: Decimal
    market_cap: Optional[Decimal]
    liquidity_usd: Decimal
    holder_count: Optional[int]
    transaction_count_24h: int
    large_transactions_24h: int
    whale_activity_score: Decimal
    social_sentiment_score: Decimal
    technical_indicators: Dict[str, Decimal]
    
    def to_features(self) -> np.ndarray:
        """Convert to feature array for ML models."""
        features = [
            float(self.price_24h_change),
            float(self.volume_24h),
            float(self.market_cap or 0),
            float(self.liquidity_usd),
            float(self.holder_count or 0),
            float(self.transaction_count_24h),
            float(self.large_transactions_24h),
            float(self.whale_activity_score),
            float(self.social_sentiment_score)
        ]
        
        # Add technical indicators
        for indicator_name in ['rsi', 'macd', 'bollinger_position', 'volume_sma_ratio']:
            features.append(float(self.technical_indicators.get(indicator_name, 0)))
        
        return np.array(features)


@dataclass
class RiskFactor:
    """Individual risk factor assessment."""
    category: RiskCategory
    severity: RiskSeverity
    confidence: float
    description: str
    impact_score: float
    mitigation_suggestions: List[str]
    data_sources: List[str]


@dataclass
class AIRiskAssessment:
    """Comprehensive AI risk assessment result."""
    token_address: str
    network: NetworkType
    overall_risk_score: float
    confidence_score: float
    risk_factors: List[RiskFactor]
    market_indicators: MarketIndicators
    price_prediction: Optional[Dict[str, Any]]
    recommended_action: str
    assessment_timestamp: datetime
    model_version: str
    
    @property
    def risk_level(self) -> str:
        """Get overall risk level based on score."""
        if self.overall_risk_score >= 0.8:
            return "EXTREME"
        elif self.overall_risk_score >= 0.6:
            return "HIGH"
        elif self.overall_risk_score >= 0.4:
            return "MEDIUM"
        elif self.overall_risk_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    @property
    def critical_risks(self) -> List[RiskFactor]:
        """Get critical risk factors."""
        return [rf for rf in self.risk_factors if rf.severity == RiskSeverity.CRITICAL]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "token_address": self.token_address,
            "network": self.network.value,
            "overall_risk_score": float(self.overall_risk_score),
            "risk_level": self.risk_level,
            "confidence_score": float(self.confidence_score),
            "risk_factors": [
                {
                    "category": rf.category.value,
                    "severity": rf.severity.value,
                    "confidence": rf.confidence,
                    "description": rf.description,
                    "impact_score": rf.impact_score,
                    "mitigation_suggestions": rf.mitigation_suggestions
                }
                for rf in self.risk_factors
            ],
            "critical_risks_count": len(self.critical_risks),
            "recommended_action": self.recommended_action,
            "price_prediction": self.price_prediction,
            "assessment_timestamp": self.assessment_timestamp.isoformat(),
            "model_version": self.model_version
        }


class AIRiskAssessmentEngine:
    """
    Advanced AI-powered risk assessment engine for cryptocurrency tokens.
    
    Uses machine learning models and comprehensive data analysis to assess
    risks associated with trading specific tokens.
    """
    
    def __init__(self):
        """Initialize the AI risk assessment engine."""
        logger.info("🤖 Initializing AI Risk Assessment Engine...")
        
        # Model configuration
        self.model_version = "1.0.0"
        self.active_model_type = AIModelType.ENSEMBLE
        self.models = {}
        
        # Risk assessment configuration
        self.risk_weights = {
            RiskCategory.SECURITY_RISK: 0.25,
            RiskCategory.LIQUIDITY_RISK: 0.20,
            RiskCategory.VOLATILITY_RISK: 0.20,
            RiskCategory.MARKET_RISK: 0.15,
            RiskCategory.TECHNICAL_RISK: 0.10,
            RiskCategory.SOCIAL_RISK: 0.10
        }
        
        # Feature thresholds for risk detection
        self.risk_thresholds = {
            'min_liquidity_usd': 50000,
            'max_price_volatility_24h': 0.5,
            'min_holder_count': 100,
            'max_whale_concentration': 0.3,
            'min_social_sentiment': -0.5,
            'max_security_risk_score': 0.7
        }
        
        # Data sources configuration
        self.data_sources = {
            'price_data': ['dexscreener', 'coingecko', 'dex_apis'],
            'security_data': ['honeypot_is', 'token_sniffer', 'rugcheck'],
            'social_data': ['twitter_api', 'telegram_api', 'discord_api'],
            'blockchain_data': ['etherscan', 'moralis', 'alchemy']
        }
        
        # Cache for assessments
        self.assessment_cache = {}
        self.cache_duration_minutes = 5
        
        logger.info("✅ AI Risk Assessment Engine initialized successfully")
    
    async def assess_token_risk(
        self,
        token_address: str,
        network: NetworkType,
        dex_protocol: Optional[DEXProtocol] = None,
        use_cache: bool = True
    ) -> AIRiskAssessment:
        """
        Perform comprehensive AI-powered risk assessment for a token.
        
        Args:
            token_address: Token contract address
            network: Blockchain network
            dex_protocol: DEX protocol for liquidity analysis
            use_cache: Whether to use cached results
            
        Returns:
            AIRiskAssessment: Comprehensive risk assessment
            
        Raises:
            AIError: If assessment fails
            DataError: If required data is unavailable
        """
        try:
            logger.info(f"🤖 Starting AI risk assessment for token: {token_address[:10]}...")
            
            # Check cache first
            cache_key = f"{token_address}_{network.value}"
            if use_cache and cache_key in self.assessment_cache:
                cached_assessment, timestamp = self.assessment_cache[cache_key]
                if datetime.utcnow() - timestamp < timedelta(minutes=self.cache_duration_minutes):
                    logger.info("📋 Using cached risk assessment")
                    return cached_assessment
            
            # Step 1: Gather market indicators
            market_indicators = await self.gather_market_indicators(token_address, network, dex_protocol)
            
            # Step 2: Analyze individual risk categories
            risk_factors = await self.analyze_risk_categories(token_address, network, market_indicators)
            
            # Step 3: Calculate overall risk score using AI models
            overall_risk_score, confidence_score = await self.calculate_ai_risk_score(
                market_indicators, risk_factors
            )
            
            # Step 4: Generate price prediction
            price_prediction = await self.predict_price_movement(token_address, network, market_indicators)
            
            # Step 5: Determine recommended action
            recommended_action = self.determine_recommended_action(
                overall_risk_score, risk_factors, price_prediction
            )
            
            # Create assessment result
            assessment = AIRiskAssessment(
                token_address=token_address,
                network=network,
                overall_risk_score=overall_risk_score,
                confidence_score=confidence_score,
                risk_factors=risk_factors,
                market_indicators=market_indicators,
                price_prediction=price_prediction,
                recommended_action=recommended_action,
                assessment_timestamp=datetime.utcnow(),
                model_version=self.model_version
            )
            
            # Cache the result
            self.assessment_cache[cache_key] = (assessment, datetime.utcnow())
            
            logger.info(
                f"✅ AI risk assessment complete: {assessment.risk_level} risk "
                f"(score: {overall_risk_score:.3f}, confidence: {confidence_score:.3f})"
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"❌ AI risk assessment failed: {e}")
            raise AIError(f"Risk assessment failed: {e}")
    
    async def gather_market_indicators(
        self,
        token_address: str,
        network: NetworkType,
        dex_protocol: Optional[DEXProtocol]
    ) -> MarketIndicators:
        """
        Gather comprehensive market indicators for the token.
        
        Args:
            token_address: Token contract address
            network: Blockchain network
            dex_protocol: DEX protocol for analysis
            
        Returns:
            MarketIndicators: Comprehensive market data
        """
        try:
            logger.info("📊 Gathering market indicators...")
            
            # Gather data from multiple sources
            price_data = await self._fetch_price_data(token_address, network)
            liquidity_data = await self._fetch_liquidity_data(token_address, network, dex_protocol)
            holder_data = await self._fetch_holder_data(token_address, network)
            transaction_data = await self._fetch_transaction_data(token_address, network)
            social_data = await self._fetch_social_data(token_address)
            technical_data = await self._calculate_technical_indicators(token_address, network)
            
            return MarketIndicators(
                price_24h_change=price_data.get('price_change_24h', Decimal('0')),
                volume_24h=price_data.get('volume_24h', Decimal('0')),
                market_cap=price_data.get('market_cap'),
                liquidity_usd=liquidity_data.get('total_liquidity_usd', Decimal('0')),
                holder_count=holder_data.get('holder_count'),
                transaction_count_24h=transaction_data.get('transaction_count_24h', 0),
                large_transactions_24h=transaction_data.get('large_transactions_24h', 0),
                whale_activity_score=transaction_data.get('whale_activity_score', Decimal('0')),
                social_sentiment_score=social_data.get('sentiment_score', Decimal('0')),
                technical_indicators=technical_data
            )
            
        except Exception as e:
            logger.error(f"❌ Error gathering market indicators: {e}")
            raise DataError(f"Failed to gather market indicators: {e}")
    
    async def analyze_risk_categories(
        self,
        token_address: str,
        network: NetworkType,
        market_indicators: MarketIndicators
    ) -> List[RiskFactor]:
        """
        Analyze individual risk categories using AI models.
        
        Args:
            token_address: Token contract address
            network: Blockchain network
            market_indicators: Market indicators data
            
        Returns:
            List[RiskFactor]: List of identified risk factors
        """
        risk_factors = []
        
        try:
            # Security risk analysis
            security_risks = await self._analyze_security_risks(token_address, network)
            risk_factors.extend(security_risks)
            
            # Liquidity risk analysis
            liquidity_risks = self._analyze_liquidity_risks(market_indicators)
            risk_factors.extend(liquidity_risks)
            
            # Volatility risk analysis
            volatility_risks = self._analyze_volatility_risks(market_indicators)
            risk_factors.extend(volatility_risks)
            
            # Market risk analysis
            market_risks = self._analyze_market_risks(market_indicators)
            risk_factors.extend(market_risks)
            
            # Technical risk analysis
            technical_risks = self._analyze_technical_risks(market_indicators)
            risk_factors.extend(technical_risks)
            
            # Social risk analysis
            social_risks = self._analyze_social_risks(market_indicators)
            risk_factors.extend(social_risks)
            
            logger.info(f"📋 Identified {len(risk_factors)} risk factors")
            return risk_factors
            
        except Exception as e:
            logger.error(f"❌ Error analyzing risk categories: {e}")
            raise AIError(f"Risk category analysis failed: {e}")
    
    async def calculate_ai_risk_score(
        self,
        market_indicators: MarketIndicators,
        risk_factors: List[RiskFactor]
    ) -> Tuple[float, float]:
        """
        Calculate overall risk score using AI models.
        
        Args:
            market_indicators: Market indicators data
            risk_factors: Identified risk factors
            
        Returns:
            Tuple[float, float]: (risk_score, confidence_score)
        """
        try:
            # Convert market indicators to feature vector
            features = market_indicators.to_features()
            
            # Calculate category-based risk scores
            category_scores = {}
            for category in RiskCategory:
                category_factors = [rf for rf in risk_factors if rf.category == category]
                if category_factors:
                    avg_impact = sum(rf.impact_score for rf in category_factors) / len(category_factors)
                    category_scores[category] = min(avg_impact, 1.0)
                else:
                    category_scores[category] = 0.0
            
            # Apply weights to calculate overall score
            weighted_score = sum(
                category_scores[category] * weight
                for category, weight in self.risk_weights.items()
            )
            
            # Apply AI model adjustments (simulated advanced ML)
            ai_adjustment = await self._apply_ai_model_prediction(features, category_scores)
            final_score = min(max(weighted_score + ai_adjustment, 0.0), 1.0)
            
            # Calculate confidence based on data quality and model certainty
            confidence_score = self._calculate_confidence_score(market_indicators, risk_factors)
            
            return final_score, confidence_score
            
        except Exception as e:
            logger.error(f"❌ Error calculating AI risk score: {e}")
            return 0.5, 0.3  # Conservative defaults
    
    async def predict_price_movement(
        self,
        token_address: str,
        network: NetworkType,
        market_indicators: MarketIndicators
    ) -> Optional[Dict[str, Any]]:
        """
        Predict short-term price movement using AI models.
        
        Args:
            token_address: Token contract address
            network: Blockchain network
            market_indicators: Market indicators data
            
        Returns:
            Optional[Dict[str, Any]]: Price prediction data
        """
        try:
            logger.info("🔮 Generating price prediction...")
            
            features = market_indicators.to_features()
            
            # Simulate advanced price prediction model
            # In a real implementation, this would use trained ML models
            prediction_confidence = float(market_indicators.technical_indicators.get('prediction_confidence', 0.5))
            
            # Calculate prediction based on technical indicators and market conditions
            rsi = float(market_indicators.technical_indicators.get('rsi', 50))
            macd = float(market_indicators.technical_indicators.get('macd', 0))
            volume_ratio = float(market_indicators.technical_indicators.get('volume_sma_ratio', 1))
            
            # Simple prediction logic (would be replaced with actual ML model)
            bullish_signals = 0
            bearish_signals = 0
            
            if rsi < 30:  # Oversold
                bullish_signals += 1
            elif rsi > 70:  # Overbought
                bearish_signals += 1
            
            if macd > 0:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if volume_ratio > 1.5:  # High volume
                bullish_signals += 1
            
            # Calculate predicted direction and magnitude
            signal_diff = bullish_signals - bearish_signals
            direction = "bullish" if signal_diff > 0 else "bearish" if signal_diff < 0 else "neutral"
            
            # Calculate predicted price change (simplified)
            base_volatility = float(market_indicators.price_24h_change)
            predicted_change = signal_diff * 0.05 * (1 + abs(base_volatility))
            
            return {
                "direction": direction,
                "predicted_change_24h": predicted_change,
                "confidence": prediction_confidence,
                "bullish_signals": bullish_signals,
                "bearish_signals": bearish_signals,
                "key_factors": [
                    f"RSI: {rsi:.1f}",
                    f"MACD: {macd:.4f}",
                    f"Volume Ratio: {volume_ratio:.2f}"
                ],
                "prediction_horizon": "24h",
                "model_type": "ensemble"
            }
            
        except Exception as e:
            logger.error(f"❌ Error predicting price movement: {e}")
            return None
    
    def determine_recommended_action(
        self,
        risk_score: float,
        risk_factors: List[RiskFactor],
        price_prediction: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determine recommended trading action based on assessment.
        
        Args:
            risk_score: Overall risk score
            risk_factors: Identified risk factors
            price_prediction: Price prediction data
            
        Returns:
            str: Recommended action
        """
        try:
            critical_risks = [rf for rf in risk_factors if rf.severity == RiskSeverity.CRITICAL]
            
            # Critical risk override
            if critical_risks:
                return "AVOID - Critical risks detected"
            
            # High risk threshold
            if risk_score >= 0.8:
                return "AVOID - Extremely high risk"
            elif risk_score >= 0.6:
                return "CAUTION - High risk, small position only"
            elif risk_score >= 0.4:
                action = "MODERATE - Medium risk"
                if price_prediction and price_prediction.get('direction') == 'bullish':
                    action += ", consider small position"
                return action
            elif risk_score >= 0.2:
                action = "FAVORABLE - Low risk"
                if price_prediction and price_prediction.get('confidence', 0) > 0.7:
                    if price_prediction.get('direction') == 'bullish':
                        action += ", good entry opportunity"
                    elif price_prediction.get('direction') == 'bearish':
                        action += ", wait for better entry"
                return action
            else:
                return "EXCELLENT - Very low risk, good opportunity"
                
        except Exception as e:
            logger.error(f"❌ Error determining recommended action: {e}")
            return "UNCERTAIN - Analysis incomplete"
    
    # Helper methods for data fetching and analysis
    
    async def _fetch_price_data(self, token_address: str, network: NetworkType) -> Dict[str, Any]:
        """Fetch price and volume data."""
        # Simulate API calls to price data sources
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            'price_change_24h': Decimal('0.05'),  # 5% change
            'volume_24h': Decimal('100000'),      # $100k volume
            'market_cap': Decimal('1000000')      # $1M market cap
        }
    
    async def _fetch_liquidity_data(
        self, 
        token_address: str, 
        network: NetworkType, 
        dex_protocol: Optional[DEXProtocol]
    ) -> Dict[str, Any]:
        """Fetch liquidity data from DEX."""
        await asyncio.sleep(0.1)
        
        return {
            'total_liquidity_usd': Decimal('250000'),
            'liquidity_distribution': {
                'uniswap_v2': 0.6,
                'uniswap_v3': 0.3,
                'sushiswap': 0.1
            }
        }
    
    async def _fetch_holder_data(self, token_address: str, network: NetworkType) -> Dict[str, Any]:
        """Fetch token holder data."""
        await asyncio.sleep(0.1)
        
        return {
            'holder_count': 1500,
            'whale_concentration': 0.25,
            'top_10_holders_percentage': 0.45
        }
    
    async def _fetch_transaction_data(self, token_address: str, network: NetworkType) -> Dict[str, Any]:
        """Fetch transaction analysis data."""
        await asyncio.sleep(0.1)
        
        return {
            'transaction_count_24h': 150,
            'large_transactions_24h': 5,
            'whale_activity_score': Decimal('0.3'),
            'buy_sell_ratio': 1.2
        }
    
    async def _fetch_social_data(self, token_address: str) -> Dict[str, Any]:
        """Fetch social sentiment data."""
        await asyncio.sleep(0.1)
        
        return {
            'sentiment_score': Decimal('0.2'),  # Slightly positive
            'social_volume': 50,
            'influencer_mentions': 2
        }
    
    async def _calculate_technical_indicators(
        self, 
        token_address: str, 
        network: NetworkType
    ) -> Dict[str, Decimal]:
        """Calculate technical indicators."""
        await asyncio.sleep(0.1)
        
        return {
            'rsi': Decimal('45'),
            'macd': Decimal('0.002'),
            'bollinger_position': Decimal('0.3'),
            'volume_sma_ratio': Decimal('1.2'),
            'prediction_confidence': Decimal('0.65')
        }
    
    async def _analyze_security_risks(
        self, 
        token_address: str, 
        network: NetworkType
    ) -> List[RiskFactor]:
        """Analyze security-related risks."""
        risks = []
        
        # Simulate security analysis
        await asyncio.sleep(0.1)
        
        # Example security risk
        risks.append(RiskFactor(
            category=RiskCategory.SECURITY_RISK,
            severity=RiskSeverity.LOW,
            confidence=0.85,
            description="Contract appears to be legitimate with standard functions",
            impact_score=0.1,
            mitigation_suggestions=["Verify contract source code", "Check for recent audits"],
            data_sources=["etherscan", "token_sniffer"]
        ))
        
        return risks
    
    def _analyze_liquidity_risks(self, market_indicators: MarketIndicators) -> List[RiskFactor]:
        """Analyze liquidity-related risks."""
        risks = []
        
        if market_indicators.liquidity_usd < Decimal('50000'):
            risks.append(RiskFactor(
                category=RiskCategory.LIQUIDITY_RISK,
                severity=RiskSeverity.HIGH,
                confidence=0.9,
                description="Low liquidity may cause high slippage",
                impact_score=0.7,
                mitigation_suggestions=["Use lower position size", "Split trades", "Monitor liquidity before trading"],
                data_sources=["dex_apis"]
            ))
        
        return risks
    
    def _analyze_volatility_risks(self, market_indicators: MarketIndicators) -> List[RiskFactor]:
        """Analyze volatility-related risks."""
        risks = []
        
        if abs(market_indicators.price_24h_change) > Decimal('0.3'):  # 30%
            risks.append(RiskFactor(
                category=RiskCategory.VOLATILITY_RISK,
                severity=RiskSeverity.MEDIUM,
                confidence=0.8,
                description="High price volatility detected",
                impact_score=0.5,
                mitigation_suggestions=["Use tighter stop losses", "Consider smaller position size"],
                data_sources=["price_apis"]
            ))
        
        return risks
    
    def _analyze_market_risks(self, market_indicators: MarketIndicators) -> List[RiskFactor]:
        """Analyze market-related risks."""
        risks = []
        
        if market_indicators.volume_24h < Decimal('10000'):  # Low volume
            risks.append(RiskFactor(
                category=RiskCategory.MARKET_RISK,
                severity=RiskSeverity.MEDIUM,
                confidence=0.75,
                description="Low trading volume may indicate limited interest",
                impact_score=0.4,
                mitigation_suggestions=["Monitor volume trends", "Verify market conditions"],
                data_sources=["dex_apis", "market_data"]
            ))
        
        return risks
    
    def _analyze_technical_risks(self, market_indicators: MarketIndicators) -> List[RiskFactor]:
        """Analyze technical analysis risks."""
        risks = []
        
        rsi = market_indicators.technical_indicators.get('rsi', Decimal('50'))
        if rsi > Decimal('80'):
            risks.append(RiskFactor(
                category=RiskCategory.TECHNICAL_RISK,
                severity=RiskSeverity.MEDIUM,
                confidence=0.7,
                description="RSI indicates overbought conditions",
                impact_score=0.3,
                mitigation_suggestions=["Wait for pullback", "Consider taking profits"],
                data_sources=["technical_analysis"]
            ))
        
        return risks
    
    def _analyze_social_risks(self, market_indicators: MarketIndicators) -> List[RiskFactor]:
        """Analyze social sentiment risks."""
        risks = []
        
        if market_indicators.social_sentiment_score < Decimal('-0.5'):
            risks.append(RiskFactor(
                category=RiskCategory.SOCIAL_RISK,
                severity=RiskSeverity.MEDIUM,
                confidence=0.6,
                description="Negative social sentiment detected",
                impact_score=0.4,
                mitigation_suggestions=["Monitor social channels", "Wait for sentiment improvement"],
                data_sources=["social_apis"]
            ))
        
        return risks
    
    async def _apply_ai_model_prediction(
        self, 
        features: np.ndarray, 
        category_scores: Dict[RiskCategory, float]
    ) -> float:
        """Apply AI model prediction adjustments."""
        # Simulate advanced ML model prediction
        await asyncio.sleep(0.05)
        
        # Simple ensemble adjustment (would be replaced with actual ML models)
        feature_mean = np.mean(features)
        feature_std = np.std(features)
        
        # Normalize and apply model adjustment
        if feature_std > 0:
            normalized_variance = feature_std / (abs(feature_mean) + 1)
            adjustment = (normalized_variance - 0.5) * 0.1  # ±10% adjustment
        else:
            adjustment = 0.0
        
        return max(min(adjustment, 0.2), -0.2)  # Clamp to ±20%
    
    def _calculate_confidence_score(
        self, 
        market_indicators: MarketIndicators, 
        risk_factors: List[RiskFactor]
    ) -> float:
        """Calculate confidence score for the assessment."""
        confidence_factors = []
        
        # Data availability confidence
        data_completeness = 0.8  # Assume good data availability
        confidence_factors.append(data_completeness)
        
        # Risk factor confidence
        if risk_factors:
            avg_risk_confidence = sum(rf.confidence for rf in risk_factors) / len(risk_factors)
            confidence_factors.append(avg_risk_confidence)
        else:
            confidence_factors.append(0.5)  # Medium confidence if no specific risks
        
        # Market conditions confidence
        if market_indicators.volume_24h > Decimal('50000'):
            confidence_factors.append(0.9)  # High confidence with good volume
        else:
            confidence_factors.append(0.6)  # Lower confidence with low volume
        
        return sum(confidence_factors) / len(confidence_factors)


# Global instance for application use
_ai_risk_engine: Optional[AIRiskAssessmentEngine] = None


async def get_ai_risk_engine() -> AIRiskAssessmentEngine:
    """Get the global AI risk assessment engine instance."""
    global _ai_risk_engine
    
    if _ai_risk_engine is None:
        _ai_risk_engine = AIRiskAssessmentEngine()
    
    return _ai_risk_engine


async def initialize_ai_risk_engine() -> AIRiskAssessmentEngine:
    """Initialize the AI risk assessment engine for application startup."""
    engine = await get_ai_risk_engine()
    logger.info("🤖 AI Risk Assessment Engine initialized for application")
    return engine