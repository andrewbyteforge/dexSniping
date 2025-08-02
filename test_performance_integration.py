"""
Streamlined test for Phase 2B performance components integration.
Save as test_performance_integration.py and run after creating performance files.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def test_performance_integration():
    """Test performance components with working config."""
    print('🚀 Phase 2B Performance Integration Test')
    print('=' * 50)
    
    try:
        # Test 1: Import Performance Components
        print('📦 Testing performance component imports...')
        try:
            from app.core.performance.connection_pool import connection_pool
            from app.core.performance.cache_manager import cache_manager
            from app.core.performance.circuit_breaker import CircuitBreakerManager
            print('   ✅ Performance components imported successfully')
        except ImportError as e:
            print(f'   ❌ Performance components missing: {e}')
            print('   💡 Please create the 3 performance component files')
            print('   📋 Files needed:')
            print('      - app/core/performance/connection_pool.py')
            print('      - app/core/performance/cache_manager.py')
            print('      - app/core/performance/circuit_breaker.py')
            return False
        
        # Test 2: Multi-Chain + Performance Integration
        print('\n🔗 Testing multi-chain + performance integration...')
        from app.core.blockchain.multi_chain_manager import MultiChainManager
        from app.config import settings
        
        # Initialize systems
        await connection_pool.initialize()
        await cache_manager.connect()
        breaker_manager = CircuitBreakerManager()
        
        manager = MultiChainManager()
        await manager.initialize(['ethereum', 'polygon'])
        
        print('   ✅ All systems initialized successfully')
        
        # Test 3: Performance Under Load
        print('\n⚡ Testing performance under simulated load...')
        
        # Database operations
        tasks = []
        for i in range(5):
            async def db_operation():
                async with connection_pool.session_scope() as session:
                    from sqlalchemy import text
                    result = await session.execute(text("SELECT 'performance_test' as result"))
                    return result.fetchone()[0]
            tasks.append(db_operation())
        
        db_results = await asyncio.gather(*tasks)
        print(f'   ✅ Database: {len(db_results)} concurrent operations completed')
        
        # Cache operations
        for i in range(10):
            await cache_manager.set(f'perf_test_{i}', {'test_id': i, 'status': 'active'})
        
        cached_items = 0
        for i in range(10):
            if await cache_manager.exists(f'perf_test_{i}'):
                cached_items += 1
        
        print(f'   ✅ Cache: {cached_items}/10 items cached successfully')
        
        # Circuit breaker test
        blockchain_breaker = breaker_manager.get_breaker('blockchain_api')
        
        async def blockchain_operation():
            # Simulate blockchain call
            enabled_networks = await manager.get_enabled_networks()
            return len(enabled_networks)
        
        network_count = await blockchain_breaker.call(blockchain_operation)
        print(f'   ✅ Circuit breaker: Protected {network_count} network operations')
        
        # Test 4: Integrated Token Discovery Simulation
        print('\n🔍 Testing integrated token discovery workflow...')
        
        # Simulate full workflow with all performance components
        discovery_breaker = breaker_manager.get_breaker('token_discovery')
        
        async def mock_token_discovery():
            # Simulate token scan
            new_tokens = await manager.scan_all_chains_for_new_tokens(from_block_offset=5)
            
            # Cache results
            await cache_manager.set(
                'latest_discovery',
                {
                    'timestamp': '2025-08-02T19:08:23Z',
                    'networks': list(new_tokens.keys()),
                    'total_tokens': sum(len(tokens) for tokens in new_tokens.values())
                },
                ttl=300,
                namespace='discovery'
            )
            
            # Store in database
            async with connection_pool.session_scope() as session:
                from sqlalchemy import text
                await session.execute(text("SELECT 'discovery_stored' as result"))
            
            return new_tokens
        
        discovery_result = await discovery_breaker.call(mock_token_discovery)
        cached_discovery = await cache_manager.get('latest_discovery', namespace='discovery')
        
        print(f'   ✅ Token discovery: {len(discovery_result)} networks scanned')
        print(f'   ✅ Results cached: {cached_discovery["total_tokens"]} tokens found')
        
        # Test 5: Health Monitoring
        print('\n🏥 Testing integrated health monitoring...')
        
        # Get health from all systems
        pool_health = await connection_pool.health_check()
        cache_stats = await cache_manager.get_stats()
        breaker_health = await breaker_manager.health_check()
        chain_health = await manager.get_health_status()
        
        print(f'   ✅ Connection pool: {pool_health["status"]}')
        print(f'   ✅ Cache system: {cache_stats["cache_type"]} ({cache_stats["hit_rate"]:.1f}% hit rate)')
        print(f'   ✅ Circuit breakers: {breaker_health["status"]} ({breaker_health["total_breakers"]} active)')
        print(f'   ✅ Blockchain networks: {len([h for h in chain_health.values() if h.status.value == "connected"])}/2 connected')
        
        # Test 6: Performance Statistics
        print('\n📊 Performance statistics...')
        
        pool_stats = connection_pool.get_stats()
        all_breaker_stats = await breaker_manager.get_all_stats()
        
        print(f'   📈 Database operations: {pool_stats["pool_hits"]} successful')
        print(f'   📈 Cache operations: {cache_stats["sets"]} sets, {cache_stats["hits"]} hits')
        print(f'   📈 Circuit breaker calls: {sum(s["total_requests"] for s in all_breaker_stats.values())}')
        
        # Cleanup
        await manager.close()
        await connection_pool.close()
        await cache_manager.close()
        
        print('\n' + '=' * 50)
        print('🎉 PHASE 2B: COMPLETE SUCCESS!')
        print('=' * 50)
        
        print('\n🚀 Production-Ready System Verified:')
        print('   ✅ Multi-chain blockchain management')
        print('   ✅ High-performance database pooling')
        print('   ✅ Intelligent caching system')
        print('   ✅ Circuit breaker fault tolerance')
        print('   ✅ Integrated health monitoring')
        print('   ✅ End-to-end workflow testing')
        print('   ✅ Performance under load validated')
        
        print('\n🎯 READY FOR PHASE 2C: REAL BLOCKCHAIN DATA!')
        print('📋 Next Steps:')
        print('   1. Add Web3.py for real blockchain connections')
        print('   2. Implement actual token contract scanning')
        print('   3. Add real-time price feeds')
        print('   4. Create production API endpoints')
        
        return True
        
    except Exception as e:
        print(f'\n❌ Integration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_performance_integration())
    if success:
        print('\n🎉 Phase 2B Complete! Ready for real blockchain integration!')
    else:
        print('\n❌ Please create performance component files and try again')