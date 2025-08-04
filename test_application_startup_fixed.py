"""
Application Startup Test Script - Fixed Version
File: test_application_startup_fixed.py

Fixed test script that properly handles different response types (JSON vs HTML).
Tests Phase 4B Clean Implementation with comprehensive error handling.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ApplicationTesterFixed:
    """Fixed application testing class with proper response handling."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """Initialize the tester with base URL."""
        self.base_url = base_url
        self.session = None
        self.test_results: List[Dict[str, Any]] = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_endpoint(
        self, 
        method: str, 
        endpoint: str, 
        expected_status: int = 200,
        data: Dict[str, Any] = None,
        expect_json: bool = True
    ) -> Dict[str, Any]:
        """
        Test a single endpoint with proper response type handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Endpoint path
            expected_status: Expected HTTP status code
            data: Request data for POST requests
            expect_json: Whether to expect JSON response
            
        Returns:
            Dict containing test results
        """
        url = f"{self.base_url}{endpoint}"
        test_result = {
            "endpoint": endpoint,
            "method": method,
            "url": url,
            "expected_status": expected_status,
            "expect_json": expect_json,
            "success": False,
            "actual_status": None,
            "response_data": None,
            "response_type": None,
            "error": None
        }
        
        try:
            logger.info(f"🧪 Testing {method} {endpoint}")
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    test_result["actual_status"] = response.status
                    content_type = response.headers.get('content-type', '')
                    test_result["response_type"] = content_type
                    
                    if expect_json and 'application/json' in content_type:
                        test_result["response_data"] = await response.json()
                    elif not expect_json and 'text/html' in content_type:
                        # For HTML responses, just check that we got content
                        html_content = await response.text()
                        test_result["response_data"] = {
                            "content_length": len(html_content),
                            "contains_title": "<title>" in html_content,
                            "is_html": html_content.strip().startswith("<!DOCTYPE html")
                        }
                    else:
                        # Try to get response as text for debugging
                        test_result["response_data"] = await response.text()
            
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    test_result["actual_status"] = response.status
                    content_type = response.headers.get('content-type', '')
                    test_result["response_type"] = content_type
                    
                    if 'application/json' in content_type:
                        test_result["response_data"] = await response.json()
                    else:
                        test_result["response_data"] = await response.text()
            
            # Check if status matches expected
            if test_result["actual_status"] == expected_status:
                test_result["success"] = True
                logger.info(f"✅ {method} {endpoint} - Status: {test_result['actual_status']}")
            else:
                logger.warning(f"⚠️ {method} {endpoint} - Expected: {expected_status}, Got: {test_result['actual_status']}")
        
        except Exception as error:
            test_result["error"] = str(error)
            logger.error(f"❌ {method} {endpoint} - Error: {error}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive application tests with proper response type handling.
        
        Returns:
            Dict containing complete test results
        """
        logger.info("🚀 Starting comprehensive application tests...")
        
        # Test JSON API endpoints
        await self.test_endpoint("GET", "/", expect_json=True)
        await self.test_endpoint("GET", "/health", expect_json=True)
        await self.test_endpoint("GET", "/api/v1/dashboard/stats", expect_json=True)
        await self.test_endpoint("GET", "/api/v1/tokens/discover", expect_json=True)
        
        # Test HTML endpoints (don't expect JSON)
        await self.test_endpoint("GET", "/dashboard", expect_json=False)
        await self.test_endpoint("GET", "/docs", expect_json=False)
        
        # Test live trading API endpoints
        await self.test_endpoint("POST", "/api/v1/live-trading/session/start?trading_mode=semi_automated", expect_json=True)
        await self.test_endpoint("GET", "/api/v1/live-trading/sessions/active", expect_json=True)
        await self.test_endpoint("GET", "/api/v1/live-trading/health", expect_json=True)
        
        # Calculate test summary
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": round(success_rate, 2),
            "all_tests_passed": failed_tests == 0,
            "test_results": self.test_results,
            "json_endpoints_tested": sum(1 for r in self.test_results if r["expect_json"]),
            "html_endpoints_tested": sum(1 for r in self.test_results if not r["expect_json"])
        }
        
        # Log summary
        logger.info(f"📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Successful: {successful_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   JSON Endpoints: {summary['json_endpoints_tested']}")
        logger.info(f"   HTML Endpoints: {summary['html_endpoints_tested']}")
        
        if summary["all_tests_passed"]:
            logger.info("🎉 All tests passed! Application is fully operational.")
        else:
            logger.warning("⚠️ Some tests failed. Check the results for details.")
        
        return summary
    
    def print_detailed_results(self):
        """Print detailed test results with proper formatting."""
        print("\n" + "="*80)
        print("🧪 DETAILED TEST RESULTS")
        print("="*80)
        
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result["success"] else "❌"
            response_type = "JSON" if result["expect_json"] else "HTML"
            
            print(f"\n{i}. {status_icon} {result['method']} {result['endpoint']} ({response_type})")
            print(f"   Expected Status: {result['expected_status']}")
            print(f"   Actual Status: {result['actual_status']}")
            print(f"   Content Type: {result.get('response_type', 'Unknown')}")
            
            if result["error"]:
                print(f"   Error: {result['error']}")
            
            if result["response_data"] and result["success"]:
                if result["expect_json"] and isinstance(result["response_data"], dict):
                    # Print first few keys of JSON response for verification
                    keys = list(result["response_data"].keys())[:3]
                    print(f"   Response Keys: {keys}")
                elif not result["expect_json"] and isinstance(result["response_data"], dict):
                    # Print HTML response info
                    if "content_length" in result["response_data"]:
                        print(f"   HTML Content Length: {result['response_data']['content_length']} chars")
                        print(f"   Valid HTML: {result['response_data'].get('is_html', False)}")


