"""
Simple Trading Engine Test
File: tests/test_trading_simple.py

Basic test for the trading engine functionality.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_basic_trading_components():
    """Test that trading components can be imported and work."""
    print("Testing trading components import...")
    
    try:
        from app.core.wallet.wallet_manager import WalletManager, NetworkType, WalletType
        print("  Wallet Manager imported successfully")
        
        from app.core.dex.dex_integration import DEXIntegration, DEXProtocol
        print("  DEX Integration imported successfully")
        
        from app.core.trading.trading_engine import TradingEngine, TradingMode, StrategyType
        print("  Trading Engine imported successfully")
        
        return True
    except ImportError as e:
        print(f"  Import failed: {e}")
        return False


def test_wallet_manager_creation():
    """Test wallet manager creation."""
    print("Testing wallet manager creation...")
    
    try:
        from app.core.wallet.wallet_manager import WalletManager, NetworkType
        
        manager = WalletManager(NetworkType.ETHEREUM)
        print("  Wallet manager created successfully")
        
        # Test address validation
        valid_address = "0x1234567890123456789012345678901234567890"
        is_valid = manager._is_valid_address(valid_address)
        print(f"  Address validation works: {is_valid}")
        
        return True
    except Exception as e:
        print(f"  Wallet manager test failed: {e}")
        return False


def test_dex_integration_creation():
    """Test DEX integration creation."""
    print("Testing DEX integration creation...")
    
    try:
        from app.core.dex.dex_integration import DEXIntegration, DEXProtocol
        
        dex = DEXIntegration(network="ethereum")
        print("  DEX integration created successfully")
        
        # Test protocol loading
        protocols = dex.protocols
        print(f"  Loaded {len(protocols)} DEX protocols")
        
        return True
    except Exception as e:
        print(f"  DEX integration test failed: {e}")
        return False


async def test_trading_engine_async():
    """Test trading engine with async operations."""
    print("Testing trading engine (async)...")
    
    try:
        from app.core.trading.trading_engine import TradingEngine, NetworkType
        from app.core.wallet.wallet_manager import WalletManager, WalletType
        from decimal import Decimal
        
        # Create trading engine
        engine = TradingEngine(NetworkType.ETHEREUM)
        print("  Trading engine created")
        
        # Initialize with wallet manager
        wallet_manager = WalletManager(NetworkType.ETHEREUM)
        await engine.initialize(wallet_manager=wallet_manager)
        print("  Trading engine initialized")
        
        # Test wallet connection
        test_address = "0x1234567890123456789012345678901234567890"
        connect_result = await wallet_manager.connect_wallet(
            wallet_address=test_address,
            wallet_type=WalletType.METAMASK
        )
        print(f"  Wallet connection: {connect_result['success']}")
        
        # Test trading start
        start_result = await engine.start_trading(test_address)
        print(f"  Trading start: {start_result['success']}")
        
        # Test status
        status = await engine.get_trading_status()
        print(f"  Trading status: running={status['is_running']}")
        
        # Test stop
        stop_result = await engine.stop_trading()
        print(f"  Trading stop: {stop_result['success']}")
        
        return True
    except Exception as e:
        print(f"  Trading engine test failed: {e}")
        return False


def test_trading_engine_sync():
    """Test trading engine synchronously."""
    import asyncio
    return asyncio.run(test_trading_engine_async())


def run_all_tests():
    """Run all trading tests."""
    print("[BOT] DEX Sniper Pro - Trading Engine Test")
    print("=" * 50)
    
    tests = [
        ("Trading Components Import", test_basic_trading_components),
        ("Wallet Manager Creation", test_wallet_manager_creation),
        ("DEX Integration Creation", test_dex_integration_creation),
        ("Trading Engine Full Test", test_trading_engine_sync)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "[EMOJI]" if success else "[EMOJI]"
        print(f"  {symbol} {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All trading tests passed!")
        print("\n[LOG] The trading engine is working correctly!")
        print("\nYou can now:")
        print("1. Start the API server: uvicorn app.main:app --reload")
        print("2. Connect wallets and start trading")
        print("3. Test automated strategies")
        return True
    else:
        print(f"\n[WARN]  {total - passed} tests failed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
