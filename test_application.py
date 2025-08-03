#!/usr/bin/env python3
"""
Application Test and Validation Script
File: test_application.py

Comprehensive testing to ensure the application is working correctly.
"""

import asyncio
import httpx
import os
import sys
from datetime import datetime


async def test_application():
    """Run comprehensive application tests."""
    print("🧪 Testing DEX Sniper Application")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    async with httpx.AsyncClient() as client:
        tests_passed = 0
        tests_failed = 0
        
        # Test 1: Health check
        try:
            response = await client.get(f"{base_url}/api/v1/health")
            if response.status_code == 200:
                print("✅ Health check endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Health check failed: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"❌ Health check error: {e}")
            tests_failed += 1
        
        # Test 2: Dashboard stats
        try:
            response = await client.get(f"{base_url}/api/v1/dashboard/stats")
            if response.status_code == 200:
                print("✅ Dashboard stats endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Dashboard stats failed: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"❌ Dashboard stats error: {e}")
            tests_failed += 1
        
        # Test 3: Live tokens
        try:
            response = await client.get(f"{base_url}/api/v1/dashboard/tokens/live")
            if response.status_code == 200:
                print("✅ Live tokens endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Live tokens failed: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"❌ Live tokens error: {e}")
            tests_failed += 1
        
        # Test 4: Trading metrics
        try:
            response = await client.get(f"{base_url}/api/v1/dashboard/trading/metrics")
            if response.status_code == 200:
                print("✅ Trading metrics endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Trading metrics failed: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"❌ Trading metrics error: {e}")
            tests_failed += 1
        
        # Test 5: Root endpoint
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ Root endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            tests_failed += 1
        
        # Test 6: Dashboard page
        try:
            response = await client.get(f"{base_url}/dashboard")
            if response.status_code == 200:
                print("✅ Dashboard page working")
                tests_passed += 1
            else:
                print(f"❌ Dashboard page failed: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"❌ Dashboard page error: {e}")
            tests_failed += 1
        
        print(f"\n📊 Test Results:")
        print(f"   ✅ Passed: {tests_passed}")
        print(f"   ❌ Failed: {tests_failed}")
        print(f"   📈 Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
        
        if tests_passed >= 5:
            print("\n🎉 Application is working correctly!")
            return True
        else:
            print("\n⚠️ Application has issues that need fixing")
            return False


def check_file_structure():
    """Check if all required files exist."""
    print("\n📁 Checking File Structure")
    print("-" * 30)
    
    required_files = [
        "app/main.py",
        "app/config.py",
        "app/core/database.py",
        "app/core/database_mock.py",
        "app/core/exceptions.py",
        "app/utils/logger.py",
        "app/api/v1/endpoints/dashboard.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} required files")
        return False
    else:
        print("\n✅ All required files present")
        return True


if __name__ == "__main__":
    print("🔍 DEX Sniper Application Validation")
    print("=" * 50)
    
    # Check file structure first
    structure_ok = check_file_structure()
    
    if not structure_ok:
        print("\n❌ File structure issues detected. Run comprehensive_fix.py first.")
        sys.exit(1)
    
    # Run application tests
    print("\n🧪 Starting application tests...")
    print("Note: Make sure the application is running on http://127.0.0.1:8001")
    
    try:
        success = asyncio.run(test_application())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted")
        sys.exit(1)
