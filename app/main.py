"""
Main Application Entry Point
File: app/main.py
Streamlined main entry point for the DEX Sniper Pro application.
Uses modular architecture with separate managers for different concerns.
FIXED: Dashboard route registration to serve professional template with sidebar.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.utils.logger import setup_logger
from app.factory import create_app
from app.core.lifecycle_manager import LifecycleManager

logger = setup_logger(__name__)

# Application metadata
__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"
__description__ = "Professional trading bot with AI-powered risk assessment"


def verify_template_structure() -> bool:
    """
    Verify that required template files exist before starting the application.
    
    Returns:
        bool: True if all required templates exist
        
    Raises:
        FileNotFoundError: If critical template files are missing
    """
    try:
        logger.info("🔍 Verifying template structure...")
        
        template_dir = Path("frontend/templates")
        if not template_dir.exists():
            logger.warning(f"⚠️ Template directory not found: {template_dir}")
            template_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created template directory: {template_dir}")
        
        # Check required template files
        required_templates = {
            "base/layout.html": "Professional layout with sidebar",
            "pages/dashboard.html": "Main dashboard template"
        }
        
        missing_templates = []
        for template_path, description in required_templates.items():
            full_path = template_dir / template_path
            if not full_path.exists():
                missing_templates.append(f"{template_path} ({description})")
                logger.error(f"❌ Missing template: {template_path}")
            else:
                logger.info(f"✅ Found template: {template_path}")
        
        if missing_templates:
            error_msg = f"Missing required templates: {missing_templates}"
            logger.error(f"❌ Template verification failed: {error_msg}")
            raise FileNotFoundError(error_msg)
        
        logger.info("✅ Template structure verification completed successfully")
        return True
        
    except Exception as error:
        logger.error(f"❌ Template structure verification failed: {error}")
        raise


def setup_professional_dashboard_routes(app) -> None:
    """
    Setup professional dashboard routes that serve the template with sidebar.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If template initialization fails
    """
    try:
        logger.info("🔧 Setting up professional dashboard routes...")
        
        # Verify templates exist before initializing Jinja2
        verify_template_structure()
        
        # Initialize Jinja2Templates with error handling
        try:
            templates = Jinja2Templates(directory="frontend/templates")
            logger.info("✅ Jinja2Templates initialized successfully")
        except Exception as template_error:
            logger.error(f"❌ Failed to initialize Jinja2Templates: {template_error}")
            raise RuntimeError(f"Template initialization failed: {template_error}")
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_professional_dashboard(request: Request) -> HTMLResponse:
            """
            Serve the professional trading dashboard with sidebar.
            
            Args:
                request: HTTP request object
                
            Returns:
                HTMLResponse: Professional dashboard template
                
            Raises:
                HTTPException: If template rendering fails
            """
            try:
                logger.info("🎯 Serving professional dashboard with sidebar")
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as render_error:
                logger.error(f"❌ Dashboard template rendering failed: {render_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Dashboard template error: {render_error}"
                )
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection page using professional template."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Wallet connection template error: {error}")
                raise HTTPException(status_code=500, detail=f"Template error: {error}")
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading interface using professional template."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Live trading template error: {error}")
                raise HTTPException(status_code=500, detail=f"Template error: {error}")
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio management page using professional template."""
            try:
                return templates.TemplateResponse(
                    "pages/dashboard.html", 
                    {"request": request}
                )
            except Exception as error:
                logger.error(f"❌ Portfolio template error: {error}")
                raise HTTPException(status_code=500, detail=f"Template error: {error}")
        
        # Root redirect to dashboard
        @app.get("/", response_class=HTMLResponse)
        async def root_redirect(request: Request) -> HTMLResponse:
            """Root endpoint redirects to professional dashboard."""
            return await serve_professional_dashboard(request)
        
        logger.info("✅ Professional dashboard routes configured successfully")
        
    except Exception as error:
        logger.error(f"❌ Failed to setup professional dashboard routes: {error}")
        raise RuntimeError(f"Dashboard routes setup failed: {error}")


