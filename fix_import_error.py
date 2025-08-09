"""
Fix Import Error in main.py
File: fix_import_error.py

Fixes the incorrect import statement causing the server startup failure.
"""

import os
from pathlib import Path


def fix_main_imports():
    """Fix the incorrect import statements in main.py"""
    
    main_file = Path("app/main.py")
    
    if not main_file.exists():
        print("❌ app/main.py not found!")
        return False
    
    try:
        # Read current content
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔧 Fixing import statements...")
        
        # Fix incorrect imports
        incorrect_imports = [
            "from fastapi.staticfiles import StaticFiles, Request",
            "from fastapi import Request\nfrom fastapi.responses import HTMLResponse\nfrom fastapi import FastAPI",
            "from fastapi import FastAPI, Request\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.responses import HTMLResponse\nfrom fastapi.staticfiles import StaticFiles"
        ]
        
        # Remove incorrect imports
        for incorrect_import in incorrect_imports:
            content = content.replace(incorrect_import, "")
        
        # Add correct imports at the top
        correct_imports = """from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
"""
        
        # Remove any duplicate FastAPI imports
        content = content.replace("from fastapi import FastAPI\n", "")
        
        # Find where to insert imports (after any existing imports or at the top)
        lines = content.split('\n')
        insert_position = 0
        
        # Find the end of existing imports
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and '"""' in line.strip()[3:]:
                # Single line docstring
                insert_position = i + 1
                break
            elif line.strip().startswith('"""'):
                # Multi-line docstring start
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j]:
                        insert_position = j + 1
                        break
                break
            elif line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from'):
                insert_position = i
                break
        
        # Insert correct imports
        lines.insert(insert_position, correct_imports)
        content = '\n'.join(lines)
        
        # Clean up any duplicate blank lines
        content = '\n'.join(line for line in content.split('\n') if line.strip() or content.split('\n').index(line) == 0 or content.split('\n')[content.split('\n').index(line)-1].strip())
        
        # Write back the corrected content
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Import statements fixed successfully!")
        print("✅ Corrected imports:")
        print("   - from fastapi import FastAPI, Request")
        print("   - from fastapi.templating import Jinja2Templates") 
        print("   - from fastapi.responses import HTMLResponse")
        print("   - from fastapi.staticfiles import StaticFiles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing imports: {e}")
        return False


def verify_main_py():
    """Verify the main.py file has correct structure"""
    
    main_file = Path("app/main.py")
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n🔍 Verifying main.py structure...")
        
        # Check for required components
        checks = {
            "FastAPI import": "from fastapi import FastAPI" in content,
            "Request import": "Request" in content and "from fastapi import" in content,
            "HTMLResponse import": "HTMLResponse" in content,
            "Templates import": "Jinja2Templates" in content,
            "FastAPI app creation": "app = FastAPI" in content,
            "Dashboard route": "@app.get(\"/dashboard\")" in content or "dashboard" in content.lower()
        }
        
        all_good = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
            if not result:
                all_good = False
        
        if all_good:
            print("\n✅ main.py structure looks good!")
        else:
            print("\n⚠️ Some issues detected in main.py")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error verifying main.py: {e}")
        return False


def create_minimal_working_main():
    """Create a minimal working main.py if needed"""
    
    print("\n🔧 Creating minimal working main.py...")
    
    minimal_main_content = '''"""
DEX Sniper Pro - Main Application
File: app/main.py
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="DEX Sniper Pro",
    description="Professional DEX Trading Bot",
    version="1.0.0"
)

# Template configuration
templates = Jinja2Templates(directory="frontend/templates")

# Static files (if directory exists)
if Path("frontend/static").exists():
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include API routers
try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
    logger.info("[OK] Dashboard router included")
except Exception as e:
    logger.warning(f"[WARN] Dashboard router not available: {e}")

try:
    from app.api.v1.endpoints.trading import router as trading_router
    app.include_router(trading_router, prefix="/api/v1", tags=["trading"])
    logger.info("[OK] Trading router included")
except Exception as e:
    logger.warning(f"[WARN] Trading router not available: {e}")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the home page."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DEX Sniper Pro</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; }
            .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 DEX Sniper Pro</h1>
            <p>Professional Trading Bot Platform</p>
            <a href="/dashboard" class="btn">Open Dashboard</a>
            <a href="/api/docs" class="btn">API Documentation</a>
            <a href="/health" class="btn">Health Check</a>
        </div>
    </body>
    </html>
    """)


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the dashboard page."""
    try:
        return templates.TemplateResponse(
            "pages/dashboard.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Dashboard template error: {e}")
        # Fallback dashboard
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DEX Sniper Pro Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; }
                .header { background: #343a40; color: white; padding: 20px; text-align: center; }
                .container { padding: 40px; text-align: center; }
                .status { background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 DEX Sniper Pro Dashboard</h1>
            </div>
            <div class="container">
                <div class="status">
                    <h3>✅ System Operational</h3>
                    <p>Dashboard is running successfully!</p>
                </div>
                <a href="/api/v1/dashboard/stats" class="btn">Test API</a>
                <a href="/api/docs" class="btn">API Docs</a>
                <a href="/health" class="btn">Health Check</a>
            </div>
        </body>
        </html>
        """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "DEX Sniper Pro",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    try:
        main_file = Path("app/main.py")
        
        # Backup existing file
        if main_file.exists():
            backup_file = Path("app/main.py.backup")
            with open(main_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"✅ Backup created: {backup_file}")
        
        # Write minimal working version
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(minimal_main_content)
        
        print("✅ Minimal working main.py created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating minimal main.py: {e}")
        return False


def main():
    """Main execution function."""
    print("Fix Import Error in main.py")
    print("=" * 40)
    
    try:
        # Try to fix existing imports first
        if fix_main_imports():
            if verify_main_py():
                print("\n✅ main.py fixed successfully!")
                print("\nNext steps:")
                print("1. Restart server: uvicorn app.main:app --reload")
                print("2. Visit dashboard: http://127.0.0.1:8000/dashboard")
                return True
        
        print("\n⚠️ Creating minimal working version...")
        if create_minimal_working_main():
            print("\n✅ Minimal main.py created successfully!")
            print("\nNext steps:")
            print("1. Restart server: uvicorn app.main:app --reload")
            print("2. Visit dashboard: http://127.0.0.1:8000/dashboard")
            return True
        
        return False
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)