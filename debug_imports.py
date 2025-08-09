"""
Debug Import Issues
File: debug_imports.py

Isolate and fix import issues step by step.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_step_by_step():
    """Test imports step by step to isolate the issue."""
    print("🔧 Debug Import Issues - Step by Step")
    print("=" * 50)
    
    # Step 1: Test basic logger
    print("Step 1: Testing logger...")
    try:
        from app.utils.logger import setup_logger
        print("✅ Logger import successful")
    except Exception as e:
        print(f"❌ Logger import failed: {e}")
        return
    
    # Step 2: Test core exceptions
    print("\nStep 2: Testing core exceptions...")
    try:
        from app.core.exceptions import PerformanceError, TradingError
        print("✅ Core exceptions import successful")
        
        # Check if GasOptimizationError exists
        try:
            from app.core.exceptions import GasOptimizationError
            print("✅ GasOptimizationError found in exceptions")
        except ImportError:
            print("❌ GasOptimizationError NOT found in exceptions")
        
    except Exception as e:
        print(f"❌ Core exceptions import failed: {e}")
        return
    
    # Step 3: Test order executor
    print("\nStep 3: Testing order executor...")
    try:
        from app.core.trading.order_executor import Order, OrderSide, OrderType
        print("✅ Order executor import successful")
    except Exception as e:
        print(f"❌ Order executor import failed: {e}")
        return
    
    # Step 4: Test trading optimizer (without gas optimizer)
    print("\nStep 4: Testing trading optimizer...")
    try:
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
        print("✅ Trading optimizer import successful")
    except Exception as e:
        print(f"❌ Trading optimizer import failed: {e}")
        return
    
    # Step 5: Test gas optimizer separately
    print("\nStep 5: Testing gas optimizer...")
    try:
        from app.core.performance.gas_optimizer import GasOptimizationEngine
        print("✅ Gas optimizer import successful")
    except Exception as e:
        print(f"❌ Gas optimizer import failed: {e}")
        print(f"Error details: {e}")
        
        # Try to import gas optimizer dependencies one by one
        print("\nTesting gas optimizer dependencies...")
        try:
            from app.utils.logger import setup_logger
            print("✅ Gas optimizer - logger dependency OK")
        except Exception as e2:
            print(f"❌ Gas optimizer - logger dependency failed: {e2}")
        
        try:
            from app.core.exceptions import PerformanceError, NetworkError
            print("✅ Gas optimizer - basic exceptions OK")
        except Exception as e3:
            print(f"❌ Gas optimizer - basic exceptions failed: {e3}")
        
        return
    
    # Step 6: Test network manager
    print("\nStep 6: Testing network manager...")
    try:
        from app.core.blockchain.network_manager import NetworkManager, NetworkType
        print("✅ Network manager import successful")
    except Exception as e:
        print(f"❌ Network manager import failed: {e}")
        return
    
    print("\n🎉 All imports successful!")

if __name__ == "__main__":
    test_step_by_step()