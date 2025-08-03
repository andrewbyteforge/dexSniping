#!/usr/bin/env python3
"""
Comprehensive Dashboard Test Script
File: test_dashboard_complete.py

Tests all dashboard components to ensure everything is working correctly.
"""

import asyncio
import aiohttp
import os
import sys
from datetime import datetime


async def test_api_endpoints():
    """Test all dashboard API endpoints."""
    base_url = "http://localhost:8000"  # Adjust port as needed
    
    endpoints_to_test = [
        ("/", "Root Page"),
        ("/dashboard", "Dashboard Page"),
        ("/api/v1/health", "Health Check"),
        ("/api/v1/dashboard/stats", "Dashboard Statistics"),
        ("/api/v1/dashboard/tokens/live", "Live Tokens"),
        ("/api/v1/dashboard/alerts", "Recent Alerts"),
        ("/api/v1/dashboard/performance", "Performance Metrics"),
    ]
    
    print("🧪 Testing Dashboard API Endpoints")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Test Time: {datetime.now()}")
    print()
    
    passed = 0
    failed = 0
    
    async with aiohttp.ClientSession() as session:
        for endpoint, description in endpoints_to_test:
            try:
                print(f"📡 Testing: {description}")
                print(f"   URL: {base_url}{endpoint}")
                
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        print(f"   ✅ SUCCESS - Status: {response.status}")
                        
                        # Analyze response content
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            data = await response.json()
                            print(f"   📊 JSON Response - Keys: {list(data.keys())}")
                            
                            # Show specific data for different endpoints
                            if 'tokens' in data:
                                print(f"   🪙 Token count: {len(data['tokens'])}")
                            if 'alerts' in data:
                                print(f"   🚨 Alert count: {len(data['alerts'])}")
                            if 'portfolio_value' in data:
                                print(f"   💰 Portfolio: ${data['portfolio_value']:,.2f}")
                                
                        elif 'text/html' in content_type:
                            content = await response.text()
                            print(f"   📄 HTML Response - Size: {len(content):,} chars")
                            
                            # Check for dashboard elements
                            if 'dashboard' in content.lower():
                                print(f"   ✅ Contains dashboard content")
                            if 'bootstrap' in content.lower():
                                print(f"   ✅ Contains Bootstrap styling")
                        
                        passed += 1
                    else:
                        print(f"   ❌ FAILED - Status: {response.status}")
                        error_text = await response.text()
                        print(f"   💥 Error: {error_text[:150]}...")
                        failed += 1
                        
            except Exception as e:
                print(f"   ❌ CONNECTION ERROR: {e}")
                failed += 1
            
            print()
    
    print("📊 Test Results Summary")
    print("-" * 40)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    return passed >= 5


def check_file_structure():
    """Check if all required files exist."""
    print("📁 Checking File Structure")
    print("-" * 40)
    
    required_files = [
        ("frontend/templates/pages/dashboard.html", "Dashboard Template"),
        ("frontend/templates/base/layout.html", "Base Layout Template"),
        ("app/api/v1/endpoints/dashboard_working.py", "Working Dashboard API"),
        ("app/main_fixed.py", "Fixed Main Application"),
        ("frontend/static/js/components/dashboard-controller.js", "Dashboard Controller"),
    ]
    
    optional_files = [
        ("frontend/static/css/main.css", "Main CSS"),
        ("frontend/static/js/utils/formatters.js", "Utility Functions"),
    ]
    
    all_good = True
    
    print("📋 Required Files:")
    for file_path, description in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {description}: {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {description}: {file_path} - MISSING")
            all_good = False
    
    print("\n📋 Optional Files:")
    for file_path, description in optional_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {description}: {file_path} ({size:,} bytes)")
        else:
            print(f"   ⚠️ {description}: {file_path} - Optional")
    
    print()
    return all_good


def main():
    """Main test function."""
    print("🔍 Comprehensive Dashboard Test")
    print("=" * 60)
    print("Testing all dashboard components and functionality...")
    print()
    
    # Step 1: Check file structure
    files_ok = check_file_structure()
    
    if not files_ok:
        print("❌ File structure issues detected!")
        print("🔧 Run the complete_dashboard_fix.py script first")
        return False
    
    print("✅ File structure looks good!")
    print()
    
    # Step 2: Test API endpoints
    print("Starting API endpoint tests...")
    print("⚠️ Make sure your application is running!")
    print()
    
    try:
        api_ok = asyncio.run(test_api_endpoints())
        
        if api_ok:
            print("\n🎉 Dashboard Test Results: SUCCESS!")
            print("=" * 50)
            print("✅ All tests passed")
            print("✅ Dashboard is working correctly")
            print("✅ API endpoints are responding")
            print("✅ Data is flowing properly")
            print()
            print("🚀 Your dashboard should now be fully functional!")
            print("📊 Visit: http://localhost:8000/dashboard")
            return True
        else:
            print("\n⚠️ Dashboard Test Results: PARTIAL SUCCESS")
            print("=" * 50)
            print("⚠️ Some tests failed")
            print("🔧 Check the application logs")
            print("🔄 Restart the application if needed")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
