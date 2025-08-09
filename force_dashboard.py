"""
Force Correct Dashboard Display
File: force_dashboard.py

This will ensure your professional dashboard with sidebar is displayed.
"""

from pathlib import Path
import shutil
from datetime import datetime


def find_and_fix_dashboard_route():
    """
    Find where the dashboard route is defined and fix it.
    """
    print("\n🔍 Finding Dashboard Route Handler...")
    print("=" * 60)
    
    # Check multiple possible locations
    files_to_check = [
        "app/factory.py",
        "app/main.py",
        "app/api/route_manager.py"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"\n📄 Checking {file_path}...")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for dashboard route
            if '@app.get("/dashboard")' in content or 'def serve_dashboard' in content:
                print(f"✅ Found dashboard route in {file_path}")
                
                # Check what it's returning
                if 'System Status: Operational' in content:
                    print("❌ This file contains the fallback landing page")
                    fix_file(path)
                elif 'create_comprehensive_landing_page' in content:
                    print("❌ This file returns the landing page")
                    fix_file(path)
                elif 'pages/dashboard.html' in content:
                    print("✅ This file tries to use the correct template")
                    # But let's ensure it's working
                    ensure_template_works(path)


def fix_file(file_path: Path):
    """
    Fix a file that's returning the wrong dashboard.
    """
    print(f"\n🔧 Fixing {file_path}...")
    
    # Backup
    backup_path = file_path.with_suffix('.py.fallback_backup')
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and replace the dashboard route
    fixed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Found dashboard route decorator
        if '@app.get("/dashboard")' in line or '@router.get("/dashboard")' in line:
            print(f"Found dashboard route at line {i+1}")
            
            # Find the function body
            func_start = i + 1
            func_end = func_start
            
            # Find where the function ends
            for j in range(func_start + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' '):
                    func_end = j
                    break
            
            # Replace the entire function
            new_function = '''async def serve_dashboard(request: Request) -> HTMLResponse:
    """Serve the professional dashboard with sidebar."""
    from fastapi.templating import Jinja2Templates
    from fastapi.responses import HTMLResponse
    
    templates = Jinja2Templates(directory="frontend/templates")
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})
'''
            
            # Replace function body
            lines[func_start:func_end] = [new_function + '\n']
            fixed = True
            print(f"✅ Replaced dashboard function")
            break
        
        i += 1
    
    if fixed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Fixed {file_path}")
    else:
        print(f"⚠️ Could not find dashboard route to fix")


def ensure_template_works(file_path: Path):
    """
    Ensure the template rendering works correctly.
    """
    print(f"\n🔧 Ensuring Template Works in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace any complex error handling with simple template return
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'def serve_dashboard' in line or 'async def dashboard' in line:
            # Check if it has complex error handling
            func_body = '\n'.join(lines[i:i+30])
            
            if 'except' in func_body and 'HTMLResponse' in func_body:
                print("Found complex error handling, simplifying...")
                
                # Simplify the function
                simple_function = '''async def serve_dashboard(request: Request) -> HTMLResponse:
    """Serve the professional dashboard with sidebar."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="frontend/templates")
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})'''
                
                # Find function boundaries and replace
                func_start = i
                func_end = i + 1
                for j in range(i + 1, min(len(lines), i + 50)):
                    if lines[j].strip() and not lines[j].startswith(' '):
                        func_end = j
                        break
                
                lines[func_start:func_end] = simple_function.split('\n')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Simplified dashboard function")
                break


def verify_templates():
    """
    Verify the dashboard template is correct.
    """
    print("\n🔍 Verifying Dashboard Template...")
    print("=" * 60)
    
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard template missing!")
        create_dashboard_template()
    else:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it extends from layout
        if '{% extends "base/layout.html"' not in content:
            print("❌ Dashboard doesn't extend from layout.html (no sidebar)")
            
            # Fix it
            if '{% extends' in content:
                # Replace the extends
                content = content.replace(
                    '{% extends "base.html" %}',
                    '{% extends "base/layout.html" %}'
                )
                content = content.replace(
                    "{% extends 'base.html' %}",
                    '{% extends "base/layout.html" %}'
                )
            else:
                # Add extends at the beginning
                content = '{% extends "base/layout.html" %}\n\n' + content
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed dashboard to extend from layout.html")
        else:
            print("✅ Dashboard correctly extends from layout.html")


def create_dashboard_template():
    """
    Create a proper dashboard template if missing.
    """
    print("Creating dashboard template...")
    
    dashboard_content = '''{% extends "base/layout.html" %}

{% block title %}Trading Dashboard{% endblock %}

{% block page_title %}Professional Trading Dashboard{% endblock %}
{% block page_subtitle %}Real-time DEX monitoring and AI-powered analysis{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Stats Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body">
                    <h6 class="text-white-50">Portfolio Value</h6>
                    <h3 id="portfolioValue">$0.00</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body">
                    <h6 class="text-white-50">Daily P&L</h6>
                    <h3 id="dailyPnL">$0.00</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body">
                    <h6 class="text-white-50">Active Trades</h6>
                    <h3 id="activeTrades">0</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card stats-card">
                <div class="card-body">
                    <h6 class="text-white-50">Success Rate</h6>
                    <h3 id="successRate">0%</h3>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="row">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h5>Live Token Discovery</h5>
                </div>
                <div class="card-body" id="tokensContainer">
                    <p>Loading tokens...</p>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Alerts</h5>
                </div>
                <div class="card-body" id="alertsContainer">
                    <p>No recent alerts</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Load dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch('/api/v1/dashboard/stats');
        const data = await response.json();
        
        document.getElementById('portfolioValue').textContent = '$' + (data.portfolio_value || 0);
        document.getElementById('dailyPnL').textContent = '$' + (data.daily_pnl || 0);
        document.getElementById('activeTrades').textContent = data.trades_today || 0;
        document.getElementById('successRate').textContent = (data.success_rate || 0) + '%';
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load on page load
document.addEventListener('DOMContentLoaded', loadDashboardData);
</script>
{% endblock %}'''
    
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard_content, encoding='utf-8')
    
    print("✅ Created dashboard template")


