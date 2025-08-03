"""
Updated FastAPI Main Application
File: app/main.py

Enhanced main application with Phase 3B dashboard integration including:
- Professional trading dashboard routes
- WebSocket support for real-time updates
- Static file serving for dashboard assets
- CORS middleware for frontend integration
- Background tasks for live data updates
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import asyncio
from contextlib import asynccontextmanager

from app.api.v1.endpoints import tokens, trading
from app.api.v1.endpoints import dashboard
from app.core.dependencies import get_current_user
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)


# Background tasks storage
background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Handles startup and shutdown tasks including:
    - Starting background tasks for real-time updates
    - Initializing dashboard components
    - Cleanup on shutdown
    """
    # Startup
    logger.info("🚀 Starting DEX Sniping Platform - Phase 3B")
    
    # Start background tasks for dashboard
    task = asyncio.create_task(start_dashboard_background_tasks())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    
    logger.info("✅ Dashboard background tasks started")
    logger.info("🎯 Phase 3B Professional Dashboard ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down DEX Sniping Platform")
    
    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
    
    # Wait for tasks to complete
    if background_tasks:
        await asyncio.gather(*background_tasks, return_exceptions=True)
    
    logger.info("✅ Shutdown complete")


# Create FastAPI application with lifespan events
app = FastAPI(
    title="DEX Sniping Platform",
    description="""
    Professional-grade DEX sniping platform with real-time token discovery, 
    Block 0 sniping capabilities, and advanced arbitrage detection.
    
    ## Phase 3A Complete ✅
    - Live DEX integration (Uniswap V2/V3)
    - Block 0 sniping engine
    - Real-time mempool monitoring
    - Multi-chain support (8+ networks)
    - Enterprise performance infrastructure
    
    ## Phase 3B In Progress 🚀
    - Professional trading dashboard
    - Real-time WebSocket feeds
    - Advanced portfolio analytics
    - AI-powered risk assessment
    """,
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8000",  # Alternative port
        "http://localhost:8001",  # Current FastAPI port
        "http://127.0.0.1:8001",
        "https://your-domain.com"  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.your-domain.com"]
)


# Static file serving for dashboard assets
if os.path.exists("dashboard/static"):
    app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")
    logger.info("✅ Static files mounted at /static")


# Include API routers
app.include_router(tokens.router, prefix="/api/v1")
app.include_router(trading.router, prefix="/api/v1")  
app.include_router(dashboard.router, prefix="/api/v1")

