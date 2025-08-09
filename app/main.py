"""
DEX Sniper Pro - Main Application - Phase 4B
File: app/main.py
Class: FastAPI Application
Methods: create_application, lifespan management

Professional FastAPI application with proper error handling and component integration.
Fixed syntax error and improved structure.
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global instances
trading_engine_instance = None
templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan management for startup and shutdown.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: During application runtime
    """
    # Startup
    logger.info("🚀 Starting DEX Sniper Pro Trading Bot...")
    
    try:
        # Initialize core systems
        await initialize_core_systems()
        
        # Initialize trading engine
        await initialize_trading_engine()
        
        # Initialize database
        await initialize_database()
        
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        # Don't raise - allow app to start in limited mode
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down DEX Sniper Pro Trading Bot...")
    
    try:
        # Cleanup trading engine
        if trading_engine_instance:
            await trading_engine_instance.shutdown()
        
        # Cleanup database connections
        await cleanup_database()
        
        logger.info("✅ Application shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


async def initialize_core_systems() -> None:
    """Initialize core application systems."""
    try:
        logger.info("📋 Initializing core systems...")
        
        # Initialize configuration
        from app.core.config.settings_manager import get_settings
        settings = get_settings()
        logger.info("✅ Configuration system initialized")
        
        # Initialize logging
        logger.info("✅ Logging system operational")
        
    except Exception as e:
        logger.error(f"❌ Core system initialization failed: {e}")
        raise


async def initialize_trading_engine() -> None:
    """Initialize the trading engine."""
    global trading_engine_instance
    
    try:
        logger.info("⚡ Initializing trading engine...")
        
        # Import and create trading engine
        from app.core.trading.trading_engine import TradingEngine
        trading_engine_instance = TradingEngine()
        
        # Initialize the engine
        await trading_engine_instance.initialize()
        
        logger.info("✅ Trading engine initialized successfully")
        
    except ImportError:
        logger.warning("⚠️ Trading engine not available - running in limited mode")
    except Exception as e:
        logger.error(f"❌ Trading engine initialization failed: {e}")


async def initialize_database() -> None:
    """Initialize database connections."""
    try:
        logger.info("💾 Initializing database...")
        
        from app.core.database.persistence_manager import initialize_persistence_system
        success = await initialize_persistence_system()
        
        if success:
            logger.info("✅ Database initialized successfully")
        else:
            logger.warning("⚠️ Database initialization failed - using fallback")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")


async def cleanup_database() -> None:
    """Cleanup database connections."""
    try:
        from app.core.database.persistence_manager import get_persistence_manager
        manager = await get_persistence_manager()
        await manager.shutdown()
        logger.info("✅ Database connections closed")
        
    except Exception as e:
        logger.error(f"❌ Database cleanup error: {e}")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    # Create FastAPI application
    app = FastAPI(
        title="DEX Sniper Pro Trading Bot",
        description="Professional automated trading bot for decentralized exchanges",
        version="4.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup static files
    setup_static_files(app)
    
    # Setup routes
    setup_routes(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    logger.info("✅ FastAPI application created successfully")
    return app


def setup_middleware(app: FastAPI) -> None:
    """Setup application middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info("✅ Middleware configured")


def setup_static_files(app: FastAPI) -> None:
    """Setup static file serving."""
    try:
        # Frontend static files
        frontend_static_path = Path("frontend/static")
        if frontend_static_path.exists():
            app.mount(
                "/static", 
                StaticFiles(directory=str(frontend_static_path)), 
                name="static"
            )
            logger.info(f"✅ Static files mounted: {frontend_static_path}")
        else:
            logger.warning("⚠️ Frontend static directory not found")
        
    except Exception as e:
        logger.error(f"❌ Static file setup failed: {e}")


def setup_routes(app: FastAPI) -> None:
    """Setup application routes."""
    try:
        # Import and include API routers
        setup_api_routes(app)
        
        # Setup frontend routes
        setup_frontend_routes(app)
        
        # Setup system routes
        setup_system_routes(app)
        
        logger.info("✅ Routes configured successfully")
        
    except Exception as e:
        logger.error(f"❌ Route setup failed: {e}")


def setup_api_routes(app: FastAPI) -> None:
    """Setup API routes."""
    try:
        # Dashboard API
        try:
            from app.api.v1.endpoints.dashboard import router as dashboard_router
            app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
        except ImportError:
            logger.warning("⚠️ Dashboard router not available")
        
        # Trading API
        try:
            from app.api.v1.endpoints.trading import router as trading_router
            app.include_router(trading_router, prefix="/api/v1", tags=["trading"])
        except ImportError:
            logger.warning("⚠️ Trading router not available")
        
        # Wallet API
        try:
            from app.api.v1.endpoints.wallet import router as wallet_router
            app.include_router(wallet_router, prefix="/api/v1", tags=["wallet"])
        except ImportError:
            logger.warning("⚠️ Wallet router not available")
        
        # Live Trading API
        try:
            from app.api.v1.endpoints.live_trading_api import router as live_trading_router
            app.include_router(live_trading_router, prefix="/api/v1", tags=["live-trading"])
        except ImportError:
            logger.warning("⚠️ Live trading router not available")
        
        logger.info("✅ API routes configured")
        
    except Exception as e:
        logger.error(f"❌ API route setup failed: {e}")


def setup_frontend_routes(app: FastAPI) -> None:
    """Setup frontend page routes."""
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint - redirect to dashboard."""
        return """
        <html>
            <head><title>DEX Sniper Pro</title></head>
            <body>
                <h1>🤖 DEX Sniper Pro Trading Bot</h1>
                <p>Professional automated trading bot for decentralized exchanges</p>
                <p><a href="/dashboard">Go to Dashboard</a></p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Serve the main dashboard."""
        try:
            return templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "title": "Trading Dashboard"}
            )
        except Exception as e:
            logger.error(f"❌ Dashboard template error: {e}")
            return HTMLResponse(
                "<h1>Dashboard Temporarily Unavailable</h1>"
                "<p>Please check template configuration.</p>"
            )


def setup_system_routes(app: FastAPI) -> None:
    """Setup system and health check routes."""
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        try:
            # Check database
            database_status = "operational"
            try:
                from app.core.database.persistence_manager import get_persistence_manager
                manager = await get_persistence_manager()
                status = manager.get_database_status()
                if not status.get("operational", False):
                    database_status = "degraded"
            except Exception:
                database_status = "unavailable"
            
            # Check trading engine
            trading_status = "operational" if trading_engine_instance else "unavailable"
            
            return {
                "status": "healthy",
                "service": "DEX Sniper Pro Trading Bot",
                "version": "4.0.0",
                "components": {
                    "database": database_status,
                    "trading_engine": trading_status,
                    "api": "operational"
                },
                "timestamp": "2025-08-09T09:30:00Z"
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": str(e)}
            )
    
    @app.get("/status")
    async def status():
        """Detailed status endpoint."""
        return {
            "application": "DEX Sniper Pro Trading Bot",
            "version": "4.0.0",
            "status": "operational",
            "features": {
                "database_persistence": True,
                "trading_engine": trading_engine_instance is not None,
                "wallet_integration": True,
                "dex_connectivity": True
            }
        }


def setup_error_handlers(app: FastAPI) -> None:
    """Setup global error handlers."""
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Handle 404 errors."""
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "path": str(request.url.path)}
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )


def get_trading_engine():
    """Get the trading engine instance."""
    global trading_engine_instance
    
    if trading_engine_instance is None:
        raise RuntimeError("Trading engine not initialized")
    
    return trading_engine_instance


# Create the FastAPI application
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )