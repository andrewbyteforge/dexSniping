"""
Main FastAPI Application
File: app/main.py

Main application entry point for the DEX Sniper Pro trading bot.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.endpoints import live_trading
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global trading engine instance
trading_engine_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    global trading_engine_instance
    
    # Startup
    logger.info("🚀 Starting DEX Sniper Pro Trading Bot...")
    try:
        from app.core.trading.trading_engine import TradingEngine, NetworkType
        trading_engine_instance = TradingEngine(NetworkType.ETHEREUM)
        await trading_engine_instance.initialize()
        logger.info("✅ Trading engine initialized successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize trading engine: {e}")
        yield
    finally:
        # Shutdown
        logger.info("🛑 Shutting down trading bot...")
        if trading_engine_instance:
            try:
                await trading_engine_instance.stop_trading()
                logger.info("✅ Trading engine stopped successfully")
            except Exception as e:
                logger.error(f"❌ Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="DEX Sniper Pro API",
    description="Automated crypto trading bot with profit generation capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(live_trading.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "🤖 DEX Sniper Pro Trading Bot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "trading_endpoints": "/api/v1/live-trading"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global trading_engine_instance
    
    return {
        "status": "healthy",
        "trading_engine": trading_engine_instance is not None,
        "message": "Trading bot is operational"
    }


def get_trading_engine():
    """Get the global trading engine instance."""
    global trading_engine_instance
    if trading_engine_instance is None:
        raise HTTPException(status_code=503, detail="Trading engine not initialized")
    return trading_engine_instance


# Make trading engine available to endpoints
live_trading.set_trading_engine_getter(get_trading_engine)
