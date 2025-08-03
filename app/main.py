"""
FastAPI Main Application
File: app/main.py

Consolidated professional FastAPI application combining the best features
from both application structures with proper lifespan management, middleware,
and trading engine integration.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

# Import API routers
from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router

# Import core components
from app.core.trading.trading_engine import TradingEngine
from app.services import initialize_trading_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global trading engine instance
trading_engine_instance: TradingEngine = None

# Templates for serving HTML pages
templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handle application startup and shutdown with proper trading engine lifecycle.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Application lifecycle context
        
    Raises:
        RuntimeError: If trading engine initialization fails
    """
    # Startup
    logger.info("🚀 Initializing DEX Sniper Pro Trading Engine...")
    
    try:
        global trading_engine_instance
        trading_engine_instance = TradingEngine()
        await trading_engine_instance.initialize()
        
        # Store in app state for access by routes
        app.state.trading_engine = trading_engine_instance
        
        # Initialize trading service
        trading_service = initialize_trading_service(trading_engine_instance)
        app.state.trading_service = trading_service
        
        logger.info("✅ Trading engine initialized successfully")
        logger.info("✅ Trading service initialized successfully")
        
    except Exception as error:
        logger.error(f"❌ Failed to initialize trading engine: {error}")
        raise RuntimeError(f"Trading engine initialization failed: {error}")
    
    # Application is ready
    logger.info("🎯 DEX Sniper Pro Trading Bot is ready for operation")
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down DEX Sniper Pro Trading Engine...")
    
    try:
        if trading_engine_instance:
            await trading_engine_instance.shutdown()
        logger.info("✅ Trading engine shutdown complete")
        
    except Exception as error:
        logger.error(f"❌ Error during shutdown: {error}")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application with all middleware and routes.
    
    Returns:
        FastAPI: Configured application instance
        
    Raises:
        RuntimeError: If application creation fails
    """
    try:
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
        
        # Setup static file serving
        setup_static_files(app)
        
        # Setup all routes
        setup_routes(app)
        
        logger.info("✅ FastAPI application created successfully")
        return app
        
    except Exception as error:
        logger.error(f"❌ Failed to create FastAPI application: {error}")
        raise RuntimeError(f"Application creation failed: {error}")


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If middleware setup fails
    """
    try:
        # CORS middleware - must be added first
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify exact origins
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
        )
        logger.info("✅ CORS middleware configured")
        
        # Trusted host middleware for security
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "*.vercel.app"]
        )
        logger.info("✅ Trusted host middleware configured")
        
        logger.info("✅ All middleware configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Failed to setup middleware: {error}")
        raise RuntimeError(f"Middleware setup failed: {error}")


def setup_static_files(app: FastAPI) -> None:
    """
    Setup static file serving for frontend assets.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If static file setup fails
    """
    try:
        # Frontend static files (CSS, JS, images)
        frontend_static_path = Path("frontend/static")
        if frontend_static_path.exists():
            app.mount(
                "/static", 
                StaticFiles(directory=str(frontend_static_path)), 
                name="static"
            )
            logger.info(f"✅ Mounted static files from: {frontend_static_path}")
        else:
            logger.warning(f"⚠️ Frontend static directory not found: {frontend_static_path}")
        
    except Exception as error:
        logger.error(f"❌ Failed to setup static files: {error}")
        raise RuntimeError(f"Static file setup failed: {error}")


def setup_routes(app: FastAPI) -> None:
    """
    Configure all routes for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If route setup fails
    """
    try:
        # Setup API routes
        setup_api_routes(app)
        
        # Setup frontend page routes
        setup_frontend_routes(app)
        
        # Setup system routes
        setup_system_routes(app)
        
        logger.info("✅ All routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Failed to setup routes: {error}")
        raise RuntimeError(f"Route setup failed: {error}")


def setup_api_routes(app: FastAPI) -> None:
    """
    Setup API endpoint routes.
    
    Args:
        app: FastAPI application instance
    """
    # API v1 routes
    app.include_router(
        dashboard_router, 
        prefix="/api/v1", 
        tags=["dashboard"]
    )
    
    app.include_router(
        tokens_router, 
        prefix="/api/v1", 
        tags=["tokens"]
    )
    
    logger.info("✅ API routes configured")


