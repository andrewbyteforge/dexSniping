"""
System Info Provider Module
File: app/core/system_info.py

Provides comprehensive system information and health status reporting.
Handles component status tracking and system metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Application metadata
__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"
__description__ = "Professional trading bot with AI-powered risk assessment"


class SystemInfoProvider:
    """Provides system information and health status."""
    
    def __init__(self):
        """Initialize the system info provider."""
        pass
    
    async def get_comprehensive_system_info(self, component_status: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Args:
            component_status: Dict of component availability status
            
        Returns:
            Dict containing comprehensive system information
        """
        try:
            system_status = await self._get_system_status_safe(component_status)
            
            return {
                "message": "DEX Sniper Pro - AI-Powered Trading Bot API",
                "version": __version__,
                "phase": __phase__,
                "status": "operational",
                "description": __description__,
                "blockchain_approach": "public_rpc_priority",
                "rpc_authentication": "fixed_with_fallback",
                "ai_features": {
                    "risk_assessment": {
                        "status": "operational" if component_status.get("ai_risk_assessment") else "unavailable",
                        "description": "AI-powered risk analysis for trading decisions",
                        "capabilities": [
                            "Token risk assessment",
                            "Portfolio risk analysis",
                            "Market condition analysis",
                            "Automated recommendations"
                        ] if component_status.get("ai_risk_assessment") else []
                    },
                    "portfolio_intelligence": {
                        "status": "operational" if component_status.get("ai_portfolio_analysis") else "unavailable",
                        "description": "AI-driven portfolio optimization and insights"
                    }
                },
                "capabilities": self._get_available_capabilities(component_status),
                "supported_networks": self._get_supported_networks(component_status),
                "component_status": component_status,
                "system_status": system_status,
                "endpoints": {
                    "dashboard": "/dashboard",
                    "risk_analysis": "/risk-analysis" if component_status.get("ai_risk_assessment") else None,
                    "api_docs": "/docs",
                    "health_check": "/health",
                    "dashboard_stats": "/api/v1/dashboard/stats",
                    "token_discovery": "/api/v1/tokens/discover",
                    "ai_risk_api": "/api/v1/ai-risk" if component_status.get("ai_api_endpoints") else None
                },
                "blockchain_connectivity": {
                    "approach": "Public RPC endpoints prioritized over private",
                    "authentication": "API keys used only when available and working",
                    "fallback": "Comprehensive public RPC endpoint fallback system",
                    "reliability": "No startup blocking due to RPC authentication issues"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as error:
            logger.error(f"System info error: {error}")
            return await self.get_fallback_system_info(component_status, str(error))
    
    async def get_fallback_system_info(self, component_status: Dict[str, bool], error: str) -> Dict[str, Any]:
        """
        Get fallback system information when main info gathering fails.
        
        Args:
            component_status: Dict of component availability status
            error: Error message
            
        Returns:
            Dict containing fallback system information
        """
        return {
            "message": "DEX Sniper Pro - AI-Powered Trading Bot API",
            "version": __version__,
            "phase": __phase__,
            "status": "limited_functionality",
            "error": "System information temporarily unavailable",
            "ai_features": {
                "risk_assessment": component_status.get("ai_risk_assessment", False),
                "portfolio_analysis": component_status.get("ai_portfolio_analysis", False)
            },
            "endpoints": {
                "dashboard": "/dashboard",
                "risk_analysis": "/risk-analysis",
                "health": "/health",
                "docs": "/docs",
                "ai_risk_api": "/api/v1/ai-risk" if component_status.get("ai_api_endpoints") else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_comprehensive_health_status(self, component_status: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Args:
            component_status: Dict of component availability status
            
        Returns:
            Dict containing comprehensive health status
        """
        try:
            health_status = {
                "status": "healthy",
                "service": "DEX Sniper Pro AI-Powered Trading Bot",
                "version": __version__,
                "phase": __phase__,
                "startup_mode": "safe_mode",
                "blockchain_status": "on_demand_initialization",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {},
                "overall_health_score": 0.0
            }
            
            component_scores = []
            
            # Check AI Risk Assessment
            if component_status.get("ai_risk_assessment"):
                health_status["components"]["ai_risk_assessment"] = {
                    "status": "healthy",
                    "mode": "operational",
                    "message": "AI Risk Assessment system operational",
                    "features": ["token_analysis", "portfolio_analysis", "market_assessment"]
                }
                component_scores.append(1.0)
            else:
                health_status["components"]["ai_risk_assessment"] = {
                    "status": "not_loaded",
                    "message": "AI Risk Assessment component not available"
                }
                component_scores.append(0.0)
            
            # Check AI Portfolio Analysis
            if component_status.get("ai_portfolio_analysis"):
                health_status["components"]["ai_portfolio_analysis"] = {
                    "status": "healthy",
                    "mode": "operational",
                    "message": "AI Portfolio Analysis operational"
                }
                component_scores.append(1.0)
            else:
                health_status["components"]["ai_portfolio_analysis"] = {
                    "status": "not_loaded",
                    "message": "AI Portfolio Analysis not available"
                }
                component_scores.append(0.0)
            
            # Check other components (available but not connected during startup)
            for component_name in ["trading_engine", "wallet_system", "dex_integration"]:
                if component_status.get(component_name):
                    health_status["components"][component_name] = {
                        "status": "available",
                        "mode": "on_demand_initialization",
                        "message": f"Ready to initialize when {component_name} features are accessed",
                        "startup_connection": "disabled_for_stability"
                    }
                    component_scores.append(0.8)  # Available but not connected
                else:
                    health_status["components"][component_name] = {
                        "status": "not_loaded",
                        "message": "Component not available"
                    }
                    component_scores.append(0.0)
            
            # Core components (always healthy if app is running)
            health_status["components"]["dashboard"] = {
                "status": "healthy",
                "message": "Dashboard API operational"
            }
            health_status["components"]["api"] = {
                "status": "healthy", 
                "message": "REST API operational"
            }
            health_status["components"]["phase4a_compatibility"] = {
                "status": "healthy" if component_status.get("live_trading_api") else "degraded",
                "message": "Phase 4A live trading API available" if component_status.get("live_trading_api") else "Phase 4A API not available"
            }
            component_scores.extend([1.0, 1.0, 1.0 if component_status.get("live_trading_api") else 0.5])
            
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
            
            # Add AI capabilities summary
            health_status["ai_capabilities"] = {
                "risk_assessment": component_status.get("ai_risk_assessment", False),
                "portfolio_analysis": component_status.get("ai_portfolio_analysis", False),
                "market_intelligence": component_status.get("ai_risk_assessment", False),
                "automated_recommendations": component_status.get("ai_risk_assessment", False)
            }
            
            # Add safe startup explanation
            health_status["safe_startup_info"] = {
                "enabled": True,
                "reason": "Prevents RPC authentication errors during startup",
                "benefit": "Application starts reliably without blockchain dependencies",
                "blockchain_initialization": "On-demand when trading features are first used",
                "ai_initialization": "Immediate for AI risk assessment features"
            }
            
            return health_status
            
        except Exception as error:
            logger.error(f"Health status error: {error}")
            return await self.get_fallback_health_status(str(error))
    
    async def get_fallback_health_status(self, error: str) -> Dict[str, Any]:
        """
        Get fallback health status when main health check fails.
        
        Args:
            error: Error message
            
        Returns:
            Dict containing fallback health status
        """
        return {
            "status": "unhealthy",
            "service": "DEX Sniper Pro AI-Powered Trading Bot",
            "version": __version__,
            "phase": __phase__,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_system_status_safe(self, component_status: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get system status with comprehensive error handling.
        
        Args:
            component_status: Dict of component availability status
            
        Returns:
            Dict containing system status information
        """
        try:
            status = {
                "initialized": False,
                "uptime_hours": 0,
                "active_sessions": 0,
                "active_connections": 0,
                "component_availability": component_status,
                "ai_status": {
                    "risk_assessments_performed": 0,
                    "portfolio_analyses": 0,
                    "ai_recommendations_generated": 0,
                    "system_ready": component_status.get("ai_risk_assessment", False)
                }
            }
            
            # Try to get more detailed status from components if available
            # This would be implemented with actual component instances
            # For now, return basic status
            
            return status
            
        except Exception as error:
            logger.error(f"System status error: {error}")
            return {
                "error": "Status unavailable", 
                "component_availability": component_status,
                "ai_status": {"available": component_status.get("ai_risk_assessment", False)}
            }
    
    def _get_available_capabilities(self, component_status: Dict[str, bool]) -> List[str]:
        """
        Get list of available capabilities based on loaded components.
        
        Args:
            component_status: Dict of component availability status
            
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
        if component_status.get("ai_risk_assessment"):
            capabilities.extend([
                "AI-Powered Risk Assessment",
                "Intelligent Trading Recommendations",
                "Smart Position Sizing",
                "Market Condition Analysis"
            ])
        
        if component_status.get("ai_portfolio_analysis"):
            capabilities.append("AI Portfolio Risk Management")
        
        if component_status.get("ai_api_endpoints"):
            capabilities.append("AI Risk Assessment API")
        
        if component_status.get("phase4a_schemas"):
            capabilities.append("Phase 4A Trading Schemas")
        
        if component_status.get("live_trading_api"):
            capabilities.append("Live Trading Session Management")
        
        if component_status.get("wallet_system"):
            capabilities.append("Wallet Connection System (Public RPC)")
        
        if component_status.get("dex_integration"):
            capabilities.append("Live DEX Integration (Public RPC)")
        
        if component_status.get("trading_engine"):
            capabilities.append("Automated Trading Engine (Public RPC)")
        
        return capabilities
    
    def _get_supported_networks(self, component_status: Dict[str, bool]) -> List[str]:
        """
        Get list of supported network names.
        
        Args:
            component_status: Dict of component availability status
            
        Returns:
            List of supported network names
        """
        # For now, return standard networks
        # This could be enhanced to get actual networks from components
        return ["ethereum", "polygon", "bsc", "arbitrum"]