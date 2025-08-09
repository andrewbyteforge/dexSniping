"""
Routes Configuration - Fixed Dashboard Display
File: app/server/routes.py

Fixes the dashboard routing to ensure the professional dashboard displays correctly.
"""

from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router
from app.api.v1.endpoints.live_trading import live_trading_router
from app.api.v1.endpoints.trading import trading_router
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Templates for serving HTML pages - ensure correct path
TEMPLATES_DIR = Path("frontend/templates")
if not TEMPLATES_DIR.exists():
    logger.error(f"Templates directory not found at {TEMPLATES_DIR}")
    TEMPLATES_DIR = Path("templates")  # Fallback

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def setup_routes(app: FastAPI) -> None:
    """
    Configure all routes for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If route setup fails
    """
    try:
        # Mount static files first
        static_dir = Path("frontend/static")
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
            logger.info("Static files mounted successfully")
        else:
            logger.warning(f"Static directory not found at {static_dir}")
        
        # Setup API routes
        setup_api_routes(app)
        
        # Setup frontend page routes
        setup_frontend_routes(app)
        
        # Setup health and status routes
        setup_system_routes(app)
        
        logger.info("All routes configured successfully")
        
    except Exception as error:
        logger.error(f"Failed to setup routes: {error}")
        raise RuntimeError(f"Route setup failed: {error}")


def setup_api_routes(app: FastAPI) -> None:
    """
    Setup API endpoint routes.
    
    Args:
        app: FastAPI application instance
    """
    try:
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
        
        # Check if live_trading_router exists before including
        try:
            app.include_router(
                live_trading_router, 
                prefix="/api/v1", 
                tags=["trading"]
            )
        except Exception as e:
            logger.warning(f"Live trading router not available: {e}")
        
        # Check if trading_router exists before including
        try:
            app.include_router(
                trading_router, 
                prefix="/api/v1", 
                tags=["trading-operations"]
            )
        except Exception as e:
            logger.warning(f"Trading router not available: {e}")
        
        logger.info("API routes configured")
        
    except Exception as error:
        logger.error(f"Failed to setup API routes: {error}")
        raise


def setup_frontend_routes(app: FastAPI) -> None:
    """
    Setup frontend page serving routes with proper error handling.
    
    Args:
        app: FastAPI application instance
    """
    
    def verify_template_exists(template_name: str) -> bool:
        """Check if a template file exists."""
        template_path = TEMPLATES_DIR / template_name
        exists = template_path.exists()
        if not exists:
            logger.warning(f"Template not found: {template_path}")
        return exists
    
    # Main dashboard page
    @app.get("/dashboard", response_class=HTMLResponse)
    async def serve_dashboard(request: Request) -> HTMLResponse:
        """
        Serve the main trading dashboard.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTMLResponse: Dashboard HTML page
        """
        try:
            # Verify template exists
            if not verify_template_exists("pages/dashboard.html"):
                # Try backup
                if verify_template_exists("pages/dashboard.html.backup"):
                    logger.info("Using backup dashboard template")
                    return templates.TemplateResponse(
                        "pages/dashboard.html.backup", 
                        {"request": request}
                    )
                else:
                    logger.error("No dashboard template found")
                    raise HTTPException(
                        status_code=500, 
                        detail="Dashboard template not found"
                    )
            
            # Serve the professional dashboard
            logger.info("Serving professional dashboard")
            return templates.TemplateResponse(
                "pages/dashboard.html", 
                {
                    "request": request,
                    "title": "DEX Sniper Pro Dashboard",
                    "version": "4.0.0"
                }
            )
            
        except HTTPException:
            raise
        except Exception as error:
            logger.error(f"Failed to serve dashboard: {error}")
            # Create a proper error response instead of fallback
            raise HTTPException(
                status_code=500, 
                detail=f"Dashboard unavailable: {str(error)}"
            )
    
    # Token discovery page - for now serve dashboard
    @app.get("/token-discovery", response_class=HTMLResponse)
    async def serve_token_discovery(request: Request) -> HTMLResponse:
        """
        Serve the token discovery page.
        Currently serves dashboard until dedicated template is created.
        """
        return await serve_dashboard(request)
    
    # Live trading page - for now serve dashboard
    @app.get("/live-trading", response_class=HTMLResponse)
    async def serve_live_trading(request: Request) -> HTMLResponse:
        """
        Serve the live trading page.
        Currently serves dashboard until dedicated template is created.
        """
        return await serve_dashboard(request)
    
    # Portfolio page - for now serve dashboard
    @app.get("/portfolio", response_class=HTMLResponse)
    async def serve_portfolio(request: Request) -> HTMLResponse:
        """
        Serve the portfolio management page.
        Currently serves dashboard until dedicated template is created.
        """
        return await serve_dashboard(request)
    
    # Root redirect to dashboard
    @app.get("/", response_class=HTMLResponse)
    async def root_redirect(request: Request) -> HTMLResponse:
        """
        Root endpoint that redirects to the dashboard.
        """
        # Direct serve instead of redirect for better reliability
        return await serve_dashboard(request)
    
    logger.info("Frontend routes configured successfully")


def setup_system_routes(app: FastAPI) -> None:
    """
    Setup system routes for health checks and status.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.get("/api/v1/health")
    async def health_check() -> Dict[str, Any]:
        """
        Health check endpoint.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Check template directory
            templates_available = TEMPLATES_DIR.exists()
            dashboard_available = (TEMPLATES_DIR / "pages/dashboard.html").exists()
            
            # Check if trading engine is available
            trading_engine_status = "healthy"
            if hasattr(app.state, 'trading_engine'):
                trading_engine = app.state.trading_engine
                if trading_engine and hasattr(trading_engine, 'is_running'):
                    trading_engine_status = "running" if trading_engine.is_running else "stopped"
            
            return {
                "status": "healthy",
                "service": "DEX Sniper Pro Trading Bot",
                "version": "4.0.0",
                "components": {
                    "trading_engine": trading_engine_status,
                    "templates": "available" if templates_available else "missing",
                    "dashboard": "available" if dashboard_available else "missing",
                    "api": "operational"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as error:
            logger.error(f"Health check failed: {error}")
            return {
                "status": "unhealthy",
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @app.get("/api/v1/status")
    async def system_status() -> Dict[str, Any]:
        """
        Detailed system status endpoint.
        
        Returns:
            Dict[str, Any]: Detailed status information
        """
        try:
            # List available templates
            available_templates = []
            if TEMPLATES_DIR.exists():
                pages_dir = TEMPLATES_DIR / "pages"
                if pages_dir.exists():
                    available_templates = [
                        f.name for f in pages_dir.iterdir() 
                        if f.suffix == '.html'
                    ]
            
            return {
                "status": "operational",
                "version": "4.0.0",
                "phase": "4B - Live Trading Integration",
                "templates": {
                    "directory": str(TEMPLATES_DIR),
                    "exists": TEMPLATES_DIR.exists(),
                    "available": available_templates
                },
                "routes": {
                    "dashboard": "/dashboard",
                    "api_health": "/api/v1/health",
                    "api_docs": "/docs"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as error:
            logger.error(f"Status check failed: {error}")
            return {
                "status": "error",
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    logger.info("System routes configured successfully")


# Import datetime for timestamps
from datetime import datetime