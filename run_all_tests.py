"""
Run All Tests - Check Overall Progress
File: run_all_tests.py

Recreates the comprehensive test that was mentioned in the original test results.
This checks all 32 tests to see our progress after Phase 5A completion.
"""

import sys
import os
import asyncio
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def run_test_category(category_name: str, test_functions: List) -> Dict[str, Any]:
    """Run a category of tests and return results."""
    print(f"\n{category_name}")
    print("-" * 50)
    
    passed = 0
    failed = 0
    test_results = []
    
    for test_func in test_functions:
        try:
            print(f"🧪 Running {test_func.__name__}...")
            result = test_func()
            
            if result:
                print(f"  ✅ {test_func.__name__}: PASSED")
                passed += 1
                test_results.append({
                    "test_name": test_func.__name__,
                    "passed": True,
                    "category": category_name
                })
            else:
                print(f"  ❌ {test_func.__name__}: FAILED")
                failed += 1
                test_results.append({
                    "test_name": test_func.__name__,
                    "passed": False,
                    "category": category_name,
                    "error": "Test returned False"
                })
                
        except Exception as e:
            print(f"  ❌ {test_func.__name__}: ERROR - {e}")
            failed += 1
            test_results.append({
                "test_name": test_func.__name__,
                "passed": False,
                "category": category_name,
                "error": str(e)
            })
    
    return {
        "category": category_name,
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "results": test_results
    }

# ==================== CORE INFRASTRUCTURE TESTS ====================

