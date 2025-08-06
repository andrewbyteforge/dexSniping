"""
Component Manager Module
File: app/core/component_manager.py

Manages loading and status tracking of all application components.
Handles safe imports and component availability detection.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ComponentManager:
    """Manages loading and status of application components."""
    
    def __init__(self):
        """Initialize the component manager."""
        self.component_status = {
            # Core Phase 4B components
            "wallet_system": False,
            "dex_integration": False,
            "trading_engine": False,
            "live_trading_api": False,
            "phase4a_schemas": False,
            # Phase 4C AI components
            "ai_risk_assessment": False,
            "ai_portfolio_analysis": False,
            "ai_api_endpoints": False
        }
        
        self.component_instances = {}
        
    async def initialize_components(self) -> bool:
        """
        Initialize all available components.
        
        Returns:
            bool: True if at least some components initialized successfully
        """
        try:
            logger.info("Initializing application components...")
            
            # Load components in dependency order
            await self._load_core_components()
            await self._load_trading_components()
            await self._load_ai_components()
            await self._load_api_components()
            
            success_count = sum(self.component_status.values())
            total_components = len(self.component_status)
            
            logger.info(f"Components initialized: {success_count}/{total_components}")
            return success_count > 0
            
        except Exception as error:
            logger.error(f"Component initialization failed: {error}")
            return False
    
    async def _load_core_components(self) -> None:
        """Load core system components."""
        # Load Phase 4A schemas
        try:
            from app.schemas.trading_schemas import TradingSessionResponse
            self.component_status["phase4a_schemas"] = True
            logger.info("Phase 4A schemas loaded successfully")
        except ImportError as e:
            logger.warning(f"Phase 4A schemas not available: {e}")
        except Exception as e:
            logger.error(f"Phase 4A schemas loading error: {e}")
    
    async def _load_trading_components(self) -> None:
        """Load trading-related components."""
        # Load wallet system
        try:
            from app.core.wallet.wallet_connection_manager import (
                get_wallet_connection_manager,
                initialize_wallet_system,
                NetworkType
            )
            self.component_instances["wallet_manager"] = get_wallet_connection_manager
            self.component_instances["initialize_wallet"] = initialize_wallet_system
            self.component_instances["NetworkType"] = NetworkType
            self.component_status["wallet_system"] = True
            logger.info("Wallet system components loaded successfully")
        except ImportError as e:
            logger.warning(f"Wallet system not available: {e}")
        except Exception as e:
            logger.error(f"Wallet system loading error: {e}")
        
        # Load DEX integration
        try:
            from app.core.dex.live_dex_integration import (
                get_live_dex_integration,
                initialize_dex_integration
            )
            self.component_instances["dex_integration"] = get_live_dex_integration
            self.component_instances["initialize_dex"] = initialize_dex_integration
            self.component_status["dex_integration"] = True
            logger.info("DEX integration components loaded successfully")
        except ImportError as e:
            logger.warning(f"DEX integration not available: {e}")
        except Exception as e:
            logger.error(f"DEX integration loading error: {e}")
        
        # Load trading engine
        try:
            from app.core.trading.live_trading_engine_enhanced import (
                get_live_trading_engine,
                initialize_live_trading_system
            )
            self.component_instances["trading_engine"] = get_live_trading_engine
            self.component_instances["initialize_trading"] = initialize_live_trading_system
            self.component_status["trading_engine"] = True
            logger.info("Trading engine components loaded successfully")
        except ImportError as e:
            logger.warning(f"Trading engine not available: {e}")
        except Exception as e:
            logger.error(f"Trading engine loading error: {e}")
    
    async def _load_ai_components(self) -> None:
        """Load AI-related components."""
        # Load AI Risk Assessment
        try:
            from app.core.trading.ai_risk_assessor import (
                get_ai_risk_assessor,
                AIRiskAssessor,
                RiskAssessment
            )
            self.component_instances["ai_risk_assessor"] = get_ai_risk_assessor
            self.component_instances["AIRiskAssessor"] = AIRiskAssessor
            self.component_instances["RiskAssessment"] = RiskAssessment
            self.component_status["ai_risk_assessment"] = True
            self.component_status["ai_portfolio_analysis"] = True  # Enabled with risk assessment
            logger.info("AI Risk Assessment system loaded successfully")
        except ImportError as e:
            logger.warning(f"AI Risk Assessment not available: {e}")
        except Exception as e:
            logger.error(f"AI Risk Assessment loading error: {e}")
    
    async def _load_api_components(self) -> None:
        """Load API endpoint components."""
        # Load live trading API
        try:
            from app.api.v1.endpoints.live_trading_fixed import router as live_trading_router
            self.component_instances["live_trading_router"] = live_trading_router
            self.component_status["live_trading_api"] = True
            logger.info("Live trading API (Phase 4A) loaded successfully")
        except ImportError as e:
            logger.warning(f"Live trading API not available: {e}")
        except Exception as e:
            logger.error(f"Live trading API loading error: {e}")
        
        # Load AI Risk API
        try:
            from app.api.v1.endpoints.ai_risk_api import ai_risk_router
            self.component_instances["ai_risk_router"] = ai_risk_router
            self.component_status["ai_api_endpoints"] = True
            logger.info("AI Risk Assessment API endpoints loaded successfully")
        except ImportError as e:
            logger.warning(f"AI Risk Assessment API not available: {e}")
        except Exception as e:
            logger.error(f"AI Risk Assessment API loading error: {e}")
    
    async def get_component_status(self) -> Dict[str, bool]:
        """
        Get current component status.
        
        Returns:
            Dict mapping component names to availability status
        """
        if not any(self.component_status.values()):
            # If no components loaded yet, try to initialize
            await self.initialize_components()
        
        return self.component_status.copy()
    
    def get_component_instance(self, component_name: str) -> Optional[Any]:
        """
        Get a component instance by name.
        
        Args:
            component_name: Name of the component to retrieve
            
        Returns:
            Component instance or None if not available
        """
        return self.component_instances.get(component_name)
    
    async def initialize_trading_systems(self) -> bool:
        """
        Initialize trading systems with proper network setup.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            success_count = 0
            total_systems = 4
            
            logger.info("Initializing trading systems with public RPC priority...")
            
            # Initialize network manager
            try:
                from app.core.blockchain.network_manager_fixed import initialize_network_manager
                network_success = await initialize_network_manager()
                
                if network_success:
                    logger.info("Network manager initialized with public RPC fallback")
                    success_count += 1
                else:
                    logger.warning("Network manager initialization issues")
            except Exception as e:
                logger.error(f"Network manager initialization error: {e}")
            
            # Initialize AI Risk Assessment
            if self.component_status["ai_risk_assessment"]:
                try:
                    logger.info("Initializing AI Risk Assessment system...")
                    ai_assessor_func = self.get_component_instance("ai_risk_assessor")
                    if ai_assessor_func:
                        ai_assessor = await ai_assessor_func()
                        if ai_assessor:
                            logger.info("AI Risk Assessment system initialized successfully")
                            success_count += 1
                        else:
                            logger.warning("AI Risk Assessment system initialization returned None")
                    else:
                        logger.warning("AI Risk Assessment component not available")
                except Exception as e:
                    logger.error(f"AI Risk Assessment initialization error: {e}")
            else:
                logger.info("AI Risk Assessment not available - skipping initialization")
            
            # Other systems will be initialized on-demand
            if self.component_status["wallet_system"]:
                logger.info("Wallet system prepared (will connect on-demand)")
                success_count += 1
            
            if self.component_status["trading_engine"]:
                logger.info("Trading engine prepared (will connect on-demand)")
                success_count += 1
            
            logger.info(f"Trading systems initialization: {success_count}/{total_systems} systems operational")
            return success_count > 0
            
        except Exception as error:
            logger.error(f"Trading systems initialization failed: {error}")
            return False
    
    async def cleanup_components(self) -> None:
        """Cleanup all components on shutdown."""
        try:
            logger.info("Cleaning up application components...")
            
            cleanup_tasks = []
            
            # Cleanup trading engine
            if self.component_status["trading_engine"]:
                try:
                    trading_engine_func = self.get_component_instance("trading_engine")
                    if trading_engine_func:
                        trading_engine = trading_engine_func()
                        cleanup_tasks.append(trading_engine.shutdown())
                        logger.info("Trading engine cleanup scheduled")
                except Exception as e:
                    logger.error(f"Trading engine cleanup error: {e}")
            
            # Cleanup wallet connections
            if self.component_status["wallet_system"]:
                try:
                    wallet_manager_func = self.get_component_instance("wallet_manager")
                    if wallet_manager_func:
                        wallet_manager = wallet_manager_func()
                        cleanup_tasks.append(wallet_manager.cleanup_expired_connections())
                        logger.info("Wallet cleanup scheduled")
                except Exception as e:
                    logger.error(f"Wallet cleanup error: {e}")
            
            # Execute cleanup tasks
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                logger.info("All cleanup tasks completed")
            
        except Exception as error:
            logger.error(f"Component cleanup error: {error}")
    
    def get_supported_networks(self) -> List[str]:
        """
        Get list of supported network names.
        
        Returns:
            List of supported network names
        """
        if self.component_status["wallet_system"]:
            try:
                NetworkType = self.get_component_instance("NetworkType")
                if NetworkType:
                    return [
                        NetworkType.ETHEREUM.value,
                        NetworkType.POLYGON.value,
                        NetworkType.BSC.value
                    ]
            except Exception as e:
                logger.warning(f"Network enumeration error: {e}")
        
        return ["ethereum", "polygon", "bsc", "arbitrum"]
    
    def get_available_capabilities(self) -> List[str]:
        """
        Get list of available capabilities based on loaded components.
        
        Returns:
            List of capability descriptions
        """
        capabilities = [
            "Professional Dashboard Interface",
            "RESTful API Framework", 
            "Token Discovery System",
            "Health Monitoring & Status Reporting",
            "Fixed RPC Authentication (Public Endpoint Priority)",
            "Blockchain Connectivity with Fallback System"
        ]
        
        # Add AI capabilities
        if self.component_status["ai_risk_assessment"]:
            capabilities.extend([
                "AI-Powered Risk Assessment",
                "Intelligent Trading Recommendations",
                "Smart Position Sizing",
                "Market Condition Analysis"
            ])
        
        if self.component_status["ai_portfolio_analysis"]:
            capabilities.append("AI Portfolio Risk Management")
        
        if self.component_status["ai_api_endpoints"]:
            capabilities.append("AI Risk Assessment API")
        
        if self.component_status["phase4a_schemas"]:
            capabilities.append("Phase 4A Trading Schemas")
        
        if self.component_status["live_trading_api"]:
            capabilities.append("Live Trading Session Management")
        
        if self.component_status["wallet_system"]:
            capabilities.append("Wallet Connection System (Public RPC)")
        
        if self.component_status["dex_integration"]:
            capabilities.append("Live DEX Integration (Public RPC)")
        
        if self.component_status["trading_engine"]:
            capabilities.append("Automated Trading Engine (Public RPC)")
        
        return capabilities
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health information.
        
        Returns:
            Dict containing system health status
        """
        try:
            health_status = {
                "status": "healthy",
                "components": {},
                "overall_health_score": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            component_scores = []
            
            # Check each component
            for component_name, is_available in self.component_status.items():
                if is_available:
                    if component_name.startswith("ai_"):
                        # AI components are fully operational when available
                        health_status["components"][component_name] = {
                            "status": "healthy",
                            "mode": "operational"
                        }
                        component_scores.append(1.0)
                    else:
                        # Other components use on-demand initialization
                        health_status["components"][component_name] = {
                            "status": "available",
                            "mode": "on_demand_initialization"
                        }
                        component_scores.append(0.8)
                else:
                    health_status["components"][component_name] = {
                        "status": "not_loaded"
                    }
                    component_scores.append(0.0)
            
            # Calculate overall health score
            if component_scores:
                health_status["overall_health_score"] = sum(component_scores) / len(component_scores)
            
            # Determine overall status
            if health_status["overall_health_score"] >= 0.8:
                health_status["status"] = "healthy"
            elif health_status["overall_health_score"] >= 0.5:
                health_status["status"] = "degraded"
            else:
                health_status["status"] = "unhealthy"
            
            return health_status
            
        except Exception as error:
            logger.error(f"System health check error: {error}")
            return {
                "status": "error",
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }