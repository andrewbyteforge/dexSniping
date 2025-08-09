#!/usr/bin/env python3
"""
Fix Missing Exception Classes
File: fix_missing_exceptions.py

Adds all required exception classes to app/core/exceptions.py
"""

import os
from pathlib import Path


def fix_exceptions_file():
    """Fix the exceptions.py file by adding all required exception classes."""
    
    exceptions_file = Path("app/core/exceptions.py")
    
    # Create the file if it doesn't exist
    if not exceptions_file.exists():
        print("Creating new exceptions.py file...")
        exceptions_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Read existing content if any
        existing_content = ""
        if exceptions_file.exists():
            existing_content = exceptions_file.read_text(encoding='utf-8')
        
        # Define all required exception classes
        complete_exceptions_content = '''"""
Core Trading Bot Exceptions
File: app/core/exceptions.py

Comprehensive exception hierarchy for the DEX Sniper Pro trading bot.
"""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""
    pass


class DatabaseError(TradingBotError):
    """Database operation errors."""
    pass


class NetworkError(TradingBotError):
    """Network connection and communication errors."""
    pass


class TradingError(TradingBotError):
    """Trading operation errors."""
    pass


class InsufficientFundsError(TradingError):
    """Insufficient funds for trading operations."""
    pass


class ConfigurationError(TradingBotError):
    """Configuration validation and setup errors."""
    pass


class ValidationError(TradingBotError):
    """Data validation errors."""
    pass


class AuthenticationError(TradingBotError):
    """Authentication and authorization errors."""
    pass


class RateLimitError(TradingBotError):
    """API rate limit exceeded errors."""
    pass


# AI and ML specific exceptions
class AIAnalysisError(TradingBotError):
    """AI analysis and machine learning errors."""
    pass


class HoneypotDetectionError(AIAnalysisError):
    """Honeypot detection specific errors."""
    pass


class RiskAssessmentError(AIAnalysisError):
    """Risk assessment calculation errors."""
    pass


class ModelLoadError(AIAnalysisError):
    """Machine learning model loading errors."""
    pass


class SentimentAnalysisError(AIAnalysisError):
    """Sentiment analysis processing errors."""
    pass


class PredictionError(AIAnalysisError):
    """Price and trend prediction errors."""
    pass


# Blockchain and DEX specific exceptions
class BlockchainError(TradingBotError):
    """Blockchain interaction errors."""
    pass


class ContractError(BlockchainError):
    """Smart contract interaction errors."""
    pass


class TransactionError(BlockchainError):
    """Transaction execution errors."""
    pass


class GasEstimationError(TransactionError):
    """Gas estimation and optimization errors."""
    pass


class SlippageError(TradingError):
    """Slippage tolerance exceeded errors."""
    pass


class LiquidityError(TradingError):
    """Insufficient liquidity errors."""
    pass


# Wallet and security exceptions
class WalletError(TradingBotError):
    """Wallet connection and management errors."""
    pass


class WalletConnectionError(WalletError):
    """Wallet connection specific errors."""
    pass


class WalletSigningError(WalletError):
    """Transaction signing errors."""
    pass


class SecurityError(TradingBotError):
    """Security and safety check errors."""
    pass


# WebSocket and streaming exceptions
class WebSocketError(TradingBotError):
    """WebSocket connection and streaming errors."""
    pass


class StreamingError(TradingBotError):
    """Real-time data streaming errors."""
    pass


class ConnectionTimeoutError(NetworkError):
    """Connection timeout errors."""
    pass


# Strategy and execution exceptions
class StrategyError(TradingBotError):
    """Trading strategy errors."""
    pass


class ExecutionError(TradingError):
    """Trade execution specific errors."""
    pass


class OrderError(TradingError):
    """Order placement and management errors."""
    pass


class PositionError(TradingError):
    """Position management errors."""
    pass


# Data and API exceptions
class DataError(TradingBotError):
    """Data processing and validation errors."""
    pass


class APIError(TradingBotError):
    """External API interaction errors."""
    pass


class CacheError(TradingBotError):
    """Caching system errors."""
    pass


class ParsingError(DataError):
    """Data parsing and formatting errors."""
    pass


# System and performance exceptions
class SystemError(TradingBotError):
    """System-level errors."""
    pass


class PerformanceError(SystemError):
    """Performance and resource errors."""
    pass


class CircuitBreakerError(SystemError):
    """Circuit breaker activation errors."""
    pass


class ResourceError(SystemError):
    """Resource allocation and management errors."""
    pass


# Custom exception with additional context
class TradingBotException(TradingBotError):
    """
    Enhanced exception with additional context.
    
    Provides structured error information including:
    - Error code
    - Component that failed
    - Suggested actions
    - Timestamp
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None,
        component: str = None,
        suggested_action: str = None,
        original_error: Exception = None
    ):
        """
        Initialize enhanced exception.
        
        Args:
            message: Error description
            error_code: Unique error identifier
            component: Component that generated the error
            suggested_action: Recommended resolution steps
            original_error: Original exception if this is a wrapper
        """
        super().__init__(message)
        self.error_code = error_code
        self.component = component
        self.suggested_action = suggested_action
        self.original_error = original_error
        self.timestamp = None
        
        # Set timestamp when exception is created
        from datetime import datetime
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary format."""
        return {
            "message": str(self),
            "error_code": self.error_code,
            "component": self.component,
            "suggested_action": self.suggested_action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "original_error": str(self.original_error) if self.original_error else None
        }
    
    def __str__(self) -> str:
        """String representation with enhanced context."""
        base_msg = super().__str__()
        
        if self.component:
            base_msg = f"[{self.component}] {base_msg}"
        
        if self.error_code:
            base_msg = f"{base_msg} (Code: {self.error_code})"
        
        return base_msg


# Error code constants for standardized error handling
class ErrorCodes:
    """Standardized error codes for the trading bot."""
    
    # Database errors
    DB_CONNECTION_FAILED = "DB001"
    DB_QUERY_FAILED = "DB002"
    DB_TRANSACTION_FAILED = "DB003"
    
    # Trading errors
    TRADE_EXECUTION_FAILED = "TR001"
    INSUFFICIENT_BALANCE = "TR002"
    SLIPPAGE_EXCEEDED = "TR003"
    
    # AI/ML errors
    MODEL_LOAD_FAILED = "AI001"
    PREDICTION_FAILED = "AI002"
    RISK_ASSESSMENT_FAILED = "AI003"
    
    # Network errors
    CONNECTION_TIMEOUT = "NET001"
    API_RATE_LIMITED = "NET002"
    BLOCKCHAIN_ERROR = "NET003"
    
    # Configuration errors
    INVALID_CONFIG = "CFG001"
    MISSING_API_KEY = "CFG002"
    
    # Security errors
    WALLET_CONNECTION_FAILED = "SEC001"
    SIGNATURE_FAILED = "SEC002"
    HONEYPOT_DETECTED = "SEC003"


# Utility functions for exception handling
def create_trading_exception(
    message: str,
    error_code: str = None,
    component: str = None,
    suggested_action: str = None,
    original_error: Exception = None
) -> TradingBotException:
    """
    Create a standardized trading bot exception.
    
    Args:
        message: Error description
        error_code: Error code from ErrorCodes class
        component: Component that failed
        suggested_action: Recommended resolution
        original_error: Original exception
        
    Returns:
        TradingBotException: Formatted exception
    """
    return TradingBotException(
        message=message,
        error_code=error_code,
        component=component,
        suggested_action=suggested_action,
        original_error=original_error
    )


def handle_exception_gracefully(
    func_name: str,
    error: Exception,
    default_return=None,
    log_error: bool = True
):
    """
    Handle exceptions gracefully with logging and fallback.
    
    Args:
        func_name: Name of function that failed
        error: Exception that occurred
        default_return: Default value to return
        log_error: Whether to log the error
        
    Returns:
        Default return value
    """
    if log_error:
        try:
            # Try to import logger, but don't fail if not available
            from app.utils.logger import setup_logger
            logger = setup_logger(__name__)
            logger.error(f"[ERROR] Function {func_name} failed: {error}")
        except:
            # Fallback to print if logger not available
            print(f"[ERROR] Function {func_name} failed: {error}")
    
    return default_return


# Exception hierarchy validation
def validate_exception_hierarchy():
    """Validate that all exceptions inherit from TradingBotError."""
    import inspect
    
    # Get all classes in this module
    current_module = __import__(__name__)
    
    issues = []
    
    for name, obj in inspect.getmembers(current_module):
        if (inspect.isclass(obj) and 
            issubclass(obj, Exception) and 
            obj != TradingBotError and
            obj != TradingBotException and
            not issubclass(obj, TradingBotError)):
            issues.append(f"Exception {name} does not inherit from TradingBotError")
    
    return issues


# Export all exception classes
__all__ = [
    # Base exceptions
    'TradingBotError',
    'TradingBotException',
    
    # Core exceptions
    'DatabaseError',
    'NetworkError', 
    'TradingError',
    'ConfigurationError',
    'ValidationError',
    'AuthenticationError',
    'RateLimitError',
    
    # AI exceptions
    'AIAnalysisError',
    'HoneypotDetectionError',
    'RiskAssessmentError',
    'ModelLoadError',
    'SentimentAnalysisError',
    'PredictionError',
    
    # Blockchain exceptions
    'BlockchainError',
    'ContractError',
    'TransactionError',
    'GasEstimationError',
    'SlippageError',
    'LiquidityError',
    
    # Wallet exceptions
    'WalletError',
    'WalletConnectionError',
    'WalletSigningError',
    'SecurityError',
    
    # Streaming exceptions
    'WebSocketError',
    'StreamingError',
    'ConnectionTimeoutError',
    
    # Strategy exceptions
    'StrategyError',
    'ExecutionError',
    'OrderError',
    'PositionError',
    
    # Data exceptions
    'DataError',
    'APIError',
    'CacheError',
    'ParsingError',
    
    # System exceptions
    'SystemError',
    'PerformanceError',
    'CircuitBreakerError',
    'ResourceError',
    
    # Trading specific
    'InsufficientFundsError',
    
    # Utilities
    'ErrorCodes',
    'create_trading_exception',
    'handle_exception_gracefully',
    'validate_exception_hierarchy'
]
'''
        
        # Write the complete exceptions file
        exceptions_file.write_text(complete_exceptions_content, encoding='utf-8')
        
        print("✅ Created comprehensive exceptions.py with all required classes")
        return True
        
    except Exception as e:
        print(f"❌ Error creating exceptions.py: {e}")
        return False


