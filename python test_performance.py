"""
Test script for performance components.
Run with: python test_performance.py
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.performance.connection_pool import connection_pool
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager

async def test_performance_components():
    """Test all performance components."""
    print('🚀 Testing performance components...')
    
    try:
        # Test connection pool
        print('📊 Testing connection pool...')
        await connection_pool.initialize()
        session = await connection_pool.get_session()
        print(f'✅ Connection pool: {type(session).__name__}')
        
        # Test cache manager (will work without Redis)
        print('💾 Testing cache manager...')
        await cache_manager.connect()
        await cache_manager.set('test_key', {'test': 'value'})
        result = await cache_manager.get('test_key')
        print(f'✅ Cache manager: {result}')
        
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
        
        # Cleanup
        await connection_pool.close()
        await cache_manager.close()
        
        print('🎉 All performance components working!')
        
    except Exception as e:
        print(f'❌ Error testing performance components: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_performance_components())