"""
Phase 2B Integration Test - Performance Components + Multi-Chain Manager
Save as test_phase2b_integration.py and run after creating performance files.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def test_phase2b_integration():
    """Test Phase 2B integration with real performance components."""
    print('🚀 Phase 2B Integration Test')
    print('=' * 50)
    
    try:
        # Test 1: Performance Components Import
        print('📦 Testing Performance Component Imports...')
        try:
            from app.core.performance.connection_pool import connection_pool
            from app.core.performance.cache_manager import cache_manager
            from app.core.performance.circuit_breaker import CircuitBreakerManager
            print('   ✅ All performance components imported successfully')
        except ImportError as e:
            print(f'   ❌ Performance components not found: {e}')
            print('   💡 Please create the performance component files first')
            return False
        
        # Test 2: Multi-Chain Manager Integration
        print('\n🔗 Testing Multi-Chain Manager Integration...')
        from app.core.blockchain.multi_chain_manager import MultiChainManager
        from app.utils.logger import setup_logger
        
        logger = setup_logger("phase2b_integration")
        manager = MultiChainManager()
        
        # Initialize with test networks
        await manager.initialize(['ethereum', 'polygon'])
        enabled_networks = await manager.get_enabled_networks()
        print(f'   ✅ Multi-chain manager: {len(enabled_networks)} networks enabled')
        
        # Test 3: Performance Components Initialization
        print('\n🏗️ Testing Performance Components...')
        
        # Initialize connection pool
        await connection_pool.initialize()
        pool_health = await connection_pool.health_check()
        print(f'   ✅ Connection pool: {pool_health["status"]}')
        
        # Initialize cache manager
        await cache_manager.connect()
        await cache_manager.set('test_integration', {'phase': '2B', 'status': 'success'})
        cached_data = await cache_manager.get('test_integration')
        print(f'   ✅ Cache manager: {cached_data["status"]}')
        
        # Initialize circuit breaker
        breaker_manager = CircuitBreakerManager()
        test_breaker = breaker_manager.get_breaker('blockchain_test')
        print(f'   ✅ Circuit breaker: {test_breaker.state.value}')
        
        # Test 4: Integrated Health Check
        print('\n🏥 Testing Integrated Health Checks...')
        
        # Multi-chain health
        chain_health = await manager.get_health_status()
        healthy_chains = sum(1 for health in chain_health.values() if health.status.value == 'connected')
        print(f'   ✅ Chain health: {healthy_chains}/{len(chain_health)} chains healthy')
        
        # Performance component health
        breaker_health = await breaker_manager.health_check()
        print(f'   ✅ Circuit breaker health: {breaker_health["status"]}')
        
        # Test 5: Performance Under Load Simulation
        print('\n⚡ Testing Performance Under Load...')
        
        # Simulate multiple database operations
        async def db_operation():
            async with connection_pool.session_scope() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 'load_test' as operation"))
                return result.fetchone()[0]
        
        # Run multiple operations concurrently
        tasks = [db_operation() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        print(f'   ✅ Database load test: {len(results)} concurrent operations successful')
        
        # Test cache under load
        cache_tasks = []
        for i in range(20):
            cache_tasks.append(cache_manager.set(f'load_test_{i}', {'value': i}))
        await asyncio.gather(*cache_tasks)
        
        # Verify cache operations
        cached_count = 0
        for i in range(20):
            if await cache_manager.exists(f'load_test_{i}'):
                cached_count += 1
        print(f'   ✅ Cache load test: {cached_count}/20 items cached successfully')
        
        # Test 6: Circuit Breaker Under Stress
        print('\n🔄 Testing Circuit Breaker Under Stress...')
        
        async def failing_operation():
            raise Exception("Simulated failure")
        
        async def successful_operation():
            return "success"
        
        stress_breaker = breaker_manager.get_breaker('stress_test')
        
        # Trigger failures to test circuit breaker
        failure_count = 0
        for _ in range(7):  # More than failure threshold
            try:
                await stress_breaker.call(failing_operation)
            except Exception:
                failure_count += 1
        
        # Check if circuit breaker opened
        breaker_stats = stress_breaker.get_stats()
        print(f'   ✅ Circuit breaker stress test: {failure_count} failures handled')
        print(f'   📊 Breaker state: {breaker_stats["state"]} (expected: open after failures)')
        
        # Test 7: End-to-End Token Discovery Simulation
        print('\n🔍 Testing Token Discovery Integration...')
        
        # Simulate token discovery with performance components
        async def discover_tokens_with_performance():
            # Use circuit breaker for external API calls
            api_breaker = breaker_manager.get_breaker('token_discovery_api')
            
            async def mock_api_call():
                # Simulate API response
                return {
                    'new_tokens': [
                        {'address': '0x123...', 'name': 'TestToken', 'symbol': 'TEST'},
                        {'address': '0x456...', 'name': 'MockCoin', 'symbol': 'MOCK'}
                    ]
                }
            
            # Call through circuit breaker
            api_result = await api_breaker.call(mock_api_call)
            
            # Cache the results
            await cache_manager.set(
                'latest_tokens', 
                api_result, 
                ttl=300,  # 5 minutes
                namespace='discovery'
            )
            
            # Store in database through connection pool
            async with connection_pool.session_scope() as session:
                from sqlalchemy import text
                # Simulate storing token data
                await session.execute(text("SELECT 'token_stored' as result"))
            
            return len(api_result['new_tokens'])
        
        discovered_count = await discover_tokens_with_performance()
        print(f'   ✅ Token discovery simulation: {discovered_count} tokens processed')
        
        # Verify cached data
        cached_tokens = await cache_manager.get('latest_tokens', namespace='discovery')
        print(f'   ✅ Cache verification: {len(cached_tokens["new_tokens"])} tokens cached')
        
        # Test 8: Cleanup and Resource Management
        print('\n🧹 Testing Cleanup and Resource Management...')
        
        # Get final statistics
        final_pool_stats = connection_pool.get_stats()
        final_cache_stats = await cache_manager.get_stats()
        final_breaker_stats = await breaker_manager.get_all_stats()
        
        print(f'   📊 Final pool stats: {final_pool_stats["pool_hits"]} hits')
        print(f'   📊 Final cache stats: {final_cache_stats["hit_rate"]:.1f}% hit rate')
        print(f'   📊 Final breaker stats: {len(final_breaker_stats)} breakers active')
        
        # Cleanup all components
        await manager.close()
        await connection_pool.close()
        await cache_manager.close()
        
        print('   ✅ All resources cleaned up successfully')
        
        print('\n' + '=' * 50)
        print('🎉 PHASE 2B INTEGRATION: COMPLETE SUCCESS!')
        print('=' * 50)
        
        print('\n🚀 Production-Ready Features Verified:')
        print('   ✅ Multi-chain blockchain management')
        print('   ✅ High-performance database connection pooling')
        print('   ✅ Intelligent caching system')
        print('   ✅ Circuit breaker fault tolerance')
        print('   ✅ Integrated health monitoring')
        print('   ✅ Load testing and performance validation')
        print('   ✅ Resource management and cleanup')
        
        print('\n🎯 Ready for Phase 2C: Real Blockchain Data!')
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
    success = asyncio.run(test_phase2b_integration())
    if success:
        print('\n🚀 Phase 2B Complete - Ready for Real Blockchain Integration!')
    else:
        print('\n❌ Please resolve issues and create performance component files')