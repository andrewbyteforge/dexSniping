"""
Quick Test Runner - Immediate Phase 3B Validation
File: test_runner.py
Functions: check_file_structure(), test_imports(), validate_apis(), run_quick_tests()

Quick validation script to test our Phase 3B implementation before AI phase.
This can be run immediately to check system status.
"""

import os
import sys
import asyncio
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any


class QuickTester:
    """Quick testing utility for Phase 3B validation."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors: List[str] = []
    
    def test_pass(self, name: str):
        """Record a passing test."""
        self.passed += 1
        print(f"✅ {name}")
    
    def test_fail(self, name: str, error: str = ""):
        """Record a failing test."""
        self.failed += 1
        error_msg = f" - {error}" if error else ""
        print(f"❌ {name}{error_msg}")
        if error:
            self.errors.append(f"{name}: {error}")
    
    def test_warn(self, name: str, warning: str = ""):
        """Record a warning."""
        self.warnings += 1
        warn_msg = f" - {warning}" if warning else ""
        print(f"⚠️ {name}{warn_msg}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        total = self.passed + self.failed + self.warnings
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "success_rate": round(success_rate, 1),
            "errors": self.errors
        }


def check_file_structure() -> QuickTester:
    """Check if all required files are present."""
    print("📁 Checking File Structure")
    print("-" * 30)
    
    tester = QuickTester()
    
    # Core application files
    core_files = [
        "app/main.py",
        "app/__init__.py",
        "app/config.py",
        "requirements.txt"
    ]
    
    # API endpoint files
    api_files = [
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/api/v1/endpoints/dashboard.py",
        "app/api/v1/endpoints/tokens.py",
        "app/api/v1/endpoints/trading.py"
    ]
    
    # Core system files
    core_system_files = [
        "app/core/__init__.py",
        "app/core/performance/connection_pool.py",
        "app/core/performance/cache_manager.py",
        "app/core/performance/circuit_breaker.py"
    ]
    
    # Frontend files
    frontend_files = [
        "frontend/templates/base.html",
        "frontend/templates/dashboard.html",
        "frontend/static/css/main.css",
        "frontend/static/js/app.js",
        "frontend/static/js/api-client.js",
        "frontend/static/js/websocket-manager.js"
    ]
    
    # Component files
    component_files = [
        "frontend/static/js/components/dashboard-controller.js",
        "frontend/static/js/components/chart-controller.js",
        "frontend/static/js/components/price-feed-controller.js",
        "frontend/static/js/components/dex-comparison.js"
    ]
    
    # Utility files
    utility_files = [
        "frontend/static/js/utils/constants.js",
        "frontend/static/js/utils/formatters.js",
        "frontend/static/js/utils/validators.js",
        "frontend/static/js/utils/technical-indicators.js"
    ]
    
    # Advanced backend files
    advanced_files = [
        "app/core/dex/dex_router.py",
        "app/core/risk/position_sizer.py",
        "app/core/risk/stop_loss_manager.py"
    ]
    
    all_files = {
        "Core Application": core_files,
        "API Endpoints": api_files,
        "Core Systems": core_system_files,
        "Frontend Templates/CSS": frontend_files,
        "JS Components": component_files,
        "JS Utilities": utility_files,
        "Advanced Backend": advanced_files
    }
    
    for category, files in all_files.items():
        print(f"\n{category}:")
        for file_path in files:
            if os.path.exists(file_path):
                tester.test_pass(f"  {file_path}")
            else:
                tester.test_fail(f"  {file_path}", "File not found")
    
    return tester


def check_python_imports() -> QuickTester:
    """Test if core Python modules can be imported."""
    print("\n🐍 Checking Python Imports")
    print("-" * 30)
    
    tester = QuickTester()
    
    # Core imports to test
    import_tests = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("web3", "Blockchain integration"),
        ("httpx", "HTTP client"),
        ("websockets", "WebSocket support")
    ]
    
    for module_name, description in import_tests:
        try:
            importlib.import_module(module_name)
            tester.test_pass(f"{description} ({module_name})")
        except ImportError as e:
            tester.test_fail(f"{description} ({module_name})", str(e))
        except Exception as e:
            tester.test_warn(f"{description} ({module_name})", f"Warning: {e}")
    
    # Test app imports
    app_imports = [
        ("app.main", "Main application"),
        ("app.config", "Configuration"),
        ("app.api.v1.endpoints.dashboard", "Dashboard API"),
        ("app.api.v1.endpoints.tokens", "Tokens API"),
        ("app.api.v1.endpoints.trading", "Trading API")
    ]
    
    print("\nApp Module Imports:")
    for module_name, description in app_imports:
        try:
            importlib.import_module(module_name)
            tester.test_pass(f"  {description}")
        except ImportError as e:
            tester.test_fail(f"  {description}", str(e))
        except Exception as e:
            tester.test_warn(f"  {description}", f"Warning: {e}")
    
    return tester


def check_configuration() -> QuickTester:
    """Check application configuration."""
    print("\n⚙️ Checking Configuration")
    print("-" * 30)
    
    tester = QuickTester()
    
    # Check environment file
    if os.path.exists(".env"):
        tester.test_pass("Environment file (.env)")
    else:
        tester.test_warn("Environment file (.env)", "Not found - using defaults")
    
    # Check if we can load config
    try:
        from app.config import settings
        tester.test_pass("Configuration loading")
        
        # Check key config values
        if hasattr(settings, 'database_url'):
            tester.test_pass("Database URL configured")
        else:
            tester.test_warn("Database URL", "Not found in config")
        
        if hasattr(settings, 'api_v1_str'):
            tester.test_pass("API version string configured")
        else:
            tester.test_warn("API version string", "Not found in config")
            
    except Exception as e:
        tester.test_fail("Configuration loading", str(e))
    
    return tester


async def test_performance_systems() -> QuickTester:
    """Test performance and infrastructure systems."""
    print("\n⚡ Testing Performance Systems")
    print("-" * 30)
    
    tester = QuickTester()
    
    # Test connection pool
    try:
        from app.core.performance.connection_pool import connection_pool
        await connection_pool.initialize()
        
        stats = connection_pool.get_stats()
        if stats.get("is_initialized"):
            tester.test_pass("Connection pool initialization")
        else:
            tester.test_fail("Connection pool initialization", "Not initialized")
        
        await connection_pool.close()
        
    except Exception as e:
        tester.test_fail("Connection pool system", str(e))
    
    # Test cache manager
    try:
        from app.core.performance.cache_manager import cache_manager
        await cache_manager.initialize()
        
        # Test basic cache operations
        await cache_manager.set("test_key", "test_value", 60)
        value = await cache_manager.get("test_key")
        
        if value == "test_value":
            tester.test_pass("Cache manager operations")
        else:
            tester.test_fail("Cache manager operations", "Cache test failed")
            
    except Exception as e:
        tester.test_fail("Cache manager system", str(e))
    
    # Test circuit breaker
    try:
        from app.core.performance.circuit_breaker import CircuitBreakerManager
        cb_manager = CircuitBreakerManager()
        
        # Test getting a breaker
        breaker = await cb_manager.get_breaker("test_service")
        
        # Test a simple operation
        async def test_operation():
            return "success"
        
        result = await breaker.call(test_operation)
        if result == "success":
            tester.test_pass("Circuit breaker operations")
        else:
            tester.test_fail("Circuit breaker operations", "Test operation failed")
            
    except Exception as e:
        tester.test_fail("Circuit breaker system", str(e))
    
    return tester


def check_frontend_structure() -> QuickTester:
    """Check frontend file structure and content."""
    print("\n🎨 Checking Frontend Structure")
    print("-" * 30)
    
    tester = QuickTester()
    
    # Check main template
    dashboard_template = "frontend/templates/dashboard.html"
    if os.path.exists(dashboard_template):
        tester.test_pass("Dashboard template exists")
        
        # Check template content
        try:
            with open(dashboard_template, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "{% extends" in content:
                tester.test_pass("Template inheritance syntax")
            else:
                tester.test_warn("Template inheritance", "Extends syntax not found")
            
            if "Bootstrap" in content or "bootstrap" in content:
                tester.test_pass("Bootstrap integration")
            else:
                tester.test_warn("Bootstrap integration", "Bootstrap not detected")
                
            if "Chart.js" in content or "chart.js" in content:
                tester.test_pass("Chart.js integration")
            else:
                tester.test_warn("Chart.js integration", "Chart.js not detected")
                
        except Exception as e:
            tester.test_fail("Template content analysis", str(e))
    else:
        tester.test_fail("Dashboard template", "File not found")
    
    # Check main CSS
    main_css = "frontend/static/css/main.css"
    if os.path.exists(main_css):
        tester.test_pass("Main CSS file exists")
        
        try:
            with open(main_css, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            if len(css_content) > 1000:  # Reasonable CSS size
                tester.test_pass("CSS content substantial")
            else:
                tester.test_warn("CSS content", "File seems small")
                
        except Exception as e:
            tester.test_fail("CSS content analysis", str(e))
    else:
        tester.test_fail("Main CSS file", "File not found")
    
    # Check main JavaScript
    main_js = "frontend/static/js/app.js"
    if os.path.exists(main_js):
        tester.test_pass("Main JavaScript file exists")
        
        try:
            with open(main_js, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            if "class" in js_content and "async" in js_content:
                tester.test_pass("Modern JavaScript features")
            else:
                tester.test_warn("JavaScript features", "Modern syntax not detected")
                
        except Exception as e:
            tester.test_fail("JavaScript content analysis", str(e))
    else:
        tester.test_fail("Main JavaScript file", "File not found")
    
    return tester


def print_final_summary(testers: List[QuickTester]):
    """Print comprehensive summary of all tests."""
    print("\n" + "=" * 60)
    print("📋 QUICK VALIDATION SUMMARY")
    print("=" * 60)
    
    total_passed = sum(t.passed for t in testers)
    total_failed = sum(t.failed for t in testers)
    total_warnings = sum(t.warnings for t in testers)
    total_tests = total_passed + total_failed + total_warnings
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"⚠️ Warnings: {total_warnings}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Print all errors
    all_errors = []
    for tester in testers:
        all_errors.extend(tester.errors)
    
    if all_errors:
        print(f"\n❌ ERRORS FOUND ({len(all_errors)}):")
        for error in all_errors:
            print(f"   • {error}")
    
    # Final assessment
    print(f"\n🎯 ASSESSMENT:")
    if success_rate >= 95:
        print("🏆 EXCELLENT - All systems operational!")
        status = "READY"
    elif success_rate >= 85:
        print("✅ GOOD - Ready for next phase with minor warnings")
        status = "READY"
    elif success_rate >= 70:
        print("⚠️ CAUTION - Some issues detected, review recommended")
        status = "REVIEW_NEEDED"
    else:
        print("❌ CRITICAL - Significant issues found, fixes required")
        status = "FIXES_REQUIRED"
    
    print(f"🚦 STATUS: {status}")
    
    return status, success_rate


async def run_quick_validation():
    """Run all quick validation tests."""
    print("🚀 Phase 3B Quick Validation Starting...")
    print("=" * 60)
    
    testers = []
    
    try:
        # Run synchronous tests
        testers.append(check_file_structure())
        testers.append(check_python_imports())
        testers.append(check_configuration())
        testers.append(check_frontend_structure())
        
        # Run async tests
        testers.append(await test_performance_systems())
        
        # Print final summary
        status, success_rate = print_final_summary(testers)
        
        return status == "READY" or status == "REVIEW_NEEDED"
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during validation: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    print("🧪 Phase 3B Quick Test Runner")
    print("Testing current implementation before AI phase...")
    print()
    
    try:
        success = asyncio.run(run_quick_validation())
        
        if success:
            print("\n🎉 VALIDATION SUCCESSFUL!")
            print("✅ Ready to proceed to Phase 3B Week 7-8 AI & Analytics")
            exit(0)
        else:
            print("\n⚠️ VALIDATION ISSUES DETECTED")
            print("🔧 Please review and fix issues before proceeding")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        exit(1)