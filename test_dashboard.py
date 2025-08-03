#!/usr/bin/env python3
"""
Dashboard Test Script
File: test_dashboard.py

Quick test to verify dashboard endpoints are working.
"""

import urllib.request
import urllib.error
import json

def test_endpoint(url, description):
    """Test a single endpoint."""
    try:
        print(f"Testing {description}...")
        response = urllib.request.urlopen(url, timeout=10)
        
        if response.getcode() == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = json.loads(response.read().decode())
                print(f"✅ {description} - JSON Response")
                print(f"   Status: {data.get('status', 'unknown')}")
                if 'message' in data:
                    print(f"   Message: {data['message']}")
            elif 'text/html' in content_type:
                content = response.read().decode()
                print(f"✅ {description} - HTML Response")
                print(f"   Content length: {len(content)} chars")
                if 'Dashboard' in content or 'DEX Sniper Pro' in content:
                    print(f"   Contains dashboard content: ✅")
                else:
                    print(f"   Contains dashboard content: ❌")
            else:
                print(f"✅ {description} - Other content type: {content_type}")
        else:
            print(f"❌ {description} - HTTP {response.getcode()}")
    
    except urllib.error.HTTPError as e:
        print(f"❌ {description} - HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ {description} - URL Error: {e.reason}")
    except Exception as e:
        print(f"❌ {description} - Error: {e}")

def main():
    """Test all dashboard endpoints."""
    print("🧪 Testing Dashboard Endpoints")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    endpoints = [
        (f"{base_url}/", "Root endpoint"),
        (f"{base_url}/health", "Health check"),
        (f"{base_url}/dashboard", "Main dashboard"),
        (f"{base_url}/dashboard/live", "Live dashboard"),
        (f"{base_url}/api/v1/ws/status", "WebSocket status"),
        (f"{base_url}/api/v1/ws/test", "WebSocket test page"),
        (f"{base_url}/docs", "API documentation"),
    ]
    
    for url, description in endpoints:
        test_endpoint(url, description)
        print()
    
    print("=" * 50)
    print("🎯 Recommended Dashboard URLs:")
    print(f"   Main Dashboard: {base_url}/dashboard")
    print(f"   Live Dashboard: {base_url}/dashboard/live")
    print(f"   WebSocket Test: {base_url}/api/v1/ws/test")
    print(f"   API Docs: {base_url}/docs")

if __name__ == "__main__":
    main()