def create_override_route():
    """
    Create an override file that forces the correct dashboard.
    """
    print("\n🔧 Creating Override Route...")
    print("=" * 60)
    
    override_content = '''"""
Dashboard Override
File: dashboard_override.py

Forces the correct dashboard to display.
"""

from pathlib import Path

def apply_override():
    """Apply the dashboard override to factory.py."""
    
    factory_path = Path("app/factory.py")
    if not factory_path.exists():
        print("Factory.py not found")
        return False
    
    with open(factory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import at the top if not present
    if 'from fastapi.templating import Jinja2Templates' not in content:
        content = 'from fastapi.templating import Jinja2Templates\\n' + content
    
    # Find _setup_essential_routes function
    if 'def _setup_essential_routes' in content:
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if 'def _setup_essential_routes' in line:
                # Add our override after the function definition
                override_code = """
    # OVERRIDE: Force correct dashboard
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard_override(request: Request):
        templates = Jinja2Templates(directory="frontend/templates")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
    
    @app.get("/", response_class=HTMLResponse)
    async def root_override(request: Request):
        templates = Jinja2Templates(directory="frontend/templates")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
"""
                lines.insert(i + 2, override_code)
                content = '\\n'.join(lines)
                break
    
    with open(factory_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Override applied!")
    return True

if __name__ == "__main__":
    apply_override()
'''
    
    override_path = Path("dashboard_override.py")
    override_path.write_text(override_content, encoding='utf-8')
    print(f"✅ Created {override_path}")


def main():
    """
    Main function.
    """
    print("🚀 DEX Sniper Pro - Force Correct Dashboard")
    print("=" * 60)
    
    # Find and fix dashboard routes
    find_and_fix_dashboard_route()
    
    # Verify templates
    verify_templates()
    
    # Create override
    create_override_route()
    
    print("\n" + "=" * 60)
    print("✅ Dashboard fixes applied!")
    print("\n📝 Next Steps:")
    print("1. RESTART your server (Ctrl+C and start again)")
    print("   uvicorn app.main:app --reload")
    print("\n2. Clear your browser cache (Ctrl+F5)")
    print("\n3. Navigate to:")
    print("   http://127.0.0.1:8000/dashboard")
    print("\nYou should now see your professional dashboard with:")
    print("- Purple gradient sidebar on the left")
    print("- Navigation items (Dashboard, Token Discovery, etc.)")
    print("- Stats cards in the main area")
    print("\nIf still showing fallback, run:")
    print("   python dashboard_override.py")
    print("   Then restart the server again")


if __name__ == "__main__":
    main()