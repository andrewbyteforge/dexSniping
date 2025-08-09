"""
Quick Import Test
File: quick_test.py

Quick test to verify gas optimizer import works.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gas_optimizer():
    """Test gas optimizer import specifically."""
    print("🧪 Testing gas optimizer import...")
    
    try:
        from app.core.performance.gas_optimizer import GasOptimizationEngine, GasStrategy, GasPrice
        print("✅ Gas optimizer imports successful")
        
        # Test creating instance
        engine = GasOptimizationEngine()
        print("✅ Gas optimization engine created")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in gas optimizer: {e}")
        print(f"   File: {e.filename}")
        print(f"   Line: {e.lineno}")
        print(f"   Text: {e.text}")
        return False
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_performance_optimizer():
    """Test performance optimizer import."""
    print("🧪 Testing performance optimizer import...")
    
    try:
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
        print("✅ Trading performance optimizer imports successful")
        
        # Test creating instance
        optimizer = TradingPerformanceOptimizer("balanced")
        print("✅ Trading performance optimizer created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🔧 Quick Import Test")
    print("=" * 30)
    
    success_count = 0
    
    # Test gas optimizer
    if test_gas_optimizer():
        success_count += 1
    print()
    
    # Test performance optimizer  
    if test_performance_optimizer():
        success_count += 1
    print()
    
    print(f"📊 Results: {success_count}/2 tests passed")
    
    if success_count == 2:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    main()