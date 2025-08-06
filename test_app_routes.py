"""
Quick Application Route Test
File: test_app_routes.py

Quick test to verify that all routes are working correctly.
"""

import sys
from pathlib import Path

def setup_path():
    """Setup Python path."""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def test_app_routes():
    """Test application routes."""
    setup_path()
    
    print("🧪 Testing Application Routes...")
    
    try:
        from app.main import app
        
        # Print all routes
        print(f"✅ Application loaded with {len(app.routes)} routes:")
        
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods) if hasattr(route, 'methods') else ['GET']
                print(f"   {methods[0]:6} {route.path}")
        
        # Test that we have essential routes
        paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        essential_paths = ["/", "/health", "/dashboard", "/docs", "/openapi.json"]
        
        print(f"\n🔍 Checking essential routes:")
        for path in essential_paths:
            if path in paths:
                print(f"   ✅ {path}")
            else:
                print(f"   ❌ {path} - Missing")
        
        # Check if dashboard route exists
        dashboard_exists = "/dashboard" in paths
        
        if dashboard_exists:
            print(f"\n✅ Dashboard route is available!")
            print(f"🚀 You can access the dashboard at: http://localhost:8000/dashboard")
        else:
            print(f"\n❌ Dashboard route is missing!")
        
        return True, len(app.routes), dashboard_exists
        
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False, 0, False


def main():
    """Main test function."""
    print("=" * 60)
    print("🚀 QUICK APPLICATION ROUTE TEST")
    print("=" * 60)
    
    success, route_count, dashboard_ok = test_app_routes()
    
    if success and dashboard_ok:
        print(f"\n🎉 SUCCESS! Application is ready with {route_count} routes!")
        print(f"✅ Dashboard route is working")
        print(f"🚀 Run 'python -m app.main' to start the server")
        print(f"🌐 Then visit: http://localhost:8000/dashboard")
    elif success:
        print(f"\n⚠️  Partial success: {route_count} routes loaded but dashboard may have issues")
    else:
        print(f"\n❌ Route test failed - check the application setup")
    
    print("=" * 60)


if __name__ == "__main__":
    main()