"""
Main FastAPI Application - Phase 5B Fixed
File: app/main.py

Fixed FastAPI application with proper integration.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DEX Sniper Pro Trading Bot",
    description="Professional automated trading bot",
    version="4.0.0-beta"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "DEX Sniper Pro Trading Bot", "version": "4.0.0-beta"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "4.0.0-beta"
    }

# Include API routers
try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1")
    logger.info("✅ Dashboard router included")
except ImportError as e:
    logger.warning(f"⚠️ Dashboard router not available: {e}")

try:
    from app.api.v1.endpoints.trading import router as trading_router
    app.include_router(trading_router, prefix="/api/v1")
    logger.info("✅ Trading router included")
except ImportError as e:
    logger.warning(f"⚠️ Trading router not available: {e}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Export
__all__ = ["app"]
