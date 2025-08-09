#!/usr/bin/env python3
"""
Windows-Compatible Logging Test
File: test_windows_logging.py

Test script that works properly on Windows without Unicode issues.
"""

import sys
from pathlib import Path

def test_windows_logging():
    """Test the Windows-compatible logging system."""
    print("=== Windows-Compatible Logging Test ===")
    
    try:
        # Test imports
        from app.utils.logger import (
            setup_logger, 
            get_trading_logger,
            get_performance_logger
        )
        print("[SUCCESS] Enhanced logger imports successful")
        
        # Test basic logger
        logger = setup_logger("test.windows", "application")
        logger.info("[TARGET] Testing Windows-compatible logging system")
        logger.warning("[WARN] This is a test warning")
        logger.error("[ERROR] This is a test error")
        print("[SUCCESS] Basic logging test completed")
        
        # Test trading logger
        trading_logger = get_trading_logger("test.trading")
        trading_logger.log_trade_execution({
            "symbol": "ETH/USDC",
            "amount": "1.0",
            "type": "test"
        })
        print("[SUCCESS] Trading logger test completed")
        
        # Test performance logger
        perf_logger = get_performance_logger("test.performance")
        perf_logger.start_timer("test_operation")
        import time
        time.sleep(0.1)
        perf_logger.end_timer("test_operation")
        print("[SUCCESS] Performance logger test completed")
        
        # Check log files
        logs_dir = Path("logs")
        if logs_dir.exists():
            print("\n[FILES] Log files created:")
            for log_file in logs_dir.rglob("*.log"):
                if log_file.stat().st_size > 0:
                    print(f"  [OK] {log_file} ({log_file.stat().st_size} bytes)")
        else:
            print("[WARN] Logs directory not found")
        
        print("\n[SUCCESS] Windows-compatible logging system is working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_windows_logging()
    sys.exit(0 if success else 1)
