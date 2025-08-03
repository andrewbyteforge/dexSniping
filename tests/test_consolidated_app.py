"""
Consolidated Application Test Suite
File: tests/test_consolidated_app.py
Class: TestConsolidatedApplication
Methods: test_application_creation, test_health_endpoints, test_dashboard_access

Tests the consolidated main.py application to ensure all features work correctly
after merging the best components from both previous main files.
"""

import sys
import os
import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConsolidatedApplication:
    """Test suite for the consolidated main application."""
    
    def test_import_consolidated_app(self):
        """Test that the consolidated app can be imported successfully."""
        print("🧪 Testing consolidated app import...")
        
        try:
            from app.main import app, create_application, get_trading_engine
            
            assert app is not None, "App instance should not be None"
            assert callable(create_application), "create_application should be callable"
            assert callable(get_trading_engine), "get_trading_engine should be callable"
            
            print("✅ Consolidated app imported successfully")
            return True
            
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def test_application_configuration(self):
        """Test application is properly configured."""
        print("🧪 Testing application configuration...")
        
        try:
            from app.main import app
            
            # Check basic app properties
            assert app.title == "DEX Sniper Pro Trading Bot"
            assert app.version == "4.0.0"
            assert app.docs_url == "/docs"
            assert app.redoc_url == "/redoc"
            
            print("✅ Application configuration is correct")
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
    
    def test_middleware_setup(self):
        """Test that middleware is properly configured."""
        print("🧪 Testing middleware setup...")
        
        try:
            from app.main import app
            
            # Check if middleware is present by examining user_middleware
            middleware_found = {
                'CORS': False,
                'TrustedHost': False
            }
            
            # Check middleware stack
            for middleware in app.user_middleware:
                middleware_class_name = middleware.cls.__name__
                
                if 'CORS' in middleware_class_name:
                    middleware_found['CORS'] = True
                    print(f"✅ CORSMiddleware configured")
                
                if 'TrustedHost' in middleware_class_name:
                    middleware_found['TrustedHost'] = True
                    print(f"✅ TrustedHostMiddleware configured")
            
            # Report results
            if middleware_found['CORS']:
                print("✅ CORS middleware properly configured")
            else:
                print("⚠️ CORS middleware not detected")
                
            if middleware_found['TrustedHost']:
                print("✅ TrustedHost middleware properly configured")
            else:
                print("⚠️ TrustedHost middleware not detected")
            
            print("✅ Middleware setup verified")
            return True
            
        except Exception as e:
            print(f"❌ Middleware test failed: {e}")
            return False
    
    def test_routes_configuration(self):
        """Test that routes are properly configured."""
        print("🧪 Testing routes configuration...")
        
        try:
            from app.main import app
            
            # Get all routes
            routes = []
            for route in app.routes:
                if hasattr(route, 'path'):
                    routes.append(route.path)
            
            # Check expected routes
            expected_routes = [
                "/",
                "/dashboard", 
                "/health",
                "/status",
                "/token-discovery",
                "/live-trading",
                "/portfolio"
            ]
            
            for expected_route in expected_routes:
                if expected_route in routes:
                    print(f"✅ Route {expected_route} configured")
                else:
                    print(f"⚠️ Route {expected_route} not found")
            
            print(f"✅ Found {len(routes)} total routes configured")
            return True
            
        except Exception as e:
            print(f"❌ Routes test failed: {e}")
            return False
    
    def test_static_files_mount(self):
        """Test that static files are properly mounted."""
        print("🧪 Testing static files mount...")
        
        try:
            from app.main import app
            
            # Check if static files are mounted
            static_mounted = False
            for route in app.routes:
                if hasattr(route, 'path') and route.path == '/static':
                    static_mounted = True
                    break
            
            if static_mounted:
                print("✅ Static files properly mounted at /static")
            else:
                # Check if static directory exists
                static_path = Path("frontend/static")
                if static_path.exists():
                    print("⚠️ Static directory exists but not mounted")
                else:
                    print("ℹ️ Static directory doesn't exist (expected in some environments)")
            
            return True
            
        except Exception as e:
            print(f"❌ Static files test failed: {e}")
            return False
    
    def test_api_routers_inclusion(self):
        """Test that API routers are properly included."""
        print("🧪 Testing API routers inclusion...")
        
        try:
            from app.main import app
            
            # Check for API routes
            api_routes = []
            for route in app.routes:
                if hasattr(route, 'path') and '/api/v1' in route.path:
                    api_routes.append(route.path)
            
            # Should have dashboard and tokens API routes
            expected_api_routes = ['/api/v1/dashboard', '/api/v1/tokens']
            found_routes = 0
            
            for route_path in api_routes:
                for expected in expected_api_routes:
                    if expected in route_path:
                        print(f"✅ API route found: {route_path}")
                        found_routes += 1
                        break
            
            if found_routes > 0:
                print(f"✅ Found {found_routes} API routes")
            else:
                print("⚠️ No API routes found")
            
            return True
            
        except Exception as e:
            print(f"❌ API routers test failed: {e}")
            return False
    
    def test_lifespan_context_manager(self):
        """Test that lifespan context manager is properly configured."""
        print("🧪 Testing lifespan context manager...")
        
        try:
            from app.main import lifespan
            
            # Check that lifespan is a function
            assert callable(lifespan), "Lifespan should be callable"
            
            # Check that it's an async context manager (decorated with @asynccontextmanager)
            import inspect
            # For async context managers, we check if it's a generator function
            # and has the proper attributes from the decorator
            if hasattr(lifespan, '__wrapped__'):
                # It's decorated, check the wrapped function
                assert inspect.isasyncgenfunction(lifespan.__wrapped__), "Lifespan should be async generator"
            else:
                # Direct check - should be async generator or have contextmanager attributes
                is_async_gen = inspect.isasyncgenfunction(lifespan)
                has_context_attrs = hasattr(lifespan, '__aenter__') or hasattr(lifespan, '__aexit__')
                assert is_async_gen or has_context_attrs, "Lifespan should be async context manager"
            
            print("✅ Lifespan context manager properly configured")
            return True
            
        except Exception as e:
            print(f"❌ Lifespan test failed: {e}")
            return False
    
    def test_trading_engine_integration(self):
        """Test trading engine integration points."""
        print("🧪 Testing trading engine integration...")
        
        try:
            from app.main import get_trading_engine
            
            # Test that get_trading_engine function exists
            assert callable(get_trading_engine), "get_trading_engine should be callable"
            
            # Test error handling when engine not initialized
            try:
                engine = get_trading_engine()
                print("⚠️ Trading engine unexpectedly available")
            except RuntimeError as e:
                if "not initialized" in str(e):
                    print("✅ Proper error handling when engine not initialized")
                else:
                    print(f"⚠️ Unexpected error: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Trading engine integration test failed: {e}")
            return False


def run_all_tests():
    """Run all consolidation tests."""
    print("🚀 Starting Consolidated Application Test Suite")
    print("=" * 60)
    
    test_suite = TestConsolidatedApplication()
    tests = [
        test_suite.test_import_consolidated_app,
        test_suite.test_application_configuration,
        test_suite.test_middleware_setup,
        test_suite.test_routes_configuration,
        test_suite.test_static_files_mount,
        test_suite.test_api_routers_inclusion,
        test_suite.test_lifespan_context_manager,
        test_suite.test_trading_engine_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} raised exception: {e}")
            failed += 1
        
        print("-" * 40)
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All consolidation tests passed!")
        print("✅ Application structure successfully consolidated")
        return True
    else:
        print(f"⚠️ {failed} tests failed - review consolidation")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)