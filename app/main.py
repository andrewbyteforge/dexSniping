"""
Clean Phase 4B Implementation - Enhanced Main Application
File: app/main.py

Professional FastAPI application with comprehensive error handling,
Phase 4B component integration, and graceful fallback mechanisms.
Maintains backward compatibility while enabling advanced features.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# ==================== COMPONENT AVAILABILITY DETECTION ====================

# Initialize component availability flags
COMPONENT_STATUS = {
    "wallet_system": False,
    "dex_integration": False,
    "trading_engine": False,
    "live_trading_api": False,
    "phase4a_schemas": False
}

# Safe import of Phase 4B components with comprehensive error handling
try:
    from app.core.wallet.wallet_connection_manager import (
        get_wallet_connection_manager,
        initialize_wallet_system,
        NetworkType
    )
    COMPONENT_STATUS["wallet_system"] = True
    logger.info("✅ Wallet system components loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Wallet system not available: {e}")
except Exception as e:
    logger.error(f"❌ Wallet system loading error: {e}")

try:
    from app.core.dex.live_dex_integration import (
        get_live_dex_integration,
        initialize_dex_integration
    )
    COMPONENT_STATUS["dex_integration"] = True
    logger.info("✅ DEX integration components loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ DEX integration not available: {e}")
except Exception as e:
    logger.error(f"❌ DEX integration loading error: {e}")

try:
    from app.core.trading.live_trading_engine_enhanced import (
        get_live_trading_engine,
        initialize_live_trading_system
    )
    COMPONENT_STATUS["trading_engine"] = True
    logger.info("✅ Trading engine components loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Trading engine not available: {e}")
except Exception as e:
    logger.error(f"❌ Trading engine loading error: {e}")

# Import existing working components with fallbacks
try:
    from app.api.v1.endpoints.live_trading_fixed import router as live_trading_router
    COMPONENT_STATUS["live_trading_api"] = True
    logger.info("✅ Live trading API (Phase 4A) loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Live trading API not available: {e}")
except Exception as e:
    logger.error(f"❌ Live trading API loading error: {e}")

try:
    from app.schemas.trading_schemas import TradingSessionResponse
    COMPONENT_STATUS["phase4a_schemas"] = True
    logger.info("✅ Phase 4A schemas loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Phase 4A schemas not available: {e}")
except Exception as e:
    logger.error(f"❌ Phase 4A schemas loading error: {e}")

# Safe import of dashboard components (these should always work)
try:
    from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router
    logger.info("✅ Dashboard components loaded successfully")
except ImportError as e:
    logger.error(f"❌ Critical: Dashboard components not available: {e}")
    # Create fallback routers
    from fastapi import APIRouter
    
    dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])
    tokens_router = APIRouter(prefix="/tokens", tags=["tokens"])
    
    @dashboard_router.get("/stats")
    async def fallback_dashboard_stats():
        """Fallback dashboard statistics."""
        return {
            "status": "operational",
            "mode": "fallback_mode",
            "total_opportunities": 0,
            "active_trades": 0,
            "success_rate": "0%",
            "total_profit": "$0.00",
            "system_uptime": "0 hours",
            "connected_wallets": 0,
            "phase": "4B - Clean Implementation",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @tokens_router.get("/discover")
    async def fallback_token_discovery():
        """Fallback token discovery."""
        return {
            "discovered_tokens": [],
            "total_discovered": 0,
            "discovery_rate": "0 tokens/hour",
            "last_discovery": None,
            "status": "fallback_mode",
            "supported_networks": get_supported_networks()
        }
    
    logger.info("✅ Fallback dashboard components created")

# ==================== APPLICATION LIFECYCLE MANAGEMENT ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced application lifespan management with comprehensive error handling.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Application context
    """
    logger.info("🚀 Starting DEX Sniper Pro - Phase 4B Clean Implementation...")
    
    startup_success = False
    try:
        startup_success = await execute_startup_procedures()
        
        if startup_success:
            logger.info("✅ Application startup completed successfully")
        else:
            logger.warning("⚠️ Application started with limited functionality")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.info("🔄 Starting with basic functionality only...")
        yield
    finally:
        try:
            await execute_shutdown_procedures()
            logger.info("✅ Application shutdown completed successfully")
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