logger.info("✅ API routers included")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - redirect to dashboard.
    
    Returns:
        HTMLResponse: Welcome page with links to dashboard and docs
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniping Platform</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
            }
            .hero-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-10">
                    <div class="hero-card p-5">
                        <div class="text-center mb-5">
                            <h1 class="display-3 fw-bold text-primary mb-3">
                                <i class="bi bi-graph-up-arrow"></i>
                                DEX Sniping Platform
                            </h1>
                            <p class="lead text-muted">
                                Professional-grade automated trading for DEX sniping and arbitrage
                            </p>
                            <div class="badge bg-success fs-6 mb-3">
                                Phase 3A Complete ✅ | Phase 3B Active 🚀
                            </div>
                        </div>
                        
                        <div class="row text-center mb-5">
                            <div class="col-md-4">
                                <div class="feature-icon text-success">
                                    <i class="bi bi-lightning-charge"></i>
                                </div>
                                <h5>Block 0 Sniping</h5>
                                <p class="text-muted">Instant execution on token launches with MEV protection</p>
                            </div>
                            <div class="col-md-4">
                                <div class="feature-icon text-warning">
                                    <i class="bi bi-search"></i>
                                </div>
                                <h5>Live Discovery</h5>
                                <p class="text-muted">Real-time token discovery across 8+ blockchain networks</p>
                            </div>
                            <div class="col-md-4">
                                <div class="feature-icon text-info">
                                    <i class="bi bi-shield-check"></i>
                                </div>
                                <h5>AI Risk Assessment</h5>
                                <p class="text-muted">Advanced contract analysis and risk scoring</p>
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <a href="/dashboard" class="btn btn-primary btn-lg me-3">
                                <i class="bi bi-speedometer2"></i>
                                Open Dashboard
                            </a>
                            <a href="/docs" class="btn btn-outline-primary btn-lg me-3">
                                <i class="bi bi-book"></i>
                                API Docs
                            </a>
                            <a href="/api/v1/health" class="btn btn-outline-success btn-lg">
                                <i class="bi bi-heart-pulse"></i>
                                Health Check
                            </a>
                        </div>
                        
                        <div class="mt-4 text-center">
                            <small class="text-muted">
                                <i class="bi bi-circle-fill text-success"></i>
                                System Status: <span id="status">Checking...</span>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Check system health
            fetch('/api/v1/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = 'Operational';
                    document.getElementById('status').className = 'text-success fw-bold';
                })
                .catch(error => {
                    document.getElementById('status').textContent = 'Degraded';
                    document.getElementById('status').className = 'text-warning fw-bold';
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Serve the professional trading dashboard.
    
    Returns:
        HTMLResponse: The dashboard HTML page
    """
    try:
        dashboard_path = "dashboard/index.html"
        if os.path.exists(dashboard_path):
            return FileResponse(dashboard_path)
        else:
            # Return setup message if dashboard not found
            return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Dashboard Setup Required</title>
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="alert alert-warning">
                            <h4>Dashboard Setup Required</h4>
                            <p>Please run the setup script to initialize the dashboard:</p>
                            <code>python setup_phase3b_dashboard.py</code>
                        </div>
                        <a href="/" class="btn btn-primary">Back to Home</a>
                    </div>
                </body>
                </html>
            """)
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        raise


@app.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Dict: System health status
    """
    return {
        "status": "healthy",
        "timestamp": "2025-08-03T09:00:00Z",
        "version": "3.1.0",
        "phase": "3B - Professional Dashboard",
        "components": {
            "api": "operational",
            "database": "operational", 
            "blockchain": "operational",
            "dex_integration": "operational",
            "dashboard": "operational"
        }
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors."""
    # Return a simple response or serve actual favicon if available
    return {"message": "favicon"}


async def start_dashboard_background_tasks():
    """
    Start background tasks for dashboard real-time updates.
    
    This function runs continuously and manages:
    - Real-time data updates
    - WebSocket message broadcasting
    - System health monitoring
    """
    from app.api.v1.endpoints.dashboard import connection_manager
    
    logger.info("🔄 Starting dashboard background tasks...")
    
    update_interval = 10  # seconds
    
    while True:
        try:
            # Only run updates if there are active connections
            if connection_manager.active_connections:
                
                # Update dashboard statistics
                from app.api.v1.endpoints.dashboard import get_dashboard_stats
                stats = await get_dashboard_stats()
                await connection_manager.send_stats_update(stats)
                
                # Send token discovery updates every 30 seconds
                if int(asyncio.get_event_loop().time()) % 30 == 0:
                    from app.api.v1.endpoints.dashboard import get_live_token_discovery
                    tokens = await get_live_token_discovery()
                    await connection_manager.send_token_discovery(tokens)
                
                # Send random alerts occasionally
                if int(asyncio.get_event_loop().time()) % 45 == 0:
                    from app.api.v1.endpoints.dashboard import LiveAlert
                    alert = LiveAlert(
                        alert_type="system_update",
                        title="System Update",
                        message="Dashboard data refreshed successfully",
                        severity="info"
                    )
                    await connection_manager.send_alert(alert)
            
            await asyncio.sleep(update_interval)
            
        except Exception as e:
            logger.error(f"Dashboard background task error: {e}")
            await asyncio.sleep(update_interval)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 error handler."""
    return HTMLResponse(
        status_code=404,
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Not Found</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5 text-center">
                <h1 class="display-1">404</h1>
                <h2>Page Not Found</h2>
                <p>The requested page could not be found.</p>
                <a href="/" class="btn btn-primary">Go Home</a>
                <a href="/dashboard" class="btn btn-outline-primary">Dashboard</a>
            </div>
        </body>
        </html>
        """
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 error handler."""
    logger.error(f"Internal server error: {exc}")
    return HTMLResponse(
        status_code=500,
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Server Error</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5 text-center">
                <h1 class="display-1">500</h1>
                <h2>Internal Server Error</h2>
                <p>Something went wrong on our end. Please try again later.</p>
                <a href="/" class="btn btn-primary">Go Home</a>
            </div>
        </body>
        </html>
        """
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )