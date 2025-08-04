"""
Core Exception Classes - Phase 4B
File: app/core/exceptions.py

Custom exception classes for the DEX Sniper Pro trading bot with
comprehensive error handling for all system components.
"""

from typing import Optional, Dict, Any


class DEXSniperError(Exception):
    """Base exception class for DEX Sniper Pro."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize DEX Sniper error.
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


# Wallet-related exceptions
class WalletError(DEXSniperError):
    """Exceptions related to wallet operations."""
    pass


class InvalidAddressError(WalletError):
    """Exception for invalid wallet addresses."""
    pass


class WalletConnectionError(WalletError):
    """Exception for wallet connection failures."""
    pass


class InsufficientFundsError(WalletError):
    """Exception for insufficient wallet funds."""
    pass


# Network-related exceptions
class NetworkError(DEXSniperError):
    """Exceptions related to blockchain network connectivity."""
    pass


class RPCError(NetworkError):
    """Exception for RPC connection issues."""
    pass


class ChainIDMismatchError(NetworkError):
    """Exception for chain ID mismatches."""
    pass


# DEX-related exceptions
class DEXError(DEXSniperError):
    """Exceptions related to DEX operations."""
    pass


class InsufficientLiquidityError(DEXError):
    """Exception for insufficient DEX liquidity."""
    pass


class PriceImpactError(DEXError):
    """Exception for excessive price impact."""
    pass


class TransactionError(DEXError):
    """Exception for blockchain transaction failures."""
    pass


class SwapError(DEXError):
    """Exception for swap execution failures."""
    pass


# Trading-related exceptions
class TradingError(DEXSniperError):
    """Exceptions related to trading operations."""
    pass


class RiskManagementError(TradingError):
    """Exception for risk management violations."""
    pass


class PositionSizeError(TradingError):
    """Exception for invalid position sizes."""
    pass


class ExecutionError(TradingError):
    """Exception for trade execution failures."""
    pass


class OpportunityExpiredError(TradingError):
    """Exception for expired trading opportunities."""
    pass


# Service-related exceptions
class ServiceError(DEXSniperError):
    """Exception for service-level errors."""
    pass


class ServiceUnavailableError(ServiceError):
    """Exception for unavailable services."""
    pass


class ConfigurationError(ServiceError):
    """Exception for configuration issues."""
    pass


# Data and validation exceptions
class ValidationError(DEXSniperError):
    """Exception for data validation failures."""
    pass


class DataError(DEXSniperError):
    """Exception for data processing errors."""
    pass


class ParseError(DataError):
    """Exception for data parsing failures."""
    pass


# Authentication and authorization exceptions
class AuthenticationError(DEXSniperError):
    """Exception for authentication failures."""
    pass


class AuthorizationError(DEXSniperError):
    """Exception for authorization failures."""
    pass


class SecurityError(DEXSniperError):
    """Exception for security-related issues."""
    pass


class PermissionError(DEXSniperError):
    """Exception for permission-related issues."""
    pass


# Rate limiting and timeout exceptions
class RateLimitError(DEXSniperError):
    """Exception for rate limit violations."""
    pass


class TimeoutError(DEXSniperError):
    """Exception for operation timeouts."""
    pass


class APIError(DEXSniperError):
    """Exception for API-related errors."""
    pass


# Discovery and analysis exceptions
class DiscoveryError(DEXSniperError):
    """Exception for token discovery errors."""
    pass


class AnalysisError(DEXSniperError):
    """Exception for analysis failures."""
    pass


class RiskAssessmentError(AnalysisError):
    """Exception for risk assessment failures."""
    pass


# Token and contract exceptions
class TokenError(DEXSniperError):
    """Exception for token-related issues."""
    pass


class ContractError(DEXSniperError):
    """Exception for smart contract issues."""
    pass


class InvalidTokenError(TokenError):
    """Exception for invalid tokens."""
    pass


# Mempool and monitoring exceptions
class MempoolError(DEXSniperError):
    """Exception for mempool monitoring issues."""
    pass


class MonitoringError(DEXSniperError):
    """Exception for monitoring system issues."""
    pass


# Database and storage exceptions
class DatabaseError(DEXSniperError):
    """Exception for database-related issues."""
    pass


class StorageError(DEXSniperError):
    """Exception for storage-related issues."""
    pass


# Cache and performance exceptions
class CacheError(DEXSniperError):
    """Exception for cache-related issues."""
    pass


class PerformanceError(DEXSniperError):
    """Exception for performance-related issues."""
    pass


# Integration and external service exceptions
class IntegrationError(DEXSniperError):
    """Exception for integration issues."""
    pass


class ExternalServiceError(DEXSniperError):
    """Exception for external service issues."""
    pass


# Session and state exceptions
class SessionError(DEXSniperError):
    """Exception for session-related issues."""
    pass


class StateError(DEXSniperError):
    """Exception for state management issues."""
    pass


# Protocol and communication exceptions
class ProtocolError(DEXSniperError):
    """Exception for protocol-related issues."""
    pass


class CommunicationError(DEXSniperError):
    """Exception for communication issues."""
    pass


# Synchronization and concurrency exceptions
class SynchronizationError(DEXSniperError):
    """Exception for synchronization issues."""
    pass


class ConcurrencyError(DEXSniperError):
    """Exception for concurrency issues."""
    pass


# Resource and capacity exceptions
class ResourceError(DEXSniperError):
    """Exception for resource-related issues."""
    pass


class CapacityError(DEXSniperError):
    """Exception for capacity-related issues."""
    pass


# Format and encoding exceptions
class FormatError(DEXSniperError):
    """Exception for format-related issues."""
    pass


class EncodingError(DEXSniperError):
    """Exception for encoding-related issues."""
    pass


# Backup compatibility exceptions (common names)
class ConnectionError(NetworkError):
    """Exception for connection issues."""
    pass


class ProcessingError(DEXSniperError):
    """Exception for processing issues."""
    pass


class InitializationError(DEXSniperError):
    """Exception for initialization issues."""
    pass


class ShutdownError(DEXSniperError):
    """Exception for shutdown issues."""
    pass


# Error code constants
class ErrorCodes:
    """Standard error codes for consistent error handling."""
    
    # Wallet errors
    WALLET_CONNECTION_FAILED = "WALLET_001"
    WALLET_DISCONNECTED = "WALLET_002"
    INSUFFICIENT_FUNDS = "WALLET_003"
    INVALID_ADDRESS = "WALLET_004"
    
    # Network errors
    NETWORK_UNAVAILABLE = "NETWORK_001"
    RPC_ERROR = "NETWORK_002"
    CHAIN_ID_MISMATCH = "NETWORK_003"
    
    # DEX errors
    DEX_UNAVAILABLE = "DEX_001"
    PRICE_FEED_ERROR = "DEX_002"
    LIQUIDITY_ERROR = "DEX_003"
    SWAP_FAILED = "DEX_004"
    
    # Trading errors
    OPPORTUNITY_EXPIRED = "TRADING_001"
    RISK_LIMIT_EXCEEDED = "TRADING_002"
    POSITION_SIZE_ERROR = "TRADING_003"
    EXECUTION_FAILED = "TRADING_004"
    
    # Service errors
    SERVICE_UNAVAILABLE = "SERVICE_001"
    CONFIGURATION_ERROR = "SERVICE_002"
    
    # General errors
    VALIDATION_FAILED = "GENERAL_001"
    TIMEOUT_ERROR = "GENERAL_002"
    RATE_LIMIT_EXCEEDED = "GENERAL_003"
    API_ERROR = "GENERAL_004"


# Helper functions for creating standardized errors
def create_wallet_error(message: str, error_code: str = None, **details) -> WalletError:
    """Create a wallet error with standard formatting."""
    return WalletError(
        message=message,
        error_code=error_code or ErrorCodes.WALLET_CONNECTION_FAILED,
        details=details
    )


def create_dex_error(message: str, error_code: str = None, **details) -> DEXError:
    """Create a DEX error with standard formatting."""
    return DEXError(
        message=message,
        error_code=error_code or ErrorCodes.DEX_UNAVAILABLE,
        details=details
    )


def create_trading_error(message: str, error_code: str = None, **details) -> TradingError:
    """Create a trading error with standard formatting."""
    return TradingError(
        message=message,
        error_code=error_code or ErrorCodes.EXECUTION_FAILED,
        details=details
    )


def create_network_error(message: str, error_code: str = None, **details) -> NetworkError:
    """Create a network error with standard formatting."""
    return NetworkError(
        message=message,
        error_code=error_code or ErrorCodes.NETWORK_UNAVAILABLE,
        details=details
    )


def create_service_error(message: str, error_code: str = None, **details) -> ServiceError:
    """Create a service error with standard formatting."""
    return ServiceError(
        message=message,
        error_code=error_code or ErrorCodes.SERVICE_UNAVAILABLE,
        details=details
    )


def create_validation_error(message: str, error_code: str = None, **details) -> ValidationError:
    """Create a validation error with standard formatting."""
    return ValidationError(
        message=message,
        error_code=error_code or ErrorCodes.VALIDATION_FAILED,
        details=details
    )

"""
Core Exceptions
File: app/core/exceptions.py

