"""
Core Exception Classes - Phase 4B Complete
File: app/core/exceptions.py

Comprehensive exception system for the DEX Sniper Pro trading bot with
thorough error handling for all system components and backward compatibility.
"""

from typing import Optional, Dict, Any


class DEXSniperError(Exception):
    """
    Base exception class for DEX Sniper Pro.
    
    Provides comprehensive error handling with error codes, details,
    and standardized error response formatting for API consistency.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize DEX Sniper error with comprehensive error information.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for categorization and tracking
            details: Optional additional error details for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses.
        
        Returns:
            Dict containing structured error information
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# ==================== WALLET-RELATED EXCEPTIONS ====================

class WalletError(DEXSniperError):
    """Base class for all wallet-related exceptions."""
    pass


class InvalidAddressError(WalletError):
    """Exception for invalid wallet or contract addresses."""
    pass


class WalletConnectionError(WalletError):
    """Exception for wallet connection failures."""
    pass


class InsufficientFundsError(WalletError):
    """Exception for insufficient wallet funds."""
    pass


class WalletNotConnectedError(WalletError):
    """Exception for operations requiring connected wallet."""
    pass


class WalletLockError(WalletError):
    """Exception for locked wallet operations."""
    pass


class SignatureError(WalletError):
    """Exception for transaction signature failures."""
    pass


# ==================== NETWORK-RELATED EXCEPTIONS ====================

class NetworkError(DEXSniperError):
    """Base class for blockchain network connectivity issues."""
    pass


class ConnectionError(NetworkError):
    """Exception for network connection failures."""
    pass


class RPCError(NetworkError):
    """Exception for RPC connection and communication issues."""
    pass


class ChainIDMismatchError(NetworkError):
    """Exception for blockchain chain ID mismatches."""
    pass


class BlockchainError(NetworkError):
    """Exception for general blockchain interaction errors."""
    pass


class GasEstimationError(NetworkError):
    """Exception for transaction gas estimation failures."""
    pass


class NonceError(NetworkError):
    """Exception for transaction nonce management issues."""
    pass


# ==================== DEX-RELATED EXCEPTIONS ====================

class DEXError(DEXSniperError):
    """Base class for DEX operations and protocol errors."""
    pass


class InsufficientLiquidityError(DEXError):
    """Exception for insufficient DEX liquidity."""
    pass


class PriceImpactError(DEXError):
    """Exception for excessive price impact on trades."""
    pass


class SlippageExceededError(DEXError):
    """Exception for slippage exceeding acceptable limits."""
    pass


class TransactionError(DEXError):
    """Exception for blockchain transaction execution failures."""
    pass


class SwapError(DEXError):
    """Exception for token swap execution failures."""
    pass


class LiquidityPoolError(DEXError):
    """Exception for liquidity pool interaction issues."""
    pass


class RouterError(DEXError):
    """Exception for DEX router contract issues."""
    pass


class PairNotFoundError(DEXError):
    """Exception for non-existent trading pairs."""
    pass


# ==================== TRADING-RELATED EXCEPTIONS ====================

class TradingError(DEXSniperError):
    """Base class for trading operations and strategy errors."""
    pass


class RiskManagementError(TradingError):
    """Exception for risk management violations."""
    pass


class RiskLimitExceededError(TradingError):
    """Exception for exceeded risk limits."""
    pass


class PositionSizeError(TradingError):
    """Exception for invalid position sizes."""
    pass


class ExecutionError(TradingError):
    """Exception for trade execution failures."""
    pass


class OrderExecutionError(TradingError):
    """Exception for order placement and execution errors."""
    pass


class InvalidOrderError(TradingError):
    """Exception for invalid order parameters."""
    pass


class OpportunityExpiredError(TradingError):
    """Exception for expired trading opportunities."""
    pass


class StrategyError(TradingError):
    """Exception for trading strategy execution errors."""
    pass


class PortfolioError(TradingError):
    """Exception for portfolio management and tracking errors."""
    pass


class BalanceError(TradingError):
    """Exception for balance calculation and tracking errors."""
    pass


# ==================== SERVICE-RELATED EXCEPTIONS ====================

class ServiceError(DEXSniperError):
    """Base class for service-level errors."""
    pass


class ServiceUnavailableError(ServiceError):
    """Exception for unavailable services."""
    pass


class ConfigurationError(ServiceError):
    """Exception for configuration and setup issues."""
    pass


class InitializationError(ServiceError):
    """Exception for service initialization failures."""
    pass


class ShutdownError(ServiceError):
    """Exception for service shutdown issues."""
    pass


class DependencyError(ServiceError):
    """Exception for service dependency issues."""
    pass


# ==================== DATA AND VALIDATION EXCEPTIONS ====================

class ValidationError(DEXSniperError):
    """Exception for data validation failures."""
    pass


class DataError(DEXSniperError):
    """Exception for data processing errors."""
    pass


class ParseError(DataError):
    """Exception for data parsing failures."""
    pass


class FormatError(DEXSniperError):
    """Exception for data format issues."""
    pass


class EncodingError(DEXSniperError):
    """Exception for data encoding issues."""
    pass


class SerializationError(DataError):
    """Exception for data serialization failures."""
    pass


# ==================== AUTHENTICATION AND SECURITY EXCEPTIONS ====================

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


class AccessDeniedError(SecurityError):
    """Exception for access denied scenarios."""
    pass


class CredentialError(AuthenticationError):
    """Exception for credential-related issues."""
    pass


# ==================== RATE LIMITING AND TIMEOUT EXCEPTIONS ====================

class RateLimitError(DEXSniperError):
    """Exception for API rate limit violations."""
    pass


class TimeoutError(DEXSniperError):
    """Exception for operation timeouts."""
    pass


class APIError(DEXSniperError):
    """Exception for general API-related errors."""
    pass


class QuotaExceededError(RateLimitError):
    """Exception for exceeded API quotas."""
    pass


class ThrottleError(RateLimitError):
    """Exception for API throttling."""
    pass


# ==================== DISCOVERY AND ANALYSIS EXCEPTIONS ====================

class DiscoveryError(DEXSniperError):
    """Exception for token discovery errors."""
    pass


class AnalysisError(DEXSniperError):
    """Exception for market analysis failures."""
    pass


class RiskAssessmentError(AnalysisError):
    """Exception for risk assessment failures."""
    pass


class MarketDataError(AnalysisError):
    """Exception for market data retrieval and processing errors."""
    pass


class PriceDataError(MarketDataError):
    """Exception for price data issues."""
    pass


class IndicatorError(AnalysisError):
    """Exception for technical indicator calculation errors."""
    pass


# ==================== TOKEN AND CONTRACT EXCEPTIONS ====================

class TokenError(DEXSniperError):
    """Exception for token-related issues."""
    pass


class ContractError(DEXSniperError):
    """Exception for smart contract interaction issues."""
    pass


class InvalidTokenError(TokenError):
    """Exception for invalid or malicious tokens."""
    pass


class TokenNotFoundError(TokenError):
    """Exception for non-existent tokens."""
    pass


class ContractNotFoundError(ContractError):
    """Exception for non-existent contracts."""
    pass


class ContractCallError(ContractError):
    """Exception for smart contract call failures."""
    pass


class ABIError(ContractError):
    """Exception for contract ABI issues."""
    pass


# ==================== MEMPOOL AND MONITORING EXCEPTIONS ====================

class MempoolError(DEXSniperError):
    """Exception for mempool monitoring issues."""
    pass


class MonitoringError(DEXSniperError):
    """Exception for monitoring system issues."""
    pass


class ScannerError(MonitoringError):
    """Exception for token scanner issues."""
    pass


class DetectionError(MonitoringError):
    """Exception for opportunity detection failures."""
    pass


class AlertError(MonitoringError):
    """Exception for alert system issues."""
    pass


# ==================== DATABASE AND STORAGE EXCEPTIONS ====================

class DatabaseError(DEXSniperError):
    """Exception for database-related issues."""
    pass


class StorageError(DEXSniperError):
    """Exception for storage-related issues."""
    pass


class QueryError(DatabaseError):
    """Exception for database query failures."""
    pass


class ConnectionPoolError(DatabaseError):
    """Exception for database connection pool issues."""
    pass


class MigrationError(DatabaseError):
    """Exception for database migration issues."""
    pass


# ==================== CACHE AND PERFORMANCE EXCEPTIONS ====================

class CacheError(DEXSniperError):
    """Exception for cache-related issues."""
    pass


class PerformanceError(DEXSniperError):
    """Exception for performance-related issues."""
    pass


class MemoryError(PerformanceError):
    """Exception for memory-related issues."""
    pass


class CPUError(PerformanceError):
    """Exception for CPU-related issues."""
    pass


class CacheMissError(CacheError):
    """Exception for cache miss scenarios."""
    pass


class CacheExpiredError(CacheError):
    """Exception for expired cache entries."""
    pass


# ==================== INTEGRATION AND EXTERNAL SERVICE EXCEPTIONS ====================

class IntegrationError(DEXSniperError):
    """Exception for integration issues."""
    pass


class ExternalServiceError(DEXSniperError):
    """Exception for external service issues."""
    pass


class WebhookError(IntegrationError):
    """Exception for webhook-related issues."""
    pass


class NotificationError(IntegrationError):
    """Exception for notification system issues."""
    pass


class ThirdPartyError(ExternalServiceError):
    """Exception for third-party service issues."""
    pass


# ==================== SESSION AND STATE EXCEPTIONS ====================

class SessionError(DEXSniperError):
    """Exception for session-related issues."""
    pass


class StateError(DEXSniperError):
    """Exception for state management issues."""
    pass


class SessionExpiredError(SessionError):
    """Exception for expired sessions."""
    pass


class StateCorruptionError(StateError):
    """Exception for corrupted state data."""
    pass


class StateSyncError(StateError):
    """Exception for state synchronization issues."""
    pass


# ==================== PROTOCOL AND COMMUNICATION EXCEPTIONS ====================

class ProtocolError(DEXSniperError):
    """Exception for protocol-related issues."""
    pass


class CommunicationError(DEXSniperError):
    """Exception for communication issues."""
    pass


class WebSocketError(CommunicationError):
    """Exception for WebSocket connection and communication errors."""
    pass


class MessageError(CommunicationError):
    """Exception for message processing issues."""
    pass


class ChannelError(CommunicationError):
    """Exception for communication channel issues."""
    pass


# ==================== SYNCHRONIZATION AND CONCURRENCY EXCEPTIONS ====================

class SynchronizationError(DEXSniperError):
    """Exception for synchronization issues."""
    pass


class ConcurrencyError(DEXSniperError):
    """Exception for concurrency issues."""
    pass


class DeadlockError(ConcurrencyError):
    """Exception for deadlock scenarios."""
    pass


class RaceConditionError(ConcurrencyError):
    """Exception for race condition issues."""
    pass


class LockError(SynchronizationError):
    """Exception for locking mechanism issues."""
    pass


# ==================== RESOURCE AND CAPACITY EXCEPTIONS ====================

class ResourceError(DEXSniperError):
    """Exception for resource-related issues."""
    pass


class CapacityError(DEXSniperError):
    """Exception for capacity-related issues."""
    pass


class ResourceExhaustionError(ResourceError):
    """Exception for resource exhaustion scenarios."""
    pass


class CapacityExceededError(CapacityError):
    """Exception for exceeded capacity limits."""
    pass


class AllocationError(ResourceError):
    """Exception for resource allocation failures."""
    pass


# ==================== PROCESSING AND CALCULATION EXCEPTIONS ====================

class ProcessingError(DEXSniperError):
    """Exception for general processing issues."""
    pass


class CalculationError(DEXSniperError):
    """Exception for calculation errors."""
    pass


class AlgorithmError(DEXSniperError):
    """Exception for algorithm execution errors."""
    pass


class OptimizationError(DEXSniperError):
    """Exception for optimization process errors."""
    pass


class ConvergenceError(AlgorithmError):
    """Exception for algorithm convergence failures."""
    pass


# ==================== ERROR CODE CONSTANTS ====================

class ErrorCodes:
    """
    Standard error codes for consistent error handling and categorization.
    Provides structured error identification across all system components.
    """
    
    # Wallet error codes
    WALLET_CONNECTION_FAILED = "WALLET_001"
    WALLET_DISCONNECTED = "WALLET_002"
    INSUFFICIENT_FUNDS = "WALLET_003"
    INVALID_ADDRESS = "WALLET_004"
    WALLET_LOCKED = "WALLET_005"
    SIGNATURE_FAILED = "WALLET_006"
    
    # Network error codes
    NETWORK_UNAVAILABLE = "NETWORK_001"
    RPC_ERROR = "NETWORK_002"
    CHAIN_ID_MISMATCH = "NETWORK_003"
    GAS_ESTIMATION_FAILED = "NETWORK_004"
    NONCE_ERROR = "NETWORK_005"
    BLOCKCHAIN_ERROR = "NETWORK_006"
    
    # DEX error codes
    DEX_UNAVAILABLE = "DEX_001"
    PRICE_FEED_ERROR = "DEX_002"
    LIQUIDITY_ERROR = "DEX_003"
    SWAP_FAILED = "DEX_004"
    SLIPPAGE_EXCEEDED = "DEX_005"
    PRICE_IMPACT_HIGH = "DEX_006"
    PAIR_NOT_FOUND = "DEX_007"
    ROUTER_ERROR = "DEX_008"
    
    # Trading error codes
    OPPORTUNITY_EXPIRED = "TRADING_001"
    RISK_LIMIT_EXCEEDED = "TRADING_002"
    POSITION_SIZE_ERROR = "TRADING_003"
    EXECUTION_FAILED = "TRADING_004"
    INVALID_ORDER = "TRADING_005"
    STRATEGY_ERROR = "TRADING_006"
    PORTFOLIO_ERROR = "TRADING_007"
    BALANCE_ERROR = "TRADING_008"
    
    # Service error codes
    SERVICE_UNAVAILABLE = "SERVICE_001"
    CONFIGURATION_ERROR = "SERVICE_002"
    INITIALIZATION_FAILED = "SERVICE_003"
    DEPENDENCY_ERROR = "SERVICE_004"
    SHUTDOWN_ERROR = "SERVICE_005"
    
    # Data and validation error codes
    VALIDATION_FAILED = "DATA_001"
    PARSE_ERROR = "DATA_002"
    FORMAT_ERROR = "DATA_003"
    ENCODING_ERROR = "DATA_004"
    SERIALIZATION_ERROR = "DATA_005"
    
    # Authentication and security error codes
    AUTHENTICATION_FAILED = "AUTH_001"
    AUTHORIZATION_FAILED = "AUTH_002"
    ACCESS_DENIED = "AUTH_003"
    PERMISSION_ERROR = "AUTH_004"
    CREDENTIAL_ERROR = "AUTH_005"
    SECURITY_ERROR = "AUTH_006"
    
    # Rate limiting and timeout error codes
    RATE_LIMIT_EXCEEDED = "RATE_001"
    TIMEOUT_ERROR = "RATE_002"
    QUOTA_EXCEEDED = "RATE_003"
    THROTTLED = "RATE_004"
    API_ERROR = "RATE_005"
    
    # Discovery and analysis error codes
    DISCOVERY_FAILED = "ANALYSIS_001"
    RISK_ASSESSMENT_FAILED = "ANALYSIS_002"
    MARKET_DATA_ERROR = "ANALYSIS_003"
    PRICE_DATA_ERROR = "ANALYSIS_004"
    INDICATOR_ERROR = "ANALYSIS_005"
    
    # Token and contract error codes
    INVALID_TOKEN = "TOKEN_001"
    TOKEN_NOT_FOUND = "TOKEN_002"
    CONTRACT_ERROR = "TOKEN_003"
    CONTRACT_NOT_FOUND = "TOKEN_004"
    CONTRACT_CALL_FAILED = "TOKEN_005"
    ABI_ERROR = "TOKEN_006"
    
    # Database and storage error codes
    DATABASE_ERROR = "DB_001"
    STORAGE_ERROR = "DB_002"
    QUERY_ERROR = "DB_003"
    CONNECTION_POOL_ERROR = "DB_004"
    MIGRATION_ERROR = "DB_005"
    
    # Performance and resource error codes
    PERFORMANCE_ERROR = "PERF_001"
    MEMORY_ERROR = "PERF_002"
    CPU_ERROR = "PERF_003"
    RESOURCE_EXHAUSTION = "PERF_004"
    CAPACITY_EXCEEDED = "PERF_005"
    
    # General system error codes
    UNKNOWN_ERROR = "SYS_001"
    INTERNAL_ERROR = "SYS_002"
    PROCESSING_ERROR = "SYS_003"
    CALCULATION_ERROR = "SYS_004"
    ALGORITHM_ERROR = "SYS_005"


# ==================== HTTP STATUS CODE MAPPING ====================

EXCEPTION_STATUS_MAP = {
    # 400 Bad Request
    ValidationError: 400,
    InvalidOrderError: 400,
    InvalidAddressError: 400,
    InvalidTokenError: 400,
    ParseError: 400,
    FormatError: 400,
    
    # 401 Unauthorized
    AuthenticationError: 401,
    CredentialError: 401,
    
    # 403 Forbidden
    AuthorizationError: 403,
    SecurityError: 403,
    AccessDeniedError: 403,
    PermissionError: 403,
    
    # 402 Payment Required
    InsufficientFundsError: 402,
    
    # 404 Not Found
    TokenNotFoundError: 404,
    ContractNotFoundError: 404,
    PairNotFoundError: 404,
    
    # 408 Request Timeout
    TimeoutError: 408,
    
    # 409 Conflict
    StateError: 409,
    ConcurrencyError: 409,
    DeadlockError: 409,
    
    # 410 Gone
    SessionExpiredError: 410,
    OpportunityExpiredError: 410,
    
    # 413 Payload Too Large
    CapacityExceededError: 413,
    
    # 422 Unprocessable Entity
    PositionSizeError: 422,
    RiskLimitExceededError: 422,
    SlippageExceededError: 422,
    
    # 429 Too Many Requests
    RateLimitError: 429,
    QuotaExceededError: 429,
    ThrottleError: 429,
    
    # 500 Internal Server Error
    TradingError: 500,
    ProcessingError: 500,
    CalculationError: 500,
    AlgorithmError: 500,
    
    # 502 Bad Gateway
    ExternalServiceError: 502,
    ThirdPartyError: 502,
    
    # 503 Service Unavailable
    ServiceUnavailableError: 503,
    InsufficientLiquidityError: 503,
    NetworkError: 503,
    ConnectionError: 503,
    DEXError: 503,
    
    # 504 Gateway Timeout
    RPCError: 504,
    
    # 507 Insufficient Storage
    StorageError: 507,
    DatabaseError: 507,
    
    # 508 Loop Detected
    RaceConditionError: 508,
    
    # 509 Bandwidth Limit Exceeded
    ResourceExhaustionError: 509,
    
    # 510 Not Extended
    ConfigurationError: 510,
    DependencyError: 510
}


def get_http_status_for_exception(exception: Exception) -> int:
    """
    Get appropriate HTTP status code for exception with comprehensive mapping.
    
    Args:
        exception: Exception instance to map
        
    Returns:
        int: HTTP status code (defaults to 500 for unmapped exceptions)
    """
    for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status_code
    
    return 500  # Default to internal server error


# ==================== HELPER FUNCTIONS FOR STANDARDIZED ERROR CREATION ====================

def create_wallet_error(message: str, error_code: str = None, **details) -> WalletError:
    """Create a wallet error with standard formatting and error code."""
    return WalletError(
        message=message,
        error_code=error_code or ErrorCodes.WALLET_CONNECTION_FAILED,
        details=details
    )


def create_dex_error(message: str, error_code: str = None, **details) -> DEXError:
    """Create a DEX error with standard formatting and error code."""
    return DEXError(
        message=message,
        error_code=error_code or ErrorCodes.DEX_UNAVAILABLE,
        details=details
    )


def create_trading_error(message: str, error_code: str = None, **details) -> TradingError:
    """Create a trading error with standard formatting and error code."""
    return TradingError(
        message=message,
        error_code=error_code or ErrorCodes.EXECUTION_FAILED,
        details=details
    )


def create_network_error(message: str, error_code: str = None, **details) -> NetworkError:
    """Create a network error with standard formatting and error code."""
    return NetworkError(
        message=message,
        error_code=error_code or ErrorCodes.NETWORK_UNAVAILABLE,
        details=details
    )


def create_service_error(message: str, error_code: str = None, **details) -> ServiceError:
    """Create a service error with standard formatting and error code."""
    return ServiceError(
        message=message,
        error_code=error_code or ErrorCodes.SERVICE_UNAVAILABLE,
        details=details
    )


def create_validation_error(message: str, error_code: str = None, **details) -> ValidationError:
    """Create a validation error with standard formatting and error code."""
    return ValidationError(
        message=message,
        error_code=error_code or ErrorCodes.VALIDATION_FAILED,
        details=details
    )


def create_api_error(message: str, error_code: str = None, **details) -> APIError:
    """Create an API error with standard formatting and error code."""
    return APIError(
        message=message,
        error_code=error_code or ErrorCodes.API_ERROR,
        details=details
    )


def create_timeout_error(message: str, error_code: str = None, **details) -> TimeoutError:
    """Create a timeout error with standard formatting and error code."""
    return TimeoutError(
        message=message,
        error_code=error_code or ErrorCodes.TIMEOUT_ERROR,
        details=details
    )


def create_authentication_error(message: str, error_code: str = None, **details) -> AuthenticationError:
    """Create an authentication error with standard formatting and error code."""
    return AuthenticationError(
        message=message,
        error_code=error_code or ErrorCodes.AUTHENTICATION_FAILED,
        details=details
    )


def create_rate_limit_error(message: str, error_code: str = None, **details) -> RateLimitError:
    """Create a rate limit error with standard formatting and error code."""
    return RateLimitError(
        message=message,
        error_code=error_code or ErrorCodes.RATE_LIMIT_EXCEEDED,
        details=details
    )


# ==================== ERROR HANDLING UTILITIES ====================

def handle_exception_gracefully(func):
    """
    Decorator for graceful exception handling with logging and standardized responses.
    
    Args:
        func: Function to wrap with exception handling
        
    Returns:
        Wrapped function with exception handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DEXSniperError as e:
            # Log structured error information
            error_info = e.to_dict()
            print(f"DEX Sniper Error: {error_info}")
            raise
        except Exception as e:
            # Convert unexpected errors to standardized format
            standardized_error = DEXSniperError(
                message=f"Unexpected error: {str(e)}",
                error_code=ErrorCodes.UNKNOWN_ERROR,
                details={"original_exception": type(e).__name__}
            )
            print(f"Unexpected Error: {standardized_error.to_dict()}")
            raise standardized_error
    
    return wrapper


