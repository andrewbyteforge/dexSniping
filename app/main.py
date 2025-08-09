"""
Main Application Entry Point
File: app/main.py
CLEAN VERSION - NO FALLBACK LOGIC - PROFESSIONAL DASHBOARD ONLY

Streamlined main entry point for the DEX Sniper Pro application.
Removed ALL fallback mechanisms that were overriding the professional dashboard.
BYPASSES app/factory.py and app/server/routes.py to avoid fallback routes.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.utils.logger import (
    setup_logger, 
    log_application_startup, 
    log_application_shutdown,
    get_performance_logger
)

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = setup_logger(__name__)

# Application metadata
__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"
__description__ = "Professional trading bot with AI-powered risk assessment"


def verify_template_files() -> bool:
    """
    Verify that all required template files exist.
    
    Returns:
        bool: True if all templates exist
        
    Raises:
        FileNotFoundError: If required templates are missing
    """
    logger.info("🔍 Starting template verification...")
    
    template_dir = Path("frontend/templates")
    logger.info(f"📁 Checking template directory: {template_dir.absolute()}")
    
    if not template_dir.exists():
        logger.error(f"❌ Template directory does not exist: {template_dir.absolute()}")
        raise FileNotFoundError(f"Template directory not found: {template_dir.absolute()}")
    
    logger.info(f"✅ Template directory exists: {template_dir.absolute()}")
    
    # Check required template files
    required_templates = [
        "base/layout.html",
        "pages/dashboard.html"
    ]
    
    for template_path in required_templates:
        full_path = template_dir / template_path
        logger.info(f"🔍 Checking template: {full_path}")
        
        if not full_path.exists():
            logger.error(f"❌ Required template missing: {full_path}")
            raise FileNotFoundError(f"Required template not found: {full_path}")
        
        logger.info(f"✅ Template found: {template_path}")
    
    logger.info("✅ All template files verified successfully")
    return True


def setup_static_files(app: FastAPI) -> None:
    """
    Setup static file serving.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("🔧 Setting up static files...")
    
    try:
        static_dir = Path("frontend/static")
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
            logger.info(f"✅ Static files mounted: {static_dir.absolute()}")
        else:
            logger.warning(f"⚠️ Static directory not found: {static_dir.absolute()}")
    except Exception as error:
        logger.error(f"❌ Static files setup failed: {error}")
        # Don't fail - static files are not critical


def setup_middleware(app: FastAPI) -> None:
    """
    Setup application middleware.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("🔧 Setting up middleware...")
    
    try:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("✅ CORS middleware configured")
    except Exception as error:
        logger.error(f"❌ Middleware setup failed: {error}")
        raise


def setup_api_routes(app: FastAPI) -> None:
    """
    Setup API routes with detailed logging.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("🔧 Setting up API routes...")
    
    try:
        # Import API routers with error handling
        try:
            from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router
            logger.info("✅ Dashboard and tokens routers imported successfully")
        except ImportError as error:
            logger.error(f"❌ Failed to import API routers: {error}")
            raise
        
        # Include API routers
        app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
        app.include_router(tokens_router, prefix="/api/v1", tags=["tokens"])
        logger.info("✅ API routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ API routes setup failed: {error}")
        raise


