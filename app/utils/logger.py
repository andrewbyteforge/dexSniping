"""
File: app/utils/logger.py

Centralized logging configuration for the DEX sniping application.
Provides structured logging with different levels and formatters.
"""

import logging
import structlog
import sys
from typing import Optional
from pathlib import Path

from app.config import settings


def setup_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Setup structured logger for the application.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structured logger instance
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if not settings.debug 
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Add file handler for production
    if not settings.debug:
        file_handler = logging.FileHandler(log_dir / "dex_sniping.log")
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logging.getLogger().addHandler(file_handler)
    
    return structlog.get_logger(name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    
    Provides a logger property that creates a logger instance
    with the class name as the logger name.
    """
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger instance for this class."""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger


# File: app/utils/exceptions.py

"""
Custom exception classes for the DEX sniping application.
Provides specific exception types for different error scenarios.
"""


class DexSnipingException(Exception):
    """Base exception class for all DEX sniping application errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
        """
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


class InsufficientLiquidityError(DexSnipingException):
    """Exception raised when token has insufficient liquidity for trading."""
    pass


class TradingException(DexSnipingException):
    """Base exception for trading-related errors."""
    pass


class OrderExecutionError(TradingException):
    """Exception raised when order execution fails."""
    pass


class InsufficientBalanceError(TradingException):
    """Exception raised when wallet has insufficient balance."""
    pass


class SlippageExceededError(TradingException):
    """Exception raised when trade slippage exceeds maximum allowed."""
    pass


class RiskThresholdExceededError(TradingException):
    """Exception raised when trade risk exceeds acceptable threshold."""
    pass


class ArbitrageException(DexSnipingException):
    """Base exception for arbitrage-related errors."""
    pass


class ArbitrageOpportunityExpiredError(ArbitrageException):
    """Exception raised when arbitrage opportunity is no longer profitable."""
    pass


class BridgeFailureError(ArbitrageException):
    """Exception raised when cross-chain bridge operation fails."""
    pass


class APIException(DexSnipingException):
    """Base exception for external API errors."""
    pass


class APIRateLimitError(APIException):
    """Exception raised when API rate limit is exceeded."""
    pass


class APIUnauthorizedError(APIException):
    """Exception raised when API authentication fails."""
    pass


class APITimeoutError(APIException):
    """Exception raised when API request times out."""
    pass


class ValidationError(DexSnipingException):
    """Exception raised when data validation fails."""
    pass


class ConfigurationError(DexSnipingException):
    """Exception raised when application configuration is invalid."""
    pass


class DatabaseException(DexSnipingException):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseException):
    """Exception raised when database connection fails."""
    pass


class SecurityException(DexSnipingException):
    """Base exception for security-related errors."""
    pass


class HoneypotDetectedError(SecurityException):
    """Exception raised when a honeypot contract is detected."""
    pass


class MaliciousContractError(SecurityException):
    """Exception raised when a malicious contract is detected."""
    pass


class WalletException(DexSnipingException):
    """Base exception for wallet-related errors."""
    pass


class WalletConnectionError(WalletException):
    """Exception raised when wallet connection fails."""
    pass


class WalletSignatureError(WalletException):
    """Exception raised when wallet signature is invalid."""
    pass


class WorkerException(DexSnipingException):
    """Base exception for background worker errors."""
    pass


class WorkerStartupError(WorkerException):
    """Exception raised when worker fails to start."""
    pass


class WorkerShutdownError(WorkerException):
    """Exception raised when worker fails to shutdown properly."""
    pass


# Error code constants
class ErrorCodes:
    """Constants for error codes used throughout the application."""
    
    # Chain errors
    CHAIN_CONNECTION_FAILED = "CHAIN_001"
    CHAIN_NOT_SUPPORTED = "CHAIN_002"
    CHAIN_RPC_ERROR = "CHAIN_003"
    
    # Token errors
    TOKEN_NOT_FOUND = "TOKEN_001"
    TOKEN_INSUFFICIENT_LIQUIDITY = "TOKEN_002"
    TOKEN_INVALID_CONTRACT = "TOKEN_003"
    
    # Trading errors
    TRADING_INSUFFICIENT_BALANCE = "TRADE_001"
    TRADING_SLIPPAGE_EXCEEDED = "TRADE_002"
    TRADING_ORDER_FAILED = "TRADE_003"
    TRADING_RISK_EXCEEDED = "TRADE_004"
    
    # Arbitrage errors
    ARBITRAGE_OPPORTUNITY_EXPIRED = "ARB_001"
    ARBITRAGE_BRIDGE_FAILED = "ARB_002"
    ARBITRAGE_INSUFFICIENT_PROFIT = "ARB_003"
    
    # API errors
    API_RATE_LIMIT = "API_001"
    API_UNAUTHORIZED = "API_002"
    API_TIMEOUT = "API_003"
    API_INVALID_RESPONSE = "API_004"
    
    # Security errors
    SECURITY_HONEYPOT_DETECTED = "SEC_001"
    SECURITY_MALICIOUS_CONTRACT = "SEC_002"
    SECURITY_SUSPICIOUS_ACTIVITY = "SEC_003"
    
    # Wallet errors
    WALLET_CONNECTION_FAILED = "WALLET_001"
    WALLET_SIGNATURE_INVALID = "WALLET_002"
    WALLET_INSUFFICIENT_GAS = "WALLET_003"
    
    # Worker errors
    WORKER_STARTUP_FAILED = "WORKER_001"
    WORKER_SHUTDOWN_FAILED = "WORKER_002"
    WORKER_TASK_FAILED = "WORKER_003"


def create_error_response(
    exception: DexSnipingException,
    status_code: int = 500
) -> dict:
    """
    Create standardized error response dictionary.
    
    Args:
        exception: The exception instance
        status_code: HTTP status code
        
    Returns:
        Dictionary containing error response data
    """
    return {
        "error": {
            "message": exception.message,
            "code": exception.error_code,
            "type": exception.__class__.__name__,
            "status_code": status_code
        }
    }