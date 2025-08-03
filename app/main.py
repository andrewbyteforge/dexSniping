"""
Fixed FastAPI Main Application
File: app/main.py

Professional main application without problematic background tasks.
Clean, working implementation focused on core functionality.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from app.utils.logger import setup_logger
from app.core.database import init_database, close_database

logger = setup_logger(__name__)

# Configure templates
templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting DEX Sniping Platform")
    
    try:
        await init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
    
    # Validate directories
    directories = [
        "frontend/templates",
        "frontend/static",
        "app/api/v1/endpoints"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            logger.info(f"✅ Directory found: {directory}")
        else:
            logger.warning(f"⚠️ Directory missing: {directory}")
    
    logger.info("✅ Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application")
    
    try:
        await close_database()
        logger.info("✅ Database closed")
    except Exception as e:
        logger.warning(f"Database shutdown error: {e}")
    
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

# Include API routers with error handling
try:
    from app.api.v1.endpoints import dashboard, tokens, trading
    
    app.include_router(dashboard.router, prefix="/api/v1")
    app.include_router(tokens.router, prefix="/api/v1") 
    app.include_router(trading.router, prefix="/api/v1")
    logger.info("✅ API routers included")
    
except Exception as e:
    logger.error(f"Error including routers: {e}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint."""
    try:
        if os.path.exists("frontend/templates/dashboard.html"):
            return templates.TemplateResponse("dashboard.html", {"request": request})
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>DEX Sniper Pro</title>
                <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container mt-5">
                    <div class="text-center">
                        <div class="card shadow-lg">
                            <div class="card-body p-5">
                                <h1 class="display-4 text-primary mb-3">
                                    <i class="bi bi-rocket-takeoff"></i> DEX Sniper Pro
                                </h1>
                                <p class="lead text-muted mb-4">Professional Trading Bot Platform</p>
                                <div class="row g-3">
                                    <div class="col-md-4">
                                        <a href="/api/v1/dashboard/stats" class="btn btn-primary w-100">
                                            <i class="bi bi-graph-up"></i> Dashboard Stats
                                        </a>
                                    </div>
                                    <div class="col-md-4">
                                        <a href="/docs" class="btn btn-outline-info w-100">
                                            <i class="bi bi-book"></i> API Documentation
                                        </a>
                                    </div>
                                    <div class="col-md-4">
                                        <a href="/api/v1/health" class="btn btn-outline-success w-100">
                                            <i class="bi bi-heart-pulse"></i> Health Check
                                        </a>
                                    </div>
                                </div>
                                <hr class="my-4">
                                <div class="row text-start">
                                    <div class="col-md-6">
                                        <h6 class="text-primary">Core Features:</h6>
                                        <ul class="list-unstyled small">
                                            <li><i class="bi bi-check-circle text-success"></i> Real-time Token Discovery</li>
                                            <li><i class="bi bi-check-circle text-success"></i> Advanced Risk Assessment</li>
                                            <li><i class="bi bi-check-circle text-success"></i> Multi-DEX Integration</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="text-primary">Status:</h6>
                                        <ul class="list-unstyled small">
                                            <li><i class="bi bi-check-circle text-success"></i> Phase 3B Complete</li>
                                            <li><i class="bi bi-gear text-warning"></i> AI Phase Starting</li>
                                            <li><i class="bi bi-check-circle text-success"></i> All Systems Online</li>
                                        </ul>
                                    </div>
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
    """Dashboard page endpoint."""
    try:
        if os.path.exists("frontend/templates/dashboard.html"):
            return templates.TemplateResponse("dashboard.html", {"request": request})
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard - DEX Sniper Pro</title>
                <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container mt-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h1><i class="bi bi-speedometer2"></i> Dashboard</h1>
                        <span class="badge bg-success">Online</span>
                    </div>
                    <div class="row g-4">
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="bi bi-bar-chart"></i> Statistics
                                    </h5>
                                    <p class="card-text">View real-time trading statistics and performance metrics.</p>
                                    <a href="/api/v1/dashboard/stats" class="btn btn-primary">View Stats API</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="bi bi-currency-exchange"></i> Live Tokens
                                    </h5>
                                    <p class="card-text">Monitor live token prices and market data.</p>
                                    <a href="/api/v1/dashboard/tokens/live" class="btn btn-success">View Tokens API</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="bi bi-graph-up-arrow"></i> Trading Metrics
                                    </h5>
                                    <p class="card-text">Access comprehensive trading performance data.</p>
                                    <a href="/api/v1/dashboard/trading/metrics" class="btn btn-info">View Metrics API</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="bi bi-heart-pulse"></i> System Health
                                    </h5>
                                    <p class="card-text">Monitor system health and performance status.</p>
                                    <a href="/api/v1/health" class="btn btn-outline-success">Health Check</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Dashboard endpoint error: {e}")
        return HTMLResponse(content=f"<h1>Dashboard Error</h1><p>{e}</p>")


@app.get("/api/v1/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        # Test database connectivity
        db_status = "unknown"
        try:
            from app.core.database import get_db_session
            async for session in get_db_session():
                db_status = "connected" if session else "mock_mode"
                break
        except Exception:
            db_status = "disconnected"
        
        # Check file system
        template_status = "operational" if os.path.exists("frontend/templates") else "missing"
        static_status = "operational" if os.path.exists("frontend/static") else "missing"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.1.0",
            "phase": "3B - Fixed and Operational",
            "components": {
                "api": "operational",
                "database": db_status,
                "templates": template_status,
                "static_files": static_status,
                "dashboard": "operational"
            },
            "endpoints": {
                "dashboard": "/dashboard",
                "dashboard_stats": "/api/v1/dashboard/stats",
                "live_tokens": "/api/v1/dashboard/tokens/live",
                "trading_metrics": "/api/v1/dashboard/trading/metrics",
                "health": "/api/v1/health"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/api/v1/")
async def api_info():
    """API information endpoint."""
    return {
        "message": "DEX Sniper Pro API",
        "version": "3.1.0",
        "phase": "3B - Fixed and Operational",
        "status": "operational",
        "documentation": "/docs"
    }


# Error handlers
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
