"""
Main FastAPI Application - Phase 4B Gradual Integration
File: app/main.py

Updated main.py that works with existing structure while gradually
integrating Phase 4B live blockchain features.
"""

import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

# Try to import live trading components, fall back to existing if not available
try:
    from app.utils.logger import setup_logger
    logger = setup_logger(__name__)
    logger_available = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger_available = False

# Global state
live_mode_enabled = False
blockchain_connected = False
network_manager = None
live_trading_engine = None


async def try_initialize_live_trading():
    """Try to initialize live trading components."""
    global live_mode_enabled, blockchain_connected, network_manager, live_trading_engine
    
    try:
        # Test blockchain connections first using our proven method
        from web3 import Web3
        
        logger.info("🔄 Testing blockchain connections...")
        
        # Test public RPCs (we know these work from earlier test)
        test_rpcs = [
            ('ethereum', 'https://ethereum.publicnode.com'),
            ('polygon', 'https://polygon-rpc.com'),
            ('bsc', 'https://bsc-dataseed.binance.org/')
        ]
        
        connected_networks = []
        for name, url in test_rpcs:
            try:
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 5}))
                if w3.is_connected():
                    block = w3.eth.block_number
                    connected_networks.append(name)
                    logger.info(f"✅ {name}: Connected (Block {block:,})")
            except Exception as e:
                logger.warning(f"⚠️ {name}: {str(e)[:50]}...")
        
        if connected_networks:
            blockchain_connected = True
            logger.info(f"🌐 Blockchain connectivity: {len(connected_networks)} networks")
        
        # Try to import and initialize live components
        try:
            from app.core.blockchain.network_manager import get_network_manager
            network_manager = get_network_manager()
            
            from app.core.trading.live_trading_engine import get_live_trading_engine
            live_trading_engine = get_live_trading_engine()
            
            live_mode_enabled = True
            logger.info("🚀 Live trading components initialized")
            
        except ImportError as e:
            logger.info(f"ℹ️ Live trading components not available: {e}")
            logger.info("🔄 Running in compatibility mode")
        
    except Exception as e:
        logger.error(f"❌ Live initialization failed: {e}")
        logger.info("🔄 Continuing in standard mode")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    if logger_available:
        logger.info("🚀 Starting DEX Sniper Pro")
        logger.info("🔄 Checking for live trading capabilities...")
    
    # Try to initialize live trading
    await try_initialize_live_trading()
    
    if live_mode_enabled and blockchain_connected:
        if logger_available:
            logger.info("✅ Phase 4B: Live blockchain integration active")
    else:
        if logger_available:
            logger.info("🔄 Running in standard mode with existing features")
    
    yield
    
    # Cleanup
    if logger_available:
        logger.info("🛑 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="DEX Sniper Pro API",
    description="Automated cryptocurrency trading bot",
    version="4B.0.1",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="frontend/templates")
if Path("frontend/static").exists():
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include existing API routers
try:
    from app.api.v1.endpoints.dashboard import dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1")
    if logger_available:
        logger.info("✅ Dashboard router loaded")
except ImportError as e:
    if logger_available:
        logger.warning(f"⚠️ Dashboard router not available: {e}")

try:
    from app.api.v1.endpoints.tokens import router as tokens_router
    app.include_router(tokens_router, prefix="/api/v1")
    if logger_available:
        logger.info("✅ Tokens router loaded")
except ImportError as e:
    if logger_available:
        logger.warning(f"⚠️ Tokens router not available: {e}")

# Try to include live trading router if available
try:
    from app.api.v1.endpoints.live_trading import router as live_trading_router
    app.include_router(live_trading_router, prefix="/api/v1")
    if logger_available:
        logger.info("✅ Live trading router loaded")
except ImportError as e:
    if logger_available:
        logger.info(f"ℹ️ Live trading router not available: {e}")

try:
    from app.api.v1.endpoints.trading import router as trading_router
    app.include_router(trading_router, prefix="/api/v1")
    if logger_available:
        logger.info("✅ Trading router loaded")
except ImportError as e:
    if logger_available:
        logger.info(f"ℹ️ Trading router not available: {e}")


