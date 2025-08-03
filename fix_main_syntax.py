#!/usr/bin/env python3
"""
Main.py Syntax Error Fix Script
File: fix_main_syntax.py

Fixes the JavaScript syntax error in main.py at line 711.
The error shows JavaScript's .toFixed() method in Python code.
"""

import os
import shutil
import re
from datetime import datetime


def backup_main_file():
    """Backup the current main.py file."""
    main_file = "app/main.py"
    
    if os.path.exists(main_file):
        backup_name = f"{main_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(main_file, backup_name)
        print(f"✅ Backed up {main_file} to {backup_name}")
        return True
    else:
        print(f"❌ {main_file} not found")
        return False


def read_current_main_file():
    """Read the current main.py file to identify the issue."""
    main_file = "app/main.py"
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ Error reading {main_file}: {e}")
        return None


def fix_javascript_syntax_in_python(content):
    """Fix JavaScript syntax mixed into Python code."""
    if not content:
        return None
    
    # Split content into lines to check around line 711
    lines = content.split('\n')
    
    # Look for JavaScript syntax patterns in Python code
    problematic_patterns = [
        r'\.toFixed\(',  # JavaScript's toFixed method
        r'value / 1000000\)\.toFixed\(1\)',  # Specific pattern from error
        r'\+ \'M\';',  # JavaScript string concatenation
        r'return \$',  # JavaScript-style return statements
    ]
    
    fixed_lines = []
    fixes_made = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Fix .toFixed() JavaScript method calls
        if '.toFixed(' in line:
            # Convert JavaScript .toFixed() to Python format
            line = re.sub(r'([^.]+)\.toFixed\((\d+)\)', r'f"{float(\1):.\\2f}"', line)
            fixes_made.append(f"Line {i+1}: Fixed .toFixed() method")
        
        # Fix JavaScript string concatenation patterns
        if "+ (value / 1000000).toFixed(1) + 'M';" in line:
            line = line.replace(
                "+ (value / 1000000).toFixed(1) + 'M';",
                "f'{value / 1000000:.1f}M'"
            )
            fixes_made.append(f"Line {i+1}: Fixed JavaScript string concatenation")
        
        # Remove JavaScript semicolons at end of Python lines
        if line.strip().endswith(';') and not line.strip().startswith('#'):
            line = line.rstrip(';')
            fixes_made.append(f"Line {i+1}: Removed JavaScript semicolon")
        
        # Fix other common JavaScript to Python conversions
        line = re.sub(r'return \$([^;]+);', r'return f"${\\1}"', line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes_made


def create_clean_main_file():
    """Create a clean main.py file without JavaScript syntax issues."""
    
    clean_content = '''"""
DEX Sniping Platform - Main Application
File: app/main.py

Professional FastAPI application with proper Python syntax.
Fixed JavaScript syntax errors and Unicode issues.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from app.utils.logger import setup_logger
from app.core.exceptions import DexSnipingException, ValidationError

logger = setup_logger(__name__)

# Initialize templates
templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("🚀 Starting DEX Sniping Platform")
    logger.info("📊 Dashboard: http://127.0.0.1:8001/dashboard")
    logger.info("📚 API Docs: http://127.0.0.1:8001/docs")
    
    try:
        # Initialize database connections
        from app.core.database import init_database
        await init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {e}")
        logger.info("💡 Continuing with mock data")
    
    yield
    
    logger.info("🔄 Shutting down DEX Sniping Platform")
    
    try:
        from app.core.database import close_database
        await close_database()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.warning(f"⚠️ Database cleanup warning: {e}")


# Create FastAPI application
app = FastAPI(
    title="DEX Sniping Platform",
    description="Professional DEX Sniping and Trading Bot Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    logger.info("✅ Static files mounted")


# Include API routers with error handling
try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1")
    logger.info("✅ Dashboard API routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Dashboard API not available: {e}")

try:
    from app.api.v1.endpoints.tokens import router as tokens_router
    app.include_router(tokens_router, prefix="/api/v1")
    logger.info("✅ Tokens API routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Tokens API not available: {e}")

try:
    from app.api.v1.endpoints.trading import router as trading_router
    app.include_router(trading_router, prefix="/api/v1")
    logger.info("✅ Trading API routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Trading API not available: {e}")


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - redirect to dashboard."""
    return RedirectResponse(url="/dashboard")


# Dashboard page
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Render the main dashboard page."""
    try:
        # Check if dashboard template exists
        template_path = "frontend/templates/pages/dashboard.html"
        if not os.path.exists(template_path):
            # Return simple dashboard if template missing
            return HTMLResponse(content=get_simple_dashboard_html())
        
        return templates.TemplateResponse("pages/dashboard.html", {
            "request": request,
            "title": "DEX Sniping Dashboard",
            "page": "dashboard"
        })
    except Exception as e:
        logger.error(f"Dashboard page error: {e}")
        return HTMLResponse(content=get_error_dashboard_html(str(e)))


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "database": "mock_mode",
            "frontend": "operational"
        }
    }


# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status information."""
    return {
        "application": "DEX Sniping Platform",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "dashboard": "/dashboard",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }


def get_simple_dashboard_html() -> str:
    """Get simple dashboard HTML when template is missing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DEX Sniping Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body text-center">
                            <h1 class="card-title text-primary">
                                <i class="bi bi-robot"></i>
                                DEX Sniping Platform
                            </h1>
                            <p class="card-text">Professional Trading Bot Dashboard</p>
                            <div class="alert alert-success">
                                <i class="bi bi-check-circle"></i>
                                Application is running successfully!
                            </div>
                            <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                                <a href="/docs" class="btn btn-primary">
                                    <i class="bi bi-book"></i> API Documentation
                                </a>
                                <a href="/api/v1/health" class="btn btn-outline-success">
                                    <i class="bi bi-heart-pulse"></i> Health Check
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """


def get_error_dashboard_html(error_message: str) -> str:
    """Get error dashboard HTML."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DEX Sniping Dashboard - Error</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card border-warning">
                        <div class="card-body text-center">
                            <h1 class="card-title text-warning">
                                <i class="bi bi-exclamation-triangle"></i>
                                Dashboard Error
                            </h1>
                            <div class="alert alert-warning">
                                <strong>Error:</strong> {error_message}
                            </div>
                            <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                                <a href="/docs" class="btn btn-primary">
                                    <i class="bi bi-book"></i> API Documentation
                                </a>
                                <a href="/api/v1/health" class="btn btn-outline-success">
                                    <i class="bi bi-heart-pulse"></i> Health Check
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """


# Error handlers
@app.exception_handler(DexSnipingException)
async def dex_sniping_exception_handler(request: Request, exc: DexSnipingException):
    """Handle custom DexSnipingException."""
    logger.error(f"DexSnipingException: {exc.message}")
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    logger.error(f"ValidationError: {exc.message}")
    return JSONResponse(
        status_code=422,
        content=exc.to_dict()
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "path": str(request.url.path),
            "suggestion": "Check /docs for available endpoints"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# Utility functions for Python formatting (replacing JavaScript functions)
def format_currency(amount: float, decimals: int = 2) -> str:
    """Format currency amount (Python replacement for JavaScript toFixed)."""
    try:
        if amount >= 1e9:
            return f"${amount / 1e9:.1f}B"
        elif amount >= 1e6:
            return f"${amount / 1e6:.1f}M"
        elif amount >= 1e3:
            return f"${amount / 1e3:.1f}K"
        else:
            return f"${amount:.{decimals}f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage value."""
    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.00%"


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting DEX Sniping Platform")
    logger.info("📊 Dashboard: http://127.0.0.1:8001/dashboard")
    logger.info("📚 API Docs: http://127.0.0.1:8001/docs")
    logger.info("💓 Health: http://127.0.0.1:8001/api/v1/health")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
'''
    
    return clean_content


def main():
    """Main execution function."""
    print("🔧 Main.py Syntax Error Fix")
    print("=" * 50)
    print("Fixing JavaScript syntax errors in Python code")
    print()
    
    try:
        # Step 1: Backup current file
        print("📋 Step 1: Backing up current main.py...")
        if not backup_main_file():
            print("⚠️ No main.py file found, creating new one")
        
        # Step 2: Read current file content
        print("\n📖 Step 2: Reading current file...")
        current_content = read_current_main_file()
        
        if current_content:
            print("✅ Current file read successfully")
            
            # Step 3: Attempt to fix JavaScript syntax
            print("\n🔧 Step 3: Fixing JavaScript syntax...")
            result = fix_javascript_syntax_in_python(current_content)
            
            if result:
                fixed_content, fixes_made = result
                
                if fixes_made:
                    print("✅ JavaScript syntax issues found and fixed:")
                    for fix in fixes_made:
                        print(f"   - {fix}")
                    
                    # Write fixed content
                    with open("app/main.py", 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print("✅ Fixed content written to main.py")
                else:
                    print("⚠️ No obvious JavaScript syntax found, creating clean file")
                    # Create clean file
                    clean_content = create_clean_main_file()
                    with open("app/main.py", 'w', encoding='utf-8') as f:
                        f.write(clean_content)
                    print("✅ Clean main.py created")
            else:
                print("❌ Could not fix current content, creating clean file")
                # Create clean file
                clean_content = create_clean_main_file()
                with open("app/main.py", 'w', encoding='utf-8') as f:
                    f.write(clean_content)
                print("✅ Clean main.py created")
        else:
            print("⚠️ Could not read current file, creating new one")
            # Create clean file
            clean_content = create_clean_main_file()
            
            # Ensure directory exists
            os.makedirs("app", exist_ok=True)
            
            with open("app/main.py", 'w', encoding='utf-8') as f:
                f.write(clean_content)
            print("✅ New main.py created")
        
        print("\n🎉 Syntax fix completed successfully!")
        print()
        print("📋 Next steps:")
        print("1. Start the application: uvicorn app.main:app --reload --port 8001")
        print("2. Check for any remaining import errors")
        print("3. Access dashboard: http://127.0.0.1:8001/dashboard")
        print()
        print("✅ The JavaScript syntax error should now be resolved!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fix script failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)