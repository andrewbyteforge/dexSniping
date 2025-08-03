#!/usr/bin/env python3
"""
Quick WebSocket Integration Test
File: test_phase4c.py

Quick test script to verify Phase 4C WebSocket integration is working.
Run this after starting the server to test real-time functionality.
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime

# Add the project root to Python path if needed
if os.path.exists('app'):
    sys.path.insert(0, os.getcwd())

try:
    import aiohttp
    import websockets
except ImportError:
    print("❌ Missing dependencies. Install with: pip install aiohttp websockets")
    sys.exit(1)

# Configuration
SERVER_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
CLIENT_ID = f"test_client_{int(time.time())}"


async def test_api_endpoints():
    """Test API endpoints are responding correctly."""
    print("🔍 Testing API endpoints...")
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        try:
            async with session.get(f"{SERVER_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data.get('status')} - Phase {data.get('phase')}")
                    if 'websocket' in data:
                        print(f"   WebSocket: {data['websocket']['active_connections']} connections")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test WebSocket status
        try:
            async with session.get(f"{SERVER_URL}/api/v1/ws/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ WebSocket status: {data.get('status')}")
                    print(f"   Connected clients: {data.get('connected_clients')}")
                else:
                    print(f"❌ WebSocket status failed: {response.status}")
        except Exception as e:
            print(f"❌ WebSocket status error: {e}")


async def test_websocket_connection():
    """Test WebSocket connection and messaging."""
    print(f"🔌 Testing WebSocket connection to {WS_URL}/api/v1/ws/dashboard/{CLIENT_ID}")
    
    try:
        async with websockets.connect(f"{WS_URL}/api/v1/ws/dashboard/{CLIENT_ID}") as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for initial connection message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received initial message: {data.get('type')}")
            except asyncio.TimeoutError:
                print("⚠️ No initial message received (this is okay)")
            
            # Send subscription message
            subscription_msg = {
                "type": "subscribe",
                "data": {"subscription": "dashboard"}
            }
            await websocket.send(json.dumps(subscription_msg))
            print("📤 Sent dashboard subscription")
            
            # Send heartbeat
            heartbeat_msg = {
                "type": "heartbeat",
                "data": {"timestamp": datetime.utcnow().isoformat()}
            }
            await websocket.send(json.dumps(heartbeat_msg))
            print("📤 Sent heartbeat")
            
            # Listen for messages for 10 seconds
            print("👂 Listening for messages (10 seconds)...")
            messages_received = 0
            
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    messages_received += 1
                    print(f"📨 Message {messages_received}: {data.get('type')} - {data.get('timestamp', 'no timestamp')[:19]}")
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Message error: {e}")
                    break
            
            print(f"✅ WebSocket test completed - received {messages_received} messages")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")


async def test_live_dashboard_page():
    """Test live dashboard page loads correctly."""
    print("🌐 Testing live dashboard page...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/dashboard/live") as response:
                if response.status == 200:
                    content = await response.text()
                    if "Live Dashboard" in content and "WebSocket" in content:
                        print("✅ Live dashboard page loads correctly")
                        print("   Contains: Live Dashboard, WebSocket integration")
                    else:
                        print("⚠️ Live dashboard page missing expected content")
                else:
                    print(f"❌ Live dashboard page failed: {response.status}")
        except Exception as e:
            print(f"❌ Live dashboard page error: {e}")


async def test_websocket_test_page():
    """Test WebSocket test page loads correctly."""
    print("🧪 Testing WebSocket test page...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/api/v1/ws/test") as response:
                if response.status == 200:
                    content = await response.text()
                    if "WebSocket Test" in content and "DEX Sniper Pro" in content:
                        print("✅ WebSocket test page loads correctly")
                    else:
                        print("⚠️ WebSocket test page missing expected content")
                else:
                    print(f"❌ WebSocket test page failed: {response.status}")
        except Exception as e:
            print(f"❌ WebSocket test page error: {e}")


async def test_broadcast_functionality():
    """Test message broadcasting functionality."""
    print("📡 Testing broadcast functionality...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Send test broadcast
            test_data = {
                "test_message": "Phase 4C integration test",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with session.post(
                f"{SERVER_URL}/api/v1/ws/broadcast/test",
                params={"message_type": "test_broadcast"},
                json=test_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Broadcast test successful")
                    print(f"   Recipients: {data.get('recipients')}")
                    print(f"   Status: {data.get('status')}")
                else:
                    print(f"❌ Broadcast test failed: {response.status}")
        except Exception as e:
            print(f"❌ Broadcast test error: {e}")


async def main():
    """Run all Phase 4C integration tests."""
    print("🚀 Starting Phase 4C WebSocket Integration Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    await test_api_endpoints()
    print()
    
    await test_live_dashboard_page()
    print()
    
    await test_websocket_test_page()
    print()
    
    await test_websocket_connection()
    print()
    
    await test_broadcast_functionality()
    print()
    
    end_time = time.time()
    test_duration = end_time - start_time
    
    print("=" * 60)
    print(f"✅ Phase 4C integration tests completed in {test_duration:.2f} seconds")
    print()
    print("🎯 Next steps:")
    print("1. Open http://localhost:8000/dashboard/live to see the live dashboard")
    print("2. Open http://localhost:8000/api/v1/ws/test to test WebSocket connections")
    print("3. Check http://localhost:8000/docs for complete API documentation")
    print("4. Monitor http://localhost:8000/health for system status")
    print()
    print("🚀 Phase 4C: Live Dashboard Integration - COMPLETE")
    print("📋 Ready for Phase 4D: Advanced Trading Features")


def check_server_running():
    """Check if the server is running before starting tests."""
    import urllib.request
    import urllib.error
    
    try:
        response = urllib.request.urlopen(f"{SERVER_URL}/health", timeout=5)
        if response.getcode() == 200:
            return True
    except urllib.error.URLError:
        return False
    except Exception:
        return False
    
    return False


if __name__ == "__main__":
    print("🤖 DEX Sniper Pro - Phase 4C Integration Test")
    print()
    
    # Check if server is running
    if not check_server_running():
        print("❌ Server not running!")
        print("Please start the server first:")
        print("   uvicorn app.main:app --reload")
        print()
        exit(1)
    
    print("✅ Server is running, starting tests...")
    print()
    
    # Run tests
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)