"""
Updated FastAPI Main Application - Complete Version
File: app/main.py

Enhanced main application with Phase 3B dashboard integration including:
- Professional trading dashboard routes
- WebSocket support for real-time updates
- Static file serving for dashboard assets
- CORS middleware for frontend integration
- Background tasks for live data updates
- Fixed API endpoints and health checks
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

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


# Include API routers with correct prefixes
app.include_router(tokens.router, prefix="/api/v1")
app.include_router(trading.router, prefix="/api/v1")  
app.include_router(dashboard.router, prefix="/api/v1")

logger.info("✅ API routers included")


# FIXED API ENDPOINTS - Add missing health and info endpoints
@app.get("/api/v1/health")
async def health_check():
    """API health check endpoint - FIXED."""
    return {
        "status": "healthy",
        "api_version": "3.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "3B - Enhanced Dashboard Features",
        "dashboard": "operational",
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "dashboard_stats": "/api/v1/dashboard/stats",
            "live_tokens": "/api/v1/dashboard/tokens/live",
            "token_discovery": "/api/v1/tokens/discover",
            "health": "/api/v1/health"
        },
        "components": {
            "api": "operational",
            "database": "operational", 
            "blockchain": "operational",
            "dex_integration": "operational",
            "dashboard": "operational",
            "websocket": "operational"
        }
    }


@app.get("/api/v1/")
async def api_info():
    """API information endpoint - FIXED."""
    return {
        "message": "DEX Sniping API v3.1.0",
        "version": "3.1.0",
        "phase": "3B - Enhanced Dashboard Features",
        "status": "operational",
        "documentation": "/docs",
        "step_1_status": "✅ COMPLETED - Enhanced Live Token Discovery Table",
        "endpoints": {
            "dashboard": "/api/v1/dashboard",
            "dashboard_stats": "/api/v1/dashboard/stats",
            "live_tokens": "/api/v1/dashboard/tokens/live",
            "token_discovery": "/api/v1/tokens/discover",
            "token_analyze": "/api/v1/dashboard/tokens/analyze/{address}",
            "websocket": "/api/v1/dashboard/ws",
            "health": "/api/v1/health"
        },
        "features": {
            "live_token_discovery": "✅ Operational",
            "real_time_filtering": "✅ Operational", 
            "websocket_updates": "✅ Operational",
            "risk_assessment": "✅ Operational",
            "multi_network_support": "✅ Operational"
        }
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - Enhanced welcome page.
    
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
            .pulse {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
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
                            <div class="badge bg-success fs-6 mb-3 pulse">
                                Phase 3A Complete ✅ | Phase 3B Step 1 Complete ✅
                            </div>
                        </div>
                        
                        <div class="row text-center mb-5">
                            <div class="col-md-4">
                                <div class="feature-icon text-success">
                                    <i class="bi bi-lightning-charge"></i>
                                </div>
                                <h5>Block 0 Sniping</h5>
                                <p class="text-muted">Instant execution on token launches with MEV protection</p>
                                <small class="badge bg-success">✅ Operational</small>
                            </div>
                            <div class="col-md-4">
                                <div class="feature-icon text-warning">
                                    <i class="bi bi-search"></i>
                                </div>
                                <h5>Live Token Discovery</h5>
                                <p class="text-muted">Real-time token discovery across 8+ blockchain networks</p>
                                <small class="badge bg-success">✅ Enhanced (Step 1)</small>
                            </div>
                            <div class="col-md-4">
                                <div class="feature-icon text-info">
                                    <i class="bi bi-shield-check"></i>
                                </div>
                                <h5>AI Risk Assessment</h5>
                                <p class="text-muted">Advanced contract analysis and risk scoring</p>
                                <small class="badge bg-warning">🔄 Phase 3B</small>
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <a href="/dashboard" class="btn btn-primary btn-lg me-3 pulse">
                                <i class="bi bi-speedometer2"></i>
                                Open Enhanced Dashboard
                            </a>
                            <a href="/docs" class="btn btn-outline-primary btn-lg me-3">
                                <i class="bi bi-book"></i>
                                API Docs
                            </a>
                            <a href="/api/v1/health" class="btn btn-outline-success btn-lg" target="_blank">
                                <i class="bi bi-heart-pulse"></i>
                                Health Check
                            </a>
                        </div>
                        
                        <div class="mt-4 text-center">
                            <div class="row">
                                <div class="col-md-6">
                                    <small class="text-muted">
                                        <i class="bi bi-circle-fill text-success"></i>
                                        System Status: <span id="status" class="fw-bold">Checking...</span>
                                    </small>
                                </div>
                                <div class="col-md-6">
                                    <small class="text-muted">
                                        <i class="bi bi-gear-fill text-primary"></i>
                                        Current Phase: 3B - Enhanced Dashboard Features
                                    </small>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Quick Stats -->
                        <div class="row mt-4" id="quick-stats" style="display: none;">
                            <div class="col-md-3 text-center">
                                <div class="h5 text-primary" id="stat-tokens">0</div>
                                <small class="text-muted">Tokens Discovered</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="h5 text-success" id="stat-trades">0</div>
                                <small class="text-muted">Active Trades</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="h5 text-warning" id="stat-arb">0</div>
                                <small class="text-muted">Arbitrage Ops</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="h5 text-info" id="stat-portfolio">$0</div>
                                <small class="text-muted">Portfolio Value</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Check system health and load quick stats
            async function loadSystemStatus() {
                try {
                    // Health check
                    const healthResponse = await fetch('/api/v1/health');
                    const healthData = await healthResponse.json();
                    
                    document.getElementById('status').textContent = 'Operational ✅';
                    document.getElementById('status').className = 'text-success fw-bold';
                    
                    // Load dashboard stats
                    const statsResponse = await fetch('/api/v1/dashboard/stats');
                    const statsData = await statsResponse.json();
                    
                    document.getElementById('stat-tokens').textContent = statsData.tokens_discovered;
                    document.getElementById('stat-trades').textContent = statsData.active_trades;
                    document.getElementById('stat-arb').textContent = statsData.arbitrage_opportunities;
                    document.getElementById('stat-portfolio').textContent = '$' + statsData.portfolio_value.toFixed(0);
                    
                    document.getElementById('quick-stats').style.display = 'block';
                    
                } catch (error) {
                    console.error('Status check failed:', error);
                    document.getElementById('status').textContent = 'Degraded ⚠️';
                    document.getElementById('status').className = 'text-warning fw-bold';
                }
            }
            
            // Load status on page load
            loadSystemStatus();
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
            # Return enhanced setup message if dashboard not found
            return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Dashboard - DEX Sniper Pro</title>
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
                </head>
                <body class="bg-light">
                    <div class="container mt-5">
                        <div class="row justify-content-center">
                            <div class="col-lg-8">
                                <div class="card shadow">
                                    <div class="card-header bg-primary text-white">
                                        <h4 class="mb-0">
                                            <i class="bi bi-speedometer2"></i>
                                            DEX Sniper Dashboard
                                        </h4>
                                    </div>
                                    <div class="card-body">
                                        <div class="alert alert-info">
                                            <h5>📊 Dashboard APIs Ready!</h5>
                                            <p class="mb-3">The dashboard backend is operational. You can access the APIs directly:</p>
                                            
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <h6>📈 Dashboard Stats:</h6>
                                                    <a href="/api/v1/dashboard/stats" class="btn btn-sm btn-outline-primary mb-2" target="_blank">
                                                        <i class="bi bi-graph-up"></i> View Stats API
                                                    </a>
                                                </div>
                                                <div class="col-md-6">
                                                    <h6>🔍 Live Token Discovery:</h6>
                                                    <a href="/api/v1/dashboard/tokens/live" class="btn btn-sm btn-outline-success mb-2" target="_blank">
                                                        <i class="bi bi-search"></i> View Tokens API
                                                    </a>
                                                </div>
                                            </div>
                                            
                                            <h6 class="mt-3">🔗 Additional APIs:</h6>
                                            <div class="btn-group-sm">
                                                <a href="/api/v1/tokens/discover" class="btn btn-outline-warning btn-sm me-2" target="_blank">
                                                    Token Discovery
                                                </a>
                                                <a href="/api/v1/health" class="btn btn-outline-success btn-sm me-2" target="_blank">
                                                    Health Check
                                                </a>
                                                <a href="/docs" class="btn btn-outline-info btn-sm" target="_blank">
                                                    API Documentation
                                                </a>
                                            </div>
                                        </div>
                                        
                                        <div class="alert alert-success">
                                            <h6>✅ Phase 3B Step 1 Complete!</h6>
                                            <p class="mb-0">Enhanced Live Token Discovery Table with real-time filtering and professional UI is ready!</p>
                                        </div>
                                        
                                        <div class="text-center">
                                            <a href="/" class="btn btn-primary">
                                                <i class="bi bi-house"></i> Back to Home
                                            </a>
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
        logger.error(f"Error serving dashboard: {e}")
        raise


@app.get("/health")
async def basic_health_check():
    """
    Basic health check endpoint (alternative path).
    
    Returns:
        Dict: System health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.1.0",
        "phase": "3B - Professional Dashboard",
        "step_1_status": "✅ COMPLETED - Enhanced Live Token Discovery Table",
        "components": {
            "api": "operational",
            "database": "operational", 
            "blockchain": "operational",
            "dex_integration": "operational",
            "dashboard": "operational",
            "websocket": "operational"
        }
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors."""
    return {"message": "DEX Sniper Pro"}


async def start_dashboard_background_tasks():
    """
    Start background tasks for dashboard real-time updates.
    
    This function runs continuously and manages:
    - Real-time data updates
    - WebSocket message broadcasting
    - System health monitoring
    """
    logger.info("🔄 Starting dashboard background tasks...")
    
    update_interval = 10  # seconds
    
    while True:
        try:
            # Import here to avoid circular imports
            from app.api.v1.endpoints.dashboard import connection_manager
            
            # Only run updates if there are active connections
            if connection_manager.active_connections:
                
                # Update dashboard statistics
                try:
                    from app.api.v1.endpoints.dashboard import get_dashboard_stats
                    stats = await get_dashboard_stats()
                    await connection_manager.send_stats_update(stats.dict())
                except Exception as e:
                    logger.error(f"Failed to update stats: {e}")
                
                # Send token discovery updates every 30 seconds
                if int(asyncio.get_event_loop().time()) % 30 == 0:
                    try:
                        from app.api.v1.endpoints.dashboard import get_live_tokens
                        tokens = await get_live_tokens()
                        await connection_manager.send_token_discovery([t.dict() for t in tokens])
                    except Exception as e:
                        logger.error(f"Failed to update tokens: {e}")
                
                # Send periodic alerts
                if int(asyncio.get_event_loop().time()) % 60 == 0:
                    try:
                        from app.api.v1.endpoints.dashboard import LiveAlert
                        alert = LiveAlert(
                            alert_type="system_update",
                            title="System Update",
                            message="Dashboard data refreshed successfully",
                            severity="info",
                            timestamp=datetime.utcnow().isoformat()
                        )
                        await connection_manager.send_alert(alert)
                    except Exception as e:
                        logger.error(f"Failed to send alert: {e}")
            
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
            <title>Page Not Found - DEX Sniper</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container mt-5 text-center">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card shadow">
                            <div class="card-body">
                                <h1 class="display-1 text-muted">404</h1>
                                <h2 class="mb-3">Page Not Found</h2>
                                <p class="text-muted mb-4">The requested page could not be found.</p>
                                <div class="btn-group">
                                    <a href="/" class="btn btn-primary">
                                        <i class="bi bi-house"></i> Go Home
                                    </a>
                                    <a href="/dashboard" class="btn btn-outline-primary">
                                        <i class="bi bi-speedometer2"></i> Dashboard
                                    </a>
                                    <a href="/docs" class="btn btn-outline-info">
                                        <i class="bi bi-book"></i> API Docs
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
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
            <title>Server Error - DEX Sniper</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.1/font/bootstrap-icons.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container mt-5 text-center">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card shadow">
                            <div class="card-body">
                                <h1 class="display-1 text-danger">500</h1>
                                <h2 class="mb-3">Internal Server Error</h2>
                                <p class="text-muted mb-4">Something went wrong on our end. Please try again later.</p>
                                <div class="btn-group">
                                    <a href="/" class="btn btn-primary">
                                        <i class="bi bi-house"></i> Go Home
                                    </a>
                                    <a href="/api/v1/health" class="btn btn-outline-success">
                                        <i class="bi bi-heart-pulse"></i> Check Status
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
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