"""
Enhanced AI Prediction Models System - Phase 4C Implementation
File: app/core/ai/enhanced_prediction_models.py
Class: EnhancedAIPredictionSystem
Methods: predict_price_movement, analyze_market_sentiment, detect_anomalies, generate_trading_signals

Advanced machine learning system for cryptocurrency price prediction, market analysis,
and automated trading signal generation using multiple AI models and data sources.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import warnings
warnings.filterwarnings('ignore')

from app.utils.logger import setup_logger
from app.core.exceptions import TradingError, AIModelError

logger = setup_logger(__name__)


class PredictionTimeframe(str, Enum):
    """Prediction timeframe options."""
    SHORT_TERM = "5_minutes"
    MEDIUM_TERM = "1_hour"
    LONG_TERM = "24_hours"
    EXTENDED = "7_days"


class MarketSentiment(str, Enum):
    """Market sentiment classifications."""
    EXTREMELY_BEARISH = "extremely_bearish"
    BEARISH = "bearish"
    SLIGHTLY_BEARISH = "slightly_bearish"
    NEUTRAL = "neutral"
    SLIGHTLY_BULLISH = "slightly_bullish"
    BULLISH = "bullish"
    EXTREMELY_BULLISH = "extremely_bullish"


class AnomalyType(str, Enum):
    """Types of market anomalies."""
    PRICE_SPIKE = "price_spike"
    VOLUME_SURGE = "volume_surge"
    LIQUIDITY_DRAIN = "liquidity_drain"
    WHALE_MOVEMENT = "whale_movement"
    BOT_ACTIVITY = "bot_activity"
    MARKET_MANIPULATION = "market_manipulation"


class SignalStrength(str, Enum):
    """Trading signal strength levels."""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class PriceMovementPrediction:
    """Price movement prediction result."""
    token_address: str
    token_symbol: str
    network: str
    timeframe: PredictionTimeframe
    current_price: float
    predicted_price: float
    price_change_percent: float
    confidence_score: float
    probability_up: float
    probability_down: float
    support_levels: List[float]
    resistance_levels: List[float]
    volatility_forecast: float
    trend_direction: str
    model_consensus: Dict[str, Any]
    prediction_timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))


@dataclass
class SentimentAnalysis:
    """Market sentiment analysis result."""
    token_address: str
    token_symbol: str
    network: str
    overall_sentiment: MarketSentiment
    sentiment_score: float  # -1.0 to 1.0
    confidence: float
    social_sentiment: float
    news_sentiment: float
    technical_sentiment: float
    volume_sentiment: float
    whale_sentiment: float
    sentiment_trend: str  # improving, declining, stable
    key_factors: List[str]
    sentiment_sources: Dict[str, float]
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyDetection:
    """Market anomaly detection result."""
    anomaly_id: str
    token_address: str
    token_symbol: str
    network: str
    anomaly_type: AnomalyType
    severity: float  # 0.0 to 1.0
    confidence: float
    description: str
    affected_metrics: List[str]
    potential_impact: str
    recommended_action: str
    detection_timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradingSignal:
    """AI-generated trading signal."""
    signal_id: str
    token_address: str
    token_symbol: str
    network: str
    signal_type: str  # buy, sell, hold
    signal_strength: SignalStrength
    confidence: float
    expected_profit: float
    risk_level: float
    time_horizon: PredictionTimeframe
    entry_price: float
    target_price: float
    stop_loss_price: float
    reasoning: str
    contributing_factors: List[str]
    model_agreements: int
    signal_timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=30))


@dataclass
class ModelPerformance:
    """AI model performance metrics."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    mae: float
    directional_accuracy: float
    last_trained: datetime
    training_samples: int
    validation_score: float


