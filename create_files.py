#!/usr/bin/env python3
"""
Create Project Files Script
File: create_files.py

Creates all the necessary trading engine files for the DEX Sniper Pro project.
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure."""
    directories = [
        "app",
        "app/core",
        "app/core/wallet",
        "app/core/dex", 
        "app/core/trading",
        "app/core/portfolio",
        "app/core/analytics",
        "app/api",
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/utils",
        "app/models",
        "app/models/dex",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists() and directory.startswith("app"):
            init_file.write_text('"""Package initialization."""\n')
    
    print("Directory structure created")

def create_core_exception_file():
    """Create the core exceptions file."""
    exceptions_content = '''"""
Core Exceptions
File: app/core/exceptions.py

Custom exceptions for the trading platform.
"""


class TradingError(Exception):
    """Base exception for trading operations."""
    pass


class WalletError(TradingError):
    """Wallet-related errors."""
    pass


class DEXError(TradingError):
    """DEX integration errors."""
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
'''
    
    with open("app/core/exceptions.py", "w", encoding='utf-8') as f:
        f.write(exceptions_content)
    
    print("Created app/core/exceptions.py")

def create_logger_file():
    """Create the logger utility file."""
    logger_content = '''"""
Logger Utility
File: app/utils/logger.py

Centralized logging configuration for the trading platform.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    if LOGURU_AVAILABLE:
        # Use loguru if available
        return LoguruWrapper(name)
    
    # Fallback to standard logging
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger


class LoguruWrapper:
    """Wrapper to make loguru compatible with standard logging interface."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = loguru_logger
    
    def info(self, message: str, *args, **kwargs):
        self.logger.info(f"[{self.name}] {message}", *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.logger.error(f"[{self.name}] {message}", *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(f"[{self.name}] {message}", *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(f"[{self.name}] {message}", *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(f"[{self.name}] {message}", *args, **kwargs)
'''
    
    Path("app/utils").mkdir(exist_ok=True)
    with open("app/utils/logger.py", "w", encoding='utf-8') as f:
        f.write(logger_content)
    
    print("Created app/utils/logger.py")

def create_simple_test_file():
    """Create a simple test file to verify setup."""
    test_content = '''"""
Simple Trading Engine Tests
File: tests/test_simple.py

Basic tests to verify the setup is working.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that we can import our modules."""
    try:
        from app.core.exceptions import TradingError
        from app.utils.logger import setup_logger
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_logger_creation():
    """Test logger creation."""
    from app.utils.logger import setup_logger
    
    logger = setup_logger("test")
    assert logger is not None
    
    # Test logging
    logger.info("Test log message")


def test_exceptions():
    """Test custom exceptions."""
    from app.core.exceptions import TradingError, WalletError
    
    # Test exception hierarchy
    assert issubclass(WalletError, TradingError)
    
    # Test exception creation
    error = TradingError("Test error")
    assert str(error) == "Test error"


def test_web3_import():
    """Test Web3 import."""
    try:
        import web3
        print(f"Web3 version: {web3.__version__}")
        assert True
    except ImportError:
        pytest.fail("Web3 not available")


def test_fastapi_import():
    """Test FastAPI import."""
    try:
        import fastapi
        print("FastAPI imported successfully")
        assert True
    except ImportError:
        pytest.fail("FastAPI not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    with open("tests/test_simple.py", "w", encoding='utf-8') as f:
        f.write(test_content)
    
    print("Created tests/test_simple.py")

def main():
    """Main setup function."""
    print("🤖 Creating DEX Sniper Pro Project Files")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    # Create core files
    create_core_exception_file()
    create_logger_file()
    create_simple_test_file()
    
    print("\nBasic project structure created!")
    print("\nNext steps:")
    print("1. Run simple test: python -m pytest tests/test_simple.py -v")
    print("2. If tests pass, we'll create the full trading engine files")
    print("3. Then run the complete test suite")
    
    return True


if __name__ == "__main__":
    main()