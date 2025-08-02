"""
Custom exception classes for the DEX sniping application.
Provides specific exception types for different error scenarios.
"""

from typing import Optional


class DexSnipingException(Exception):
    """Base exception class for all DEX sniping application errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ChainConnectionException(DexSnipingException):
    """Exception raised when blockchain connection fails."""
    pass


class ChainNotSupportedException(DexSnipingException):
    """Exception raised when requested blockchain is not supported."""
    pass


class TokenNotFoundError(DexSnipingException):
    """Exception raised when token information cannot be found."""
    pass


class TradingException(DexSnipingException):
    """Base exception for trading-related errors."""
    pass


class APIException(DexSnipingException):
    """Base exception for external API errors."""
    pass


class ValidationError(DexSnipingException):
    """Exception raised when data validation fails."""
    pass