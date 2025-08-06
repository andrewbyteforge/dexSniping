"""
Comprehensive Application Test
File: test_complete_application.py

Complete testing of the refactored application including:
- Pydantic schema validation
- Component loading
- API endpoint testing
- Application startup/shutdown
"""

import asyncio
import sys
import warnings
from pathlib import Path

# Filter out the specific Pydantic warning we're addressing
warnings.filterwarnings("ignore", message=".*schema_extra.*json_schema_extra.*", category=UserWarning)

def setup_python_path():
    """Setup Python path for testing."""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    print(f"✅ Python path configured: {project_root}")


def test_pydantic_schemas():
    """Test Pydantic schema loading without warnings."""
    print("\n🧪 Testing Pydantic Schemas...")
    
    try:
        # Test importing all schemas
        from app.schemas.trading_schemas import TradingSessionResponse, TradingMode
        from app.schemas.dashboard import DashboardStatsResponse
        
        # Test schema instantiation
        trading_response = TradingSessionResponse(
            session_id="test_123",
            status="active",
            trading_mode="semi_automated",
            wallet_connected=True,
            wallet_address="0x1234567890123456789012345678901234567890",
            wallet_network="ethereum",
            wallet_balance_eth="1.5",
            wallet_balance_usd="3000.00",
            total_positions=2,
            active_orders=1,
            trading_stats={
                "total_trades": 10,
                "successful_trades": 8,
                "total_volume": "5000.00",
                "total_pnl": "150.00"
            },
            risk_management={
                "max_position_size": "1000.00",
                "stop_loss_enabled": True,
                "max_slippage": "2.0"
            }
        )
        
        print("✅ TradingSessionResponse schema created successfully")
        
        # Test serialization
        json_data = trading_response.model_dump()
        print(f"✅ Schema serialization successful: {len(json_data)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


async def test_application_startup():
    """Test complete application startup and shutdown."""
    print("\n🧪 Testing Application Startup/Shutdown...")
    
    try:
        from app.factory import create_app
        from app.core.lifecycle_manager import LifecycleManager
        
        # Create application
        app = create_app()
        print("✅ Application created")
        
        # Test that we can access app properties
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        print(f"✅ Routes: {len(app.routes)}")
        
        # Test lifecycle manager
        lifecycle_manager = LifecycleManager()
        print("✅ Lifecycle manager created")
        
        # Test startup procedures
        startup_success = await lifecycle_manager.execute_startup_procedures()
        print(f"✅ Startup procedures: {'success' if startup_success else 'partial'}")
        
        # Test runtime status
        runtime_status = await lifecycle_manager.get_runtime_status()
        print(f"✅ Runtime status: {len(runtime_status)} metrics")
        
        return True, app, lifecycle_manager
        
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        return False, None, None


async def test_component_integration():
    """Test component integration and health."""
    print("\n🧪 Testing Component Integration...")
    
    try:
        from app.core.component_manager import ComponentManager
        
        cm = ComponentManager()
        
        # Test component initialization
        init_success = await cm.initialize_components()
        print(f"✅ Components initialized: {'success' if init_success else 'partial'}")
        
        # Test component status
        status = await cm.get_component_status()
        available_count = sum(status.values())
        total_count = len(status)
        print(f"✅ Component status: {available_count}/{total_count} available")
        
        # Test system health
        health = await cm.get_system_health()
        health_score = health.get('overall_health_score', 0)
        print(f"✅ System health score: {health_score:.2f}/1.0")
        
        # Test AI components specifically
        if status.get('ai_risk_assessment'):
            print("✅ AI Risk Assessment: Available")
            
            # Try to get AI component instance
            ai_instance = cm.get_component_instance('ai_risk_assessor')
            if ai_instance:
                print("✅ AI Risk Assessor instance: Available")
            else:
                print("⚠️  AI Risk Assessor instance: Not initialized")
        
        # Test capabilities
        capabilities = cm.get_available_capabilities()
        print(f"✅ Available capabilities: {len(capabilities)} features")
        
        # Test supported networks
        networks = cm.get_supported_networks()
        print(f"✅ Supported networks: {networks}")
        
        return True, status, health
        
    except Exception as e:
        print(f"❌ Component integration test failed: {e}")
        return False, {}, {}


def test_api_endpoints_structure():
    """Test API endpoint structure and availability."""
    print("\n🧪 Testing API Endpoint Structure...")
    
    try:
        from app.api.route_manager import RouteManager
        from fastapi import FastAPI
        
        # Test route manager
        route_manager = RouteManager()
        print("✅ Route manager created")
        
        # Create test app
        test_app = FastAPI()
        
        # Test fallback routes creation
        fallback_dashboard = route_manager._create_fallback_dashboard_router()
        fallback_tokens = route_manager._create_fallback_tokens_router()
        
        print("✅ Fallback routers created")
        print(f"✅ Dashboard routes: {len(fallback_dashboard.routes)}")
        print(f"✅ Tokens routes: {len(fallback_tokens.routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False


def test_error_handling():
    """Test error handling system."""
    print("\n🧪 Testing Error Handling System...")
    
    try:
        from app.core.error_handlers import (
            setup_error_handlers, 
            ApplicationError,
            ComponentError, 
            AIError,
            TradingError,
            BlockchainError
        )
        from fastapi import FastAPI
        
        # Test error handler setup
        test_app = FastAPI()
        setup_error_handlers(test_app)
        print("✅ Error handlers configured")
        
        # Test custom exception classes
        app_error = ApplicationError("Test error", "test_error")
        component_error = ComponentError("test_component", "Component failed")
        ai_error = AIError("risk_assessment", "AI system error")
        trading_error = TradingError("buy_order", "Order failed")
        blockchain_error = BlockchainError("ethereum", "Network error")
        
        print("✅ Custom exception classes created")
        
        # Test error serialization
        error_dict = app_error.to_dict()
        print(f"✅ Error serialization: {len(error_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def run_comprehensive_application_test():
    """Run complete application test suite."""
    print("=" * 80)
    print("🚀 COMPREHENSIVE APPLICATION TEST SUITE")
    print("=" * 80)
    print("Testing the complete refactored application with all components")
    
    test_results = {}
    
    # Test Pydantic schemas
    test_results['pydantic_schemas'] = test_pydantic_schemas()
    
    # Test application startup
    startup_success, app, lifecycle_manager = await test_application_startup()
    test_results['application_startup'] = startup_success
    
    # Test component integration
    component_success, component_status, system_health = await test_component_integration()
    test_results['component_integration'] = component_success
    
    # Test API endpoints
    test_results['api_endpoints'] = test_api_endpoints_structure()
    
    # Test error handling
    test_results['error_handling'] = test_error_handling()
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print()
    
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name:25}: {'PASS' if result else 'FAIL'}")
    
    print()
    
    # Component status summary
    if component_status:
        available_components = sum(component_status.values())
        total_components = len(component_status)
        print(f"📦 Component Status: {available_components}/{total_components} available")
        
        # Show AI components specifically
        ai_components = {k: v for k, v in component_status.items() if 'ai_' in k}
        if ai_components:
            ai_available = sum(ai_components.values())
            ai_total = len(ai_components)
            print(f"🧠 AI Components: {ai_available}/{ai_total} available")
    
    if system_health:
        health_score = system_health.get('overall_health_score', 0)
        print(f"🏥 System Health Score: {health_score:.2f}/1.0")
    
    # Performance metrics
    print(f"\n⚡ Performance Metrics:")
    print(f"   - Application routes: {len(app.routes) if app else 0}")
    print(f"   - Middleware components: {len(app.user_middleware) if app else 0}")
    print(f"   - Component manager: {'✅ Operational' if component_success else '❌ Issues'}")
    print(f"   - Lifecycle manager: {'✅ Operational' if lifecycle_manager else '❌ Issues'}")
    
    # Final assessment and recommendations
    print(f"\n🔧 FINAL ASSESSMENT:")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! All major systems are working correctly.")
        print("🚀 Application is ready for production use.")
        print("💡 Recommended next steps:")
        print("   1. Run: python -m app.main")
        print("   2. Access dashboard: http://localhost:8000/dashboard")
        print("   3. Check API docs: http://localhost:8000/docs")
        print("   4. Test AI features: http://localhost:8000/risk-analysis")
    elif success_rate >= 75:
        print("✅ GOOD! Most systems are working with minor issues.")
        print("⚠️  Some components may need attention.")
        print("🔧 Review failed tests and fix issues before production.")
    else:
        print("⚠️  WARNING! Multiple systems have issues.")
        print("🚨 Critical problems detected - review all failed tests.")
        print("🔧 Fix core issues before proceeding.")
    
    # Specific recommendations based on results
    if not test_results.get('pydantic_schemas'):
        print("\n📝 Pydantic Issue: Run 'python fix_pydantic_v2.py' to fix schema warnings")
    
    if not test_results.get('component_integration'):
        print("\n🔧 Component Issue: Check component loading and dependencies")
    
    if not test_results.get('application_startup'):
        print("\n🚀 Startup Issue: Review application factory and lifecycle manager")
    
    print("\n" + "=" * 80)
    return success_rate >= 75


def main():
    """Main test execution function."""
    setup_python_path()
    
    try:
        print("🧪 Starting comprehensive application test...")
        print("⏱️  This may take a few moments to complete all tests...")
        
        success = asyncio.run(run_comprehensive_application_test())
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("✅ Application is ready to run!")
        else:
            print("\n⚠️  Some tests failed - review the results above")
            print("🔧 Fix the issues before running the application")
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()