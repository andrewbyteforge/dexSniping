#!/usr/bin/env python3
"""
Application Test and Validation Script
File: test_application.py

Comprehensive testing to ensure the DEX Sniper application is working correctly.
Tests all endpoints, functionality, and provides detailed reporting.
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple


class TestRunner:
    """Comprehensive test runner for the DEX Sniper application."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        self.start_time = datetime.now()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_time_ms: float = 0):
        """Log a test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_time_ms": response_time_ms
        })
        
        timing_info = f" ({response_time_ms:.0f}ms)" if response_time_ms > 0 else ""
        print(f"{status}: {test_name}{timing_info}")
        if details and not success:
            print(f"      Details: {details}")
    
    async def test_endpoint(
        self, 
        client: httpx.AsyncClient, 
        endpoint: str, 
        expected_status: int = 200,
        test_name: str = None,
        validate_json: bool = True,
        required_fields: List[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Test a single endpoint."""
        test_name = test_name or f"Endpoint {endpoint}"
        
        try:
            start_time = datetime.now()
            response = await client.get(f"{self.base_url}{endpoint}")
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Check status code
            if response.status_code != expected_status:
                self.log_test(test_name, False, f"Expected {expected_status}, got {response.status_code}", response_time_ms)
                return False, {}
            
            # Validate JSON response if requested
            if validate_json:
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    self.log_test(test_name, False, f"Invalid JSON response: {e}", response_time_ms)
                    return False, {}
                
                # Check required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test(test_name, False, f"Missing required fields: {missing_fields}", response_time_ms)
                        return False, data
                
                self.log_test(test_name, True, f"JSON response valid", response_time_ms)
                return True, data
            else:
                self.log_test(test_name, True, f"HTML response received", response_time_ms)
                return True, {}
        
        except httpx.ConnectError:
            self.log_test(test_name, False, "Connection refused - is the app running on port 8001?")
            return False, {}
        except httpx.TimeoutException:
            self.log_test(test_name, False, "Request timeout")
            return False, {}
        except Exception as e:
            self.log_test(test_name, False, f"Unexpected error: {str(e)}")
            return False, {}
    
    async def test_health_endpoint(self, client: httpx.AsyncClient):
        """Test health check endpoint."""
        print("\n🏥 Testing Health Check Endpoint")
        print("-" * 40)
        
        required_fields = ["status", "timestamp", "components"]
        success, data = await self.test_endpoint(
            client, 
            "/api/v1/health",
            test_name="Health Check",
            required_fields=required_fields
        )
        
        if success and data:
            # Additional health check validations
            if data.get("status") == "healthy":
                self.log_test("Health Status", True, "System reports healthy")
            else:
                self.log_test("Health Status", False, f"System status: {data.get('status')}")
            
            components = data.get("components", {})
            if isinstance(components, dict) and len(components) > 0:
                self.log_test("Health Components", True, f"Found {len(components)} components")
            else:
                self.log_test("Health Components", False, "No components in health response")
    
    async def test_dashboard_endpoints(self, client: httpx.AsyncClient):
        """Test dashboard API endpoints."""
        print("\n📊 Testing Dashboard API Endpoints")
        print("-" * 40)
        
        # Dashboard stats
        required_stats_fields = ["portfolio_value", "daily_pnl", "trades_today", "success_rate"]
        success, stats_data = await self.test_endpoint(
            client,
            "/api/v1/dashboard/stats",
            test_name="Dashboard Stats",
            required_fields=required_stats_fields
        )
        
        if success and stats_data:
            # Validate stats data types
            try:
                portfolio_value = float(stats_data.get("portfolio_value", 0))
                success_rate = float(stats_data.get("success_rate", 0))
                trades_today = int(stats_data.get("trades_today", 0))
                
                if 0 <= success_rate <= 100:
                    self.log_test("Stats Data Validation", True, "Success rate within valid range")
                else:
                    self.log_test("Stats Data Validation", False, f"Success rate out of range: {success_rate}")
                    
            except (ValueError, TypeError) as e:
                self.log_test("Stats Data Validation", False, f"Data type validation failed: {e}")
        
        # Live tokens
        success, tokens_data = await self.test_endpoint(
            client,
            "/api/v1/dashboard/tokens/live",
            test_name="Live Tokens"
        )
        
        if success and tokens_data:
            if isinstance(tokens_data, list) and len(tokens_data) > 0:
                self.log_test("Tokens Data", True, f"Received {len(tokens_data)} tokens")
                
                # Validate first token structure
                first_token = tokens_data[0]
                required_token_fields = ["symbol", "name", "address", "price"]
                missing_token_fields = [field for field in required_token_fields if field not in first_token]
                
                if not missing_token_fields:
                    self.log_test("Token Structure", True, "Token data structure valid")
                else:
                    self.log_test("Token Structure", False, f"Missing fields: {missing_token_fields}")
            else:
                self.log_test("Tokens Data", False, "No tokens received or invalid format")
        
        # Trading metrics
        required_metrics_fields = ["timeframe", "total_trades", "success_rate", "net_profit"]
        success, metrics_data = await self.test_endpoint(
            client,
            "/api/v1/dashboard/trading/metrics",
            test_name="Trading Metrics",
            required_fields=required_metrics_fields
        )
        
        if success and metrics_data:
            timeframe = metrics_data.get("timeframe")
            if timeframe in ["1h", "4h", "24h", "7d", "30d"]:
                self.log_test("Metrics Timeframe", True, f"Valid timeframe: {timeframe}")
            else:
                self.log_test("Metrics Timeframe", False, f"Invalid timeframe: {timeframe}")
    
    async def test_dashboard_refresh(self, client: httpx.AsyncClient):
        """Test dashboard refresh endpoint."""
        print("\n🔄 Testing Dashboard Refresh")
        print("-" * 40)
        
        try:
            start_time = datetime.now()
            response = await client.post(f"{self.base_url}/api/v1/dashboard/refresh")
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 202:  # Accepted
                data = response.json()
                if "message" in data and "timestamp" in data:
                    self.log_test("Dashboard Refresh", True, "Refresh initiated successfully", response_time_ms)
                else:
                    self.log_test("Dashboard Refresh", False, "Missing required response fields", response_time_ms)
            else:
                self.log_test("Dashboard Refresh", False, f"Expected 202, got {response.status_code}", response_time_ms)
                
        except Exception as e:
            self.log_test("Dashboard Refresh", False, f"Request failed: {str(e)}")
    
    async def test_frontend_pages(self, client: httpx.AsyncClient):
        """Test frontend page endpoints."""
        print("\n🌐 Testing Frontend Pages")
        print("-" * 40)
        
        # Root page
        await self.test_endpoint(
            client,
            "/",
            test_name="Root Page",
            validate_json=False
        )
        
        # Dashboard page
        await self.test_endpoint(
            client,
            "/dashboard",
            test_name="Dashboard Page",
            validate_json=False
        )
    
    async def test_api_documentation(self, client: httpx.AsyncClient):
        """Test API documentation endpoint."""
        print("\n📚 Testing API Documentation")
        print("-" * 40)
        
        await self.test_endpoint(
            client,
            "/docs",
            test_name="API Documentation",
            validate_json=False
        )
        
        await self.test_endpoint(
            client,
            "/openapi.json",
            test_name="OpenAPI Schema"
        )
    
    async def test_error_handling(self, client: httpx.AsyncClient):
        """Test error handling for non-existent endpoints."""
        print("\n❌ Testing Error Handling")
        print("-" * 40)
        
        await self.test_endpoint(
            client,
            "/api/v1/nonexistent",
            expected_status=404,
            test_name="404 Error Handling"
        )
    
    async def run_all_tests(self):
        """Run all test suites."""
        print("🧪 DEX Sniper Application Testing Suite")
        print("=" * 60)
        print(f"Testing application at: {self.base_url}")
        print(f"Test started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test suites
            await self.test_health_endpoint(client)
            await self.test_dashboard_endpoints(client)
            await self.test_dashboard_refresh(client)
            await self.test_frontend_pages(client)
            await self.test_api_documentation(client)
            await self.test_error_handling(client)
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate and print final test report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 FINAL TEST REPORT")
        print("=" * 60)
        
        print(f"📋 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   🎯 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️ Duration: {duration:.2f} seconds")
        
        # Performance summary
        response_times = [r["response_time_ms"] for r in self.test_results if r["response_time_ms"] > 0]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"\n⚡ Performance:")
            print(f"   Average Response Time: {avg_response_time:.0f}ms")
            print(f"   Slowest Response: {max_response_time:.0f}ms")
        
        # Failed tests details
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        print(f"\n🎯 Overall Assessment:")
        if success_rate >= 95:
            print("   🎉 EXCELLENT - Application is working perfectly!")
            print("   ✅ Ready for production use and AI implementation")
        elif success_rate >= 85:
            print("   ✅ GOOD - Application is working well with minor issues")
            print("   ⚠️ Consider fixing failed tests before proceeding")
        elif success_rate >= 70:
            print("   ⚠️ FAIR - Application has some issues that should be addressed")
            print("   🔧 Fix critical failures before proceeding")
        else:
            print("   ❌ POOR - Application has significant issues")
            print("   🚨 Major fixes required before proceeding")
        
        print(f"\n📋 Next Steps:")
        if success_rate >= 90:
            print("   1. ✅ Application is ready for AI Risk Assessment implementation")
            print("   2. 🚀 Proceed with Phase 3B Week 7-8 AI features")
            print("   3. 📈 Monitor performance in production")
        else:
            print("   1. 🔧 Review and fix failed tests")
            print("   2. 🔄 Re-run tests until success rate > 90%")
            print("   3. 🚀 Then proceed with AI implementation")


async def main():
    """Main test execution function."""
    print("🔍 Checking if application is running...")
    
    try:
        # Quick connectivity test
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://127.0.0.1:8001/api/v1/health")
            if response.status_code == 200:
                print("✅ Application is running and responsive")
            else:
                print(f"⚠️ Application responded with status {response.status_code}")
    except httpx.ConnectError:
        print("❌ ERROR: Cannot connect to application")
        print("   Make sure the application is running with:")
        print("   uvicorn app.main:app --reload --port 8001")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    print()
    
    # Run comprehensive tests
    runner = TestRunner()
    await runner.run_all_tests()
    
    # Return success status
    total_tests = runner.passed_tests + runner.failed_tests
    success_rate = (runner.passed_tests / total_tests * 100) if total_tests > 0 else 0
    return success_rate >= 90


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)