Custom exceptions for the DEX Sniper Pro trading platform.
Comprehensive exception hierarchy for all trading operations.
"""


class TradingError(Exception):
    """Base exception for all trading operations."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize trading error.
        
        Args:
            message: Error description
            error_code: Optional error code for categorization
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class WalletError(TradingError):
    """Wallet-related errors and exceptions."""
    pass


class DEXError(TradingError):
    """DEX integration and protocol errors."""
    pass


class NetworkError(TradingError):
    """Network connection and blockchain communication errors."""
    pass


class ConnectionError(NetworkError):
    """Connection-specific network errors."""
    pass


class InsufficientFundsError(TradingError):
    """Insufficient funds for trading operation."""
    pass


class InvalidAddressError(WalletError):
    """Invalid wallet or contract address format."""
    pass


class TransactionError(TradingError):
    """Transaction execution and blockchain errors."""
    pass


class SecurityError(WalletError):
    """Security-related wallet and authentication errors."""
    pass


class RiskLimitExceededError(TradingError):
    """Risk management limit exceeded."""
    pass


class StrategyError(TradingError):
    """Trading strategy execution errors."""
    pass


class PortfolioError(TradingError):
    """Portfolio management and tracking errors."""
    pass


class OrderExecutionError(TradingError):
    """Order placement and execution errors."""
    pass


