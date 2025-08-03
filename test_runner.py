#!/usr/bin/env python3
"""
Test Runner for Phase 4C WebSocket Integration
File: test_runner.py

Simple test runner that properly handles Python paths and dependencies.
"""

import os
import sys
import subprocess
import time
import urllib.request
import urllib.error


def check_server_running(url="http://localhost:8000", timeout=5):
    """Check if the server is running."""
    try:
        response = urllib.request.urlopen(f"{url}/health", timeout=timeout)
        return response.getcode() == 200
    except (urllib.error.URLError, Exception):
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['aiohttp', 'websockets', 'fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing dependencies: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def run_quick_test():
    """Run the quick WebSocket test."""
    print("🚀 Running quick WebSocket integration test...")
    
    # Check if server is running
    if not check_server_running():
        print("❌ Server not running!")
        print("Please start the server first:")
        print("   uvicorn app.main:app --reload")
        return False
    
    print("✅ Server is running")
    
    # Add current directory to Python path
    current_dir = os.getcwd()
    env = os.environ.copy()
    env['PYTHONPATH'] = current_dir + os.pathsep + env.get('PYTHONPATH', '')
    
    # Run the quick test script
    try:
        result = subprocess.run([
            sys.executable, 'test_phase4c.py'
        ], env=env, capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except FileNotFoundError:
        print("❌ test_phase4c.py not found")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def run_websocket_tests():
    """Run the WebSocket integration tests."""
    print("🧪 Running WebSocket integration tests...")
    
    # Add current directory to Python path
    current_dir = os.getcwd()
    env = os.environ.copy()
    env['PYTHONPATH'] = current_dir + os.pathsep + env.get('PYTHONPATH', '')
    
    # Run the test script
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/test_websocket_integration.py', '-v'
        ], env=env, capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False


def main():
    """Main test runner function."""
    print("🤖 DEX Sniper Pro - Phase 4C Test Runner")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("✅ Dependencies check passed")
    
    # Check server
    if not check_server_running():
        print("❌ Server not running!")
        print("\nTo start the server:")
        print("   uvicorn app.main:app --reload")
        print("\nThen run this test again.")
        return 1
    
    print("✅ Server is running")
    
    # Run quick test
    print("\n" + "=" * 50)
    quick_test_success = run_quick_test()
    
    if quick_test_success:
        print("✅ Quick test passed")
    else:
        print("❌ Quick test failed")
    
    # Ask user if they want to run full tests
    print("\n" + "=" * 50)
    try:
        if input("Run full WebSocket integration tests? (y/N): ").lower().startswith('y'):
            full_test_success = run_websocket_tests()
            if full_test_success:
                print("✅ Full tests passed")
            else:
                print("❌ Full tests failed")
        else:
            print("⏭️ Skipping full tests")
            full_test_success = True
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Quick test: {'✅ PASSED' if quick_test_success else '❌ FAILED'}")
    
    if quick_test_success:
        print("\n🎯 Next steps:")
        print("1. Open http://localhost:8000/dashboard/live to see the live dashboard")
        print("2. Open http://localhost:8000/api/v1/ws/test to test WebSocket connections")
        print("3. Check http://localhost:8000/docs for complete API documentation")
        print("\n🚀 Phase 4C: Live Dashboard Integration - READY")
    
    return 0 if quick_test_success else 1


if __name__ == "__main__":
    sys.exit(main())