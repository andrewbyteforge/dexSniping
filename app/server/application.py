"""
FastAPI Application Factory
File: app/server/application.py

Creates and configures the FastAPI application with all middleware,
routes, and static file serving.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.server.middleware import setup_middleware
from app.server.routes import setup_routes
from app.core.trading.trading_engine import TradingEngine
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global trading engine instance
trading_engine_instance: TradingEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handle application startup and shutdown.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Application lifecycle context
    """
    # Startup
    logger.info("Initializing DEX Sniper Pro Trading Engine...")
    
    try:
        global trading_engine_instance
        trading_engine_instance = TradingEngine()
        await trading_engine_instance.initialize()
        
        # Store in app state for access by routes
        app.state.trading_engine = trading_engine_instance
        
        logger.info("Trading engine initialized successfully")
        
    except Exception as error:
        logger.error(f"Failed to initialize trading engine: {error}")
        raise
    
    # Application is ready
    yield
    
    # Shutdown
    logger.info("Shutting down DEX Sniper Pro Trading Engine...")
    
    try:
        if trading_engine_instance:
            await trading_engine_instance.shutdown()
        logger.info("Trading engine shutdown complete")
        
    except Exception as error:
        logger.error(f"Error during shutdown: {error}")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
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
            version="3.1.0",
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
        
        logger.info("FastAPI application created successfully")
        return app
        
    except Exception as error:
        logger.error(f"Failed to create FastAPI application: {error}")
        raise RuntimeError(f"Application creation failed: {error}")


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
            logger.info(f"Mounted static files from: {frontend_static_path}")
        else:
            logger.warning(f"Frontend static directory not found: {frontend_static_path}")
        
        # Additional static directories can be added here
        # Example: Documentation assets, uploaded files, etc.
        
    except Exception as error:
        logger.error(f"Failed to setup static files: {error}")
        raise RuntimeError(f"Static file setup failed: {error}")


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