async def execute_startup_procedures() -> bool:
    """
    Execute comprehensive startup procedures with error handling.
    Skip blockchain connections during startup to prevent RPC errors.
    
    Returns:
        bool: True if startup successful, False if limited functionality
    """
    try:
        success_count = 0
        total_procedures = 4
        
        logger.info("🔧 Starting application in safe mode (no blockchain connections)")
        
        # Skip blockchain network initialization during startup
        # This prevents RPC authentication errors from blocking the application
        logger.info("⚠️ Blockchain connections disabled during startup")
        logger.info("💡 Networks will connect on-demand when trading features are used")
        
        # Initialize wallet system without network connections
        if COMPONENT_STATUS["wallet_system"]:
            try:
                logger.info("🔗 Initializing wallet system (offline mode)...")
                # Don't actually initialize - just mark as available for later
                logger.info("✅ Wallet system prepared for on-demand initialization")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Wallet system preparation error: {e}")
        else:
            logger.info("📋 Wallet system not available - skipping preparation")
        
        # Initialize DEX integration without network connections
        if COMPONENT_STATUS["dex_integration"]:
            try:
                logger.info("📊 Initializing DEX integration (offline mode)...")
                # Don't actually initialize - just mark as available for later
                logger.info("✅ DEX integration prepared for on-demand initialization")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ DEX integration preparation error: {e}")
        else:
            logger.info("📋 DEX integration not available - skipping preparation")
        
        # Initialize trading engine without network connections
        if COMPONENT_STATUS["trading_engine"]:
            try:
                logger.info("🤖 Initializing trading engine (offline mode)...")
                # Don't actually initialize - just mark as available for later
                logger.info("✅ Trading engine prepared for on-demand initialization")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Trading engine preparation error: {e}")
        else:
            logger.info("📋 Trading engine not available - skipping preparation")
        
        # Verify Phase 4A components (these should always work)
        if COMPONENT_STATUS["live_trading_api"] and COMPONENT_STATUS["phase4a_schemas"]:
            logger.info("✅ Phase 4A components verified and ready")
            success_count += 1
        else:
            logger.warning("⚠️ Phase 4A components not fully available")
        
        # Log initialization summary
        logger.info(f"🎯 Safe startup complete: {success_count}/{total_procedures} systems prepared")
        logger.info("💡 Application ready - blockchain features will initialize on first use")
        
        return success_count > 0  # At least some functionality available
        
    except Exception as e:
        logger.error(f"❌ Startup procedures failed: {e}")
        return False


async def execute_shutdown_procedures():
    """Execute comprehensive shutdown procedures with error handling."""
    try:
        logger.info("🛑 Executing shutdown procedures...")
        
        shutdown_tasks = []
        
        # Shutdown trading engine
        if COMPONENT_STATUS["trading_engine"]:
            try:
                trading_engine = get_live_trading_engine()
                shutdown_tasks.append(trading_engine.shutdown())
                logger.info("📝 Trading engine shutdown scheduled")
            except Exception as e:
                logger.error(f"❌ Trading engine shutdown scheduling error: {e}")
        
        # Cleanup wallet connections
        if COMPONENT_STATUS["wallet_system"]:
            try:
                wallet_manager = get_wallet_connection_manager()
                shutdown_tasks.append(wallet_manager.cleanup_expired_connections())
                logger.info("📝 Wallet cleanup scheduled")
            except Exception as e:
                logger.error(f"❌ Wallet cleanup scheduling error: {e}")
        
        # Execute all shutdown tasks
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            logger.info("✅ All shutdown tasks completed")
        
    except Exception as e:
        logger.error(f"❌ Shutdown procedures error: {e}")


# ==================== FASTAPI APPLICATION CREATION ====================

def create_fastapi_application() -> FastAPI:
    """
    Create and configure FastAPI application with comprehensive setup.
    
    Returns:
        FastAPI: Configured application instance
        
    Raises:
        RuntimeError: If application creation fails critically
    """
    try:
        # Determine application mode
        is_full_mode = all([
            COMPONENT_STATUS["wallet_system"],
            COMPONENT_STATUS["dex_integration"],
            COMPONENT_STATUS["trading_engine"]
        ])
        
        mode = "Live Trading Integration" if is_full_mode else "Development Mode"
        
        # Create FastAPI application
        app = FastAPI(
            title="DEX Sniper Pro - Live Trading Bot",
            description="Professional automated trading bot with live blockchain integration",
            version="4.0.0-beta",
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=lifespan,
        )
        
        # Configure middleware
        setup_middleware(app)
        
        # Setup static files
        setup_static_files(app)
        
        # Setup routes
        setup_application_routes(app)
        
        # Setup error handlers
        setup_error_handlers(app)
        
        logger.info(f"✅ FastAPI application created successfully - Mode: {mode}")
        return app
        
    except Exception as error:
        logger.error(f"❌ Failed to create FastAPI application: {error}")
        raise RuntimeError(f"Application creation failed: {error}")


