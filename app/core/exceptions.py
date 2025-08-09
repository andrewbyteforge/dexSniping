"""
Complete Exception System for Phase 4C
File: app/core/exceptions.py
"""

from typing import Optional, Dict, Any


class DEXSniperError(Exception):
    """Base exception class for DEX Sniper Pro."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


# All required exception classes for Phase 4C
class TradingError(DEXSniperError):
    """Trading-related exceptions."""
    pass

class ValidationError(DEXSniperError):
    """Validation exceptions."""
    pass

class NetworkError(DEXSniperError):
    """Network exceptions."""
    pass

class ServiceError(DEXSniperError):
    """Service exceptions."""
    pass

class AIAnalysisError(DEXSniperError):
    """AI analysis exceptions."""
    pass

class TradingStrategyError(DEXSniperError):
    """Trading strategy exceptions."""
    pass

class ModelPredictionError(DEXSniperError):
    """ML model prediction exceptions."""
    pass

class DataInsufficientError(DEXSniperError):
    """Insufficient data exceptions."""
    pass

class ModelLoadError(DEXSniperError):
    """Model loading exceptions."""
    pass

class HoneypotDetectionError(DEXSniperError):
    """Honeypot detection exceptions."""
    pass

class ContractAnalysisError(DEXSniperError):
    """Contract analysis exceptions."""
    pass

class SentimentAnalysisError(DEXSniperError):
    """Sentiment analysis exceptions."""
    pass

class PredictionError(DEXSniperError):
    """Prediction exceptions."""
    pass

class StrategyExecutionError(DEXSniperError):
    """Strategy execution exceptions."""
    pass

class ExecutionTimeoutError(DEXSniperError):
    """Execution timeout exceptions."""
    pass

class PerformanceOptimizationError(DEXSniperError):
    """Performance optimization exceptions."""
    pass

class BacktestingError(DEXSniperError):
    """Backtesting exceptions."""
    pass

class ExecutionError(DEXSniperError):
    """Execution exceptions."""
    pass

class WebSocketManagerError(DEXSniperError):
    """WebSocket manager exceptions."""
    pass

class RealTimeDataError(DEXSniperError):
    """Real-time data exceptions."""
    pass

class BroadcastError(DEXSniperError):
    """Broadcast exceptions."""
    pass

class ConnectionManagerError(DEXSniperError):
    """Connection manager exceptions."""
    pass

class RiskAssessmentError(DEXSniperError):
    """Risk assessment exceptions."""
    pass

class MarketDataError(DEXSniperError):
    """Market data exceptions."""
    pass

class PriceDataError(DEXSniperError):
    """Price data exceptions."""
    pass

class IndicatorError(DEXSniperError):
    """Indicator exceptions."""
    pass

class AnalysisError(DEXSniperError):
    """Analysis exceptions."""
    pass

class DiscoveryError(DEXSniperError):
    """Discovery exceptions."""
    pass

class InvalidTokenError(DEXSniperError):
    """Invalid token exceptions."""
    pass

class TokenError(DEXSniperError):
    """Token exceptions."""
    pass

class ContractError(DEXSniperError):
    """Contract exceptions."""
    pass

# Backward compatibility
DexSnipingException = DEXSniperError
