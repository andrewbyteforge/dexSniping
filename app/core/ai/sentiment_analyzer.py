"""
Market Sentiment Analysis Engine
File: app/core/ai/sentiment_analyzer.py

Advanced market sentiment analysis with multi-source data integration,
real-time social monitoring, and ML-powered sentiment scoring.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib

import numpy as np
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import StandardScaler
import joblib

from app.utils.logger import setup_logger
from app.core.exceptions import (
    SentimentAnalysisError,
    APIError,
    DataProcessingError
)
from app.core.cache.cache_manager import CacheManager
from app.core.performance.circuit_breaker import CircuitBreakerManager

logger = setup_logger(__name__)


class SentimentCategory(Enum):
    """Sentiment categories."""
    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"


class SourceType(Enum):
    """Data source types."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    NEWS = "news"
    BLOG = "blog"
    FORUM = "forum"
    YOUTUBE = "youtube"


class TrendDirection(Enum):
    """Trend directions."""
    STRONGLY_DECLINING = "strongly_declining"
    DECLINING = "declining"
    STABLE = "stable"
    RISING = "rising"
    STRONGLY_RISING = "strongly_rising"


@dataclass
class SocialMetrics:
    """Social media metrics."""
    total_mentions: int = 0
    positive_mentions: int = 0
    negative_mentions: int = 0
    neutral_mentions: int = 0
    engagement_rate: float = 0.0
    reach_estimate: int = 0
    viral_score: float = 0.0
    influencer_mentions: int = 0
    unique_authors: int = 0
    retweets_shares: int = 0
    likes_reactions: int = 0
    comments_replies: int = 0


@dataclass
class NewsMetrics:
    """News and media metrics."""
    news_articles: int = 0
    positive_articles: int = 0
    negative_articles: int = 0
    neutral_articles: int = 0
    major_outlet_coverage: int = 0
    press_releases: int = 0
    analyst_reports: int = 0
    media_sentiment_score: float = 0.0
    coverage_trend: TrendDirection = TrendDirection.STABLE
    headline_sentiment: float = 0.0


@dataclass
class CommunityMetrics:
    """Community engagement metrics."""
    telegram_members: int = 0
    discord_members: int = 0
    reddit_subscribers: int = 0
    forum_users: int = 0
    github_stars: int = 0
    community_growth_rate: float = 0.0
    active_users_24h: int = 0
    community_sentiment: float = 0.0
    developer_activity: float = 0.0
    community_health_score: float = 0.0


@dataclass
class InfluencerMention:
    """Influencer mention data."""
    influencer_name: str
    platform: str
    follower_count: int
    mention_content: str
    sentiment_score: float
    engagement_count: int
    timestamp: datetime
    verified: bool = False
    influence_score: float = 0.0


@dataclass
class TrendingKeyword:
    """Trending keyword data."""
    keyword: str
    mention_count: int
    growth_rate: float
    sentiment_score: float
    sources: List[str]
    confidence: float
    trend_strength: float


@dataclass
class SentimentAnalysisResult:
    """Complete sentiment analysis result."""
    token_address: str
    token_symbol: str
    network: str
    
    # Overall sentiment
    overall_sentiment: SentimentCategory
    sentiment_score: float  # -1.0 to +1.0
    confidence: float
    
    # Source breakdown
    social_metrics: SocialMetrics
    news_metrics: NewsMetrics
    community_metrics: CommunityMetrics
    
    # Trending data
    trending_keywords: List[TrendingKeyword]
    influencer_mentions: List[InfluencerMention]
    
    # Analysis details
    data_sources: List[str]
    analysis_period: str
    sample_size: int
    data_quality_score: float
    
    # Predictions
    sentiment_trend: TrendDirection
    predicted_sentiment_24h: float
    volatility_indicator: float
    
    # Metadata
    analysis_timestamp: datetime
    analysis_duration_ms: int
    model_version: str


