"""
Enhanced Exceptions Module
File: app/core/exceptions.py

Comprehensive exception classes for the DEX Sniper Pro trading bot.
"""

class DexSnipingException(Exception):
    """Base exception for DEX sniping operations."""
    pass

class TradingError(DexSnipingException):
    """Exception raised when trading operations fail."""
    pass

class ConfigurationError(DexSnipingException):
    """Exception raised when configuration is invalid."""
    pass

class WalletError(DexSnipingException):
    """Exception raised when wallet operations fail."""
    pass

class NetworkError(DexSnipingException):
    """Exception raised when network operations fail."""
    pass

class DatabaseError(DexSnipingException):
    """Exception raised when database operations fail."""
    pass

class ValidationError(DexSnipingException):
    """Exception raised when data validation fails."""
    pass

# AI and Analysis Exceptions
class AIAnalysisError(DexSnipingException):
    """Exception raised when AI analysis operations fail."""
    pass

class HoneypotDetectionError(AIAnalysisError):
    """Exception raised when honeypot detection fails."""
    pass

class RiskAssessmentError(AIAnalysisError):
    """Exception raised when risk assessment fails."""
    pass

class ModelLoadError(AIAnalysisError):
    """Exception raised when ML model loading fails."""
    pass

# Strategy and Trading Exceptions
class StrategyExecutionError(TradingError):
    """Exception raised when strategy execution fails."""
    pass

class OrderExecutionError(TradingError):
    """Exception raised when order execution fails."""
    pass

class InsufficientFundsError(TradingError):
    """Exception raised when insufficient funds for trading."""
    pass

# Multi-chain and WebSocket Exceptions
class MultiChainError(DexSnipingException):
    """Exception raised when multi-chain operations fail."""
    pass

class WebSocketError(DexSnipingException):
    """Exception raised when WebSocket operations fail."""
    pass

class ChainConnectionException(NetworkError):
    """Exception raised when blockchain connection fails."""
    pass

# Backwards compatibility aliases
TokenScannerError = DexSnipingException
ContractAnalysisError = AIAnalysisError


# DEX and Trading Related Exceptions
class DEXError(DexSnipingException):
    """Exception raised when DEX operations fail."""
    pass

class SwapError(DEXError):
    """Exception raised when swap operations fail."""
    pass

class LiquidityError(DEXError):
    """Exception raised when liquidity operations fail."""
    pass

class SlippageError(DEXError):
    """Exception raised when slippage is too high."""
    pass

class PriceError(DEXError):
    """Exception raised when price operations fail."""
    pass

class PoolError(DEXError):
    """Exception raised when pool operations fail."""
    pass
