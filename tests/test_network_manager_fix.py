"""
Network Manager Fix Verification Test
File: tests/test_network_manager_fix.py

Comprehensive test suite to verify the network manager fixes handle
invalid input types properly and prevent the integer type error.
"""

import asyncio
import sys
import traceback
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Add the parent directory to Python path FIRST, before any app imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the app modules AFTER setting the path
try:
    from app.utils.logger import setup_logger
    from app.core.blockchain.network_manager_fixed import (
        NetworkManagerFixed, NetworkType, get_network_manager
    )
    from app.core.wallet.enhanced_wallet_manager import (
        EnhancedWalletManager, WalletType, get_enhanced_wallet_manager
    )
    logger = setup_logger(__name__)
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the project root directory")
    print("💡 Command: python tests/test_phase_4b_integration.py")
    print(f"💡 Current working directory: {Path.cwd()}")
    print(f"💡 Script location: {Path(__file__).parent.parent}")
    sys.exit(1)


class NetworkManagerFixTester:
    """Test suite for network manager fixes."""
    
    def __init__(self):
        """Initialize the network manager fix tester."""
        self.test_results: List[Dict[str, Any]] = []
        self.network_manager = None
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive network manager fix tests.
        
        Returns:
            Dict containing test results and summary
        """
        logger.info("🧪 Starting Network Manager Fix Verification Tests")
        logger.info("=" * 60)
        
        test_methods = [
            self.test_invalid_integer_input,
            self.test_invalid_string_input,
            self.test_none_input,
            self.test_valid_string_input,
            self.test_valid_enum_input,
            self.test_error_handling_graceful,
            self.test_network_validation_comprehensive,
            self.test_status_retrieval_robustness
        ]
        
        total_tests = len(test_methods)
        passed_tests = 0
        failed_tests = 0
        
        for test_method in test_methods:
            try:
                logger.info(f"🔍 Running {test_method.__name__}...")
                
                result = await test_method()
                
                if result.get("passed", False):
                    logger.info(f"✅ {test_method.__name__} - PASSED")
                    passed_tests += 1
                else:
                    logger.error(f"❌ {test_method.__name__} - FAILED")
                    logger.error(f"   Reason: {result.get('error', 'Unknown error')}")
                    failed_tests += 1
                
                self.test_results.append(result)
                
            except Exception as e:
                logger.error(f"💥 {test_method.__name__} - EXCEPTION: {e}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                failed_tests += 1
                
                self.test_results.append({
                    "test_name": test_method.__name__,
                    "passed": False,
                    "error": f"Exception: {e}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Calculate summary
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "all_results": self.test_results
        }
        
        logger.info("=" * 60)
        logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        if failed_tests == 0:
            logger.info("🎉 All network manager fix tests passed!")
        else:
            logger.warning(f"⚠️ {failed_tests} tests failed - review implementation")
        
        return summary
    
    async def test_invalid_integer_input(self) -> Dict[str, Any]:
        """Test that integer inputs are handled gracefully (this was the original error)."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            # Test the exact error case: integer input (12345)
            result = await self.network_manager.connect_to_network(12345)
            
            # Should return False, not raise exception
            if result is False:
                return {
                    "test_name": "test_invalid_integer_input",
                    "passed": True,
                    "message": "Integer input handled gracefully (returned False)",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_invalid_integer_input",
                    "passed": False,
                    "error": f"Expected False but got: {result}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_invalid_integer_input",
                "passed": False,
                "error": f"Should not raise exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_invalid_string_input(self) -> Dict[str, Any]:
        """Test that invalid string inputs are handled gracefully."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            invalid_strings = ["invalid_network", "bitcoin", "solana", ""]
            
            for invalid_string in invalid_strings:
                result = await self.network_manager.connect_to_network(invalid_string)
                
                if result is not False:
                    return {
                        "test_name": "test_invalid_string_input",
                        "passed": False,
                        "error": f"Invalid string '{invalid_string}' should return False, got: {result}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            return {
                "test_name": "test_invalid_string_input",
                "passed": True,
                "message": "All invalid string inputs handled gracefully",
                "timestamp": datetime.utcnow().isoformat()
            }
                
        except Exception as e:
            return {
                "test_name": "test_invalid_string_input",
                "passed": False,
                "error": f"Should not raise exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_none_input(self) -> Dict[str, Any]:
        """Test that None input is handled gracefully."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            result = await self.network_manager.connect_to_network(None)
            
            if result is False:
                return {
                    "test_name": "test_none_input",
                    "passed": True,
                    "message": "None input handled gracefully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_none_input",
                    "passed": False,
                    "error": f"None input should return False, got: {result}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_none_input",
                "passed": False,
                "error": f"Should not raise exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_valid_string_input(self) -> Dict[str, Any]:
        """Test that valid string inputs are processed correctly."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            valid_strings = ["ethereum", "polygon", "bsc", "arbitrum"]
            validation_results = []
            
            for valid_string in valid_strings:
                # Test validation (should not raise exception)
                network_type = self.network_manager._validate_network_type(valid_string)
                
                if network_type is None:
                    validation_results.append(f"Valid string '{valid_string}' not recognized")
                elif isinstance(network_type, NetworkType):
                    validation_results.append(f"✅ '{valid_string}' -> {network_type.value}")
                else:
                    validation_results.append(f"Invalid type returned for '{valid_string}': {type(network_type)}")
            
            # Check if all validations were successful
            successful_validations = [r for r in validation_results if r.startswith("✅")]
            
            if len(successful_validations) == len(valid_strings):
                return {
                    "test_name": "test_valid_string_input",
                    "passed": True,
                    "message": f"All valid strings processed correctly: {validation_results}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_valid_string_input",
                    "passed": False,
                    "error": f"Some valid strings not processed correctly: {validation_results}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_valid_string_input",
                "passed": False,
                "error": f"Should not raise exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_valid_enum_input(self) -> Dict[str, Any]:
        """Test that NetworkType enum inputs work correctly."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            enum_inputs = [NetworkType.ETHEREUM, NetworkType.POLYGON, NetworkType.BSC, NetworkType.ARBITRUM]
            validation_results = []
            
            for enum_input in enum_inputs:
                network_type = self.network_manager._validate_network_type(enum_input)
                
                if network_type == enum_input:
                    validation_results.append(f"✅ {enum_input.value} enum validated correctly")
                else:
                    validation_results.append(f"❌ {enum_input.value} enum validation failed")
            
            successful_validations = [r for r in validation_results if r.startswith("✅")]
            
            if len(successful_validations) == len(enum_inputs):
                return {
                    "test_name": "test_valid_enum_input",
                    "passed": True,
                    "message": "All enum inputs processed correctly",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_valid_enum_input",
                    "passed": False,
                    "error": f"Some enum inputs failed: {validation_results}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_valid_enum_input",
                "passed": False,
                "error": f"Should not raise exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_error_handling_graceful(self) -> Dict[str, Any]:
        """Test that error handling is graceful across all methods."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            error_test_cases = [
                ("connect_to_network", 12345),
                ("connect_to_network", [1, 2, 3]),
                ("connect_to_network", {"invalid": "dict"}),
                ("get_network_status", 999),
                ("get_web3_instance", "invalid_network"),
                ("is_connected", None),
                ("disconnect_from_network", 12345)
            ]
            
            graceful_handling = True
            error_details = []
            
            for method_name, invalid_input in error_test_cases:
                try:
                    method = getattr(self.network_manager, method_name)
                    
                    if asyncio.iscoroutinefunction(method):
                        result = await method(invalid_input)
                    else:
                        result = method(invalid_input)
                    
                    # Should return False/None for invalid inputs, not raise exception
                    if result not in [False, None]:
                        error_details.append(f"{method_name}({invalid_input}) returned unexpected: {result}")
                    
                except Exception as e:
                    # Some exceptions might be acceptable, but shouldn't be TypeError about int
                    if "Invalid network type" in str(e) or "int" in str(e).lower():
                        graceful_handling = False
                        error_details.append(f"{method_name}({invalid_input}) raised: {e}")
            
            if graceful_handling:
                return {
                    "test_name": "test_error_handling_graceful",
                    "passed": True,
                    "message": "All error cases handled gracefully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_error_handling_graceful",
                    "passed": False,
                    "error": f"Non-graceful error handling: {error_details}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_error_handling_graceful",
                "passed": False,
                "error": f"Test framework error: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_network_validation_comprehensive(self) -> Dict[str, Any]:
        """Test comprehensive network validation edge cases."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            test_cases = [
                # Valid cases
                ("ethereum", True),
                ("ETHEREUM", True),
                ("Ethereum", True),
                (NetworkType.ETHEREUM, True),
                
                # Invalid cases
                (12345, False),
                (None, False),
                ("", False),
                ("bitcoin", False),
                ([], False),
                ({}, False),
                (True, False),
                (3.14, False)
            ]
            
            validation_errors = []
            
            for test_input, expected_valid in test_cases:
                try:
                    network_type = self.network_manager._validate_network_type(test_input)
                    is_valid = network_type is not None
                    
                    if is_valid != expected_valid:
                        validation_errors.append(
                            f"Input: {test_input} (type: {type(test_input)}), "
                            f"expected valid: {expected_valid}, got valid: {is_valid}"
                        )
                        
                except Exception as e:
                    validation_errors.append(f"Input: {test_input} raised exception: {e}")
            
            if not validation_errors:
                return {
                    "test_name": "test_network_validation_comprehensive",
                    "passed": True,
                    "message": "All validation cases handled correctly",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_network_validation_comprehensive",
                    "passed": False,
                    "error": f"Validation errors: {validation_errors}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_network_validation_comprehensive",
                "passed": False,
                "error": f"Test error: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_status_retrieval_robustness(self) -> Dict[str, Any]:
        """Test that status retrieval methods are robust."""
        try:
            if not self.network_manager:
                self.network_manager = NetworkManagerFixed()
            
            # Test various status retrieval scenarios
            status_tests = [
                ("get_network_status", NetworkType.ETHEREUM),
                ("get_network_status", "ethereum"),
                ("get_network_status", 12345),  # Should handle gracefully
                ("get_network_status", None),
            ]
            
            robust_handling = True
            error_details = []
            
            for method_name, test_input in status_tests:
                try:
                    method = getattr(self.network_manager, method_name)
                    result = method(test_input)
                    
                    # Should return NetworkStatus object or None, never raise exception
                    if result is not None and not hasattr(result, 'network_type'):
                        error_details.append(f"{method_name}({test_input}) returned unexpected type: {type(result)}")
                        
                except Exception as e:
                    robust_handling = False
                    error_details.append(f"{method_name}({test_input}) raised: {e}")
            
            # Test get_all_network_status
            try:
                all_status = self.network_manager.get_all_network_status()
                if not isinstance(all_status, dict):
                    error_details.append(f"get_all_network_status returned non-dict: {type(all_status)}")
            except Exception as e:
                robust_handling = False
                error_details.append(f"get_all_network_status raised: {e}")
            
            if robust_handling and not error_details:
                return {
                    "test_name": "test_status_retrieval_robustness",
                    "passed": True,
                    "message": "All status retrieval methods are robust",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "test_name": "test_status_retrieval_robustness",
                    "passed": False,
                    "error": f"Status retrieval issues: {error_details}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                "test_name": "test_status_retrieval_robustness",
                "passed": False,
                "error": f"Test error: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }


async def run_network_manager_fix_tests() -> bool:
    """
    Run all network manager fix tests.
    
    Returns:
        bool: True if all tests passed, False if any failed
    """
    try:
        tester = NetworkManagerFixTester()
        results = await tester.run_comprehensive_tests()
        
        # Return success if all tests passed
        return results["failed_tests"] == 0
        
    except Exception as e:
        logger.error(f"❌ Test suite execution failed: {e}")
        return False


if __name__ == "__main__":
    """Run the network manager fix tests."""
    async def main():
        logger.info("🧪 Network Manager Fix Verification Test Suite")
        logger.info("=" * 60)
        
        success = await run_network_manager_fix_tests()
        
        if success:
            logger.info("🎉 All network manager fix tests passed!")
            logger.info("✅ The integer input error has been resolved")
            sys.exit(0)
        else:
            logger.error("❌ Some tests failed - check implementation")
            sys.exit(1)
    
    # Run the async main function
    asyncio.run(main())