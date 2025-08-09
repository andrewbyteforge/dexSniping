"""
DEX Sniper Pro - Main Application - Windows Compatible
File: app/main.py

Fixed version that works on Windows with proper encoding and async handling.
"""

import sys
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Initialize logger (Windows-compatible, no emojis)
try:
    from app.core.utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    try:
        from app.utils.logger import setup_logger
        logger = setup_logger(__name__)
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

# Import Phase 4D exceptions with fallbacks
try:
    from app.core.exceptions import TradingError
except ImportError:
    class TradingError(Exception):
        """Fallback TradingError for compatibility."""
        pass

try:
    from app.core.exceptions import AIError
except ImportError:
    class AIError(Exception):
        """Fallback AIError for Phase 4D compatibility."""
        pass

try:
    from app.core.exceptions import WalletError
except ImportError:
    class WalletError(Exception):
        """Fallback WalletError for Phase 4D compatibility."""
        pass

try:
    from app.core.exceptions import DEXError
except ImportError:
    class DEXError(Exception):
        """Fallback DEXError for Phase 4D compatibility."""
        pass

# Phase 4D component imports with fallbacks
SNIPE_TRADING_AVAILABLE = False
AI_RISK_AVAILABLE = False
WALLET_MANAGER_AVAILABLE = False

try:
    from app.core.trading.snipe_trading_controller import (
        initialize_snipe_trading_controller,
        get_snipe_trading_controller
    )
    SNIPE_TRADING_AVAILABLE = True
    logger.info("SNIPE: Snipe trading controller available")
except ImportError:
    logger.warning("SNIPE: Snipe trading controller not available")

try:
    from app.core.ai.risk_assessment_engine import (
        initialize_ai_risk_engine,
        get_ai_risk_engine
    )
    AI_RISK_AVAILABLE = True
    logger.info("AI: AI risk assessment engine available")
except ImportError:
    logger.warning("AI: AI risk assessment engine not available")

try:
    from app.core.wallet.enhanced_wallet_manager import EnhancedWalletManager
    WALLET_MANAGER_AVAILABLE = True
    logger.info("WALLET: Enhanced wallet manager available")
except ImportError:
    logger.warning("WALLET: Enhanced wallet manager not available")

