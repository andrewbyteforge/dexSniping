"""
Core Exceptions for DEX Sniper Pro
File: app/core/exceptions.py

Essential exception classes for the trading platform with comprehensive
error handling for all system components.
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


# ==================== TRADING-RELATED EXCEPTIONS ====================

class TradingError(DEXSniperError):
    """Base exception for trading operations."""
    pass


class WalletError(TradingError):
    """Wallet-related errors."""
    pass


class DEXError(TradingError):
    """DEX integration errors."""
    pass


class NetworkError(TradingError):
    """Network connection and blockchain errors."""
    pass


class ConnectionError(NetworkError):
    """Connection-specific errors."""
    pass


class InsufficientFundsError(TradingError):
    """Insufficient funds for operation."""
    pass


class InvalidAddressError(WalletError):
    """Invalid wallet address format."""
    pass


class TransactionError(TradingError):
    """Transaction execution errors."""
    pass


class SecurityError(WalletError):
    """Security-related errors."""
    pass


class RiskLimitExceededError(TradingError):
    """Risk limit exceeded."""
    pass


class StrategyError(TradingError):
    """Strategy execution errors."""
    pass


class PortfolioError(TradingError):
    """Portfolio management errors."""
    pass


class OrderExecutionError(TradingError):
    """Order execution errors."""
    pass


class InvalidOrderError(TradingError):
    """Invalid order parameters."""
    pass


class SlippageExceededError(TradingError):
    """Slippage exceeded acceptable limits."""
    pass


class InsufficientLiquidityError(DEXError):
    """Insufficient liquidity for trade."""
    pass


class PriceImpactError(DEXError):
    """Price impact too high for safe execution."""
    pass


class OpportunityExpiredError(TradingError):
    """Trading opportunity has expired."""
    pass


# ==================== PERFORMANCE-RELATED EXCEPTIONS ====================

class PerformanceError(DEXSniperError):
    """Exception for performance-related issues."""
    pass


class CacheError(DEXSniperError):
    """Exception for cache-related issues."""
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


class OptimizationError(PerformanceError):
    """Exception for optimization process errors."""
    pass


class GasOptimizationError(PerformanceError):
    """Exception for gas optimization failures."""
    pass


class GasEstimationError(NetworkError):
    """Exception for gas estimation failures."""  
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
    """Exception for rate limiting issues."""
    pass


class TimeoutError(DEXSniperError):
    """Exception for timeout scenarios."""
    pass


class APIError(DEXSniperError):
    """Exception for API-related issues."""
    pass


class QuotaExceededError(RateLimitError):
    """Exception for quota exceeded scenarios."""
    pass


class ThrottleError(RateLimitError):
    """Exception for throttling scenarios."""
    pass


# ==================== ANALYSIS AND DISCOVERY EXCEPTIONS ====================

class DiscoveryError(DEXSniperError):
    """Exception for token discovery failures."""
    pass


class AnalysisError(DEXSniperError):
    """Exception for analysis processing errors."""
    pass


class RiskAssessmentError(AnalysisError):
    """Exception for risk assessment failures."""
    pass


class MarketDataError(AnalysisError):
    """Exception for market data retrieval errors."""
    pass


class PriceDataError(MarketDataError):
    """Exception for price data errors."""
    pass


class IndicatorError(AnalysisError):
    """Exception for technical indicator calculation errors."""
    pass


# ==================== TOKEN AND CONTRACT EXCEPTIONS ====================

class TokenError(DEXSniperError):
    """Exception for token-related issues."""
    pass


class ContractError(DEXSniperError):
    """Exception for smart contract issues."""
    pass


class InvalidTokenError(TokenError):
    """Exception for invalid token addresses or data."""
    pass


class TokenNotFoundError(TokenError):
    """Exception for tokens that cannot be found."""
    pass


class ContractNotFoundError(ContractError):
    """Exception for contracts that cannot be found."""
    pass


class ContractCallError(ContractError):
    """Exception for contract call failures."""
    pass


class ABIError(ContractError):
    """Exception for contract ABI issues."""
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


# ==================== BLOCKCHAIN NETWORK EXCEPTIONS ====================

class ChainIDMismatchError(NetworkError):
    """Exception for chain ID mismatches."""
    pass


class BlockchainError(NetworkError):
    """Exception for blockchain-related issues."""
    pass


class GasEstimationError(NetworkError):
    """Exception for gas estimation failures."""
    pass


class NonceError(NetworkError):
    """Exception for nonce-related issues."""
    pass


class RPCError(NetworkError):
    """Exception for RPC connection and communication issues."""
    pass


# ==================== WALLET-RELATED EXCEPTIONS ====================

class WalletConnectionError(WalletError):
    """Exception for wallet connection failures."""
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


class ConvergenceError(AlgorithmError):
    """Exception for algorithm convergence failures."""
    pass


# ==================== ERROR CODE CONSTANTS ====================

class ErrorCodes:
    """Standard error codes for consistent error handling and categorization."""
    
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
    
    # Performance error codes
    PERFORMANCE_ERROR = "PERF_001"
    MEMORY_ERROR = "PERF_002"
    CPU_ERROR = "PERF_003"
    RESOURCE_EXHAUSTION = "PERF_004"
    CAPACITY_EXCEEDED = "PERF_005"
    
    # Service error codes
    SERVICE_UNAVAILABLE = "SERVICE_001"
    CONFIGURATION_ERROR = "SERVICE_002"
    INITIALIZATION_FAILED = "SERVICE_003"
    DEPENDENCY_ERROR = "SERVICE_004"
    SHUTDOWN_ERROR = "SERVICE_005"


# Export all exception classes for easy importing
__all__ = [
    # Base exceptions
    'DEXSniperError',
    
    # Trading exceptions
    'TradingError', 'WalletError', 'DEXError', 'NetworkError', 'ConnectionError',
    'InsufficientFundsError', 'InvalidAddressError', 'TransactionError',
    'SecurityError', 'RiskLimitExceededError', 'StrategyError', 'PortfolioError',
    'OrderExecutionError', 'InvalidOrderError', 'SlippageExceededError',
    'InsufficientLiquidityError', 'PriceImpactError', 'OpportunityExpiredError',
    
    # Performance exceptions  
    'PerformanceError', 'CacheError', 'MemoryError', 'CPUError',
    'CacheMissError', 'CacheExpiredError', 'OptimizationError', 'GasOptimizationError',
    
    # Database exceptions
    'DatabaseError', 'StorageError', 'QueryError', 'ConnectionPoolError',
    'MigrationError',
    
    # Service exceptions
    'ServiceError', 'ServiceUnavailableError', 'ConfigurationError',
    'InitializationError', 'ShutdownError', 'DependencyError',
    
    # Data exceptions
    'ValidationError', 'DataError', 'ParseError', 'FormatError',
    'EncodingError', 'SerializationError',
    
    # Security exceptions
    'AuthenticationError', 'AuthorizationError', 'PermissionError',
    'AccessDeniedError', 'CredentialError',
    
    # Rate limit exceptions
    'RateLimitError', 'TimeoutError', 'APIError', 'QuotaExceededError',
    'ThrottleError',
    
    # Analysis exceptions
    'DiscoveryError', 'AnalysisError', 'RiskAssessmentError',
    'MarketDataError', 'PriceDataError', 'IndicatorError',
    
    # Token exceptions
    'TokenError', 'ContractError', 'InvalidTokenError', 'TokenNotFoundError',
    'ContractNotFoundError', 'ContractCallError', 'ABIError',
    
    # Integration exceptions
    'IntegrationError', 'ExternalServiceError', 'WebhookError',
    'NotificationError', 'ThirdPartyError',
    
    # Blockchain exceptions
    'ChainIDMismatchError', 'BlockchainError', 'GasEstimationError',
    'NonceError', 'RPCError',
    
    # Wallet exceptions (extended)
    'WalletConnectionError', 'WalletNotConnectedError', 'WalletLockError',
    'SignatureError',
    
    # Resource exceptions
    'ResourceError', 'CapacityError', 'ResourceExhaustionError',
    'CapacityExceededError', 'AllocationError',
    
    # Processing exceptions
    'ProcessingError', 'CalculationError', 'AlgorithmError',
    'ConvergenceError',
    
    # Error codes
    'ErrorCodes'
]