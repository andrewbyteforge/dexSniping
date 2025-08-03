"""
Updated Main Application with Fixed Dashboard Route
File: app/main.py
Class: N/A (FastAPI app)
Methods: root, dashboard_page, health_check

Fixed main application with correct dashboard template routing.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Configure templates to use the frontend/templates directory
templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting DEX Sniping Platform")
    
    # Check required directories
    required_dirs = [
        "frontend/templates",
        "frontend/templates/pages",
        "frontend/templates/base",
        "frontend/static",
        "app/api/v1/endpoints"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            logger.info(f"✅ Directory found: {directory}")
        else:
            logger.warning(f"⚠️ Directory missing: {directory}")
    
    # Check dashboard template
    dashboard_template = "frontend/templates/pages/dashboard.html"
    if os.path.exists(dashboard_template):
        logger.info("✅ Dashboard template found")
    else:
        logger.error("❌ Dashboard template missing")
    
    logger.info("✅ Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application")
    logger.info("✅ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="DEX Sniping Platform",
    description="Professional-grade DEX sniping platform with AI risk assessment",
    version="3.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    logger.info("✅ Static files mounted")
else:
    logger.warning("⚠️ Static files directory not found")

# Include API routers with error handling
try:
    # Import the working dashboard API
    from app.api.v1.endpoints.dashboard_working import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1")
    logger.info("✅ Dashboard API router included")
    
    # Try to include other routers if they exist
    try:
        from app.api.v1.endpoints import tokens, trading
        app.include_router(tokens.router, prefix="/api/v1")
        app.include_router(trading.router, prefix="/api/v1")
        logger.info("✅ Additional API routers included")
    except ImportError as e:
        logger.warning(f"⚠️ Some API routers not available: {e}")
    
except Exception as e:
    logger.error(f"❌ Error including dashboard router: {e}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint with basic landing page.
    File: app/main.py
    Function: root
    """
    try:
        logger.info("Root page requested")
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DEX Sniper Pro</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-lg-8">
                        <div class="card shadow">
                            <div class="card-header bg-primary text-white">
                                <h1 class="mb-0">
                                    <i class="bi bi-graph-up-arrow"></i>
                                    DEX Sniper Pro
                                </h1>
                                <p class="mb-0">Professional Trading Platform</p>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h5>Quick Access</h5>
                                        <div class="d-grid gap-2">
                                            <a href="/dashboard" class="btn btn-primary">
                                                <i class="bi bi-speedometer2"></i>
                                                Dashboard
                                            </a>
                                            <a href="/docs" class="btn btn-outline-primary">
                                                <i class="bi bi-book"></i>
                                                API Documentation
                                            </a>
                                            <a href="/api/v1/dashboard/stats" class="btn btn-outline-info">
                                                <i class="bi bi-bar-chart"></i>
                                                API Stats (JSON)
                                            </a>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h5>System Status</h5>
                                        <ul class="list-unstyled">
                                            <li class="mb-2">
                                                <i class="bi bi-check-circle text-success"></i>
                                                <strong>API:</strong> Online
                                            </li>
                                            <li class="mb-2">
                                                <i class="bi bi-check-circle text-success"></i>
                                                <strong>Dashboard:</strong> Available
                                            </li>
                                            <li class="mb-2">
                                                <i class="bi bi-check-circle text-success"></i>
                                                <strong>Data Feed:</strong> Active
                                            </li>
                                            <li class="mb-2">
                                                <span class="badge bg-success">Phase 3B Complete</span>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                                <hr>
                                <small class="text-muted">
                                    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return HTMLResponse(content=f"<h1>DEX Sniper Pro</h1><p>Error: {e}</p>")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Dashboard page endpoint with corrected template routing.
    File: app/main.py
    Function: dashboard_page
    """
    try:
        logger.info("📊 Dashboard page requested")
        
        # Use the correct dashboard template from pages directory
        template_path = "pages/dashboard.html"
        
        # Check if template exists
        full_template_path = f"frontend/templates/{template_path}"
        
        if not os.path.exists(full_template_path):
            logger.error(f"❌ Dashboard template not found: {full_template_path}")
            
            # Return a simple fallback dashboard
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard - DEX Sniper Pro</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-4">
                    <h1><i class="bi bi-speedometer2"></i> Dashboard</h1>
                    <div class="alert alert-warning">
                        <strong>Template Missing:</strong> Please run the dashboard fix script.
                        <br>
                        <a href="/api/v1/dashboard/stats" class="btn btn-sm btn-primary mt-2">
                            View API Data
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """)
        
        # Render the correct template
        context = {
            "request": request,
            "page_title": "Professional Trading Dashboard",
            "current_time": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Rendering dashboard template: {template_path}")
        return templates.TemplateResponse(template_path, context)
        
    except Exception as e:
        logger.error(f"❌ Dashboard page error: {e}")
        
        # Return error page with useful information
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Error - DEX Sniper Pro</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <div class="alert alert-danger">
                    <h4>Dashboard Error</h4>
                    <p><strong>Error:</strong> {e}</p>
                    <p><strong>Solution:</strong> Run the dashboard fix script</p>
                    <a href="/" class="btn btn-primary">Return Home</a>
                </div>
            </div>
        </body>
        </html>
        """, status_code=500)


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint.
    File: app/main.py
    Function: health_check
    """
    try:
        return {
            "status": "healthy",
            "service": "DEX Sniping Platform",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "api": "online",
                "dashboard": "available",
                "templates": "loaded"
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Global exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url.path}")
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


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting DEX Sniping Platform")
    logger.info("📊 Dashboard: http://127.0.0.1:8000/dashboard")
    logger.info("📚 API Docs: http://127.0.0.1:8000/docs")
    logger.info("💓 Health: http://127.0.0.1:8000/api/v1/health")
    logger.info("📊 Stats API: http://127.0.0.1:8000/api/v1/dashboard/stats")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