class InvalidOrderError(TradingError):
    """Invalid order parameters or configuration."""
    pass


class SlippageExceededError(TradingError):
    """Slippage exceeded acceptable tolerance limits."""
    pass


class InsufficientLiquidityError(DEXError):
    """Insufficient liquidity for trade execution."""
    pass


class PriceImpactError(DEXError):
    """Price impact too high for safe execution."""
    pass


class GasEstimationError(NetworkError):
    """Gas estimation failed for transaction."""
    pass


class ContractError(NetworkError):
    """Smart contract interaction error."""
    pass


class ValidationError(TradingError):
    """Data validation and format errors."""
    pass


class ConfigurationError(TradingError):
    """Configuration and setup errors."""
    pass


class AuthenticationError(SecurityError):
    """Authentication and authorization errors."""
    pass


class RateLimitError(NetworkError):
    """API rate limit exceeded."""
    pass


class TimeoutError(NetworkError):
    """Operation timeout exceeded."""
    pass


class MarketDataError(TradingError):
    """Market data retrieval and processing errors."""
    pass


class AnalysisError(TradingError):
    """Market analysis and calculation errors."""
    pass


class WebSocketError(NetworkError):
    """WebSocket connection and communication errors."""
    pass


class DatabaseError(TradingError):
    """Database operations and connectivity errors."""
    pass


# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    InvalidOrderError: 400,
    InvalidAddressError: 400,
    AuthenticationError: 401,
    SecurityError: 403,
    InsufficientFundsError: 402,
    RateLimitError: 429,
    TimeoutError: 408,
    InsufficientLiquidityError: 503,
    SlippageExceededError: 503,
    NetworkError: 503,
    ConnectionError: 503,
    TradingError: 500
}


def get_http_status_for_exception(exception: Exception) -> int:
    """
    Get appropriate HTTP status code for exception.
    
    Args:
        exception: Exception instance
        
    Returns:
        int: HTTP status code
    """
    for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status_code
    
    return 500  # Default to internal server error