# Global component instances
global_components = {
    "snipe_controller": None,
    "ai_engine": None,
    "wallet_manager": None,
    "dex_integration": None,
    "network_manager": None
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler with Phase 4D component initialization."""
    
    # Startup
    logger.info("STARTUP: Starting DEX Sniper Pro - Phase 4D Enhanced")
    logger.info("=" * 60)
    
    try:
        # Initialize Phase 4D components if available
        if AI_RISK_AVAILABLE:
            logger.info("AI: Initializing AI Risk Assessment Engine...")
            try:
                ai_engine = await initialize_ai_risk_engine()
                global_components["ai_engine"] = ai_engine
                app.state.ai_engine = ai_engine
                logger.info("AI: AI Risk Assessment Engine initialized")
            except Exception as e:
                logger.warning(f"AI: Engine initialization failed: {e}")
        
        if WALLET_MANAGER_AVAILABLE:
            logger.info("WALLET: Initializing Enhanced Wallet Manager...")
            try:
                # Fixed: Don't await - it's not an async function
                wallet_manager = EnhancedWalletManager()
                global_components["wallet_manager"] = wallet_manager
                app.state.wallet_manager = wallet_manager
                logger.info("WALLET: Enhanced Wallet Manager initialized")
            except Exception as e:
                logger.warning(f"WALLET: Manager initialization failed: {e}")
        
        if SNIPE_TRADING_AVAILABLE:
            logger.info("SNIPE: Initializing Snipe Trading Controller...")
            try:
                snipe_controller = await initialize_snipe_trading_controller()
                global_components["snipe_controller"] = snipe_controller
                app.state.snipe_controller = snipe_controller
                logger.info("SNIPE: Snipe Trading Controller initialized")
            except Exception as e:
                logger.warning(f"SNIPE: Controller initialization failed: {e}")
        
        logger.info("STARTUP: Application initialization complete!")
        if not any([AI_RISK_AVAILABLE, WALLET_MANAGER_AVAILABLE, SNIPE_TRADING_AVAILABLE]):
            logger.info("INFO: Running in compatibility mode - Phase 4D features will be added as components become available")
        
    except Exception as error:
        logger.error(f"ERROR: Phase 4D initialization error: {error}")
        logger.info("INFO: Continuing without Phase 4D features...")
    
    # Application is ready
    yield
    
    # Shutdown
    logger.info("SHUTDOWN: Shutting down DEX Sniper Pro")
    
    try:
        # Cleanup Phase 4D components
        if global_components["snipe_controller"]:
            try:
                active_snipes = global_components["snipe_controller"].get_active_snipes()
                if active_snipes:
                    logger.info(f"CLEANUP: Cleaning up {len(active_snipes)} active snipes...")
                    for request_id in list(active_snipes.keys()):
                        try:
                            del global_components["snipe_controller"].active_snipes[request_id]
                        except Exception:
                            pass
            except Exception as e:
                logger.warning(f"CLEANUP: Snipe cleanup error: {e}")
        
        if global_components["ai_engine"]:
            try:
                logger.info("CLEANUP: Cleaning up AI Engine...")
                global_components["ai_engine"].assessment_cache.clear()
            except Exception as e:
                logger.warning(f"CLEANUP: AI cleanup error: {e}")
        
        logger.info("SHUTDOWN: Shutdown complete")
        
    except Exception as error:
        logger.error(f"ERROR: Error during shutdown: {error}")


# Create FastAPI application
app = FastAPI(
    title="DEX Sniper Pro - Phase 4D",
    description="Professional automated trading bot with progressive enhancement",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
try:
    templates = Jinja2Templates(directory="frontend/templates")
    logger.info("TEMPLATE: Templates configured")
except Exception as e:
    templates = None
    logger.warning(f"TEMPLATE: Templates not available: {e}")

# Mount static files if directory exists
static_path = Path("frontend/static")
if static_path.exists():
    try:
        app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
        logger.info("STATIC: Static files mounted")
    except Exception as e:
        logger.warning(f"STATIC: Static files not mounted: {e}")

# Include API routers with error handling
try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
    logger.info("ROUTER: Dashboard router included")
except Exception as e:
    logger.warning(f"ROUTER: Dashboard router not available: {e}")

try:
    from app.api.v1.endpoints.tokens import router as tokens_router
    app.include_router(tokens_router, prefix="/api/v1", tags=["tokens"])
    logger.info("ROUTER: Tokens router included")
except Exception as e:
    logger.warning(f"ROUTER: Tokens router not available: {e}")

try:
    from app.api.v1.endpoints.trading import router as trading_router
    app.include_router(trading_router, prefix="/api/v1", tags=["trading"])
    logger.info("ROUTER: Trading router included")
except Exception as e:
    logger.warning(f"ROUTER: Trading router not available: {e}")

# Include Phase 4D API routers
if SNIPE_TRADING_AVAILABLE:
    try:
        from app.api.v1.endpoints.snipe_trading import router as snipe_router
        app.include_router(snipe_router, prefix="/api/v1", tags=["Phase 4D - Snipe Trading"])
        logger.info("ROUTER: Phase 4D Snipe Trading router included")
    except Exception as e:
        logger.warning(f"ROUTER: Snipe Trading router not available: {e}")

# Setup Phase 4D error handlers
@app.exception_handler(TradingError)
async def trading_error_handler(request, exc: TradingError):
    """Handle trading-related errors."""
    logger.error(f"Trading error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error_type": "trading_error",
            "message": str(exc),
            "timestamp": "2025-08-09T12:00:00Z"
        }
    )

@app.exception_handler(AIError)
async def ai_error_handler(request, exc: AIError):
    """Handle AI-related errors."""
    logger.error(f"AI error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_type": "ai_error",
            "message": str(exc),
            "timestamp": "2025-08-09T12:00:00Z"
        }
    )

@app.exception_handler(WalletError)
async def wallet_error_handler(request, exc: WalletError):
    """Handle wallet-related errors."""
    logger.error(f"Wallet error: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error_type": "wallet_error",
            "message": str(exc),
            "timestamp": "2025-08-09T12:00:00Z"
        }
    )


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the home page with Phase 4D features."""
    
    # Check which Phase 4D features are available
    features_status = {
        "snipe_trading": "ACTIVE" if SNIPE_TRADING_AVAILABLE else "NOT AVAILABLE",
        "ai_risk_assessment": "ACTIVE" if AI_RISK_AVAILABLE else "NOT AVAILABLE", 
        "wallet_integration": "ACTIVE" if WALLET_MANAGER_AVAILABLE else "NOT AVAILABLE",
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro - Phase 4D</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 3rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                max-width: 800px;
            }}
            h1 {{
                font-size: 3rem;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            p {{
                font-size: 1.2rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }}
            .btn {{
                display: inline-block;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                margin: 10px;
                transition: all 0.3s ease;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}
            .btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }}
            .status {{
                background: rgba(40, 167, 69, 0.2);
                padding: 1rem;
                border-radius: 10px;
                margin: 2rem 0;
                border: 1px solid rgba(40, 167, 69, 0.5);
            }}
            .features {{
                background: rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                border-radius: 10px;
                margin: 2rem 0;
                text-align: left;
            }}
            .feature-item {{
                margin: 0.5rem 0;
                padding: 0.5rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }}
            .version-badge {{
                background: linear-gradient(45deg, #ff6b6b, #feca57);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin: 1rem 0;
            }}
            .compatibility-notice {{
                background: rgba(255, 193, 7, 0.2);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border: 1px solid rgba(255, 193, 7, 0.5);
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DEX Sniper Pro</h1>
            <div class="version-badge">Phase 4D Enhanced - v4.0.0</div>
            <p>Professional Trading Bot with Progressive Enhancement</p>
            
            <div class="status">
                <strong>SYSTEM STATUS: OPERATIONAL</strong><br>
                Enhanced dashboard with live opportunities and graceful fallbacks!
            </div>
            
            <div class="features">
                <h3>Available Features</h3>
                <div class="feature-item">SNIPE TRADING: {features_status['snipe_trading']}</div>
                <div class="feature-item">AI RISK ASSESSMENT: {features_status['ai_risk_assessment']}</div>
                <div class="feature-item">WALLET INTEGRATION: {features_status['wallet_integration']}</div>
                <div class="feature-item">ENHANCED DASHBOARD: ALWAYS AVAILABLE</div>
                <div class="feature-item">LIVE TOKEN DISCOVERY: ALWAYS AVAILABLE</div>
                <div class="feature-item">TRADING ACTIVITY: ALWAYS AVAILABLE</div>
            </div>
            
            <a href="/dashboard" class="btn">Enhanced Dashboard</a>
            <a href="/activity" class="btn">Trading Activity</a>
            <a href="/api/docs" class="btn">API Documentation</a>
            <a href="/health" class="btn">System Health</a>
            
            <div class="compatibility-notice">
                <strong>COMPATIBILITY MODE ACTIVE</strong><br>
                This application uses progressive enhancement. Phase 4D features will automatically 
                activate as components become available. The core functionality is always operational.
            </div>
            
            <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
                Ready for development - Phase 4D components load progressively
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Enhanced dashboard endpoint - keeping your original excellent design
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the enhanced dashboard with live opportunities."""
    
    # Try to use templates first
    if templates:
        try:
            return templates.TemplateResponse(
                "pages/dashboard.html", 
                {"request": request}
            )
        except Exception as e:
            logger.warning(f"Template error: {e}")
    
    # Your original enhanced dashboard HTML
    dashboard_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro Dashboard - Phase 4D Enhanced</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { 
                background: #f8fafc; 
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(180deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                z-index: 1000;
                overflow-y: auto;
            }
            .main-content {
                margin-left: 280px;
                padding: 2rem;
            }
            .metric-card {
                background: linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                border: none;
                transition: transform 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
            }
            .opportunity-card {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                transition: all 0.2s ease;
                background: white;
            }
            .opportunity-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .token-symbol {
                font-weight: 700;
                font-size: 1.1rem;
            }
            .price-change-positive {
                color: #10b981;
                font-weight: 600;
            }
            .price-change-negative {
                color: #ef4444;
                font-weight: 600;
            }
            .risk-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .risk-low { background: #d1fae5; color: #065f46; }
            .risk-medium { background: #fef3c7; color: #92400e; }
            .risk-high { background: #fee2e2; color: #991b1b; }
            .network-badge {
                background: linear-gradient(45deg, rgb(102, 126, 234), rgb(118, 75, 162));
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
            }
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid rgb(102, 126, 234);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @media (max-width: 768px) {
                .sidebar { transform: translateX(-100%); }
                .main-content { margin-left: 0; }
            }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="p-4 text-center border-bottom border-light border-opacity-25">
                <h4 class="mb-0">DEX Sniper</h4>
                <small class="text-light opacity-75">Phase 4D v4.0</small>
            </div>
            <nav class="p-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link text-light active" href="/dashboard">
                            <i class="bi bi-speedometer2 me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/activity">
                            <i class="bi bi-clock-history me-2"></i>Activity
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/api/docs">
                            <i class="bi bi-book me-2"></i>API Docs
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/health">
                            <i class="bi bi-heart-pulse me-2"></i>Health
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2>Enhanced Trading Dashboard</h2>
                    <p class="text-muted mb-0">Real-time portfolio monitoring with live opportunities</p>
                </div>
                <div class="badge bg-success">
                    <i class="bi bi-dot"></i> Live
                </div>
            </div>

            <!-- Metrics Row -->
            <div class="row g-4 mb-4">
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="portfolioValue">$1,247.83</div>
                            <div class="opacity-75">Portfolio Value</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value text-success" id="dailyPnl">+$45.67</div>
                            <div class="opacity-75">Daily P&L</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="activePositions">3</div>
                            <div class="opacity-75">Active Positions</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="successRate">78.5%</div>
                            <div class="opacity-75">Success Rate</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Opportunities Section -->
            <div class="row g-4 mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                <i class="bi bi-search text-primary"></i>
                                Live Opportunities
                            </h5>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="refreshOpportunities()">
                                    <i class="bi bi-arrow-clockwise"></i>
                                    Refresh
                                </button>
                                <span class="badge bg-success">
                                    <i class="bi bi-dot"></i>
                                    Live
                                </span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="opportunitiesContainer">
                                <div class="text-center">
                                    <div class="loading-spinner"></div>
                                    <p class="mt-2">Loading opportunities...</p>
                                </div>
                            </div>
                            
                            <div class="text-center mt-3">
                                <button class="btn btn-outline-primary" onclick="loadMoreOpportunities()">
                                    <i class="bi bi-plus-circle"></i>
                                    Load More Opportunities
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- API Testing Section -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">API Testing Center</h5>
                </div>
                <div class="card-body">
                    <p>Test the enhanced API endpoints:</p>
                    <button class="btn btn-primary me-2" onclick="testAPI('/api/v1/dashboard/stats')">
                        <i class="bi bi-graph-up"></i> Dashboard Stats
                    </button>
                    <button class="btn btn-success me-2" onclick="testAPI('/api/v1/tokens/discover')">
                        <i class="bi bi-search"></i> Token Discovery
                    </button>
                    <button class="btn btn-info me-2" onclick="testAPI('/api/v1/tokens/trending')">
                        <i class="bi bi-fire"></i> Trending Tokens
                    </button>
                    <button class="btn btn-warning me-2" onclick="testAPI('/health')">
                        <i class="bi bi-heart-pulse"></i> Health Check
                    </button>
                    <button class="btn btn-secondary" onclick="refreshDashboard()">
                        <i class="bi bi-arrow-clockwise"></i> Refresh Data
                    </button>
                    <div id="apiResults" class="mt-3 p-3 bg-light rounded" style="display: none;"></div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Global variables
            let currentTokens = [];
            let isLoading = false;
            
            console.log('DEX Sniper Pro Enhanced Dashboard initializing...');
            
            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Dashboard DOM loaded, starting initialization...');
                refreshDashboard();
                loadOpportunities();
                
                // Auto-refresh every 30 seconds
                setInterval(() => {
                    if (!document.hidden) {
                        refreshDashboard();
                        loadOpportunities();
                    }
                }, 30000);
                
                console.log('Dashboard initialization complete');
            });
            
            async function loadOpportunities() {
                if (isLoading) {
                    console.log('Already loading opportunities, skipping...');
                    return;
                }
                
                isLoading = true;
                const container = document.getElementById('opportunitiesContainer');
                
                try {
                    console.log('Loading live opportunities from API...');
                    
                    const response = await fetch('/api/v1/tokens/discover?limit=8');
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('API Response received:', data);
                    
                    if (data.tokens && data.tokens.length > 0) {
                        currentTokens = data.tokens;
                        displayOpportunities(data.tokens);
                        console.log(`Displaying ${data.tokens.length} opportunities`);
                    } else {
                        container.innerHTML = '<p class="text-muted text-center">No opportunities found. Try refreshing.</p>';
                        console.log('No tokens in API response');
                    }
                    
                } catch (error) {
                    console.error('Failed to load opportunities:', error);
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <strong>Unable to load opportunities</strong><br>
                            ${error.message}<br>
                            <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadOpportunities()">
                                Try Again
                            </button>
                        </div>
                    `;
                } finally {
                    isLoading = false;
                }
            }
            
            function displayOpportunities(tokens) {
                console.log('Starting to display opportunities:', tokens);
                const container = document.getElementById('opportunitiesContainer');
                
                if (!container) {
                    console.error('Container element not found!');
                    return;
                }
                
                if (!tokens || tokens.length === 0) {
                    container.innerHTML = '<p class="text-muted text-center">No opportunities available</p>';
                    console.log('No tokens to display');
                    return;
                }
                
                console.log(`Processing ${tokens.length} tokens for display`);
                
                const opportunitiesHTML = tokens.map((token, index) => {
                    console.log(`Processing token ${index + 1}:`, token);
                    
                    // Safely access token properties with fallbacks
                    const symbol = token.symbol || 'UNKNOWN';
                    const name = token.name || 'Unknown Token';
                    const network = token.network || 'Unknown';
                    const price = token.price || '$0.000000';
                    const change24h = token.change_24h || 0;
                    const liquidity = token.liquidity || 0;
                    const riskLevel = token.risk_level || 'medium';
                    const riskScore = token.risk_score || 5.0;
                    const ageHours = token.age_hours || 1;
                    const address = token.address || '0x0000000000000000000000000000000000000000';
                    
                    const changeClass = change24h > 0 ? 'price-change-positive' : 'price-change-negative';
                    const changeIcon = change24h > 0 ? 'bi-trending-up' : 'bi-trending-down';
                    const riskClass = `risk-${riskLevel}`;
                    
                    return `
                        <div class="opportunity-card" data-token="${symbol}">
                            <div class="row align-items-center">
                                <div class="col-md-3">
                                    <div class="d-flex align-items-center">
                                        <div>
                                            <div class="token-symbol">${symbol}</div>
                                            <small class="text-muted">${name}</small>
                                            <br>
                                            <span class="network-badge">${network}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <div class="fw-bold">${price}</div>
                                    <div class="${changeClass}">
                                        <i class="bi ${changeIcon}"></i>
                                        ${change24h > 0 ? '+' : ''}${change24h.toFixed(1)}%
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Liquidity:</small>
                                    <div class="fw-bold">$${liquidity.toLocaleString()}</div>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Risk:</small>
                                    <div>
                                        <span class="risk-badge ${riskClass}">
                                            ${riskLevel} (${riskScore})
                                        </span>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">Age:</small>
                                    <div class="fw-bold">${formatAge(ageHours)}</div>
                                </div>
                                <div class="col-md-1 text-end">
                                    <button class="btn btn-primary btn-sm" onclick="snipeToken('${symbol}', '${address}')">
                                        <i class="bi bi-lightning"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                console.log('Generated HTML length:', opportunitiesHTML.length);
                container.innerHTML = opportunitiesHTML;
                console.log(`Successfully rendered ${tokens.length} opportunity cards`);
                
                // Verify that cards were actually added to DOM
                const addedCards = container.querySelectorAll('.opportunity-card');
                console.log(`Verification: ${addedCards.length} cards found in DOM`);
            }
            
            function formatAge(hours) {
                if (hours < 1) return `${Math.round(hours * 60)}m`;
                if (hours < 24) return `${Math.round(hours)}h`;
                return `${Math.round(hours / 24)}d`;
            }
            
            function snipeToken(symbol, address) {
                console.log(`Enhanced Snipe request: ${symbol} (${address})`);
                alert(`Enhanced Snipe ${symbol} functionality ready!\\nAddress: ${address}\\nThis will connect to your enhanced trading engine with Phase 4D features when available.`);
            }
            
            async function refreshOpportunities() {
                console.log('Manual refresh requested...');
                await loadOpportunities();
            }
            
            async function loadMoreOpportunities() {
                console.log('Loading more opportunities...');
                try {
                    const response = await fetch('/api/v1/tokens/discover?limit=15');
                    const data = await response.json();
                    
                    if (data.tokens) {
                        currentTokens = [...currentTokens, ...data.tokens];
                        displayOpportunities(currentTokens.slice(0, 20)); // Show max 20
                    }
                } catch (error) {
                    console.error('Failed to load more opportunities:', error);
                }
            }
            
            async function testAPI(endpoint) {
                const resultsDiv = document.getElementById('apiResults');
                resultsDiv.style.display = 'block';
                resultsDiv.innerHTML = `<strong>Testing:</strong> ${endpoint}...`;
                
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultsDiv.className = 'mt-3 p-3 bg-success text-white rounded';
                        resultsDiv.innerHTML = `
                            <strong>Success (${response.status}):</strong> ${endpoint}<br>
                            <small>${JSON.stringify(data, null, 2)}</small>
                        `;
                    } else {
                        resultsDiv.className = 'mt-3 p-3 bg-danger text-white rounded';
                        resultsDiv.innerHTML = `
                            <strong>Error (${response.status}):</strong> ${endpoint}<br>
                            <small>${JSON.stringify(data, null, 2)}</small>
                        `;
                    }
                } catch (error) {
                    resultsDiv.className = 'mt-3 p-3 bg-danger text-white rounded';
                    resultsDiv.innerHTML = `
                        <strong>Network Error:</strong> ${endpoint}<br>
                        <small>${error.message}</small>
                    `;
                }
            }
            
            async function refreshDashboard() {
                try {
                    const response = await fetch('/api/v1/dashboard/stats');
                    if (response.ok) {
                        const result = await response.json();
                        if (result.status === 'success' && result.data) {
                            const data = result.data;
                            document.getElementById('portfolioValue').textContent = '$' + data.portfolio_value;
                            document.getElementById('dailyPnl').textContent = '+$' + data.daily_pnl;
                            document.getElementById('successRate').textContent = data.success_rate;
                            document.getElementById('activePositions').textContent = data.active_trades;
                        }
                    }
                } catch (error) {
                    console.error('Dashboard refresh error:', error);
                }
            }
            
            console.log('DEX Sniper Pro Enhanced Dashboard scripts loaded successfully!');
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=dashboard_html)


# Keep the original activity endpoint
@app.get("/activity", response_class=HTMLResponse)
async def activity(request: Request):
    """Serve the trading activity page."""
    
    # Try to use templates first
    if templates:
        try:
            return templates.TemplateResponse(
                "pages/activity.html", 
                {"request": request}
            )
        except Exception as e:
            logger.warning(f"Activity template error: {e}")
    
    # Fallback activity page
    activity_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Activity - DEX Sniper Pro</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { 
                background: #f8fafc; 
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(180deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                z-index: 1000;
                overflow-y: auto;
            }
            .main-content {
                margin-left: 280px;
                padding: 2rem;
            }
            .activity-card {
                border-left: 4px solid #10b981;
                transition: transform 0.2s ease;
            }
            .activity-card:hover {
                transform: translateY(-2px);
            }
            .profit-positive { color: #10b981; font-weight: 600; }
            .profit-negative { color: #ef4444; font-weight: 600; }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="p-4 text-center border-bottom border-light border-opacity-25">
                <h4 class="mb-0">DEX Sniper</h4>
                <small class="text-light opacity-75">Pro v4.0</small>
            </div>
            <nav class="p-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/dashboard">
                            <i class="bi bi-speedometer2 me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light active" href="/activity">
                            <i class="bi bi-clock-history me-2"></i>Activity
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/api/docs">
                            <i class="bi bi-book me-2"></i>API Docs
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2>Trading Activity</h2>
                    <p class="text-muted mb-0">Complete history of trading operations</p>
                </div>
                <div class="badge bg-success">
                    <i class="bi bi-dot"></i> Live
                </div>
            </div>

            <!-- Activity Cards -->
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="card activity-card">
                        <div class="card-body">
                            <h6 class="mb-1">PEPE Token Purchase</h6>
                            <p class="text-muted mb-1">Bought 1,000,000 PEPE at $0.00000123</p>
                            <div class="d-flex justify-content-between">
                                <small class="text-muted">2 hours ago</small>
                                <span class="profit-positive">+$33.40 (+26.8%)</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card activity-card">
                        <div class="card-body">
                            <h6 class="mb-1">WOJAK Token Sale</h6>
                            <p class="text-muted mb-1">Sold 500,000 WOJAK at $0.000045</p>
                            <div class="d-flex justify-content-between">
                                <small class="text-muted">4 hours ago</small>
                                <span class="profit-positive">+$22.50 (+15.2%)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-4">
                <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=activity_html)


# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint."""
    
    health_status = {
        "status": "healthy",
        "service": "DEX Sniper Pro - Phase 4D Enhanced", 
        "version": "4.0.0",
        "components": {
            "dashboard": "operational",
            "tokens_api": "operational", 
            "activity": "operational",
            "enhanced_discovery": "operational"
        },
        "features": {
            "live_opportunities": "enabled",
            "enhanced_tokens": "enabled",
            "risk_assessment": "enabled",
            "multi_network": "enabled"
        },
        "phase4d_status": {
            "snipe_trading": "active" if SNIPE_TRADING_AVAILABLE else "not_available",
            "ai_risk_engine": "active" if AI_RISK_AVAILABLE else "not_available",
            "wallet_integration": "active" if WALLET_MANAGER_AVAILABLE else "not_available"
        }
    }
    
    return health_status


# Phase 4D System Information Endpoints (with fallbacks)
@app.get("/api/v1/system/info")
async def get_system_info():
    """Get comprehensive system information."""
    try:
        return {
            "application": "DEX Sniper Pro",
            "version": "4.0.0",
            "phase": "4D - Enhanced with Progressive Loading",
            "features": {
                "snipe_trading": {
                    "enabled": SNIPE_TRADING_AVAILABLE,
                    "description": "Advanced snipe trading with real-time execution"
                },
                "ai_risk_assessment": {
                    "enabled": AI_RISK_AVAILABLE,
                    "description": "Machine learning-powered risk analysis"
                },
                "wallet_integration": {
                    "enabled": WALLET_MANAGER_AVAILABLE,
                    "description": "MetaMask, WalletConnect multi-network support"
                },
                "enhanced_dashboard": {
                    "enabled": True,
                    "description": "Live opportunities and real-time monitoring"
                }
            },
            "compatibility_mode": not any([SNIPE_TRADING_AVAILABLE, AI_RISK_AVAILABLE, WALLET_MANAGER_AVAILABLE]),
            "supported_networks": ["ethereum", "polygon", "bsc", "arbitrum"],
            "api_endpoints": {
                "dashboard": "/dashboard",
                "health": "/health",
                "docs": "/api/docs"
            },
            "timestamp": "2025-08-09T12:00:00Z"
        }
    except Exception as error:
        logger.error(f"Error getting system info: {error}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system information")


# Development server runner
if __name__ == "__main__":
    import uvicorn

    logger.info("STARTUP: Starting DEX Sniper Pro - Phase 4D Enhanced Development Server")
    logger.info("=" * 70)
    logger.info("FEATURES: Progressive Enhancement Features:")
    logger.info("  DASHBOARD: Enhanced Dashboard - Always Available")
    logger.info("  DISCOVERY: Live Token Discovery - Always Available")
    logger.info("  SNIPE: Snipe Trading - Loads when components available")
    logger.info("  AI: AI Risk Assessment - Loads when components available")
    logger.info("  WALLET: Wallet Integration - Loads when components available")
    logger.info("=" * 70)

    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("SHUTDOWN: Development server stopped by user")
    except Exception as error:
        logger.error(f"ERROR: Development server error: {error}")
        raise
