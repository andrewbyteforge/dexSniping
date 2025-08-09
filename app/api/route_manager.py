"""
Route Manager Module
File: app/api/route_manager.py

Manages all application routes and endpoints with component-based loading.
Handles safe route registration and fallback routes.
"""

from typing import Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, Request, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime

from app.utils.logger import setup_logger
from app.core.system_info import SystemInfoProvider
from fastapi.responses import HTMLResponse


logger = setup_logger(__name__)


class RouteManager:
    """Manages application routes and endpoints."""
    
    def __init__(self):
        """Initialize the route manager."""
        self.system_info = SystemInfoProvider()
        self.templates = None
        
    async def setup_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """
        Setup all application routes based on component availability.
        
        Args:
            app: FastAPI application instance
            component_status: Dict of component availability status
        """
        try:
            logger.info("Setting up application routes...")
            
            # Setup templates
            self._setup_templates()
            
            # Include core API routers
            await self._setup_core_routes(app, component_status)
            
            # Include component-specific routes
            await self._setup_component_routes(app, component_status)
            
            # Setup frontend routes
            self._setup_frontend_routes(app, component_status)
            
            # Setup system routes
            self._setup_system_routes(app, component_status)
            
            logger.info("Application routes configured successfully")
            
        except Exception as error:
            logger.error(f"Route setup failed: {error}")
            # Setup minimal fallback routes
            self._setup_fallback_routes(app)
    
    def _setup_templates(self) -> None:
        """Setup Jinja2 templates."""
        try:
            template_dirs = [
                "frontend/templates",
                "templates",
                "app/templates"
            ]
            
            for template_dir in template_dirs:
                if Path(template_dir).exists():
                    self.templates = Jinja2Templates(directory=template_dir)
                    logger.info(f"Templates loaded from: {template_dir}")
                    break
            
            if not self.templates:
                logger.warning("No template directory found")
                
        except Exception as error:
            logger.error(f"Template setup error: {error}")
    
    async def _setup_core_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup core API routes that should always be available."""
        try:
            # Load dashboard routes
            try:
                from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router
                app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
                app.include_router(tokens_router, prefix="/api/v1", tags=["tokens"])
                logger.info("Core API routers included")
            except ImportError:
                # Create fallback dashboard routes
                dashboard_router = self._create_fallback_dashboard_router()
                tokens_router = self._create_fallback_tokens_router()
                app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
                app.include_router(tokens_router, prefix="/api/v1", tags=["tokens"])
                logger.info("Fallback dashboard routers created")
                
        except Exception as error:
            logger.error(f"Core routes setup error: {error}")
    
    async def _setup_component_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup component-specific routes based on availability."""
        # AI Risk Assessment API
        if component_status.get("ai_api_endpoints") and component_status.get("ai_risk_assessment"):
            try:
                from app.api.v1.endpoints.ai_risk_api import ai_risk_router
                app.include_router(ai_risk_router, prefix="/api/v1/ai-risk", tags=["ai-risk"])
                logger.info("AI Risk Assessment router included")
            except ImportError as e:
                logger.warning(f"AI Risk Assessment router not available: {e}")
        
        # Live Trading API (Phase 4A)
        if component_status.get("live_trading_api"):
            try:
                from app.api.v1.endpoints.live_trading_fixed import router as live_trading_router
                app.include_router(live_trading_router, prefix="/api/v1", tags=["live-trading"])
                logger.info("Phase 4A live trading router included")
            except ImportError as e:
                logger.warning(f"Phase 4A live trading router not available: {e}")
    
    def _setup_frontend_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup frontend routes using the ORIGINAL working template approach."""
        
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve the main trading dashboard with sidebar."""
            try:
                logger.info("Serving dashboard with proper sidebar layout")
                
                # Check template exists
                dashboard_path = Path("frontend/templates/pages/dashboard.html")
                if not dashboard_path.exists():
                    logger.error("Dashboard template not found!")
                    # Return error page
                    return HTMLResponse("""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Dashboard Setup</title>
                        <style>
                            body { font-family: Arial; padding: 50px; text-align: center; }
                            .message { background: #f0f0f0; padding: 30px; border-radius: 10px; }
                        </style>
                    </head>
                    <body>
                        <div class="message">
                            <h2>Dashboard template missing!</h2>
                            <p>Run: <code>python cleanup_dashboard.py</code> to fix</p>
                            <p>Then restart the server</p>
                        </div>
                    </body>
                    </html>
                    """)
                
                if self.templates:
                    return self.templates.TemplateResponse(
                        "pages/dashboard.html",
                        {"request": request}
                    )
                else:
                    raise Exception("Templates not initialized")
                    
            except Exception as error:
                logger.error(f"Dashboard error: {error}")
                # Return error page, not landing page
                return HTMLResponse(f"""
                <html>
                <head><title>Dashboard Error</title></head>
                <body style="padding: 50px; font-family: Arial;">
                    <h1>Dashboard Loading Error</h1>
                    <p>Error: {error}</p>
                    <p>Please check that frontend/templates/pages/dashboard.html exists.</p>
                </body>
                </html>
                """, status_code=500)
        
        @app.get("/", response_class=HTMLResponse)  
        async def root_redirect(request: Request) -> HTMLResponse:
            """Root redirect to dashboard - ORIGINAL VERSION."""
            return await serve_dashboard(request)
        
        @app.get("/risk-analysis", response_class=HTMLResponse)
        async def serve_risk_analysis(request: Request) -> HTMLResponse:
            """Serve risk analysis - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection - redirect to dashboard for now."""
            return await serve_dashboard(request)
        
        logger.info("Frontend routes configured with ORIGINAL template approach")
    
    def _setup_system_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup system health and status routes."""
        
        @app.get("/api/v1/health")
        async def health_check() -> Dict[str, Any]:
            """Comprehensive health check endpoint."""
            try:
                return await self.system_info.get_comprehensive_health_status(component_status)
            except Exception as error:
                logger.error(f"Health check error: {error}")
                return await self.system_info.get_fallback_health_status(str(error))
        
        @app.get("/api/v1/status")
        async def system_status() -> Dict[str, Any]:
            """System status endpoint."""
            try:
                return await self.system_info.get_comprehensive_system_info(component_status)
            except Exception as error:
                logger.error(f"Status endpoint error: {error}")
                return await self.system_info.get_fallback_system_info(component_status, str(error))
        
        logger.info("System routes configured")
    
    def _setup_fallback_routes(self, app: FastAPI) -> None:
        """Setup minimal fallback routes."""
        
        @app.get("/fallback")
        async def fallback_root():
            """Fallback root endpoint."""
            return {
                "message": "DEX Sniper Pro - AI-Powered Trading Bot API",
                "status": "limited_functionality",
                "version": "4.1.0-beta",
                "endpoints": {
                    "health": "/api/v1/health",
                    "docs": "/docs"
                }
            }
        
        @app.get("/fallback/health")
        async def fallback_health():
            """Fallback health endpoint."""
            return {
                "status": "limited",
                "service": "DEX Sniper Pro",
                "message": "Running in fallback mode",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        logger.info("Fallback routes configured")
    
    async def _render_dashboard_template(
        self,
        request: Request,
        context: Dict[str, Any]
    ) -> HTMLResponse:
        """
        Render the original dashboard template with proper error handling.
        
        Args:
            request: FastAPI request object
            context: Template context variables
            
        Returns:
            HTMLResponse with rendered dashboard template
        """
        try:
            if self.templates:
                # Try to render the original dashboard template
                template_paths = [
                    "pages/dashboard.html",
                    "dashboard.html",
                    "base/dashboard.html"
                ]
                
                for template_path in template_paths:
                    try:
                        return self.templates.TemplateResponse(
                            template_path,
                            {"request": request, **context}
                        )
                    except Exception as e:
                        logger.debug(f"Template {template_path} not found: {e}")
                        continue
                
                # If no template found, create a professional fallback
                return self._create_professional_dashboard_fallback(context)
            else:
                return self._create_professional_dashboard_fallback(context)
                
        except Exception as error:
            logger.error(f"Dashboard template rendering error: {error}")
            return self._create_professional_dashboard_fallback(context)
    
    def _create_professional_dashboard_fallback(self, context: Dict[str, Any]) -> HTMLResponse:
        """Create a professional dashboard fallback."""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DEX Sniper Pro - Dashboard</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f5f5f5;
                }
                .container { 
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 2rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                }
                .card {
                    background: white;
                    padding: 1.5rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>DEX Sniper Pro Dashboard</h1>
                    <p>Professional Trading Interface</p>
                </div>
                <div class="card">
                    <h2>Template Loading...</h2>
                    <p>The dashboard template is being loaded. If this persists, check the template configuration.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    def _create_fallback_dashboard_router(self) -> APIRouter:
        """Create fallback dashboard router."""
        router = APIRouter(prefix="/dashboard", tags=["dashboard"])
        
        @router.get("/stats")
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
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @router.get("/health")
        async def fallback_dashboard_health():
            """Fallback dashboard health."""
            return {
                "status": "healthy",
                "components": {
                    "api": "operational",
                    "database": "operational",
                    "websocket": "operational"
                }
            }
        
        return router
    
    def _create_fallback_tokens_router(self) -> APIRouter:
        """Create fallback tokens router."""
        router = APIRouter(prefix="/tokens", tags=["tokens"])
        
        @router.get("/discover")
        async def fallback_token_discovery():
            """Fallback token discovery."""
            return {
                "discovered_tokens": [],
                "total_discovered": 0,
                "discovery_rate": "0 tokens/hour",
                "last_discovery": None,
                "status": "fallback_mode",
                "supported_networks": ["ethereum", "polygon", "bsc", "arbitrum"]
            }
        
        @router.get("/live")
        async def fallback_live_tokens():
            """Fallback live tokens."""
            return {
                "tokens": [],
                "total": 0,
                "last_update": datetime.utcnow().isoformat()
            }
        
        return router


# Create a singleton instance
route_manager = RouteManager()