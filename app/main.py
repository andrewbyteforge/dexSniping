"""
DEX Sniper Pro - Enhanced Main Application
File: app/main.py

Professional cryptocurrency trading bot with comprehensive error handling,
progressive enhancement, and Phase 4D compatibility.
"""

import sys
import asyncio
import os
import traceback
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, Optional, List

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ==================== LOGGING SETUP ====================

def setup_logging():
    """Setup comprehensive logging system with fallbacks."""
    import logging
    
    # Try enhanced logger first, then fallback to basic
    try:
        from app.core.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("LOGGER: Enhanced logging system initialized")
        return logger
    except ImportError:
        try:
            from app.utils.logger import setup_logger
            logger = setup_logger(__name__)
            logger.info("LOGGER: Standard logging system initialized")
            return logger
        except ImportError:
            # Fallback to basic logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler('dex_sniper.log', encoding='utf-8')
                ]
            )
            logger = logging.getLogger(__name__)
            logger.info("LOGGER: Basic fallback logging system initialized")
            return logger

logger = setup_logging()

# ==================== EXCEPTION CLASSES ====================

class DEXSniperError(Exception):
    """Base exception for DEX Sniper Pro."""
    pass

class ComponentInitializationError(DEXSniperError):
    """Exception raised when component initialization fails."""
    pass

class RoutingError(DEXSniperError):
    """Exception raised when route setup fails."""
    pass

# Import Phase 4D exceptions with comprehensive fallbacks
try:
    from app.core.exceptions import TradingError, AIError, WalletError, DEXError
    logger.info("EXCEPTIONS: Phase 4D exception classes imported")
except ImportError:
    logger.warning("EXCEPTIONS: Using fallback exception classes")
    
    class TradingError(DEXSniperError):
        """Trading-related error."""
        pass
    
    class AIError(DEXSniperError):
        """AI system error."""
        pass
    
    class WalletError(DEXSniperError):
        """Wallet integration error."""
        pass
    
    class DEXError(DEXSniperError):
        """DEX integration error."""
        pass

# ==================== COMPONENT AVAILABILITY DETECTION ====================

class ComponentRegistry:
    """Registry for tracking available components and their status."""
    
    def __init__(self):
        self.components = {}
        self.initialization_errors = {}
        self.detect_available_components()
    
    def detect_available_components(self):
        """Detect which Phase 4D components are available."""
        
        # Snipe Trading Controller
        try:
            from app.core.trading.snipe_trading_controller import (
                initialize_snipe_trading_controller,
                get_snipe_trading_controller
            )
            self.components['snipe_trading'] = {
                'available': True,
                'initialize_func': initialize_snipe_trading_controller,
                'get_func': get_snipe_trading_controller,
                'description': 'Advanced snipe trading with real-time execution'
            }
            logger.info("COMPONENT: Snipe trading controller detected")
        except ImportError as e:
            self.components['snipe_trading'] = {
                'available': False,
                'error': str(e),
                'description': 'Advanced snipe trading (not available)'
            }
            logger.warning(f"COMPONENT: Snipe trading controller not available: {e}")
        
        # AI Risk Assessment Engine
        try:
            from app.core.ai.risk_assessment_engine import (
                initialize_ai_risk_engine,
                get_ai_risk_engine
            )
            self.components['ai_risk'] = {
                'available': True,
                'initialize_func': initialize_ai_risk_engine,
                'get_func': get_ai_risk_engine,
                'description': 'Machine learning-powered risk analysis'
            }
            logger.info("COMPONENT: AI risk assessment engine detected")
        except ImportError as e:
            self.components['ai_risk'] = {
                'available': False,
                'error': str(e),
                'description': 'AI risk assessment (not available)'
            }
            logger.warning(f"COMPONENT: AI risk assessment engine not available: {e}")
        
        # Enhanced Wallet Manager
        try:
            from app.core.wallet.enhanced_wallet_manager import EnhancedWalletManager
            self.components['wallet_manager'] = {
                'available': True,
                'class': EnhancedWalletManager,
                'description': 'MetaMask, WalletConnect multi-network support'
            }
            logger.info("COMPONENT: Enhanced wallet manager detected")
        except ImportError as e:
            self.components['wallet_manager'] = {
                'available': False,
                'error': str(e),
                'description': 'Wallet integration (not available)'
            }
            logger.warning(f"COMPONENT: Enhanced wallet manager not available: {e}")
        
        # Database Persistence Manager
        try:
            from app.core.database.persistence_manager import initialize_persistence_system
            self.components['database'] = {
                'available': True,
                'initialize_func': initialize_persistence_system,
                'description': 'Database persistence and data management'
            }
            logger.info("COMPONENT: Database system detected")
        except ImportError as e:
            self.components['database'] = {
                'available': False,
                'error': str(e),
                'description': 'Database persistence (not available)'
            }
            logger.warning(f"COMPONENT: Database system not available: {e}")
        
        # Live Trading Engine
        try:
            from app.core.trading.live_trading_engine_enhanced import initialize_trading_system
            self.components['trading_engine'] = {
                'available': True,
                'initialize_func': initialize_trading_system,
                'description': 'Enhanced live trading execution engine'
            }
            logger.info("COMPONENT: Live trading engine detected")
        except ImportError as e:
            self.components['trading_engine'] = {
                'available': False,
                'error': str(e),
                'description': 'Live trading engine (not available)'
            }
            logger.warning(f"COMPONENT: Live trading engine not available: {e}")
    
    def is_available(self, component_name: str) -> bool:
        """Check if a component is available."""
        return self.components.get(component_name, {}).get('available', False)
    
    def get_component_info(self, component_name: str) -> Dict[str, Any]:
        """Get information about a component."""
        return self.components.get(component_name, {})
    
    def get_available_components(self) -> List[str]:
        """Get list of available component names."""
        return [name for name, info in self.components.items() if info.get('available', False)]
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all component statuses."""
        available = self.get_available_components()
        unavailable = [name for name in self.components.keys() if name not in available]
        
        return {
            'total_components': len(self.components),
            'available_count': len(available),
            'unavailable_count': len(unavailable),
            'available_components': available,
            'unavailable_components': unavailable,
            'compatibility_mode': len(available) == 0
        }

# Global component registry
component_registry = ComponentRegistry()

# Global application state
app_state = {
    'initialized_components': {},
    'startup_time': None,
    'startup_errors': [],
    'startup_warnings': []
}

# ==================== COMPONENT INITIALIZATION ====================

async def initialize_component(component_name: str, component_info: Dict[str, Any]) -> Optional[Any]:
    """Initialize a single component with comprehensive error handling."""
    
    if not component_info.get('available', False):
        logger.info(f"INIT: Skipping {component_name} - not available")
        return None
    
    try:
        logger.info(f"INIT: Initializing {component_name}...")
        
        if 'initialize_func' in component_info:
            # Async initialization function
            component_instance = await component_info['initialize_func']()
        elif 'class' in component_info:
            # Direct class instantiation
            component_instance = component_info['class']()
        else:
            raise ComponentInitializationError(f"No initialization method found for {component_name}")
        
        app_state['initialized_components'][component_name] = component_instance
        logger.info(f"INIT: {component_name} initialized successfully")
        return component_instance
        
    except Exception as error:
        error_msg = f"Failed to initialize {component_name}: {error}"
        logger.error(f"INIT: {error_msg}")
        logger.debug(f"INIT: {component_name} traceback: {traceback.format_exc()}")
        
        app_state['startup_errors'].append({
            'component': component_name,
            'error': str(error),
            'traceback': traceback.format_exc()
        })
        
        component_registry.initialization_errors[component_name] = error
        return None

async def initialize_all_components() -> Dict[str, Any]:
    """Initialize all available components."""
    
    logger.info("INIT: Starting component initialization phase...")
    initialization_results = {}
    
    # Initialize components in dependency order
    initialization_order = [
        'database',
        'wallet_manager', 
        'trading_engine',
        'ai_risk',
        'snipe_trading'
    ]
    
    for component_name in initialization_order:
        if component_name in component_registry.components:
            component_info = component_registry.components[component_name]
            
            try:
                result = await initialize_component(component_name, component_info)
                initialization_results[component_name] = {
                    'success': result is not None,
                    'instance': result,
                    'error': None
                }
                
                if result is not None:
                    logger.info(f"INIT: ✅ {component_name} ready")
                else:
                    logger.warning(f"INIT: ⚠️ {component_name} skipped")
                    
            except Exception as error:
                initialization_results[component_name] = {
                    'success': False,
                    'instance': None,
                    'error': str(error)
                }
                logger.error(f"INIT: ❌ {component_name} failed: {error}")
    
    # Log summary
    successful = sum(1 for result in initialization_results.values() if result['success'])
    total = len(initialization_results)
    
    logger.info(f"INIT: Component initialization complete: {successful}/{total} successful")
    
    if successful == 0:
        logger.warning("INIT: Running in compatibility mode - no Phase 4D components available")
        app_state['startup_warnings'].append("Running in compatibility mode")
    
    return initialization_results

# ==================== APPLICATION LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Enhanced application lifespan manager."""
    
    app_state['startup_time'] = datetime.now(timezone.utc)
    
    logger.info("=" * 80)
    logger.info("🚀 DEX SNIPER PRO - PHASE 4D ENHANCED STARTUP")
    logger.info("=" * 80)
    logger.info(f"STARTUP: Application version 4.0.0")
    logger.info(f"STARTUP: Startup time: {app_state['startup_time'].isoformat()}")
    logger.info(f"STARTUP: Python version: {sys.version}")
    logger.info(f"STARTUP: Working directory: {os.getcwd()}")
    
    try:
        # Component detection summary
        status_summary = component_registry.get_status_summary()
        logger.info(f"DETECTION: Found {status_summary['available_count']}/{status_summary['total_components']} components available")
        
        if status_summary['available_components']:
            logger.info(f"DETECTION: Available: {', '.join(status_summary['available_components'])}")
        
        if status_summary['unavailable_components']:
            logger.info(f"DETECTION: Unavailable: {', '.join(status_summary['unavailable_components'])}")
        
        # Initialize components
        initialization_results = await initialize_all_components()
        
        # Store initialization results in app state
        app.state.component_registry = component_registry
        app.state.initialization_results = initialization_results
        app.state.app_state = app_state
        
        # Add initialized components to app state for easy access
        for component_name, result in initialization_results.items():
            if result['success'] and result['instance']:
                setattr(app.state, component_name, result['instance'])
        
        logger.info("✅ STARTUP: Application initialization completed successfully")
        
        if app_state['startup_warnings']:
            for warning in app_state['startup_warnings']:
                logger.warning(f"STARTUP: ⚠️ {warning}")
        
        if app_state['startup_errors']:
            logger.warning(f"STARTUP: ⚠️ {len(app_state['startup_errors'])} initialization errors occurred")
        
        logger.info("=" * 80)
        
    except Exception as error:
        logger.error(f"❌ STARTUP: Critical startup error: {error}")
        logger.error(f"STARTUP: Traceback: {traceback.format_exc()}")
        app_state['startup_errors'].append({
            'component': 'application',
            'error': str(error),
            'traceback': traceback.format_exc()
        })
        
        # Continue with limited functionality
        logger.warning("STARTUP: Continuing with limited functionality...")
    
    # Application is ready
    yield
    
    # Shutdown phase
    logger.info("=" * 80)
    logger.info("🔄 DEX SNIPER PRO - SHUTDOWN INITIATED")
    logger.info("=" * 80)
    
    try:
        await cleanup_components()
        logger.info("✅ SHUTDOWN: Application shutdown completed successfully")
    except Exception as error:
        logger.error(f"❌ SHUTDOWN: Error during shutdown: {error}")
    
    logger.info("=" * 80)