def format_error_response(exception: Exception) -> Dict[str, Any]:
    """
    Format exception as standardized API error response.
    
    Args:
        exception: Exception to format
        
    Returns:
        Dict containing formatted error response
    """
    if isinstance(exception, DEXSniperError):
        return {
            "success": False,
            "error": exception.to_dict(),
            "http_status": get_http_status_for_exception(exception)
        }
    else:
        return {
            "success": False,
            "error": {
                "error_type": "UnhandledException",
                "message": str(exception),
                "error_code": ErrorCodes.UNKNOWN_ERROR,
                "details": {"original_exception": type(exception).__name__}
            },
            "http_status": 500
        }


# ==================== BACKWARD COMPATIBILITY ALIASES ====================

# Maintain backward compatibility with existing code
class SlippageExceededError(DEXError):
    """Backward compatibility alias for slippage exceeded errors."""
    pass


# Additional backward compatibility aliases
ProcessingError = ProcessingError  # Already defined above
InitializationError = InitializationError  # Already defined above
ShutdownError = ShutdownError  # Already defined above


# ==================== MODULE METADATA ====================

__version__ = "4.0.0-beta"
__phase__ = "4B - Complete Exception System"
__description__ = "Comprehensive exception handling system for DEX Sniper Pro"

# Export all exception classes for easy importing
__all__ = [
    # Base exceptions
    'DEXSniperError',
    
    # Wallet exceptions
    'WalletError', 'InvalidAddressError', 'WalletConnectionError', 
    'InsufficientFundsError', 'WalletNotConnectedError', 'WalletLockError', 
    'SignatureError',
    
    # Network exceptions
    'NetworkError', 'ConnectionError', 'RPCError', 'ChainIDMismatchError',
    'BlockchainError', 'GasEstimationError', 'NonceError',
    
    # DEX exceptions
    'DEXError', 'InsufficientLiquidityError', 'PriceImpactError', 
    'SlippageExceededError', 'TransactionError', 'SwapError',
    'LiquidityPoolError', 'RouterError', 'PairNotFoundError',
    
    # Trading exceptions
    'TradingError', 'RiskManagementError', 'RiskLimitExceededError',
    'PositionSizeError', 'ExecutionError', 'OrderExecutionError',
    'InvalidOrderError', 'OpportunityExpiredError', 'StrategyError',
    'PortfolioError', 'BalanceError',
    
    # Service exceptions
    'ServiceError', 'ServiceUnavailableError', 'ConfigurationError',
    'InitializationError', 'ShutdownError', 'DependencyError',
    
    # Data exceptions
    'ValidationError', 'DataError', 'ParseError', 'FormatError',
    'EncodingError', 'SerializationError',
    
    # Security exceptions
    'AuthenticationError', 'AuthorizationError', 'SecurityError',
    'PermissionError', 'AccessDeniedError', 'CredentialError',
    
    # Rate limit exceptions
    'RateLimitError', 'TimeoutError', 'APIError', 'QuotaExceededError',
    'ThrottleError',
    
    # Analysis exceptions
    'DiscoveryError', 'AnalysisError', 'RiskAssessmentError',
    'MarketDataError', 'PriceDataError', 'IndicatorError',
    
    # Token exceptions
    'TokenError', 'ContractError', 'InvalidTokenError', 'TokenNotFoundError',
    'ContractNotFoundError', 'ContractCallError', 'ABIError',
    
    # System exceptions
    'ProcessingError', 'CalculationError', 'AlgorithmError',
    'OptimizationError', 'ConvergenceError',
    
    # Utility functions
    'get_http_status_for_exception', 'format_error_response',
    'handle_exception_gracefully',
    
    # Error code constants
    'ErrorCodes',
    
    # Helper functions
    'create_wallet_error', 'create_dex_error', 'create_trading_error',
    'create_network_error', 'create_service_error', 'create_validation_error',
    'create_api_error', 'create_timeout_error', 'create_authentication_error',
    'create_rate_limit_error'
]