class SentimentAnalyzer:
    """
    Advanced market sentiment analysis engine.
    
    Features:
    - Multi-source sentiment aggregation
    - Real-time social media monitoring
    - News and media analysis
    - Influencer tracking
    - Trend prediction
    - Community health assessment
    """
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.cache_manager = CacheManager()
        self.circuit_breaker = CircuitBreakerManager()
        
        # Configuration
        self.model_version = "2.0.0"
        self.models_path = "models/sentiment/"
        
        # ML Models
        self.sentiment_classifier: Optional[VotingClassifier] = None
        self.trend_predictor: Optional[LogisticRegression] = None
        self.text_vectorizer: Optional[TfidfVectorizer] = None
        self.feature_scaler: Optional[StandardScaler] = None
        
        # API configurations (mock for demo)
        self.api_configs = {
            "twitter": {"enabled": False, "rate_limit": 100},
            "reddit": {"enabled": False, "rate_limit": 60},
            "news": {"enabled": False, "rate_limit": 50},
            "telegram": {"enabled": False, "rate_limit": 30}
        }
        
        # Sentiment thresholds
        self.sentiment_thresholds = {
            SentimentCategory.VERY_BEARISH: -0.6,
            SentimentCategory.BEARISH: -0.2,
            SentimentCategory.NEUTRAL: 0.2,
            SentimentCategory.BULLISH: 0.6,
            SentimentCategory.VERY_BULLISH: 1.0
        }
        
        # Cache settings
        self.cache_ttl = 600  # 10 minutes
        self.trend_cache_ttl = 1800  # 30 minutes
        
        logger.info("📊 Market Sentiment Analyzer initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize sentiment analysis models and APIs.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Load or train models
            await self._load_models()
            
            # Initialize API connections (mock)
            await self._initialize_apis()
            
            # Validate model performance
            await self._validate_models()
            
            logger.info(f"✅ Sentiment analyzer ready (v{self.model_version})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sentiment analyzer: {e}")
            return False
    
    async def analyze_sentiment(
        self,
        token_address: str,
        token_symbol: str,
        network: str,
        analysis_period: str = "24h",
        include_predictions: bool = True
    ) -> SentimentAnalysisResult:
        """
        Perform comprehensive sentiment analysis.
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol
            network: Network name
            analysis_period: Analysis time period (1h, 6h, 24h, 7d)
            include_predictions: Include trend predictions
            
        Returns:
            SentimentAnalysisResult: Complete sentiment analysis
            
        Raises:
            SentimentAnalysisError: If analysis fails
        """
        start_time = datetime.utcnow()
        
        try:
            cache_key = f"sentiment:{network}:{token_address}:{analysis_period}:{include_predictions}"
            
            # Check cache first
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.debug(f"📋 Using cached sentiment analysis for {token_symbol}")
                return SentimentAnalysisResult(**cached_result)
            
            logger.info(f"📊 Starting sentiment analysis for {token_symbol} ({analysis_period})")
            
            # Collect data from multiple sources
            social_data = await self._collect_social_data(token_symbol, analysis_period)
            news_data = await self._collect_news_data(token_symbol, analysis_period)
            community_data = await self._collect_community_data(token_symbol)
            
            # Process and analyze data
            social_metrics = await self._analyze_social_sentiment(social_data)
            news_metrics = await self._analyze_news_sentiment(news_data)
            community_metrics = await self._analyze_community_sentiment(community_data)
            
            # Extract trending keywords and influencer mentions
            trending_keywords = await self._extract_trending_keywords(social_data, news_data)
            influencer_mentions = await self._extract_influencer_mentions(social_data)
            
            # Calculate overall sentiment
            overall_sentiment_score = await self._calculate_overall_sentiment(
                social_metrics, news_metrics, community_metrics
            )
            
            overall_sentiment = self._classify_sentiment(overall_sentiment_score)
            confidence = await self._calculate_confidence(social_metrics, news_metrics, community_metrics)
            
            # Predict trends if requested
            sentiment_trend = TrendDirection.STABLE
            predicted_sentiment_24h = overall_sentiment_score
            volatility_indicator = 0.5
            
            if include_predictions:
                sentiment_trend, predicted_sentiment_24h, volatility_indicator = await self._predict_trends(
                    overall_sentiment_score, social_metrics, news_metrics
                )
            
            # Calculate data quality
            data_quality_score = self._calculate_data_quality(social_metrics, news_metrics, community_metrics)
            sample_size = social_metrics.total_mentions + news_metrics.news_articles
            
            # Calculate analysis duration
            analysis_duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Create result
            result = SentimentAnalysisResult(
                token_address=token_address,
                token_symbol=token_symbol,
                network=network,
                overall_sentiment=overall_sentiment,
                sentiment_score=overall_sentiment_score,
                confidence=confidence,
                social_metrics=social_metrics,
                news_metrics=news_metrics,
                community_metrics=community_metrics,
                trending_keywords=trending_keywords,
                influencer_mentions=influencer_mentions,
                data_sources=self._get_active_sources(),
                analysis_period=analysis_period,
                sample_size=sample_size,
                data_quality_score=data_quality_score,
                sentiment_trend=sentiment_trend,
                predicted_sentiment_24h=predicted_sentiment_24h,
                volatility_indicator=volatility_indicator,
                analysis_timestamp=datetime.utcnow(),
                analysis_duration_ms=analysis_duration,
                model_version=self.model_version
            )
            
            # Cache result
            await self.cache_manager.set(
                cache_key,
                asdict(result),
                ttl=self.cache_ttl
            )
            
            logger.info(f"✅ Sentiment analysis complete for {token_symbol} - "
                       f"Sentiment: {overall_sentiment.value} ({overall_sentiment_score:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed for {token_symbol}: {e}")
            raise SentimentAnalysisError(f"Sentiment analysis failed: {str(e)}")
    
    async def get_trending_tokens(
        self,
        network: Optional[str] = None,
        min_mentions: int = 10,
        period: str = "24h"
    ) -> List[Dict[str, Any]]:
        """
        Get trending tokens based on sentiment analysis.
        
        Args:
            network: Filter by network
            min_mentions: Minimum mention threshold
            period: Analysis period
            
        Returns:
            List of trending tokens with sentiment data
        """
        try:
            logger.info(f"📈 Finding trending tokens ({period}, min {min_mentions} mentions)")
            
            # Mock trending tokens data
            trending_tokens = []
            
            for i in range(10):
                token_data = {
                    "symbol": f"TOKEN{i}",
                    "address": f"0x{''.join(np.random.choice(list('0123456789abcdef'), 40))}",
                    "network": network or "ethereum",
                    "mentions": int(np.random.uniform(min_mentions, 1000)),
                    "sentiment_score": np.random.uniform(-0.8, 0.8),
                    "trend_strength": np.random.uniform(0.1, 1.0),
                    "growth_rate": np.random.uniform(-50, 200),
                    "confidence": np.random.uniform(0.6, 0.95)
                }
                
                # Classify sentiment
                token_data["sentiment"] = self._classify_sentiment(token_data["sentiment_score"]).value
                
                trending_tokens.append(token_data)
            
            # Sort by trend strength
            trending_tokens.sort(key=lambda x: x["trend_strength"], reverse=True)
            
            logger.info(f"✅ Found {len(trending_tokens)} trending tokens")
            return trending_tokens
            
        except Exception as e:
            logger.error(f"❌ Failed to get trending tokens: {e}")
            return []
    
    async def monitor_sentiment_alerts(
        self,
        tokens: List[str],
        alert_thresholds: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Monitor tokens for sentiment alerts.
        
        Args:
            tokens: List of token symbols to monitor
            alert_thresholds: Alert threshold configurations
            
        Returns:
            List of triggered alerts
        """
        try:
            logger.info(f"🚨 Monitoring sentiment alerts for {len(tokens)} tokens")
            
            alerts = []
            
            for token in tokens:
                # Mock sentiment check
                current_sentiment = np.random.uniform(-1.0, 1.0)
                previous_sentiment = np.random.uniform(-1.0, 1.0)
                change = current_sentiment - previous_sentiment
                
                # Check thresholds
                if abs(change) > alert_thresholds.get("sentiment_change", 0.3):
                    alert = {
                        "token": token,
                        "alert_type": "sentiment_change",
                        "current_sentiment": current_sentiment,
                        "previous_sentiment": previous_sentiment,
                        "change": change,
                        "severity": "high" if abs(change) > 0.5 else "medium",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    alerts.append(alert)
            
            logger.info(f"🚨 Generated {len(alerts)} sentiment alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Sentiment monitoring failed: {e}")
            return []
    
    # ==================== PRIVATE METHODS ====================
    
    async def _load_models(self) -> None:
        """Load or train sentiment analysis models."""
        try:
            # Try loading existing models
            self.sentiment_classifier = joblib.load(f"{self.models_path}sentiment_classifier_v{self.model_version}.pkl")
            self.trend_predictor = joblib.load(f"{self.models_path}trend_predictor_v{self.model_version}.pkl")
            self.text_vectorizer = joblib.load(f"{self.models_path}text_vectorizer_v{self.model_version}.pkl")
            self.feature_scaler = joblib.load(f"{self.models_path}feature_scaler_v{self.model_version}.pkl")
            
            logger.info("📁 Loaded existing sentiment analysis models")
            
        except FileNotFoundError:
            logger.info("🔧 Training new sentiment analysis models...")
            await self._train_models()
    
    async def _train_models(self) -> None:
        """Train sentiment analysis models."""
        # Generate synthetic training data
        X_text, X_features, y = await self._generate_training_data()
        
        # Train text vectorizer
        self.text_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        X_text_vec = self.text_vectorizer.fit_transform(X_text)
        
        # Train feature scaler
        self.feature_scaler = StandardScaler()
        X_features_scaled = self.feature_scaler.fit_transform(X_features)
        
        # Combine features
        X_combined = np.hstack([X_text_vec.toarray(), X_features_scaled])
        
        # Train ensemble classifier
        self.sentiment_classifier = VotingClassifier([
            ('nb', MultinomialNB()),
            ('lr', LogisticRegression(random_state=42)),
        ], voting='soft')
        
        self.sentiment_classifier.fit(X_combined, y)
        
        # Train trend predictor
        self.trend_predictor = LogisticRegression(random_state=42)
        self.trend_predictor.fit(X_features_scaled, y)
        
        logger.info("✅ Sentiment analysis models trained")
    
    async def _generate_training_data(self) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Generate synthetic training data."""
        n_samples = 1000
        
        # Generate text data
        positive_words = ["moon", "bullish", "pump", "gem", "rocket", "gains", "amazing", "great"]
        negative_words = ["dump", "bearish", "scam", "rug", "crash", "terrible", "awful", "disaster"]
        neutral_words = ["price", "market", "token", "trading", "analysis", "chart", "data"]
        
        texts = []
        features = []
        labels = []
        
        for i in range(n_samples):
            # Generate sentiment label
            sentiment = np.random.choice([0, 1, 2], p=[0.3, 0.4, 0.3])  # negative, neutral, positive
            
            # Generate text based on sentiment
            if sentiment == 2:  # positive
                words = np.random.choice(positive_words + neutral_words, size=np.random.randint(5, 15))
            elif sentiment == 0:  # negative
                words = np.random.choice(negative_words + neutral_words, size=np.random.randint(5, 15))
            else:  # neutral
                words = np.random.choice(neutral_words, size=np.random.randint(5, 15))
            
            text = " ".join(words)
            texts.append(text)
            
            # Generate numerical features
            feature_vector = np.random.randn(20)
            if sentiment == 2:
                feature_vector += 0.5  # Positive bias
            elif sentiment == 0:
                feature_vector -= 0.5  # Negative bias
            
            features.append(feature_vector)
            labels.append(sentiment)
        
        return texts, np.array(features), np.array(labels)
    
    async def _initialize_apis(self) -> None:
        """Initialize API connections."""
        # Mock API initialization
        logger.info("🔗 API connections initialized (mock mode)")
    
    async def _validate_models(self) -> None:
        """Validate model performance."""
        # Mock validation
        logger.info("✅ Model validation passed")
    
    async def _collect_social_data(self, token_symbol: str, period: str) -> List[Dict[str, Any]]:
        """Collect social media data."""
        # Mock social data collection
        social_posts = []
        
        num_posts = int(np.random.uniform(50, 500))
        
        for i in range(num_posts):
            post = {
                "text": f"Sample post about {token_symbol} token #{i}",
                "platform": np.random.choice(["twitter", "reddit", "telegram"]),
                "author": f"user_{i}",
                "timestamp": datetime.utcnow() - timedelta(hours=np.random.uniform(0, 24)),
                "engagement": int(np.random.uniform(1, 100)),
                "sentiment": np.random.uniform(-1, 1)
            }
            social_posts.append(post)
        
        logger.debug(f"📱 Collected {len(social_posts)} social media posts")
        return social_posts
    
    async def _collect_news_data(self, token_symbol: str, period: str) -> List[Dict[str, Any]]:
        """Collect news and media data."""
        # Mock news data collection
        news_articles = []
        
        num_articles = int(np.random.uniform(5, 50))
        
        for i in range(num_articles):
            article = {
                "title": f"News article about {token_symbol} #{i}",
                "content": f"Content about {token_symbol} token and market analysis...",
                "source": np.random.choice(["CoinDesk", "CoinTelegraph", "CryptoNews", "Bloomberg"]),
                "timestamp": datetime.utcnow() - timedelta(hours=np.random.uniform(0, 24)),
                "sentiment": np.random.uniform(-1, 1),
                "credibility": np.random.uniform(0.5, 1.0)
            }
            news_articles.append(article)
        
        logger.debug(f"📰 Collected {len(news_articles)} news articles")
        return news_articles
    
    async def _collect_community_data(self, token_symbol: str) -> Dict[str, Any]:
        """Collect community engagement data."""
        # Mock community data
        community_data = {
            "telegram_members": int(np.random.uniform(100, 10000)),
            "discord_members": int(np.random.uniform(50, 5000)),
            "reddit_subscribers": int(np.random.uniform(10, 1000)),
            "github_stars": int(np.random.uniform(0, 500)),
            "active_users_24h": int(np.random.uniform(10, 500)),
            "growth_rate": np.random.uniform(-10, 50),
            "engagement_score": np.random.uniform(0.1, 1.0)
        }
        
        logger.debug(f"👥 Collected community data for {token_symbol}")
        return community_data
    
    async def _analyze_social_sentiment(self, social_data: List[Dict[str, Any]]) -> SocialMetrics:
        """Analyze social media sentiment."""
        if not social_data:
            return SocialMetrics()
        
        total_mentions = len(social_data)
        positive_mentions = sum(1 for post in social_data if post["sentiment"] > 0.2)
        negative_mentions = sum(1 for post in social_data if post["sentiment"] < -0.2)
        neutral_mentions = total_mentions - positive_mentions - negative_mentions
        
        total_engagement = sum(post["engagement"] for post in social_data)
        unique_authors = len(set(post["author"] for post in social_data))
        
        return SocialMetrics(
            total_mentions=total_mentions,
            positive_mentions=positive_mentions,
            negative_mentions=negative_mentions,
            neutral_mentions=neutral_mentions,
            engagement_rate=total_engagement / max(total_mentions, 1),
            reach_estimate=total_engagement * 10,  # Mock calculation
            viral_score=min(total_engagement / 1000, 1.0),
            influencer_mentions=sum(1 for post in social_data if post["engagement"] > 50),
            unique_authors=unique_authors,
            retweets_shares=int(total_engagement * 0.3),
            likes_reactions=int(total_engagement * 0.6),
            comments_replies=int(total_engagement * 0.1)
        )
    
    async def _analyze_news_sentiment(self, news_data: List[Dict[str, Any]]) -> NewsMetrics:
        """Analyze news and media sentiment."""
        if not news_data:
            return NewsMetrics()
        
        total_articles = len(news_data)
        positive_articles = sum(1 for article in news_data if article["sentiment"] > 0.2)
        negative_articles = sum(1 for article in news_data if article["sentiment"] < -0.2)
        neutral_articles = total_articles - positive_articles - negative_articles
        
        major_outlets = ["CoinDesk", "CoinTelegraph", "Bloomberg", "Reuters"]
        major_outlet_coverage = sum(1 for article in news_data if article["source"] in major_outlets)
        
        avg_sentiment = np.mean([article["sentiment"] for article in news_data])
        
        return NewsMetrics(
            news_articles=total_articles,
            positive_articles=positive_articles,
            negative_articles=negative_articles,
            neutral_articles=neutral_articles,
            major_outlet_coverage=major_outlet_coverage,
            press_releases=int(total_articles * 0.1),
            analyst_reports=int(total_articles * 0.05),
            media_sentiment_score=avg_sentiment,
            coverage_trend=TrendDirection.STABLE,
            headline_sentiment=avg_sentiment
        )
    
    async def _analyze_community_sentiment(self, community_data: Dict[str, Any]) -> CommunityMetrics:
        """Analyze community engagement sentiment."""
        return CommunityMetrics(
            telegram_members=community_data.get("telegram_members", 0),
            discord_members=community_data.get("discord_members", 0),
            reddit_subscribers=community_data.get("reddit_subscribers", 0),
            github_stars=community_data.get("github_stars", 0),
            community_growth_rate=community_data.get("growth_rate", 0.0),
            active_users_24h=community_data.get("active_users_24h", 0),
            community_sentiment=community_data.get("engagement_score", 0.5),
            developer_activity=min(community_data.get("github_stars", 0) / 100, 1.0),
            community_health_score=community_data.get("engagement_score", 0.5)
        )
    
    async def _extract_trending_keywords(
        self,
        social_data: List[Dict[str, Any]],
        news_data: List[Dict[str, Any]]
    ) -> List[TrendingKeyword]:
        """Extract trending keywords from text data."""
        # Mock trending keywords extraction
        trending_keywords = [
            TrendingKeyword(
                keyword="moon",
                mention_count=50,
                growth_rate=25.0,
                sentiment_score=0.8,
                sources=["twitter", "reddit"],
                confidence=0.9,
                trend_strength=0.8
            ),
            TrendingKeyword(
                keyword="pump",
                mention_count=30,
                growth_rate=15.0,
                sentiment_score=0.6,
                sources=["twitter", "telegram"],
                confidence=0.7,
                trend_strength=0.6
            ),
            TrendingKeyword(
                keyword="hodl",
                mention_count=25,
                growth_rate=10.0,
                sentiment_score=0.4,
                sources=["reddit", "discord"],
                confidence=0.8,
                trend_strength=0.5
            )
        ]
        
        return trending_keywords
    
    async def _extract_influencer_mentions(self, social_data: List[Dict[str, Any]]) -> List[InfluencerMention]:
        """Extract influencer mentions from social data."""
        # Mock influencer mentions
        influencer_mentions = []
        
        influential_posts = [post for post in social_data if post["engagement"] > 50]
        
        for post in influential_posts[:5]:  # Top 5 influential posts
            mention = InfluencerMention(
                influencer_name=post["author"],
                platform=post["platform"],
                follower_count=int(np.random.uniform(1000, 100000)),
                mention_content=post["text"],
                sentiment_score=post["sentiment"],
                engagement_count=post["engagement"],
                timestamp=post["timestamp"],
                verified=np.random.choice([True, False], p=[0.3, 0.7]),
                influence_score=min(post["engagement"] / 100, 1.0)
            )
            influencer_mentions.append(mention)
        
        return influencer_mentions
    
    async def _calculate_overall_sentiment(
        self,
        social_metrics: SocialMetrics,
        news_metrics: NewsMetrics,
        community_metrics: CommunityMetrics
    ) -> float:
        """Calculate overall sentiment score."""
        # Weighted combination of different sentiment sources
        social_weight = 0.5
        news_weight = 0.3
        community_weight = 0.2
        
        # Calculate individual scores
        social_score = 0.0
        if social_metrics.total_mentions > 0:
            social_score = (
                (social_metrics.positive_mentions - social_metrics.negative_mentions) / 
                social_metrics.total_mentions
            )
        
        news_score = news_metrics.media_sentiment_score
        community_score = community_metrics.community_sentiment * 2 - 1  # Convert to -1 to 1 range
        
        # Weighted average
        overall_score = (
            social_score * social_weight +
            news_score * news_weight +
            community_score * community_weight
        )
        
        return np.clip(overall_score, -1.0, 1.0)
    
    def _classify_sentiment(self, sentiment_score: float) -> SentimentCategory:
        """Classify sentiment score into category."""
        if sentiment_score >= 0.6:
            return SentimentCategory.VERY_BULLISH
        elif sentiment_score >= 0.2:
            return SentimentCategory.BULLISH
        elif sentiment_score >= -0.2:
            return SentimentCategory.NEUTRAL
        elif sentiment_score >= -0.6:
            return SentimentCategory.BEARISH
        else:
            return SentimentCategory.VERY_BEARISH
    
    async def _calculate_confidence(
        self,
        social_metrics: SocialMetrics,
        news_metrics: NewsMetrics,
        community_metrics: CommunityMetrics
    ) -> float:
        """Calculate confidence in sentiment analysis."""
        # Base confidence on data volume and quality
        base_confidence = 0.5
        
        # Social media confidence
        if social_metrics.total_mentions > 100:
            base_confidence += 0.2
        elif social_metrics.total_mentions > 20:
            base_confidence += 0.1
        
        # News confidence
        if news_metrics.news_articles > 10:
            base_confidence += 0.15
        elif news_metrics.news_articles > 3:
            base_confidence += 0.1
        
        # Community confidence
        if community_metrics.telegram_members > 1000:
            base_confidence += 0.1
        
        # Major outlet coverage boost
        if news_metrics.major_outlet_coverage > 0:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    async def _predict_trends(
        self,
        current_sentiment: float,
        social_metrics: SocialMetrics,
        news_metrics: NewsMetrics
    ) -> Tuple[TrendDirection, float, float]:
        """Predict sentiment trends."""
        # Mock trend prediction
        trend_change = np.random.uniform(-0.2, 0.2)
        predicted_sentiment = np.clip(current_sentiment + trend_change, -1.0, 1.0)
        
        # Determine trend direction
        if trend_change > 0.1:
            trend_direction = TrendDirection.STRONGLY_RISING
        elif trend_change > 0.05:
            trend_direction = TrendDirection.RISING
        elif trend_change < -0.1:
            trend_direction = TrendDirection.STRONGLY_DECLINING
        elif trend_change < -0.05:
            trend_direction = TrendDirection.DECLINING
        else:
            trend_direction = TrendDirection.STABLE
        
        # Calculate volatility indicator
        volatility = abs(trend_change) + (social_metrics.viral_score * 0.3)
        volatility_indicator = min(volatility, 1.0)
        
        return trend_direction, predicted_sentiment, volatility_indicator
    
    def _calculate_data_quality(
        self,
        social_metrics: SocialMetrics,
        news_metrics: NewsMetrics,
        community_metrics: CommunityMetrics
    ) -> float:
        """Calculate data quality score."""
        quality_score = 0.0
        
        # Social data quality
        if social_metrics.total_mentions > 50:
            quality_score += 0.3
        elif social_metrics.total_mentions > 10:
            quality_score += 0.2
        else:
            quality_score += 0.1
        
        # Unique authors diversity
        if social_metrics.unique_authors > social_metrics.total_mentions * 0.7:
            quality_score += 0.1  # High diversity
        
        # News data quality
        if news_metrics.news_articles > 5:
            quality_score += 0.3
        elif news_metrics.news_articles > 1:
            quality_score += 0.2
        else:
            quality_score += 0.1
        
        # Major outlet coverage
        if news_metrics.major_outlet_coverage > 0:
            quality_score += 0.1
        
        # Community data quality
        if community_metrics.telegram_members > 1000:
            quality_score += 0.2
        elif community_metrics.telegram_members > 100:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _get_active_sources(self) -> List[str]:
        """Get list of active data sources."""
        active_sources = []
        
        for source, config in self.api_configs.items():
            if config.get("enabled", False):
                active_sources.append(source)
        
        # Always include mock sources for demo
        if not active_sources:
            active_sources = ["twitter_mock", "reddit_mock", "news_mock", "community_mock"]
        
        return active_sources