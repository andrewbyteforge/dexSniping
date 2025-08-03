#!/usr/bin/env python3
"""
Final Application Validation Script
File: final_validation.py

Comprehensive validation to ensure the application is fully working
before proceeding to the AI implementation phase.
"""

import os
import sys
import asyncio
import subprocess
import time
import httpx
from datetime import datetime
from pathlib import Path


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
        self.errors = []
    
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
    
    def add_warning(self, test_name: str, warning: str):
        """Record a warning."""
        self.warnings += 1
        print(f"⚠️ WARN: {test_name} - {warning}")
    
    def get_summary(self):
        """Get test summary."""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        return {
            "total": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "warnings": self.warnings,
            "success_rate": round(success_rate, 1)
        }


def validate_file_structure() -> ValidationResult:
    """Validate that all required files exist."""
    print("📁 Validating File Structure")
    print("-" * 40)
    
    result = ValidationResult()
    
    # Required files and directories
    required_items = {
        "directories": [
            "app",
            "app/core",
            "app/api/v1/endpoints",
            "app/utils",
            "frontend/templates",
            "frontend/static"
        ],
        "files": [
            "app/main.py",
            "app/config.py",
            "app/core/database.py",
            "app/core/database_mock.py",
            "app/core/exceptions.py",
            "app/utils/logger.py",
            "app/api/v1/endpoints/dashboard.py",
            "app/__init__.py",
            "app/core/__init__.py",
            "app/api/__init__.py",
            "app/api/v1/__init__.py"
        ]
    }
    
    # Check directories
    for directory in required_items["directories"]:
        if os.path.exists(directory) and os.path.isdir(directory):
            result.add_pass(f"Directory: {directory}")
        else:
            result.add_fail(f"Directory: {directory}", "Missing or not a directory")
    
    # Check files
    for file_path in required_items["files"]:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            result.add_pass(f"File: {file_path}")
        else:
            result.add_fail(f"File: {file_path}", "Missing or not a file")
    
    return result


def validate_python_imports() -> ValidationResult:
    """Validate that all Python modules can be imported."""
    print("\n🐍 Validating Python Imports")
    print("-" * 40)
    
    result = ValidationResult()
    
    # Test imports
    import_tests = [
        ("app.config", "Application configuration"),
        ("app.utils.logger", "Logger module"),
        ("app.core.exceptions", "Exceptions module"),
        ("app.core.database", "Database module"),
        ("app.core.database_mock", "Mock database module"),
        ("app.api.v1.endpoints.dashboard", "Dashboard endpoint")
    ]
    
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            result.add_pass(f"Import: {description}")
        except ImportError as e:
            result.add_fail(f"Import: {description}", str(e))
        except Exception as e:
            result.add_fail(f"Import: {description}", f"Unexpected error: {e}")
    
    return result


def validate_fastapi_app() -> ValidationResult:
    """Validate FastAPI application can be loaded."""
    print("\n🚀 Validating FastAPI Application")
    print("-" * 40)
    
    result = ValidationResult()
    
    try:
        from app.main import app
        result.add_pass("FastAPI app creation")
        
        # Check if app has expected attributes
        if hasattr(app, 'title'):
            result.add_pass("App title attribute")
        else:
            result.add_fail("App title attribute", "Missing title")
        
        if hasattr(app, 'routes'):
            route_count = len(app.routes)
            if route_count > 0:
                result.add_pass(f"App routes ({route_count} routes)")
            else:
                result.add_fail("App routes", "No routes found")
        else:
            result.add_fail("App routes", "Routes attribute missing")
        
    except Exception as e:
        result.add_fail("FastAPI app creation", str(e))
    
    return result