# ==================== MAIN ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint with system status."""
    try:
        return {
            "message": "🤖 DEX Sniper Pro Trading Bot API",
            "version": "4B.0.1",
            "status": "running",
            "mode": "live_integration" if live_mode_enabled else "standard",
            "blockchain_connected": blockchain_connected,
            "endpoints": {
                "dashboard": "/dashboard",
                "health": "/health",
                "docs": "/docs",
                "live_trading": "/api/v1/live-trading" if live_mode_enabled else None
            },
            "features": {
                "live_blockchain": blockchain_connected,
                "phase": "4B_gradual_integration"
            }
        }
    except Exception as e:
        return {
            "message": "🤖 DEX Sniper Pro Trading Bot API",
            "version": "4B.0.1",
            "status": "error",
            "error": str(e)
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        health = {
            "status": "healthy",
            "timestamp": "2025-08-03T00:00:00Z",
            "version": "4B.0.1",
            "mode": "live_integration" if live_mode_enabled else "standard",
            "blockchain_connectivity": blockchain_connected
        }
        
        # Add live system status if available
        if live_mode_enabled and network_manager:
            try:
                # Basic network check
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
                if w3.is_connected():
                    health["live_networks"] = {
                        "ethereum": {
                            "connected": True,
                            "latest_block": w3.eth.block_number
                        }
                    }
            except Exception as e:
                health["live_networks_error"] = str(e)
        
        return health
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": "2025-08-03T00:00:00Z",
            "error": str(e)
        }


# ==================== FRONTEND ROUTES ====================

@app.get("/dashboard")
async def serve_dashboard(request: Request):
    """Serve the dashboard."""
    try:
        context = {
            "request": request,
            "live_mode": live_mode_enabled,
            "blockchain_connected": blockchain_connected
        }
        return templates.TemplateResponse("pages/dashboard.html", context)
    except Exception as e:
        if logger_available:
            logger.error(f"❌ Dashboard error: {e}")
        return templates.TemplateResponse("pages/dashboard.html", {
            "request": request, 
            "error": str(e)
        })


@app.get("/live-trading")
async def live_trading_page(request: Request):
    """Live trading page."""
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


@app.get("/token-discovery")
async def token_discovery_page(request: Request):
    """Token discovery page."""
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


@app.get("/portfolio")
async def portfolio_page(request: Request):
    """Portfolio page."""
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


# ==================== LIVE BLOCKCHAIN TEST ENDPOINT ====================

@app.get("/api/v1/blockchain/test")
async def test_blockchain_connections():
    """Test blockchain connections in real-time."""
    try:
        from web3 import Web3
        
        test_rpcs = [
            ('Ethereum', 'https://ethereum.publicnode.com'),
            ('Polygon', 'https://polygon-rpc.com'),
            ('BSC', 'https://bsc-dataseed.binance.org/'),
            ('Arbitrum', 'https://arb1.arbitrum.io/rpc')
        ]
        
        results = []
        for name, url in test_rpcs:
            try:
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 5}))
                if w3.is_connected():
                    block = w3.eth.block_number
                    gas_price = w3.eth.gas_price
                    gas_gwei = w3.from_wei(gas_price, 'gwei')
                    
                    results.append({
                        "network": name,
                        "url": url,
                        "connected": True,
                        "latest_block": block,
                        "gas_price_gwei": float(gas_gwei)
                    })
                else:
                    results.append({
                        "network": name,
                        "url": url,
                        "connected": False,
                        "error": "Connection failed"
                    })
                    
            except Exception as e:
                results.append({
                    "network": name,
                    "url": url,
                    "connected": False,
                    "error": str(e)
                })
        
        connected_count = len([r for r in results if r["connected"]])
        
        return {
            "success": True,
            "timestamp": "2025-08-03T00:00:00Z",
            "total_networks": len(results),
            "connected_networks": connected_count,
            "results": results,
            "blockchain_ready": connected_count > 0
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": "2025-08-03T00:00:00Z"
        }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    if logger_available:
        logger.error(f"❌ Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": "2025-08-03T00:00:00Z"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting DEX Sniper Pro...")
    print("📊 Dashboard: http://127.0.0.1:8000/dashboard")
    print("🔗 API Docs: http://127.0.0.1:8000/docs")
    print("🧪 Blockchain Test: http://127.0.0.1:8000/api/v1/blockchain/test")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )