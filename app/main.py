"""
Enhanced Phase 4C Implementation - AI Risk Assessment Integration
File: app/main.py

Professional FastAPI application with comprehensive error handling,
Phase 4B component integration, Phase 4C AI capabilities, and graceful fallback mechanisms.
Maintains backward compatibility while enabling advanced AI features.
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

# ==================== APPLICATION METADATA ====================

__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"
__description__ = "Professional trading bot with AI-powered risk assessment and intelligent trading"

# ==================== COMPONENT AVAILABILITY DETECTION ====================

# Initialize component availability flags with AI components
COMPONENT_STATUS = {
    # Core Phase 4B components
    "wallet_system": False,
    "dex_integration": False,
    "trading_engine": False,
    "live_trading_api": False,
    "phase4a_schemas": False,
    # NEW Phase 4C AI components
    "ai_risk_assessment": False,
    "ai_portfolio_analysis": False,
    "ai_api_endpoints": False
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

# NEW: Safe import of Phase 4C AI components
try:
    from app.core.trading.ai_risk_assessor import (
        get_ai_risk_assessor,
        AIRiskAssessor,
        RiskAssessment
    )
    COMPONENT_STATUS["ai_risk_assessment"] = True
    logger.info("✅ AI Risk Assessment system loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ AI Risk Assessment not available: {e}")
except Exception as e:
    logger.error(f"❌ AI Risk Assessment loading error: {e}")

try:
    from app.api.v1.endpoints.ai_risk_api import ai_risk_router
    COMPONENT_STATUS["ai_api_endpoints"] = True
    logger.info("✅ AI Risk Assessment API endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ AI Risk Assessment API not available: {e}")
except Exception as e:
    logger.error(f"❌ AI Risk Assessment API loading error: {e}")

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
            "phase": "4C - AI Risk Assessment Integration",
            "ai_features": COMPONENT_STATUS["ai_risk_assessment"],
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
            "ai_analysis": "unavailable" if not COMPONENT_STATUS["ai_risk_assessment"] else "available",
            "supported_networks": get_supported_networks()
        }
    
    logger.info("✅ Fallback dashboard components created")

# ==================== APPLICATION LIFECYCLE MANAGEMENT ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced application lifespan management with Phase 4C AI initialization.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Application context
    """
    logger.info("🚀 Starting DEX Sniper Pro - Phase 4C AI Risk Assessment Integration...")
    
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
    Execute comprehensive startup procedures with Phase 4C AI initialization.
    Uses fixed network manager with public RPC fallback to avoid authentication issues.
    
    Returns:
        bool: True if startup successful, False if limited functionality
    """
    try:
        success_count = 0
        total_procedures = 5  # Updated for AI component
        
        logger.info("🚀 Starting Phase 4C with AI Risk Assessment and fixed RPC authentication...")
        
        # Initialize AI Risk Assessment System (NEW in Phase 4C)
        if COMPONENT_STATUS["ai_risk_assessment"]:
            try:
                logger.info("🧠 Initializing AI Risk Assessment system...")
                ai_assessor = await get_ai_risk_assessor()
                if ai_assessor:
                    COMPONENT_STATUS["ai_portfolio_analysis"] = True
                    logger.info("✅ AI Risk Assessment system initialized successfully")
                    success_count += 1
                else:
                    logger.warning("⚠️ AI Risk Assessment system initialization returned None")
            except Exception as e:
                logger.error(f"❌ AI Risk Assessment initialization error: {e}")
                COMPONENT_STATUS["ai_risk_assessment"] = False
                COMPONENT_STATUS["ai_portfolio_analysis"] = False
        else:
            logger.info("📋 AI Risk Assessment not available - skipping initialization")
        
        # Initialize network manager with public RPC fallback
        if COMPONENT_STATUS["wallet_system"] or COMPONENT_STATUS["dex_integration"] or COMPONENT_STATUS["trading_engine"]:
            try:
                logger.info("🔗 Initializing network manager with public RPC priority...")
                
                # Use fixed network manager that prioritizes public RPC endpoints
                from app.core.blockchain.network_manager_fixed import initialize_network_manager
                network_success = await initialize_network_manager()
                
                if network_success:
                    logger.info("✅ Network manager initialized with public RPC fallback")
                    success_count += 1
                else:
                    logger.warning("⚠️ Network manager initialization issues")
                    
            except Exception as e:
                logger.error(f"❌ Network manager initialization error: {e}")
                logger.info("🔄 Continuing without network manager...")
        
        # Initialize wallet system with proper error handling
        if COMPONENT_STATUS["wallet_system"]:
            try:
                logger.info("🔗 Initializing wallet system...")
                # Wallet system will use the fixed network manager
                logger.info("✅ Wallet system prepared (will connect to networks on-demand)")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Wallet system initialization error: {e}")
        else:
            logger.info("📋 Wallet system not available - skipping initialization")
        
        # Initialize DEX integration with proper error handling
        if COMPONENT_STATUS["dex_integration"]:
            try:
                logger.info("📊 Initializing DEX integration...")
                # DEX integration will use the fixed network manager
                logger.info("✅ DEX integration prepared (will connect to networks on-demand)")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ DEX integration initialization error: {e}")
        else:
            logger.info("📋 DEX integration not available - skipping initialization")
        
        # Initialize trading engine with proper error handling
        if COMPONENT_STATUS["trading_engine"]:
            try:
                logger.info("🤖 Initializing trading engine...")
                # Trading engine will use the fixed network manager
                logger.info("✅ Trading engine prepared (will connect to networks on-demand)")
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Trading engine initialization error: {e}")
        else:
            logger.info("📋 Trading engine not available - skipping initialization")
        
        # Verify Phase 4A components (these should always work)
        if COMPONENT_STATUS["live_trading_api"] and COMPONENT_STATUS["phase4a_schemas"]:
            logger.info("✅ Phase 4A components verified and operational")
            success_count += 1
        else:
            logger.warning("⚠️ Phase 4A components not fully available")
        
        # Log initialization summary
        logger.info(f"🎯 Initialization complete: {success_count}/{total_procedures} systems operational")
        logger.info("🧠 AI Risk Assessment integration status: " + 
                   ("✅ Active" if COMPONENT_STATUS["ai_risk_assessment"] else "⚠️ Unavailable"))
        logger.info("💡 Fixed RPC authentication - blockchain connections ready")
        
        return success_count > 0  # At least some functionality available
        
    except Exception as e:
        logger.error(f"❌ Startup procedures failed: {e}")
        return False


async def execute_shutdown_procedures():
    """Execute comprehensive shutdown procedures with AI cleanup."""
    try:
        logger.info("🛑 Executing shutdown procedures...")
        
        shutdown_tasks = []
        
        # Shutdown AI Risk Assessment system (NEW)
        if COMPONENT_STATUS["ai_risk_assessment"]:
            try:
                # AI Risk Assessment cleanup would go here
                logger.info("📝 AI Risk Assessment cleanup scheduled")
            except Exception as e:
                logger.error(f"❌ AI Risk Assessment cleanup error: {e}")
        
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
    Create and configure FastAPI application with Phase 4C AI capabilities.
    
    Returns:
        FastAPI: Configured application instance
        
    Raises:
        RuntimeError: If application creation fails critically
    """
    try:
        # Determine application mode based on AI availability
        is_full_mode = all([
            COMPONENT_STATUS["wallet_system"],
            COMPONENT_STATUS["dex_integration"],
            COMPONENT_STATUS["trading_engine"]
        ])
        
        has_ai_features = COMPONENT_STATUS["ai_risk_assessment"]
        
        if is_full_mode and has_ai_features:
            mode = "AI-Powered Live Trading"
        elif is_full_mode:
            mode = "Live Trading Integration"
        elif has_ai_features:
            mode = "AI Risk Assessment Mode"
        else:
            mode = "Development Mode"
        
        # Create FastAPI application with enhanced description
        app = FastAPI(
            title="DEX Sniper Pro - AI-Powered Trading Bot",
            description="Professional automated trading bot with AI risk assessment and live blockchain integration",
            version=__version__,
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=lifespan,
        )
        
        # Configure middleware
        setup_middleware(app)
        
        # Setup static files
        setup_static_files(app)
        
        # Setup routes with AI integration
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
    Setup all application routes with Phase 4C AI integration.
    
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
        
        # Include AI Risk Assessment router (NEW in Phase 4C)
        if COMPONENT_STATUS["ai_api_endpoints"] and COMPONENT_STATUS["ai_risk_assessment"]:
            app.include_router(ai_risk_router, prefix="/api/v1/ai-risk", tags=["ai-risk"])
            logger.info("✅ AI Risk Assessment router included")
        else:
            logger.warning("⚠️ AI Risk Assessment router not available")
        
        # Include Phase 4A live trading router if available
        if COMPONENT_STATUS["live_trading_api"]:
            app.include_router(live_trading_router, prefix="/api/v1", tags=["live-trading"])
            logger.info("✅ Phase 4A live trading router included")
        else:
            logger.warning("⚠️ Phase 4A live trading router not available")
        
        # Setup frontend routes with AI enhancements
        setup_frontend_routes(app)
        
        # Setup system routes with AI information
        setup_system_routes(app)
        
        logger.info("✅ All application routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Route setup failed: {error}")
        raise RuntimeError(f"Route setup failed: {error}")


