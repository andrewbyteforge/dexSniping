"""
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