class EnhancedAIPredictionSystem:
    """
    Enhanced AI Prediction Models System
    
    Advanced machine learning system for cryptocurrency trading that combines
    multiple AI models for price prediction, sentiment analysis, anomaly detection,
    and automated signal generation.
    
    Features:
    - Multi-model ensemble predictions with consensus scoring
    - Real-time market sentiment analysis from multiple sources
    - Advanced anomaly detection for market manipulation
    - Automated trading signal generation with risk assessment
    - Continuous model training and performance monitoring
    - Feature engineering with technical indicators
    """
    
    def __init__(self, model_directory: str = "models/"):
        """Initialize Enhanced AI Prediction System."""
        self.model_directory = model_directory
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.model_performance: Dict[str, ModelPerformance] = {}
        
        # Model configurations
        self.price_prediction_models = [
            "random_forest_regressor",
            "gradient_boosting_regressor",
            "lstm_neural_network"
        ]
        
        self.classification_models = [
            "gradient_boosting_classifier",
            "random_forest_classifier",
            "svm_classifier"
        ]
        
        # Feature engineering components
        self.feature_extractors = {}
        self.technical_indicators = {}
        
        # Prediction cache
        self.prediction_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Performance tracking
        self.total_predictions_made = 0
        self.correct_predictions = 0
        self.system_start_time = datetime.utcnow()
        
        # Anomaly detection
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.anomaly_thresholds = {
            AnomalyType.PRICE_SPIKE: 0.8,
            AnomalyType.VOLUME_SURGE: 0.7,
            AnomalyType.LIQUIDITY_DRAIN: 0.9,
            AnomalyType.WHALE_MOVEMENT: 0.85,
            AnomalyType.BOT_ACTIVITY: 0.75
        }
        
        # Signal generation
        self.active_signals: Dict[str, TradingSignal] = {}
        self.signal_history: List[TradingSignal] = []
        
        os.makedirs(model_directory, exist_ok=True)
        logger.info("🧠 Enhanced AI Prediction System initialized")
    
    async def initialize_models(self) -> bool:
        """
        Initialize and load all AI models.
        
        Returns:
            bool: True if models initialized successfully
        """
        try:
            logger.info("🚀 Initializing AI prediction models...")
            
            # Initialize price prediction models
            await self._initialize_price_prediction_models()
            
            # Initialize classification models
            await self._initialize_classification_models()
            
            # Initialize anomaly detection models
            await self._initialize_anomaly_detection_models()
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            # Load or train models
            await self._load_or_train_models()
            
            logger.info("✅ AI prediction models initialized successfully")
            logger.info(f"📊 Loaded {len(self.models)} models")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI models: {e}")
            return False
    
    async def predict_price_movement(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        timeframe: PredictionTimeframe,
        price_history: List[Dict[str, Any]],
        volume_history: List[Dict[str, Any]],
        market_data: Optional[Dict[str, Any]] = None
    ) -> PriceMovementPrediction:
        """
        Predict price movement using ensemble of AI models.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            timeframe: Prediction timeframe
            price_history: Historical price data
            volume_history: Historical volume data
            market_data: Additional market data
            
        Returns:
            Price movement prediction with confidence scores
        """
        try:
            # Check cache first
            cache_key = f"{token_address}_{timeframe.value}_{datetime.utcnow().strftime('%Y%m%d%H%M')[:11]}"
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]
            
            # Extract features
            features = await self._extract_features(
                price_history, volume_history, market_data
            )
            
            if len(features) < 10:  # Minimum feature requirement
                raise AIModelError("Insufficient data for prediction")
            
            # Get predictions from multiple models
            model_predictions = {}
            confidence_scores = {}
            
            for model_name in self.price_prediction_models:
                if model_name in self.models:
                    try:
                        prediction, confidence = await self._get_model_prediction(
                            model_name, features, timeframe
                        )
                        model_predictions[model_name] = prediction
                        confidence_scores[model_name] = confidence
                    except Exception as e:
                        logger.warning(f"Model {model_name} prediction failed: {e}")
            
            if not model_predictions:
                raise AIModelError("No models available for prediction")
            
            # Calculate ensemble prediction
            predictions = list(model_predictions.values())
            weights = list(confidence_scores.values())
            
            # Weighted average prediction
            weighted_prediction = np.average(predictions, weights=weights)
            overall_confidence = np.mean(list(confidence_scores.values()))
            
            # Calculate price change
            current_price = price_history[-1]['price']
            price_change_percent = ((weighted_prediction - current_price) / current_price) * 100
            
            # Calculate probabilities
            probability_up = self._calculate_upward_probability(
                price_change_percent, overall_confidence
            )
            probability_down = 1.0 - probability_up
            
            # Calculate support and resistance levels
            support_levels, resistance_levels = await self._calculate_support_resistance(
                price_history, weighted_prediction
            )
            
            # Forecast volatility
            volatility_forecast = await self._forecast_volatility(price_history, timeframe)
            
            # Determine trend direction
            trend_direction = await self._determine_trend_direction(
                price_history, weighted_prediction
            )
            
            # Create model consensus summary
            model_consensus = {
                "predictions": model_predictions,
                "confidences": confidence_scores,
                "ensemble_weight": weights,
                "agreement_score": self._calculate_model_agreement(predictions),
                "model_count": len(model_predictions)
            }
            
            # Create prediction result
            prediction_result = PriceMovementPrediction(
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                timeframe=timeframe,
                current_price=current_price,
                predicted_price=weighted_prediction,
                price_change_percent=price_change_percent,
                confidence_score=overall_confidence,
                probability_up=probability_up,
                probability_down=probability_down,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                volatility_forecast=volatility_forecast,
                trend_direction=trend_direction,
                model_consensus=model_consensus
            )
            
            # Cache prediction
            self.prediction_cache[cache_key] = prediction_result
            self.total_predictions_made += 1
            
            logger.info(f"📈 Price prediction generated for {token_symbol}: "
                       f"{price_change_percent:.2f}% change predicted "
                       f"({overall_confidence:.2f} confidence)")
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"❌ Price prediction error: {e}")
            raise AIModelError(f"Price prediction failed: {e}")
    
    async def analyze_market_sentiment(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        price_history: List[Dict[str, Any]],
        volume_history: List[Dict[str, Any]],
        social_data: Optional[Dict[str, Any]] = None,
        news_data: Optional[List[Dict[str, Any]]] = None
    ) -> SentimentAnalysis:
        """
        Analyze market sentiment using multiple data sources and AI models.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            price_history: Historical price data
            volume_history: Historical volume data
            social_data: Social media sentiment data
            news_data: News sentiment data
            
        Returns:
            Comprehensive sentiment analysis
        """
        try:
            # Technical sentiment from price/volume patterns
            technical_sentiment = await self._analyze_technical_sentiment(
                price_history, volume_history
            )
            
            # Social media sentiment
            social_sentiment = await self._analyze_social_sentiment(
                social_data, token_symbol
            )
            
            # News sentiment
            news_sentiment = await self._analyze_news_sentiment(
                news_data, token_symbol
            )
            
            # Volume-based sentiment
            volume_sentiment = await self._analyze_volume_sentiment(
                volume_history, price_history
            )
            
            # Whale activity sentiment
            whale_sentiment = await self._analyze_whale_sentiment(
                token_address, price_history
            )
            
            # Calculate overall sentiment
            sentiment_components = {
                "technical": technical_sentiment * 0.3,
                "social": social_sentiment * 0.2,
                "news": news_sentiment * 0.2,
                "volume": volume_sentiment * 0.15,
                "whale": whale_sentiment * 0.15
            }
            
            overall_sentiment_score = sum(sentiment_components.values())
            
            # Map sentiment score to category
            overall_sentiment = self._map_sentiment_score_to_category(overall_sentiment_score)
            
            # Calculate confidence based on data availability and agreement
            confidence = self._calculate_sentiment_confidence(
                technical_sentiment, social_sentiment, news_sentiment,
                volume_sentiment, whale_sentiment
            )
            
            # Determine sentiment trend
            sentiment_trend = await self._determine_sentiment_trend(
                price_history, volume_history
            )
            
            # Identify key factors
            key_factors = self._identify_sentiment_factors(
                sentiment_components, overall_sentiment_score
            )
            
            # Create sentiment analysis result
            sentiment_analysis = SentimentAnalysis(
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                overall_sentiment=overall_sentiment,
                sentiment_score=overall_sentiment_score,
                confidence=confidence,
                social_sentiment=social_sentiment,
                news_sentiment=news_sentiment,
                technical_sentiment=technical_sentiment,
                volume_sentiment=volume_sentiment,
                whale_sentiment=whale_sentiment,
                sentiment_trend=sentiment_trend,
                key_factors=key_factors,
                sentiment_sources=sentiment_components
            )
            
            logger.info(f"💭 Sentiment analysis completed for {token_symbol}: "
                       f"{overall_sentiment.value} ({overall_sentiment_score:.2f})")
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis error: {e}")
            raise AIModelError(f"Sentiment analysis failed: {e}")
    
    async def detect_anomalies(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        price_history: List[Dict[str, Any]],
        volume_history: List[Dict[str, Any]],
        liquidity_data: Optional[Dict[str, Any]] = None,
        transaction_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[AnomalyDetection]:
        """
        Detect market anomalies using advanced AI models.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            price_history: Historical price data
            volume_history: Historical volume data
            liquidity_data: Liquidity pool data
            transaction_data: Recent transaction data
            
        Returns:
            List of detected anomalies
        """
        try:
            detected_anomalies = []
            
            # Price spike detection
            price_anomalies = await self._detect_price_anomalies(
                price_history, token_address, token_symbol, network
            )
            detected_anomalies.extend(price_anomalies)
            
            # Volume surge detection
            volume_anomalies = await self._detect_volume_anomalies(
                volume_history, token_address, token_symbol, network
            )
            detected_anomalies.extend(volume_anomalies)
            
            # Liquidity drain detection
            if liquidity_data:
                liquidity_anomalies = await self._detect_liquidity_anomalies(
                    liquidity_data, token_address, token_symbol, network
                )
                detected_anomalies.extend(liquidity_anomalies)
            
            # Whale movement detection
            if transaction_data:
                whale_anomalies = await self._detect_whale_anomalies(
                    transaction_data, token_address, token_symbol, network
                )
                detected_anomalies.extend(whale_anomalies)
            
            # Bot activity detection
            bot_anomalies = await self._detect_bot_activity(
                transaction_data or [], price_history, token_address, token_symbol, network
            )
            detected_anomalies.extend(bot_anomalies)
            
            # Sort by severity
            detected_anomalies.sort(key=lambda x: x.severity, reverse=True)
            
            if detected_anomalies:
                logger.info(f"🚨 {len(detected_anomalies)} anomalies detected for {token_symbol}")
            
            return detected_anomalies
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection error: {e}")
            return []
    
    async def generate_trading_signals(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        price_prediction: PriceMovementPrediction,
        sentiment_analysis: SentimentAnalysis,
        anomalies: List[AnomalyDetection],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> List[TradingSignal]:
        """
        Generate AI-powered trading signals based on all analysis components.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Blockchain network
            price_prediction: Price movement prediction
            sentiment_analysis: Market sentiment analysis
            anomalies: Detected market anomalies
            market_conditions: Overall market conditions
            
        Returns:
            List of generated trading signals
        """
        try:
            signals = []
            
            # Generate signals for each timeframe
            timeframes = [
                PredictionTimeframe.SHORT_TERM,
                PredictionTimeframe.MEDIUM_TERM,
                PredictionTimeframe.LONG_TERM
            ]
            
            for timeframe in timeframes:
                signal = await self._generate_signal_for_timeframe(
                    token_address, token_symbol, network, timeframe,
                    price_prediction, sentiment_analysis, anomalies, market_conditions
                )
                
                if signal:
                    signals.append(signal)
                    self.active_signals[signal.signal_id] = signal
            
            # Filter and rank signals
            signals = self._filter_and_rank_signals(signals)
            
            if signals:
                logger.info(f"📡 {len(signals)} trading signals generated for {token_symbol}")
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            return []
    
    async def get_model_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive model performance summary.
        
        Returns:
            Model performance metrics and statistics
        """
        try:
            total_accuracy = 0
            active_models = 0
            
            model_stats = {}
            for model_name, performance in self.model_performance.items():
                model_stats[model_name] = {
                    "accuracy": performance.accuracy,
                    "precision": performance.precision,
                    "recall": performance.recall,
                    "f1_score": performance.f1_score,
                    "directional_accuracy": performance.directional_accuracy,
                    "last_trained": performance.last_trained.isoformat(),
                    "training_samples": performance.training_samples
                }
                
                if performance.accuracy > 0:
                    total_accuracy += performance.accuracy
                    active_models += 1
            
            average_accuracy = total_accuracy / active_models if active_models > 0 else 0
            prediction_accuracy = (self.correct_predictions / self.total_predictions_made * 100 
                                  if self.total_predictions_made > 0 else 0)
            
            return {
                "system_uptime_hours": (datetime.utcnow() - self.system_start_time).total_seconds() / 3600,
                "total_predictions_made": self.total_predictions_made,
                "prediction_accuracy_percent": prediction_accuracy,
                "average_model_accuracy": average_accuracy,
                "active_models": active_models,
                "active_signals": len(self.active_signals),
                "model_performance": model_stats,
                "cache_size": len(self.prediction_cache)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance summary: {e}")
            return {}
    
    # Private helper methods
    async def _initialize_price_prediction_models(self) -> None:
        """Initialize price prediction models."""
        try:
            # Random Forest Regressor
            self.models["random_forest_regressor"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Gradient Boosting Regressor  
            self.models["gradient_boosting_regressor"] = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
            
            # Initialize scalers
            self.scalers["price_scaler"] = StandardScaler()
            self.scalers["feature_scaler"] = MinMaxScaler()
            
            logger.info("✅ Price prediction models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing price models: {e}")
            raise
    
    async def _initialize_classification_models(self) -> None:
        """Initialize classification models."""
        try:
            # Gradient Boosting Classifier
            self.models["gradient_boosting_classifier"] = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
            
            # Random Forest Classifier
            from sklearn.ensemble import RandomForestClassifier
            self.models["random_forest_classifier"] = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            logger.info("✅ Classification models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing classification models: {e}")
            raise
    
    async def _initialize_anomaly_detection_models(self) -> None:
        """Initialize anomaly detection models."""
        try:
            # Price anomaly detector
            self.anomaly_detectors["price"] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Volume anomaly detector
            self.anomaly_detectors["volume"] = IsolationForest(
                contamination=0.15,
                random_state=42
            )
            
            # Transaction pattern detector
            self.anomaly_detectors["transactions"] = IsolationForest(
                contamination=0.05,
                random_state=42
            )
            
            logger.info("✅ Anomaly detection models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing anomaly models: {e}")
            raise
    
    async def _initialize_feature_extractors(self) -> None:
        """Initialize feature extraction components."""
        try:
            # Technical indicators
            self.technical_indicators = {
                "sma_periods": [5, 10, 20, 50],
                "ema_periods": [12, 26],
                "rsi_period": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "bollinger_period": 20,
                "volatility_period": 20
            }
            
            # Feature extraction functions
            self.feature_extractors = {
                "price_features": self._extract_price_features,
                "volume_features": self._extract_volume_features,
                "technical_features": self._extract_technical_features,
                "momentum_features": self._extract_momentum_features
            }
            
            logger.info("✅ Feature extractors initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing feature extractors: {e}")
            raise
    
    async def _load_or_train_models(self) -> None:
        """Load existing models or train new ones."""
        try:
            # Check if models exist
            models_exist = os.path.exists(os.path.join(self.model_directory, "models.pkl"))
            
            if models_exist:
                await self._load_models()
            else:
                await self._train_initial_models()
            
            logger.info("✅ Models loaded/trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading/training models: {e}")
            # Continue with untrained models for graceful degradation
    
    async def _load_models(self) -> None:
        """Load pre-trained models from disk."""
        try:
            model_file = os.path.join(self.model_directory, "models.pkl")
            with open(model_file, 'rb') as f:
                saved_data = pickle.load(f)
                
            self.models.update(saved_data.get("models", {}))
            self.scalers.update(saved_data.get("scalers", {}))
            
            # Load performance metrics
            performance_file = os.path.join(self.model_directory, "performance.json")
            if os.path.exists(performance_file):
                with open(performance_file, 'r') as f:
                    perf_data = json.load(f)
                    
                for model_name, perf in perf_data.items():
                    self.model_performance[model_name] = ModelPerformance(
                        model_name=model_name,
                        accuracy=perf.get("accuracy", 0.0),
                        precision=perf.get("precision", 0.0),
                        recall=perf.get("recall", 0.0),
                        f1_score=perf.get("f1_score", 0.0),
                        mse=perf.get("mse", 0.0),
                        mae=perf.get("mae", 0.0),
                        directional_accuracy=perf.get("directional_accuracy", 0.0),
                        last_trained=datetime.fromisoformat(perf.get("last_trained", datetime.utcnow().isoformat())),
                        training_samples=perf.get("training_samples", 0),
                        validation_score=perf.get("validation_score", 0.0)
                    )
            
            logger.info("📁 Pre-trained models loaded from disk")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            raise
    
    async def _train_initial_models(self) -> None:
        """Train initial models with synthetic data."""
        try:
            # Generate synthetic training data
            training_data = self._generate_synthetic_training_data()
            
            X = training_data["features"]
            y_price = training_data["price_targets"]
            y_direction = training_data["direction_targets"]
            
            # Split data
            X_train, X_test, y_price_train, y_price_test = train_test_split(
                X, y_price, test_size=0.2, random_state=42
            )
            
            _, _, y_dir_train, y_dir_test = train_test_split(
                X, y_direction, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scalers["feature_scaler"].fit_transform(X_train)
            X_test_scaled = self.scalers["feature_scaler"].transform(X_test)
            
            # Train regression models
            if "random_forest_regressor" in self.models:
                self.models["random_forest_regressor"].fit(X_train_scaled, y_price_train)
                
            # Train classification models
            if "gradient_boosting_classifier" in self.models:
                self.models["gradient_boosting_classifier"].fit(X_train_scaled, y_dir_train)
                
            if "random_forest_classifier" in self.models:
                self.models["random_forest_classifier"].fit(X_train_scaled, y_dir_train)
            
            # Train anomaly detectors with normal data
            normal_data = X_train_scaled[y_direction[:len(X_train_scaled)] == 0]  # Stable price data
            
            for detector_name, detector in self.anomaly_detectors.items():
                if len(normal_data) > 10:  # Minimum samples required
                    detector.fit(normal_data)
            
            # Calculate performance metrics
            await self._calculate_model_performance(X_test_scaled, y_price_test, y_dir_test)
            
            # Save models
            await self._save_models()
            
            logger.info("🎯 Initial models trained with synthetic data")
            
        except Exception as e:
            logger.error(f"❌ Error training initial models: {e}")
            # Continue without trained models for graceful degradation
    
    def _generate_synthetic_training_data(self) -> Dict[str, np.ndarray]:
        """Generate synthetic training data for initial model training."""
        try:
            # Generate 1000 samples
            n_samples = 1000
            n_features = 20
            
            # Random features representing technical indicators
            features = np.random.randn(n_samples, n_features)
            
            # Add some realistic patterns
            for i in range(n_samples):
                # Add trend patterns
                features[i, 0] = np.mean(features[max(0, i-5):i+1, 0])  # Moving average
                
                # Add volatility patterns
                if i > 10:
                    features[i, 1] = np.std(features[i-10:i, 0])  # Volatility
                
                # Add momentum patterns
                if i > 1:
                    features[i, 2] = features[i, 0] - features[i-1, 0]  # Price change
            
            # Generate price targets (next period price change)
            price_targets = []
            direction_targets = []
            
            for i in range(n_samples):
                # Simulate price movement based on features
                momentum = features[i, 2] * 0.5
                volatility_factor = abs(features[i, 1]) * 0.3
                trend_factor = features[i, 0] * 0.2
                
                price_change = momentum + np.random.normal(0, volatility_factor) + trend_factor
                price_targets.append(price_change)
                
                # Direction: 1 for up, 0 for stable, -1 for down
                if price_change > 0.02:
                    direction_targets.append(1)
                elif price_change < -0.02:
                    direction_targets.append(-1)
                else:
                    direction_targets.append(0)
            
            return {
                "features": features,
                "price_targets": np.array(price_targets),
                "direction_targets": np.array(direction_targets)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating synthetic data: {e}")
            return {
                "features": np.random.randn(100, 10),
                "price_targets": np.random.randn(100),
                "direction_targets": np.random.choice([-1, 0, 1], 100)
            }
    
    async def _extract_features(
        self,
        price_history: List[Dict[str, Any]],
        volume_history: List[Dict[str, Any]],
        market_data: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """Extract features for model prediction."""
        try:
            features = []
            
            # Extract price features
            price_features = await self._extract_price_features(price_history)
            features.extend(price_features)
            
            # Extract volume features
            volume_features = await self._extract_volume_features(volume_history)
            features.extend(volume_features)
            
            # Extract technical features
            technical_features = await self._extract_technical_features(price_history)
            features.extend(technical_features)
            
            # Extract momentum features
            momentum_features = await self._extract_momentum_features(price_history, volume_history)
            features.extend(momentum_features)
            
            # Add market data features if available
            if market_data:
                market_features = self._extract_market_features(market_data)
                features.extend(market_features)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"❌ Feature extraction error: {e}")
            return np.random.randn(1, 10)  # Fallback random features
    
    async def _extract_price_features(self, price_history: List[Dict[str, Any]]) -> List[float]:
        """Extract price-based features."""
        try:
            if len(price_history) < 2:
                return [0.0] * 5
            
            prices = [p['price'] for p in price_history[-50:]]  # Last 50 prices
            
            features = []
            
            # Current price
            features.append(prices[-1])
            
            # Price changes
            if len(prices) > 1:
                features.append(prices[-1] - prices[-2])  # 1-period change
                
            if len(prices) > 5:
                features.append(prices[-1] - prices[-6])  # 5-period change
                
            # Moving averages
            if len(prices) >= 10:
                features.append(np.mean(prices[-10:]))  # 10-period MA
                
            if len(prices) >= 20:
                features.append(np.mean(prices[-20:]))  # 20-period MA
            else:
                features.append(np.mean(prices))
                
            # Price volatility
            if len(prices) >= 10:
                features.append(np.std(prices[-10:]))
            else:
                features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Price feature extraction error: {e}")
            return [0.0] * 5
    
    async def _extract_volume_features(self, volume_history: List[Dict[str, Any]]) -> List[float]:
        """Extract volume-based features."""
        try:
            if not volume_history:
                return [0.0] * 3
            
            volumes = [v.get('volume', 0) for v in volume_history[-50:]]
            
            features = []
            
            # Current volume
            features.append(volumes[-1] if volumes else 0.0)
            
            # Volume moving average
            if len(volumes) >= 10:
                features.append(np.mean(volumes[-10:]))
            else:
                features.append(np.mean(volumes) if volumes else 0.0)
                
            # Volume ratio (current vs average)
            avg_volume = np.mean(volumes) if volumes else 1.0
            if avg_volume > 0:
                features.append(volumes[-1] / avg_volume if volumes else 0.0)
            else:
                features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Volume feature extraction error: {e}")
            return [0.0] * 3
    
    async def _extract_technical_features(self, price_history: List[Dict[str, Any]]) -> List[float]:
        """Extract technical indicator features."""
        try:
            if len(price_history) < 15:
                return [0.0] * 4
            
            prices = [p['price'] for p in price_history[-50:]]
            
            features = []
            
            # RSI
            rsi = await self._calculate_rsi_simple(prices)
            features.append(rsi)
            
            # MACD
            if len(prices) >= 26:
                ema_12 = self._calculate_ema(prices, 12)
                ema_26 = self._calculate_ema(prices, 26)
                macd = ema_12 - ema_26
                features.append(macd)
            else:
                features.append(0.0)
            
            # Bollinger Bands position
            if len(prices) >= 20:
                sma_20 = np.mean(prices[-20:])
                std_20 = np.std(prices[-20:])
                upper_band = sma_20 + (2 * std_20)
                lower_band = sma_20 - (2 * std_20)
                
                if upper_band != lower_band:
                    bb_position = (prices[-1] - lower_band) / (upper_band - lower_band)
                    features.append(bb_position)
                else:
                    features.append(0.5)
            else:
                features.append(0.5)
            
            # Price momentum
            if len(prices) >= 10:
                momentum = prices[-1] - prices[-11]
                features.append(momentum)
            else:
                features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Technical feature extraction error: {e}")
            return [0.0] * 4
    
    async def _extract_momentum_features(
        self,
        price_history: List[Dict[str, Any]],
        volume_history: List[Dict[str, Any]]
    ) -> List[float]:
        """Extract momentum-based features."""
        try:
            features = []
            
            if len(price_history) < 2:
                return [0.0] * 3
            
            prices = [p['price'] for p in price_history[-20:]]
            volumes = [v.get('volume', 0) for v in volume_history[-20:]] if volume_history else [0] * len(prices)
            
            # Price momentum (rate of change)
            if len(prices) >= 5:
                price_momentum = (prices[-1] - prices[-6]) / prices[-6] if prices[-6] != 0 else 0
                features.append(price_momentum)
            else:
                features.append(0.0)
            
            # Volume momentum
            if len(volumes) >= 5 and volumes[-6] != 0:
                volume_momentum = (volumes[-1] - volumes[-6]) / volumes[-6]
                features.append(volume_momentum)
            else:
                features.append(0.0)
            
            # Price-volume correlation
            if len(prices) >= 10 and len(volumes) >= 10:
                correlation = np.corrcoef(prices[-10:], volumes[-10:])[0, 1]
                features.append(correlation if not np.isnan(correlation) else 0.0)
            else:
                features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Momentum feature extraction error: {e}")
            return [0.0] * 3
    
    def _extract_market_features(self, market_data: Dict[str, Any]) -> List[float]:
        """Extract market-wide features."""
        try:
            features = []
            
            # Market cap
            market_cap = market_data.get('market_cap', 0)
            features.append(np.log(market_cap + 1))  # Log transform
            
            # Liquidity
            liquidity = market_data.get('liquidity_usd', 0)
            features.append(np.log(liquidity + 1))
            
            # Trading volume
            volume_24h = market_data.get('volume_24h', 0)
            features.append(np.log(volume_24h + 1))
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Market feature extraction error: {e}")
            return [0.0] * 3
    
    async def _calculate_rsi_simple(self, prices: List[float], period: int = 14) -> float:
        """Calculate simple RSI."""
        try:
            if len(prices) < period + 1:
                return 50.0
            
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
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        try:
            if len(prices) < period:
                return np.mean(prices)
            
            multiplier = 2 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
            
        except Exception:
            return prices[-1] if prices else 0.0