def setup_frontend_routes(app: FastAPI) -> None:
    """
    Setup frontend page serving routes.
    
    Args:
        app: FastAPI application instance
    """
    @app.get("/dashboard", response_class=HTMLResponse)
    async def serve_dashboard(request: Request) -> HTMLResponse:
        """
        Serve the main trading dashboard.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTMLResponse: Dashboard HTML page
            
        Raises:
            HTTPException: If dashboard cannot be served
        """
        try:
            return templates.TemplateResponse(
                "pages/dashboard.html", 
                {"request": request}
            )
        except Exception as error:
            logger.error(f"❌ Failed to serve dashboard: {error}")
            raise HTTPException(status_code=500, detail="Dashboard unavailable")
    
    # Sidebar navigation routes - all redirect to dashboard for now
    @app.get("/token-discovery", response_class=HTMLResponse)
    async def token_discovery(request: Request) -> HTMLResponse:
        """Serve token discovery page (currently redirects to dashboard)."""
        return await serve_dashboard(request)
    
    @app.get("/live-trading", response_class=HTMLResponse)
    async def live_trading(request: Request) -> HTMLResponse:
        """Serve live trading page (currently redirects to dashboard)."""
        return await serve_dashboard(request)
    
    @app.get("/portfolio", response_class=HTMLResponse)
    async def portfolio(request: Request) -> HTMLResponse:
        """Serve portfolio page (currently redirects to dashboard)."""
        return await serve_dashboard(request)
    
    # Root redirect to dashboard
    @app.get("/", response_class=HTMLResponse)
    async def root_redirect(request: Request) -> HTMLResponse:
        """Root endpoint that serves the dashboard."""
        return await serve_dashboard(request)
    
    logger.info("✅ Frontend routes configured")


def setup_system_routes(app: FastAPI) -> None:
    """
    Setup system routes for health checks and status.
    
    Args:
        app: FastAPI application instance
    """
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """
        Health check endpoint for monitoring.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Check if trading engine is available
            trading_engine_status = "initializing"
            if hasattr(app.state, 'trading_engine') and app.state.trading_engine:
                trading_engine = app.state.trading_engine
                if hasattr(trading_engine, 'is_running'):
                    trading_engine_status = "running" if trading_engine.is_running else "stopped"
                else:
                    trading_engine_status = "available"
            
            return {
                "status": "healthy",
                "service": "DEX Sniper Pro Trading Bot",
                "version": "4.0.0",
                "phase": "4A - Backend Integration",
                "trading_engine": trading_engine_status,
                "dashboard": "/dashboard",
                "api_docs": "/docs",
                "timestamp": "2025-08-03T00:00:00Z"
            }
            
        except Exception as error:
            logger.error(f"❌ Health check failed: {error}")
            return {
                "status": "unhealthy",
                "error": str(error),
                "timestamp": "2025-08-03T00:00:00Z"
            }
    
    @app.get("/status")
    async def system_status() -> Dict[str, Any]:
        """
        Detailed system status endpoint.
        
        Returns:
            Dict[str, Any]: Detailed system status
        """
        try:
            status_info = {
                "service": "DEX Sniper Pro Trading Bot",
                "version": "4.0.0",
                "phase": "4A - Backend Integration", 
                "status": "operational",
                "components": {
                    "api": "healthy",
                    "dashboard": "healthy",
                    "trading_engine": "healthy" if hasattr(app.state, 'trading_engine') else "initializing"
                },
                "endpoints": {
                    "dashboard": "/dashboard",
                    "health": "/health", 
                    "api_docs": "/docs",
                    "api_v1": "/api/v1"
                },
                "timestamp": "2025-08-03T00:00:00Z"
            }
            
            return status_info
            
        except Exception as error:
            logger.error(f"❌ System status check failed: {error}")
            raise HTTPException(status_code=500, detail=str(error))
    
    logger.info("✅ System routes configured")


def get_trading_engine() -> TradingEngine:
    """
    Get the global trading engine instance.
    
    Returns:
        TradingEngine: The trading engine instance
        
    Raises:
        RuntimeError: If trading engine is not initialized
    """
    global trading_engine_instance
    
    if trading_engine_instance is None:
        raise RuntimeError("Trading engine not initialized")
    
    return trading_engine_instance


# Create the application instance
app = create_application()


# For direct execution during development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )