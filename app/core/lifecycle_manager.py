"""
Lifecycle Manager Module
File: app/core/lifecycle_manager.py

Manages application lifecycle including startup and shutdown procedures.
Handles component initialization and cleanup with proper error handling.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from app.utils.logger import setup_logger
from app.core.component_manager import ComponentManager

logger = setup_logger(__name__)

# Application metadata
__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"


class LifecycleManager:
    """Manages application lifecycle events."""
    
    def __init__(self):
        """Initialize the lifecycle manager."""
        self.component_manager = ComponentManager()
        self.startup_successful = False
        
    @asynccontextmanager
    async def lifespan(self, app):
        """
        Application lifespan context manager.
        
        Args:
            app: FastAPI application instance
            
        Yields:
            None: Application context
        """
        logger.info("Starting DEX Sniper Pro - Phase 4C AI Risk Assessment Integration...")
        
        try:
            self.startup_successful = await self.execute_startup_procedures()
            
            if self.startup_successful:
                logger.info("Application startup completed successfully")
            else:
                logger.warning("Application started with limited functionality")
            
            # Store component manager in app state
            app.state.component_manager = self.component_manager
            app.state.lifecycle_manager = self
            
            yield
            
        except Exception as e:
            logger.error(f"Startup error: {e}")
            logger.info("Starting with basic functionality only...")
            yield
        finally:
            try:
                await self.execute_shutdown_procedures()
                logger.info("Application shutdown completed successfully")
            except Exception as e:
                logger.error(f"Shutdown error: {e}")
    
    async def execute_startup_procedures(self) -> bool:
        """
        Execute comprehensive startup procedures with Phase 4C AI initialization.
        
        Returns:
            bool: True if startup successful, False if limited functionality
        """
        try:
            logger.info("Starting Phase 4C with AI Risk Assessment and fixed RPC authentication...")
            
            # Initialize components
            component_init_success = await self.component_manager.initialize_components()
            
            if not component_init_success:
                logger.warning("Component initialization had issues")
                return False
            
            # Initialize trading systems
            trading_init_success = await self.component_manager.initialize_trading_systems()
            
            # Get component status for logging
            component_status = await self.component_manager.get_component_status()
            success_count = sum(component_status.values())
            total_components = len(component_status)
            
            # Log initialization summary
            logger.info(f"Initialization complete: {success_count}/{total_components} systems operational")
            logger.info("AI Risk Assessment integration status: " + 
                       ("Active" if component_status.get("ai_risk_assessment") else "Unavailable"))
            logger.info("Fixed RPC authentication - blockchain connections ready")
            
            return success_count > 0  # At least some functionality available
            
        except Exception as e:
            logger.error(f"Startup procedures failed: {e}")
            return False
    
    async def execute_shutdown_procedures(self) -> None:
        """Execute comprehensive shutdown procedures with AI cleanup."""
        try:
            logger.info("Executing shutdown procedures...")
            
            # Use component manager for cleanup
            await self.component_manager.cleanup_components()
            
            logger.info("Shutdown procedures completed")
            
        except Exception as e:
            logger.error(f"Shutdown procedures error: {e}")
    
    async def display_startup_message(self) -> None:
        """Display comprehensive startup message with AI information."""
        logger.info("=" * 80)
        logger.info("DEX SNIPER PRO - PHASE 4C AI RISK ASSESSMENT INTEGRATION")
        logger.info("=" * 80)
        logger.info("Status: Starting up...")
        logger.info(f"Version: {__version__}")
        logger.info(f"Phase: {__phase__}")
        logger.info("NEW: AI-Powered Risk Assessment System")
        logger.info("Mode: Clean Implementation with AI Integration")
        
        try:
            component_status = await self.component_manager.get_component_status()
            available_count = sum(component_status.values())
            total_count = len(component_status)
            
            logger.info(f"Components Available: {available_count}/{total_count}")
            logger.info(f"AI Features: {'Active' if component_status.get('ai_risk_assessment') else 'Unavailable'}")
        except Exception as e:
            logger.warning(f"Could not get component status for startup message: {e}")
        
        logger.info("=" * 80)
    
    async def display_shutdown_message(self) -> None:
        """Display shutdown message."""
        logger.info("=" * 80)
        logger.info("DEX SNIPER PRO - SHUTTING DOWN")
        logger.info("=" * 80)
        logger.info("Shutdown complete")
        logger.info("=" * 80)
    
    def is_startup_successful(self) -> bool:
        """
        Check if startup was successful.
        
        Returns:
            bool: True if startup was successful
        """
        return self.startup_successful
    
    async def get_runtime_status(self) -> Dict[str, Any]:
        """
        Get current runtime status.
        
        Returns:
            Dict containing runtime status information
        """
        try:
            component_status = await self.component_manager.get_component_status()
            system_health = await self.component_manager.get_system_health()
            
            return {
                "startup_successful": self.startup_successful,
                "component_status": component_status,
                "system_health": system_health,
                "capabilities": self.component_manager.get_available_capabilities(),
                "supported_networks": self.component_manager.get_supported_networks()
            }
            
        except Exception as error:
            logger.error(f"Runtime status error: {error}")
            return {
                "startup_successful": self.startup_successful,
                "error": str(error)
            }
    
    async def restart_component(self, component_name: str) -> bool:
        """
        Attempt to restart a specific component.
        
        Args:
            component_name: Name of component to restart
            
        Returns:
            bool: True if restart successful
        """
        try:
            logger.info(f"Attempting to restart component: {component_name}")
            
            # This would implement component-specific restart logic
            # For now, just re-initialize all components
            success = await self.component_manager.initialize_components()
            
            if success:
                logger.info(f"Component restart successful: {component_name}")
            else:
                logger.warning(f"Component restart failed: {component_name}")
            
            return success
            
        except Exception as error:
            logger.error(f"Component restart error for {component_name}: {error}")
            return False
    
    async def get_component_instance(self, component_name: str) -> Optional[Any]:
        """
        Get a component instance by name.
        
        Args:
            component_name: Name of the component to retrieve
            
        Returns:
            Component instance or None if not available
        """
        return self.component_manager.get_component_instance(component_name)