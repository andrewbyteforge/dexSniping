#!/usr/bin/env python3
"""
Startup Script for DEX Sniper Pro
File: scripts/start_server.py

Professional startup script with environment validation and graceful handling.
"""

import sys
import os
from pathlib import Path
import subprocess
import signal
from typing import Optional, List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ServerManager:
    """
    Manages the DEX Sniper Pro server startup and shutdown.
    """
    
    def __init__(self):
        """Initialize the server manager."""
        self.server_process: Optional[subprocess.Popen] = None
        self.is_running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame) -> None:
        """
        Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop_server()
        sys.exit(0)
    
    def validate_environment(self) -> bool:
        """
        Validate the environment before starting the server.
        
        Returns:
            bool: True if environment is valid
        """
        try:
            logger.info("Validating environment...")
            
            # Check Python version
            if sys.version_info < (3, 8):
                logger.error("Python 3.8+ is required")
                return False
            
            # Check if required files exist
            required_files = [
                "main.py",
                "app/server/application.py",
                "app/utils/logger.py",
                "frontend/templates/pages/dashboard.html"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                logger.error(f"Missing required files: {missing_files}")
                return False
            
            # Check if required directories exist
            required_dirs = [
                "app/server",
                "app/api/v1/endpoints",
                "frontend/static",
                "frontend/templates"
            ]
            
            missing_dirs = []
            for dir_path in required_dirs:
                if not Path(dir_path).exists():
                    missing_dirs.append(dir_path)
            
            if missing_dirs:
                logger.error(f"Missing required directories: {missing_dirs}")
                return False
            
            # Try importing key modules
            try:
                from app.server.application import create_application
                from app.utils.logger import setup_logger
                logger.info("Core modules import successfully")
                
            except ImportError as error:
                logger.error(f"Failed to import core modules: {error}")
                return False
            
            logger.info("Environment validation passed")
            return True
            
        except Exception as error:
            logger.error(f"Environment validation failed: {error}")
            return False
    
    def check_dependencies(self) -> bool:
        """
        Check if required dependencies are installed.
        
        Returns:
            bool: True if all dependencies are available
        """
        try:
            logger.info("Checking dependencies...")
            
            required_packages = [
                "fastapi",
                "uvicorn",
                "jinja2",
                "python-multipart"
            ]
            
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package.replace("-", "_"))
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.error(f"Missing required packages: {missing_packages}")
                logger.info("Install missing packages with:")
                logger.info(f"pip install {' '.join(missing_packages)}")
                return False
            
            logger.info("All dependencies are available")
            return True
            
        except Exception as error:
            logger.error(f"Dependency check failed: {error}")
            return False
    
    def start_server(
        self, 
        host: str = "127.0.0.1", 
        port: int = 8000, 
        reload: bool = True
    ) -> bool:
        """
        Start the FastAPI server.
        
        Args:
            host: Server host address
            port: Server port number
            reload: Enable auto-reload for development
            
        Returns:
            bool: True if server started successfully
        """
        try:
            if self.is_running:
                logger.warning("Server is already running")
                return False
            
            logger.info("Starting DEX Sniper Pro server...")
            logger.info(f"Host: {host}")
            logger.info(f"Port: {port}")
            logger.info(f"Reload: {reload}")
            
            # Import and run the main function
            from main import main
            
            # Start the server (this will block)
            main()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Server shutdown requested by user")
            return True
            
        except Exception as error:
            logger.error(f"Failed to start server: {error}")
            return False
    
    def stop_server(self) -> None:
        """Stop the server gracefully."""
        try:
            if self.server_process and self.server_process.poll() is None:
                logger.info("Stopping server...")
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("Server stopped")
            
            self.is_running = False
            
        except subprocess.TimeoutExpired:
            logger.warning("Server did not stop gracefully, forcing shutdown")
            self.server_process.kill()
            
        except Exception as error:
            logger.error(f"Error stopping server: {error}")
    
    def print_startup_info(self) -> None:
        """Print startup information."""
        print("\n" + "=" * 60)
        print("🤖 DEX Sniper Pro Trading Bot")
        print("=" * 60)
        print("🚀 Starting professional trading interface...")
        print("📊 Dashboard: http://127.0.0.1:8000/dashboard")
        print("📚 API Docs: http://127.0.0.1:8000/docs")
        print("🔍 Health Check: http://127.0.0.1:8000/health")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60 + "\n")


def main() -> None:
    """
    Main startup function.
    """
    server_manager = ServerManager()
    
    try:
        # Print startup information
        server_manager.print_startup_info()
        
        # Validate environment
        if not server_manager.validate_environment():
            logger.error("Environment validation failed")
            sys.exit(1)
        
        # Check dependencies
        if not server_manager.check_dependencies():
            logger.error("Dependency check failed")
            sys.exit(1)
        
        # Start the server
        success = server_manager.start_server()
        
        if not success:
            logger.error("Failed to start server")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Startup interrupted by user")
        sys.exit(0)
        
    except Exception as error:
        logger.error(f"Startup failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()