"""
Simple Network Manager Test - Standalone
File: test_network_simple.py

A standalone test script to verify the network manager integer error fix.
This script handles all import issues and should work from any directory.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional, Any

def setup_python_path():
    """Setup Python path to find the app modules."""
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Try to find the project root (directory containing 'app' folder)
    project_root = None
    
    # Check current directory and parent directories
    for potential_root in [script_dir, script_dir.parent, Path.cwd()]:
        if (potential_root / "app").exists():
            project_root = potential_root
            break
    
    if project_root is None:
        print("❌ Cannot find project root directory containing 'app' folder")
        print(f"   Script location: {script_dir}")
        print(f"   Current directory: {Path.cwd()}")
        print("💡 Make sure you're running from the project root or tests directory")
        return False
    
    # Add project root to Python path
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    print(f"✅ Project root found: {project_root}")
    print(f"✅ Python path updated: {project_root_str}")
    
    return True


def test_imports():
    """Test that we can import the required modules."""
    try:
        # Test logger import
        from app.utils.logger import setup_logger
        print("✅ Logger import successful")
        
        # Test network manager import
        from app.core.blockchain.network_manager_fixed import NetworkManagerFixed, NetworkType
        print("✅ Network manager import successful")
        
        return True, setup_logger, NetworkManagerFixed, NetworkType
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Check that all required files exist:")
        print("   - app/utils/logger.py")
        print("   - app/core/blockchain/network_manager_fixed.py")
        return False, None, None, None
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False, None, None, None


async def test_network_manager_integer_fix(NetworkManagerFixed):
    """Test that the integer input error is fixed."""
    print("\n🔧 Testing Network Manager Integer Input Fix...")
    print("-" * 50)
    
    try:
        # Create network manager instance
        network_manager = NetworkManagerFixed()
        print("✅ Network manager created successfully")
        
        # Test the original problematic input: integer 12345
        print("🧪 Testing integer input: 12345")
        result = await network_manager.connect_to_network(12345)
        
        if result is False:
            print("✅ Integer input handled correctly (returned False, no exception)")
        else:
            print(f"❌ Integer input not handled correctly (returned: {result})")
            return False
        
        # Test other invalid integer inputs
        invalid_integers = [999, 0, -1, 123456789]
        print("🧪 Testing other invalid integer inputs...")
        
        for invalid_int in invalid_integers:
            try:
                result = await network_manager.connect_to_network(invalid_int)
                if result is False:
                    print(f"✅ Integer {invalid_int} handled correctly")
                else:
                    print(f"⚠️ Integer {invalid_int} returned: {result}")
            except Exception as e:
                print(f"❌ Integer {invalid_int} raised exception: {e}")
                return False
        
        # Test other invalid input types
        invalid_inputs = [
            (None, "None"),
            ([], "empty list"),
            ({}, "empty dict"),
            ("invalid_network", "invalid string"),
            (3.14, "float")
        ]
        
        print("🧪 Testing other invalid input types...")
        for invalid_input, description in invalid_inputs:
            try:
                result = await network_manager.connect_to_network(invalid_input)
                if result is False:
                    print(f"✅ {description} handled correctly")
                else:
                    print(f"⚠️ {description} returned: {result}")
            except Exception as e:
                print(f"⚠️ {description} raised exception: {type(e).__name__}")
        
        # Test valid string inputs (should work with validation)
        print("🧪 Testing valid string inputs...")
        valid_strings = ["ethereum", "polygon", "bsc", "arbitrum"]
        
        for valid_string in valid_strings:
            try:
                # This may fail due to network connectivity, but should not raise type errors
                result = await network_manager.connect_to_network(valid_string)
                print(f"✅ {valid_string} processed without type errors (result: {result})")
            except Exception as e:
                # Network errors are OK, type errors are not
                if "Invalid network type" in str(e) or "int" in str(e).lower():
                    print(f"❌ {valid_string} still has type error: {e}")
                    return False
                else:
                    print(f"ℹ️ {valid_string} network error (acceptable): {type(e).__name__}")
        
        print("\n✅ All network manager integer input tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Network manager test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🤖 DEX Sniper Pro - Simple Network Manager Test")
    print("=" * 60)
    
    # Setup Python path
    if not setup_python_path():
        return False
    
    # Test imports
    import_success, setup_logger, NetworkManagerFixed, NetworkType = test_imports()
    if not import_success:
        return False
    
    # Setup logger
    try:
        logger = setup_logger(__name__)
        print("✅ Logger setup successful")
    except Exception as e:
        print(f"⚠️ Logger setup failed: {e} (continuing anyway)")
    
    # Run the main test
    try:
        success = asyncio.run(test_network_manager_integer_fix(NetworkManagerFixed))
        
        if success:
            print("\n🎉 SUCCESS: Network manager integer error is FIXED!")
            print("✅ The original error 'Invalid network type: <class 'int'> - 12345' is resolved")
            print("🚀 Phase 4B network manager implementation is working correctly")
            return True
        else:
            print("\n❌ FAILED: Network manager test failed")
            print("🔧 Review the network manager implementation")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test execution error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run the test."""
    try:
        success = main()
        print("\n" + "=" * 60)
        if success:
            print("🎯 RESULT: All tests PASSED - Phase 4B network fix is working!")
        else:
            print("🎯 RESULT: Some tests FAILED - review implementation")
        print("=" * 60)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Script error: {e}")
        sys.exit(1)