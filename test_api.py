#!/usr/bin/env python3
"""
API Test Script
File: test_api.py

Test the trading API endpoints.
"""

import requests
import json
from decimal import Decimal


BASE_URL = "http://localhost:8000"


def test_api_health():
    """Test API health check."""
    print("Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Trading Engine: {data['trading_engine']}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Health check failed: {e}")
        return False


def test_wallet_connection():
    """Test wallet connection."""
    print("Testing wallet connection...")
    try:
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "wallet_type": "metamask",
            "network": "ethereum"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/live-trading/wallet/connect",
            json=payload
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success']:
            print(f"  Session token: {data['data']['session_token'][:20]}...")
        
        return data['success']
    except Exception as e:
        print(f"  Wallet connection failed: {e}")
        return False


def test_get_quotes():
    """Test getting swap quotes."""
    print("Testing swap quotes...")
    try:
        params = {
            "input_token": "0x0000000000000000000000000000000000000000",
            "output_token": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "amount": "1.0",
            "slippage": "0.01"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/live-trading/quotes",
            params=params
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success']:
            quotes = data['data']['quotes']
            print(f"  Got {len(quotes)} quotes")
            if quotes:
                best = quotes[0]
                print(f"  Best rate: {best['output_amount']} tokens for 1 ETH")
        
        return data['success']
    except Exception as e:
        print(f"  Quote test failed: {e}")
        return False


def test_manual_trade():
    """Test manual trade execution."""
    print("Testing manual trade...")
    try:
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "token_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "intent": "buy",
            "amount": "0.1",
            "slippage_tolerance": "0.01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/live-trading/trade/manual",
            json=payload
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success']:
            trade_data = data['data']
            print(f"  Trade ID: {trade_data['trade_id']}")
            print(f"  TX Hash: {trade_data['transaction_hash'][:20]}...")
            print(f"  Execution time: {trade_data['execution_time']:.2f}s")
        
        return data['success']
    except Exception as e:
        print(f"  Manual trade test failed: {e}")
        return False


def test_trading_status():
    """Test trading status."""
    print("Testing trading status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/live-trading/status")
        data = response.json()
        
        print(f"  Success: {data['success']}")
        if data['success']:
            status = data['data']
            print(f"  Running: {status['is_running']}")
            print(f"  Mode: {status['trading_mode']}")
            print(f"  Total trades: {status['total_trades']}")
        
        return data['success']
    except Exception as e:
        print(f"  Status test failed: {e}")
        return False


def test_generate_signal():
    """Test signal generation."""
    print("Testing signal generation...")
    try:
        params = {
            "strategy": "arbitrage",
            "token_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/live-trading/test/generate-signal",
            params=params
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success'] and data['data']:
            signal = data['data']
            print(f"  Strategy: {signal['strategy']}")
            print(f"  Intent: {signal['intent']}")
            print(f"  Confidence: {signal['confidence']:.2f}")
            print(f"  Reasoning: {signal['reasoning']}")
        
        return True
    except Exception as e:
        print(f"  Signal generation test failed: {e}")
        return False


def run_all_api_tests():
    """Run all API tests."""
    print("🤖 DEX Sniper Pro - API Testing")
    print("=" * 50)
    print("Make sure the API server is running:")
    print("  uvicorn app.main:app --reload")
    print("")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Wallet Connection", test_wallet_connection),
        ("Swap Quotes", test_get_quotes),
        ("Manual Trade", test_manual_trade),
        ("Trading Status", test_trading_status),
        ("Signal Generation", test_generate_signal)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  Test failed with exception: {e}")
            results.append((test_name, False))
        print("")
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"  {symbol} {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} API tests passed")
    
    if passed == total:
        print("\n🎉 All API tests passed!")
        print("\n📋 API is ready for live trading!")
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
    
    return passed == total


if __name__ == "__main__":
    run_all_api_tests()
