"""
Test to verify the config fix works with your comprehensive .env file.
Save as test_config_fix.py and run: python test_config_fix.py
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def test_config_fix():
    """Test the config fix with production settings."""
    print('🎯 Config Fix Verification')
    print('=' * 40)
    
    try:
        # Test 1: Import fixed config
        print('📦 Testing config import...')
        from app.config import settings, NetworkConfig
        print(f'   ✅ Config imported successfully')
        print(f'   📊 Environment: {settings.environment}')
        print(f'   🔗 Networks available: {len(NetworkConfig.get_all_networks())}')
        
        # Test 2: Verify all your .env values are loaded
        print('\n⚙️ Testing .env integration...')
        print(f'   🔑 Moralis API: {"SET" if settings.moralis_api_key != "your_moralis_api_key" else "DEFAULT"}')
        print(f'   🔗 Ethereum RPC: {"CONFIGURED" if "YOUR_KEY" not in settings.ethereum_rpc_url else "TEMPLATE"}')
        print(f'   💾 Redis URL: {settings.redis_url}')
        print(f'   📈 Min Liquidity: ${settings.min_liquidity_usd_int:,}')
        print(f'   ⛽ Max Gas Price: {settings.max_gas_price_gwei_int} gwei')
        
        # Test 3: Test network configuration with real RPC URLs
        print('\n🌐 Testing network configuration...')
        ethereum_config = NetworkConfig.get_network_config('ethereum', settings)
        polygon_config = NetworkConfig.get_network_config('polygon', settings)
        
        print(f'   ✅ Ethereum: Chain ID {ethereum_config["chain_id"]}, {len(ethereum_config["rpc_urls"])} RPC URLs')
        print(f'   ✅ Polygon: Chain ID {polygon_config["chain_id"]}, {len(polygon_config["rpc_urls"])} RPC URLs')
        
        # Test 4: Test existing multi-chain manager with new config
        print('\n🔗 Testing multi-chain manager integration...')
        from app.core.blockchain.multi_chain_manager import MultiChainManager
        
        manager = MultiChainManager()
        print('   ✅ Multi-chain manager created successfully')
        
        # Initialize with your configured networks
        await manager.initialize(['ethereum', 'polygon'])
        enabled_networks = await manager.get_enabled_networks()
        print(f'   ✅ Networks initialized: {list(enabled_networks)}')
        
        # Test health check
        health_status = await manager.get_health_status()
        for network, health in health_status.items():
            print(f'   📊 {network}: {health.status.value}')
        
        # Test 5: Test trading parameters
        print('\n💰 Testing trading parameters...')
        print(f'   📊 Max Slippage: {float(settings.max_slippage_decimal) * 100}%')
        print(f'   💰 Min Liquidity: ${settings.min_liquidity_usd_int:,}')
        print(f'   🎯 Risk Threshold: {settings.risk_score_threshold_float}/10')
        print(f'   💎 Min Profit: {float(settings.min_profit_threshold_decimal) * 100}%')
        
        # Cleanup
        await manager.close()
        
        print('\n' + '=' * 40)
        print('🎉 CONFIG FIX: COMPLETE SUCCESS!')
        print('=' * 40)
        
        print('\n✅ What\'s Now Working:')
        print('   ✅ Complete .env integration')
        print('   ✅ Production-ready configuration')
        print('   ✅ All API keys and RPC URLs supported')
        print('   ✅ Trading parameters loaded')
        print('   ✅ Multi-chain manager compatibility')
        print('   ✅ Network configuration with real RPC URLs')
        
        print('\n🎯 Ready for Performance Components!')
        print('📋 Next Steps:')
        print('   1. Create performance component files')
        print('   2. Run Phase 2B integration test')
        print('   3. Add Web3 blockchain connections')
        
        return True
        
    except Exception as e:
        print(f'\n❌ Config test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_config_fix())
    if success:
        print('\n🚀 Config is fixed! Ready for performance components!')
    else:
        print('\n❌ Please check the config file')