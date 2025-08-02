"""
Run this script to test the performance components.
Save as test_performance_components.py and run with: python test_performance_components.py
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

async def test_performance_components():
    """Test all performance components."""
    print('🚀 Testing performance components...')
    
    try:
        # Import the performance components
        from app.core.performance.connection_pool import connection_pool
        from app.core.performance.cache_manager import cache_manager
        from app.core.performance.circuit_breaker import CircuitBreakerManager
        
        print('✅ Successfully imported all performance components')
        
        # Test connection pool
        print('📊 Testing connection pool...')
        await connection_pool.initialize()
        session = await connection_pool.get_session()
        print(f'✅ Connection pool: {type(session).__name__}')
        pool_stats = connection_pool.get_stats()
        print(f'📈 Pool stats: {pool_stats["active_connections"]} active connections')
        
        # Test cache manager (will work without Redis)
        print('💾 Testing cache manager...')
        await cache_manager.connect()
        await cache_manager.set('test_key', {'test': 'value', 'timestamp': '2025-01-01'})
        result = await cache_manager.get('test_key')
        print(f'✅ Cache manager: {result}')
        cache_stats = await cache_manager.get_stats()
        print(f'📊 Cache stats: {cache_stats["cache_type"]} with {cache_stats["sets"]} sets')
        
        # Test circuit breaker
        print('🔄 Testing circuit breaker...')
        breaker_manager = CircuitBreakerManager()
        breaker = breaker_manager.get_breaker('test_service')
        print(f'✅ Circuit breaker: {breaker.state.value}')
        
        # Test circuit breaker functionality
        async def test_function():
            return "success"
        
        # Test successful call
        result = await breaker.call(test_function)
        print(f'✅ Circuit breaker call: {result}')
        
        # Get circuit breaker stats
        breaker_stats = breaker.get_stats()
        print(f'📊 Circuit breaker stats: {breaker_stats["total_requests"]} requests, {breaker_stats["success_rate"]}% success rate')
        
        # Test health checks
        print('🏥 Testing health checks...')
        pool_health = await connection_pool.health_check()
        print(f'✅ Connection pool health: {pool_health["status"]}')
        
        manager_health = await breaker_manager.health_check()
        print(f'✅ Circuit breaker health: {manager_health["status"]}')
        
        # Cleanup
        print('🧹 Cleaning up...')
        await connection_pool.close()
        await cache_manager.close()
        
        print('🎉 All performance components working perfectly!')
        print('✅ Phase 2 Infrastructure: Connection Pool, Cache Manager, Circuit Breaker')
        print('✅ Ready for next development phase!')
        
    except ImportError as e:
        print(f'❌ Import error: {e}')
        print('💡 Make sure to create the performance component files first')
        return False
    except Exception as e:
        print(f'❌ Error testing performance components: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_performance_components())
    if success:
        print('\n🚀 Phase 2 infrastructure components are ready!')
        print('Next: Implement real blockchain connections with Web3.py')
    else:
        print('\n❌ Please fix the issues above before proceeding')