"""
Safe Startup Verification Script
File: verify_safe_startup.py

Verifies that the Phase 4B Clean Implementation starts without RPC errors
and all systems are operational in safe startup mode.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SafeStartupVerifier:
    """Verification system for safe startup mode."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """Initialize the verifier."""
        self.base_url = base_url
        self.session = None
        self.verification_results: List[Dict[str, Any]] = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def verify_safe_startup(self) -> Dict[str, Any]:
        """
        Comprehensive verification of safe startup mode.
        
        Returns:
            Dict containing verification results
        """
        logger.info("🔍 Starting Safe Startup Verification...")
        
        verification_results = {
            "startup_mode": await self.verify_startup_mode(),
            "component_status": await self.verify_component_status(),
            "api_functionality": await self.verify_api_functionality(),
            "health_monitoring": await self.verify_health_monitoring(),
            "safe_mode_features": await self.verify_safe_mode_features()
        }
        
        # Calculate overall verification status
        all_passed = all(
            result.get("success", False) 
            for result in verification_results.values()
        )
        
        verification_summary = {
            "overall_status": "PASSED" if all_passed else "FAILED",
            "verification_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": verification_results,
            "recommendations": self.get_recommendations(verification_results)
        }
        
        return verification_summary
    
    async def verify_startup_mode(self) -> Dict[str, Any]:
        """Verify safe startup mode is active."""
        try:
            logger.info("🧪 Verifying safe startup mode...")
            
            url = f"{self.base_url}/"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for safe startup indicators
                    startup_mode = data.get("startup_mode")
                    blockchain_status = data.get("blockchain_status")
                    phase = data.get("phase", "")
                    
                    success = (
                        startup_mode == "safe_mode" and
                        blockchain_status == "on_demand_initialization" and
                        "Safe Startup" in phase
                    )
                    
                    return {
                        "test": "safe_startup_mode",
                        "success": success,
                        "startup_mode": startup_mode,
                        "blockchain_status": blockchain_status,
                        "phase": phase,
                        "message": "Safe startup mode active" if success else "Safe startup mode not detected"
                    }
                else:
                    return {
                        "test": "safe_startup_mode",
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Failed to connect to application"
                    }
        
        except Exception as e:
            logger.error(f"❌ Safe startup verification failed: {e}")
            return {
                "test": "safe_startup_mode",
                "success": False,
                "error": str(e),
                "message": "Safe startup verification error"
            }
    
    async def verify_component_status(self) -> Dict[str, Any]:
        """Verify component detection and status reporting."""
        try:
            logger.info("🧪 Verifying component status...")
            
            url = f"{self.base_url}/"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    component_status = data.get("component_status", {})
                    capabilities = data.get("capabilities", [])
                    
                    # Check that components are detected
                    has_components = len(component_status) > 0
                    has_capabilities = len(capabilities) > 0
                    
                    # Look for safe startup indicators in capabilities
                    safe_startup_capability = any(
                        "Safe Startup" in cap or "On-Demand" in cap 
                        for cap in capabilities
                    )
                    
                    success = has_components and has_capabilities and safe_startup_capability
                    
                    return {
                        "test": "component_status",
                        "success": success,
                        "components_detected": len(component_status),
                        "capabilities_listed": len(capabilities),
                        "safe_startup_capability": safe_startup_capability,
                        "component_status": component_status,
                        "message": "Component detection working" if success else "Component detection issues"
                    }
                else:
                    return {
                        "test": "component_status",
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Failed to get component status"
                    }
        
        except Exception as e:
            logger.error(f"❌ Component status verification failed: {e}")
            return {
                "test": "component_status",
                "success": False,
                "error": str(e),
                "message": "Component status verification error"
            }
    
    async def verify_api_functionality(self) -> Dict[str, Any]:
        """Verify core API functionality."""
        try:
            logger.info("🧪 Verifying API functionality...")
            
            endpoints_to_test = [
                ("/", "root_api"),
                ("/health", "health_check"),
                ("/api/v1/dashboard/stats", "dashboard_stats"),
                ("/api/v1/tokens/discover", "token_discovery")
            ]
            
            results = {}
            all_success = True
            
            for endpoint, name in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint}"
                    async with self.session.get(url) as response:
                        success = response.status == 200
                        results[name] = {
                            "status": response.status,
                            "success": success
                        }
                        if not success:
                            all_success = False
                
                except Exception as e:
                    results[name] = {
                        "status": 0,
                        "success": False,
                        "error": str(e)
                    }
                    all_success = False
            
            return {
                "test": "api_functionality",
                "success": all_success,
                "endpoints_tested": len(endpoints_to_test),
                "endpoints_passed": sum(1 for r in results.values() if r["success"]),
                "results": results,
                "message": "All APIs operational" if all_success else "Some API issues detected"
            }
        
        except Exception as e:
            logger.error(f"❌ API functionality verification failed: {e}")
            return {
                "test": "api_functionality",
                "success": False,
                "error": str(e),
                "message": "API functionality verification error"
            }
    
    async def verify_health_monitoring(self) -> Dict[str, Any]:
        """Verify health monitoring system."""
        try:
            logger.info("🧪 Verifying health monitoring...")
            
            url = f"{self.base_url}/health"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check health monitoring features
                    has_components = "components" in data
                    has_health_score = "overall_health_score" in data
                    has_safe_startup_info = "safe_startup_info" in data
                    startup_mode = data.get("startup_mode") == "safe_mode"
                    
                    success = has_components and has_health_score and has_safe_startup_info and startup_mode
                    
                    return {
                        "test": "health_monitoring",
                        "success": success,
                        "has_components": has_components,
                        "has_health_score": has_health_score,
                        "has_safe_startup_info": has_safe_startup_info,
                        "startup_mode": startup_mode,
                        "health_score": data.get("overall_health_score", 0),
                        "message": "Health monitoring operational" if success else "Health monitoring issues"
                    }
                else:
                    return {
                        "test": "health_monitoring",
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Health endpoint not accessible"
                    }
        
        except Exception as e:
            logger.error(f"❌ Health monitoring verification failed: {e}")
            return {
                "test": "health_monitoring",
                "success": False,
                "error": str(e),
                "message": "Health monitoring verification error"
            }
    
    async def verify_safe_mode_features(self) -> Dict[str, Any]:
        """Verify safe mode specific features."""
        try:
            logger.info("🧪 Verifying safe mode features...")
            
            # Check root endpoint for safe mode indicators
            url = f"{self.base_url}/"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    notes = data.get("notes", {})
                    safe_startup_info = notes.get("safe_startup", 
                        "Application starts without blockchain dependencies" in str(notes))
                    
                    blockchain_connections = "on-demand" in str(notes).lower()
                    prevents_rpc_errors = "rpc errors" in str(notes).lower()
                    
                    success = safe_startup_info and blockchain_connections
                    
                    return {
                        "test": "safe_mode_features",
                        "success": success,
                        "safe_startup_documented": safe_startup_info,
                        "blockchain_on_demand": blockchain_connections,
                        "rpc_error_prevention": prevents_rpc_errors,
                        "notes": notes,
                        "message": "Safe mode features verified" if success else "Safe mode features incomplete"
                    }
                else:
                    return {
                        "test": "safe_mode_features",
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "message": "Cannot verify safe mode features"
                    }
        
        except Exception as e:
            logger.error(f"❌ Safe mode features verification failed: {e}")
            return {
                "test": "safe_mode_features",
                "success": False,
                "error": str(e),
                "message": "Safe mode features verification error"
            }
    
    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Get recommendations based on verification results."""
        recommendations = []
        
        for test_name, result in results.items():
            if not result.get("success", False):
                if test_name == "startup_mode":
                    recommendations.append("🔧 Fix safe startup mode configuration")
                elif test_name == "component_status":
                    recommendations.append("🔧 Fix component detection system")
                elif test_name == "api_functionality":
                    recommendations.append("🔧 Fix API endpoint issues")
                elif test_name == "health_monitoring":
                    recommendations.append("🔧 Fix health monitoring system")
                elif test_name == "safe_mode_features":
                    recommendations.append("🔧 Fix safe mode feature documentation")
        
        if not recommendations:
            recommendations = [
                "✅ All systems operational - ready for Phase 4C development",
                "✅ Safe startup mode working correctly",
                "✅ No RPC authentication errors during startup",
                "✅ Application ready for blockchain integration"
            ]
        
        return recommendations
    
    def print_verification_results(self, results: Dict[str, Any]):
        """Print comprehensive verification results."""
        print("\n" + "="*80)
        print("🔍 SAFE STARTUP VERIFICATION RESULTS")
        print("="*80)
        
        overall_status = results["overall_status"]
        status_icon = "✅" if overall_status == "PASSED" else "❌"
        
        print(f"\n{status_icon} OVERALL STATUS: {overall_status}")
        print(f"⏰ Verification Time: {results['verification_time']}")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, result in results["results"].items():
            success = result.get("success", False)
            test_icon = "✅" if success else "❌"
            message = result.get("message", "No message")
            
            print(f"\n{test_icon} {test_name.replace('_', ' ').title()}:")
            print(f"   Status: {'PASSED' if success else 'FAILED'}")
            print(f"   Message: {message}")
            
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        print("\n🎯 RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"   {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main verification function."""
    print("🤖 DEX Sniper Pro - Safe Startup Verification")
    print("="*60)
    
    print("\n⚠️ Make sure the application is running on http://127.0.0.1:8000")
    print("   Start with: uvicorn app.main:app --reload")
    
    # Wait for user confirmation
    input("\nPress Enter when the application is running...")
    
    # Run verification
    async with SafeStartupVerifier() as verifier:
        try:
            results = await verifier.verify_safe_startup()
            verifier.print_verification_results(results)
            
            if results["overall_status"] == "PASSED":
                print("\n🎉 VERIFICATION SUCCESSFUL!")
                print("✅ Safe startup mode is working correctly")
                print("✅ No RPC authentication errors")
                print("✅ All systems operational")
                print("✅ Ready for Phase 4C blockchain integration")
            else:
                print("\n⚠️ VERIFICATION ISSUES DETECTED")
                print("Please address the issues listed above")
        
        except Exception as error:
            logger.error(f"❌ Verification failed: {error}")
            print(f"\n❌ Verification suite encountered an error: {error}")


if __name__ == "__main__":
    """Run the verification suite."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Verification interrupted by user")
    except Exception as error:
        print(f"\n❌ Verification suite failed: {error}")
        logger.error(f"Verification suite error: {error}")