async def cleanup_components():
    """Cleanup all initialized components."""
    
    logger.info("CLEANUP: Starting component cleanup...")
    
    for component_name, component_instance in app_state['initialized_components'].items():
        try:
            logger.info(f"CLEANUP: Cleaning up {component_name}...")
            
            # Component-specific cleanup
            if component_name == 'snipe_trading' and hasattr(component_instance, 'active_snipes'):
                active_count = len(component_instance.active_snipes)
                if active_count > 0:
                    logger.info(f"CLEANUP: Cleaning up {active_count} active snipes...")
                    component_instance.active_snipes.clear()
            
            elif component_name == 'ai_risk' and hasattr(component_instance, 'assessment_cache'):
                cache_size = len(component_instance.assessment_cache)
                if cache_size > 0:
                    logger.info(f"CLEANUP: Clearing AI cache ({cache_size} entries)...")
                    component_instance.assessment_cache.clear()
            
            elif component_name == 'wallet_manager' and hasattr(component_instance, 'cleanup'):
                await component_instance.cleanup()
            
            logger.info(f"CLEANUP: ✅ {component_name} cleaned up")
            
        except Exception as error:
            logger.warning(f"CLEANUP: ⚠️ Error cleaning up {component_name}: {error}")
    
    logger.info("CLEANUP: Component cleanup completed")

# ==================== FASTAPI APPLICATION SETUP ====================

def create_fastapi_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    try:
        app = FastAPI(
            title="DEX Sniper Pro - Phase 4D Enhanced",
            description="Professional cryptocurrency trading bot with progressive enhancement and comprehensive error handling",
            version="4.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            lifespan=lifespan,
            debug=os.getenv("DEBUG", "False").lower() == "true"
        )
        
        logger.info("FASTAPI: Application instance created")
        return app
        
    except Exception as error:
        logger.error(f"FASTAPI: Failed to create application: {error}")
        raise DEXSniperError(f"Failed to create FastAPI application: {error}")

def setup_middleware(app: FastAPI) -> None:
    """Setup application middleware with error handling."""
    
    try:
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware  
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )
        
        logger.info("MIDDLEWARE: All middleware configured successfully")
        
    except Exception as error:
        logger.error(f"MIDDLEWARE: Setup failed: {error}")
        raise DEXSniperError(f"Middleware setup failed: {error}")

