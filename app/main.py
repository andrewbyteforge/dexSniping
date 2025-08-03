"""
Refactored Main Application Entry Point
File: main.py

Clean main entry point that delegates to appropriate modules.
"""

import uvicorn
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.server.application import create_application
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    """
    Main application entry point.
    
    Creates and configures the FastAPI application, then starts the server.
    """
    try:
        # Create the FastAPI application
        app = create_application()
        
        # Server configuration
        server_config = {
            "app": app,
            "host": "127.0.0.1",
            "port": 8000,
            "reload": True,
            "log_level": "info",
            "access_log": True,
        }
        
        logger.info("Starting DEX Sniper Pro Trading Bot Server...")
        logger.info(f"Dashboard: http://127.0.0.1:8000/dashboard")
        logger.info(f"API Docs: http://127.0.0.1:8000/docs")
        
        # Start the server
        uvicorn.run(**server_config)
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as error:
        logger.error(f"Failed to start server: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()