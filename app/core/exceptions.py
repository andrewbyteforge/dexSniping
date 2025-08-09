"""
Fixed Core Exceptions - Import Issues Resolution
File: app/core/exceptions.py

Fixed import issues with InsufficientLiquidityError and other missing exceptions.
All exceptions properly defined and exported.
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


class ChainConnectionException(NetworkError):
    """Exception for chain connection failures."""
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
    """Exception for trading strategy errors."""
    pass


class PortfolioError(TradingError):
    """Exception for portfolio management errors."""
    pass


class BalanceError(TradingError):
    """Exception for balance calculation errors."""
    pass


# ==================== SERVICE-RELATED EXCEPTIONS ====================

class ServiceError(DEXSniperError):
    """Base class for service and system errors."""
    pass


class ServiceUnavailableError(ServiceError):
    """Exception for unavailable services."""
    pass


class ConfigurationError(ServiceError):
    """Exception for configuration issues."""
    pass


class InitializationError(ServiceError):
    """Exception for service initialization failures."""
    pass


class ShutdownError(ServiceError):
    """Exception for service shutdown failures."""
    pass


class DependencyError(ServiceError):
    """Exception for missing or failed dependencies."""
    pass


# ==================== DATA-RELATED EXCEPTIONS ====================

class DataError(DEXSniperError):
    """Base class for data processing errors."""
    pass


class ValidationError(DataError):
    """Exception for data validation failures."""
    pass


class ParseError(DataError):
    """Exception for data parsing failures."""
    pass


class FormatError(DataError):
    """Exception for data format errors."""
    pass


class EncodingError(DataError):
    """Exception for data encoding/decoding errors."""
    pass


class SerializationError(DataError):
    """Exception for data serialization failures."""
    pass


# ==================== SECURITY-RELATED EXCEPTIONS ====================

class SecurityError(DEXSniperError):
    """Base class for security-related errors."""
    pass


class AuthenticationError(SecurityError):
    """Exception for authentication failures."""
    pass


class AuthorizationError(SecurityError):
    """Exception for authorization failures."""
    pass


class PermissionError(SecurityError):
    """Exception for permission-related errors."""
    pass


class AccessDeniedError(SecurityError):
    """Exception for access denied errors."""
    pass


class CredentialError(SecurityError):
    """Exception for credential-related errors."""
    pass


# ==================== RATE LIMITING AND API EXCEPTIONS ====================

class APIError(DEXSniperError):
    """Base class for API-related errors."""
    pass


class RateLimitError(APIError):
    """Exception for rate limit exceeded errors."""
    pass


class TimeoutError(APIError):
    """Exception for timeout errors."""
    pass


class QuotaExceededError(APIError):
    """Exception for quota exceeded errors."""
    pass


class ThrottleError(APIError):
    """Exception for throttling errors."""
    pass


# ==================== ANALYSIS AND AI EXCEPTIONS ====================

class AnalysisError(DEXSniperError):
    """Base class for analysis errors."""
    pass


class AIAnalysisError(AnalysisError):
    """Exception for AI analysis failures."""
    pass


class HoneypotDetectionError(AnalysisError):
    """Exception for honeypot detection failures."""
    pass


class SentimentAnalysisError(AnalysisError):
    """Exception for sentiment analysis failures."""
    pass


class DiscoveryError(AnalysisError):
    """Exception for token discovery errors."""
    pass


class RiskAssessmentError(AnalysisError):
    """Exception for risk assessment failures."""
    pass


class MarketDataError(AnalysisError):
    """Exception for market data errors."""
    pass


class PriceDataError(AnalysisError):
    """Exception for price data errors."""
    pass


class IndicatorError(AnalysisError):
    """Exception for technical indicator errors."""
    pass


# ==================== TOKEN AND CONTRACT EXCEPTIONS ====================

class TokenError(DEXSniperError):
    """Base class for token-related errors."""
    pass


class ContractError(TokenError):
    """Exception for smart contract errors."""
    pass


class InvalidTokenError(TokenError):
    """Exception for invalid token errors."""
    pass


class TokenNotFoundError(TokenError):
    """Exception for token not found errors."""
    pass


class ContractNotFoundError(ContractError):
    """Exception for contract not found errors."""
    pass


class ContractCallError(ContractError):
    """Exception for contract call failures."""
    pass


class ABIError(ContractError):
    """Exception for ABI-related errors."""
    pass


# ==================== SYSTEM AND PROCESSING EXCEPTIONS ====================

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


# ==================== ADDITIONAL COMPATIBILITY EXCEPTIONS ====================

# Legacy and backward compatibility exceptions
TradingError = TradingError  # Already defined above
WalletError = WalletError    # Already defined above
DEXError = DEXError          # Already defined above
NetworkError = NetworkError  # Already defined above


# Additional backward compatibility aliases
ProcessingError = ProcessingError  # Already defined above
InitializationError = InitializationError  # Already defined above
ShutdownError = ShutdownError  # Already defined above


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
    
    # Rate limiting error codes
    RATE_LIMIT_EXCEEDED = "RATE_001"
    TIMEOUT_ERROR = "RATE_002"
    API_ERROR = "RATE_003"
    QUOTA_EXCEEDED = "RATE_004"
    THROTTLE_ERROR = "RATE_005"
    
    # Analysis error codes
    AI_ANALYSIS_FAILED = "ANALYSIS_001"
    HONEYPOT_DETECTION_FAILED = "ANALYSIS_002"
    SENTIMENT_ANALYSIS_FAILED = "ANALYSIS_003"
    RISK_ASSESSMENT_FAILED = "ANALYSIS_004"
    MARKET_DATA_ERROR = "ANALYSIS_005"
    
    # Token error codes
    TOKEN_NOT_FOUND = "TOKEN_001"
    INVALID_TOKEN = "TOKEN_002"
    CONTRACT_ERROR = "TOKEN_003"
    ABI_ERROR = "TOKEN_004"
    CONTRACT_CALL_FAILED = "TOKEN_005"


# ==================== HTTP STATUS CODE MAPPING ====================

EXCEPTION_STATUS_MAP = {
    # 400 Bad Request
    ValidationError: 400,
    InvalidOrderError: 400,
    InvalidAddressError: 400,
    InvalidTokenError: 400,
    FormatError: 400,
    ParseError: 400,
    
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
    
    # 410 Gone
    OpportunityExpiredError: 410,
    
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
    
    # 503 Service Unavailable
    ServiceUnavailableError: 503,
    InsufficientLiquidityError: 503,
    NetworkError: 503,
    ConnectionError: 503,
    DEXError: 503,
    
    # 504 Gateway Timeout
    RPCError: 504,
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


def format_error_response(exception: Exception) -> Dict[str, Any]:
    """
    Format exception as standardized error response.
    
    Args:
        exception: Exception to format
        
    Returns:
        Dict containing formatted error information
    """
    if isinstance(exception, DEXSniperError):
        return exception.to_dict()
    
    return {
        "error_type": exception.__class__.__name__,
        "message": str(exception),
        "error_code": None,
        "details": {}
    }


def handle_exception_gracefully(func):
    """
    Decorator for graceful exception handling with logging and standardized responses.
    """
    import functools
    import logging
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Exception in {func.__name__}: {e}")
            return format_error_response(e)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Exception in {func.__name__}: {e}")
            return format_error_response(e)
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


# ==================== MODULE METADATA ====================

__version__ = "4.0.0-beta"
__phase__ = "4C - Complete Exception System"
__description__ = "Comprehensive exception handling system for DEX Sniper Pro with all required exceptions"

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
    'BlockchainError', 'GasEstimationError', 'NonceError', 'ChainConnectionException',
    
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
    'DiscoveryError', 'AnalysisError', 'AIAnalysisError', 'HoneypotDetectionError',
    'SentimentAnalysisError', 'RiskAssessmentError', 'MarketDataError', 
    'PriceDataError', 'IndicatorError',
    
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
    'create_network_error'
]