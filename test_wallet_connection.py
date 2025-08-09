"""
Windows Wallet Connection Test Script
File: test_wallet_connection.py

Test script for Windows to verify MetaMask wallet connection API endpoints.
Run this from the project root directory while the server is running.
"""

import json
import requests
import sys
from datetime import datetime
from typing import Dict, Any


def test_server_health():
    """Test that the server is running."""
    print("🏥 Testing server health...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data.get('service', 'Unknown')}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_live_trading_health():
    """Test live trading API health."""
    print("🔧 Testing live trading API health...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/live-trading/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Live trading API is healthy")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Live trading API health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to live trading API")
        return False
    except Exception as e:
        print(f"❌ Live trading health check error: {e}")
        return False


def test_wallet_connect_endpoint():
    """Test the wallet connection endpoint."""
    print("🔗 Testing wallet connection endpoint...")
    
    # Test data
    wallet_data = {
        "wallet_address": "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC",
        "wallet_type": "metamask",
        "requested_networks": ["ethereum"]
    }
    
    try:
        # Make the POST request
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/live-trading/wallet/connect",
            json=wallet_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Wallet connection successful!")
            print(f"   Connection ID: {data.get('connection_id', 'Unknown')}")
            print(f"   Wallet Address: {data.get('wallet_address', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Connected Networks: {data.get('connected_networks', [])}")
            return True, data
            
        elif response.status_code == 404:
            print("❌ Endpoint not found (404)")
            print("   This means the route is not properly configured")
            print(f"   Response: {response.text}")
            return False, None
            
        elif response.status_code == 422:
            print("❌ Validation error (422)")
            print("   Check the request data format")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response: {response.text}")
            return False, None
            
        else:
            print(f"❌ Wallet connection failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to wallet API endpoint")
        return False, None
    except Exception as e:
        print(f"❌ Wallet connection test error: {e}")
        return False, None


def test_wallet_test_endpoint():
    """Test the wallet test endpoint."""
    print("🧪 Testing wallet test endpoint...")
    
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/v1/live-trading/test/wallet-connect",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Wallet test endpoint working!")
            print(f"   Message: {data.get('message', 'Unknown')}")
            print(f"   Endpoint: {data.get('endpoint', 'Unknown')}")
            return True
        else:
            print(f"❌ Wallet test endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Wallet test endpoint error: {e}")
        return False


def test_api_docs():
    """Test API documentation endpoint."""
    print("📚 Testing API documentation...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        
        if response.status_code == 200:
            print("✅ API documentation is available at http://127.0.0.1:8000/docs")
            return True
        else:
            print(f"❌ API documentation not available: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API documentation test error: {e}")
        return False


def run_comprehensive_test():
    """Run comprehensive wallet connection tests."""
    print("🚀 Starting Comprehensive Wallet Connection Test")
    print("=" * 60)
    
    tests = [
        ("Server Health", test_server_health),
        ("Live Trading API Health", test_live_trading_health),
        ("Wallet Test Endpoint", test_wallet_test_endpoint),
        ("Wallet Connection", test_wallet_connect_endpoint),
        ("API Documentation", test_api_docs)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_name == "Wallet Connection":
                result, _ = test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All wallet connection tests passed!")
        print("✅ MetaMask wallet connection API is working correctly")
    else:
        print(f"⚠️ {failed} tests failed - review the issues above")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure the server is running: uvicorn app.main:app --reload")
        print("   2. Check that the live trading API routes are properly configured")
        print("   3. Verify the wallet connection endpoint is included in main.py")
    
    return failed == 0


if __name__ == "__main__":
    print("🔧 Windows-Compatible Wallet Connection Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = run_comprehensive_test()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🎯 Next steps:")
        print("   1. Test with real MetaMask wallet integration")
        print("   2. Implement frontend wallet connection interface")
        print("   3. Add transaction execution capabilities")
    
    sys.exit(0 if success else 1)