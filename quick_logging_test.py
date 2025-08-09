"""
Quick Logging Test
File: quick_logging_test.py

Simple test to verify the enhanced logging system is working.
"""

import sys
from pathlib import Path

def test_logging():
    """Test the enhanced logging system."""
    print("[TEST] Quick Logging System Test")
    print("=" * 40)
    
    try:
        # Test imports
        from app.utils.logger import (
            setup_logger, 
            log_application_startup,
            get_trading_logger,
            get_performance_logger
        )
        print("[OK] Enhanced logger imports successful")
        
        # Test basic logger
        logger = setup_logger("test.quick", "application")
        logger.info("[TARGET] Testing enhanced logging system")
        logger.warning("[WARN] This is a test warning")
        logger.error("[ERROR] This is a test error")
        print("[OK] Basic logging test completed")
        
        # Test trading logger
        trading_logger = get_trading_logger("test.trading")
        trading_logger.log_trade_execution({
            "symbol": "ETH/USDC",
            "amount": "1.0",
            "type": "test"
        })
        print("[OK] Trading logger test completed")
        
        # Test performance logger
        perf_logger = get_performance_logger("test.performance")
        perf_logger.start_timer("test_operation")
        import time
        time.sleep(0.1)
        perf_logger.end_timer("test_operation")
        print("[OK] Performance logger test completed")
        
        # Check log files
        logs_dir = Path("logs")
        if logs_dir.exists():
            print(f"\n[DIR] Log files created:")
            for log_file in logs_dir.rglob("*.log"):
                if log_file.stat().st_size > 0:
                    print(f"  [OK] {log_file} ({log_file.stat().st_size} bytes)")
        else:
            print("[WARN] Logs directory not found")
        
        print("\n[SUCCESS] Enhanced logging system is working!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1)