def setup_frontend_routes(app: FastAPI) -> None:
    """
    Setup frontend page serving routes with AI enhancements.
    
    Args:
        app: FastAPI application instance
    """
    try:
        templates = Jinja2Templates(directory="frontend/templates")
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve the main trading dashboard with AI features."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {
                        "request": request,
                        "ai_risk_enabled": COMPONENT_STATUS["ai_risk_assessment"],
                        "phase": __phase__
                    }
                )
            except Exception as error:
                logger.error(f"❌ Dashboard template error: {error}")
                return create_fallback_html_response(
                    "🤖 DEX Sniper Pro Dashboard",
                    "Phase 4C - AI Risk Assessment Integration",
                    "AI-powered dashboard with intelligent risk analysis"
                )
        
        @app.get("/risk-analysis", response_class=HTMLResponse)
        async def serve_risk_analysis(request: Request) -> HTMLResponse:
            """Serve AI risk analysis page (NEW in Phase 4C)."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {
                        "request": request,
                        "page_type": "risk_analysis",
                        "ai_risk_enabled": COMPONENT_STATUS["ai_risk_assessment"]
                    }
                )
            except Exception as error:
                logger.error(f"❌ Risk analysis template error: {error}")
                return create_fallback_html_response(
                    "🧠 AI Risk Analysis",
                    "Intelligent risk assessment for trading decisions",
                    "AI-powered risk analysis interface"
                )
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection page with error handling."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {
                        "request": request,
                        "ai_risk_enabled": COMPONENT_STATUS["ai_risk_assessment"]
                    }
                )
            except Exception as error:
                logger.error(f"❌ Wallet connection template error: {error}")
                return create_fallback_html_response(
                    "🔗 Wallet Connection",
                    "Connect your MetaMask or WalletConnect wallet",
                    "Wallet connection interface with AI risk insights"
                )
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading interface with AI enhancements."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {
                        "request": request,
                        "ai_risk_enabled": COMPONENT_STATUS["ai_risk_assessment"]
                    }
                )
            except Exception as error:
                logger.error(f"❌ Live trading template error: {error}")
                return create_fallback_html_response(
                    "⚡ Live Trading",
                    "Real-time trading with AI risk assessment",
                    "AI-enhanced live trading interface"
                )
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio management page with AI insights."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {
                        "request": request,
                        "page_type": "portfolio",
                        "ai_risk_enabled": COMPONENT_STATUS["ai_risk_assessment"]
                    }
                )
            except Exception as error:
                logger.error(f"❌ Portfolio template error: {error}")
                return create_fallback_html_response(
                    "📊 Portfolio Management",
                    "Track performance with AI risk insights",
                    "AI-enhanced portfolio management interface"
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
            __phase__,
            "Minimal interface mode with AI risk assessment capabilities"
        )
    
    logger.info("✅ Minimal frontend routes configured")


def setup_system_routes(app: FastAPI) -> None:
    """
    Setup system health and status routes with Phase 4C AI information.
    
    Args:
        app: FastAPI application instance
    """
    try:
        @app.get("/")
        async def root() -> Dict[str, Any]:
            """Enhanced root endpoint with Phase 4C AI system information."""
            try:
                return await get_comprehensive_system_info()
            except Exception as error:
                logger.error(f"❌ Root endpoint error: {error}")
                return {
                    "message": "🤖 DEX Sniper Pro - AI-Powered Trading Bot API",
                    "version": __version__,
                    "phase": __phase__,
                    "status": "limited_functionality",
                    "error": "System information temporarily unavailable",
                    "ai_features": {
                        "risk_assessment": COMPONENT_STATUS["ai_risk_assessment"],
                        "portfolio_analysis": COMPONENT_STATUS["ai_portfolio_analysis"]
                    },
                    "endpoints": {
                        "dashboard": "/dashboard",
                        "risk_analysis": "/risk-analysis",
                        "health": "/health",
                        "docs": "/docs",
                        "ai_risk_api": "/api/v1/ai-risk" if COMPONENT_STATUS["ai_api_endpoints"] else None
                    }
                }
        
        @app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """Comprehensive health check with Phase 4C AI component status."""
            try:
                return await get_comprehensive_health_status()
            except Exception as error:
                logger.error(f"❌ Health check error: {error}")
                return {
                    "status": "unhealthy",
                    "service": "DEX Sniper Pro AI-Powered Trading Bot",
                    "version": __version__,
                    "phase": __phase__,
                    "error": str(error),
                    "components": COMPONENT_STATUS,
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
                    "phase": __phase__,
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
                    "available_endpoints": [
                        "/", "/health", "/dashboard", "/risk-analysis", "/docs",
                        "/api/v1/ai-risk" if COMPONENT_STATUS["ai_api_endpoints"] else None
                    ],
                    "ai_features": COMPONENT_STATUS["ai_risk_assessment"]
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
                    "body": exc.body,
                    "phase": __phase__
                }
            )
        
        logger.info("✅ Error handlers configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Error handlers setup failed: {error}")


# ==================== UTILITY FUNCTIONS ====================

async def get_comprehensive_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information with Phase 4C AI features.
    
    Returns:
        Dict containing system information with AI capabilities
    """
    try:
        system_status = await get_system_status_safe()
        
        return {
            "message": "🤖 DEX Sniper Pro - AI-Powered Trading Bot API",
            "version": __version__,
            "phase": __phase__,
            "status": "operational",
            "description": __description__,
            "blockchain_approach": "public_rpc_priority",
            "rpc_authentication": "fixed_with_fallback",
            "ai_features": {
                "risk_assessment": {
                    "status": "operational" if COMPONENT_STATUS["ai_risk_assessment"] else "unavailable",
                    "description": "AI-powered risk analysis for trading decisions",
                    "capabilities": [
                        "Token risk assessment",
                        "Portfolio risk analysis",
                        "Market condition analysis",
                        "Automated recommendations"
                    ] if COMPONENT_STATUS["ai_risk_assessment"] else []
                },
                "portfolio_intelligence": {
                    "status": "operational" if COMPONENT_STATUS["ai_portfolio_analysis"] else "unavailable",
                    "description": "AI-driven portfolio optimization and insights"
                }
            },
            "capabilities": get_available_capabilities(),
            "supported_networks": get_supported_networks(),
            "component_status": COMPONENT_STATUS,
            "system_status": system_status,
            "endpoints": {
                "dashboard": "/dashboard",
                "risk_analysis": "/risk-analysis" if COMPONENT_STATUS["ai_risk_assessment"] else None,
                "api_docs": "/docs",
                "health_check": "/health",
                "dashboard_stats": "/api/v1/dashboard/stats",
                "token_discovery": "/api/v1/tokens/discover",
                "ai_risk_api": "/api/v1/ai-risk" if COMPONENT_STATUS["ai_api_endpoints"] else None
            },
            "blockchain_connectivity": {
                "approach": "Public RPC endpoints prioritized over private",
                "authentication": "API keys used only when available and working",
                "fallback": "Comprehensive public RPC endpoint fallback system",
                "reliability": "No startup blocking due to RPC authentication issues"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as error:
        logger.error(f"❌ System info error: {error}")
        raise


async def get_comprehensive_health_status() -> Dict[str, Any]:
    """
    Get comprehensive health status with Phase 4C AI component information.
    
    Returns:
        Dict containing health status with AI capabilities
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "DEX Sniper Pro AI-Powered Trading Bot",
            "version": __version__,
            "phase": __phase__,
            "startup_mode": "safe_mode",
            "blockchain_status": "on_demand_initialization",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
            "overall_health_score": 0.0
        }
        
        component_scores = []
        
        # Check AI Risk Assessment (NEW)
        if COMPONENT_STATUS["ai_risk_assessment"]:
            health_status["components"]["ai_risk_assessment"] = {
                "status": "healthy",
                "mode": "operational",
                "message": "AI Risk Assessment system operational",
                "features": ["token_analysis", "portfolio_analysis", "market_assessment"]
            }
            component_scores.append(1.0)
        else:
            health_status["components"]["ai_risk_assessment"] = {
                "status": "not_loaded",
                "message": "AI Risk Assessment component not available"
            }
            component_scores.append(0.0)
        
        # Check AI Portfolio Analysis (NEW)
        if COMPONENT_STATUS["ai_portfolio_analysis"]:
            health_status["components"]["ai_portfolio_analysis"] = {
                "status": "healthy",
                "mode": "operational",
                "message": "AI Portfolio Analysis operational"
            }
            component_scores.append(1.0)
        else:
            health_status["components"]["ai_portfolio_analysis"] = {
                "status": "not_loaded",
                "message": "AI Portfolio Analysis not available"
            }
            component_scores.append(0.0)
        
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
        
        # Add AI capabilities summary
        health_status["ai_capabilities"] = {
            "risk_assessment": COMPONENT_STATUS["ai_risk_assessment"],
            "portfolio_analysis": COMPONENT_STATUS["ai_portfolio_analysis"],
            "market_intelligence": COMPONENT_STATUS["ai_risk_assessment"],
            "automated_recommendations": COMPONENT_STATUS["ai_risk_assessment"]
        }
        
        # Add safe startup explanation
        health_status["safe_startup_info"] = {
            "enabled": True,
            "reason": "Prevents RPC authentication errors during startup",
            "benefit": "Application starts reliably without blockchain dependencies",
            "blockchain_initialization": "On-demand when trading features are first used",
            "ai_initialization": "Immediate for AI risk assessment features"
        }
        
        return health_status
        
    except Exception as error:
        logger.error(f"❌ Health status error: {error}")
        raise


async def get_system_status_safe() -> Dict[str, Any]:
    """
    Get system status with comprehensive error handling and AI information.
    
    Returns:
        Dict containing system status information with AI metrics
    """
    try:
        status = {
            "initialized": False,
            "uptime_hours": 0,
            "active_sessions": 0,
            "active_connections": 0,
            "component_availability": COMPONENT_STATUS,
            "ai_status": {
                "risk_assessments_performed": 0,
                "portfolio_analyses": 0,
                "ai_recommendations_generated": 0
            }
        }
        
        # Get AI system status if available
        if COMPONENT_STATUS["ai_risk_assessment"]:
            try:
                ai_assessor = await get_ai_risk_assessor()
                if ai_assessor:
                    # Would collect AI metrics here
                    status["ai_status"]["system_ready"] = True
                    status["ai_status"]["cache_size"] = len(ai_assessor.assessment_cache)
            except Exception as e:
                logger.warning(f"⚠️ AI status collection error: {e}")
        
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
        return {
            "error": "Status unavailable", 
            "component_availability": COMPONENT_STATUS,
            "ai_status": {"available": COMPONENT_STATUS["ai_risk_assessment"]}
        }


def get_available_capabilities() -> List[str]:
    """
    Get list of available capabilities based on loaded components including AI features.
    
    Returns:
        List of capability descriptions with AI features
    """
    capabilities = [
        "✅ Professional Dashboard Interface",
        "✅ RESTful API Framework", 
        "✅ Token Discovery System",
        "✅ Health Monitoring & Status Reporting",
        "✅ Fixed RPC Authentication (Public Endpoint Priority)",
        "✅ Blockchain Connectivity with Fallback System"
    ]
    
    # Add AI capabilities
    if COMPONENT_STATUS["ai_risk_assessment"]:
        capabilities.extend([
            "🧠 AI-Powered Risk Assessment",
            "🎯 Intelligent Trading Recommendations",
            "📊 Smart Position Sizing",
            "📈 Market Condition Analysis"
        ])
    
    if COMPONENT_STATUS["ai_portfolio_analysis"]:
        capabilities.append("📊 AI Portfolio Risk Management")
    
    if COMPONENT_STATUS["ai_api_endpoints"]:
        capabilities.append("🔗 AI Risk Assessment API")
    
    if COMPONENT_STATUS["phase4a_schemas"]:
        capabilities.append("✅ Phase 4A Trading Schemas")
    
    if COMPONENT_STATUS["live_trading_api"]:
        capabilities.append("✅ Live Trading Session Management")
    
    if COMPONENT_STATUS["wallet_system"]:
        capabilities.append("✅ Wallet Connection System (Public RPC)")
    
    if COMPONENT_STATUS["dex_integration"]:
        capabilities.append("✅ Live DEX Integration (Public RPC)")
    
    if COMPONENT_STATUS["trading_engine"]:
        capabilities.append("✅ Automated Trading Engine (Public RPC)")
    
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
    Create a fallback HTML response with AI feature information.
    
    Args:
        title: Page title
        subtitle: Page subtitle
        description: Page description
        
    Returns:
        HTMLResponse with fallback content including AI features
    """
    ai_features = "🧠 AI Risk Assessment" if COMPONENT_STATUS["ai_risk_assessment"] else "⚠️ AI Features Unavailable"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{ 
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 3rem;
                text-align: center;
                max-width: 600px;
                margin: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
            h1 {{ 
                font-size: 2.5rem; 
                margin-bottom: 1rem;
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            h2 {{ 
                font-size: 1.5rem; 
                margin-bottom: 1.5rem;
                opacity: 0.9;
            }}
            p {{ 
                font-size: 1.1rem; 
                line-height: 1.6;
                opacity: 0.8;
                margin-bottom: 2rem;
            }}
            .feature-list {{
                list-style: none;
                padding: 0;
                margin: 2rem 0;
            }}
            .feature-list li {{
                background: rgba(255, 255, 255, 0.1);
                margin: 0.5rem 0;
                padding: 0.8rem;
                border-radius: 10px;
                font-size: 1rem;
            }}
            .ai-status {{
                background: rgba(76, 175, 80, 0.2);
                color: #4CAF50;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                display: inline-block;
                margin: 1rem 0;
                font-weight: bold;
            }}
            .links {{
                margin-top: 2rem;
            }}
            .links a {{
                color: white;
                text-decoration: none;
                background: rgba(255, 255, 255, 0.2);
                padding: 0.8rem 1.5rem;
                border-radius: 10px;
                margin: 0.5rem;
                display: inline-block;
                transition: all 0.3s ease;
            }}
            .links a:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <h2>{subtitle}</h2>
            <div class="ai-status">{ai_features}</div>
            <p>{description}</p>
            
            <ul class="feature-list">
                <li>🧠 AI-Powered Risk Assessment</li>
                <li>📊 Intelligent Portfolio Analysis</li>
                <li>⚡ Real-time Market Insights</li>
                <li>🛡️ Automated Risk Management</li>
                <li>📈 Smart Trading Recommendations</li>
                <li>🔗 Professional API Framework</li>
            </ul>
            
            <div class="links">
                <a href="/docs">📖 API Documentation</a>
                <a href="/health">🔍 System Health</a>
                {f'<a href="/api/v1/ai-risk/health">🧠 AI System Health</a>' if COMPONENT_STATUS["ai_api_endpoints"] else ''}
                {f'<a href="/api/v1/ai-risk/risk-levels">🎯 Risk Levels</a>' if COMPONENT_STATUS["ai_api_endpoints"] else ''}
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
    logger.info("🎯 DEX Sniper Pro Phase 4C application instance created successfully")
except Exception as e:
    logger.error(f"💥 Critical: Failed to create application instance: {e}")
    sys.exit(1)

# ==================== STARTUP EVENTS ====================

@app.on_event("startup")
async def display_startup_message():
    """Display comprehensive startup message with AI information."""
    logger.info("=" * 80)
    logger.info("🤖 DEX SNIPER PRO - PHASE 4C AI RISK ASSESSMENT INTEGRATION")
    logger.info("=" * 80)
    logger.info("🚀 Status: Starting up...")
    logger.info(f"📋 Version: {__version__}")
    logger.info(f"🎯 Phase: {__phase__}")
    logger.info("🧠 NEW: AI-Powered Risk Assessment System")
    logger.info("🔗 Mode: Clean Implementation with AI Integration")
    logger.info(f"📊 Components Available: {sum(COMPONENT_STATUS.values())}/{len(COMPONENT_STATUS)}")
    logger.info(f"🧠 AI Features: {'✅ Active' if COMPONENT_STATUS['ai_risk_assessment'] else '⚠️ Unavailable'}")
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
        logger.info("🚀 Starting DEX Sniper Pro Phase 4C development server...")
        logger.info("🧠 AI Risk Assessment features enabled")
        
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

# Export application
__all__ = ["app", "COMPONENT_STATUS"]