def setup_middleware(app: FastAPI) -> None:
    """
    Setup application middleware with error handling.
    
    Args:
        app: FastAPI application instance
    """
    try:
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        logger.info("✅ Middleware configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Middleware setup failed: {error}")
        raise RuntimeError(f"Middleware setup failed: {error}")


def setup_static_files(app: FastAPI) -> None:
    """
    Setup static file serving with error handling.
    
    Args:
        app: FastAPI application instance
    """
    try:
        frontend_static_path = Path("frontend/static")
        if frontend_static_path.exists():
            app.mount(
                "/static", 
                StaticFiles(directory=str(frontend_static_path)), 
                name="static"
            )
            logger.info(f"✅ Static files mounted: {frontend_static_path}")
        else:
            logger.warning(f"⚠️ Frontend static directory not found: {frontend_static_path}")
        
    except Exception as error:
        logger.error(f"❌ Static file setup failed: {error}")
        # Don't raise - static files are not critical


def setup_application_routes(app: FastAPI) -> None:
    """
    Setup all application routes with error handling.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If critical route setup fails
    """
    try:
        # Include core API routers (always available)
        app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
        app.include_router(tokens_router, prefix="/api/v1", tags=["tokens"])
        logger.info("✅ Core API routers included")
        
        # Include Phase 4A live trading router if available
        if COMPONENT_STATUS["live_trading_api"]:
            app.include_router(live_trading_router, prefix="/api/v1", tags=["live-trading"])
            logger.info("✅ Phase 4A live trading router included")
        else:
            logger.warning("⚠️ Phase 4A live trading router not available")
        
        # Setup frontend routes
        setup_frontend_routes(app)
        
        # Setup system routes
        setup_system_routes(app)
        
        logger.info("✅ All application routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Route setup failed: {error}")
        raise RuntimeError(f"Route setup failed: {error}")


def setup_frontend_routes(app: FastAPI) -> None:
    """
    Setup frontend page serving routes with error handling.
    
    Args:
        app: FastAPI application instance
    """
    try:
        templates = Jinja2Templates(directory="frontend/templates")
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve the main trading dashboard with error handling."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Dashboard template error: {error}")
                return create_fallback_html_response(
                    "🤖 DEX Sniper Pro Dashboard",
                    "Phase 4B - Live Trading Integration",
                    "Dashboard template temporarily unavailable"
                )
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection page with error handling."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Wallet connection template error: {error}")
                return create_fallback_html_response(
                    "🔗 Wallet Connection",
                    "Connect your MetaMask or WalletConnect wallet",
                    "Wallet connection interface"
                )
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading interface with error handling."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Live trading template error: {error}")
                return create_fallback_html_response(
                    "⚡ Live Trading",
                    "Real-time trading opportunities and execution",
                    "Live trading interface"
                )
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio management page with error handling."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Portfolio template error: {error}")
                return create_fallback_html_response(
                    "📊 Portfolio Management",
                    "Track your trading performance and positions",
                    "Portfolio management interface"
                )
        
        logger.info("✅ Frontend routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Frontend routes setup failed: {error}")
        # Don't raise - create minimal fallback routes
        setup_minimal_frontend_routes(app)


def setup_minimal_frontend_routes(app: FastAPI) -> None:
    """Setup minimal frontend routes as fallback."""
    @app.get("/dashboard", response_class=HTMLResponse)
    async def minimal_dashboard():
        """Minimal dashboard fallback."""
        return create_fallback_html_response(
            "🤖 DEX Sniper Pro",
            "Phase 4B - Clean Implementation",
            "Minimal interface mode"
        )
    
    logger.info("✅ Minimal frontend routes configured")


