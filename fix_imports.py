"""
Fix Import Issues in main.py
File: fix_imports.py

Fix the HTMLResponse import error and router definition issue.
"""

import os
from pathlib import Path
import shutil
from datetime import datetime


def fix_main_imports():
    """
    Fix missing imports in main.py.
    """
    print("\n🔧 Fixing Imports in main.py...")
    print("=" * 60)
    
    main_path = Path("app/main.py")
    
    if not main_path.exists():
        print("❌ main.py not found!")
        return False
    
    # Backup
    backup_path = main_path.with_suffix('.py.imports_backup')
    shutil.copy2(main_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")
    
    with open(main_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check if HTMLResponse is imported
    has_html_response = False
    has_request = False
    import_line = -1
    
    for i, line in enumerate(lines):
        if 'from fastapi' in line and 'import' in line:
            import_line = i
            if 'HTMLResponse' in line:
                has_html_response = True
            if 'Request' in line:
                has_request = True
        elif 'from fastapi.responses import' in line:
            import_line = i
            if 'HTMLResponse' in line:
                has_html_response = True
    
    # Add missing imports
    if not has_html_response:
        print("Adding HTMLResponse import...")
        
        if import_line >= 0:
            # Add to existing import
            if 'from fastapi.responses import' in lines[import_line]:
                lines[import_line] = lines[import_line].rstrip() + ', HTMLResponse\n'
            else:
                # Add new import line after the fastapi import
                lines.insert(import_line + 1, 'from fastapi.responses import HTMLResponse\n')
        else:
            # Add at the top after initial imports
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and not line.startswith('"""'):
                    lines.insert(i, 'from fastapi.responses import HTMLResponse\n')
                    lines.insert(i + 1, 'from fastapi import Request\n')
                    break
        
        print("✅ Added HTMLResponse import")
    
    # Fix the failsafe route at the end if it exists
    for i, line in enumerate(lines):
        if '@app.get("/dashboard-fixed"' in line:
            # Make sure Request is imported in this context
            if i > 0 and 'from fastapi import Request' not in ''.join(lines[max(0, i-10):i]):
                lines.insert(i, 'from fastapi import Request\n')
                print("✅ Added Request import for failsafe route")
            break
    
    # Write the fixed file
    with open(main_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Fixed imports in main.py")
    return True


def fix_route_manager_imports():
    """
    Fix the 'router' is not defined error in route_manager.py.
    """
    print("\n🔧 Fixing route_manager.py...")
    print("=" * 60)
    
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ route_manager.py not found!")
        return False
    
    with open(route_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check the error context
    if "'router' is not defined" in str(content) or "router" in content:
        print("Analyzing router usage...")
        
        # The issue is likely in the frontend routes setup
        # The router variable needs to be defined in the method context
        
        lines = content.split('\n')
        
        # Find the _setup_frontend_routes method
        for i, line in enumerate(lines):
            if 'def _setup_frontend_routes' in line or 'def setup_frontend_routes' in line:
                print(f"Found frontend routes method at line {i+1}")
                
                # Check if router is defined in this method
                method_start = i
                method_end = len(lines)
                
                # Find method end
                for j in range(i + 1, len(lines)):
                    if lines[j] and not lines[j].startswith(' '):
                        method_end = j
                        break
                
                # Check if router is defined
                has_router_def = False
                for j in range(method_start, min(method_end, method_start + 20)):
                    if 'router = APIRouter' in lines[j] or 'router = ' in lines[j]:
                        has_router_def = True
                        print(f"Router defined at line {j+1}")
                        break
                
                if not has_router_def:
                    print("Router not defined in method, fixing...")
                    
                    # Add router definition at the beginning of the method
                    indent = '        '  # Assuming method indent
                    insertion_point = method_start + 1
                    
                    # Skip docstring if present
                    if '"""' in lines[insertion_point]:
                        for j in range(insertion_point + 1, method_end):
                            if '"""' in lines[j]:
                                insertion_point = j + 1
                                break
                    
                    lines.insert(insertion_point, f'{indent}from fastapi import APIRouter\n')
                    lines.insert(insertion_point + 1, f'{indent}router = APIRouter()\n')
                    lines.insert(insertion_point + 2, f'{indent}\n')
                    
                    print("✅ Added router definition")
                    
                    # Make sure the method returns the router
                    for j in range(method_start, method_end):
                        if 'return router' in lines[j]:
                            break
                    else:
                        # Add return statement
                        lines.insert(method_end - 1, f'{indent}return router\n')
                        print("✅ Added return statement")
                    
                    # Write the fixed content
                    with open(route_manager_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    print("✅ Fixed route_manager.py")
                    return True
    
    print("Router issue might be elsewhere or already fixed")
    return True


def test_server_startup():
    """
    Test if the server can start now.
    """
    print("\n🧪 Testing Server Startup...")
    print("=" * 60)
    
    try:
        # Import the main app
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        # Clear any cached imports
        if 'app.main' in sys.modules:
            del sys.modules['app.main']
        
        import app.main
        
        print("✅ Main module imports successfully!")
        
        # Check if app exists
        if hasattr(app.main, 'app'):
            print("✅ FastAPI app object found!")
            
            # Check for dashboard route
            routes = []
            for route in app.main.app.routes:
                if hasattr(route, 'path'):
                    routes.append(route.path)
                    if route.path == '/dashboard':
                        print(f"✅ Dashboard route found: {route.path}")
            
            print(f"Total routes: {len(routes)}")
            return True
        else:
            print("❌ App object not found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """
    Main fix function.
    """
    print("🚀 DEX Sniper Pro - Fix Import Issues")
    print("=" * 60)
    
    # Fix main.py imports
    fix_main_imports()
    
    # Fix route_manager.py
    fix_route_manager_imports()
    
    # Test the fixes
    if test_server_startup():
        print("\n" + "=" * 60)
        print("✅ All issues fixed!")
        print("\n📝 Start your server now:")
        print("   uvicorn app.main:app --reload")
        print("\nThen navigate to:")
        print("   http://127.0.0.1:8000/dashboard")
        print("\nYou should see your professional dashboard with sidebar!")
    else:
        print("\n⚠️ Some issues may remain")
        print("Try starting the server anyway:")
        print("   uvicorn app.main:app --reload")
        print("\nIf it fails, share the error message.")


if __name__ == "__main__":
    main()