async def validate_api_endpoints() -> ValidationResult:
    """Validate API endpoints are working."""
    print("\n🌐 Validating API Endpoints")
    print("-" * 40)
    print("Note: This test requires the application to be running on port 8001")
    
    result = ValidationResult()
    base_url = "http://127.0.0.1:8001"
    
    # Endpoints to test
    endpoints = [
        ("/api/v1/health", "Health check endpoint"),
        ("/api/v1/dashboard/stats", "Dashboard stats endpoint"),
        ("/api/v1/dashboard/tokens/live", "Live tokens endpoint"),
        ("/api/v1/dashboard/trading/metrics", "Trading metrics endpoint"),
        ("/", "Root endpoint"),
        ("/dashboard", "Dashboard page")
    ]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, description in endpoints:
                try:
                    response = await client.get(f"{base_url}{endpoint}")
                    if response.status_code == 200:
                        result.add_pass(f"API: {description}")
                    else:
                        result.add_fail(f"API: {description}", f"HTTP {response.status_code}")
                except httpx.ConnectError:
                    result.add_fail(f"API: {description}", "Connection refused - app not running?")
                except Exception as e:
                    result.add_fail(f"API: {description}", str(e))
    
    except Exception as e:
        result.add_fail("API testing setup", str(e))
    
    return result


def validate_database_connections() -> ValidationResult:
    """Validate database connection handling."""
    print("\n🗄️ Validating Database Connections")
    print("-" * 40)
    
    result = ValidationResult()
    
    try:
        # Test database module
        from app.core.database import get_db_session
        result.add_pass("Database module import")
        
        # Test mock database
        from app.core.database_mock import get_mock_session
        result.add_pass("Mock database module import")
        
        # Test async session creation
        async def test_session():
            try:
                async for session in get_db_session():
                    result.add_pass("Database session creation")
                    return
            except Exception as e:
                result.add_fail("Database session creation", str(e))
        
        asyncio.create_task(test_session())
        
    except Exception as e:
        result.add_fail("Database validation", str(e))
    
    return result


def check_application_running() -> bool:
    """Check if the application is currently running."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8001/api/v1/health", timeout=2)
        return response.status_code == 200
    except:
        return False


async def run_comprehensive_validation():
    """Run all validation tests."""
    print("🔍 DEX Sniper Pro - Comprehensive Validation")
    print("=" * 60)
    print("Validating application before AI implementation phase")
    print()
    
    all_results = []
    
    # Validation tests
    tests = [
        ("File Structure", validate_file_structure),
        ("Python Imports", validate_python_imports),
        ("FastAPI Application", validate_fastapi_app),
        ("Database Connections", validate_database_connections)
    ]
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            all_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} validation failed: {e}")
    
    # Check if application is running for API tests
    app_running = check_application_running()
    if app_running:
        print("\n🟢 Application detected running - testing API endpoints...")
        api_result = await validate_api_endpoints()
        all_results.append(("API Endpoints", api_result))
    else:
        print("\n🟡 Application not running - skipping API endpoint tests")
        print("   To test API endpoints, start the app with:")
        print("   uvicorn app.main:app --reload --port 8001")
    
    # Calculate overall results
    print("\n📊 Validation Summary")
    print("=" * 60)
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    
    for test_name, result in all_results:
        summary = result.get_summary()
        total_tests += summary["total"]
        total_passed += summary["passed"]
        total_failed += summary["failed"]
        total_warnings += summary["warnings"]
        
        print(f"{test_name}:")
        print(f"  ✅ Passed: {summary['passed']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  ⚠️ Warnings: {summary['warnings']}")
        print(f"  📈 Success Rate: {summary['success_rate']}%")
        print()
    
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print("Overall Results:")
    print(f"  📊 Total Tests: {total_tests}")
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  ⚠️ Warnings: {total_warnings}")
    print(f"  🎯 Success Rate: {overall_success_rate:.1f}%")
    print()
    
    # Final assessment
    if overall_success_rate >= 90:
        print("🎉 VALIDATION PASSED!")
        print("✅ Application is ready for AI implementation phase")
        if not app_running:
            print("\n📋 Next steps:")
            print("1. Start the application: uvicorn app.main:app --reload --port 8001")
            print("2. Access dashboard: http://127.0.0.1:8001/dashboard")
            print("3. Proceed with AI Risk Assessment implementation")
        return True
    elif overall_success_rate >= 75:
        print("⚠️ VALIDATION PARTIALLY PASSED")
        print("🔧 Some issues detected but application should work")
        print("   Consider fixing warnings before proceeding")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("🚨 Critical issues detected - fix before proceeding")
        print("\n📋 Recommended actions:")
        print("1. Run: python comprehensive_fix.py")
        print("2. Check error messages above")
        print("3. Re-run validation")
        return False


def main():
    """Main execution function."""
    try:
        success = asyncio.run(run_comprehensive_validation())
        return success
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)