"""
Updated Main FastAPI Application with WebSocket Integration
File: app/main.py

Enhanced main application with real-time WebSocket functionality for Phase 4C.
Includes live dashboard integration and real-time trading updates.
"""

import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.cors import CORSMiddleware

# Import API routers
from app.api.v1.endpoints import live_trading, dashboard, trading
from app.api.v1.endpoints.websocket import (
    router as websocket_router,
    startup_websocket_manager,
    shutdown_websocket_manager
)

# Import core services
from app.core.trading.trading_engine import TradingEngine
from app.core.wallet.wallet_manager import WalletManager
from app.core.dex.dex_integration import DEXIntegration
from app.core.portfolio.portfolio_manager import PortfolioManager
from app.core.websocket.websocket_manager import websocket_manager
from app.core.integration.live_dashboard_service import live_dashboard_service

# Import utilities
from app.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Global instances
trading_engine_instance = None
templates = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown of services including WebSocket manager.
    """
    # Startup
    logger.info("🚀 Starting DEX Sniper Pro application...")
    
    try:
        # Initialize core services
        await initialize_trading_engine()
        
        # Start WebSocket manager
        await startup_websocket_manager()
        
        # Start live dashboard service
        await live_dashboard_service.start()
        
        # Connect services
        if trading_engine_instance:
            live_dashboard_service.set_trading_engine(trading_engine_instance)
        
        logger.info("✅ Application startup complete")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down DEX Sniper Pro application...")
    
    try:
        # Stop live dashboard service
        await live_dashboard_service.stop()
        
        # Stop WebSocket manager
        await shutdown_websocket_manager()
        
        # Stop trading engine
        if trading_engine_instance:
            # TradingEngine doesn't have a stop method, just stop trading if running
            if hasattr(trading_engine_instance, 'is_running') and trading_engine_instance.is_running:
                try:
                    await trading_engine_instance.stop_trading()
                    logger.info("🛑 Trading engine stopped")
                except Exception as e:
                    logger.warning(f"Error stopping trading engine: {e}")
            else:
                logger.info("🛑 Trading engine was not running")
        
        logger.info("✅ Application shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Application shutdown error: {e}")


# Create FastAPI application with lifespan management
app = FastAPI(
    title="DEX Sniper Pro - Live Trading Bot",
    description="Automated crypto trading platform with real-time dashboard",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for WebSocket and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates_path = Path("frontend/templates")
if templates_path.exists():
    templates = Jinja2Templates(directory=str(templates_path))
else:
    logger.warning("Templates directory not found")

# Mount static files
static_path = Path("frontend/static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Mount dashboard static files
dashboard_path = Path("dashboard")
if dashboard_path.exists():
    app.mount("/dashboard-static", StaticFiles(directory=str(dashboard_path)), name="dashboard")


async def initialize_trading_engine():
    """Initialize the trading engine and related services."""
    global trading_engine_instance
    
    try:
        logger.info("🔧 Initializing trading engine...")
        
        # Create trading engine with default network
        from app.core.wallet.wallet_manager import NetworkType
        trading_engine_instance = TradingEngine(network=NetworkType.ETHEREUM)
        
        # Initialize components
        wallet_manager = WalletManager(network=NetworkType.ETHEREUM)
        
        # Initialize the trading engine with components
        await trading_engine_instance.initialize(
            wallet_manager=wallet_manager
        )
        
        logger.info("✅ Trading engine initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize trading engine: {e}")
        trading_engine_instance = None


# Include API routers
app.include_router(live_trading.router, prefix="/api/v1", tags=["Live Trading"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(trading.router, prefix="/api/v1", tags=["Trading"])
app.include_router(websocket_router, prefix="/api/v1", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "message": "🤖 DEX Sniper Pro - Live Trading Bot with Real-time Dashboard",
        "version": "4.0.0",
        "phase": "4C - Live Dashboard Integration",
        "status": "operational",
        "features": {
            "live_trading": True,
            "real_time_dashboard": True,
            "websocket_updates": True,
            "multi_chain_support": True,
            "ai_risk_assessment": True
        },
        "endpoints": {
            "dashboard": "/dashboard",
            "api_docs": "/docs",
            "trading_api": "/api/v1/live-trading",
            "websocket": "/api/v1/ws",
            "health": "/health"
        }
    }


@app.get("/dashboard")
async def serve_dashboard(request: Request):
    """Serve the main dashboard with integrated live WebSocket functionality."""
    try:
        logger.info("📊 Serving main dashboard with live integration")
        
        # Return the integrated live dashboard directly
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DEX Sniper Pro - Live Trading Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
            <style>
                body {
                    background-color: #0a0e27;
                    color: #ffffff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                .status-dot {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    display: inline-block;
                    margin-right: 8px;
                }
                .status-success { background-color: #28a745; }
                .status-warning { background-color: #ffc107; }
                .status-danger { background-color: #dc3545; }
                .card {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    border: none;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                .metric-card {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: transform 0.3s ease;
                }
                .metric-card:hover {
                    transform: translateY(-5px);
                }
                .metric-value {
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: #00d4ff;
                }
                .metric-change {
                    font-size: 0.9rem;
                }
                .positive { color: #28a745; }
                .negative { color: #dc3545; }
                .pulse {
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.7; }
                    100% { opacity: 1; }
                }
                .log-entry {
                    background: rgba(0, 0, 0, 0.3);
                    border-left: 4px solid #00d4ff;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 0 5px 5px 0;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                }
                .navbar {
                    background: rgba(0, 0, 0, 0.8) !important;
                    backdrop-filter: blur(10px);
                }
            </style>
        </head>
        <body>
            <!-- Navigation -->
            <nav class="navbar navbar-expand-lg navbar-dark">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#">
                        <i class="bi bi-robot"></i> DEX Sniper Pro
                    </a>
                    <div class="d-flex align-items-center">
                        <span class="me-3">
                            <span id="connection-status" class="status-dot status-warning"></span>
                            <span id="connection-text">Connecting...</span>
                        </span>
                        <span class="badge bg-success">Phase 4C Live</span>
                    </div>
                </div>
            </nav>

            <div class="container-fluid mt-4">
                <div class="row">
                    <!-- Main Metrics -->
                    <div class="col-md-3 mb-4">
                        <div class="card metric-card h-100">
                            <div class="card-body text-center">
                                <i class="bi bi-wallet2 text-primary fs-1"></i>
                                <h5 class="card-title mt-2">Portfolio Value</h5>
                                <div id="portfolio-value" class="metric-value">$125,826.86</div>
                                <div id="portfolio-change" class="metric-change positive">
                                    <i class="bi bi-arrow-up"></i> +$3,241.87 (2.64%)
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3 mb-4">
                        <div class="card metric-card h-100">
                            <div class="card-body text-center">
                                <i class="bi bi-graph-up text-success fs-1"></i>
                                <h5 class="card-title mt-2">Trades Today</h5>
                                <div id="trades-today" class="metric-value">15</div>
                                <div id="success-rate" class="metric-change positive">
                                    <i class="bi bi-check-circle"></i> 84.2% Success Rate
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3 mb-4">
                        <div class="card metric-card h-100">
                            <div class="card-body text-center">
                                <i class="bi bi-search text-warning fs-1"></i>
                                <h5 class="card-title mt-2">Opportunities</h5>
                                <div id="opportunities" class="metric-value">47</div>
                                <div class="metric-change">
                                    <i class="bi bi-clock"></i> Last found 2m ago
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-3 mb-4">
                        <div class="card metric-card h-100">
                            <div class="card-body text-center">
                                <i class="bi bi-lightning text-info fs-1"></i>
                                <h5 class="card-title mt-2">Active Strategies</h5>
                                <div id="active-strategies" class="metric-value">3</div>
                                <div class="metric-change positive">
                                    <i class="bi bi-play-fill"></i> All Running
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <!-- Live Activity Feed -->
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">
                                    <i class="bi bi-activity"></i> Live Activity Feed
                                    <span id="activity-pulse" class="status-dot status-success pulse ms-2"></span>
                                </h5>
                            </div>
                            <div class="card-body">
                                <div id="activity-log" style="height: 400px; overflow-y: auto;">
                                    <!-- Real-time activity will be populated here -->
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- System Status -->
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">
                                    <i class="bi bi-gear"></i> System Status
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <strong>Trading Engine:</strong>
                                    <span id="engine-status" class="badge bg-success">Running</span>
                                </div>
                                <div class="mb-3">
                                    <strong>WebSocket:</strong>
                                    <span id="ws-status" class="badge bg-success">Connected</span>
                                </div>
                                <div class="mb-3">
                                    <strong>Blockchain:</strong>
                                    <span class="badge bg-success">ETH</span>
                                    <span class="badge bg-success">POLY</span>
                                    <span class="badge bg-success">BSC</span>
                                </div>
                                <div class="mb-3">
                                    <strong>Memory:</strong> <span id="memory-usage">45.2%</span>
                                </div>
                                <div class="mb-3">
                                    <strong>CPU:</strong> <span id="cpu-usage">23.8%</span>
                                </div>
                                <div class="mb-3">
                                    <strong>Uptime:</strong> <span id="system-uptime">24h 30m</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Quick Actions -->
                        <div class="card mt-3">
                            <div class="card-header">
                                <h5 class="mb-0">Quick Actions</h5>
                            </div>
                            <div class="card-body">
                                <button id="start-trading-btn" class="btn btn-success btn-sm w-100 mb-2">
                                    <i class="bi bi-play"></i> Start Trading
                                </button>
                                <button id="stop-trading-btn" class="btn btn-danger btn-sm w-100 mb-2">
                                    <i class="bi bi-stop"></i> Stop Trading
                                </button>
                                <button id="refresh-data-btn" class="btn btn-info btn-sm w-100">
                                    <i class="bi bi-arrow-clockwise"></i> Refresh Data
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                class LiveDashboard {
                    constructor() {
                        this.ws = null;
                        this.clientId = 'dashboard_' + Math.random().toString(36).substr(2, 9);
                        this.isConnected = false;
                        this.reconnectAttempts = 0;
                        this.maxReconnectAttempts = 5;
                        
                        this.initializeWebSocket();
                        this.bindEvents();
                    }
                    
                    initializeWebSocket() {
                        try {
                            const wsUrl = `ws://${window.location.host}/api/v1/ws/dashboard/${this.clientId}`;
                            console.log('🔌 Connecting to WebSocket:', wsUrl);
                            
                            this.ws = new WebSocket(wsUrl);
                            
                            this.ws.onopen = () => {
                                console.log('✅ WebSocket connected');
                                this.isConnected = true;
                                this.reconnectAttempts = 0;
                                this.updateConnectionStatus(true);
                                this.addLogEntry('🔌 Connected to live data feed', 'success');
                            };
                            
                            this.ws.onmessage = (event) => {
                                try {
                                    const data = JSON.parse(event.data);
                                    this.handleWebSocketMessage(data);
                                } catch (e) {
                                    console.error('Error parsing WebSocket message:', e);
                                }
                            };
                            
                            this.ws.onclose = () => {
                                console.log('🔌 WebSocket disconnected');
                                this.isConnected = false;
                                this.updateConnectionStatus(false);
                                this.addLogEntry('🔌 Disconnected from live data feed', 'warning');
                                this.attemptReconnect();
                            };
                            
                            this.ws.onerror = (error) => {
                                console.error('❌ WebSocket error:', error);
                                this.addLogEntry('❌ WebSocket connection error', 'error');
                            };
                            
                        } catch (error) {
                            console.error('Failed to initialize WebSocket:', error);
                            this.addLogEntry('❌ Failed to initialize WebSocket', 'error');
                        }
                    }
                    
                    handleWebSocketMessage(data) {
                        console.log('📨 Received:', data);
                        
                        switch (data.type) {
                            case 'portfolio_update':
                                this.updatePortfolioMetrics(data.data);
                                break;
                            case 'trading_status':
                                this.updateTradingMetrics(data.data);
                                break;
                            case 'trade_execution':
                                this.handleTradeExecution(data.data);
                                break;
                            case 'token_discovery':
                                this.handleTokenDiscovery(data.data);
                                break;
                            case 'arbitrage_alert':
                                this.handleArbitrageAlert(data.data);
                                break;
                            case 'system_health':
                                this.updateSystemHealth(data.data);
                                break;
                            case 'heartbeat':
                                this.handleHeartbeat(data.data);
                                break;
                            default:
                                console.log('Unknown message type:', data.type);
                        }
                    }
                    
                    updatePortfolioMetrics(data) {
                        if (data.portfolio) {
                            const portfolio = data.portfolio;
                            document.getElementById('portfolio-value').textContent = 
                                '


@app.get("/dashboard/live")
async def serve_live_dashboard():
    """Serve enhanced live dashboard with WebSocket integration."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro - Live Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {
                background-color: #0a0e27;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .status-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            .status-success { background-color: #28a745; }
            .status-warning { background-color: #ffc107; }
            .status-danger { background-color: #dc3545; }
            .card {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border: none;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .metric-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: bold;
                color: #00d4ff;
            }
            .metric-change {
                font-size: 0.9rem;
            }
            .positive { color: #28a745; }
            .negative { color: #dc3545; }
            .pulse {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            .log-entry {
                background: rgba(0, 0, 0, 0.3);
                border-left: 4px solid #00d4ff;
                padding: 10px;
                margin: 5px 0;
                border-radius: 0 5px 5px 0;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }
            .navbar {
                background: rgba(0, 0, 0, 0.8) !important;
                backdrop-filter: blur(10px);
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-robot"></i> DEX Sniper Pro
                </a>
                <div class="d-flex align-items-center">
                    <span class="me-3">
                        <span id="connection-status" class="status-dot status-warning"></span>
                        <span id="connection-text">Connecting...</span>
                    </span>
                    <span class="badge bg-success">Phase 4C Live</span>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <div class="row">
                <!-- Main Metrics -->
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-wallet2 text-primary fs-1"></i>
                            <h5 class="card-title mt-2">Portfolio Value</h5>
                            <div id="portfolio-value" class="metric-value">$125,826.86</div>
                            <div id="portfolio-change" class="metric-change positive">
                                <i class="bi bi-arrow-up"></i> +$3,241.87 (2.64%)
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-graph-up text-success fs-1"></i>
                            <h5 class="card-title mt-2">Trades Today</h5>
                            <div id="trades-today" class="metric-value">15</div>
                            <div id="success-rate" class="metric-change positive">
                                <i class="bi bi-check-circle"></i> 84.2% Success Rate
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-search text-warning fs-1"></i>
                            <h5 class="card-title mt-2">Opportunities</h5>
                            <div id="opportunities" class="metric-value">47</div>
                            <div class="metric-change">
                                <i class="bi bi-clock"></i> Last found 2m ago
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-lightning text-info fs-1"></i>
                            <h5 class="card-title mt-2">Active Strategies</h5>
                            <div id="active-strategies" class="metric-value">3</div>
                            <div class="metric-change positive">
                                <i class="bi bi-play-fill"></i> All Running
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Live Activity Feed -->
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-activity"></i> Live Activity Feed
                                <span id="activity-pulse" class="status-dot status-success pulse ms-2"></span>
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="activity-log" style="height: 400px; overflow-y: auto;">
                                <!-- Real-time activity will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- System Status -->
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-gear"></i> System Status
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong>Trading Engine:</strong>
                                <span id="engine-status" class="badge bg-success">Running</span>
                            </div>
                            <div class="mb-3">
                                <strong>WebSocket:</strong>
                                <span id="ws-status" class="badge bg-success">Connected</span>
                            </div>
                            <div class="mb-3">
                                <strong>Blockchain:</strong>
                                <span class="badge bg-success">ETH</span>
                                <span class="badge bg-success">POLY</span>
                                <span class="badge bg-success">BSC</span>
                            </div>
                            <div class="mb-3">
                                <strong>Memory:</strong> 45.2%
                            </div>
                            <div class="mb-3">
                                <strong>CPU:</strong> 23.8%
                            </div>
                            <div class="mb-3">
                                <strong>Uptime:</strong> 24h 30m
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Actions -->
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5 class="mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <button id="start-trading" class="btn btn-success btn-sm w-100 mb-2">
                                <i class="bi bi-play"></i> Start Trading
                            </button>
                            <button id="stop-trading" class="btn btn-danger btn-sm w-100 mb-2">
                                <i class="bi bi-stop"></i> Stop Trading
                            </button>
                            <button id="refresh-data" class="btn btn-info btn-sm w-100">
                                <i class="bi bi-arrow-clockwise"></i> Refresh Data
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            class LiveDashboard {
                constructor() {
                    this.ws = null;
                    this.clientId = 'dashboard_' + Math.random().toString(36).substr(2, 9);
                    this.isConnected = false;
                    this.reconnectAttempts = 0;
                    this.maxReconnectAttempts = 5;
                    
                    this.initializeWebSocket();
                    this.bindEvents();
                }
                
                initializeWebSocket() {
                    try {
                        const wsUrl = `ws://${window.location.host}/api/v1/ws/dashboard/${this.clientId}`;
                        console.log('🔌 Connecting to WebSocket:', wsUrl);
                        
                        this.ws = new WebSocket(wsUrl);
                        
                        this.ws.onopen = () => {
                            console.log('✅ WebSocket connected');
                            this.isConnected = true;
                            this.reconnectAttempts = 0;
                            this.updateConnectionStatus(true);
                            this.addLogEntry('🔌 Connected to live data feed', 'success');
                        };
                        
                        this.ws.onmessage = (event) => {
                            try {
                                const data = JSON.parse(event.data);
                                this.handleWebSocketMessage(data);
                            } catch (e) {
                                console.error('Error parsing WebSocket message:', e);
                            }
                        };
                        
                        this.ws.onclose = () => {
                            console.log('🔌 WebSocket disconnected');
                            this.isConnected = false;
                            this.updateConnectionStatus(false);
                            this.addLogEntry('🔌 Disconnected from live data feed', 'warning');
                            this.attemptReconnect();
                        };
                        
                        this.ws.onerror = (error) => {
                            console.error('❌ WebSocket error:', error);
                            this.addLogEntry('❌ WebSocket connection error', 'error');
                        };
                        
                    } catch (error) {
                        console.error('Failed to initialize WebSocket:', error);
                        this.addLogEntry('❌ Failed to initialize WebSocket', 'error');
                    }
                }
                
                handleWebSocketMessage(data) {
                    console.log('📨 Received:', data);
                    
                    switch (data.type) {
                        case 'portfolio_update':
                            this.updatePortfolioMetrics(data.data);
                            break;
                        case 'trading_status':
                            this.updateTradingMetrics(data.data);
                            break;
                        case 'trade_execution':
                            this.handleTradeExecution(data.data);
                            break;
                        case 'token_discovery':
                            this.handleTokenDiscovery(data.data);
                            break;
                        case 'arbitrage_alert':
                            this.handleArbitrageAlert(data.data);
                            break;
                        case 'system_health':
                            this.updateSystemHealth(data.data);
                            break;
                        case 'heartbeat':
                            this.handleHeartbeat(data.data);
                            break;
                        default:
                            console.log('Unknown message type:', data.type);
                    }
                }
                
                updatePortfolioMetrics(data) {
                    if (data.portfolio) {
                        const portfolio = data.portfolio;
                        document.getElementById('portfolio-value').textContent = 
                            ' + this.formatNumber(portfolio.total_value);
                    }
                    
                    if (data.metrics) {
                        const metrics = data.metrics;
                        if (metrics.daily_change !== undefined) {
                            const changeEl = document.getElementById('portfolio-change');
                            const isPositive = metrics.daily_change >= 0;
                            changeEl.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
                            changeEl.innerHTML = `
                                <i class="bi bi-arrow-${isPositive ? 'up' : 'down'}"></i> 
                                ${isPositive ? '+' : ''}${this.formatNumber(Math.abs(metrics.daily_change))} 
                                (${metrics.daily_change_percent?.toFixed(2) || '0.00'}%)
                            `;
                        }
                    }
                    
                    this.addLogEntry('💰 Portfolio updated', 'info');
                }
                
                updateTradingMetrics(data) {
                    if (data.total_trades_today !== undefined) {
                        document.getElementById('trades-today').textContent = data.total_trades_today;
                    }
                    
                    if (data.success_rate !== undefined) {
                        document.getElementById('success-rate').innerHTML = `
                            <i class="bi bi-check-circle"></i> ${data.success_rate.toFixed(1)}% Success Rate
                        `;
                    }
                    
                    if (data.active_strategies) {
                        document.getElementById('active-strategies').textContent = data.active_strategies.length;
                    }
                    
                    this.addLogEntry('📊 Trading metrics updated', 'info');
                }
                
                handleTradeExecution(data) {
                    const trade = data.trade || data;
                    this.addLogEntry(
                        `🔄 Trade executed: ${trade.symbol || 'Unknown'} - ${trade.status || 'Unknown'}`,
                        trade.status === 'success' ? 'success' : 'warning'
                    );
                }
                
                handleTokenDiscovery(data) {
                    const token = data.token || data;
                    this.addLogEntry(
                        `🎯 New token discovered: ${token.symbol || 'Unknown'} (${token.address?.slice(0, 10) || ''}...)`,
                        'info'
                    );
                    
                    // Update opportunities counter
                    const currentOps = parseInt(document.getElementById('opportunities').textContent) || 0;
                    document.getElementById('opportunities').textContent = currentOps + 1;
                }
                
                handleArbitrageAlert(data) {
                    const opportunity = data.opportunity || data;
                    this.addLogEntry(
                        `💰 Arbitrage opportunity: ${opportunity.profit_percentage || '0'}% profit potential`,
                        'success'
                    );
                }
                
                updateSystemHealth(data) {
                    if (data.status) {
                        const statusBadge = document.getElementById('engine-status');
                        statusBadge.textContent = data.status === 'healthy' ? 'Running' : 'Issues';
                        statusBadge.className = `badge ${data.status === 'healthy' ? 'bg-success' : 'bg-warning'}`;
                    }
                }
                
                handleHeartbeat(data) {
                    // Update last heartbeat time
                    console.log('💓 Heartbeat received');
                }
                
                updateConnectionStatus(connected) {
                    const statusDot = document.getElementById('connection-status');
                    const statusText = document.getElementById('connection-text');
                    const wsStatus = document.getElementById('ws-status');
                    
                    if (connected) {
                        statusDot.className = 'status-dot status-success';
                        statusText.textContent = 'Connected';
                        if (wsStatus) wsStatus.textContent = 'Connected';
                        if (wsStatus) wsStatus.className = 'badge bg-success';
                    } else {
                        statusDot.className = 'status-dot status-danger';
                        statusText.textContent = 'Disconnected';
                        if (wsStatus) wsStatus.textContent = 'Disconnected';
                        if (wsStatus) wsStatus.className = 'badge bg-danger';
                    }
                }
                
                attemptReconnect() {
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        console.log(`🔄 Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                        
                        setTimeout(() => {
                            this.initializeWebSocket();
                        }, 2000 * this.reconnectAttempts);
                    } else {
                        console.error('❌ Max reconnection attempts reached');
                        this.addLogEntry('❌ Connection failed - max retries reached', 'error');
                    }
                }
                
                addLogEntry(message, type = 'info') {
                    const logContainer = document.getElementById('activity-log');
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    
                    const timestamp = new Date().toLocaleTimeString();
                    entry.innerHTML = `[${timestamp}] ${message}`;
                    
                    logContainer.appendChild(entry);
                    logContainer.scrollTop = logContainer.scrollHeight;
                    
                    // Remove old entries to prevent memory issues
                    while (logContainer.children.length > 100) {
                        logContainer.removeChild(logContainer.firstChild);
                    }
                }
                
                formatNumber(num) {
                    return new Intl.NumberFormat('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(num);
                }
                
                bindEvents() {
                    // Quick action buttons
                    document.getElementById('start-trading')?.addEventListener('click', () => {
                        this.sendCommand('start_trading');
                        this.addLogEntry('🚀 Starting trading engine...', 'info');
                    });
                    
                    document.getElementById('stop-trading')?.addEventListener('click', () => {
                        this.sendCommand('stop_trading');
                        this.addLogEntry('🛑 Stopping trading engine...', 'warning');
                    });
                    
                    document.getElementById('refresh-data')?.addEventListener('click', () => {
                        this.sendCommand('refresh_data');
                        this.addLogEntry('🔄 Refreshing data...', 'info');
                    });
                }
                
                sendCommand(command) {
                    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({
                            type: 'command',
                            data: { command: command }
                        }));
                    } else {
                        this.addLogEntry('❌ Cannot send command - not connected', 'error');
                    }
                }
            }
            
            // Initialize dashboard when page loads
            document.addEventListener('DOMContentLoaded', () => {
                console.log('🚀 Initializing Live Dashboard...');
                new LiveDashboard();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with WebSocket status."""
    global trading_engine_instance
    
    try:
        websocket_status = "running" if websocket_manager.is_running else "stopped"
        active_connections = len(websocket_manager.connections) if websocket_manager.connections else 0
        live_service_status = "running" if live_dashboard_service.is_running else "stopped"
        
        return {
            "status": "healthy",
            "version": "4.0.0",
            "phase": "4C - Live Dashboard Integration",
            "services": {
                "trading_engine": trading_engine_instance is not None,
                "websocket_manager": websocket_status,
                "live_dashboard_service": live_service_status,
                "dashboard": Path("frontend/templates/pages/dashboard.html").exists(),
                "static_files": Path("frontend/static").exists()
            },
            "websocket": {
                "active_connections": active_connections,
                "message_types": list(websocket_manager.MESSAGE_TYPES.keys()) if hasattr(websocket_manager, 'MESSAGE_TYPES') else []
            },
            "features": [
                "Real-time WebSocket updates",
                "Live portfolio tracking",
                "Trading execution alerts",
                "System health monitoring",
                "Multi-chain support"
            ],
            "message": "DEX Sniper Pro is operational with live dashboard integration"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "partial",
            "error": str(e),
            "message": "Some services may be unavailable"
        }


def get_trading_engine():
    """Get the global trading engine instance."""
    global trading_engine_instance
    if trading_engine_instance is None:
        raise HTTPException(status_code=503, detail="Trading engine not initialized")
    return trading_engine_instance


# Make trading engine available to endpoints
live_trading.set_trading_engine_getter(get_trading_engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) + this.formatNumber(portfolio.total_value);
                        }
                        
                        if (data.metrics) {
                            const metrics = data.metrics;
                            if (metrics.daily_change !== undefined) {
                                const changeEl = document.getElementById('portfolio-change');
                                const isPositive = metrics.daily_change >= 0;
                                changeEl.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
                                changeEl.innerHTML = `
                                    <i class="bi bi-arrow-${isPositive ? 'up' : 'down'}"></i> 
                                    ${isPositive ? '+' : ''}${this.formatNumber(Math.abs(metrics.daily_change))} 
                                    (${metrics.daily_change_percent?.toFixed(2) || '0.00'}%)
                                `;
                            }
                        }
                        
                        this.addLogEntry('💰 Portfolio updated', 'info');
                    }
                    
                    updateTradingMetrics(data) {
                        if (data.total_trades_today !== undefined) {
                            document.getElementById('trades-today').textContent = data.total_trades_today;
                        }
                        
                        if (data.success_rate !== undefined) {
                            document.getElementById('success-rate').innerHTML = `
                                <i class="bi bi-check-circle"></i> ${data.success_rate.toFixed(1)}% Success Rate
                            `;
                        }
                        
                        if (data.active_strategies) {
                            document.getElementById('active-strategies').textContent = data.active_strategies.length;
                        }
                        
                        this.addLogEntry('📊 Trading metrics updated', 'info');
                    }
                    
                    handleTradeExecution(data) {
                        const trade = data.trade || data;
                        this.addLogEntry(
                            `🔄 Trade executed: ${trade.symbol || 'Unknown'} - ${trade.status || 'Unknown'}`,
                            trade.status === 'success' ? 'success' : 'warning'
                        );
                    }
                    
                    handleTokenDiscovery(data) {
                        const token = data.token || data;
                        this.addLogEntry(
                            `🎯 New token discovered: ${token.symbol || 'Unknown'} (${token.address?.slice(0, 10) || ''}...)`,
                            'info'
                        );
                        
                        // Update opportunities counter
                        const currentOps = parseInt(document.getElementById('opportunities').textContent) || 0;
                        document.getElementById('opportunities').textContent = currentOps + 1;
                    }
                    
                    handleArbitrageAlert(data) {
                        const opportunity = data.opportunity || data;
                        this.addLogEntry(
                            `💰 Arbitrage opportunity: ${opportunity.profit_percentage || '0'}% profit potential`,
                            'success'
                        );
                    }
                    
                    updateSystemHealth(data) {
                        if (data.status) {
                            const statusBadge = document.getElementById('engine-status');
                            statusBadge.textContent = data.status === 'healthy' ? 'Running' : 'Issues';
                            statusBadge.className = `badge ${data.status === 'healthy' ? 'bg-success' : 'bg-warning'}`;
                        }
                        
                        if (data.memory_usage !== undefined) {
                            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
                        }
                        
                        if (data.cpu_usage !== undefined) {
                            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
                        }
                        
                        if (data.uptime) {
                            document.getElementById('system-uptime').textContent = data.uptime;
                        }
                    }
                    
                    handleHeartbeat(data) {
                        console.log('💓 Heartbeat received');
                    }
                    
                    updateConnectionStatus(connected) {
                        const statusDot = document.getElementById('connection-status');
                        const statusText = document.getElementById('connection-text');
                        const wsStatus = document.getElementById('ws-status');
                        
                        if (connected) {
                            statusDot.className = 'status-dot status-success';
                            statusText.textContent = 'Connected';
                            if (wsStatus) wsStatus.textContent = 'Connected';
                            if (wsStatus) wsStatus.className = 'badge bg-success';
                        } else {
                            statusDot.className = 'status-dot status-danger';
                            statusText.textContent = 'Disconnected';
                            if (wsStatus) wsStatus.textContent = 'Disconnected';
                            if (wsStatus) wsStatus.className = 'badge bg-danger';
                        }
                    }
                    
                    attemptReconnect() {
                        if (this.reconnectAttempts < this.maxReconnectAttempts) {
                            this.reconnectAttempts++;
                            console.log(`🔄 Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                            
                            setTimeout(() => {
                                this.initializeWebSocket();
                            }, 2000 * this.reconnectAttempts);
                        } else {
                            console.error('❌ Max reconnection attempts reached');
                            this.addLogEntry('❌ Connection failed - max retries reached', 'error');
                        }
                    }
                    
                    addLogEntry(message, type = 'info') {
                        const logContainer = document.getElementById('activity-log');
                        const entry = document.createElement('div');
                        entry.className = 'log-entry';
                        
                        const timestamp = new Date().toLocaleTimeString();
                        entry.innerHTML = `[${timestamp}] ${message}`;
                        
                        logContainer.appendChild(entry);
                        logContainer.scrollTop = logContainer.scrollHeight;
                        
                        // Remove old entries to prevent memory issues
                        while (logContainer.children.length > 100) {
                            logContainer.removeChild(logContainer.firstChild);
                        }
                    }
                    
                    formatNumber(num) {
                        return new Intl.NumberFormat('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }).format(num);
                    }
                    
                    bindEvents() {
                        // Quick action buttons
                        document.getElementById('start-trading-btn')?.addEventListener('click', () => {
                            this.sendCommand('start_trading');
                            this.addLogEntry('🚀 Starting trading engine...', 'info');
                        });
                        
                        document.getElementById('stop-trading-btn')?.addEventListener('click', () => {
                            this.sendCommand('stop_trading');
                            this.addLogEntry('🛑 Stopping trading engine...', 'warning');
                        });
                        
                        document.getElementById('refresh-data-btn')?.addEventListener('click', () => {
                            this.sendCommand('refresh_data');
                            this.addLogEntry('🔄 Refreshing data...', 'info');
                        });
                    }
                    
                    sendCommand(command) {
                        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                            this.ws.send(JSON.stringify({
                                type: 'command',
                                data: { command: command }
                            }));
                        } else {
                            this.addLogEntry('❌ Cannot send command - not connected', 'error');
                        }
                    }
                }
                
                // Initialize dashboard when page loads
                document.addEventListener('DOMContentLoaded', () => {
                    console.log('🚀 Initializing Live Dashboard...');
                    new LiveDashboard();
                });
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {e}")


@app.get("/dashboard/live")
async def serve_live_dashboard():
    """Serve enhanced live dashboard with WebSocket integration."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro - Live Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {
                background-color: #0a0e27;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .status-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            .status-success { background-color: #28a745; }
            .status-warning { background-color: #ffc107; }
            .status-danger { background-color: #dc3545; }
            .card {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border: none;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .metric-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: bold;
                color: #00d4ff;
            }
            .metric-change {
                font-size: 0.9rem;
            }
            .positive { color: #28a745; }
            .negative { color: #dc3545; }
            .pulse {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            .log-entry {
                background: rgba(0, 0, 0, 0.3);
                border-left: 4px solid #00d4ff;
                padding: 10px;
                margin: 5px 0;
                border-radius: 0 5px 5px 0;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }
            .navbar {
                background: rgba(0, 0, 0, 0.8) !important;
                backdrop-filter: blur(10px);
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-robot"></i> DEX Sniper Pro
                </a>
                <div class="d-flex align-items-center">
                    <span class="me-3">
                        <span id="connection-status" class="status-dot status-warning"></span>
                        <span id="connection-text">Connecting...</span>
                    </span>
                    <span class="badge bg-success">Phase 4C Live</span>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <div class="row">
                <!-- Main Metrics -->
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-wallet2 text-primary fs-1"></i>
                            <h5 class="card-title mt-2">Portfolio Value</h5>
                            <div id="portfolio-value" class="metric-value">$125,826.86</div>
                            <div id="portfolio-change" class="metric-change positive">
                                <i class="bi bi-arrow-up"></i> +$3,241.87 (2.64%)
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-graph-up text-success fs-1"></i>
                            <h5 class="card-title mt-2">Trades Today</h5>
                            <div id="trades-today" class="metric-value">15</div>
                            <div id="success-rate" class="metric-change positive">
                                <i class="bi bi-check-circle"></i> 84.2% Success Rate
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-search text-warning fs-1"></i>
                            <h5 class="card-title mt-2">Opportunities</h5>
                            <div id="opportunities" class="metric-value">47</div>
                            <div class="metric-change">
                                <i class="bi bi-clock"></i> Last found 2m ago
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-4">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-lightning text-info fs-1"></i>
                            <h5 class="card-title mt-2">Active Strategies</h5>
                            <div id="active-strategies" class="metric-value">3</div>
                            <div class="metric-change positive">
                                <i class="bi bi-play-fill"></i> All Running
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Live Activity Feed -->
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-activity"></i> Live Activity Feed
                                <span id="activity-pulse" class="status-dot status-success pulse ms-2"></span>
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="activity-log" style="height: 400px; overflow-y: auto;">
                                <!-- Real-time activity will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- System Status -->
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-gear"></i> System Status
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong>Trading Engine:</strong>
                                <span id="engine-status" class="badge bg-success">Running</span>
                            </div>
                            <div class="mb-3">
                                <strong>WebSocket:</strong>
                                <span id="ws-status" class="badge bg-success">Connected</span>
                            </div>
                            <div class="mb-3">
                                <strong>Blockchain:</strong>
                                <span class="badge bg-success">ETH</span>
                                <span class="badge bg-success">POLY</span>
                                <span class="badge bg-success">BSC</span>
                            </div>
                            <div class="mb-3">
                                <strong>Memory:</strong> 45.2%
                            </div>
                            <div class="mb-3">
                                <strong>CPU:</strong> 23.8%
                            </div>
                            <div class="mb-3">
                                <strong>Uptime:</strong> 24h 30m
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Actions -->
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5 class="mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <button id="start-trading" class="btn btn-success btn-sm w-100 mb-2">
                                <i class="bi bi-play"></i> Start Trading
                            </button>
                            <button id="stop-trading" class="btn btn-danger btn-sm w-100 mb-2">
                                <i class="bi bi-stop"></i> Stop Trading
                            </button>
                            <button id="refresh-data" class="btn btn-info btn-sm w-100">
                                <i class="bi bi-arrow-clockwise"></i> Refresh Data
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            class LiveDashboard {
                constructor() {
                    this.ws = null;
                    this.clientId = 'dashboard_' + Math.random().toString(36).substr(2, 9);
                    this.isConnected = false;
                    this.reconnectAttempts = 0;
                    this.maxReconnectAttempts = 5;
                    
                    this.initializeWebSocket();
                    this.bindEvents();
                }
                
                initializeWebSocket() {
                    try {
                        const wsUrl = `ws://${window.location.host}/api/v1/ws/dashboard/${this.clientId}`;
                        console.log('🔌 Connecting to WebSocket:', wsUrl);
                        
                        this.ws = new WebSocket(wsUrl);
                        
                        this.ws.onopen = () => {
                            console.log('✅ WebSocket connected');
                            this.isConnected = true;
                            this.reconnectAttempts = 0;
                            this.updateConnectionStatus(true);
                            this.addLogEntry('🔌 Connected to live data feed', 'success');
                        };
                        
                        this.ws.onmessage = (event) => {
                            try {
                                const data = JSON.parse(event.data);
                                this.handleWebSocketMessage(data);
                            } catch (e) {
                                console.error('Error parsing WebSocket message:', e);
                            }
                        };
                        
                        this.ws.onclose = () => {
                            console.log('🔌 WebSocket disconnected');
                            this.isConnected = false;
                            this.updateConnectionStatus(false);
                            this.addLogEntry('🔌 Disconnected from live data feed', 'warning');
                            this.attemptReconnect();
                        };
                        
                        this.ws.onerror = (error) => {
                            console.error('❌ WebSocket error:', error);
                            this.addLogEntry('❌ WebSocket connection error', 'error');
                        };
                        
                    } catch (error) {
                        console.error('Failed to initialize WebSocket:', error);
                        this.addLogEntry('❌ Failed to initialize WebSocket', 'error');
                    }
                }
                
                handleWebSocketMessage(data) {
                    console.log('📨 Received:', data);
                    
                    switch (data.type) {
                        case 'portfolio_update':
                            this.updatePortfolioMetrics(data.data);
                            break;
                        case 'trading_status':
                            this.updateTradingMetrics(data.data);
                            break;
                        case 'trade_execution':
                            this.handleTradeExecution(data.data);
                            break;
                        case 'token_discovery':
                            this.handleTokenDiscovery(data.data);
                            break;
                        case 'arbitrage_alert':
                            this.handleArbitrageAlert(data.data);
                            break;
                        case 'system_health':
                            this.updateSystemHealth(data.data);
                            break;
                        case 'heartbeat':
                            this.handleHeartbeat(data.data);
                            break;
                        default:
                            console.log('Unknown message type:', data.type);
                    }
                }
                
                updatePortfolioMetrics(data) {
                    if (data.portfolio) {
                        const portfolio = data.portfolio;
                        document.getElementById('portfolio-value').textContent = 
                            ' + this.formatNumber(portfolio.total_value);
                    }
                    
                    if (data.metrics) {
                        const metrics = data.metrics;
                        if (metrics.daily_change !== undefined) {
                            const changeEl = document.getElementById('portfolio-change');
                            const isPositive = metrics.daily_change >= 0;
                            changeEl.className = `metric-change ${isPositive ? 'positive' : 'negative'}`;
                            changeEl.innerHTML = `
                                <i class="bi bi-arrow-${isPositive ? 'up' : 'down'}"></i> 
                                ${isPositive ? '+' : ''}${this.formatNumber(Math.abs(metrics.daily_change))} 
                                (${metrics.daily_change_percent?.toFixed(2) || '0.00'}%)
                            `;
                        }
                    }
                    
                    this.addLogEntry('💰 Portfolio updated', 'info');
                }
                
                updateTradingMetrics(data) {
                    if (data.total_trades_today !== undefined) {
                        document.getElementById('trades-today').textContent = data.total_trades_today;
                    }
                    
                    if (data.success_rate !== undefined) {
                        document.getElementById('success-rate').innerHTML = `
                            <i class="bi bi-check-circle"></i> ${data.success_rate.toFixed(1)}% Success Rate
                        `;
                    }
                    
                    if (data.active_strategies) {
                        document.getElementById('active-strategies').textContent = data.active_strategies.length;
                    }
                    
                    this.addLogEntry('📊 Trading metrics updated', 'info');
                }
                
                handleTradeExecution(data) {
                    const trade = data.trade || data;
                    this.addLogEntry(
                        `🔄 Trade executed: ${trade.symbol || 'Unknown'} - ${trade.status || 'Unknown'}`,
                        trade.status === 'success' ? 'success' : 'warning'
                    );
                }
                
                handleTokenDiscovery(data) {
                    const token = data.token || data;
                    this.addLogEntry(
                        `🎯 New token discovered: ${token.symbol || 'Unknown'} (${token.address?.slice(0, 10) || ''}...)`,
                        'info'
                    );
                    
                    // Update opportunities counter
                    const currentOps = parseInt(document.getElementById('opportunities').textContent) || 0;
                    document.getElementById('opportunities').textContent = currentOps + 1;
                }
                
                handleArbitrageAlert(data) {
                    const opportunity = data.opportunity || data;
                    this.addLogEntry(
                        `💰 Arbitrage opportunity: ${opportunity.profit_percentage || '0'}% profit potential`,
                        'success'
                    );
                }
                
                updateSystemHealth(data) {
                    if (data.status) {
                        const statusBadge = document.getElementById('engine-status');
                        statusBadge.textContent = data.status === 'healthy' ? 'Running' : 'Issues';
                        statusBadge.className = `badge ${data.status === 'healthy' ? 'bg-success' : 'bg-warning'}`;
                    }
                }
                
                handleHeartbeat(data) {
                    // Update last heartbeat time
                    console.log('💓 Heartbeat received');
                }
                
                updateConnectionStatus(connected) {
                    const statusDot = document.getElementById('connection-status');
                    const statusText = document.getElementById('connection-text');
                    const wsStatus = document.getElementById('ws-status');
                    
                    if (connected) {
                        statusDot.className = 'status-dot status-success';
                        statusText.textContent = 'Connected';
                        if (wsStatus) wsStatus.textContent = 'Connected';
                        if (wsStatus) wsStatus.className = 'badge bg-success';
                    } else {
                        statusDot.className = 'status-dot status-danger';
                        statusText.textContent = 'Disconnected';
                        if (wsStatus) wsStatus.textContent = 'Disconnected';
                        if (wsStatus) wsStatus.className = 'badge bg-danger';
                    }
                }
                
                attemptReconnect() {
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        console.log(`🔄 Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                        
                        setTimeout(() => {
                            this.initializeWebSocket();
                        }, 2000 * this.reconnectAttempts);
                    } else {
                        console.error('❌ Max reconnection attempts reached');
                        this.addLogEntry('❌ Connection failed - max retries reached', 'error');
                    }
                }
                
                addLogEntry(message, type = 'info') {
                    const logContainer = document.getElementById('activity-log');
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    
                    const timestamp = new Date().toLocaleTimeString();
                    entry.innerHTML = `[${timestamp}] ${message}`;
                    
                    logContainer.appendChild(entry);
                    logContainer.scrollTop = logContainer.scrollHeight;
                    
                    // Remove old entries to prevent memory issues
                    while (logContainer.children.length > 100) {
                        logContainer.removeChild(logContainer.firstChild);
                    }
                }
                
                formatNumber(num) {
                    return new Intl.NumberFormat('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(num);
                }
                
                bindEvents() {
                    // Quick action buttons
                    document.getElementById('start-trading')?.addEventListener('click', () => {
                        this.sendCommand('start_trading');
                        this.addLogEntry('🚀 Starting trading engine...', 'info');
                    });
                    
                    document.getElementById('stop-trading')?.addEventListener('click', () => {
                        this.sendCommand('stop_trading');
                        this.addLogEntry('🛑 Stopping trading engine...', 'warning');
                    });
                    
                    document.getElementById('refresh-data')?.addEventListener('click', () => {
                        this.sendCommand('refresh_data');
                        this.addLogEntry('🔄 Refreshing data...', 'info');
                    });
                }
                
                sendCommand(command) {
                    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({
                            type: 'command',
                            data: { command: command }
                        }));
                    } else {
                        this.addLogEntry('❌ Cannot send command - not connected', 'error');
                    }
                }
            }
            
            // Initialize dashboard when page loads
            document.addEventListener('DOMContentLoaded', () => {
                console.log('🚀 Initializing Live Dashboard...');
                new LiveDashboard();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with WebSocket status."""
    global trading_engine_instance
    
    try:
        websocket_status = "running" if websocket_manager.is_running else "stopped"
        active_connections = len(websocket_manager.connections) if websocket_manager.connections else 0
        live_service_status = "running" if live_dashboard_service.is_running else "stopped"
        
        return {
            "status": "healthy",
            "version": "4.0.0",
            "phase": "4C - Live Dashboard Integration",
            "services": {
                "trading_engine": trading_engine_instance is not None,
                "websocket_manager": websocket_status,
                "live_dashboard_service": live_service_status,
                "dashboard": Path("frontend/templates/pages/dashboard.html").exists(),
                "static_files": Path("frontend/static").exists()
            },
            "websocket": {
                "active_connections": active_connections,
                "message_types": list(websocket_manager.MESSAGE_TYPES.keys()) if hasattr(websocket_manager, 'MESSAGE_TYPES') else []
            },
            "features": [
                "Real-time WebSocket updates",
                "Live portfolio tracking",
                "Trading execution alerts",
                "System health monitoring",
                "Multi-chain support"
            ],
            "message": "DEX Sniper Pro is operational with live dashboard integration"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "partial",
            "error": str(e),
            "message": "Some services may be unavailable"
        }


def get_trading_engine():
    """Get the global trading engine instance."""
    global trading_engine_instance
    if trading_engine_instance is None:
        raise HTTPException(status_code=503, detail="Trading engine not initialized")
    return trading_engine_instance


# Make trading engine available to endpoints
live_trading.set_trading_engine_getter(get_trading_engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )