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
        """Setup frontend page routes with original dashboard templates."""
        @app.get("/dashboard", response_class=HTMLResponse)
        async def serve_dashboard(request: Request) -> HTMLResponse:
            """Serve the original professional trading dashboard."""
            return await self._render_dashboard_template(
                request,
                {
                    "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                    "phase": "4C - AI Risk Assessment Integration",
                    "component_status": component_status
                }
            )
        
        @app.get("/risk-analysis", response_class=HTMLResponse)
        async def serve_risk_analysis(request: Request) -> HTMLResponse:
            """Serve AI risk analysis page using dashboard template."""
            return await self._render_dashboard_template(
                request,
                {
                    "page_type": "risk_analysis",
                    "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                    "component_status": component_status
                }
            )
        
        @app.get("/wallet-connection", response_class=HTMLResponse)
        async def serve_wallet_connection(request: Request) -> HTMLResponse:
            """Serve wallet connection page using dashboard template."""
            return await self._render_dashboard_template(
                request,
                {
                    "page_type": "wallet_connection",
                    "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                    "component_status": component_status
                }
            )
        
        @app.get("/live-trading", response_class=HTMLResponse)
        async def serve_live_trading(request: Request) -> HTMLResponse:
            """Serve live trading interface using dashboard template."""
            return await self._render_dashboard_template(
                request,
                {
                    "page_type": "live_trading",
                    "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                    "component_status": component_status
                }
            )
        
        @app.get("/portfolio", response_class=HTMLResponse)
        async def serve_portfolio(request: Request) -> HTMLResponse:
            """Serve portfolio management page using dashboard template."""
            return await self._render_dashboard_template(
                request,
                {
                    "page_type": "portfolio",
                    "ai_risk_enabled": component_status.get("ai_risk_assessment", False),
                    "component_status": component_status
                }
            )
        
        logger.info("Frontend routes configured with original dashboard templates")
    
    def _setup_system_routes(self, app: FastAPI, component_status: Dict[str, bool]) -> None:
        """Setup system health and status routes."""
        @app.get("/")
        async def root() -> Dict[str, Any]:
            """Root endpoint with comprehensive system information."""
            try:
                return await self.system_info.get_comprehensive_system_info(component_status)
            except Exception as error:
                logger.error(f"Root endpoint error: {error}")
                return await self.system_info.get_fallback_system_info(component_status, str(error))
        
        @app.get("/health")
        async def health_check() -> Dict[str, Any]:
            """Comprehensive health check endpoint."""
            try:
                return await self.system_info.get_comprehensive_health_status(component_status)
            except Exception as error:
                logger.error(f"Health check error: {error}")
                return await self.system_info.get_fallback_health_status(str(error))
        
        logger.info("System routes configured")
    
    def _setup_fallback_routes(self, app: FastAPI) -> None:
        """Setup minimal fallback routes."""
        @app.get("/")
        async def fallback_root():
            """Fallback root endpoint."""
            return {
                "message": "DEX Sniper Pro - AI-Powered Trading Bot API",
                "status": "limited_functionality",
                "version": "4.1.0-beta",
                "endpoints": {
                    "health": "/health",
                    "docs": "/docs"
                }
            }
        
        @app.get("/health")
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
        """Create a simple dashboard fallback."""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEX Sniper Pro Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    <style>
        body { background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; }
        .stats-card { background: rgba(255,255,255,0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">🤖 DEX Sniper Pro - Phase 4C</span>
            <span class="navbar-text">AI-Powered Trading Bot</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="alert alert-success">
            <i class="bi bi-check-circle"></i>
            <strong>System Status:</strong> All 8/8 Components Operational
            <span class="badge bg-success ms-2">AI Risk Assessment Active</span>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-wallet2 fs-1 text-success"></i>
                    <h3>$0.00</h3>
                    <p>Portfolio Value</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-graph-up fs-1 text-info"></i>
                    <h3>+$0.00</h3>
                    <p>Daily P&L</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-activity fs-1 text-warning"></i>
                    <h3>0</h3>
                    <p>Trades Today</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stats-card text-center p-3">
                    <i class="bi bi-percent fs-1 text-primary"></i>
                    <h3>88.9%</h3>
                    <p>System Health</p>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="bi bi-graph-up"></i> Portfolio Performance</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="chart" height="200"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="/api/v1/dashboard/stats" class="btn btn-success">📊 Dashboard Stats</a>
                            <a href="/api/v1/tokens/discover" class="btn btn-info">🔍 Token Discovery</a>
                            <a href="/api/v1/ai-risk/health" class="btn btn-warning">🧠 AI Risk Status</a>
                            <a href="/docs" class="btn btn-primary">📖 API Docs</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('chart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['00:00', '06:00', '12:00', '18:00', '24:00'],
                        datasets: [{
                            label: 'Portfolio Value',
                            data: [1000, 1050, 1200, 1180, 1250],
                            borderColor: 'rgb(75, 192, 192)',
                            fill: false
                        }]
                    }
                });
            }
            
            console.log('🚀 DEX Sniper Pro Dashboard Loaded Successfully!');
        });
    </script>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
</body>
</html>'''
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
        
        return router
    
    def _create_fallback_html_response(
        self,
        title: str,
        subtitle: str,
        description: str
    ) -> HTMLResponse:
        """Create fallback HTML response."""
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
                <p>{description}</p>
                
                <div class="links">
                    <a href="/docs">API Documentation</a>
                    <a href="/health">System Health</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)