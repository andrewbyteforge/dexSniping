"""
Fix API Endpoints Script
File: fix_api_endpoints.py

Creates missing __init__.py files and tests API endpoint loading.
Run this from the project root directory.
"""

import os
from pathlib import Path

def create_init_files():
    """Create missing __init__.py files."""
    print("🔧 Creating missing __init__.py files...")
    
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py", 
        "app/api/v1/__init__.py",
        "app/api/v1/endpoints/__init__.py",
        "app/core/__init__.py",
        "app/core/blockchain/__init__.py", 
        "app/core/wallet/__init__.py",
        "app/utils/__init__.py"
    ]
    
    created_files = []
    existing_files = []
    
    for init_file in init_files:
        init_path = Path(init_file)
        
        if init_path.exists():
            existing_files.append(init_file)
            print(f"✅ {init_file} (already exists)")
        else:
            # Create directory if it doesn't exist
            init_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create the __init__.py file
            init_path.write_text(f'"""{"".join(init_file.split("/")[1:-1]).title()} package."""\n')
            created_files.append(init_file)
            print(f"✅ {init_file} (created)")
    
    print(f"\n📊 Init files: {len(existing_files)} existing, {len(created_files)} created")
    return len(created_files) > 0

def test_wallet_api_import():
    """Test that we can import the wallet API."""
    print("\n🧪 Testing wallet API import...")
    
    try:
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from app.api.v1.endpoints.wallet import router as wallet_router
        print("✅ Wallet API router import successful")
        
        # Check router details
        routes = wallet_router.routes
        print(f"✅ Found {len(routes)} wallet API routes")
        
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = getattr(route, 'methods', {'GET'})
                print(f"   📍 {list(methods)[0]:6} {route.path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Wallet API import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Wallet API test error: {e}")
        return False

def test_main_app_import():
    """Test that the main app can be imported."""
    print("\n🧪 Testing main application import...")
    
    try:
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        from app.main import app
        print("✅ Main application import successful")
        
        # Check if wallet routes are included
        wallet_routes = [route for route in app.routes if str(route.path).startswith("/api/v1/wallet")]
        print(f"✅ Found {len(wallet_routes)} wallet routes in main app")
        
        return True
        
    except ImportError as e:
        print(f"❌ Main application import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Main application test error: {e}")
        return False

def main():
    """Main fix function."""
    print("🔧 DEX Sniper Pro - API Endpoints Fix")
    print("=" * 50)
    
    # Check current directory
    if not Path("app").exists():
        print("❌ 'app' directory not found!")
        print("💡 Make sure you're running from the project root directory")
        return False
    
    # Create missing init files
    created_new_files = create_init_files()
    
    # Test imports
    wallet_import_success = test_wallet_api_import()
    main_app_success = test_main_app_import()
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 API Endpoints Fix Summary:")
    print("=" * 50)
    
    if created_new_files and wallet_import_success and main_app_success:
        print("✅ All fixes applied successfully!")
        print("🚀 API endpoints should now be available")
        print("\n💡 Next steps:")
        print("   1. Restart the server: uvicorn app.main:app --reload")
        print("   2. Check endpoints: curl http://127.0.0.1:8000/docs")
        print("   3. Test wallet API: curl http://127.0.0.1:8000/api/v1/wallet/health")
        return True
    elif wallet_import_success and main_app_success:
        print("✅ API endpoints are working (no fixes needed)")
        print("🔍 Check that the server is running the latest version")
        return True
    else:
        print("❌ Some issues remain:")
        if not wallet_import_success:
            print("   - Wallet API import failed")
        if not main_app_success:
            print("   - Main application import failed")
        print("🔧 Review the error messages above")
        return False

if __name__ == "__main__":
    """Run the fix."""
    try:
        success = main()
        if success:
            print("\n🎯 RESULT: API endpoints fix completed successfully!")
        else:
            print("\n🎯 RESULT: API endpoints fix needs attention")
    except Exception as e:
        print(f"\n💥 Fix script error: {e}")
        import traceback
        traceback.print_exc()