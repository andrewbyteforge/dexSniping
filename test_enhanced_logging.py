#!/usr/bin/env python3
"""
Test Enhanced Logging System
File: test_enhanced_logging.py

Test script to verify the enhanced logging system works correctly.
"""

import asyncio
import time
from pathlib import Path

from app.utils.logger import (
    setup_logger,
    get_trading_logger, 
    get_performance_logger,
    log_application_startup,
    log_application_shutdown
)


def test_basic_logging():
    """Test basic logging functionality."""
    print("🧪 Testing basic logging...")
    
    # Test different component loggers
    app_logger = setup_logger("test.application", "application")
    api_logger = setup_logger("test.api", "api") 
    trading_logger = setup_logger("test.trading", "trading")
    db_logger = setup_logger("test.database", "database")
    
    # Test different log levels
    app_logger.debug("🔍 Debug message from application")
    app_logger.info("ℹ️ Info message from application")
    app_logger.warning("⚠️ Warning message from application")
    app_logger.error("❌ Error message from application")
    
    api_logger.info("📡 API request processed")
    trading_logger.info("💰 Trade executed successfully") 
    db_logger.info("💾 Database query completed")
    
    print("✅ Basic logging test completed")


def test_specialized_loggers():
    """Test specialized logging functionality."""
    print("🧪 Testing specialized loggers...")
    
    # Test trading logger
    trading_logger = get_trading_logger("test.trading_specialized")
    
    trading_logger.log_trade_execution({
        "symbol": "ETH/USDC",
        "amount": "1.5",
        "price": "2500.00",
        "type": "buy"
    })
    
    trading_logger.log_trade_opportunity({
        "token": "PEPE",
        "opportunity_type": "price_surge",
        "confidence": 0.85
    })
    
    trading_logger.log_wallet_connection("0x123...abc", "connected")
    
    # Test performance logger
    perf_logger = get_performance_logger("test.performance")
    
    perf_logger.start_timer("test_operation")
    time.sleep(0.1)  # Simulate work
    perf_logger.end_timer("test_operation")
    
    perf_logger.log_performance_metrics({
        "response_time": "0.1s",
        "memory_usage": "50MB",
        "cpu_usage": "5%"
    })
    
    print("✅ Specialized loggers test completed")


def test_file_creation():
    """Test that log files are created correctly."""
    print("🧪 Testing log file creation...")
    
    logs_dir = Path("logs")
    expected_files = [
        "logs/application/dex_sniper.log",
        "logs/application/daily.log",
        "logs/trading/trading.log",
        "logs/api/api.log",
        "logs/database/database.log",
        "logs/errors/errors.log"
    ]
    
    # Trigger logging to create files
    app_logger = setup_logger("test.file_creation", "application")
    app_logger.info("📁 Testing file creation")
    
    trading_logger = get_trading_logger("test.file_creation")
    trading_logger.log_trade_execution({"test": "data"})
    
    # Check if files exist
    created_files = []
    missing_files = []
    
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            created_files.append(file_path)
            print(f"  ✅ Created: {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ Missing: {file_path}")
    
    print(f"✅ File creation test: {len(created_files)}/{len(expected_files)} files created")
    
    return len(missing_files) == 0


def main():
    """Run all logging tests."""
    print("🚀 Enhanced Logging System Test")
    print("=" * 50)
    
    # Test startup/shutdown logging
    log_application_startup()
    
    # Run tests
    test_basic_logging()
    test_specialized_loggers()
    files_ok = test_file_creation()
    
    # Test shutdown logging
    log_application_shutdown()
    
    print("=" * 50)
    if files_ok:
        print("🎉 All logging tests passed!")
        print("📁 Check the logs/ directory for log files")
    else:
        print("⚠️ Some tests failed - check the logs directory")
    
    return files_ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