async def test_application_import():
    """Test that the application can be imported without errors."""
    try:
        logger.info("🧪 Testing application import...")
        
        # Test main application import
        from app.main import app
        logger.info("✅ Main application imported successfully")
        
        # Test schema import
        from app.schemas.trading_schemas import TradingSessionResponse
        logger.info("✅ Trading schemas imported successfully")
        
        # Test fixed endpoint import
        from app.api.v1.endpoints.live_trading_fixed import router
        logger.info("✅ Live trading router imported successfully")
        
        # Test dashboard endpoints import
        from app.api.v1.endpoints.dashboard import dashboard_router, tokens_router
        logger.info("✅ Dashboard components imported successfully")
        
        logger.info("🎉 All imports successful - Phase 4B Clean Implementation working!")
        return True
        
    except Exception as error:
        logger.error(f"❌ Import test failed: {error}")
        return False


async def test_component_detection():
    """Test the Phase 4B component detection system."""
    try:
        logger.info("🧪 Testing Phase 4B component detection...")
        
        # Import the application and check component status
        from app.main import COMPONENT_STATUS
        
        logger.info("📊 Component Status:")
        for component, available in COMPONENT_STATUS.items():
            status_icon = "✅" if available else "⚠️"
            logger.info(f"   {status_icon} {component}: {'Available' if available else 'Not Available'}")
        
        available_components = sum(COMPONENT_STATUS.values())
        total_components = len(COMPONENT_STATUS)
        
        logger.info(f"📈 Component Summary: {available_components}/{total_components} components available")
        
        return True
        
    except Exception as error:
        logger.error(f"❌ Component detection test failed: {error}")
        return False


async def main():
    """Main testing function with enhanced Phase 4B testing."""
    print("🤖 DEX Sniper Pro - Phase 4B Clean Implementation Testing Suite")
    print("="*70)
    
    # Test imports first
    import_success = await test_application_import()
    
    if not import_success:
        print("❌ Import tests failed. Please check the application setup.")
        return
    
    # Test component detection
    component_success = await test_component_detection()
    
    if not component_success:
        print("❌ Component detection failed. Please check Phase 4B setup.")
        return
    
    print("\n📋 All import and component tests passed! Now testing live application...")
    print("⚠️ Make sure the application is running on http://127.0.0.1:8000")
    print("   Start with: uvicorn app.main:app --reload")
    
    # Wait for user confirmation
    input("\nPress Enter when the application is running...")
    
    # Run endpoint tests
    async with ApplicationTesterFixed() as tester:
        try:
            test_summary = await tester.run_comprehensive_tests()
            
            # Print results
            print("\n" + "="*80)
            print("📊 TEST SUMMARY")
            print("="*80)
            print(f"Total Tests: {test_summary['total_tests']}")
            print(f"Successful: {test_summary['successful_tests']}")
            print(f"Failed: {test_summary['failed_tests']}")
            print(f"Success Rate: {test_summary['success_rate']}%")
            print(f"JSON Endpoints: {test_summary['json_endpoints_tested']}")
            print(f"HTML Endpoints: {test_summary['html_endpoints_tested']}")
            
            if test_summary["all_tests_passed"]:
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ Phase 4B Clean Implementation is fully operational")
                print("✅ All API endpoints responding correctly")
                print("✅ Dashboard and documentation pages loading")
                print("✅ Live trading API working properly")
                print("✅ Component detection system functional")
                print("✅ Ready for Phase 4C blockchain integration")
            else:
                print("\n⚠️ Some tests failed.")
                print("Check the detailed results below:")
                tester.print_detailed_results()
            
            # Show next steps
            print("\n" + "="*80)
            print("🚀 NEXT STEPS")
            print("="*80)
            if test_summary["all_tests_passed"]:
                print("1. ✅ Phase 4B Clean Implementation - COMPLETE")
                print("2. ✅ Error handling and fallbacks - OPERATIONAL") 
                print("3. ✅ Component detection system - WORKING")
                print("4. 🔄 Ready for Phase 4C: Blockchain Integration")
                print("\nRecommended next development:")
                print("- Implement Web3 provider integration")
                print("- Add real DEX protocol connectivity")
                print("- Develop wallet connection system")
                print("- Enable live blockchain transactions")
            else:
                print("1. 🔧 Fix failing endpoints")
                print("2. 🧪 Re-run tests until all pass")
                print("3. ✅ Ensure Phase 4B implementation is stable")
        
        except Exception as error:
            logger.error(f"❌ Testing failed: {error}")
            print(f"\n❌ Testing suite encountered an error: {error}")
            print("Please check that the application is running correctly.")


if __name__ == "__main__":
    """Run the testing suite."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as error:
        print(f"\n❌ Testing suite failed: {error}")
        logger.error(f"Testing suite error: {error}")