def setup_professional_dashboard_routes(app: FastAPI) -> None:
    """
    Setup ONLY the professional dashboard routes - NO FALLBACK LOGIC.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If template setup fails
    """
    logger.info("🎯 Setting up PROFESSIONAL dashboard routes...")
    
    # First verify all templates exist
    verify_template_files()
    
    # Initialize Jinja2Templates
    try:
        templates = Jinja2Templates(directory="frontend/templates")
        logger.info("✅ Jinja2Templates initialized successfully")
    except Exception as error:
        logger.error(f"❌ Failed to initialize Jinja2Templates: {error}")
        raise RuntimeError(f"Template initialization failed: {error}")
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def serve_professional_dashboard(request: Request) -> HTMLResponse:
        """
        Serve the PROFESSIONAL trading dashboard with sidebar.
        NO FALLBACK - If this fails, we want to see the error.
        """
                        logger.info("🎯 Serving PROFESSIONAL dashboard with sidebar")
        logger.debug(f"📄 Template: pages/dashboard.html")
        logger.debug(f"🔗 Request URL: {request.url}")
        logger.debug(f"🕐 Request time: {datetime.now().isoformat()}")
        logger.debug(f"📄 Template: pages/dashboard.html")
        logger.debug(f"🔗 Request URL: {request.url}")
        logger.debug(f"🕐 Request time: {datetime.now().isoformat()}")
        logger.info(f"📄 Template: pages/dashboard.html")
        logger.info(f"🔗 Request URL: {request.url}")
        
        try:
            response = templates.TemplateResponse(
                "pages/dashboard.html", 
                {"request": request}
            )
            logger.info("✅ Professional dashboard rendered successfully")
            return response
        except Exception as error:
            logger.error(f"❌ CRITICAL: Professional dashboard template failed: {error}")
            logger.error(f"❌ Template path: frontend/templates/pages/dashboard.html")
            logger.error(f"❌ Request details: {request.url}, {request.method}")
            # NO FALLBACK - Raise the error so we can fix it
            raise HTTPException(
                status_code=500,
                detail=f"Professional dashboard template error: {error}"
            )
    
    @app.get("/", response_class=HTMLResponse)
    async def root_redirect(request: Request) -> HTMLResponse:
        """Root redirects to professional dashboard."""
        logger.info("🔄 Root request redirecting to professional dashboard")
        return await serve_professional_dashboard(request)
    
    @app.get("/wallet-connection", response_class=HTMLResponse)
    async def serve_wallet_connection(request: Request) -> HTMLResponse:
        """Serve wallet connection using professional template."""
        logger.info("🔗 Serving wallet connection page")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
    
    @app.get("/live-trading", response_class=HTMLResponse)
    async def serve_live_trading(request: Request) -> HTMLResponse:
        """Serve live trading using professional template."""
        logger.info("⚡ Serving live trading page")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
    
    @app.get("/portfolio", response_class=HTMLResponse)
    async def serve_portfolio(request: Request) -> HTMLResponse:
        """Serve portfolio using professional template."""
        logger.info("📊 Serving portfolio page")
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
    
    logger.info("✅ PROFESSIONAL dashboard routes configured - NO FALLBACK")


def setup_health_routes(app: FastAPI) -> None:
    """
    Setup health check routes.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("🔧 Setting up health routes...")
    
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint."""
        logger.info("🏥 Health check requested")
        return {
            "status": "healthy",
            "service": "DEX Sniper Pro Trading Bot",
            "version": __version__,
            "phase": __phase__,
            "dashboard": "professional_template",
            "timestamp": "2025-08-09T00:00:00Z"
        }
    
    logger.info("✅ Health routes configured")


def create_application() -> FastAPI:
    """
    Create the FastAPI application - PROFESSIONAL DASHBOARD ONLY.
    
    Returns:
        FastAPI: Configured application instance
        
    Raises:
        RuntimeError: If application creation fails
    """
    logger.info("🚀 Creating DEX Sniper Pro application - PROFESSIONAL DASHBOARD ONLY")
            # Log application startup
        log_application_startup()
        logger.info("🎯 Creating professional dashboard application")
                # Log application startup
        log_application_startup()
        logger.info("🎯 Creating professional dashboard application")
        logger.info(f"📖 Version: {__version__}")
    logger.info(f"🎯 Phase: {__phase__}")
    
    try:
        # Create FastAPI app
        app = FastAPI(
            title="DEX Sniper Pro - Live Trading Bot",
            description=__description__,
            version=__version__,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        logger.info("✅ FastAPI application created")
        
        # Setup middleware
        setup_middleware(app)
        
        # Setup static files
        setup_static_files(app)
        
        # Setup API routes
        setup_api_routes(app)
        
        # Setup PROFESSIONAL dashboard routes (NO FALLBACK)
        setup_professional_dashboard_routes(app)
        
        # Setup health routes
        setup_health_routes(app)
        
        # Add startup event
        @app.on_event("startup")
        async def startup_event():
            """Application startup event."""
            logger.info("🎉 DEX Sniper Pro startup complete")
            logger.info("🎯 PROFESSIONAL dashboard with sidebar ready")
            logger.info("📍 Dashboard URL: http://localhost:8000/dashboard")
        
        logger.info("✅ Application creation completed successfully")
        return app
        
    except Exception as error:
        logger.error(f"❌ CRITICAL: Application creation failed: {error}")
        raise RuntimeError(f"Application creation failed: {error}")


# Create the application instance - BYPASSING FACTORY
logger.info("🔥 Initializing DEX Sniper Pro - BYPASSING FACTORY...")
try:
    app = create_application()
    logger.info("✅ Application instance created successfully - NO FALLBACK ROUTES")
except Exception as error:
    logger.error(f"❌ FATAL: Failed to create application: {error}")
    raise


def main():
    """
    Main entry point for development server.
    """
    import uvicorn
    
    logger.info("🚀 Starting DEX Sniper Pro development server...")
    logger.info("🎯 PROFESSIONAL dashboard mode - NO FALLBACK")
    logger.info("📊 Sidebar and token discovery features enabled")
    
    try:
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
        log_application_shutdown()
        log_application_shutdown()
    except Exception as error:
        logger.error(f"❌ Server startup failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()