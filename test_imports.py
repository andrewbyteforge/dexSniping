"""
Test Imports Script - Enhanced
File: test_imports.py

Quick test to verify that all import issues are resolved.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_logger_import():
    """Test importing logger utilities."""
    print("🧪 Testing logger import...")
    
    try:
        from app.utils.logger import setup_logger
        print("✅ Successfully imported setup_logger")
        
        # Test creating logger instance
        logger = setup_logger(__name__)
        print(f"✅ Logger instance created: {logger}")
        
        # Test basic logging
        logger.info("Test log message")
        print("✅ Basic logging works")
        
        return True
        
    except ImportError as e:
        print(f"❌ Logger import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Logger test error: {e}")
        return False

def test_core_exceptions():
    """Test importing core exceptions."""
    print("🧪 Testing core exceptions import...")
    
    try:
        from app.core.exceptions import PerformanceError, TradingError
        print("✅ Successfully imported PerformanceError and TradingError")
        
        # Test creating instances
        perf_error = PerformanceError("Test performance error")
        trading_error = TradingError("Test trading error")
        
        print(f"✅ PerformanceError instance: {perf_error}")
        print(f"✅ TradingError instance: {trading_error}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_performance_optimizer():
    """Test importing the performance optimizer."""
    print("🧪 Testing performance optimizer import...")
    
    try:
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
        print("✅ Successfully imported TradingPerformanceOptimizer")
        
        # Test creating instance
        from app.core.performance.trading_optimizer import OptimizationLevel
        optimizer = TradingPerformanceOptimizer(OptimizationLevel.BALANCED)
        print(f"✅ TradingPerformanceOptimizer instance: {optimizer}")
        
        # Test gas optimizer import
        from app.core.performance.gas_optimizer import GasOptimizationEngine, GasStrategy
        gas_optimizer = GasOptimizationEngine()
        print("✅ GasOptimizationEngine imported and created successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("🔧 Checking specific import...")
        
        # Try individual imports to isolate the issue
        try:
            from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
            print("✅ TradingPerformanceOptimizer imports fine")
        except ImportError as e2:
            print(f"❌ TradingPerformanceOptimizer import failed: {e2}")
        
        try:
            from app.core.performance.gas_optimizer import GasOptimizationEngine
            print("✅ GasOptimizationEngine imports fine")
        except ImportError as e3:
            print(f"❌ GasOptimizationEngine import failed: {e3}")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_order_executor():
    """Test importing order executor components."""
    print("🧪 Testing order executor import...")
    
    try:
        from app.core.trading.order_executor import Order, OrderSide, OrderType
        print("✅ Successfully imported Order, OrderSide, OrderType")
        
        # Test creating instances
        from decimal import Decimal
        order = Order(
            order_id="test-123",
            token_address="0x1234567890123456789012345678901234567890",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            amount=Decimal("100"),
            symbol="TEST"
        )
        print(f"✅ Order instance created: {order}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_specific_gas_optimization_error():
    """Test the specific GasOptimizationError import that's failing."""
    print("🧪 Testing GasOptimizationError import...")
    
    try:
        # This is the exact import that's failing
        from app.core.exceptions import GasOptimizationError
        print("✅ GasOptimizationError import successful")
        
        # Test creating instance
        error = GasOptimizationError("Test gas optimization error")
        print(f"✅ GasOptimizationError instance: {error}")
        
        return True
        
    except ImportError as e:
        print(f"❌ GasOptimizationError import failed: {e}")
        
        # Check what's actually in the exceptions module
        try:
            import app.core.exceptions as exc_module
            print(f"✅ Exceptions module loaded")
            print(f"📋 Available exceptions: {[name for name in dir(exc_module) if 'Error' in name][:10]}...")
            
            # Check if GasOptimizationError is in __all__
            if hasattr(exc_module, '__all__'):
                gas_errors = [name for name in exc_module.__all__ if 'Gas' in name]
                print(f"📋 Gas-related errors in __all__: {gas_errors}")
        except Exception as e2:
            print(f"❌ Could not examine exceptions module: {e2}")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    """Test all imports that Phase 5A.1 test needs."""
    print("🧪 Testing all Phase 5A.1 imports together...")
    
    try:
        # All the imports that the Phase 5A.1 test tries to do
        from app.utils.logger import setup_logger
        from app.core.exceptions import TradingError, PerformanceError
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer, TradeProfitAnalysis
        from app.core.trading.order_executor import Order, OrderSide, OrderType
        from app.core.performance.gas_optimizer import GasOptimizationEngine, GasStrategy, GasPrice
        from app.core.blockchain.network_manager import get_network_manager, NetworkType
        
        print("✅ All Phase 5A.1 imports successful!")
        
        # Test creating instances like the test does
        logger = setup_logger(__name__)
        optimizer = TradingPerformanceOptimizer("balanced")  # Test string input
        network_manager = get_network_manager()
        
        print("✅ Component instances created successfully")
        print(f"✅ Optimizer level: {optimizer.optimization_level}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Phase 5A.1 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Phase 5A.1 test error: {e}")
        return False

def test_all_phase5a1_imports():
    """Test all imports that Phase 5A.1 test needs."""
    print("🧪 Testing all Phase 5A.1 imports together...")
    
    try:
        # All the imports that the Phase 5A.1 test tries to do
        from app.utils.logger import setup_logger
        from app.core.exceptions import TradingError, PerformanceError
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer, TradeProfitAnalysis
        from app.core.trading.order_executor import Order, OrderSide, OrderType
        from app.core.performance.gas_optimizer import GasOptimizationEngine, GasStrategy, GasPrice
        from app.core.blockchain.network_manager import get_network_manager, NetworkType
        
        print("✅ All Phase 5A.1 imports successful!")
        
        # Test creating instances like the test does
        logger = setup_logger(__name__)
        optimizer = TradingPerformanceOptimizer("balanced")  # Test string input
        network_manager = get_network_manager()
        
        print("✅ Component instances created successfully")
        print(f"✅ Optimizer level: {optimizer.optimization_level}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Phase 5A.1 import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Phase 5A.1 test error: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 Testing Import Fixes - Enhanced")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # Test 1: Logger
    if test_logger_import():
        success_count += 1
    print()
    
    # Test 2: Core exceptions
    if test_core_exceptions():
        success_count += 1
    print()
    
    # Test 3: Performance optimizer
    if test_performance_optimizer():
        success_count += 1
    print()
    
    # Test 4: Order executor
    if test_order_executor():
        success_count += 1
    print()
    
    # Test 5: Specific GasOptimizationError
    if test_specific_gas_optimization_error():
        success_count += 1
    print()
    
    # Test 6: All Phase 5A.1 imports together
    if test_all_phase5a1_imports():
        success_count += 1
    print()
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All imports working! Phase 5A.1 test should now pass.")
        print("🚀 Run Phase 5A.1 test: python test_phase_5a1_simple.py")
        return True
    else:
        print("❌ Some imports still failing. Need additional fixes.")
        print(f"🔧 {total_tests - success_count} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Additional troubleshooting needed")
        print("   Check the specific import error messages above")