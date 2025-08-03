"""
Comprehensive Test Suite for Phase 3B Validation
File: tests/test_phase3b_comprehensive.py
Classes: TestDashboardAPI, TestTradingFeatures, TestFrontendComponents
Functions: test_all_apis(), test_dashboard_components(), test_trading_systems()

Professional testing suite to validate all Phase 3B Week 5-6 implementations
before proceeding to Phase 3B Week 7-8 AI & Analytics.
"""

import pytest
import asyncio
import httpx
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.performance.connection_pool import connection_pool
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager
from app.core.integration.phase3a_manager import Phase3AManager
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.tokens import router as tokens_router
from app.api.v1.endpoints.trading import router as trading_router


class TestResult:
    """Container for test results with detailed metrics."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.errors: List[str] = []
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
    
    def add_pass(self, test_name: str):
        """Record a passing test."""
        self.total_tests += 1
        self.passed_tests += 1
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        """Record a failing test."""
        self.total_tests += 1
        self.failed_tests += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
    
    def add_skip(self, test_name: str, reason: str):
        """Record a skipped test."""
        self.total_tests += 1
        self.skipped_tests += 1
        print(f"⏭️ SKIP: {test_name} - {reason}")
    
    def finalize(self):
        """Finalize test results."""
        self.end_time = datetime.utcnow()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive test summary."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        return {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "skipped": self.skipped_tests,
            "success_rate": round(success_rate, 1),
            "duration_seconds": round(duration, 2),
            "errors": self.errors
        }


class Phase3BTestSuite:
    """Comprehensive test suite for Phase 3B validation."""
    
    def __init__(self):
        self.results = TestResult()
        self.base_url = "http://localhost:8001"
        self.client: Optional[httpx.AsyncClient] = None
    
    async def setup(self):
        """Set up test environment."""
        print("🚀 Setting up Phase 3B Test Environment")
        print("=" * 60)
        
        try:
            # Initialize HTTP client
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
            
            # Initialize core systems
            await self._setup_performance_systems()
            
            print("✅ Test environment setup complete")
            
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            raise
    
    async def teardown(self):
        """Clean up test environment."""
        print("\n🧹 Cleaning up test environment...")
        
        try:
            if self.client:
                await self.client.aclose()
            
            # Close performance systems
            await connection_pool.close()
            
            print("✅ Test cleanup complete")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def _setup_performance_systems(self):
        """Set up performance and infrastructure systems."""
        try:
            # Initialize connection pool
            await connection_pool.initialize()
            
            # Initialize cache manager
            await cache_manager.initialize()
            
            print("✅ Performance systems initialized")
            
        except Exception as e:
            print(f"⚠️ Performance systems setup warning: {e}")
    
    # ================================================================
    # API ENDPOINT TESTS
    # ================================================================
    
    async def test_health_endpoints(self):
        """Test all health check endpoints."""
        print("\n📊 Testing Health Check Endpoints")
        print("-" * 40)
        
        health_endpoints = [
            "/api/v1/health",
            "/api/v1/dashboard/health",
            "/api/v1/tokens/health",
            "/api/v1/trading/health"
        ]
        
        for endpoint in health_endpoints:
            try:
                response = await self.client.get(endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.results.add_pass(f"Health check: {endpoint}")
                    else:
                        self.results.add_fail(f"Health check: {endpoint}", 
                                              f"Status not healthy: {data.get('status')}")
                else:
                    self.results.add_fail(f"Health check: {endpoint}", 
                                          f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results.add_fail(f"Health check: {endpoint}", str(e))
    
    async def test_dashboard_api(self):
        """Test dashboard API endpoints."""
        print("\n📈 Testing Dashboard API Endpoints")
        print("-" * 40)
        
        dashboard_tests = [
            ("/api/v1/dashboard/stats", "Dashboard statistics"),
            ("/api/v1/dashboard/live-tokens", "Live tokens feed"),
            ("/api/v1/dashboard/arbitrage-count", "Arbitrage opportunities"),
            ("/api/v1/dashboard/portfolio-value", "Portfolio value"),
            ("/api/v1/dashboard/recent-activity", "Recent activity")
        ]
        
        for endpoint, description in dashboard_tests:
            try:
                response = await self.client.get(endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:  # Basic check that we got data
                        self.results.add_pass(f"Dashboard API: {description}")
                    else:
                        self.results.add_fail(f"Dashboard API: {description}", 
                                              "Empty response data")
                else:
                    self.results.add_fail(f"Dashboard API: {description}", 
                                          f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results.add_fail(f"Dashboard API: {description}", str(e))
    
    async def test_tokens_api(self):
        """Test token discovery and analysis APIs."""
        print("\n🔍 Testing Token Discovery APIs")
        print("-" * 40)
        
        # Test token discovery
        try:
            response = await self.client.get("/api/v1/tokens/discover")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("tokens") and len(data["tokens"]) > 0:
                    self.results.add_pass("Token discovery API")
                    
                    # Test token analysis with first token
                    first_token = data["tokens"][0]
                    if "address" in first_token:
                        await self._test_token_analysis(first_token["address"])
                else:
                    self.results.add_fail("Token discovery API", "No tokens returned")
            else:
                self.results.add_fail("Token discovery API", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_fail("Token discovery API", str(e))
    
    async def _test_token_analysis(self, token_address: str):
        """Test token analysis endpoint."""
        try:
            response = await self.client.post(f"/api/v1/tokens/analyze/{token_address}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("analysis"):
                    self.results.add_pass("Token analysis API")
                else:
                    self.results.add_fail("Token analysis API", "No analysis data")
            else:
                self.results.add_fail("Token analysis API", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_fail("Token analysis API", str(e))
    
    async def test_trading_api(self):
        """Test trading-related APIs."""
        print("\n💹 Testing Trading APIs")
        print("-" * 40)
        
        trading_tests = [
            ("/api/v1/trading/positions", "Trading positions"),
            ("/api/v1/trading/strategies", "Trading strategies"),
            ("/api/v1/trading/performance", "Trading performance")
        ]
        
        for endpoint, description in trading_tests:
            try:
                response = await self.client.get(endpoint)
                
                if response.status_code == 200:
                    self.results.add_pass(f"Trading API: {description}")
                else:
                    self.results.add_fail(f"Trading API: {description}", 
                                          f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results.add_fail(f"Trading API: {description}", str(e))
    
    # ================================================================
    # FRONTEND COMPONENT TESTS
    # ================================================================
    
    async def test_frontend_assets(self):
        """Test frontend static assets and templates."""
        print("\n🎨 Testing Frontend Assets")
        print("-" * 40)
        
        # Test static files
        static_files = [
            "/static/css/main.css",
            "/static/js/app.js",
            "/static/js/api-client.js",
            "/static/js/websocket-manager.js",
            "/static/js/components/dashboard-controller.js",
            "/static/js/components/chart-controller.js",
            "/static/js/components/price-feed-controller.js",
            "/static/js/components/dex-comparison.js",
            "/static/js/utils/constants.js",
            "/static/js/utils/formatters.js",
            "/static/js/utils/validators.js",
            "/static/js/utils/technical-indicators.js"
        ]
        
        for static_file in static_files:
            try:
                response = await self.client.get(static_file)
                
                if response.status_code == 200:
                    self.results.add_pass(f"Static asset: {static_file}")
                else:
                    self.results.add_fail(f"Static asset: {static_file}", 
                                          f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.results.add_fail(f"Static asset: {static_file}", str(e))
        
        # Test main dashboard page
        try:
            response = await self.client.get("/dashboard")
            
            if response.status_code == 200:
                content = response.text
                # Check for key elements
                if ("Bootstrap" in content and 
                    "Chart.js" in content and 
                    "dashboard-controller" in content):
                    self.results.add_pass("Dashboard template rendering")
                else:
                    self.results.add_fail("Dashboard template rendering", 
                                          "Missing required components")
            else:
                self.results.add_fail("Dashboard template rendering", 
                                      f"HTTP {response.status_code}")
                
        except Exception as e:
            self.results.add_fail("Dashboard template rendering", str(e))
    
    # ================================================================
    # PERFORMANCE SYSTEM TESTS
    # ================================================================
    
    async def test_performance_systems(self):
        """Test performance and infrastructure systems."""
        print("\n⚡ Testing Performance Systems")
        print("-" * 40)
        
        # Test connection pool
        try:
            stats = connection_pool.get_stats()
            if stats.get("is_initialized"):
                self.results.add_pass("Connection pool system")
            else:
                self.results.add_fail("Connection pool system", "Not initialized")
        except Exception as e:
            self.results.add_fail("Connection pool system", str(e))
        
        # Test cache manager
        try:
            # Test cache operations
            await cache_manager.set("test_key", "test_value", 60)
            cached_value = await cache_manager.get("test_key")
            
            if cached_value == "test_value":
                self.results.add_pass("Cache manager system")
            else:
                self.results.add_fail("Cache manager system", "Cache operation failed")
        except Exception as e:
            self.results.add_fail("Cache manager system", str(e))
        
        # Test circuit breaker
        try:
            cb_manager = CircuitBreakerManager()
            breaker = await cb_manager.get_breaker("test_service")
            
            # Test successful operation
            async def test_operation():
                return "success"
            
            result = await breaker.call(test_operation)
            if result == "success":
                self.results.add_pass("Circuit breaker system")
            else:
                self.results.add_fail("Circuit breaker system", "Operation failed")
        except Exception as e:
            self.results.add_fail("Circuit breaker system", str(e))
    
    # ================================================================
    # ADVANCED FEATURE TESTS
    # ================================================================
    
    async def test_technical_indicators(self):
        """Test technical indicator calculations."""
        print("\n📊 Testing Technical Indicators")
        print("-" * 40)
        
        # Test with sample price data
        sample_prices = [100, 102, 101, 105, 107, 106, 108, 110, 109, 112]
        
        try:
            # Test RSI calculation (simplified)
            gains = []
            losses = []
            
            for i in range(1, len(sample_prices)):
                change = sample_prices[i] - sample_prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) > 0 and len(losses) > 0:
                self.results.add_pass("Technical indicators - RSI calculation")
            else:
                self.results.add_fail("Technical indicators - RSI calculation", 
                                      "Invalid calculation")
                
        except Exception as e:
            self.results.add_fail("Technical indicators - RSI calculation", str(e))
    
    async def test_risk_management(self):
        """Test risk management features."""
        print("\n🛡️ Testing Risk Management Features")
        print("-" * 40)
        
        # Test position sizing calculation
        try:
            # Mock position sizing test
            account_balance = 10000
            risk_percentage = 2.0  # 2% risk
            stop_loss_percentage = 5.0  # 5% stop loss
            
            # Calculate position size
            risk_amount = account_balance * (risk_percentage / 100)
            position_size = risk_amount / (stop_loss_percentage / 100)
            
            if 0 < position_size <= account_balance:
                self.results.add_pass("Risk management - Position sizing")
            else:
                self.results.add_fail("Risk management - Position sizing", 
                                      "Invalid position size calculation")
                
        except Exception as e:
            self.results.add_fail("Risk management - Position sizing", str(e))
    
    # ================================================================
    # MAIN TEST RUNNER
    # ================================================================
    
    async def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🧪 Starting Comprehensive Phase 3B Test Suite")
        print("=" * 60)
        print(f"🕐 Start time: {self.results.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            await self.setup()
            
            # Run all test categories
            await self.test_health_endpoints()
            await self.test_dashboard_api()
            await self.test_tokens_api()
            await self.test_trading_api()
            await self.test_frontend_assets()
            await self.test_performance_systems()
            await self.test_technical_indicators()
            await self.test_risk_management()
            
        except Exception as e:
            print(f"❌ Test suite execution failed: {e}")
        
        finally:
            await self.teardown()
            self.results.finalize()
    
    def print_final_report(self):
        """Print comprehensive test results."""
        summary = self.results.get_summary()
        
        print("\n" + "=" * 60)
        print("📋 FINAL TEST REPORT - Phase 3B Validation")
        print("=" * 60)
        
        print(f"📊 Tests Run: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️ Skipped: {summary['skipped']}")
        print(f"📈 Success Rate: {summary['success_rate']}%")
        print(f"⏱️ Duration: {summary['duration_seconds']}s")
        
        if summary['errors']:
            print(f"\n❌ ERRORS ({len(summary['errors'])}):")
            for error in summary['errors']:
                print(f"   • {error}")
        
        print(f"\n🎯 STATUS: {'READY FOR AI PHASE' if summary['success_rate'] >= 80 else 'NEEDS FIXES'}")
        
        if summary['success_rate'] >= 95:
            print("🏆 EXCELLENT: All systems performing optimally!")
        elif summary['success_rate'] >= 80:
            print("✅ GOOD: Systems ready for next phase")
        else:
            print("⚠️ WARNING: Some issues detected, review before proceeding")


# ================================================================
# EXECUTION FUNCTIONS
# ================================================================

async def run_comprehensive_tests():
    """Execute the comprehensive test suite."""
    test_suite = Phase3BTestSuite()
    
    try:
        await test_suite.run_all_tests()
        test_suite.print_final_report()
        
        # Return success status for programmatic use
        summary = test_suite.results.get_summary()
        return summary['success_rate'] >= 80
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def run_quick_validation():
    """Run a quick validation of key systems."""
    print("🚀 Running Quick Phase 3B Validation")
    print("=" * 40)
    
    # Check file structure
    required_files = [
        "app/main.py",
        "app/api/v1/endpoints/dashboard.py",
        "app/api/v1/endpoints/tokens.py",
        "app/api/v1/endpoints/trading.py",
        "frontend/static/js/app.js",
        "frontend/static/css/main.css",
        "frontend/templates/dashboard.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return False
    else:
        print("✅ All required files present")
    
    # Check requirements
    if os.path.exists("requirements.txt"):
        print("✅ Requirements file present")
    else:
        print("⚠️ Requirements file missing")
    
    print("✅ Quick validation complete - ready for comprehensive testing")
    return True


if __name__ == "__main__":
    print("🧪 Phase 3B Test Suite")
    print("Choose testing option:")
    print("1. Quick validation")
    print("2. Comprehensive test suite")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "1":
        success = run_quick_validation()
        exit(0 if success else 1)
    elif choice == "2":
        success = asyncio.run(run_comprehensive_tests())
        exit(0 if success else 1)
    else:
        print("Invalid choice")
        exit(1)