def create_application():
    """
    Create the FastAPI application instance with professional dashboard routes.
    
    Returns:
        FastAPI: Configured application instance
        
    Raises:
        RuntimeError: If application creation fails
    """
    try:
        logger.info("🚀 Creating DEX Sniper Pro application...")
        
        # Create lifecycle manager
        lifecycle_manager = LifecycleManager()
        
        # Create application using factory
        app = create_app()
        
        # Set up lifespan management
        app.router.lifespan_context = lifecycle_manager.lifespan
        
        # Setup professional dashboard routes (CRITICAL FIX)
        try:
            setup_professional_dashboard_routes(app)
            logger.info("✅ Professional dashboard routes integrated successfully")
        except Exception as routes_error:
            logger.error(f"❌ Dashboard routes setup failed: {routes_error}")
            # Don't create fallback routes - fail transparently to fix the real issue
            raise RuntimeError(f"Dashboard routes setup failed: {routes_error}")
        
        # Add startup and shutdown event handlers
        @app.on_event("startup")
        async def startup_event():
            """Application startup event handler with template verification."""
            try:
                await lifecycle_manager.display_startup_message()
                logger.info("✅ Professional dashboard with sidebar is ready")
            except Exception as startup_error:
                logger.error(f"❌ Startup event failed: {startup_error}")
        
        @app.on_event("shutdown")
        async def shutdown_event():
            """Application shutdown event handler."""
            try:
                await lifecycle_manager.display_shutdown_message()
            except Exception as shutdown_error:
                logger.error(f"❌ Shutdown event failed: {shutdown_error}")
        
        logger.info("✅ DEX Sniper Pro Phase 4C application instance created successfully")
        return app
        
    except Exception as error:
        logger.error(f"❌ Critical: Failed to create application instance: {error}")
        raise RuntimeError(f"Application creation failed: {error}")


def create_emergency_dashboard_route(app) -> None:
    """
    Create emergency dashboard route as absolute fallback for development.
    Only used if main dashboard routes fail completely.
    
    Args:
        app: FastAPI application instance
    """
    try:
        logger.warning("⚠️ Creating emergency dashboard route as fallback")
        
        @app.get("/dashboard-emergency", response_class=HTMLResponse)
        async def emergency_dashboard(request: Request) -> HTMLResponse:
            """Emergency dashboard route for debugging template issues."""
            try:
                from fastapi.templating import Jinja2Templates
                templates = Jinja2Templates(directory="frontend/templates")
                return templates.TemplateResponse("pages/dashboard.html", {"request": request})
            except Exception as error:
                logger.error(f"❌ Emergency dashboard failed: {error}")
                return HTMLResponse(
                    content=f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>DEX Sniper Pro - Template Debug</title></head>
                    <body>
                        <h1>DEX Sniper Pro - Template Debug</h1>
                        <h2>Error: {error}</h2>
                        <p><strong>Template Path:</strong> frontend/templates/pages/dashboard.html</p>
                        <p><strong>Solution:</strong> Ensure the template file exists and is properly formatted</p>
                        <ul>
                            <li>Check that frontend/templates/pages/dashboard.html exists</li>
                            <li>Check that frontend/templates/base/layout.html exists</li>
                            <li>Verify template syntax is correct</li>
                        </ul>
                        <p><a href="/docs">API Documentation</a> | <a href="/health">Health Check</a></p>
                    </body>
                    </html>
                    """,
                    status_code=500
                )
        
        logger.info("✅ Emergency dashboard route created at /dashboard-emergency")
        
    except Exception as error:
        logger.error(f"❌ Failed to create emergency dashboard route: {error}")


# Create the FastAPI application instance
try:
    app = create_application()
    
    # Add emergency route for development debugging
    create_emergency_dashboard_route(app)
    
except Exception as error:
    logger.error(f"❌ Application creation error: {error}")
    raise


def main():
    """
    Main entry point for development server.
    
    Raises:
        SystemExit: If server startup fails
    """
    import uvicorn
    
    try:
        logger.info("🚀 Starting DEX Sniper Pro Phase 4C development server...")
        logger.info("🎯 AI Risk Assessment features enabled")
        logger.info("📊 Professional dashboard with sidebar ready")
        
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
        logger.error(f"❌ Server startup failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()