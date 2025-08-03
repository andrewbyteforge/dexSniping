"""
Simple Phase 3A Test - Basic validation without complex dependencies
File: simple_phase3a_test.py

This test provides a simpler validation approach that focuses on
core component availability and basic functionality testing.

Usage: python simple_phase3a_test.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())


def print_header(title: str):
    """Print formatted header."""
    print('\n' + '=' * 60)
    print(f'{title:^60}')
    print('=' * 60)


def print_section(title: str):
    """Print formatted section."""
    print(f'\n{title}')
    print('-' * 40)


async def test_basic_imports():
    """Test basic component imports."""
    print_section('📦 Testing Basic Imports')
    
    results = {}
    
    # Test 1: Configuration
    try:
        from app.config import settings
        print('   ✅ Configuration system')
        results['config'] = True
    except Exception as e:
        print(f'   ❌ Configuration: {e}')
        results['config'] = False
    
    # Test 2: Schemas
    try:
        from app.schemas.token import TokenResponse
        print('   ✅ Token schemas')
        results['schemas'] = True
    except Exception as e:
        print(f'   ❌ Schemas: {e}')
        results['schemas'] = False
    
    # Test 3: Core Discovery
    try:
        from app.core.discovery.token_scanner import TokenScanner
        print('   ✅ Token scanner')
        results['scanner'] = True
    except Exception as e:
        print(f'   ❌ Token scanner: {e}')
        results['scanner'] = False
    
    # Test 4: Risk Calculator
    try:
        from app.core.risk.risk_calculator import RiskCalculator
        print('   ✅ Risk calculator')
        results['risk'] = True
    except Exception as e:
        print(f'   ❌ Risk calculator: {e}')
        results['risk'] = False
    
    # Test 5: Database Models
    try:
        from app.models.token import Token
        print('   ✅ Database models')
        results['models'] = True
    except Exception as e:
        print(f'   ❌ Database models: {e}')
        results['models'] = False
    
    # Test 6: Performance Components
    try:
        from app.core.performance.connection_pool import connection_pool
        print('   ✅ Performance infrastructure')
        results['performance'] = True
    except Exception as e:
        print(f'   ❌ Performance: {e}')
        results['performance'] = False
    
    return results


async def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print_section('⚡ Testing Basic Functionality')
    
    results = {}
    
    try:
        # Override to SQLite to avoid PostgreSQL auth issues
        from app.config import settings
        settings.database_url = "sqlite+aiosqlite:///./test_simple.db"
        
        # Test connection pool
        from app.core.performance.connection_pool import connection_pool
        await connection_pool.initialize()
        
        async with connection_pool.session_scope() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 'Database working!'"))
            row = result.fetchone()
            assert 'Database working!' in str(row)
        
        print('   ✅ Database operations')
        results['database'] = True
        
        # Test cache manager
        from app.core.performance.cache_manager import cache_manager
        await cache_manager.connect()
        
        await cache_manager.set('test_key', {'status': 'working'})
        cached_data = await cache_manager.get('test_key')
        assert cached_data['status'] == 'working'
        
        print('   ✅ Cache operations')
        results['cache'] = True
        
        # Test circuit breaker
        from app.core.performance.circuit_breaker import CircuitBreakerManager
        breaker_manager = CircuitBreakerManager()
        test_breaker = breaker_manager.get_breaker('simple_test')
        
        async def test_operation():
            return "Circuit breaker working"
        
        result = await test_breaker.call(test_operation)
        assert result == "Circuit breaker working"
        
        print('   ✅ Circuit breakers')
        results['breaker'] = True
        
        # Cleanup
        await connection_pool.close()
        await cache_manager.close()
        
    except Exception as e:
        print(f'   ❌ Functionality test failed: {e}')
        results['database'] = False
        results['cache'] = False
        results['breaker'] = False
    
    return results


async def test_blockchain_readiness():
    """Test blockchain component readiness."""
    print_section('🌐 Testing Blockchain Readiness')
    
    results = {}
    
    try:
        # Test multi-chain manager import
        from app.core.blockchain.multi_chain_manager import MultiChainManager
        print('   ✅ Multi-chain manager')
        results['multi_chain'] = True
        
        # Test Ethereum chain
        from app.core.blockchain.evm_chains.ethereum_real import RealEthereumChain
        print('   ✅ Real Ethereum chain')
        results['ethereum'] = True
        
        # Test mempool components
        try:
            from app.core.mempool.mempool_manager import MempoolManager
            print('   ✅ Mempool manager')
            results['mempool'] = True
        except ImportError:
            print('   ⚠️ Mempool manager (optional for basic test)')
            results['mempool'] = False
        
    except Exception as e:
        print(f'   ❌ Blockchain readiness: {e}')
        results['multi_chain'] = False
        results['ethereum'] = False
        results['mempool'] = False
    
    return results


async def main():
    """Main test function."""
    print_header('🚀 SIMPLE PHASE 3A VALIDATION TEST')
    
    print(f'📅 Test Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'🎯 Objective: Basic Phase 3A component validation')
    print(f'🔧 Approach: Simple imports and functionality testing')
    
    all_results = {}
    
    # Test 1: Basic Imports
    import_results = await test_basic_imports()
    all_results.update(import_results)
    
    # Test 2: Basic Functionality  
    func_results = await test_basic_functionality()
    all_results.update(func_results)
    
    # Test 3: Blockchain Readiness
    blockchain_results = await test_blockchain_readiness()
    all_results.update(blockchain_results)
    
    # Final Assessment
    print_header('📊 SIMPLE TEST RESULTS')
    
    passed_tests = sum(all_results.values())
    total_tests = len(all_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f'\n📈 Success Rate: {passed_tests}/{total_tests} ({success_rate:.0f}%)')
    
    print('\n📋 Component Status:')
    for component, status in all_results.items():
        icon = '✅' if status else '❌'
        print(f'   {icon} {component.replace("_", " ").title()}')
    
    # Recommendations
    if success_rate >= 90:
        print('\n🎉 EXCELLENT! Core components ready for Phase 3B')
        print('\n🚀 Recommendations:')
        print('   1. Run full test suite: python test_phase3a_validation.py')
        print('   2. Begin Phase 3B development with confidence')
        print('   3. Focus on advanced DEX integration features')
        
    elif success_rate >= 75:
        print('\n✅ GOOD! Most components working, minor fixes needed')
        print('\n🔧 Next Steps:')
        failing_components = [comp for comp, status in all_results.items() if not status]
        for comp in failing_components:
            print(f'   • Fix {comp.replace("_", " ")} component')
        print('   • Re-run test after fixes')
        
    elif success_rate >= 50:
        print('\n⚠️ PARTIAL SUCCESS - Core infrastructure needs work')
        print('\n🚨 Priority Fixes:')
        print('   • Ensure all dependencies are installed')
        print('   • Check database configuration')
        print('   • Verify Python path and imports')
        
    else:
        print('\n❌ CRITICAL ISSUES - Major components failing')
        print('\n🆘 Emergency Actions:')
        print('   • Check virtual environment activation')
        print('   • Run: pip install -r requirements.txt')
        print('   • Verify project structure and file locations')
    
    # Phase 3B Readiness
    print('\n🎯 Phase 3B Readiness Assessment:')
    if success_rate >= 80:
        print('   🚀 READY for Phase 3B development')
        print('   🎯 Can proceed with advanced trading features')
    elif success_rate >= 60:
        print('   ⚠️ MOSTLY READY - address failing components first')
        print('   🔧 Complete fixes before Phase 3B')
    else:
        print('   ❌ NOT READY - resolve critical issues first')
        print('   🚨 Complete Phase 3A before attempting Phase 3B')
    
    return success_rate >= 75


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        
        if success:
            print('\n🎉 Simple validation passed! Ready for advanced testing.')
            sys.exit(0)
        else:
            print('\n⚠️ Please resolve issues before advanced testing.')
            sys.exit(1)
            
    except KeyboardInterrupt:
        print('\n\n⏹️ Test interrupted by user')
        sys.exit(1)
        
    except Exception as e:
        print(f'\n❌ Simple test failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)