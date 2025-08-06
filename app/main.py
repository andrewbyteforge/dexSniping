"""
Main Application Entry Point
File: app/main.py

Streamlined main entry point for the DEX Sniper Pro application.
Uses modular architecture with separate managers for different concerns.
"""

import sys
from pathlib import Path

from app.utils.logger import setup_logger
from app.factory import create_app
from app.core.lifecycle_manager import LifecycleManager

logger = setup_logger(__name__)

# Application metadata
__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"
__description__ = "Professional trading bot with AI-powered risk assessment"


def create_application():
    """
    Create the FastAPI application instance.
    
    Returns:
        FastAPI: Configured application instance
        
    Raises:
        RuntimeError: If application creation fails
    """
    try:
        logger.info("Creating DEX Sniper Pro application...")
        
        # Create lifecycle manager
        lifecycle_manager = LifecycleManager()
        
        # Create application using factory
        app = create_app()
        
        # Set up lifespan management
        app.router.lifespan_context = lifecycle_manager.lifespan
        
        # Add startup and shutdown event handlers
        @app.on_event("startup")
        async def startup_event():
            """Application startup event handler."""
            await lifecycle_manager.display_startup_message()
        
        @app.on_event("shutdown")
        async def shutdown_event():
            """Application shutdown event handler."""
            await lifecycle_manager.display_shutdown_message()
        
        logger.info("DEX Sniper Pro Phase 4C application instance created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Critical: Failed to create application instance: {e}")
        raise RuntimeError(f"Application creation failed: {e}")


# Create the FastAPI application instance
try:
    app = create_application()
except Exception as e:
    logger.error(f"Application creation failed: {e}")
    sys.exit(1)


# Export application metadata and instance
__all__ = ["app", "__version__", "__phase__", "__description__"]


def main():
    """Main entry point for development server."""
    import uvicorn
    
    try:
        logger.info("Starting DEX Sniper Pro Phase 4C development server...")
        logger.info("AI Risk Assessment features enabled")
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as error:
        logger.error(f"Server startup failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()