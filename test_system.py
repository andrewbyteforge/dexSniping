"""
Test Phase 4B System - Quick Verification
File: test_system.py

Quick test script to verify all Phase 4B components are working correctly.
"""

import asyncio
import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        "/",
        "/health", 
        "/api/v1/dashboard/stats",
        "/api/v1/tokens/discover"
    ]
    
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"{endpoint:<30} {status}")
            
            if endpoint == "/health":
                data = response.json()
                print(f"   Service: {data.get('service', 'Unknown')}")
                print(f"   Phase: {data.get('phase', 'Unknown')}")
                
        except Exception as e:
            print(f"{endpoint:<30} ❌ ERROR: {e}")
    
    print("=" * 50)

def test_dashboard_access():
    """Test dashboard page access."""
    print("\n🌐 Testing Dashboard Access...")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard", timeout=5)
        if response.status_code == 200:
            print("Dashboard Page:                ✅ ACCESSIBLE")
        else:
            print(f"Dashboard Page:                ❌ FAILED ({response.status_code})")
    except Exception as e:
        print(f"Dashboard Page:                ❌ ERROR: {e}")
    
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("API Documentation:             ✅ ACCESSIBLE")
        else:
            print(f"API Documentation:             ❌ FAILED ({response.status_code})")
    except Exception as e:
        print(f"API Documentation:             ❌ ERROR: {e}")
    
    print("=" * 50)

def test_live_trading_endpoints():
    """Test live trading endpoints if available."""
    print("\n⚡ Testing Live Trading Endpoints...")
    print("=" * 50)
    
    live_endpoints = [
        "/api/v1/live-trading/system/status",
        "/api/v1/live-trading/opportunities",
        "/api/v1/live-trading/wallet/connections"
    ]
    
    for endpoint in live_endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
            status = "✅ AVAILABLE" if response.status_code == 200 else f"❌ UNAVAILABLE ({response.status_code})"
            print(f"{endpoint:<40} {status}")
            
        except Exception as e:
            print(f"{endpoint:<40} ❌ ERROR: {e}")
    
    print("=" * 50)

def display_system_info():
    """Display system information."""
    print("\n📊 System Information")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Service:     {data.get('message', 'Unknown')}")
            print(f"Version:     {data.get('version', 'Unknown')}")
            print(f"Phase:       {data.get('phase', 'Unknown')}")
            print(f"Status:      {data.get('status', 'Unknown')}")
            
            capabilities = data.get('capabilities', [])
            print(f"\nCapabilities:")
            for cap in capabilities:
                print(f"  {cap}")
                
            networks = data.get('supported_networks', [])
            print(f"\nSupported Networks: {', '.join(networks)}")
            
        else:
            print("❌ Failed to get system information")
            
    except Exception as e:
        print(f"❌ Error getting system info: {e}")
    
    print("=" * 50)

def main():
    """Run all tests."""
    print("🚀 DEX Sniper Pro - Phase 4B System Test")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test dashboard access
    test_dashboard_access()
    
    # Test live trading endpoints
    test_live_trading_endpoints()
    
    # Display system info
    display_system_info()
    
    print("\n🎉 System Test Complete!")
    print("\nNext Steps:")
    print("1. Visit http://127.0.0.1:8000/dashboard for the dashboard")
    print("2. Visit http://127.0.0.1:8000/docs for API documentation")
    print("3. Check http://127.0.0.1:8000/health for system health")
    print("4. Install missing dependencies if needed:")
    print("   pip install sse-starlette")

if __name__ == "__main__":
    main()