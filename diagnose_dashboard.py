"""
Dashboard Diagnostic Script
File: diagnose_dashboard.py

Diagnoses why the professional dashboard is not displaying and provides fixes.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def check_template_structure() -> Dict[str, bool]:
    """
    Check if the template directory structure is correct.
    
    Returns:
        Dict[str, bool]: Status of each template component
    """
    print("\n📁 Checking Template Structure...")
    print("=" * 50)
    
    checks = {
        "frontend_dir": Path("frontend").exists(),
        "templates_dir": Path("frontend/templates").exists(),
        "pages_dir": Path("frontend/templates/pages").exists(),
        "base_dir": Path("frontend/templates/base").exists(),
        "dashboard_html": Path("frontend/templates/pages/dashboard.html").exists(),
        "dashboard_backup": Path("frontend/templates/pages/dashboard.html.backup").exists(),
        "base_html": Path("frontend/templates/base.html").exists(),
        "static_dir": Path("frontend/static").exists(),
        "css_dir": Path("frontend/static/css").exists(),
        "js_dir": Path("frontend/static/js").exists(),
        "main_css": Path("frontend/static/css/main.css").exists()
    }
    
    for name, exists in checks.items():
        status = "✅" if exists else "❌"
        print(f"{status} {name.replace('_', ' ').title()}: {exists}")
    
    return checks


def check_route_files() -> Dict[str, bool]:
    """
    Check if route configuration files exist.
    
    Returns:
        Dict[str, bool]: Status of route files
    """
    print("\n🛣️  Checking Route Files...")
    print("=" * 50)
    
    checks = {
        "main_py": Path("app/main.py").exists(),
        "server_routes": Path("app/server/routes.py").exists(),
        "dashboard_api": Path("app/api/v1/endpoints/dashboard.py").exists(),
        "init_files": all([
            Path("app/__init__.py").exists(),
            Path("app/api/__init__.py").exists(),
            Path("app/api/v1/__init__.py").exists(),
            Path("app/api/v1/endpoints/__init__.py").exists()
        ])
    }
    
    for name, exists in checks.items():
        status = "✅" if exists else "❌"
        print(f"{status} {name.replace('_', ' ').title()}: {exists}")
    
    return checks


def verify_dashboard_content() -> Tuple[bool, str]:
    """
    Verify the dashboard.html content is the professional version.
    
    Returns:
        Tuple[bool, str]: (Is professional version, description)
    """
    print("\n📄 Checking Dashboard Content...")
    print("=" * 50)
    
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        return False, "File not found"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for professional dashboard markers
        markers = {
            "extends base": '{% extends "base' in content,
            "bootstrap": 'bootstrap' in content.lower(),
            "chart.js": 'chart' in content.lower(),
            "dashboard stats": 'dashboard-stats' in content or 'portfolioValue' in content,
            "live tokens": 'live-tokens' in content or 'tokensContainer' in content,
            "professional layout": 'col-lg' in content or 'card' in content,
            "javascript functions": 'loadDashboardStats' in content or 'displayTokens' in content
        }
        
        professional_count = sum(markers.values())
        
        for name, found in markers.items():
            status = "✅" if found else "❌"
            print(f"{status} {name.replace('_', ' ').title()}: {found}")
        
        print(f"\n📊 Professional markers found: {professional_count}/7")
        
        if professional_count >= 5:
            return True, "Professional dashboard detected"
        elif professional_count >= 3:
            return False, "Partial professional dashboard"
        else:
            return False, "Basic or missing dashboard"
            
    except Exception as e:
        print(f"❌ Error reading dashboard: {e}")
        return False, f"Error: {e}"


def check_imports() -> bool:
    """
    Check if all necessary imports work.
    
    Returns:
        bool: True if imports work
    """
    print("\n📦 Checking Python Imports...")
    print("=" * 50)
    
    imports_status = {}
    
    # Test FastAPI imports
    try:
        from fastapi import FastAPI
        from fastapi.templating import Jinja2Templates
        imports_status["FastAPI"] = True
    except ImportError as e:
        imports_status["FastAPI"] = False
        print(f"❌ FastAPI import failed: {e}")
    
    # Test app imports
    try:
        sys.path.insert(0, str(Path.cwd()))
        from app.main import app
        imports_status["Main App"] = True
    except ImportError as e:
        imports_status["Main App"] = False
        print(f"❌ Main app import failed: {e}")
    
    # Test route imports
    try:
        from app.server.routes import setup_routes
        imports_status["Routes"] = True
    except ImportError as e:
        imports_status["Routes"] = False
        print(f"❌ Routes import failed: {e}")
    
    for name, success in imports_status.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}: {'Working' if success else 'Failed'}")
    
    return all(imports_status.values())


def suggest_fixes(checks: Dict[str, Dict[str, bool]]) -> List[str]:
    """
    Suggest fixes based on diagnostic results.
    
    Args:
        checks: Dictionary of check results
        
    Returns:
        List[str]: List of suggested fixes
    """
    fixes = []
    
    # Template fixes
    if not checks['templates']['dashboard_html']:
        if checks['templates']['dashboard_backup']:
            fixes.append("Restore dashboard from backup: cp frontend/templates/pages/dashboard.html.backup frontend/templates/pages/dashboard.html")
        else:
            fixes.append("Dashboard template missing - need to recreate it")
    
    if not checks['templates']['templates_dir']:
        fixes.append("Create templates directory: mkdir -p frontend/templates/pages")
    
    # Route fixes
    if not checks['routes']['server_routes']:
        fixes.append("Create routes file: Copy the fixed routes.py from the artifact above")
    
    # Static files fixes
    if not checks['templates']['static_dir']:
        fixes.append("Create static directory: mkdir -p frontend/static/css frontend/static/js")
    
    return fixes


def main():
    """
    Main diagnostic function.
    """
    print("🔍 DEX Sniper Pro - Dashboard Diagnostic Tool")
    print("=" * 60)
    
    all_checks = {}
    
    # Run all checks
    all_checks['templates'] = check_template_structure()
    all_checks['routes'] = check_route_files()
    
    # Check dashboard content
    is_professional, dashboard_status = verify_dashboard_content()
    
    # Check imports
    imports_ok = check_imports()
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    # Overall status
    template_ok = all_checks['templates']['dashboard_html']
    routes_ok = all_checks['routes']['server_routes']
    
    if template_ok and routes_ok and is_professional and imports_ok:
        print("✅ DASHBOARD SHOULD BE WORKING!")
        print("\nIf still not displaying, check:")
        print("1. Server is running: uvicorn app.main:app --reload")
        print("2. Correct URL: http://127.0.0.1:8000/dashboard")
        print("3. Browser cache: Clear cache or try incognito mode")
        print("4. Console errors: Open browser DevTools and check console")
    else:
        print("❌ ISSUES FOUND - Dashboard may not display correctly")
        
        # Suggest fixes
        fixes = suggest_fixes(all_checks)
        if fixes:
            print("\n🔧 SUGGESTED FIXES:")
            for i, fix in enumerate(fixes, 1):
                print(f"{i}. {fix}")
        
        print("\n📝 QUICK FIX STEPS:")
        print("1. Copy the fixed routes.py from the artifact above to app/server/routes.py")
        print("2. Ensure dashboard.html exists at frontend/templates/pages/dashboard.html")
        print("3. Restart the server: uvicorn app.main:app --reload")
        print("4. Navigate to: http://127.0.0.1:8000/dashboard")
    
    # Template status
    print(f"\n📄 Dashboard Template Status: {dashboard_status}")
    
    return template_ok and routes_ok and is_professional


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)