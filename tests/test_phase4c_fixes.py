"""
Phase 4C Fixes Validation Test
File: tests/test_phase4c_fixes.py

Comprehensive test to validate all Phase 4C fixes including:
- AI Risk Assessor async/await fixes
- LiveDashboardService WebSocket integration
- Multi-chain manager EVM error handling
- Exception imports resolution
"""

import asyncio
import sys
import os
import traceback
from typing import Dict, List, Any
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules for testing
try:
    from app.utils.logger import setup_logger
    logger = setup_logger(__name__)
except ImportError as e:
    print(f"❌ Logger import failed: {e}")
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class Phase4CFixesValidator:
    """Comprehensive validator for Phase 4C fixes."""
    
    def __init__(self):
        """Initialize the validator."""
        self.test_results: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 4C fix validation tests."""
        logger.info("🚀 Starting Phase 4C Fixes Validation")
        logger.info("=" * 80)
        
        # Test categories
        test_categories = [
            ("Exception Imports", self.test_exception_imports),
            ("AI Risk Assessor", self.test_ai_risk_assessor),
            ("WebSocket Integration", self.test_websocket_integration),
            ("Multi-Chain Manager", self.test_multi_chain_manager),
            ("Live Dashboard Service", self.test_live_dashboard_service),
            ("Integration Tests", self.test_integration_scenarios)
        ]
        
        for category_name, test_method in test_categories:
            logger.info(f"\n🔍 Testing {category_name}")
            logger.info("-" * 60)
            
            try:
                await test_method()
            except Exception as e:
                logger.error(f"❌ {category_name} test category failed: {e}")
                self._record_result(f"{category_name} Category", False, str(e))
        
        return self._generate_summary()
    
    async def test_exception_imports(self):
        """Test that all required exceptions can be imported."""
        logger.info("🧪 Testing exception imports...")
        
        # Test core exceptions import
        try:
            from app.core.exceptions import (
                InsufficientLiquidityError, 
                DEXError, 
                TradingError,
                NetworkError,
                WalletError,
                AIAnalysisError,
                HoneypotDetectionError,
                SentimentAnalysisError
            )
            logger.info("✅ Core exceptions imported successfully")
            self._record_result("Core Exceptions Import", True)
        except ImportError as e:
            logger.error(f"❌ Core exceptions import failed: {e}")
            self._record_result("Core Exceptions Import", False, str(e))
        
        # Test specific problematic exception
        try:
            from app.core.exceptions import InsufficientLiquidityError
            logger.info("✅ InsufficientLiquidityError imported successfully")
            self._record_result("InsufficientLiquidityError Import", True)
        except ImportError as e:
            logger.error(f"❌ InsufficientLiquidityError import failed: {e}")
            self._record_result("InsufficientLiquidityError Import", False, str(e))
        
        # Test exception instantiation
        try:
            from app.core.exceptions import InsufficientLiquidityError, DEXError
            
            # Test creating exceptions
            dex_error = DEXError("Test DEX error", error_code="TEST_001")
            liquidity_error = InsufficientLiquidityError("Test liquidity error")
            
            # Test methods
            error_dict = dex_error.to_dict()
            assert "error_type" in error_dict
            assert "message" in error_dict
            
            logger.info("✅ Exception instantiation and methods work")
            self._record_result("Exception Instantiation", True)
        except Exception as e:
            logger.error(f"❌ Exception instantiation failed: {e}")
            self._record_result("Exception Instantiation", False, str(e))
    
    async def test_ai_risk_assessor(self):
        """Test AI Risk Assessor fixes."""
        logger.info("🧪 Testing AI Risk Assessor...")
        
        # Test AI Risk Assessor import
        try:
            from app.core.ai.risk_assessor import AIRiskAssessor, risk_assessor
            logger.info("✅ AI Risk Assessor imported successfully")
            self._record_result("AI Risk Assessor Import", True)
        except ImportError as e:
            logger.error(f"❌ AI Risk Assessor import failed: {e}")
            self._record_result("AI Risk Assessor Import", False, str(e))
            return
        
        # Test initialization
        try:
            from app.core.ai.risk_assessor import AIRiskAssessor
            assessor = AIRiskAssessor()
            assert assessor.model_version == "2.1.0"
            logger.info("✅ AI Risk Assessor initialization works")
            self._record_result("AI Risk Assessor Initialization", True)
        except Exception as e:
            logger.error(f"❌ AI Risk Assessor initialization failed: {e}")
            self._record_result("AI Risk Assessor Initialization", False, str(e))
        
        # Test async methods
        try:
            from app.core.ai.risk_assessor import AIRiskAssessor
            from app.core.blockchain.multi_chain_manager import MockChain
            
            assessor = AIRiskAssessor()
            mock_chain = MockChain("ethereum", {"type": "evm"})
            
            # Test honeypot detection
            honeypot_result = await assessor.detect_honeypot(
                "0x1234567890abcdef1234567890abcdef12345678",
                "ethereum"
            )
            assert honeypot_result is not None
            assert hasattr(honeypot_result, 'risk_level')
            logger.info("✅ Honeypot detection async method works")
            
            # Test sentiment analysis
            sentiment_result = await assessor.analyze_market_sentiment(
                "0x1234567890abcdef1234567890abcdef12345678",
                "ethereum"
            )
            assert sentiment_result is not None
            assert hasattr(sentiment_result, 'sentiment_score')
            logger.info("✅ Sentiment analysis async method works")
            
            self._record_result("AI Risk Assessor Async Methods", True)
        except Exception as e:
            logger.error(f"❌ AI Risk Assessor async methods failed: {e}")
            self._record_result("AI Risk Assessor Async Methods", False, str(e))
    
    async def test_websocket_integration(self):
        """Test WebSocket integration fixes."""
        logger.info("🧪 Testing WebSocket integration...")
        
        # Test WebSocket manager import
        try:
            from app.core.websocket.websocket_manager import WebSocketManager, websocket_manager
            logger.info("✅ WebSocket manager imported successfully")
            self._record_result("WebSocket Manager Import", True)
        except ImportError as e:
            logger.error(f"❌ WebSocket manager import failed: {e}")
            self._record_result("WebSocket Manager Import", False, str(e))
            return
        
        # Test WebSocket manager initialization
        try:
            from app.core.websocket.websocket_manager import WebSocketManager
            manager = WebSocketManager()
            assert hasattr(manager, 'connections')
            assert hasattr(manager, 'MESSAGE_TYPES')
            logger.info("✅ WebSocket manager initialization works")
            self._record_result("WebSocket Manager Initialization", True)
        except Exception as e:
            logger.error(f"❌ WebSocket manager initialization failed: {e}")
            self._record_result("WebSocket Manager Initialization", False, str(e))
    
    async def test_multi_chain_manager(self):
        """Test Multi-Chain Manager fixes."""
        logger.info("🧪 Testing Multi-Chain Manager...")
        
        # Test Multi-Chain Manager import
        try:
            from app.core.blockchain.multi_chain_manager import MultiChainManager, multi_chain_manager
            logger.info("✅ Multi-Chain Manager imported successfully")
            self._record_result("Multi-Chain Manager Import", True)
        except ImportError as e:
            logger.error(f"❌ Multi-Chain Manager import failed: {e}")
            self._record_result("Multi-Chain Manager Import", False, str(e))
            return
        
        # Test initialization
        try:
            from app.core.blockchain.multi_chain_manager import MultiChainManager
            manager = MultiChainManager()
            assert hasattr(manager, 'chains')
            assert hasattr(manager, 'enabled_networks')
            assert hasattr(manager, 'chain_health')
            logger.info("✅ Multi-Chain Manager initialization works")
            self._record_result("Multi-Chain Manager Initialization", True)
        except Exception as e:
            logger.error(f"❌ Multi-Chain Manager initialization failed: {e}")
            self._record_result("Multi-Chain Manager Initialization", False, str(e))
        
        # Test EVM chain handling
        try:
            from app.core.blockchain.multi_chain_manager import MultiChainManager
            manager = MultiChainManager()
            
            # Test initialization with networks
            await manager.initialize(['ethereum'])
            assert manager.is_initialized()
            logger.info("✅ Multi-Chain Manager EVM handling works")
            self._record_result("Multi-Chain Manager EVM Handling", True)
        except Exception as e:
            logger.error(f"❌ Multi-Chain Manager EVM handling failed: {e}")
            self._record_result("Multi-Chain Manager EVM Handling", False, str(e))
    
    async def test_live_dashboard_service(self):
        """Test Live Dashboard Service fixes."""
        logger.info("🧪 Testing Live Dashboard Service...")
        
        # Test Live Dashboard Service import
        try:
            from app.core.integration.live_dashboard_service import LiveDashboardService, live_dashboard_service
            logger.info("✅ Live Dashboard Service imported successfully")
            self._record_result("Live Dashboard Service Import", True)
        except ImportError as e:
            logger.error(f"❌ Live Dashboard Service import failed: {e}")
            self._record_result("Live Dashboard Service Import", False, str(e))
            return
        
        # Test initialization and websocket_service attribute
        try:
            from app.core.integration.live_dashboard_service import LiveDashboardService
            service = LiveDashboardService()
            
            # Check for the fixed websocket_service attribute
            assert hasattr(service, 'websocket_service')
            assert hasattr(service, 'websocket_manager')
            assert service.websocket_service is not None
            logger.info("✅ Live Dashboard Service websocket_service attribute exists")
            self._record_result("Live Dashboard Service WebSocket Attribute", True)
        except Exception as e:
            logger.error(f"❌ Live Dashboard Service websocket_service check failed: {e}")
            self._record_result("Live Dashboard Service WebSocket Attribute", False, str(e))
        
        # Test service methods
        try:
            from app.core.integration.live_dashboard_service import LiveDashboardService
            service = LiveDashboardService()
            
            # Test async methods
            await service.start()
            assert service.is_running
            
            # Test broadcast methods
            await service.broadcast_portfolio_update({"test": "data"})
            await service.broadcast_trading_status({"status": "running"})
            
            await service.stop()
            assert not service.is_running
            
            logger.info("✅ Live Dashboard Service methods work")
            self._record_result("Live Dashboard Service Methods", True)
        except Exception as e:
            logger.error(f"❌ Live Dashboard Service methods failed: {e}")
            self._record_result("Live Dashboard Service Methods", False, str(e))
    
    async def test_integration_scenarios(self):
        """Test integration scenarios that were failing."""
        logger.info("🧪 Testing integration scenarios...")
        
        # Test advanced trading strategies import (was failing due to InsufficientLiquidityError)
        try:
            from app.core.exceptions import InsufficientLiquidityError
            # This should not fail now
            error = InsufficientLiquidityError("Test error")
            assert str(error) == "Test error"
            logger.info("✅ Advanced trading strategies exception handling works")
            self._record_result("Advanced Trading Strategies Import", True)
        except Exception as e:
            logger.error(f"❌ Advanced trading strategies import failed: {e}")
            self._record_result("Advanced Trading Strategies Import", False, str(e))
        
        # Test cross-component integration
        try:
            from app.core.ai.risk_assessor import risk_assessor
            from app.core.integration.live_dashboard_service import live_dashboard_service
            from app.core.blockchain.multi_chain_manager import multi_chain_manager
            
            # Test that components can work together
            assert risk_assessor is not None
            assert live_dashboard_service is not None
            assert multi_chain_manager is not None
            
            logger.info("✅ Cross-component integration works")
            self._record_result("Cross-Component Integration", True)
        except Exception as e:
            logger.error(f"❌ Cross-component integration failed: {e}")
            self._record_result("Cross-Component Integration", False, str(e))
    
    def _record_result(self, test_name: str, success: bool, error: str = None):
        """Record test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = len(self.test_results)
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": success_rate,
            "all_tests_passed": self.failed == 0,
            "test_results": self.test_results,
            "summary": {
                "status": "PASSED" if self.failed == 0 else "FAILED",
                "message": f"{self.passed}/{total_tests} tests passed ({success_rate:.1f}%)"
            }
        }


async def main():
    """Main test execution function."""
    print("🚀 DEX Sniper Pro - Phase 4C Fixes Validation")
    print("=" * 80)
    
    validator = Phase4CFixesValidator()
    
    try:
        summary = await validator.run_all_tests()
        
        # Print detailed results
        print("\n" + "=" * 80)
        print("📊 PHASE 4C FIXES VALIDATION RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        # Print failed tests if any
        if summary['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            print("-" * 40)
            for result in summary['test_results']:
                if not result['success']:
                    print(f"  • {result['test_name']}: {result['error']}")
        
        # Print summary
        print(f"\n🎯 OVERALL STATUS: {summary['summary']['status']}")
        print(f"📈 {summary['summary']['message']}")
        
        if summary['all_tests_passed']:
            print("\n🎉 ALL PHASE 4C FIXES VALIDATED SUCCESSFULLY!")
            print("✅ Ready to proceed with Phase 4C integration testing")
        else:
            print(f"\n⚠️ {summary['failed']} tests failed - review fixes before proceeding")
        
        return summary['all_tests_passed']
        
    except Exception as e:
        print(f"\n❌ Validation failed with exception: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)