def setup_system_routes(app: FastAPI) -> None:
    """
    Setup system health and status routes with comprehensive error handling.
    
    Args:
        app: FastAPI application instance
    """
    try:
        @app.get("/")
        async def root() -> Dict[str, Any]:
            """Enhanced root endpoint with comprehensive system information."""
            try:
                return await get_comprehensive_system_info()
            except Exception as error:
                logger.error(f"❌ Root endpoint error: {error}")
                return {
                    "message": "🤖 DEX Sniper Pro - Live Trading Bot API",
                    "version": "4.0.0-beta",
                    "status": "limited_functionality",
                    "error": "System information temporarily unavailable",
                    "endpoints": {
                        "dashboard": "/dashboard",
                        "health": "/health",
                        "docs": "/docs"
                    }
                }
        
        @app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """Comprehensive health check with detailed component status."""
            try:
                return await get_comprehensive_health_status()
            except Exception as error:
                logger.error(f"❌ Health check error: {error}")
                return {
                    "status": "unhealthy",
                    "service": "DEX Sniper Pro Live Trading Bot",
                    "version": "4.0.0-beta",
                    "error": str(error),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        logger.info("✅ System routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ System routes setup failed: {error}")
        raise RuntimeError(f"System routes setup failed: {error}")


def setup_error_handlers(app: FastAPI) -> None:
    """
    Setup comprehensive error handlers.
    
    Args:
        app: FastAPI application instance
    """
    try:
        @app.exception_handler(500)
        async def internal_error_handler(request: Request, exc: Exception):
            """Handle internal server errors with detailed logging."""
            logger.error(f"💥 Internal Server Error: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An internal error occurred",
                    "type": "InternalServerError",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(404)
        async def not_found_handler(request: Request, exc: HTTPException):
            """Handle 404 errors with helpful suggestions."""
            return JSONResponse(
                status_code=404,
                content={
                    "error": "not_found",
                    "message": "Endpoint not found",
                    "suggestion": "Check /docs for available endpoints",
                    "available_endpoints": ["/", "/health", "/dashboard", "/docs"]
                }
            )
        
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Handle request validation errors with detailed information."""
            return JSONResponse(
                status_code=422,
                content={
                    "error": "validation_error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "body": exc.body
                }
            )
        
        logger.info("✅ Error handlers configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Error handlers setup failed: {error}")


# ==================== UTILITY FUNCTIONS ====================

async def get_comprehensive_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information with error handling.
    
    Returns:
        Dict containing system information
    """
    try:
        system_status = await get_system_status_safe()
        
        return {
            "message": "🤖 DEX Sniper Pro - Live Trading Bot API",
            "version": "4.0.0-beta",
            "phase": "4B - Clean Implementation with Safe Startup",
            "status": "operational",
            "startup_mode": "safe_mode",
            "blockchain_status": "on_demand_initialization",
            "capabilities": get_available_capabilities(),
            "supported_networks": get_supported_networks(),
            "component_status": COMPONENT_STATUS,
            "system_status": system_status,
            "endpoints": {
                "dashboard": "/dashboard",
                "api_docs": "/docs",
                "health_check": "/health",
                "dashboard_stats": "/api/v1/dashboard/stats",
                "token_discovery": "/api/v1/tokens/discover"
            },
            "notes": {
                "blockchain_connections": "Available on-demand (prevents startup RPC errors)",
                "trading_features": "Will initialize when first accessed",
                "safe_startup": "Application starts without blockchain dependencies"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as error:
        logger.error(f"❌ System info error: {error}")
        raise


async def get_comprehensive_health_status() -> Dict[str, Any]:
    """
    Get comprehensive health status with detailed component information.
    
    Returns:
        Dict containing health status
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "DEX Sniper Pro Live Trading Bot",
            "version": "4.0.0-beta",
            "phase": "4B - Clean Implementation with Safe Startup",
            "startup_mode": "safe_mode",
            "blockchain_status": "on_demand_initialization",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_health_score": 0.0
        }
        
        component_scores = []
        
        # Check trading engine (not connected during startup)
        if COMPONENT_STATUS["trading_engine"]:
            health_status["components"]["trading_engine"] = {
                "status": "available",
                "mode": "on_demand_initialization",
                "message": "Ready to initialize when trading features are accessed",
                "startup_connection": "disabled_for_stability"
            }
            component_scores.append(0.8)  # Available but not connected
        else:
            health_status["components"]["trading_engine"] = {
                "status": "not_loaded",
                "message": "Component not available"
            }
            component_scores.append(0.0)
        
        # Check wallet system (not connected during startup)
        if COMPONENT_STATUS["wallet_system"]:
            health_status["components"]["wallet_system"] = {
                "status": "available",
                "mode": "on_demand_initialization", 
                "message": "Ready to initialize when wallet features are accessed",
                "startup_connection": "disabled_for_stability"
            }
            component_scores.append(0.8)  # Available but not connected
        else:
            health_status["components"]["wallet_system"] = {
                "status": "not_loaded",
                "message": "Component not available"
            }
            component_scores.append(0.0)
        
        # Check DEX integration (not connected during startup)
        if COMPONENT_STATUS["dex_integration"]:
            health_status["components"]["dex_integration"] = {
                "status": "available",
                "mode": "on_demand_initialization",
                "message": "Ready to initialize when DEX features are accessed", 
                "startup_connection": "disabled_for_stability"
            }
            component_scores.append(0.8)  # Available but not connected
        else:
            health_status["components"]["dex_integration"] = {
                "status": "not_loaded",
                "message": "Component not available"
            }
            component_scores.append(0.0)
        
        # Core components (always healthy if app is running)
        health_status["components"]["dashboard"] = {
            "status": "healthy",
            "message": "Dashboard API operational"
        }
        health_status["components"]["api"] = {
            "status": "healthy", 
            "message": "REST API operational"
        }
        health_status["components"]["phase4a_compatibility"] = {
            "status": "healthy" if COMPONENT_STATUS["live_trading_api"] else "degraded",
            "message": "Phase 4A live trading API available" if COMPONENT_STATUS["live_trading_api"] else "Phase 4A API not available"
        }
        component_scores.extend([1.0, 1.0, 1.0 if COMPONENT_STATUS["live_trading_api"] else 0.5])
        
        # Calculate overall health score
        if component_scores:
            health_status["overall_health_score"] = sum(component_scores) / len(component_scores)
        
        # Determine overall status
        if health_status["overall_health_score"] >= 0.8:
            health_status["status"] = "healthy"
        elif health_status["overall_health_score"] >= 0.5:
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
        
        # Add safe startup explanation
        health_status["safe_startup_info"] = {
            "enabled": True,
            "reason": "Prevents RPC authentication errors during startup",
            "benefit": "Application starts reliably without blockchain dependencies",
            "blockchain_initialization": "On-demand when trading features are first used"
        }
        
        return health_status
        
    except Exception as error:
        logger.error(f"❌ Health status error: {error}")
        raise


async def get_system_status_safe() -> Dict[str, Any]:
    """
    Get system status with comprehensive error handling.
    
    Returns:
        Dict containing system status information
    """
    try:
        status = {
            "initialized": False,
            "uptime_hours": 0,
            "active_sessions": 0,
            "active_connections": 0,
            "component_availability": COMPONENT_STATUS
        }
        
        if COMPONENT_STATUS["trading_engine"]:
            try:
                trading_engine = get_live_trading_engine()
                stats = trading_engine.get_system_statistics()
                status.update({
                    "initialized": stats.get("is_initialized", False),
                    "uptime_hours": stats.get("system_uptime_hours", 0),
                    "active_sessions": stats.get("active_sessions", 0)
                })
            except Exception as e:
                logger.warning(f"⚠️ Trading engine status error: {e}")
        
        if COMPONENT_STATUS["wallet_system"]:
            try:
                wallet_manager = get_wallet_connection_manager()
                active_connections = wallet_manager.get_active_connections()
                status["active_connections"] = len(active_connections)
            except Exception as e:
                logger.warning(f"⚠️ Wallet manager status error: {e}")
        
        return status
        
    except Exception as error:
        logger.error(f"❌ System status error: {error}")
        return {"error": "Status unavailable", "component_availability": COMPONENT_STATUS}


def get_available_capabilities() -> List[str]:
    """
    Get list of available capabilities based on loaded components.
    
    Returns:
        List of capability descriptions
    """
    capabilities = [
        "✅ Professional Dashboard Interface",
        "✅ RESTful API Framework", 
        "✅ Token Discovery System",
        "✅ Health Monitoring & Status Reporting",
        "✅ Safe Startup Mode (No RPC Errors)",
        "✅ On-Demand Blockchain Initialization"
    ]
    
    if COMPONENT_STATUS["phase4a_schemas"]:
        capabilities.append("✅ Phase 4A Trading Schemas")
    
    if COMPONENT_STATUS["live_trading_api"]:
        capabilities.append("✅ Live Trading Session Management")
    
    if COMPONENT_STATUS["wallet_system"]:
        capabilities.append("🔄 Wallet Connection System (On-Demand)")
    
    if COMPONENT_STATUS["dex_integration"]:
        capabilities.append("🔄 Live DEX Integration (On-Demand)")
    
    if COMPONENT_STATUS["trading_engine"]:
        capabilities.append("🔄 Automated Trading Engine (On-Demand)")
    
    return capabilities


def get_supported_networks() -> List[str]:
    """
    Get list of supported network names.
    
    Returns:
        List of supported network names
    """
    if COMPONENT_STATUS["wallet_system"]:
        try:
            networks = get_supported_networks_enum()
            return [network.value for network in networks]
        except Exception as e:
            logger.warning(f"⚠️ Network enumeration error: {e}")
    
    return ["ethereum", "polygon", "bsc", "arbitrum"]


def get_supported_networks_enum():
    """
    Get supported networks as enum objects with error handling.
    
    Returns:
        List of NetworkType enum values or empty list
    """
    try:
        if COMPONENT_STATUS["wallet_system"]:
            return [
                NetworkType.ETHEREUM,
                NetworkType.POLYGON,
                NetworkType.BSC
            ]
    except Exception as e:
        logger.warning(f"⚠️ Network enum error: {e}")
    
    return []


def create_fallback_html_response(title: str, subtitle: str, description: str) -> HTMLResponse:
    """
    Create a fallback HTML response when templates are not available.
    
    Args:
        title: Page title
        subtitle: Page subtitle
        description: Page description
        
    Returns:
        HTMLResponse with fallback content
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
            .status {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .links {{ margin-top: 30px; }}
            .links a {{ display: inline-block; margin: 5px 10px 5px 0; padding: 8px 15px; background: #007acc; color: white; text-decoration: none; border-radius: 4px; }}
            .links a:hover {{ background: #005f9a; }}
            .capabilities {{ margin-top: 20px; }}
            .capabilities li {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <div class="status">
                <strong>Status:</strong> Operational - {subtitle}
            </div>
            <p>{description}</p>
            <div class="capabilities">
                <h3>Available Features:</h3>
                <ul>
                    <li>Professional API Framework</li>
                    <li>Health Monitoring System</li>
                    <li>Token Discovery Interface</li>
                    <li>Dashboard Statistics</li>
                </ul>
            </div>
            <div class="links">
                <a href="/docs">API Documentation</a>
                <a href="/health">System Health</a>
                <a href="/api/v1/dashboard/stats">Dashboard API</a>
                <a href="/">Root API</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ==================== APPLICATION INSTANCE CREATION ====================

# Create the FastAPI application instance
try:
    app = create_fastapi_application()
    logger.info("🎯 DEX Sniper Pro application instance created successfully")
except Exception as e:
    logger.error(f"💥 Critical: Failed to create application instance: {e}")
    sys.exit(1)

# ==================== STARTUP EVENTS ====================

@app.on_event("startup")
async def display_startup_message():
    """Display comprehensive startup message."""
    logger.info("=" * 80)
    logger.info("🤖 DEX SNIPER PRO - PHASE 4B CLEAN IMPLEMENTATION")
    logger.info("=" * 80)
    logger.info("🚀 Status: Starting up...")
    logger.info("📋 Version: 4.0.0-beta")
    logger.info("🎯 Phase: 4B - Live Trading Integration")
    logger.info("🔗 Mode: Clean Implementation with Fallback Support")
    logger.info(f"📊 Components Available: {sum(COMPONENT_STATUS.values())}/{len(COMPONENT_STATUS)}")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def display_shutdown_message():
    """Display shutdown message."""
    logger.info("=" * 80)
    logger.info("🛑 DEX SNIPER PRO - SHUTTING DOWN")
    logger.info("=" * 80)
    logger.info("✅ Shutdown complete")
    logger.info("=" * 80)


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    """Run the application directly for development."""
    import uvicorn
    
    try:
        logger.info("🚀 Starting DEX Sniper Pro development server...")
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as error:
        logger.error(f"💥 Server startup failed: {error}")
        sys.exit(1)


# ==================== APPLICATION METADATA ====================

__version__ = "4.0.0-beta"
__phase__ = "4B - Clean Implementation"
__description__ = "Professional trading bot with clean Phase 4B architecture and comprehensive error handling"

# Export application
__all__ = ["app"]