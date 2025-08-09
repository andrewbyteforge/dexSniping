"""
Fix Server Binding and Dashboard Route
File: fix_server_binding.py

Ensures the server binds correctly and dashboard route exists.
"""

from pathlib import Path
import shutil
from datetime import datetime


def add_dashboard_route_to_factory():
    """
    Add the dashboard route directly to factory.py.
    """
    print("\n🔧 Adding Dashboard Route to factory.py...")
    print("=" * 60)
    
    factory_path = Path("app/factory.py")
    
    if not factory_path.exists():
        print("❌ factory.py not found!")
        return False
    
    # Backup
    backup_path = factory_path.with_suffix('.py.dashboard_backup')
    shutil.copy2(factory_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")
    
    with open(factory_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if dashboard route already exists
    if '@app.get("/dashboard")' in content:
        print("⚠️ Dashboard route already exists in factory.py")
        return True
    
    # Find where to add the route (after essential routes setup)
    lines = content.split('\n')
    insertion_point = -1
    
    # Look for the _setup_essential_routes function
    for i, line in enumerate(lines):
        if 'def _setup_essential_routes' in line:
            # Find the end of this function
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' '):
                    insertion_point = j
                    break
            break
    
    if insertion_point == -1:
        # Alternative: Add before the return statement
        for i, line in enumerate(lines):
            if 'return app' in line and 'def create_app' in '\n'.join(lines[:i]):
                insertion_point = i
                break
    
    if insertion_point > 0:
        # Add the dashboard route
        dashboard_route_code = '''
    # Dashboard route with proper template
    @app.get("/dashboard", response_class=HTMLResponse)
    async def serve_dashboard(request: Request) -> HTMLResponse:
        """Serve the professional dashboard with sidebar."""
        from fastapi.templating import Jinja2Templates
        from fastapi.responses import HTMLResponse
        from fastapi import Request
        
        templates = Jinja2Templates(directory="frontend/templates")
        try:
            # Serve the dashboard that extends from layout.html (has sidebar)
            return templates.TemplateResponse(
                "pages/dashboard.html",
                {"request": request}
            )
        except Exception as e:
            logger.error(f"Dashboard template error: {e}")
            # Return simple error page
            return HTMLResponse(f"""
            <html>
            <head><title>Dashboard Error</title></head>
            <body style="padding: 50px;">
                <h1>Dashboard Template Error</h1>
                <p>Error: {e}</p>
                <p>Please ensure frontend/templates/pages/dashboard.html exists</p>
            </body>
            </html>
            """)
    
    # Root redirect to dashboard
    @app.get("/", response_class=HTMLResponse)
    async def root_to_dashboard(request: Request) -> HTMLResponse:
        """Redirect root to dashboard."""
        return await serve_dashboard(request)
'''
        
        lines.insert(insertion_point, dashboard_route_code)
        print(f"✅ Added dashboard route at line {insertion_point}")
        
        # Write back
        with open(factory_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    print("❌ Could not find insertion point")
    return False


def fix_main_server_binding():
    """
    Ensure main.py runs the server with correct binding.
    """
    print("\n🔧 Checking Server Binding in main.py...")
    print("=" * 60)
    
    main_path = Path("app/main.py")
    
    if not main_path.exists():
        print("❌ main.py not found!")
        return False
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if __main__ block exists
    if 'if __name__ == "__main__":' not in content:
        print("Adding __main__ block for direct running...")
        
        # Add at the end
        main_block = '''

# Allow running directly
if __name__ == "__main__":
    import uvicorn
    print("Starting DEX Sniper Pro server...")
    print("Dashboard will be available at: http://127.0.0.1:8000/dashboard")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
'''
        
        content += main_block
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added __main__ block for direct running")
    else:
        print("✅ __main__ block already exists")
    
    return True


def create_simple_test_server():
    """
    Create a simple test server to verify connectivity.
    """
    print("\n🔧 Creating Simple Test Server...")
    print("=" * 60)
    
    test_server_content = '''"""
Simple Test Server
File: test_server.py

A minimal server to test if we can serve the dashboard.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Dashboard Test")

# Mount static files
if Path("frontend/static").exists():
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple root endpoint."""
    return HTMLResponse("""
    <html>
    <body style="padding: 50px; font-family: Arial;">
        <h1>Test Server Running!</h1>
        <p>Server is accessible at http://127.0.0.1:8000</p>
        <p><a href="/dashboard">Go to Dashboard</a></p>
    </body>
    </html>
    """)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard with sidebar."""
    try:
        return templates.TemplateResponse(
            "pages/dashboard.html",
            {"request": request}
        )
    except Exception as e:
        return HTMLResponse(f"""
        <html>
        <body style="padding: 50px;">
            <h1>Dashboard Error</h1>
            <p>Error: {e}</p>
            <p>Template path: frontend/templates/pages/dashboard.html</p>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    print("Starting test server...")
    print("Dashboard: http://127.0.0.1:8000/dashboard")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
'''
    
    test_path = Path("test_server.py")
    test_path.write_text(test_server_content, encoding='utf-8')
    print(f"✅ Created {test_path}")
    
    return True


def main():
    """
    Main function.
    """
    print("🚀 DEX Sniper Pro - Fix Server and Dashboard")
    print("=" * 60)
    
    # Add dashboard route to factory
    add_dashboard_route_to_factory()
    
    # Fix main.py binding
    fix_main_server_binding()
    
    # Create test server
    create_simple_test_server()
    
    print("\n" + "=" * 60)
    print("✅ Fixes applied!")
    print("\n📝 Try these options:")
    print("\n1. RESTART your main server:")
    print("   Stop it (Ctrl+C) and start again:")
    print("   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
    print("\n2. OR try the test server:")
    print("   python test_server.py")
    print("\n3. Then open in your browser:")
    print("   http://127.0.0.1:8000/dashboard")
    print("\n4. If you see 'This site can't be reached':")
    print("   - Check Windows Firewall")
    print("   - Try: http://localhost:8000/dashboard")
    print("   - Try a different port: --port 8080")


if __name__ == "__main__":
    main()