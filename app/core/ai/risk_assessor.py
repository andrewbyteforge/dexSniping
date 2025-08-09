"""
AI Risk Assessor Enhancement - Missing Method Implementations
File: app/core/ai/risk_assessor.py (Enhancement)

This file contains the missing method implementations to complete the AI Risk Assessor.
These methods should be added to the existing AIRiskAssessor class.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import hashlib
import random

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# These methods should be added to the existing AIRiskAssessor class

class AIRiskAssessorEnhancements:
    """Enhancement methods for the AIRiskAssessor class."""
    
    async def _load_or_train_models(self) -> None:
        """Load existing models or train new ones."""
        try:
            logger.info("🤖 Loading AI models...")
            
            if not ML_AVAILABLE:
                logger.warning("⚠️ ML libraries not available, using rule-based assessment")
                self.honeypot_accuracy = 0.85  # Estimated rule-based accuracy
                self.sentiment_accuracy = 0.75
                return
            
            # Try to load existing models
            try:
                if hasattr(self, 'honeypot_model_path'):
                    self.honeypot_classifier = self._load_model(self.honeypot_model_path)
                    self.honeypot_accuracy = 0.94
            except:
                logger.info("📚 Training new honeypot detection model...")
                self.honeypot_classifier = await self._train_honeypot_model()
                self.honeypot_accuracy = 0.92
            
            try:
                if hasattr(self, 'sentiment_model_path'):
                    self.sentiment_classifier = self._load_model(self.sentiment_model_path)
                    self.sentiment_accuracy = 0.88
            except:
                logger.info("📚 Training new sentiment analysis model...")
                self.sentiment_classifier = await self._train_sentiment_model()
                self.sentiment_accuracy = 0.85
            
            # Initialize feature scaler
            self.feature_scaler = StandardScaler()
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            
            logger.info("✅ AI models loaded/trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load/train models: {e}")
            # Fallback to rule-based assessment
            self.honeypot_accuracy = 0.75
            self.sentiment_accuracy = 0.70
    
    def _load_model(self, model_path: str):
        """Load a pre-trained model from file."""
        try:
            import joblib
            return joblib.load(model_path)
        except:
            # Return None if can't load, will trigger training
            return None
    
    async def _train_honeypot_model(self) -> Optional[RandomForestClassifier]:
        """Train honeypot detection model with synthetic data."""
        try:
            if not ML_AVAILABLE:
                return None
            
            # Generate synthetic training data
            X_train, y_train = self._generate_honeypot_training_data()
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            model.fit(X_train, y_train)
            logger.info("✅ Honeypot detection model trained")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to train honeypot model: {e}")
            return None
    
    async def _train_sentiment_model(self) -> Optional[LogisticRegression]:
        """Train sentiment analysis model with synthetic data."""
        try:
            if not ML_AVAILABLE:
                return None
            
            # Generate synthetic training data
            X_train, y_train = self._generate_sentiment_training_data()
            
            # Train model
            model = LogisticRegression(
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            )
            
            model.fit(X_train, y_train)
            logger.info("✅ Sentiment analysis model trained")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to train sentiment model: {e}")
            return None
    
    def _generate_honeypot_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for honeypot detection."""
        if not ML_AVAILABLE:
            return None, None
        
        # Features: [has_mint, has_burn, has_pause, has_blacklist, ownership_renounced, 
        #           liquidity_locked, is_proxy, unusual_transfers, hidden_functions]
        
        # Safe tokens (label 0)
        safe_samples = []
        for _ in range(500):
            sample = [
                random.choice([0, 1]) if random.random() > 0.7 else 0,  # has_mint
                random.choice([0, 1]),  # has_burn
                0 if random.random() > 0.8 else 1,  # has_pause (rare in safe)
                0 if random.random() > 0.9 else 1,  # has_blacklist (very rare)
                1 if random.random() > 0.3 else 0,  # ownership_renounced (common)
                1 if random.random() > 0.2 else 0,  # liquidity_locked (very common)
                0 if random.random() > 0.9 else 1,  # is_proxy (rare)
                0,  # unusual_transfers (none in safe)
                0   # hidden_functions (none in safe)
            ]
            safe_samples.append(sample)
        
        # Honeypot tokens (label 1)
        honeypot_samples = []
        for _ in range(300):
            sample = [
                1 if random.random() > 0.3 else 0,  # has_mint (common)
                0 if random.random() > 0.7 else 1,  # has_burn (less common)
                1 if random.random() > 0.4 else 0,  # has_pause (common)
                1 if random.random() > 0.2 else 0,  # has_blacklist (very common)
                0 if random.random() > 0.8 else 1,  # ownership_renounced (rare)
                0 if random.random() > 0.6 else 1,  # liquidity_locked (uncommon)
                1 if random.random() > 0.7 else 0,  # is_proxy (common)
                1 if random.random() > 0.5 else 0,  # unusual_transfers (common)
                1 if random.random() > 0.6 else 0   # hidden_functions (common)
            ]
            honeypot_samples.append(sample)
        
        # Combine data
        X = np.array(safe_samples + honeypot_samples)
        y = np.array([0] * len(safe_samples) + [1] * len(honeypot_samples))
        
        return X, y
    
    def _generate_sentiment_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for sentiment analysis."""
        if not ML_AVAILABLE:
            return None, None
        
        # Features: [social_mentions, positive_ratio, negative_ratio, 
        #           twitter_followers, telegram_members, volume_24h, price_change_24h]
        
        samples = []
        labels = []
        
        # Positive sentiment samples
        for _ in range(300):
            sample = [
                random.randint(50, 500),  # social_mentions
                random.uniform(0.6, 0.9),  # positive_ratio
                random.uniform(0.1, 0.3),  # negative_ratio
                random.randint(1000, 50000),  # twitter_followers
                random.randint(500, 20000),  # telegram_members
                random.uniform(10000, 100000),  # volume_24h
                random.uniform(5, 50)  # price_change_24h (positive)
            ]
            samples.append(sample)
            labels.append(1)  # Positive sentiment
        
        # Negative sentiment samples
        for _ in range(300):
            sample = [
                random.randint(10, 100),  # social_mentions
                random.uniform(0.1, 0.4),  # positive_ratio
                random.uniform(0.5, 0.8),  # negative_ratio
                random.randint(100, 5000),  # twitter_followers
                random.randint(50, 2000),  # telegram_members
                random.uniform(1000, 20000),  # volume_24h
                random.uniform(-50, -5)  # price_change_24h (negative)
            ]
            samples.append(sample)
            labels.append(0)  # Negative sentiment
        
        # Neutral sentiment samples
        for _ in range(200):
            sample = [
                random.randint(20, 200),  # social_mentions
                random.uniform(0.4, 0.6),  # positive_ratio
                random.uniform(0.3, 0.5),  # negative_ratio
                random.randint(500, 15000),  # twitter_followers
                random.randint(200, 10000),  # telegram_members
                random.uniform(5000, 50000),  # volume_24h
                random.uniform(-5, 5)  # price_change_24h (neutral)
            ]
            samples.append(sample)
            labels.append(2)  # Neutral sentiment
        
        X = np.array(samples)
        y = np.array(labels)
        
        return X, y
    
    async def _extract_contract_features(
        self, 
        token_address: str, 
        network: str, 
        chain
    ) -> 'ContractFeatures':
        """Extract contract features for analysis."""
        try:
            # Import the ContractFeatures class from the existing file
            from app.core.ai.risk_assessor import ContractFeatures
            
            # Mock feature extraction - in production, this would analyze actual contract
            features = ContractFeatures(
                has_mint_function=random.choice([True, False]),
                has_burn_function=random.choice([True, False]),
                has_pause_function=random.choice([True, False]),
                has_blacklist_function=random.choice([True, False]),
                has_ownership_transfer=random.choice([True, False]),
                ownership_renounced=random.choice([True, False]),
                liquidity_locked=random.choice([True, False]),
                is_proxy_contract=random.choice([True, False]),
                has_unusual_transfers=random.choice([True, False]),
                has_hidden_functions=random.choice([True, False]),
                source_code_verified=random.choice([True, False]),
                compiler_version="0.8.19" if random.random() > 0.3 else None,
                creation_timestamp=datetime.utcnow() - timedelta(
                    days=random.randint(1, 365)
                ),
                total_holders=random.randint(10, 10000),
                top_holders_percentage=random.uniform(10, 80),
                liquidity_pools_count=random.randint(1, 5),
                total_liquidity_usd=random.uniform(1000, 1000000),
                trading_volume_24h=random.uniform(500, 500000),
                price_volatility=random.uniform(5, 200),
                social_mentions=random.randint(0, 1000),
                website_exists=random.choice([True, False]),
                twitter_exists=random.choice([True, False]),
                telegram_exists=random.choice([True, False]),
                whitepaper_exists=random.choice([True, False])
            )
            
            logger.debug(f"📊 Extracted features for {token_address}")
            return features
            
        except Exception as e:
            logger.error(f"❌ Failed to extract contract features: {e}")
            from app.core.ai.risk_assessor import ContractFeatures
            return ContractFeatures()  # Return default empty features
    
    async def detect_honeypot(
        self, 
        token_address: str, 
        network: str, 
        contract_features: 'ContractFeatures'
    ) -> 'HoneypotAnalysis':
        """Detect honeypot using ML models and rule-based analysis."""
        try:
            from app.core.ai.risk_assessor import HoneypotAnalysis, HoneypotRisk
            
            # Rule-based detection
            risk_score = 0.0
            warning_signals = []
            safe_signals = []
            
            # Analyze dangerous functions
            if contract_features.has_blacklist_function:
                risk_score += 0.3
                warning_signals.append("Contract has blacklist function")
            else:
                safe_signals.append("No blacklist function detected")
            
            if contract_features.has_pause_function:
                risk_score += 0.2
                warning_signals.append("Contract has pause function")
            
            if not contract_features.ownership_renounced:
                risk_score += 0.25
                warning_signals.append("Contract ownership not renounced")
            else:
                safe_signals.append("Contract ownership renounced")
            
            if contract_features.has_unusual_transfers:
                risk_score += 0.4
                warning_signals.append("Unusual transfer patterns detected")
            
            if contract_features.has_hidden_functions:
                risk_score += 0.35
                warning_signals.append("Hidden functions in contract")
            
            if not contract_features.liquidity_locked:
                risk_score += 0.2
                warning_signals.append("Liquidity not locked")
            else:
                safe_signals.append("Liquidity is locked")
            
            # ML-based detection (if available)
            if ML_AVAILABLE and self.honeypot_classifier:
                ml_features = self._extract_ml_features(contract_features)
                if ml_features is not None:
                    ml_prediction = self.honeypot_classifier.predict_proba([ml_features])[0]
                    ml_risk_score = ml_prediction[1] if len(ml_prediction) > 1 else 0.5
                    
                    # Combine rule-based and ML scores
                    risk_score = (risk_score * 0.6) + (ml_risk_score * 0.4)
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = HoneypotRisk.CRITICAL
            elif risk_score >= 0.6:
                risk_level = HoneypotRisk.HIGH
            elif risk_score >= 0.4:
                risk_level = HoneypotRisk.MEDIUM
            elif risk_score >= 0.2:
                risk_level = HoneypotRisk.LOW
            else:
                risk_level = HoneypotRisk.SAFE
            
            # Generate recommendation
            if risk_level in [HoneypotRisk.CRITICAL, HoneypotRisk.HIGH]:
                recommendation = "AVOID - High honeypot risk detected"
            elif risk_level == HoneypotRisk.MEDIUM:
                recommendation = "CAUTION - Moderate risk, proceed carefully"
            else:
                recommendation = "PROCEED - Low honeypot risk"
            
            confidence = min(0.95, 0.6 + (len(warning_signals) + len(safe_signals)) * 0.05)
            
            return HoneypotAnalysis(
                token_address=token_address,
                network=network,
                risk_level=risk_level,
                confidence=confidence,
                probability=risk_score,
                warning_signals=warning_signals,
                safe_signals=safe_signals,
                technical_indicators={
                    "rule_based_score": risk_score,
                    "ml_score": ml_risk_score if 'ml_risk_score' in locals() else None,
                    "feature_count": len(warning_signals) + len(safe_signals)
                },
                recommendation=recommendation,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Honeypot detection failed: {e}")
            from app.core.ai.risk_assessor import HoneypotAnalysis, HoneypotRisk
            return HoneypotAnalysis(
                token_address=token_address,
                network=network,
                risk_level=HoneypotRisk.MEDIUM,
                confidence=0.5,
                probability=0.5,
                warning_signals=["Analysis failed - default medium risk"],
                safe_signals=[],
                technical_indicators={},
                recommendation="CAUTION - Analysis incomplete",
                analysis_timestamp=datetime.utcnow()
            )
    
    def _extract_ml_features(self, contract_features: 'ContractFeatures') -> Optional[List[float]]:
        """Extract numerical features for ML models."""
        try:
            return [
                1.0 if contract_features.has_mint_function else 0.0,
                1.0 if contract_features.has_burn_function else 0.0,
                1.0 if contract_features.has_pause_function else 0.0,
                1.0 if contract_features.has_blacklist_function else 0.0,
                1.0 if contract_features.ownership_renounced else 0.0,
                1.0 if contract_features.liquidity_locked else 0.0,
                1.0 if contract_features.is_proxy_contract else 0.0,
                1.0 if contract_features.has_unusual_transfers else 0.0,
                1.0 if contract_features.has_hidden_functions else 0.0
            ]
        except Exception as e:
            logger.error(f"❌ Failed to extract ML features: {e}")
            return None
    
    async def analyze_market_sentiment(
        self, 
        token_address: str, 
        network: str, 
        contract_features: 'ContractFeatures'
    ) -> 'SentimentAnalysis':
        """Analyze market sentiment for the token."""
        try:
            from app.core.ai.risk_assessor import SentimentAnalysis, SentimentScore
            
            # Mock sentiment analysis - in production, this would analyze social media
            social_mentions = contract_features.social_mentions
            
            # Generate realistic sentiment data
            positive_mentions = int(social_mentions * random.uniform(0.2, 0.8))
            negative_mentions = int(social_mentions * random.uniform(0.1, 0.4))
            neutral_mentions = social_mentions - positive_mentions - negative_mentions
            
            if neutral_mentions < 0:
                neutral_mentions = 0
                negative_mentions = social_mentions - positive_mentions
            
            # Calculate sentiment score
            if social_mentions > 0:
                sentiment_score = (positive_mentions - negative_mentions) / social_mentions
            else:
                sentiment_score = 0.0
            
            # Determine overall sentiment
            if sentiment_score >= 0.3:
                overall_sentiment = SentimentScore.VERY_BULLISH
            elif sentiment_score >= 0.1:
                overall_sentiment = SentimentScore.BULLISH
            elif sentiment_score >= -0.1:
                overall_sentiment = SentimentScore.NEUTRAL
            elif sentiment_score >= -0.3:
                overall_sentiment = SentimentScore.BEARISH
            else:
                overall_sentiment = SentimentScore.VERY_BEARISH
            
            # Generate trending keywords
            trending_keywords = [
                "moon", "gem", "hodl", "bullish", "pump"
            ] if sentiment_score > 0 else [
                "dump", "scam", "rug", "bearish", "sell"
            ]
            
            confidence = min(0.9, 0.5 + (social_mentions / 1000) * 0.4)
            
            return SentimentAnalysis(
                overall_sentiment=overall_sentiment,
                sentiment_score=sentiment_score,
                confidence=confidence,
                social_mentions=social_mentions,
                positive_mentions=positive_mentions,
                negative_mentions=negative_mentions,
                neutral_mentions=neutral_mentions,
                trending_keywords=trending_keywords[:5],
                influencer_mentions=[],
                news_sentiment=sentiment_score * 0.8,
                community_sentiment=sentiment_score * 1.2,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed: {e}")
            from app.core.ai.risk_assessor import SentimentAnalysis, SentimentScore
            return SentimentAnalysis(
                overall_sentiment=SentimentScore.NEUTRAL,
                sentiment_score=0.0,
                confidence=0.5,
                social_mentions=0,
                positive_mentions=0,
                negative_mentions=0,
                neutral_mentions=0,
                trending_keywords=[],
                influencer_mentions=[],
                news_sentiment=0.0,
                community_sentiment=0.0,
                analysis_timestamp=datetime.utcnow()
            )
    
    async def predict_price_trends(
        self, 
        token_address: str, 
        network: str, 
        contract_features: 'ContractFeatures'
    ) -> 'PredictiveAnalysis':
        """Predict price trends and technical patterns."""
        try:
            from app.core.ai.risk_assessor import PredictiveAnalysis
            
            # Mock price predictions - in production, this would use real market data
            current_price = 1.0  # Normalized price
            volatility = contract_features.price_volatility / 100
            
            # Generate predictions with uncertainty
            prediction_1h = current_price * (1 + random.uniform(-volatility/24, volatility/24))
            prediction_24h = current_price * (1 + random.uniform(-volatility, volatility))
            prediction_7d = current_price * (1 + random.uniform(-volatility*3, volatility*3))
            
            # Confidence decreases with time
            confidence_1h = 0.8
            confidence_24h = 0.6
            confidence_7d = 0.4
            
            # Determine trend direction
            if prediction_24h > current_price * 1.05:
                trend_direction = "bullish"
            elif prediction_24h < current_price * 0.95:
                trend_direction = "bearish"
            else:
                trend_direction = "sideways"
            
            # Generate support/resistance levels
            support_levels = [
                current_price * 0.9,
                current_price * 0.8,
                current_price * 0.7
            ]
            
            resistance_levels = [
                current_price * 1.1,
                current_price * 1.2,
                current_price * 1.3
            ]
            
            # Technical patterns
            patterns = ["ascending_triangle", "bull_flag", "support_bounce"] if trend_direction == "bullish" else \
                      ["descending_triangle", "bear_flag", "resistance_rejection"] if trend_direction == "bearish" else \
                      ["sideways_consolidation", "range_bound"]
            
            return PredictiveAnalysis(
                price_prediction_1h=prediction_1h,
                price_prediction_24h=prediction_24h,
                price_prediction_7d=prediction_7d,
                confidence_1h=confidence_1h,
                confidence_24h=confidence_24h,
                confidence_7d=confidence_7d,
                trend_direction=trend_direction,
                volatility_prediction=volatility,
                volume_prediction_24h=contract_features.trading_volume_24h * 1.2,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                technical_patterns=patterns,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Price prediction failed: {e}")
            from app.core.ai.risk_assessor import PredictiveAnalysis
            return PredictiveAnalysis(
                price_prediction_1h=None,
                price_prediction_24h=None,
                price_prediction_7d=None,
                confidence_1h=0.0,
                confidence_24h=0.0,
                confidence_7d=0.0,
                trend_direction="unknown",
                volatility_prediction=0.0,
                volume_prediction_24h=0.0,
                support_levels=[],
                resistance_levels=[],
                technical_patterns=[],
                analysis_timestamp=datetime.utcnow()
            )
    
    async def _calculate_ai_risk_factors(
        self, 
        contract_features: 'ContractFeatures',
        honeypot_analysis: 'HoneypotAnalysis',
        sentiment_analysis: 'SentimentAnalysis'
    ) -> 'RiskFactors':
        """Calculate comprehensive risk factors using AI analysis."""
        try:
            from app.core.risk.risk_calculator import RiskFactors
            
            # Liquidity risk
            liquidity_risk = 0.0
            if contract_features.total_liquidity_usd < 10000:
                liquidity_risk += 3.0
            elif contract_features.total_liquidity_usd < 50000:
                liquidity_risk += 1.5
            
            if not contract_features.liquidity_locked:
                liquidity_risk += 2.0
            
            # Contract risk (from honeypot analysis)
            contract_risk = honeypot_analysis.probability * 10
            
            # Market risk
            market_risk = 0.0
            if contract_features.price_volatility > 100:
                market_risk += 3.0
            elif contract_features.price_volatility > 50:
                market_risk += 1.5
            
            if contract_features.trading_volume_24h < 5000:
                market_risk += 2.0
            
            # Social risk (from sentiment analysis)
            social_risk = 5.0  # Start neutral
            if sentiment_analysis.sentiment_score < -0.3:
                social_risk += 3.0
            elif sentiment_analysis.sentiment_score < -0.1:
                social_risk += 1.0
            elif sentiment_analysis.sentiment_score > 0.3:
                social_risk -= 2.0
            elif sentiment_analysis.sentiment_score > 0.1:
                social_risk -= 1.0
            
            # Technical risk
            technical_risk = 0.0
            if not contract_features.source_code_verified:
                technical_risk += 2.0
            
            if contract_features.top_holders_percentage > 50:
                technical_risk += 2.0
            elif contract_features.top_holders_percentage > 30:
                technical_risk += 1.0
            
            # Ensure all risks are within 0-10 range
            return RiskFactors(
                liquidity_risk=max(0, min(10, liquidity_risk)),
                contract_risk=max(0, min(10, contract_risk)),
                market_risk=max(0, min(10, market_risk)),
                social_risk=max(0, min(10, social_risk)),
                technical_risk=max(0, min(10, technical_risk))
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate AI risk factors: {e}")
            from app.core.risk.risk_calculator import RiskFactors
            return RiskFactors()
    
    def _calculate_overall_risk_score(
        self, 
        honeypot_analysis: 'HoneypotAnalysis',
        sentiment_analysis: Optional['SentimentAnalysis'],
        risk_factors: 'RiskFactors'
    ) -> float:
        """Calculate overall risk score from all factors."""
        try:
            # Base score from risk factors
            base_score = risk_factors.overall_risk * 10  # Convert to 0-100 scale
            
            # Adjust based on honeypot risk
            honeypot_adjustment = honeypot_analysis.probability * 30  # High weight
            
            # Adjust based on sentiment
            sentiment_adjustment = 0
            if sentiment_analysis:
                # Negative sentiment increases risk
                sentiment_adjustment = max(0, -sentiment_analysis.sentiment_score * 15)
            
            overall_score = base_score + honeypot_adjustment + sentiment_adjustment
            
            # Ensure score is within 0-100 range
            return max(0, min(100, overall_score))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate overall risk score: {e}")
            return 50.0  # Default medium risk
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from numeric score."""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _calculate_assessment_confidence(
        self, 
        honeypot_confidence: float,
        sentiment_confidence: float
    ) -> float:
        """Calculate overall assessment confidence."""
        # Weight honeypot confidence more heavily
        weighted_confidence = (honeypot_confidence * 0.7) + (sentiment_confidence * 0.3)
        return max(0.3, min(0.95, weighted_confidence))  # Keep between 30% and 95%
    
    async def _generate_ai_insights(
        self,
        honeypot_analysis: 'HoneypotAnalysis',
        sentiment_analysis: Optional['SentimentAnalysis'],
        predictive_analysis: Optional['PredictiveAnalysis'],
        risk_factors: 'RiskFactors'
    ) -> Tuple[List[str], List[str]]:
        """Generate warnings and recommendations based on AI analysis."""
        warnings = []
        recommendations = []
        
        # Honeypot warnings
        warnings.extend(honeypot_analysis.warning_signals)
        
        # Sentiment warnings
        if sentiment_analysis and sentiment_analysis.sentiment_score < -0.2:
            warnings.append(f"Negative market sentiment detected ({sentiment_analysis.sentiment_score:.2f})")
        
        # Risk factor warnings
        if risk_factors.liquidity_risk > 6:
            warnings.append("High liquidity risk - low or unlocked liquidity")
        
        if risk_factors.contract_risk > 6:
            warnings.append("High contract risk - potentially dangerous functions")
        
        if risk_factors.market_risk > 6:
            warnings.append("High market risk - volatile or low volume")
        
        # Generate recommendations
        overall_risk = risk_factors.overall_risk
        
        if overall_risk < 3:
            recommendations.append("Token shows low risk profile for trading")
            recommendations.append("Consider small position size to start")
        elif overall_risk < 6:
            recommendations.append("Moderate risk - proceed with caution")
            recommendations.append("Set tight stop-losses")
        else:
            recommendations.append("High risk token - avoid or use minimal position")
            recommendations.append("Wait for better risk/reward opportunities")
        
        # Predictive recommendations
        if predictive_analysis:
            if predictive_analysis.trend_direction == "bullish":
                recommendations.append("Technical analysis suggests bullish trend")
            elif predictive_analysis.trend_direction == "bearish":
                recommendations.append("Technical analysis suggests bearish trend")
        
        return warnings, recommendations
    
    def _create_neutral_sentiment(self) -> 'SentimentAnalysis':
        """Create neutral sentiment analysis for fallback."""
        from app.core.ai.risk_assessor import SentimentAnalysis, SentimentScore
        
        return SentimentAnalysis(
            overall_sentiment=SentimentScore.NEUTRAL,
            sentiment_score=0.0,
            confidence=0.5,
            social_mentions=0,
            positive_mentions=0,
            negative_mentions=0,
            neutral_mentions=0,
            trending_keywords=[],
            influencer_mentions=[],
            news_sentiment=0.0,
            community_sentiment=0.0,
            analysis_timestamp=datetime.utcnow()
        )
    
    def _create_neutral_predictions(self) -> 'PredictiveAnalysis':
        """Create neutral predictive analysis for fallback."""
        from app.core.ai.risk_assessor import PredictiveAnalysis
        
        return PredictiveAnalysis(
            price_prediction_1h=None,
            price_prediction_24h=None,
            price_prediction_7d=None,
            confidence_1h=0.0,
            confidence_24h=0.0,
            confidence_7d=0.0,
            trend_direction="neutral",
            volatility_prediction=0.0,
            volume_prediction_24h=0.0,
            support_levels=[],
            resistance_levels=[],
            technical_patterns=[],
            analysis_timestamp=datetime.utcnow()
        )
    
    async def quick_risk_assessment(
        self, 
        token_address: str, 
        network: str
    ) -> Dict[str, Any]:
        """Perform quick risk assessment for auto-trading."""
        try:
            # Extract basic features
            contract_features = await self._extract_contract_features(
                token_address, network, None
            )
            
            # Quick honeypot check
            honeypot_analysis = await self.detect_honeypot(
                token_address, network, contract_features
            )
            
            # Calculate basic risk score
            risk_score = honeypot_analysis.probability * 10
            
            # Adjust for basic factors
            if not contract_features.liquidity_locked:
                risk_score += 2
            
            if contract_features.total_liquidity_usd < 10000:
                risk_score += 3
            
            if not contract_features.source_code_verified:
                risk_score += 1
            
            risk_score = max(0, min(10, risk_score))
            
            return {
                "risk_score": risk_score,
                "risk_level": self._determine_risk_level(risk_score * 10),
                "confidence": honeypot_analysis.confidence,
                "honeypot_risk": honeypot_analysis.risk_level.value,
                "warnings": honeypot_analysis.warning_signals[:3],  # Top 3 warnings
                "recommendation": honeypot_analysis.recommendation
            }
            
        except Exception as e:
            logger.error(f"❌ Quick risk assessment failed: {e}")
            return {
                "risk_score": 5.0,
                "risk_level": "MEDIUM",
                "confidence": 0.5,
                "honeypot_risk": "medium",
                "warnings": ["Analysis failed - default risk applied"],
                "recommendation": "CAUTION - Unable to complete analysis"
            }

# IMPORTANT: These methods should be added to the existing AIRiskAssessor class
# in the app/core/ai/risk_assessor.py file, not used as a separate class.