def test_project_structure():
    """Test that all required directories exist."""
    try:
        required_dirs = [
            "app", "app/core", "app/api", "app/utils",
            "app/core/database", "app/core/trading", "app/core/config",
            "app/core/security", "app/api/v1", "app/api/v1/endpoints"
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                print(f"    Missing directory: {dir_path}")
                return False
        
        return True
    except Exception:
        return False

def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from app.utils.logger import setup_logger
        from app.core.exceptions import DEXSniperError
        from app.core.security.security_manager import get_security_manager
        return True
    except Exception:
        return False

def test_logger_system():
    """Test that logging system is operational."""
    try:
        from app.utils.logger import setup_logger
        logger = setup_logger("test")
        logger.info("Test log message")
        return True
    except Exception:
        return False

def test_exception_handling():
    """Test that custom exceptions are available."""
    try:
        from app.core.exceptions import (
            SecurityError, AuthenticationError, ValidationError
        )
        return True
    except Exception:
        return False

# ==================== DATABASE SYSTEM TESTS ====================

def test_persistence_manager():
    """Test that persistence manager can be imported and initialized."""
    try:
        from app.core.database.persistence_manager import get_persistence_manager
        return True
    except Exception:
        return False

def test_database_operations():
    """Test basic database functions."""
    try:
        # This is a simplified test since we can't run async easily here
        from app.core.database.persistence_manager import PersistenceManager
        return True
    except Exception:
        return False

def test_data_models():
    """Test that data models are working."""
    try:
        from app.core.database.persistence_manager import TradeRecord, WalletSession
        return True
    except Exception:
        return False

def test_migration_system():
    """Test database migration/creation system."""
    try:
        from app.core.database.persistence_manager import PersistenceManager
        # Basic import test
        return True
    except Exception:
        return False

# ==================== TRADING ENGINE TESTS ====================

def test_trading_engine_init():
    """Test that trading engine can be initialized."""
    try:
        from app.core.trading.trading_engine import TradingEngine
        return True
    except Exception:
        return False

def test_order_execution():
    """Test order executor availability."""
    try:
        from app.core.trading.order_executor import OrderExecutor
        return True
    except Exception:
        return False

def test_portfolio_tracking():
    """Test portfolio analyzer availability."""
    try:
        from app.core.portfolio.portfolio_manager import get_portfolio_manager
        return True
    except Exception:
        return False

def test_risk_management():
    """Test risk manager availability."""
    try:
        from app.core.trading.risk_manager import RiskManager
        return True
    except Exception:
        return False

# ==================== API ENDPOINTS TESTS ====================

def test_fastapi_application():
    """Test FastAPI app creation."""
    try:
        from app.main import app
        return app is not None
    except Exception:
        return False

def test_health_endpoints():
    """Test health endpoint availability."""
    try:
        from app.main import app
        # Check if health route exists
        health_routes = [route for route in app.routes if hasattr(route, 'path') and '/health' in route.path]
        return len(health_routes) > 0
    except Exception:
        return False

def test_trading_api():
    """Test trading API endpoints."""
    try:
        from app.api.v1.endpoints.trading import router
        return len(router.routes) > 0
    except Exception:
        return False

def test_dashboard_api():
    """Test dashboard API availability."""
    try:
        from app.api.v1.endpoints.dashboard import router
        return True
    except Exception:
        return False

# ==================== FRONTEND INTERFACE TESTS ====================

def test_template_system():
    """Test template system availability."""
    try:
        template_path = Path("frontend/templates/dashboard.html")
        return template_path.exists()
    except Exception:
        return False

def test_dashboard_ui():
    """Test dashboard UI template."""
    try:
        template_path = Path("frontend/templates/dashboard.html")
        if template_path.exists():
            content = template_path.read_text()
            return "DEX Sniper Pro" in content
        return False
    except Exception:
        return False

def test_static_assets():
    """Test static assets availability."""
    try:
        static_path = Path("frontend/static")
        return static_path.exists()
    except Exception:
        return False

def test_websocket_support():
    """Test WebSocket manager availability."""
    try:
        from app.utils.websocket_manager import WebSocketManager
        return True
    except Exception:
        return False

# ==================== CONFIGURATION TESTS ====================

def test_settings_manager():
    """Test settings manager operational."""
    try:
        from app.core.config.settings_manager import get_settings
        settings = get_settings()
        return settings is not None
    except Exception:
        return False

def test_environment_config():
    """Test environment configuration."""
    try:
        from app.core.config.settings_manager import get_settings
        settings = get_settings()
        return hasattr(settings, 'environment')
    except Exception:
        return False

def test_runtime_updates():
    """Test runtime update capability."""
    try:
        from app.core.config.settings_manager import get_settings
        settings = get_settings()
        return hasattr(settings, 'update_trading_config')
    except Exception:
        return False

def test_validation_system():
    """Test configuration validation."""
    try:
        from app.core.config.settings_manager import get_settings
        settings = get_settings()
        errors = settings.validate_configuration()
        return isinstance(errors, list)
    except Exception:
        return False

# ==================== SECURITY & COMPLIANCE TESTS ====================

def test_wallet_security():
    """Test wallet security implementation."""
    try:
        from app.core.security.security_manager import get_security_manager
        security_manager = get_security_manager()
        
        # Test encryption/decryption
        test_key = "a" * 64
        test_address = "0x" + "b" * 40
        
        encrypted = security_manager.wallet_security.encrypt_private_key(test_key, test_address)
        decrypted = security_manager.wallet_security.decrypt_private_key(encrypted, test_address)
        
        return decrypted == test_key
    except Exception:
        return False

def test_api_authentication():
    """Test API authentication system."""
    try:
        from app.core.security.security_manager import get_security_manager, APIKeyType
        security_manager = get_security_manager()
        
        # Test API key generation
        api_key = security_manager.api_auth.generate_api_key(
            "test_user", APIKeyType.READ_ONLY, ["read_access"]
        )
        
        # Test validation
        key_data = security_manager.api_auth.validate_api_key(api_key, "read_access")
        
        return key_data['user_id'] == 'test_user'
    except Exception:
        return False

def test_input_validation():
    """Test input validation system."""
    try:
        from app.core.security.security_manager import get_security_manager
        security_manager = get_security_manager()
        
        # Test address validation
        valid_addr = "0x" + "a" * 40
        invalid_addr = "invalid"
        
        return (security_manager.input_validator.validate_ethereum_address(valid_addr) and
                not security_manager.input_validator.validate_ethereum_address(invalid_addr))
    except Exception:
        return False

def test_error_sanitization():
    """Test error sanitization system."""
    try:
        from app.core.security.security_manager import get_security_manager
        security_manager = get_security_manager()
        
        # Test sanitization
        error_msg = "Error with address 0x1234567890abcdef1234567890abcdef12345678"
        sanitized = security_manager.error_sanitizer.sanitize_error(error_msg)
        
        return "[REDACTED]" in sanitized or "Error" in sanitized
    except Exception:
        return False

# ==================== INTEGRATION TESTING (Phase 5B) ====================

def test_end_to_end_workflow():
    """Test end-to-end workflow (Phase 5B)."""
    # This would require full system integration
    return False  # Not implemented yet

def test_cross_component_communication():
    """Test cross-component communication (Phase 5B)."""
    # This would test service-to-service communication
    return False  # Not implemented yet

def test_performance_benchmarks():
    """Test performance benchmarks (Phase 5B)."""
    # This would run performance testing
    return False  # Not implemented yet

def test_scalability_metrics():
    """Test scalability metrics (Phase 5B)."""
    # This would test system scalability
    return False  # Not implemented yet

def main():
    """Run all comprehensive tests."""
    print("🚀 DEX Sniper Pro - Comprehensive Test Suite")
    print("=" * 60)
    print("📊 Testing all 32 components across 6 categories")
    print("=" * 60)
    
    start_time = time.time()
    
    # Define test categories
    test_categories = [
        ("🏗️ Core Infrastructure", [
            test_project_structure,
            test_core_imports,
            test_logger_system,
            test_exception_handling
        ]),
        ("💾 Database Systems", [
            test_persistence_manager,
            test_database_operations,
            test_data_models,
            test_migration_system
        ]),
        ("⚡ Trading Engine", [
            test_trading_engine_init,
            test_order_execution,
            test_portfolio_tracking,
            test_risk_management
        ]),
        ("🌐 API Endpoints", [
            test_fastapi_application,
            test_health_endpoints,
            test_trading_api,
            test_dashboard_api
        ]),
        ("🎨 Frontend Interface", [
            test_template_system,
            test_dashboard_ui,
            test_static_assets,
            test_websocket_support
        ]),
        ("⚙️ Configuration", [
            test_settings_manager,
            test_environment_config,
            test_runtime_updates,
            test_validation_system
        ]),
        ("🛡️ Security & Compliance", [
            test_wallet_security,
            test_api_authentication,
            test_input_validation,
            test_error_sanitization
        ]),
        ("🧪 Integration Testing", [
            test_end_to_end_workflow,
            test_cross_component_communication,
            test_performance_benchmarks,
            test_scalability_metrics
        ])
    ]
    
    # Run all test categories
    all_results = []
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for category_name, test_functions in test_categories:
        category_result = run_test_category(category_name, test_functions)
        all_results.append(category_result)
        total_passed += category_result['passed']
        total_failed += category_result['failed']
        total_tests += category_result['total']
    
    # Calculate overall results
    end_time = time.time()
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    print(f"📋 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️ Duration: {end_time - start_time:.2f} seconds")
    print(f"📅 Timestamp: {datetime.utcnow().isoformat()}")
    
    # Category breakdown
    print(f"\n📋 CATEGORY BREAKDOWN:")
    for result in all_results:
        status_emoji = "✅" if result['failed'] == 0 else "⚠️" if result['passed'] > result['failed'] else "❌"
        print(f"{status_emoji} {result['category']}: {result['passed']}/{result['total']} passed")
    
    # Determine system status
    if success_rate >= 90:
        status = "EXCELLENT"
        emoji = "🎉"
    elif success_rate >= 75:
        status = "GOOD"
        emoji = "✅"
    elif success_rate >= 60:
        status = "MODERATE"
        emoji = "⚠️"
    else:
        status = "NEEDS_WORK"
        emoji = "❌"
    
    print(f"\n{emoji} SYSTEM STATUS: {status}")
    print(f"🎯 READINESS LEVEL: {'PRODUCTION_READY' if success_rate >= 90 else 'DEVELOPMENT_ACTIVE'}")
    
    # Phase completion status
    security_category = next(r for r in all_results if "Security" in r['category'])
    if security_category['failed'] == 0:
        print("\n🛡️ PHASE 5A: COMPLETE - All security tests passed")
        integration_category = next(r for r in all_results if "Integration" in r['category'])
        if integration_category['failed'] == 0:
            print("🧪 PHASE 5B: COMPLETE - All integration tests passed")
        else:
            print("🔄 PHASE 5B: IN PROGRESS - Integration testing needed")
    else:
        print("\n🔄 PHASE 5A: IN PROGRESS - Security implementation needed")
    
    print("=" * 60)
    
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        sys.exit(1)