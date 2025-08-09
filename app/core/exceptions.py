"""
DEX Sniper Pro Exception System
File: app/core/exceptions.py

Comprehensive exception handling for the trading bot.
"""


class DEXSniperError(Exception):
    """Base exception class for DEX Sniper Pro."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """Initialize exception with message, code, and details."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        
    def __str__(self):
        return f"{self.error_code}: {self.message}"


# ==================== SECURITY EXCEPTIONS ====================

class SecurityError(DEXSniperError):
    """Exception for security-related issues."""
    pass


class AuthenticationError(DEXSniperError):
    """Exception for authentication failures."""
    pass


class AuthorizationError(DEXSniperError):
    """Exception for authorization failures."""
    pass


class ValidationError(DEXSniperError):
    """Exception for data validation failures."""
    pass


class AccessDeniedError(SecurityError):
    """Exception for access denied scenarios."""
    pass


class CredentialError(AuthenticationError):
    """Exception for credential-related issues."""
    pass


# ==================== WALLET EXCEPTIONS ====================

class WalletError(DEXSniperError):
    """Base class for wallet-related errors."""
    pass


class WalletConnectionError(WalletError):
    """Exception for wallet connection failures."""
    pass


class InsufficientFundsError(WalletError):
    """Exception for insufficient wallet funds."""
    pass


class InvalidAddressError(WalletError):
    """Exception for invalid wallet addresses."""
    pass


# ==================== TRADING EXCEPTIONS ====================

class TradingError(DEXSniperError):
    """Base class for trading-related errors."""
    pass


class OrderExecutionError(TradingError):
    """Exception for order execution failures."""
    pass


class RiskLimitExceededError(TradingError):
    """Exception for risk limit violations."""
    pass


# ==================== NETWORK EXCEPTIONS ====================

class NetworkError(DEXSniperError):
    """Base class for network-related errors."""
    pass


class ConnectionError(NetworkError):
    """Exception for network connection issues."""
    pass


class RPCError(NetworkError):
    """Exception for RPC communication errors."""
    pass


# ==================== SERVICE EXCEPTIONS ====================

class ServiceError(DEXSniperError):
    """Base class for service-level errors."""
    pass


class ServiceUnavailableError(ServiceError):
    """Exception for unavailable services."""
    pass


class ConfigurationError(ServiceError):
    """Exception for configuration issues."""
    pass


class InitializationError(ServiceError):
    """Exception for initialization failures."""
    pass


# ==================== DATA EXCEPTIONS ====================

class DataError(DEXSniperError):
    """Base class for data-related errors."""
    pass


class ParseError(DataError):
    """Exception for data parsing failures."""
    pass


class FormatError(DataError):
    """Exception for data format issues."""
    pass


# Export all exceptions


# ==================== ADDITIONAL EXCEPTIONS ====================

class RateLimitError(DEXSniperError):
    """Exception for rate limiting violations."""
    pass


class TimeoutError(DEXSniperError):
    """Exception for operation timeouts."""
    pass


class APIError(DEXSniperError):
    """Exception for API-related errors."""
    pass


__all__ = [
    'DEXSniperError',
    'SecurityError', 'AuthenticationError', 'AuthorizationError', 
    'ValidationError', 'AccessDeniedError', 'CredentialError',
    'WalletError', 'WalletConnectionError', 'InsufficientFundsError', 'InvalidAddressError',
    'TradingError', 'OrderExecutionError', 'RiskLimitExceededError',
    'NetworkError', 'ConnectionError', 'RPCError',
    'ServiceError', 'ServiceUnavailableError', 'ConfigurationError', 'InitializationError',
    'DataError', 'ParseError', 'FormatError',
    'RateLimitError', 'TimeoutError', 'APIError'
]
