"""
Test AI Components - Phase 4C
File: tests/test_phase_4c_ai_components.py

Comprehensive test suite for Phase 4C AI components including
honeypot detection and contract analysis.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logger import setup_logger
from app.core.ai.honeypot_detector import HoneypotDetector, HoneypotRisk
from app.core.ai.contract_analyzer import ContractAnalyzer, ContractType

logger = setup_logger(__name__)


class TestPhase4CAIComponents:
    """Test suite for Phase 4C AI components."""
    
    def __init__(self):
        """Initialize test suite."""
        self.honeypot_detector = None
        self.contract_analyzer = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def setup(self):
        """Setup test components."""
        try:
            logger.info("🚀 Setting up AI test components...")
            
            # Initialize components
            self.honeypot_detector = HoneypotDetector()
            await self.honeypot_detector.initialize()
            
            self.contract_analyzer = ContractAnalyzer()
            
            logger.info("✅ AI components initialized for testing")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    async def test_honeypot_detection(self):
        """Test honeypot detection functionality."""
        test_name = "Honeypot Detection"
        try:
            logger.info(f"🧪 Testing {test_name}...")
            
            # Test with mock contract
            test_address = "0x1234567890123456789012345678901234567890"
            test_network = "ethereum"
            
            # Quick check
            result = await self.honeypot_detector.analyze_contract(
                test_address,
                test_network,
                quick_check=True
            )
            
            # Verify result structure
            assert hasattr(result, 'is_honeypot')
            assert hasattr(result, 'risk_level')
            assert hasattr(result, 'risk_score')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'indicators')
            assert hasattr(result, 'warnings')
            assert hasattr(result, 'safe_indicators')
            
            # Verify risk level is valid
            assert result.risk_level in HoneypotRisk
            
            # Verify risk score range
            assert 0.0 <= result.risk_score <= 10.0
            
            # Verify confidence range
            assert 0.0 <= result.confidence <= 1.0
            
            logger.info(
                f"✅ {test_name} passed - "
                f"Risk: {result.risk_level.value}, "
                f"Score: {result.risk_score:.2f}"
            )
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return False
    
    async def test_comprehensive_honeypot_analysis(self):
        """Test comprehensive honeypot analysis."""
        test_name = "Comprehensive Honeypot Analysis"
        try:
            logger.info(f"🧪 Testing {test_name}...")
            
            # Test with suspicious contract patterns
            test_address = "0xBAD0000000000000000000000000000000000BAD"
            test_network = "bsc"
            mock_contract_code = """
                function blacklist(address user) public onlyOwner {
                    blacklisted[user] = true;
                }
                function mint(uint256 amount) public onlyOwner {
                    _mint(msg.sender, amount);
                }
                function pause() public onlyOwner {
                    paused = true;
                }
            """
            
            # Comprehensive analysis
            result = await self.honeypot_detector.analyze_contract(
                test_address,
                test_network,
                contract_code=mock_contract_code,
                quick_check=False
            )
            
            # Should detect multiple risk indicators
            assert len(result.indicators) > 0
            assert result.has_blacklist == True
            assert result.has_mint_function == True
            assert result.is_pausable == True
            
            # Should have high risk score
            assert result.risk_score >= 5.0
            
            # Get risk summary
            summary = self.honeypot_detector.get_risk_summary(result)
            assert summary is not None
            assert len(summary) > 0
            
            logger.info(
                f"✅ {test_name} passed - "
                f"Found {len(result.indicators)} risk indicators"
            )
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return False
    
    async def test_contract_analysis(self):
        """Test contract analysis functionality."""
        test_name = "Contract Analysis"
        try:
            logger.info(f"🧪 Testing {test_name}...")
            
            # Test contract analysis
            test_address = "0x5678901234567890123456789012345678901234"
            test_network = "ethereum"
            mock_abi = """[
                {"name": "transfer", "type": "function"},
                {"name": "approve", "type": "function"},
                {"name": "balanceOf", "type": "function"}
            ]"""
            
            result = await self.contract_analyzer.analyze_contract(
                test_address,
                test_network,
                contract_abi=mock_abi,
                deep_analysis=False
            )
            
            # Verify result structure
            assert hasattr(result, 'contract_features')
            assert hasattr(result, 'security_audit')
            assert hasattr(result, 'code_quality')
            assert hasattr(result, 'overall_score')
            assert hasattr(result, 'recommendations')
            
            # Verify contract type detection
            assert result.contract_features.contract_type == ContractType.ERC20
            
            # Verify score ranges
            assert 0.0 <= result.overall_score <= 10.0
            assert 0.0 <= result.security_audit.risk_score <= 10.0
            
            logger.info(
                f"✅ {test_name} passed - "
                f"Type: {result.contract_features.contract_type.value}, "
                f"Score: {result.overall_score:.2f}"
            )
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return False
    
    async def test_security_audit(self):
        """Test security audit functionality."""
        test_name = "Security Audit"
        try:
            logger.info(f"🧪 Testing {test_name}...")
            
            # Test with risky contract
            test_address = "0xRISK000000000000000000000000000000000000"
            test_network = "ethereum"
            risky_code = """
                function transferFrom(address from, address to, uint256 amount) {
                    require(!blacklisted[from] && !blacklisted[to]);
                    if (isPaused) revert();
                    uint256 fee = amount * sellTax / 100;
                    _transfer(from, to, amount - fee);
                    _transfer(from, taxWallet, fee);
                }
                function setTax(uint256 newTax) public onlyOwner {
                    sellTax = newTax;  // Can set to 100%
                }
            """
            
            result = await self.contract_analyzer.analyze_contract(
                test_address,
                test_network,
                contract_code=risky_code,
                deep_analysis=True
            )
            
            # Should identify security issues
            assert len(result.security_audit.warnings) > 0
            assert result.security_audit.risk_score > 0
            
            # Should have recommendations
            assert len(result.recommendations) > 0
            
            # Detailed report should be generated
            assert result.detailed_report is not None
            assert "summary" in result.detailed_report
            assert "risks" in result.detailed_report
            
            logger.info(
                f"✅ {test_name} passed - "
                f"Security Level: {result.security_audit.security_level.value}, "
                f"Warnings: {len(result.security_audit.warnings)}"
            )
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return False
    
    async def test_transaction_simulation(self):
        """Test transaction simulation for honeypot detection."""
        test_name = "Transaction Simulation"
        try:
            logger.info(f"🧪 Testing {test_name}...")
            
            # Simulate transaction
            test_address = "0xTEST00000000000000000000000000000000TEST"
            test_network = "ethereum"
            test_amount = 0.1
            
            result = await self.honeypot_detector.simulate_transaction(
                test_address,
                test_network,
                test_amount
            )
            
            # Verify simulation result
            assert "can_buy" in result
            assert "can_sell" in result
            assert "is_honeypot" in result
            assert "confidence" in result
            
            # Verify confidence range
            assert 0.0 <= result["confidence"] <= 1.0
            
            logger.info(
                f"✅ {test_name} passed - "
                f"Can Buy: {result['can_buy']}, "
                f"Can Sell: {result['can_sell']}, "
                f"Honeypot: {result['is_honeypot']}"
            )
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return False
    
    async def test_caching_mechanism(self):
        """Test caching mechanism for AI components."""
        test_name = "AI Caching Mechanism"
        try:
            logger.info(f"🧪 Testing {test_name}...")
            
            test_address = "0xCACHE0000000000000000000000000000000000"
            test_network = "ethereum"
            
            # First analysis (should cache)
            result1 = await self.honeypot_detector.analyze_contract(
                test_address, test_network, quick_check=True
            )
            
            # Second analysis (should use cache)
            result2 = await self.honeypot_detector.analyze_contract(
                test_address, test_network, quick_check=True
            )
            
            # Results should be identical
            assert result1.risk_score == result2.risk_score
            assert result1.risk_level == result2.risk_level
            
            # Contract analyzer cache test
            analysis1 = await self.contract_analyzer.analyze_contract(
                test_address, test_network, deep_analysis=False
            )
            
            analysis2 = await self.contract_analyzer.analyze_contract(
                test_address, test_network, deep_analysis=False
            )
            
            # Should use cached result
            assert analysis1.overall_score == analysis2.overall_score
            
            logger.info(f"✅ {test_name} passed - Caching working correctly")
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all AI component tests."""
        logger.info("=" * 60)
        logger.info("🤖 PHASE 4C AI COMPONENTS TEST SUITE")
        logger.info("=" * 60)
        
        # Setup
        if not await self.setup():
            logger.error("❌ Failed to setup test environment")
            return False
        
        # Run tests
        tests = [
            self.test_honeypot_detection,
            self.test_comprehensive_honeypot_analysis,
            self.test_contract_analysis,
            self.test_security_audit,
            self.test_transaction_simulation,
            self.test_caching_mechanism
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                logger.error(f"❌ Test crashed: {e}")
                self.test_results["failed"] += 1
        
        # Print results
        logger.info("=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Passed: {self.test_results['passed']}")
        logger.info(f"❌ Failed: {self.test_results['failed']}")
        logger.info(f"📊 Total: {self.test_results['passed'] + self.test_results['failed']}")
        logger.info(
            f"🎯 Success Rate: "
            f"{(self.test_results['passed'] / max(1, self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%"
        )
        
        if self.test_results["errors"]:
            logger.info("\n❌ ERRORS:")
            for error in self.test_results["errors"]:
                logger.error(f"  - {error}")
        
        logger.info("=" * 60)
        
        return self.test_results["failed"] == 0


async def main():
    """Main test runner."""
    tester = TestPhase4CAIComponents()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("✅ All Phase 4C AI component tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())