def setup_exception_handlers(app: FastAPI) -> None:
    """Setup comprehensive exception handlers."""
    
    @app.exception_handler(TradingError)
    async def trading_error_handler(request: Request, exc: TradingError):
        logger.error(f"TRADING_ERROR: {exc} for request {request.url}")
        return JSONResponse(
            status_code=400,
            content={
                "error_type": "trading_error",
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @app.exception_handler(AIError)
    async def ai_error_handler(request: Request, exc: AIError):
        logger.error(f"AI_ERROR: {exc} for request {request.url}")
        return JSONResponse(
            status_code=500,
            content={
                "error_type": "ai_error", 
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @app.exception_handler(WalletError)
    async def wallet_error_handler(request: Request, exc: WalletError):
        logger.error(f"WALLET_ERROR: {exc} for request {request.url}")
        return JSONResponse(
            status_code=400,
            content={
                "error_type": "wallet_error",
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @app.exception_handler(DEXError)
    async def dex_error_handler(request: Request, exc: DEXError):
        logger.error(f"DEX_ERROR: {exc} for request {request.url}")
        return JSONResponse(
            status_code=502,
            content={
                "error_type": "dex_error",
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @app.exception_handler(ComponentInitializationError)
    async def component_error_handler(request: Request, exc: ComponentInitializationError):
        logger.error(f"COMPONENT_ERROR: {exc} for request {request.url}")
        return JSONResponse(
            status_code=503,
            content={
                "error_type": "component_initialization_error",
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"GENERAL_ERROR: {exc} for request {request.url}")
        logger.debug(f"GENERAL_ERROR: Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "error_type": "internal_server_error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    logger.info("HANDLERS: Exception handlers configured")

def setup_static_files(app: FastAPI) -> None:
    """Setup static file serving with error handling."""
    
    try:
        static_paths = [
            Path("frontend/static"),
            Path("static"),
            Path("app/static")
        ]
        
        for static_path in static_paths:
            if static_path.exists():
                app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
                logger.info(f"STATIC: Static files mounted from {static_path}")
                break
        else:
            logger.warning("STATIC: No static directory found - static files not available")
            
    except Exception as error:
        logger.warning(f"STATIC: Failed to setup static files: {error}")

def setup_templates(app: FastAPI) -> Optional[Jinja2Templates]:
    """Setup Jinja2 templates with error handling."""
    
    try:
        template_paths = [
            Path("frontend/templates"),
            Path("templates"),
            Path("app/templates")
        ]
        
        for template_path in template_paths:
            if template_path.exists():
                templates = Jinja2Templates(directory=str(template_path))
                logger.info(f"TEMPLATES: Templates configured from {template_path}")
                return templates
        
        logger.warning("TEMPLATES: No template directory found - using fallback HTML")
        return None
        
    except Exception as error:
        logger.warning(f"TEMPLATES: Template setup failed: {error}")
        return None

# ==================== ROUTE SETUP ====================

def setup_api_routes(app: FastAPI) -> None:
    """Setup API routes with comprehensive error handling."""
    
    routes_loaded = []
    routes_failed = []
    
    # Core API routes (always attempt to load)
    api_routes = [
        ("app.api.v1.endpoints.dashboard", "dashboard_router", "dashboard"),
        ("app.api.v1.endpoints.tokens", "tokens_router", "tokens"),
        ("app.api.v1.endpoints.trading", "trading_router", "trading"),
        ("app.api.v1.endpoints.activity", "activity_router", "activity"),
    ]
    
    # Phase 4D API routes (load if components available)
    if component_registry.is_available('snipe_trading'):
        api_routes.append(("app.api.v1.endpoints.snipe_trading", "snipe_router", "snipe-trading"))
    
    if component_registry.is_available('ai_risk'):
        api_routes.append(("app.api.v1.endpoints.ai_risk", "ai_router", "ai-risk"))
    
    if component_registry.is_available('wallet_manager'):
        api_routes.append(("app.api.v1.endpoints.wallet", "wallet_router", "wallet"))
    
    # Enhanced live trading API
    try:
        from app.api.v1.endpoints.live_trading_api import router as live_trading_router
        app.include_router(live_trading_router, prefix="/api/v1", tags=["live-trading"])
        routes_loaded.append("live-trading-api")
        logger.info("ROUTES: Live trading API included")
    except ImportError as e:
        routes_failed.append(("live-trading-api", str(e)))
        logger.warning(f"ROUTES: Live trading API not available: {e}")
        setup_mock_live_trading_routes(app)
    
    # Load API routes
    for module_path, router_name, tag in api_routes:
        try:
            module = __import__(module_path, fromlist=[router_name])
            router = getattr(module, router_name)
            app.include_router(router, prefix="/api/v1", tags=[tag])
            routes_loaded.append(tag)
            logger.info(f"ROUTES: {tag} router included")
        except (ImportError, AttributeError) as e:
            routes_failed.append((tag, str(e)))
            logger.warning(f"ROUTES: {tag} router not available: {e}")
    
    # Summary
    logger.info(f"ROUTES: API routes loaded: {len(routes_loaded)}, failed: {len(routes_failed)}")
    if routes_loaded:
        logger.info(f"ROUTES: Loaded: {', '.join(routes_loaded)}")
    if routes_failed:
        logger.warning(f"ROUTES: Failed: {', '.join([f'{tag}({error})' for tag, error in routes_failed])}")

def setup_mock_live_trading_routes(app: FastAPI) -> None:
    """Setup mock live trading routes for testing."""
    
    from fastapi import APIRouter
    
    mock_router = APIRouter(prefix="/live-trading", tags=["mock-live-trading"])
    
    @mock_router.get("/health")
    async def mock_health():
        return {
            "status": "healthy",
            "service": "Mock Live Trading API",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "This is a mock implementation for testing"
        }
    
    @mock_router.post("/wallet/connect")
    async def mock_wallet_connect(request: Dict[str, Any]):
        wallet_address = request.get('wallet_address', 'unknown')
        return {
            "connection_id": f"mock_{wallet_address[:8] if wallet_address != 'unknown' else 'unknown'}",
            "wallet_address": wallet_address,
            "wallet_type": request.get('wallet_type', 'metamask'),
            "connected_networks": request.get('requested_networks', ['ethereum']),
            "balances": {
                "ethereum": {
                    "native_balance": "1.5",
                    "native_symbol": "ETH", 
                    "usd_value": "3000.00",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            },
            "status": "connected",
            "session_expires": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "This is a mock connection for testing"
        }
    
    app.include_router(mock_router, prefix="/api/v1")
    logger.info("ROUTES: Mock live trading routes included")

def setup_frontend_routes(app: FastAPI, templates: Optional[Jinja2Templates]) -> None:
    """Setup frontend routes with template fallbacks."""
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Enhanced root endpoint with Phase 4D status."""
        return create_status_page("DEX Sniper Pro - Phase 4D", "home")
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Enhanced dashboard with live opportunities."""
        if templates:
            try:
                return templates.TemplateResponse("pages/dashboard.html", {"request": request})
            except Exception as e:
                logger.warning(f"FRONTEND: Dashboard template error: {e}")
        
        return create_enhanced_dashboard_page()
    
    @app.get("/activity", response_class=HTMLResponse)
    async def activity(request: Request):
        """Trading activity page."""
        if templates:
            try:
                return templates.TemplateResponse("pages/activity.html", {"request": request})
            except Exception as e:
                logger.warning(f"FRONTEND: Activity template error: {e}")
        
        return create_activity_page()
    
    @app.get("/wallet-connection", response_class=HTMLResponse)
    async def wallet_connection():
        """Wallet connection interface."""
        return create_wallet_connection_page()
    
    logger.info("ROUTES: Frontend routes configured")

def setup_system_routes(app: FastAPI) -> None:
    """Setup system health and monitoring routes."""
    
    @app.get("/health")
    async def health_check():
        """Comprehensive health check with component status."""
        
        status_summary = component_registry.get_status_summary()
        
        health_data = {
            "status": "healthy",
            "service": "DEX Sniper Pro - Phase 4D Enhanced",
            "version": "4.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - app_state['startup_time']).total_seconds() if app_state['startup_time'] else 0,
            "components": {
                "total": status_summary['total_components'],
                "available": status_summary['available_count'],
                "unavailable": status_summary['unavailable_count'],
                "compatibility_mode": status_summary['compatibility_mode']
            },
            "features": {
                component: component_registry.is_available(component)
                for component in component_registry.components.keys()
            },
            "startup_errors": len(app_state['startup_errors']),
            "startup_warnings": len(app_state['startup_warnings'])
        }
        
        # Add component-specific health checks
        for component_name in status_summary['available_components']:
            if component_name in app_state['initialized_components']:
                instance = app_state['initialized_components'][component_name]
                if hasattr(instance, 'health_check'):
                    try:
                        component_health = await instance.health_check()
                        health_data[f"{component_name}_health"] = component_health
                    except Exception as e:
                        health_data[f"{component_name}_health"] = {"status": "error", "error": str(e)}
        
        return health_data
    
    @app.get("/status")
    async def detailed_status():
        """Detailed application status information."""
        
        return {
            "application": "DEX Sniper Pro",
            "version": "4.0.0",
            "phase": "4D - Enhanced with Progressive Loading",
            "startup_time": app_state['startup_time'].isoformat() if app_state['startup_time'] else None,
            "component_registry": component_registry.get_status_summary(),
            "initialized_components": list(app_state['initialized_components'].keys()),
            "startup_errors": app_state['startup_errors'],
            "startup_warnings": app_state['startup_warnings'],
            "features": {
                name: info.get('description', 'No description')
                for name, info in component_registry.components.items()
            },
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "dashboard": "/dashboard",
                "api_docs": "/api/docs",
                "wallet_connect": "/api/v1/live-trading/wallet/connect"
            }
        }
    
    @app.get("/api/v1/system/info")
    async def system_info():
        """System information API endpoint."""
        return await detailed_status()
    
    logger.info("ROUTES: System routes configured")

# ==================== HTML PAGE GENERATORS ====================

def create_status_page(title: str, page_type: str) -> HTMLResponse:
    """Create enhanced status page with Phase 4D information."""
    
    status_summary = component_registry.get_status_summary()
    features_status = {
        name: "ACTIVE" if info.get('available', False) else "NOT AVAILABLE"
        for name, info in component_registry.components.items()
    }
    
    compatibility_notice = ""
    if status_summary['compatibility_mode']:
        compatibility_notice = """
        <div class="alert alert-warning">
            <strong>COMPATIBILITY MODE ACTIVE</strong><br>
            This application uses progressive enhancement. Phase 4D features will automatically 
            activate as components become available. Core functionality is always operational.
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 3rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                max-width: 1000px;
                margin: 2rem;
            }}
            h1 {{
                font-size: 3rem;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            .version-badge {{
                background: linear-gradient(45deg, #ff6b6b, #feca57);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin: 1rem 0;
            }}
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }}
            .status-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                border-radius: 10px;
                text-align: left;
            }}
            .feature-item {{
                margin: 0.5rem 0;
                padding: 0.5rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .status-active {{ color: #4ade80; }}
            .status-inactive {{ color: #fbbf24; }}
            .btn {{
                display: inline-block;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                margin: 10px;
                transition: all 0.3s ease;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}
            .btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                color: white;
                text-decoration: none;
            }}
            .alert {{
                background: rgba(255, 193, 7, 0.2);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border: 1px solid rgba(255, 193, 7, 0.5);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1><i class="bi bi-lightning-charge"></i> DEX Sniper Pro</h1>
            <div class="version-badge">Phase 4D Enhanced - v4.0.0</div>
            <p class="lead">Professional Trading Bot with Progressive Enhancement & Comprehensive Error Handling</p>
            
            <div class="status-grid">
                <div class="status-card">
                    <h5><i class="bi bi-gear"></i> System Status</h5>
                    <div class="feature-item">
                        <span>Application Status</span>
                        <span class="status-active"><i class="bi bi-check-circle"></i> OPERATIONAL</span>
                    </div>
                    <div class="feature-item">
                        <span>Components Available</span>
                        <span>{status_summary['available_count']}/{status_summary['total_components']}</span>
                    </div>
                    <div class="feature-item">
                        <span>Compatibility Mode</span>
                        <span class="{'status-inactive' if status_summary['compatibility_mode'] else 'status-active'}">
                            {'ACTIVE' if status_summary['compatibility_mode'] else 'DISABLED'}
                        </span>
                    </div>
                </div>
                
                <div class="status-card">
                    <h5><i class="bi bi-cpu"></i> Phase 4D Features</h5>
                    {chr(10).join([f'<div class="feature-item"><span>{name.replace("_", " ").title()}</span><span class="{"status-active" if status == "ACTIVE" else "status-inactive"}">{status}</span></div>' for name, status in features_status.items()])}
                </div>
                
                <div class="status-card">
                    <h5><i class="bi bi-list-check"></i> Core Features</h5>
                    <div class="feature-item">
                        <span>Enhanced Dashboard</span>
                        <span class="status-active">ALWAYS AVAILABLE</span>
                    </div>
                    <div class="feature-item">
                        <span>Live Token Discovery</span>
                        <span class="status-active">ALWAYS AVAILABLE</span>
                    </div>
                    <div class="feature-item">
                        <span>Trading Activity</span>
                        <span class="status-active">ALWAYS AVAILABLE</span>
                    </div>
                    <div class="feature-item">
                        <span>API Documentation</span>
                        <span class="status-active">ALWAYS AVAILABLE</span>
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <a href="/dashboard" class="btn"><i class="bi bi-speedometer2"></i> Enhanced Dashboard</a>
                <a href="/activity" class="btn"><i class="bi bi-clock-history"></i> Trading Activity</a>
                <a href="/wallet-connection" class="btn"><i class="bi bi-wallet2"></i> Wallet Connection</a>
                <a href="/api/docs" class="btn"><i class="bi bi-book"></i> API Documentation</a>
                <a href="/health" class="btn"><i class="bi bi-heart-pulse"></i> System Health</a>
                <a href="/status" class="btn"><i class="bi bi-info-circle"></i> Detailed Status</a>
            </div>
            
            {compatibility_notice}
            
            <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.8;">
                <i class="bi bi-shield-check"></i> Ready for development - Enhanced error handling and progressive enhancement active
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

def create_enhanced_dashboard_page() -> HTMLResponse:
    """Create the enhanced dashboard page with comprehensive features."""
    
    # This is the full dashboard HTML from the second document
    dashboard_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DEX Sniper Pro Dashboard - Phase 4D Enhanced</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { 
                background: #f8fafc; 
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(180deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                z-index: 1000;
                overflow-y: auto;
            }
            .main-content {
                margin-left: 280px;
                padding: 2rem;
            }
            .metric-card {
                background: linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                border: none;
                transition: transform 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
            }
            .opportunity-card {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                transition: all 0.2s ease;
                background: white;
            }
            .opportunity-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .token-symbol {
                font-weight: 700;
                font-size: 1.1rem;
            }
            .price-change-positive {
                color: #10b981;
                font-weight: 600;
            }
            .price-change-negative {
                color: #ef4444;
                font-weight: 600;
            }
            .risk-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .risk-low { background: #d1fae5; color: #065f46; }
            .risk-medium { background: #fef3c7; color: #92400e; }
            .risk-high { background: #fee2e2; color: #991b1b; }
            .network-badge {
                background: linear-gradient(45deg, rgb(102, 126, 234), rgb(118, 75, 162));
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
            }
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid rgb(102, 126, 234);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @media (max-width: 768px) {
                .sidebar { transform: translateX(-100%); }
                .main-content { margin-left: 0; }
            }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="p-4 text-center border-bottom border-light border-opacity-25">
                <h4 class="mb-0">DEX Sniper</h4>
                <small class="text-light opacity-75">Phase 4D v4.0</small>
            </div>
            <nav class="p-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link text-light active" href="/dashboard">
                            <i class="bi bi-speedometer2 me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/activity">
                            <i class="bi bi-clock-history me-2"></i>Activity
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/wallet-connection">
                            <i class="bi bi-wallet2 me-2"></i>Wallet
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/api/docs">
                            <i class="bi bi-book me-2"></i>API Docs
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/health">
                            <i class="bi bi-heart-pulse me-2"></i>Health
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2>Enhanced Trading Dashboard</h2>
                    <p class="text-muted mb-0">Real-time portfolio monitoring with live opportunities</p>
                </div>
                <div class="badge bg-success">
                    <i class="bi bi-dot"></i> Live
                </div>
            </div>

            <!-- Metrics Row -->
            <div class="row g-4 mb-4">
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="portfolioValue">$1,247.83</div>
                            <div class="opacity-75">Portfolio Value</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value text-success" id="dailyPnl">+$45.67</div>
                            <div class="opacity-75">Daily P&L</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="activePositions">3</div>
                            <div class="opacity-75">Active Positions</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="card metric-card h-100">
                        <div class="card-body text-center">
                            <div class="metric-value" id="successRate">78.5%</div>
                            <div class="opacity-75">Success Rate</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Live Opportunities Section -->
            <div class="row g-4 mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                <i class="bi bi-search text-primary"></i>
                                Live Opportunities
                            </h5>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="refreshOpportunities()">
                                    <i class="bi bi-arrow-clockwise"></i>
                                    Refresh
                                </button>
                                <span class="badge bg-success">
                                    <i class="bi bi-dot"></i>
                                    Live
                                </span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="opportunitiesContainer">
                                <div class="text-center">
                                    <div class="loading-spinner"></div>
                                    <p class="mt-2">Loading opportunities...</p>
                                </div>
                            </div>
                            
                            <div class="text-center mt-3">
                                <button class="btn btn-outline-primary" onclick="loadMoreOpportunities()">
                                    <i class="bi bi-plus-circle"></i>
                                    Load More Opportunities
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Enhanced API Testing Section -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="bi bi-code-square"></i> Enhanced API Testing Center</h5>
                </div>
                <div class="card-body">
                    <p>Test the enhanced API endpoints with comprehensive error handling:</p>
                    <div class="row g-2">
                        <div class="col-md-6">
                            <button class="btn btn-primary w-100" onclick="testAPI('/api/v1/dashboard/stats')">
                                <i class="bi bi-graph-up"></i> Dashboard Stats
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-success w-100" onclick="testAPI('/api/v1/tokens/discover')">
                                <i class="bi bi-search"></i> Token Discovery
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-info w-100" onclick="testAPI('/api/v1/tokens/trending')">
                                <i class="bi bi-fire"></i> Trending Tokens
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-warning w-100" onclick="testAPI('/health')">
                                <i class="bi bi-heart-pulse"></i> Health Check
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-secondary w-100" onclick="testAPI('/status')">
                                <i class="bi bi-info-circle"></i> System Status
                            </button>
                        </div>
                        <div class="col-md-6">
                            <button class="btn btn-dark w-100" onclick="refreshDashboard()">
                                <i class="bi bi-arrow-clockwise"></i> Refresh Data
                            </button>
                        </div>
                    </div>
                    <div id="apiResults" class="mt-3 p-3 bg-light rounded" style="display: none;"></div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Global variables
            let currentTokens = [];
            let isLoading = false;
            let errorCount = 0;
            const maxRetries = 3;
            
            console.log('DEX Sniper Pro Enhanced Dashboard initializing...');
            
            // Initialize dashboard with enhanced error handling
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Dashboard DOM loaded, starting initialization...');
                
                // Initialize with comprehensive error handling
                initializeDashboard();
                
                // Auto-refresh every 30 seconds with error recovery
                setInterval(() => {
                    if (!document.hidden && errorCount < maxRetries) {
                        refreshDashboard();
                        loadOpportunities();
                    }
                }, 30000);
                
                console.log('Dashboard initialization complete with enhanced error handling');
            });
            
            async function initializeDashboard() {
                try {
                    await Promise.all([
                        refreshDashboard(),
                        loadOpportunities()
                    ]);
                    errorCount = 0; // Reset error count on success
                } catch (error) {
                    console.error('Dashboard initialization failed:', error);
                    handleDashboardError(error, 'initialization');
                }
            }
            
            async function loadOpportunities(retryCount = 0) {
                if (isLoading) {
                    console.log('Already loading opportunities, skipping...');
                    return;
                }
                
                isLoading = true;
                const container = document.getElementById('opportunitiesContainer');
                
                try {
                    console.log(`Loading live opportunities from API (attempt ${retryCount + 1})...`);
                    
                    // Show loading state
                    if (retryCount === 0) {
                        container.innerHTML = `
                            <div class="text-center">
                                <div class="loading-spinner"></div>
                                <p class="mt-2">Loading opportunities...</p>
                            </div>
                        `;
                    }
                    
                    const response = await fetch('/api/v1/tokens/discover?limit=8', {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        signal: AbortSignal.timeout(10000) // 10 second timeout
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('API Response received:', data);
                    
                    if (data.tokens && data.tokens.length > 0) {
                        currentTokens = data.tokens;
                        displayOpportunities(data.tokens);
                        console.log(`Successfully displayed ${data.tokens.length} opportunities`);
                        errorCount = 0; // Reset error count on success
                    } else {
                        container.innerHTML = `
                            <div class="alert alert-info">
                                <i class="bi bi-info-circle"></i>
                                <strong>No opportunities found</strong><br>
                                The market may be quiet right now. Try refreshing in a moment.
                                <button class="btn btn-sm btn-outline-primary mt-2" onclick="loadOpportunities()">
                                    <i class="bi bi-arrow-clockwise"></i> Refresh Now
                                </button>
                            </div>
                        `;
                        console.log('No tokens in API response');
                    }
                    
                } catch (error) {
                    console.error('Failed to load opportunities:', error);
                    errorCount++;
                    
                    if (retryCount < maxRetries - 1) {
                        console.log(`Retrying in 2 seconds... (${retryCount + 1}/${maxRetries})`);
                        setTimeout(() => loadOpportunities(retryCount + 1), 2000);
                    } else {
                        container.innerHTML = `
                            <div class="alert alert-danger">
                                <i class="bi bi-exclamation-triangle"></i>
                                <strong>Unable to load opportunities</strong><br>
                                ${error.name}: ${error.message}<br>
                                <small class="text-muted">Error occurred at ${new Date().toLocaleTimeString()}</small>
                                <div class="mt-2">
                                    <button class="btn btn-sm btn-outline-danger" onclick="loadOpportunities()">
                                        <i class="bi bi-arrow-clockwise"></i> Try Again
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="testAPI('/health')">
                                        <i class="bi bi-heart-pulse"></i> Check System Health
                                    </button>
                                </div>
                            </div>
                        `;
                    }
                } finally {
                    isLoading = false;
                }
            }
            
            function displayOpportunities(tokens) {
                console.log('Starting to display opportunities:', tokens);
                const container = document.getElementById('opportunitiesContainer');
                
                if (!container) {
                    console.error('Container element not found!');
                    return;
                }
                
                if (!tokens || tokens.length === 0) {
                    container.innerHTML = '<p class="text-muted text-center">No opportunities available</p>';
                    console.log('No tokens to display');
                    return;
                }
                
                console.log(`Processing ${tokens.length} tokens for display`);
                
                try {
                    const opportunitiesHTML = tokens.map((token, index) => {
                        console.log(`Processing token ${index + 1}:`, token);
                        
                        // Safely access token properties with fallbacks
                        const symbol = token.symbol || 'UNKNOWN';
                        const name = token.name || 'Unknown Token';
                        const network = token.network || 'Unknown';
                        const price = token.price || '$0.000000';
                        const change24h = token.change_24h || 0;
                        const liquidity = token.liquidity || 0;
                        const riskLevel = token.risk_level || 'medium';
                        const riskScore = token.risk_score || 5.0;
                        const ageHours = token.age_hours || 1;
                        const address = token.address || '0x0000000000000000000000000000000000000000';
                        
                        const changeClass = change24h > 0 ? 'price-change-positive' : 'price-change-negative';
                        const changeIcon = change24h > 0 ? 'bi-trending-up' : 'bi-trending-down';
                        const riskClass = `risk-${riskLevel}`;
                        
                        return `
                            <div class="opportunity-card" data-token="${symbol}">
                                <div class="row align-items-center">
                                    <div class="col-md-3">
                                        <div class="d-flex align-items-center">
                                            <div>
                                                <div class="token-symbol">${symbol}</div>
                                                <small class="text-muted">${name}</small>
                                                <br>
                                                <span class="network-badge">${network}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <div class="fw-bold">${price}</div>
                                        <div class="${changeClass}">
                                            <i class="bi ${changeIcon}"></i>
                                            ${change24h > 0 ? '+' : ''}${change24h.toFixed(1)}%
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <small class="text-muted">Liquidity:</small>
                                        <div class="fw-bold">$${liquidity.toLocaleString()}</div>
                                    </div>
                                    <div class="col-md-2">
                                        <small class="text-muted">Risk:</small>
                                        <div>
                                            <span class="risk-badge ${riskClass}">
                                                ${riskLevel} (${riskScore})
                                            </span>
                                        </div>
                                    </div>
                                    <div class="col-md-2">
                                        <small class="text-muted">Age:</small>
                                        <div class="fw-bold">${formatAge(ageHours)}</div>
                                    </div>
                                    <div class="col-md-1 text-end">
                                        <button class="btn btn-primary btn-sm" onclick="snipeToken('${symbol}', '${address}')">
                                            <i class="bi bi-lightning"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');
                    
                    console.log('Generated HTML length:', opportunitiesHTML.length);
                    container.innerHTML = opportunitiesHTML;
                    console.log(`Successfully rendered ${tokens.length} opportunity cards`);
                    
                    // Verify that cards were actually added to DOM
                    const addedCards = container.querySelectorAll('.opportunity-card');
                    console.log(`Verification: ${addedCards.length} cards found in DOM`);
                    
                } catch (error) {
                    console.error('Error rendering opportunities:', error);
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-triangle"></i>
                            <strong>Display Error</strong><br>
                            Failed to render opportunities: ${error.message}
                        </div>
                    `;
                }
            }
            
            function formatAge(hours) {
                try {
                    if (hours < 1) return `${Math.round(hours * 60)}m`;
                    if (hours < 24) return `${Math.round(hours)}h`;
                    return `${Math.round(hours / 24)}d`;
                } catch (error) {
                    return 'Unknown';
                }
            }
            
            function snipeToken(symbol, address) {
                console.log(`Enhanced Snipe request: ${symbol} (${address})`);
                
                // Enhanced snipe functionality with error handling
                const snipeData = {
                    symbol: symbol,
                    address: address,
                    timestamp: new Date().toISOString(),
                    requestId: generateRequestId()
                };
                
                // Store snipe request for tracking
                localStorage.setItem(`snipe_${snipeData.requestId}`, JSON.stringify(snipeData));
                
                alert(`Enhanced Snipe ${symbol} functionality ready!\\nAddress: ${address}\\nRequest ID: ${snipeData.requestId}\\nThis will connect to your enhanced trading engine with Phase 4D features when available.`);
            }
            
            function generateRequestId() {
                return 'snipe_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }
            
            async function refreshOpportunities() {
                console.log('Manual refresh requested...');
                errorCount = 0; // Reset error count on manual refresh
                await loadOpportunities();
            }
            
            async function loadMoreOpportunities() {
                console.log('Loading more opportunities...');
                try {
                    const response = await fetch('/api/v1/tokens/discover?limit=15', {
                        signal: AbortSignal.timeout(10000)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    
                    if (data.tokens) {
                        currentTokens = [...currentTokens, ...data.tokens];
                        displayOpportunities(currentTokens.slice(0, 20)); // Show max 20
                        console.log(`Loaded ${data.tokens.length} additional opportunities`);
                    }
                } catch (error) {
                    console.error('Failed to load more opportunities:', error);
                    showErrorNotification('Failed to load additional opportunities', error.message);
                }
            }
            
            async function testAPI(endpoint) {
                const resultsDiv = document.getElementById('apiResults');
                resultsDiv.style.display = 'block';
                resultsDiv.innerHTML = `
                    <div class="d-flex align-items-center">
                        <div class="loading-spinner me-2"></div>
                        <strong>Testing:</strong> ${endpoint}...
                    </div>
                `;
                
                const startTime = performance.now();
                
                try {
                    const response = await fetch(endpoint, {
                        signal: AbortSignal.timeout(15000) // 15 second timeout
                    });
                    
                    const endTime = performance.now();
                    const responseTime = Math.round(endTime - startTime);
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultsDiv.className = 'mt-3 p-3 bg-success text-white rounded';
                        resultsDiv.innerHTML = `
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong><i class="bi bi-check-circle"></i> Success (${response.status})</strong>
                                    <small class="d-block">${endpoint}</small>
                                </div>
                                <span class="badge bg-light text-dark">${responseTime}ms</span>
                            </div>
                            <pre class="mt-2 mb-0" style="font-size: 0.8rem; max-height: 200px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                        `;
                    } else {
                        resultsDiv.className = 'mt-3 p-3 bg-danger text-white rounded';
                        resultsDiv.innerHTML = `
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong><i class="bi bi-x-circle"></i> Error (${response.status})</strong>
                                    <small class="d-block">${endpoint}</small>
                                </div>
                                <span class="badge bg-light text-dark">${responseTime}ms</span>
                            </div>
                            <pre class="mt-2 mb-0" style="font-size: 0.8rem; max-height: 200px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                        `;
                    }
                } catch (error) {
                    const endTime = performance.now();
                    const responseTime = Math.round(endTime - startTime);
                    
                    resultsDiv.className = 'mt-3 p-3 bg-danger text-white rounded';
                    resultsDiv.innerHTML = `
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong><i class="bi bi-exclamation-triangle"></i> Network Error</strong>
                                <small class="d-block">${endpoint}</small>
                            </div>
                            <span class="badge bg-light text-dark">${responseTime}ms</span>
                        </div>
                        <div class="mt-2">
                            <strong>Error:</strong> ${error.name}<br>
                            <strong>Message:</strong> ${error.message}<br>
                            <small class="text-light">Occurred at ${new Date().toLocaleTimeString()}</small>
                        </div>
                    `;
                }
            }
            
            async function refreshDashboard() {
                try {
                    console.log('Refreshing dashboard stats...');
                    const response = await fetch('/api/v1/dashboard/stats', {
                        signal: AbortSignal.timeout(10000)
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        console.log('Dashboard stats response:', result);
                        
                        if (result.status === 'success' && result.data) {
                            const data = result.data;
                            updateDashboardMetrics(data);
                            console.log('Dashboard metrics updated successfully');
                        }
                    } else {
                        console.warn(`Dashboard stats request failed: ${response.status}`);
                    }
                } catch (error) {
                    console.error('Dashboard refresh error:', error);
                    handleDashboardError(error, 'refresh');
                }
            }
            
            function updateDashboardMetrics(data) {
                try {
                    // Update metrics with error handling for each element
                    const updates = [
                        { id: 'portfolioValue', value: ' + (data.portfolio_value || '0.00') },
                        { id: 'dailyPnl', value: (data.daily_pnl >= 0 ? '+ : '-) + Math.abs(data.daily_pnl || 0) },
                        { id: 'successRate', value: (data.success_rate || '0') + '%' },
                        { id: 'activePositions', value: data.active_trades || '0' }
                    ];
                    
                    updates.forEach(update => {
                        const element = document.getElementById(update.id);
                        if (element) {
                            element.textContent = update.value;
                        } else {
                            console.warn(`Element ${update.id} not found for metric update`);
                        }
                    });
                    
                } catch (error) {
                    console.error('Error updating dashboard metrics:', error);
                }
            }
            
            function handleDashboardError(error, context) {
                console.error(`Dashboard error in ${context}:`, error);
                
                // Show user-friendly error notification
                showErrorNotification(`Dashboard ${context} failed`, error.message);
                
                // Implement exponential backoff for retries
                if (errorCount < maxRetries) {
                    const retryDelay = Math.pow(2, errorCount) * 1000; // 1s, 2s, 4s
                    console.log(`Scheduling retry in ${retryDelay}ms...`);
                    setTimeout(() => {
                        if (context === 'refresh') refreshDashboard();
                        else if (context === 'opportunities') loadOpportunities();
                    }, retryDelay);
                }
            }
            
            function showErrorNotification(title, message) {
                // Create and show a temporary error notification
                const notification = document.createElement('div');
                notification.className = 'alert alert-warning alert-dismissible fade show position-fixed';
                notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
                notification.innerHTML = `
                    <strong>${title}</strong><br>
                    <small>${message}</small>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                document.body.appendChild(notification);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 5000);
            }
            
            // Enhanced error recovery and monitoring
            window.addEventListener('error', function(event) {
                console.error('Global JavaScript error:', event.error);
                showErrorNotification('JavaScript Error', event.error.message);
            });
            
            window.addEventListener('unhandledrejection', function(event) {
                console.error('Unhandled promise rejection:', event.reason);
                showErrorNotification('Promise Rejection', event.reason.message || 'Unknown error');
            });
            
            // Network connectivity monitoring
            window.addEventListener('online', function() {
                console.log('Network connection restored');
                showErrorNotification('Connection Restored', 'Network connectivity has been restored');
                errorCount = 0; // Reset error count
                refreshDashboard();
                loadOpportunities();
            });
            
            window.addEventListener('offline', function() {
                console.warn('Network connection lost');
                showErrorNotification('Connection Lost', 'Network connectivity has been lost');
            });
            
            console.log('DEX Sniper Pro Enhanced Dashboard scripts loaded successfully with comprehensive error handling!');
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=dashboard_html)

def create_activity_page() -> HTMLResponse:
    """Create the enhanced activity page."""
    
    activity_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Activity - DEX Sniper Pro</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { 
                background: #f8fafc; 
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(180deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                color: white;
                z-index: 1000;
                overflow-y: auto;
            }
            .main-content {
                margin-left: 280px;
                padding: 2rem;
            }
            .activity-card {
                border-left: 4px solid #10b981;
                transition: transform 0.2s ease;
                margin-bottom: 1rem;
            }
            .activity-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .activity-card.sell {
                border-left-color: #ef4444;
            }
            .profit-positive { color: #10b981; font-weight: 600; }
            .profit-negative { color: #ef4444; font-weight: 600; }
            .activity-type-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .type-buy { background: #d1fae5; color: #065f46; }
            .type-sell { background: #fee2e2; color: #991b1b; }
            .type-snipe { background: #ddd6fe; color: #5b21b6; }
            @media (max-width: 768px) {
                .sidebar { transform: translateX(-100%); }
                .main-content { margin-left: 0; }
            }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="p-4 text-center border-bottom border-light border-opacity-25">
                <h4 class="mb-0">DEX Sniper</h4>
                <small class="text-light opacity-75">Phase 4D v4.0</small>
            </div>
            <nav class="p-3">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/dashboard">
                            <i class="bi bi-speedometer2 me-2"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light active" href="/activity">
                            <i class="bi bi-clock-history me-2"></i>Activity
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/wallet-connection">
                            <i class="bi bi-wallet2 me-2"></i>Wallet
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/api/docs">
                            <i class="bi bi-book me-2"></i>API Docs
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-light" href="/health">
                            <i class="bi bi-heart-pulse me-2"></i>Health
                        </a>
                    </li>
                </ul>
            </nav>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2><i class="bi bi-clock-history"></i> Trading Activity</h2>
                    <p class="text-muted mb-0">Complete history of trading operations with enhanced tracking</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-primary" onclick="refreshActivity()">
                        <i class="bi bi-arrow-clockwise"></i> Refresh
                    </button>
                    <div class="badge bg-success">
                        <i class="bi bi-dot"></i> Live
                    </div>
                </div>
            </div>

            <!-- Activity Summary Cards -->
            <div class="row g-4 mb-4">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="text-success">12</h5>
                            <small class="text-muted">Successful Trades</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="text-primary">5</h5>
                            <small class="text-muted">Active Positions</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="text-warning">3</h5>
                            <small class="text-muted">Pending Orders</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="text-success">+$156.78</h5>
                            <small class="text-muted">Today's P&L</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Activity Feed -->
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="bi bi-list"></i> Recent Activity</h5>
                </div>
                <div class="card-body">
                    <!-- Activity Items -->
                    <div class="activity-card card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="d-flex align-items-center mb-2">
                                        <span class="activity-type-badge type-snipe me-2">SNIPE</span>
                                        <h6 class="mb-0">PEPE Token Purchase</h6>
                                    </div>
                                    <p class="text-muted mb-1">Bought 1,000,000 PEPE at $0.00000123</p>
                                    <small class="text-muted">
                                        <i class="bi bi-clock"></i> 2 hours ago • 
                                        <i class="bi bi-hash"></i> 0x1234...5678
                                    </small>
                                </div>
                                <div class="text-end">
                                    <div class="profit-positive">+$33.40</div>
                                    <small class="text-muted">+26.8%</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="activity-card card sell">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="d-flex align-items-center mb-2">
                                        <span class="activity-type-badge type-sell me-2">SELL</span>
                                        <h6 class="mb-0">WOJAK Token Sale</h6>
                                    </div>
                                    <p class="text-muted mb-1">Sold 500,000 WOJAK at $0.000045</p>
                                    <small class="text-muted">
                                        <i class="bi bi-clock"></i> 4 hours ago • 
                                        <i class="bi bi-hash"></i> 0x5678...9012
                                    </small>
                                </div>
                                <div class="text-end">
                                    <div class="profit-positive">+$22.50</div>
                                    <small class="text-muted">+15.2%</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="activity-card card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="d-flex align-items-center mb-2">
                                        <span class="activity-type-badge type-buy me-2">BUY</span>
                                        <h6 class="mb-0">DOGE Token Purchase</h6>
                                    </div>
                                    <p class="text-muted mb-1">Bought 10,000 DOGE at $0.065</p>
                                    <small class="text-muted">
                                        <i class="bi bi-clock"></i> 6 hours ago • 
                                        <i class="bi bi-hash"></i> 0x9012...3456
                                    </small>
                                </div>
                                <div class="text-end">
                                    <div class="profit-negative">-$15.30</div>
                                    <small class="text-muted">-2.3%</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="activity-card card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="d-flex align-items-center mb-2">
                                        <span class="activity-type-badge type-snipe me-2">SNIPE</span>
                                        <h6 class="mb-0">SHIB Token Snipe</h6>
                                    </div>
                                    <p class="text-muted mb-1">Sniped 50,000,000 SHIB at launch</p>
                                    <small class="text-muted">
                                        <i class="bi bi-clock"></i> 1 day ago • 
                                        <i class="bi bi-hash"></i> 0x3456...7890
                                    </small>
                                </div>
                                <div class="text-end">
                                    <div class="profit-positive">+$89.25</div>
                                    <small class="text-muted">+45.7%</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Navigation -->
            <div class="text-center mt-4">
                <a href="/dashboard" class="btn btn-primary me-2">
                    <i class="bi bi-speedometer2"></i> Back to Dashboard
                </a>
                <button class="btn btn-outline-secondary" onclick="loadMoreActivity()">
                    <i class="bi bi-plus-circle"></i> Load More Activity
                </button>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function refreshActivity() {
                console.log('Refreshing activity feed...');
                // Add activity refresh logic here
                location.reload();
            }
            
            function loadMoreActivity() {
                console.log('Loading more activity...');
                alert('Load more activity functionality will be implemented with API integration');
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=activity_html)

def create_wallet_connection_page() -> HTMLResponse:
    """Create the wallet connection page."""
    
    wallet_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wallet Connection - DEX Sniper Pro</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%);
                font-family: 'Segoe UI', system-ui, sans-serif;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .wallet-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 3rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                max-width: 500px;
                width: 100%;
                text-align: center;
            }
            .wallet-option {
                border: 2px solid #e2e8f0;
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem 0;
                cursor: pointer;
                transition: all 0.3s ease;
                background: white;
            }
            .wallet-option:hover {
                border-color: rgb(102, 126, 234);
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            }
            .wallet-icon {
                width: 48px;
                height: 48px;
                margin-bottom: 1rem;
            }
            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-left: 8px;
            }
            .status-connected { background: #10b981; }
            .status-disconnected { background: #ef4444; }
            .status-pending { background: #f59e0b; animation: pulse 2s infinite; }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
    </head>
    <body>
        <div class="wallet-container">
            <h2 class="mb-4"><i class="bi bi-wallet2"></i> Connect Your Wallet</h2>
            <p class="text-muted mb-4">Choose your preferred wallet to start trading</p>
            
            <!-- MetaMask Option -->
            <div class="wallet-option" onclick="connectMetaMask()">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <div class="wallet-icon bg-warning rounded d-flex align-items-center justify-content-center">
                            <i class="bi bi-fox text-white h4 mb-0"></i>
                        </div>
                        <div class="ms-3 text-start">
                            <h6 class="mb-1">MetaMask</h6>
                            <small class="text-muted">Most popular Ethereum wallet</small>
                        </div>
                    </div>
                    <div>
                        <span id="metamask-status" class="status-indicator status-disconnected"></span>
                    </div>
                </div>
            </div>
            
            <!-- WalletConnect Option -->
            <div class="wallet-option" onclick="connectWalletConnect()">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <div class="wallet-icon bg-primary rounded d-flex align-items-center justify-content-center">
                            <i class="bi bi-qr-code text-white h4 mb-0"></i>
                        </div>
                        <div class="ms-3 text-start">
                            <h6 class="mb-1">WalletConnect</h6>
                            <small class="text-muted">Connect with QR code</small>
                        </div>
                    </div>
                    <div>
                        <span id="walletconnect-status" class="status-indicator status-disconnected"></span>
                    </div>
                </div>
            </div>
            
            <!-- Coinbase Wallet Option -->
            <div class="wallet-option" onclick="connectCoinbase()">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center">
                        <div class="wallet-icon bg-info rounded d-flex align-items-center justify-content-center">
                            <i class="bi bi-currency-bitcoin text-white h4 mb-0"></i>
                        </div>
                        <div class="ms-3 text-start">
                            <h6 class="mb-1">Coinbase Wallet</h6>
                            <small class="text-muted">Self-custody wallet</small>
                        </div>
                    </div>
                    <div>
                        <span id="coinbase-status" class="status-indicator status-disconnected"></span>
                    </div>
                </div>
            </div>
            
            <!-- Connection Status -->
            <div id="connection-status" class="mt-4 p-3 rounded" style="display: none;">
                <h6 id="status-title"></h6>
                <p id="status-message" class="mb-0"></p>
            </div>
            
            <!-- Navigation -->
            <div class="mt-4">
                <a href="/dashboard" class="btn btn-outline-primary me-2">
                    <i class="bi bi-arrow-left"></i> Back to Dashboard
                </a>
                <button class="btn btn-primary" onclick="testConnection()">
                    <i class="bi bi-lightning"></i> Test Connection
                </button>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            async function connectMetaMask() {
                console.log('Connecting to MetaMask...');
                updateStatus('metamask', 'pending');
                
                try {
                    if (typeof window.ethereum !== 'undefined') {
                        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                        
                        if (accounts.length > 0) {
                            const account = accounts[0];
                            updateStatus('metamask', 'connected');
                            showConnectionSuccess('MetaMask', account);
                            
                            // Test API connection
                            await testAPIConnection('metamask', account);
                        } else {
                            throw new Error('No accounts found');
                        }
                    } else {
                        throw new Error('MetaMask not installed');
                    }
                } catch (error) {
                    console.error('MetaMask connection error:', error);
                    updateStatus('metamask', 'disconnected');
                    showConnectionError('MetaMask', error.message);
                }
            }
            
            async function connectWalletConnect() {
                console.log('Connecting via WalletConnect...');
                updateStatus('walletconnect', 'pending');
                
                try {
                    // Simulate WalletConnect flow
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    const mockAccount = '0x' + Math.random().toString(16).substr(2, 40);
                    
                    updateStatus('walletconnect', 'connected');
                    showConnectionSuccess('WalletConnect', mockAccount);
                    
                    await testAPIConnection('walletconnect', mockAccount);
                } catch (error) {
                    console.error('WalletConnect error:', error);
                    updateStatus('walletconnect', 'disconnected');
                    showConnectionError('WalletConnect', error.message);
                }
            }
            
            async function connectCoinbase() {
                console.log('Connecting to Coinbase Wallet...');
                updateStatus('coinbase', 'pending');
                
                try {
                    // Simulate Coinbase Wallet connection
                    await new Promise(resolve => setTimeout(resolve, 1500));
                    const mockAccount = '0x' + Math.random().toString(16).substr(2, 40);
                    
                    updateStatus('coinbase', 'connected');
                    showConnectionSuccess('Coinbase Wallet', mockAccount);
                    
                    await testAPIConnection('coinbase', mockAccount);
                } catch (error) {
                    console.error('Coinbase Wallet error:', error);
                    updateStatus('coinbase', 'disconnected');
                    showConnectionError('Coinbase Wallet', error.message);
                }
            }
            
            function updateStatus(wallet, status) {
                const indicator = document.getElementById(`${wallet}-status`);
                indicator.className = `status-indicator status-${status}`;
            }
            
            function showConnectionSuccess(walletName, account) {
                const statusDiv = document.getElementById('connection-status');
                statusDiv.className = 'mt-4 p-3 rounded bg-success text-white';
                statusDiv.style.display = 'block';
                
                document.getElementById('status-title').textContent = `${walletName} Connected!`;
                document.getElementById('status-message').innerHTML = `
                    <strong>Account:</strong> ${account.substring(0, 6)}...${account.substring(account.length - 4)}<br>
                    <small>Ready for trading operations</small>
                `;
            }
            
            function showConnectionError(walletName, error) {
                const statusDiv = document.getElementById('connection-status');
                statusDiv.className = 'mt-4 p-3 rounded bg-danger text-white';
                statusDiv.style.display = 'block';
                
                document.getElementById('status-title').textContent = `${walletName} Connection Failed`;
                document.getElementById('status-message').textContent = error;
            }
            
            async function testAPIConnection(walletType, walletAddress) {
                try {
                    console.log('Testing API connection...');
                    
                    const response = await fetch('/api/v1/live-trading/wallet/connect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            wallet_type: walletType,
                            wallet_address: walletAddress,
                            requested_networks: ['ethereum']
                        })
                    });
                    
                    const data = await response.json();
                    console.log('API connection test result:', data);
                    
                    if (response.ok) {
                        console.log('API connection successful');
                    } else {
                        console.warn('API connection test failed:', data);
                    }
                } catch (error) {
                    console.error('API connection test error:', error);
                }
            }
            
            async function testConnection() {
                console.log('Testing wallet connection...');
                
                try {
                    const response = await fetch('/health');
                    const health = await response.json();
                    
                    alert(`System Health Check:\\n\\nStatus: ${health.status}\\nService: ${health.service}\\nComponents: ${Object.keys(health.features || {}).length} features available`);
                } catch (error) {
                    alert(`Connection test failed: ${error.message}`);
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=wallet_html)

# ==================== APPLICATION CREATION ====================

# Create the main FastAPI application
app = create_fastapi_app()

# Setup all components
setup_middleware(app)
setup_exception_handlers(app)

# Setup templates
templates = setup_templates(app)

# Setup static files
setup_static_files(app)

# Setup all routes
setup_api_routes(app)
setup_frontend_routes(app, templates)
setup_system_routes(app)

logger.info("APPLICATION: DEX Sniper Pro Phase 4D Enhanced application created successfully")

# ==================== DEVELOPMENT SERVER ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("🚀 DEX SNIPER PRO - PHASE 4D ENHANCED DEVELOPMENT SERVER")
    logger.info("=" * 80)
    logger.info("FEATURES: Comprehensive Error Handling & Progressive Enhancement")
    logger.info("  ✅ DASHBOARD: Enhanced Dashboard - Always Available")
    logger.info("  ✅ DISCOVERY: Live Token Discovery - Always Available")
    logger.info("  ✅ ACTIVITY: Trading Activity Tracking - Always Available")
    logger.info("  ✅ WALLET: Wallet Connection Interface - Always Available")
    logger.info("  🔄 SNIPE: Snipe Trading - Loads when components available")
    logger.info("  🔄 AI: AI Risk Assessment - Loads when components available")
    logger.info("  🔄 TRADING: Live Trading Engine - Loads when components available")
    logger.info("  ✅ ERROR HANDLING: Comprehensive error handling & recovery")
    logger.info("  ✅ MONITORING: Health checks & system monitoring")
    logger.info("=" * 80)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            reload_excludes=["*.log", "*.tmp", "__pycache__"]
        )
    except KeyboardInterrupt:
        logger.info("SHUTDOWN: Development server stopped by user")
    except Exception as error:
        logger.error(f"ERROR: Development server error: {error}")
        logger.error(f"TRACEBACK: {traceback.format_exc()}")
        raise