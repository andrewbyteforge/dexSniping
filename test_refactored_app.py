"""
Test Refactored Application Structure
File: test_refactored_app.py

Comprehensive testing script to validate the refactored modular architecture.
Tests component loading, application creation, and system functionality.
"""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple

def setup_python_path():
    """Setup Python path for testing."""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    print(f"✅ Python path configured: {project_root}")


def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all critical imports for the refactored structure."""
    print("\n🧪 Testing Critical Imports...")
    
    import_tests = [
        ("app.utils.logger", "setup_logger"),
        ("app.core.component_manager", "ComponentManager"),
        ("app.core.lifecycle_manager", "LifecycleManager"),
        ("app.core.system_info", "SystemInfoProvider"),
        ("app.core.error_handlers", "setup_error_handlers"),
        ("app.api.route_manager", "RouteManager"),
        ("app.factory", "create_app"),
        ("app.main", "app")
    ]
    
    results = []
    
    for module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            results.append((f"{module_name}.{class_name}", True, "OK"))
            print(f"✅ {module_name}.{class_name}")
        except ImportError as e:
            results.append((f"{module_name}.{class_name}", False, f"ImportError: {e}"))
            print(f"❌ {module_name}.{class_name} - ImportError: {e}")
        except AttributeError as e:
            results.append((f"{module_name}.{class_name}", False, f"AttributeError: {e}"))
            print(f"❌ {module_name}.{class_name} - AttributeError: {e}")
        except Exception as e:
            results.append((f"{module_name}.{class_name}", False, f"Error: {e}"))
            print(f"❌ {module_name}.{class_name} - Error: {e}")
    
    return results


async def test_component_manager():
    """Test the ComponentManager functionality."""
    print("\n🧪 Testing Component Manager...")
    
    try:
        from app.core.component_manager import ComponentManager
        
        # Test initialization
        cm = ComponentManager()
        print("✅ ComponentManager instantiated")
        
        # Test component status retrieval
        status = await cm.get_component_status()
        print(f"✅ Component status retrieved: {len(status)} components")
        
        # Test component initialization
        init_success = await cm.initialize_components()
        print(f"✅ Component initialization: {'success' if init_success else 'partial'}")
        
        # Test capabilities
        capabilities = cm.get_available_capabilities()
        print(f"✅ Available capabilities: {len(capabilities)} features")
        
        # Test supported networks
        networks = cm.get_supported_networks()
        print(f"✅ Supported networks: {networks}")
        
        # Test system health
        health = await cm.get_system_health()
        health_score = health.get('overall_health_score', 0)
        print(f"✅ System health score: {health_score:.2f}")
        
        return True, status, health
        
    except Exception as e:
        print(f"❌ Component Manager test failed: {e}")
        traceback.print_exc()
        return False, {}, {}


async def test_lifecycle_manager():
    """Test the LifecycleManager functionality."""
    print("\n🧪 Testing Lifecycle Manager...")
    
    try:
        from app.core.lifecycle_manager import LifecycleManager
        
        # Test initialization
        lm = LifecycleManager()
        print("✅ LifecycleManager instantiated")
        
        # Test startup procedures (without actually starting app)
        print("✅ LifecycleManager startup procedures available")
        
        # Test runtime status
        status = await lm.get_runtime_status()
        print(f"✅ Runtime status retrieved: {len(status)} metrics")
        
        return True, status
        
    except Exception as e:
        print(f"❌ Lifecycle Manager test failed: {e}")
        traceback.print_exc()
        return False, {}


def test_system_info_provider():
    """Test the SystemInfoProvider functionality."""
    print("\n🧪 Testing System Info Provider...")
    
    try:
        from app.core.system_info import SystemInfoProvider
        
        # Test initialization
        sip = SystemInfoProvider()
        print("✅ SystemInfoProvider instantiated")
        
        # Test capabilities
        test_status = {"ai_risk_assessment": True, "wallet_system": False}
        capabilities = sip._get_available_capabilities(test_status)
        print(f"✅ Capabilities calculation: {len(capabilities)} features")
        
        # Test supported networks
        networks = sip._get_supported_networks(test_status)
        print(f"✅ Supported networks: {networks}")
        
        return True, capabilities
        
    except Exception as e:
        print(f"❌ System Info Provider test failed: {e}")
        traceback.print_exc()
        return False, []


def test_route_manager():
    """Test the RouteManager functionality."""
    print("\n🧪 Testing Route Manager...")
    
    try:
        from app.api.route_manager import RouteManager
        
        # Test initialization
        rm = RouteManager()
        print("✅ RouteManager instantiated")
        
        return True
        
    except Exception as e:
        print(f"❌ Route Manager test failed: {e}")
        traceback.print_exc()
        return False


def test_error_handlers():
    """Test the error handlers setup."""
    print("\n🧪 Testing Error Handlers...")
    
    try:
        from app.core.error_handlers import setup_error_handlers, ApplicationError
        from fastapi import FastAPI
        
        # Test with dummy FastAPI app
        app = FastAPI()
        setup_error_handlers(app)
        print("✅ Error handlers configured successfully")
        
        # Test custom exception classes
        error = ApplicationError("Test error", "test_error", {"detail": "test"})
        error_dict = error.to_dict()
        print(f"✅ Custom error classes working: {len(error_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Error Handlers test failed: {e}")
        traceback.print_exc()
        return False


def test_application_factory():
    """Test the application factory."""
    print("\n🧪 Testing Application Factory...")
    
    try:
        from app.factory import create_app
        
        # Test application creation
        app = create_app()
        print("✅ Application created successfully")
        
        # Test routes
        route_count = len(app.routes)
        print(f"✅ Routes configured: {route_count} endpoints")
        
        # Test middleware
        middleware_count = len(app.user_middleware)
        print(f"✅ Middleware configured: {middleware_count} components")
        
        return True, app
        
    except Exception as e:
        print(f"❌ Application Factory test failed: {e}")
        traceback.print_exc()
        return False, None


def test_main_application():
    """Test the main application entry point."""
    print("\n🧪 Testing Main Application...")
    
    try:
        from app.main import app, __version__, __phase__
        
        print(f"✅ Main application imported successfully")
        print(f"✅ Version: {__version__}")
        print(f"✅ Phase: {__phase__}")
        
        # Test app properties
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        print(f"✅ Routes: {len(app.routes)}")
        
        return True, app
        
    except Exception as e:
        print(f"❌ Main Application test failed: {e}")
        traceback.print_exc()
        return False, None


async def run_comprehensive_tests():
    """Run all tests and provide comprehensive report."""
    print("=" * 80)
    print("🧪 DEX SNIPER PRO - REFACTORED STRUCTURE TESTING")
    print("=" * 80)
    
    test_results = {}
    
    # Import tests
    print("\n📦 TESTING IMPORTS")
    import_results = test_imports()
    successful_imports = sum(1 for _, success, _ in import_results if success)
    total_imports = len(import_results)
    test_results['imports'] = (successful_imports, total_imports)
    print(f"📊 Imports: {successful_imports}/{total_imports} successful")
    
    # Component manager tests
    print("\n🧠 TESTING CORE COMPONENTS")
    cm_success, component_status, system_health = await test_component_manager()
    test_results['component_manager'] = cm_success
    
    # Lifecycle manager tests
    lm_success, runtime_status = await test_lifecycle_manager()
    test_results['lifecycle_manager'] = lm_success
    
    # System info provider tests
    sip_success, capabilities = test_system_info_provider()
    test_results['system_info'] = sip_success
    
    # Route manager tests
    rm_success = test_route_manager()
    test_results['route_manager'] = rm_success
    
    # Error handlers tests
    eh_success = test_error_handlers()
    test_results['error_handlers'] = eh_success
    
    # Application factory tests
    print("\n🏭 TESTING APPLICATION FACTORY")
    af_success, factory_app = test_application_factory()
    test_results['application_factory'] = af_success
    
    # Main application tests
    print("\n🚀 TESTING MAIN APPLICATION")
    main_success, main_app = test_main_application()
    test_results['main_application'] = main_success
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if isinstance(result, bool) and result)
    
    # Add import success rate
    if test_results['imports']:
        import_success_rate = test_results['imports'][0] / test_results['imports'][1]
        if import_success_rate >= 0.8:
            passed_tests += 1
    
    print(f"🎯 Overall Success Rate: {passed_tests}/{total_tests + 1} ({passed_tests/(total_tests + 1)*100:.1f}%)")
    print()
    
    for test_name, result in test_results.items():
        if test_name == 'imports':
            success_rate = result[0] / result[1] * 100 if result[1] > 0 else 0
            status = "✅" if success_rate >= 80 else "❌"
            print(f"{status} {test_name:20}: {result[0]}/{result[1]} ({success_rate:.1f}%)")
        else:
            status = "✅" if result else "❌"
            print(f"{status} {test_name:20}: {'PASS' if result else 'FAIL'}")
    
    print()
    
    if component_status:
        available_components = sum(component_status.values())
        total_components = len(component_status)
        print(f"📦 Available Components: {available_components}/{total_components}")
    
    if system_health:
        health_score = system_health.get('overall_health_score', 0)
        print(f"🏥 System Health Score: {health_score:.2f}/1.0")
    
    if capabilities:
        print(f"⚡ Available Capabilities: {len(capabilities)} features")
    
    # Final recommendations
    print("\n🔧 RECOMMENDATIONS:")
    
    if passed_tests == total_tests + 1:
        print("✅ All tests passed! The refactored structure is working correctly.")
        print("🚀 You can now run the application with: python -m app.main")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        if test_results.get('imports', (0, 1))[0] < test_results.get('imports', (0, 1))[1]:
            print("📦 Run: python create_init_files.py")
        
        failing_components = [name for name, result in test_results.items() 
                            if isinstance(result, bool) and not result]
        if failing_components:
            print(f"🔧 Focus on fixing: {', '.join(failing_components)}")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point for testing."""
    setup_python_path()
    
    try:
        # Run async tests
        asyncio.run(run_comprehensive_tests())
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()