#!/usr/bin/env python3
"""
Standalone Test Script
File: test_setup.py

Tests the basic setup without pytest to avoid Web3 plugin conflicts.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that we can import our modules."""
    print("Testing imports...")
    try:
        from app.core.exceptions import TradingError
        print("  ✓ TradingError imported successfully")
        
        from app.utils.logger import setup_logger
        print("  ✓ Logger imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_logger_creation():
    """Test logger creation."""
    print("Testing logger creation...")
    try:
        from app.utils.logger import setup_logger
        
        logger = setup_logger("test")
        print("  ✓ Logger created successfully")
        
        # Test logging
        logger.info("Test log message from setup verification")
        print("  ✓ Logger.info() works")
        
        return True
    except Exception as e:
        print(f"  ✗ Logger test failed: {e}")
        return False


def test_exceptions():
    """Test custom exceptions."""
    print("Testing custom exceptions...")
    try:
        from app.core.exceptions import TradingError, WalletError
        
        # Test exception hierarchy
        assert issubclass(WalletError, TradingError)
        print("  ✓ Exception hierarchy correct")
        
        # Test exception creation
        error = TradingError("Test error")
        assert str(error) == "Test error"
        print("  ✓ Exception creation works")
        
        return True
    except Exception as e:
        print(f"  ✗ Exception test failed: {e}")
        return False


def test_web3_import():
    """Test Web3 import."""
    print("Testing Web3 import...")
    try:
        import web3
        print(f"  ✓ Web3 version: {web3.__version__}")
        return True
    except ImportError as e:
        print(f"  ✗ Web3 not available: {e}")
        return False


def test_fastapi_import():
    """Test FastAPI import."""
    print("Testing FastAPI import...")
    try:
        import fastapi
        print("  ✓ FastAPI imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ FastAPI not available: {e}")
        return False


def test_additional_packages():
    """Test additional required packages."""
    print("Testing additional packages...")
    packages = [
        ("pydantic", "Pydantic"),
        ("eth_account", "eth-account"),
        ("eth_utils", "eth-utils"),
        ("loguru", "Loguru")
    ]
    
    all_success = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✓ {name} imported successfully")
        except ImportError as e:
            print(f"  ✗ {name} not available: {e}")
            all_success = False
    
    return all_success


def run_all_tests():
    """Run all tests."""
    print("🤖 DEX Sniper Pro - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Logger Creation", test_logger_creation),
        ("Custom Exceptions", test_exceptions),
        ("Web3 Import", test_web3_import),
        ("FastAPI Import", test_fastapi_import),
        ("Additional Packages", test_additional_packages)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"  {symbol} {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Setup is working correctly.")
        print("\n📋 Next steps:")
        print("1. Create the full trading engine files")
        print("2. Test the complete trading system")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)