def check_for_other_missing_imports():
    """Check for other potential missing import issues."""
    
    # Check if other commonly referenced modules exist
    modules_to_check = [
        ("app/core/cache/cache_manager.py", "CacheManager"),
        ("app/core/performance/circuit_breaker.py", "CircuitBreakerManager"), 
        ("app/core/risk/risk_calculator.py", "RiskFactors"),
        ("app/models/token.py", "Token"),
        ("app/schemas/token.py", "TokenInfo"),
        ("app/core/blockchain/base_chain.py", "BaseChain")
    ]
    
    missing_modules = []
    
    for module_path, class_name in modules_to_check:
        module_file = Path(module_path)
        if not module_file.exists():
            missing_modules.append((module_path, class_name))
    
    if missing_modules:
        print(f"⚠️ Warning: {len(missing_modules)} optional modules not found:")
        for module_path, class_name in missing_modules:
            print(f"   - {module_path} ({class_name})")
        print("These are optional and won't prevent testing.")
    else:
        print("✅ All commonly referenced modules exist")
    
    return len(missing_modules) == 0


def main():
    """Main fix function."""
    print("🔧 Fixing Missing Exception Classes")
    print("=" * 60)
    
    # Fix 1: Create comprehensive exceptions file
    print("1. Creating comprehensive exceptions.py...")
    exceptions_fixed = fix_exceptions_file()
    
    # Fix 2: Check for other missing imports
    print("\n2. Checking for other missing imports...")
    check_for_other_missing_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("Fix Summary:")
    print("=" * 60)
    
    if exceptions_fixed:
        print("✅ Exception classes fixed successfully")
        print("\nNext steps:")
        print("1. Run: python test_simple.py")
        print("2. If successful, try: python test_all_features.py")
        print("3. All exception imports should now work")
    else:
        print("❌ Failed to fix exception classes")
        print("Manual intervention required")
    
    return exceptions_fixed


if __name__ == "__main__":
    """Run the exception fixes."""
    success = main()
    exit(0 if success else 1)