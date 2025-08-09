"""
Phase 4B Integration Test Suite
File: tests/test_phase_4b_complete.py

Comprehensive test suite for Phase 4B components including database persistence,
transaction execution, configuration management, and overall system integration.
"""

import asyncio
import sys
import os
import tempfile
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
import json

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class Phase4BIntegrationTester:
    """Comprehensive Phase 4B integration test suite."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results: List[Dict[str, Any]] = []
        self.temp_dir = None
        self.db_path = None
        
        logger.info("[TEST] Phase 4B Integration Test Suite initialized")
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run all Phase 4B integration tests.
        
        Returns:
            Dict containing comprehensive test results
        """
        logger.info("="*80)
        logger.info("[START] Phase 4B Integration Test Suite - STARTING")
        logger.info("="*80)
        
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp(prefix="phase4b_test_")
        self.db_path = os.path.join(self.temp_dir, "test_db.sqlite")
        
        logger.info(f"[DIR] Test environment: {self.temp_dir}")
        
        # Test categories
        test_categories = [
            ("Database Persistence", [
                self.test_database_initialization,
                self.test_trade_record_storage,
                self.test_portfolio_snapshots,
                self.test_wallet_sessions,
                self.test_database_cleanup
            ]),
            ("Transaction Execution", [
                self.test_transaction_executor_init,
                self.test_swap_parameter_validation,
                self.test_gas_estimation,
                self.test_mock_transaction_execution,
                self.test_transaction_monitoring
            ]),
            ("Configuration Management", [
                self.test_settings_initialization,
                self.test_environment_loading,
                self.test_configuration_validation,
                self.test_runtime_config_updates,
                self.test_config_file_operations
            ]),
            ("System Integration", [
                self.test_component_initialization,
                self.test_cross_component_communication,
                self.test_error_handling_scenarios,
                self.test_graceful_degradation,
                self.test_system_shutdown
            ])
        ]
        
        passed_tests = 0
        failed_tests = 0
        total_tests = sum(len(tests) for _, tests in test_categories)
        
        # Run all test categories
        for category_name, test_methods in test_categories:
            logger.info(f"\n[SEARCH] {category_name}")
            logger.info("-" * 60)
            
            for test_method in test_methods:
                try:
                    logger.info(f"[TEST] Running {test_method.__name__}...")
                    
                    result = await test_method()
                    
                    if result.get("passed", False):
                        logger.info(f"[OK] {test_method.__name__} - PASSED")
                        passed_tests += 1
                    else:
                        logger.error(f"[ERROR] {test_method.__name__} - FAILED")
                        logger.error(f"   Reason: {result.get('error', 'Unknown error')}")
                        failed_tests += 1
                    
                    self.test_results.append(result)
                    
                except Exception as e:
                    logger.error(f"[EMOJI] {test_method.__name__} - EXCEPTION: {e}")
                    failed_tests += 1
                    
                    self.test_results.append({
                        "test_name": test_method.__name__,
                        "category": category_name,
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
            "all_results": self.test_results,
            "phase": "4B - Live Trading Features",
            "timestamp": datetime.utcnow().isoformat(),
            "test_environment": self.temp_dir
        }
        
        # Cleanup
        await self._cleanup_test_environment()
        
        logger.info("=" * 80)
        logger.info(f"[STATS] Phase 4B Integration Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            logger.info("[SUCCESS] All Phase 4B integration tests passed!")
            logger.info("[OK] Phase 4B components are ready for deployment")
        else:
            logger.warning(f"[WARN] {failed_tests} tests failed - review implementation")
        
        return summary
    
    # ==================== DATABASE PERSISTENCE TESTS ====================
    
    async def test_database_initialization(self) -> Dict[str, Any]:
        """Test database persistence system initialization."""
        try:
            from app.core.database.persistence_manager import PersistenceManager
            
            # Create test database
            persistence = PersistenceManager(self.db_path)
            
            # Test initialization
            init_success = await persistence.initialize()
            
            if not init_success:
                return {
                    "test_name": "test_database_initialization",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Database initialization failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify database file was created
            if not Path(self.db_path).exists():
                return {
                    "test_name": "test_database_initialization",
                    "category": "Database Persistence", 
                    "passed": False,
                    "error": "Database file was not created",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test status
            status = persistence.get_database_status()
            if not status.get("initialized", False):
                return {
                    "test_name": "test_database_initialization",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Database not marked as initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await persistence.shutdown()
            
            return {
                "test_name": "test_database_initialization",
                "category": "Database Persistence",
                "passed": True,
                "message": "Database persistence system initialized successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_database_initialization",
                "category": "Database Persistence",
                "passed": False,
                "error": f"Database initialization exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_trade_record_storage(self) -> Dict[str, Any]:
        """Test trade record storage and retrieval."""
        try:
            from app.core.database.persistence_manager import PersistenceManager, TradeRecord, TradeStatus
            
            persistence = PersistenceManager(self.db_path)
            await persistence.initialize()
            
            # Create test trade record
            trade_record = TradeRecord(
                trade_id=str(uuid.uuid4()),
                wallet_address="0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D",
                token_in="0xA0b86a33E6769C8Be9e4b49eEc48Fe5c9D0b91bA6",
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal("100.50"),
                amount_out=Decimal("0.05"),
                price_usd=Decimal("2000.00"),
                dex_protocol="uniswap_v2",
                network="ethereum",
                transaction_hash="0x" + "a" * 64,
                status=TradeStatus.EXECUTED,
                gas_used=150000,
                gas_price_gwei=Decimal("20"),
                slippage_percent=Decimal("1.0")
            )
            
            # Save trade record
            save_success = await persistence.save_trade(trade_record)
            
            if not save_success:
                await persistence.shutdown()
                return {
                    "test_name": "test_trade_record_storage",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Failed to save trade record",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Retrieve trade history
            trades = await persistence.get_trade_history(trade_record.wallet_address, limit=10)
            
            if not trades or len(trades) == 0:
                await persistence.shutdown()
                return {
                    "test_name": "test_trade_record_storage",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "No trades retrieved from database",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify trade data
            retrieved_trade = trades[0]
            if retrieved_trade["trade_id"] != trade_record.trade_id:
                await persistence.shutdown()
                return {
                    "test_name": "test_trade_record_storage",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Retrieved trade ID doesn't match saved trade",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await persistence.shutdown()
            
            return {
                "test_name": "test_trade_record_storage",
                "category": "Database Persistence",
                "passed": True,
                "message": f"Trade record storage and retrieval successful ({len(trades)} trades)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_trade_record_storage", 
                "category": "Database Persistence",
                "passed": False,
                "error": f"Trade storage test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_portfolio_snapshots(self) -> Dict[str, Any]:
        """Test portfolio snapshot storage and history."""
        try:
            from app.core.database.persistence_manager import PersistenceManager, PortfolioSnapshot
            
            persistence = PersistenceManager(self.db_path)
            await persistence.initialize()
            
            # Create test portfolio snapshot
            snapshot = PortfolioSnapshot(
                snapshot_id=str(uuid.uuid4()),
                wallet_address="0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D",
                total_value_usd=Decimal("15420.50"),
                eth_balance=Decimal("5.25"),
                token_count=8,
                top_holdings=[
                    {"symbol": "PEPE", "value_usd": 5000.0},
                    {"symbol": "SHIB", "value_usd": 3000.0}
                ],
                profit_loss_24h=Decimal("250.75"),
                network="ethereum"
            )
            
            # Save portfolio snapshot
            save_success = await persistence.save_portfolio_snapshot(snapshot)
            
            if not save_success:
                await persistence.shutdown()
                return {
                    "test_name": "test_portfolio_snapshots",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Failed to save portfolio snapshot",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Retrieve portfolio history
            history = await persistence.get_portfolio_history(snapshot.wallet_address, days=7)
            
            if not history or len(history) == 0:
                await persistence.shutdown()
                return {
                    "test_name": "test_portfolio_snapshots",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "No portfolio history retrieved",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify snapshot data
            retrieved_snapshot = history[0]
            if retrieved_snapshot["snapshot_id"] != snapshot.snapshot_id:
                await persistence.shutdown()
                return {
                    "test_name": "test_portfolio_snapshots",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Retrieved snapshot ID doesn't match",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await persistence.shutdown()
            
            return {
                "test_name": "test_portfolio_snapshots",
                "category": "Database Persistence",
                "passed": True,
                "message": f"Portfolio snapshot storage successful ({len(history)} snapshots)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_portfolio_snapshots",
                "category": "Database Persistence", 
                "passed": False,
                "error": f"Portfolio snapshot test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_wallet_sessions(self) -> Dict[str, Any]:
        """Test wallet session management."""
        try:
            from app.core.database.persistence_manager import PersistenceManager, WalletSession
            
            persistence = PersistenceManager(self.db_path)
            await persistence.initialize()
            
            # Create test wallet session
            session = WalletSession(
                session_id=str(uuid.uuid4()),
                wallet_address="0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D",
                wallet_type="metamask",
                network="ethereum",
                connected_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True,
                permissions=["trading", "balance_read"],
                metadata={"user_agent": "test", "ip": "127.0.0.1"}
            )
            
            # Save wallet session
            save_success = await persistence.save_wallet_session(session)
            
            if not save_success:
                await persistence.shutdown()
                return {
                    "test_name": "test_wallet_sessions",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Failed to save wallet session",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Retrieve active sessions
            active_sessions = await persistence.get_active_sessions()
            
            if not active_sessions or len(active_sessions) == 0:
                await persistence.shutdown()
                return {
                    "test_name": "test_wallet_sessions",
                    "category": "Database Persistence", 
                    "passed": False,
                    "error": "No active sessions retrieved",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify session data
            retrieved_session = active_sessions[0]
            if retrieved_session["session_id"] != session.session_id:
                await persistence.shutdown()
                return {
                    "test_name": "test_wallet_sessions",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Retrieved session ID doesn't match",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await persistence.shutdown()
            
            return {
                "test_name": "test_wallet_sessions",
                "category": "Database Persistence",
                "passed": True,
                "message": f"Wallet session management successful ({len(active_sessions)} sessions)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_wallet_sessions",
                "category": "Database Persistence",
                "passed": False,
                "error": f"Wallet session test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_database_cleanup(self) -> Dict[str, Any]:
        """Test database cleanup operations."""
        try:
            from app.core.database.persistence_manager import PersistenceManager
            
            persistence = PersistenceManager(self.db_path)
            await persistence.initialize()
            
            # Run cleanup
            cleanup_count = await persistence.cleanup_old_data(days=1)
            
            # Cleanup should work even if no old data
            if cleanup_count < 0:
                await persistence.shutdown()
                return {
                    "test_name": "test_database_cleanup",
                    "category": "Database Persistence",
                    "passed": False,
                    "error": "Invalid cleanup count returned",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await persistence.shutdown()
            
            return {
                "test_name": "test_database_cleanup",
                "category": "Database Persistence",
                "passed": True,
                "message": f"Database cleanup successful ({cleanup_count} records cleaned)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_database_cleanup",
                "category": "Database Persistence",
                "passed": False,
                "error": f"Database cleanup test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ==================== TRANSACTION EXECUTION TESTS ====================
    
    async def test_transaction_executor_init(self) -> Dict[str, Any]:
        """Test transaction executor initialization."""
        try:
            from app.core.trading.transaction_executor import TransactionExecutor
            
            # Create transaction executor
            executor = TransactionExecutor()
            
            # Test initialization
            init_success = await executor.initialize()
            
            if not init_success:
                return {
                    "test_name": "test_transaction_executor_init",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Transaction executor initialization failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test status
            status = executor.get_execution_status()
            
            if not isinstance(status, dict):
                await executor.shutdown()
                return {
                    "test_name": "test_transaction_executor_init",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Invalid status response",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await executor.shutdown()
            
            return {
                "test_name": "test_transaction_executor_init",
                "category": "Transaction Execution",
                "passed": True,
                "message": "Transaction executor initialized successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_transaction_executor_init",
                "category": "Transaction Execution",
                "passed": False,
                "error": f"Transaction executor init exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_swap_parameter_validation(self) -> Dict[str, Any]:
        """Test swap parameter validation."""
        try:
            from app.core.trading.transaction_executor import TransactionExecutor, SwapParameters
            from decimal import Decimal
            
            executor = TransactionExecutor()
            await executor.initialize()
            
            # Test valid parameters
            valid_params = SwapParameters(
                token_in="0xA0b86a33E6769C8Be9e4b49eEc48Fe5c9D0b91bA6",
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal("100"),
                minimum_amount_out=Decimal("0.05"),
                slippage_tolerance=Decimal("0.01")
            )
            
            # This should not raise an exception
            try:
                await executor._validate_swap_parameters(
                    valid_params, 
                    "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D"
                )
                validation_passed = True
            except Exception:
                validation_passed = False
            
            if not validation_passed:
                await executor.shutdown()
                return {
                    "test_name": "test_swap_parameter_validation",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Valid parameters failed validation",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test invalid parameters (negative amount)
            invalid_params = SwapParameters(
                token_in="0xA0b86a33E6769C8Be9e4b49eEc48Fe5c9D0b91bA6",
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal("-100"),  # Invalid negative amount
                minimum_amount_out=Decimal("0.05"),
                slippage_tolerance=Decimal("0.01")
            )
            
            # This should raise an exception
            try:
                await executor._validate_swap_parameters(
                    invalid_params,
                    "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D"
                )
                invalid_validation_passed = True
            except Exception:
                invalid_validation_passed = False
            
            if invalid_validation_passed:
                await executor.shutdown()
                return {
                    "test_name": "test_swap_parameter_validation",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Invalid parameters passed validation",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await executor.shutdown()
            
            return {
                "test_name": "test_swap_parameter_validation",
                "category": "Transaction Execution",
                "passed": True,
                "message": "Swap parameter validation working correctly",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_swap_parameter_validation",
                "category": "Transaction Execution",
                "passed": False,
                "error": f"Swap validation test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_gas_estimation(self) -> Dict[str, Any]:
        """Test gas estimation functionality."""
        try:
            from app.core.trading.transaction_executor import TransactionExecutor, SwapParameters
            from decimal import Decimal
            
            executor = TransactionExecutor()
            await executor.initialize()
            
            # Create test swap parameters
            swap_params = SwapParameters(
                token_in="0xA0b86a33E6769C8Be9e4b49eEc48Fe5c9D0b91bA6",
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal("100"),
                minimum_amount_out=Decimal("0.05"),
                slippage_tolerance=Decimal("0.01")
            )
            
            # Estimate gas
            gas_estimate = await executor.estimate_gas_for_swap(
                swap_params,
                "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D"
            )
            
            # Verify gas estimate structure
            if not hasattr(gas_estimate, 'gas_limit') or gas_estimate.gas_limit <= 0:
                await executor.shutdown()
                return {
                    "test_name": "test_gas_estimation",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Invalid gas limit in estimate",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if not hasattr(gas_estimate, 'gas_price_gwei') or gas_estimate.gas_price_gwei <= 0:
                await executor.shutdown()
                return {
                    "test_name": "test_gas_estimation",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Invalid gas price in estimate",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await executor.shutdown()
            
            return {
                "test_name": "test_gas_estimation",
                "category": "Transaction Execution",
                "passed": True,
                "message": f"Gas estimation successful (limit: {gas_estimate.gas_limit}, price: {gas_estimate.gas_price_gwei} gwei)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_gas_estimation",
                "category": "Transaction Execution",
                "passed": False,
                "error": f"Gas estimation test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_mock_transaction_execution(self) -> Dict[str, Any]:
        """Test mock transaction execution."""
        try:
            from app.core.trading.transaction_executor import (
                TransactionExecutor, SwapParameters, GasPriorityLevel, TransactionStatus
            )
            from decimal import Decimal
            
            executor = TransactionExecutor()
            await executor.initialize()
            
            # Create test swap parameters
            swap_params = SwapParameters(
                token_in="0xA0b86a33E6769C8Be9e4b49eEc48Fe5c9D0b91bA6",
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal("100"),
                minimum_amount_out=Decimal("0.05"),
                slippage_tolerance=Decimal("0.01")
            )
            
            # Execute mock swap
            result = await executor.execute_swap(
                swap_params,
                "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D",
                GasPriorityLevel.STANDARD
            )
            
            # Verify result structure
            if not result or not hasattr(result, 'transaction_hash'):
                await executor.shutdown()
                return {
                    "test_name": "test_mock_transaction_execution",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Invalid transaction result",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if result.status not in [TransactionStatus.CONFIRMED, TransactionStatus.SUBMITTED]:
                await executor.shutdown()
                return {
                    "test_name": "test_mock_transaction_execution",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": f"Unexpected transaction status: {result.status}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await executor.shutdown()
            
            return {
                "test_name": "test_mock_transaction_execution",
                "category": "Transaction Execution",
                "passed": True,
                "message": f"Mock transaction execution successful (status: {result.status.value})",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_mock_transaction_execution",
                "category": "Transaction Execution",
                "passed": False,
                "error": f"Mock transaction test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_transaction_monitoring(self) -> Dict[str, Any]:
        """Test transaction monitoring functionality."""
        try:
            from app.core.trading.transaction_executor import TransactionExecutor, TransactionStatus
            
            executor = TransactionExecutor()
            await executor.initialize()
            
            # Monitor a mock transaction hash
            mock_tx_hash = "0x" + "a" * 64
            
            result = await executor.monitor_transaction(mock_tx_hash, timeout_minutes=1)
            
            # Verify monitoring result
            if not result or not hasattr(result, 'transaction_hash'):
                await executor.shutdown()
                return {
                    "test_name": "test_transaction_monitoring",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Invalid monitoring result",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if result.transaction_hash != mock_tx_hash:
                await executor.shutdown()
                return {
                    "test_name": "test_transaction_monitoring",
                    "category": "Transaction Execution",
                    "passed": False,
                    "error": "Transaction hash mismatch in monitoring result",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await executor.shutdown()
            
            return {
                "test_name": "test_transaction_monitoring",
                "category": "Transaction Execution",
                "passed": True,
                "message": f"Transaction monitoring successful (status: {result.status.value})",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_transaction_monitoring",
                "category": "Transaction Execution",
                "passed": False,
                "error": f"Transaction monitoring test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ==================== CONFIGURATION MANAGEMENT TESTS ====================
    
    async def test_settings_initialization(self) -> Dict[str, Any]:
        """Test configuration system initialization."""
        try:
            from app.core.config.settings_manager import ApplicationSettings, Environment
            
            # Create test settings
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            
            # Verify settings structure
            if not hasattr(settings, 'database') or not hasattr(settings, 'trading'):
                return {
                    "test_name": "test_settings_initialization",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Missing configuration components",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test configuration summary
            summary = settings.get_configuration_summary()
            
            if not isinstance(summary, dict) or 'environment' not in summary:
                return {
                    "test_name": "test_settings_initialization",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Invalid configuration summary",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "test_name": "test_settings_initialization",
                "category": "Configuration Management",
                "passed": True,
                "message": f"Settings initialized for {summary['environment']} environment",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_settings_initialization",
                "category": "Configuration Management",
                "passed": False,
                "error": f"Settings initialization exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_environment_loading(self) -> Dict[str, Any]:
        """Test environment variable loading."""
        try:
            from app.core.config.settings_manager import ApplicationSettings, Environment
            
            # Set test environment variables
            os.environ["TRADING_ENABLED"] = "false"
            os.environ["MAX_POSITION_SIZE_ETH"] = "0.5"
            os.environ["LOG_LEVEL"] = "DEBUG"
            
            # Create settings with environment loading
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            
            # Verify environment variables were loaded
            if settings.trading.enabled != False:
                return {
                    "test_name": "test_environment_loading",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "TRADING_ENABLED environment variable not loaded",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if settings.trading.max_position_size_eth != 0.5:
                return {
                    "test_name": "test_environment_loading",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "MAX_POSITION_SIZE_ETH environment variable not loaded",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if settings.monitoring.log_level != "DEBUG":
                return {
                    "test_name": "test_environment_loading",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "LOG_LEVEL environment variable not loaded",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Clean up environment variables
            del os.environ["TRADING_ENABLED"]
            del os.environ["MAX_POSITION_SIZE_ETH"]
            del os.environ["LOG_LEVEL"]
            
            return {
                "test_name": "test_environment_loading",
                "category": "Configuration Management",
                "passed": True,
                "message": "Environment variables loaded successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_environment_loading",
                "category": "Configuration Management",
                "passed": False,
                "error": f"Environment loading test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_configuration_validation(self) -> Dict[str, Any]:
        """Test configuration validation."""
        try:
            from app.core.config.settings_manager import ApplicationSettings, Environment
            
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            
            # Test valid configuration
            errors = settings.validate_configuration()
            
            # Should have no errors for default configuration
            if len(errors) > 0:
                return {
                    "test_name": "test_configuration_validation",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": f"Default configuration has validation errors: {errors}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test invalid configuration
            settings.trading.max_position_size_eth = -1.0  # Invalid negative value
            
            errors = settings.validate_configuration()
            
            if len(errors) == 0:
                return {
                    "test_name": "test_configuration_validation",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Validation did not catch invalid configuration",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "test_name": "test_configuration_validation",
                "category": "Configuration Management",
                "passed": True,
                "message": f"Configuration validation working correctly ({len(errors)} errors found for invalid config)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_configuration_validation",
                "category": "Configuration Management",
                "passed": False,
                "error": f"Configuration validation test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_runtime_config_updates(self) -> Dict[str, Any]:
        """Test runtime configuration updates."""
        try:
            from app.core.config.settings_manager import ApplicationSettings, Environment
            
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            
            # Test valid configuration update
            updates = {
                "max_position_size_eth": 2.0,
                "default_slippage_percent": 2.5
            }
            
            update_success = settings.update_trading_config(updates)
            
            if not update_success:
                return {
                    "test_name": "test_runtime_config_updates",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Valid configuration update failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify updates were applied
            if settings.trading.max_position_size_eth != 2.0:
                return {
                    "test_name": "test_runtime_config_updates",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Configuration update was not applied",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test invalid configuration update
            invalid_updates = {
                "max_position_size_eth": -5.0  # Invalid negative value
            }
            
            invalid_update_success = settings.update_trading_config(invalid_updates)
            
            if invalid_update_success:
                return {
                    "test_name": "test_runtime_config_updates",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Invalid configuration update was accepted",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "test_name": "test_runtime_config_updates",
                "category": "Configuration Management",
                "passed": True,
                "message": "Runtime configuration updates working correctly",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_runtime_config_updates",
                "category": "Configuration Management",
                "passed": False,
                "error": f"Runtime config update test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_config_file_operations(self) -> Dict[str, Any]:
        """Test configuration file save/load operations."""
        try:
            from app.core.config.settings_manager import ApplicationSettings, Environment
            
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            
            # Create temporary config directory
            temp_config_dir = os.path.join(self.temp_dir, "config")
            os.makedirs(temp_config_dir, exist_ok=True)
            settings.config_dir = Path(temp_config_dir)
            
            # Test saving configuration
            save_success = settings.save_configuration(include_sensitive=False)
            
            if not save_success:
                return {
                    "test_name": "test_config_file_operations",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Configuration save failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify config file was created
            config_file = settings.config_dir / f"{settings.environment.value}.json"
            if not config_file.exists():
                return {
                    "test_name": "test_config_file_operations",
                    "category": "Configuration Management",
                    "passed": False,
                    "error": "Configuration file was not created",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test creating sample config files
            settings.create_sample_config_files()
            
            # Verify sample files were created
            expected_files = ["development.json", "production.json"]
            for filename in expected_files:
                file_path = settings.config_dir / filename
                if not file_path.exists():
                    return {
                        "test_name": "test_config_file_operations",
                        "category": "Configuration Management",
                        "passed": False,
                        "error": f"Sample config file {filename} was not created",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            return {
                "test_name": "test_config_file_operations",
                "category": "Configuration Management",
                "passed": True,
                "message": "Configuration file operations successful",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_config_file_operations",
                "category": "Configuration Management",
                "passed": False,
                "error": f"Config file operations test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ==================== SYSTEM INTEGRATION TESTS ====================
    
    async def test_component_initialization(self) -> Dict[str, Any]:
        """Test initialization of all Phase 4B components together."""
        try:
            # Test database initialization
            from app.core.database.persistence_manager import PersistenceManager
            persistence = PersistenceManager(self.db_path)
            db_success = await persistence.initialize()
            
            # Test transaction executor initialization
            from app.core.trading.transaction_executor import TransactionExecutor
            executor = TransactionExecutor()
            tx_success = await executor.initialize()
            
            # Test configuration system
            from app.core.config.settings_manager import ApplicationSettings, Environment
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            config_errors = settings.validate_configuration()
            
            # Verify all components initialized successfully
            if not db_success:
                await persistence.shutdown()
                await executor.shutdown()
                return {
                    "test_name": "test_component_initialization",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Database component initialization failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if not tx_success:
                await persistence.shutdown()
                await executor.shutdown()
                return {
                    "test_name": "test_component_initialization",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Transaction executor initialization failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if len(config_errors) > 0:
                await persistence.shutdown()
                await executor.shutdown()
                return {
                    "test_name": "test_component_initialization",
                    "category": "System Integration",
                    "passed": False,
                    "error": f"Configuration validation failed: {config_errors}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Clean up
            await persistence.shutdown()
            await executor.shutdown()
            
            return {
                "test_name": "test_component_initialization",
                "category": "System Integration",
                "passed": True,
                "message": "All Phase 4B components initialized successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_component_initialization",
                "category": "System Integration",
                "passed": False,
                "error": f"Component initialization test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_cross_component_communication(self) -> Dict[str, Any]:
        """Test communication between Phase 4B components."""
        try:
            from app.core.database.persistence_manager import PersistenceManager, TradeRecord, TradeStatus
            from app.core.trading.transaction_executor import TransactionExecutor, SwapParameters
            from app.core.config.settings_manager import ApplicationSettings, Environment
            from decimal import Decimal
            
            # Initialize components
            persistence = PersistenceManager(self.db_path)
            await persistence.initialize()
            
            executor = TransactionExecutor()
            await executor.initialize()
            
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            
            # Test cross-component workflow: Execute swap and save to database
            swap_params = SwapParameters(
                token_in="0xA0b86a33E6769C8Be9e4b49eEc48Fe5c9D0b91bA6",
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal(str(settings.trading.max_position_size_eth)),
                minimum_amount_out=Decimal("0.05"),
                slippage_tolerance=Decimal(str(settings.trading.default_slippage_percent / 100))
            )
            
            # Execute swap
            tx_result = await executor.execute_swap(
                swap_params,
                "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D"
            )
            
            if not tx_result or not tx_result.transaction_hash:
                await persistence.shutdown()
                await executor.shutdown()
                return {
                    "test_name": "test_cross_component_communication",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Transaction execution failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Verify transaction was saved to database (this happens automatically in executor)
            trades = await persistence.get_trade_history(
                "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D",
                limit=5
            )
            
            # Find our transaction
            our_trade = None
            for trade in trades:
                if trade.get("trade_id") == tx_result.transaction_id:
                    our_trade = trade
                    break
            
            if not our_trade:
                await persistence.shutdown()
                await executor.shutdown()
                return {
                    "test_name": "test_cross_component_communication",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Transaction was not saved to database",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Clean up
            await persistence.shutdown()
            await executor.shutdown()
            
            return {
                "test_name": "test_cross_component_communication",
                "category": "System Integration",
                "passed": True,
                "message": "Cross-component communication successful (executor->database)",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_cross_component_communication",
                "category": "System Integration",
                "passed": False,
                "error": f"Cross-component communication test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_error_handling_scenarios(self) -> Dict[str, Any]:
        """Test error handling across components."""
        try:
            from app.core.database.persistence_manager import PersistenceManager
            from app.core.trading.transaction_executor import TransactionExecutor, SwapParameters
            from decimal import Decimal
            
            # Test database error handling
            persistence = PersistenceManager("/invalid/path/that/does/not/exist.db")
            db_init_result = await persistence.initialize()
            
            # Should handle gracefully (mock mode)
            if db_init_result is None:
                return {
                    "test_name": "test_error_handling_scenarios",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Database error handling returned None",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test transaction executor with invalid parameters
            executor = TransactionExecutor()
            await executor.initialize()
            
            invalid_swap_params = SwapParameters(
                token_in="invalid_address",  # Invalid address format
                token_out="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                amount_in=Decimal("-100"),  # Invalid negative amount
                minimum_amount_out=Decimal("0.05"),
                slippage_tolerance=Decimal("0.01")
            )
            
            # This should fail gracefully
            tx_result = await executor.execute_swap(
                invalid_swap_params,
                "0x742D35A0D8F4F2b4d35F8F2a1e9B4C3F8b7A6E9D"
            )
            
            # Should return a failed result, not raise an exception
            if not tx_result:
                await executor.shutdown()
                return {
                    "test_name": "test_error_handling_scenarios",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Transaction executor should return failed result, not None",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            from app.core.trading.transaction_executor import TransactionStatus
            if tx_result.status != TransactionStatus.FAILED:
                await executor.shutdown()
                return {
                    "test_name": "test_error_handling_scenarios",
                    "category": "System Integration",
                    "passed": False,
                    "error": f"Expected FAILED status, got {tx_result.status}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await executor.shutdown()
            
            return {
                "test_name": "test_error_handling_scenarios",
                "category": "System Integration",
                "passed": True,
                "message": "Error handling scenarios working correctly",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_error_handling_scenarios",
                "category": "System Integration",
                "passed": False,
                "error": f"Error handling test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_graceful_degradation(self) -> Dict[str, Any]:
        """Test graceful degradation when components are unavailable."""
        try:
            # Test system behavior when optional libraries are missing
            # This simulates the environment where web3, aiosqlite, etc. are not available
            
            from app.core.config.settings_manager import ApplicationSettings, Environment
            
            # Configuration should work even without optional dependencies
            settings = ApplicationSettings(Environment.DEVELOPMENT)
            summary = settings.get_configuration_summary()
            
            if not isinstance(summary, dict):
                return {
                    "test_name": "test_graceful_degradation",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Configuration system not working without optional dependencies",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Database should initialize with mock when aiosqlite unavailable
            from app.core.database.persistence_manager import PersistenceManager
            persistence = PersistenceManager(self.db_path)
            
            # Should initialize successfully (with mocks if needed)
            init_result = await persistence.initialize()
            
            if init_result is False:
                return {
                    "test_name": "test_graceful_degradation",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Database persistence should degrade gracefully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Transaction executor should work with mocks
            from app.core.trading.transaction_executor import TransactionExecutor
            executor = TransactionExecutor()
            
            init_result = await executor.initialize(None)  # No web3 provider
            
            if init_result is False:
                await persistence.shutdown()
                return {
                    "test_name": "test_graceful_degradation",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Transaction executor should degrade gracefully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            await persistence.shutdown()
            await executor.shutdown()
            
            return {
                "test_name": "test_graceful_degradation",
                "category": "System Integration",
                "passed": True,
                "message": "Graceful degradation working correctly",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_graceful_degradation",
                "category": "System Integration",
                "passed": False,
                "error": f"Graceful degradation test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_system_shutdown(self) -> Dict[str, Any]:
        """Test proper system shutdown and cleanup."""
        try:
            from app.core.database.persistence_manager import PersistenceManager
            from app.core.trading.transaction_executor import TransactionExecutor
            
            # Initialize components
            persistence = PersistenceManager(self.db_path)
            await persistence.initialize()
            
            executor = TransactionExecutor()
            await executor.initialize()
            
            # Test shutdown procedures
            await persistence.shutdown()
            await executor.shutdown()
            
            # Verify shutdown status
            db_status = persistence.get_database_status()
            if db_status.get("initialized", True):  # Should be False after shutdown
                return {
                    "test_name": "test_system_shutdown",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Database not properly shut down",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            executor_status = executor.get_execution_status()
            # Monitoring should be inactive after shutdown
            if executor_status.get("monitoring_active", True):
                return {
                    "test_name": "test_system_shutdown",
                    "category": "System Integration",
                    "passed": False,
                    "error": "Transaction executor monitoring not properly shut down",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "test_name": "test_system_shutdown",
                "category": "System Integration",
                "passed": True,
                "message": "System shutdown and cleanup successful",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "test_name": "test_system_shutdown",
                "category": "System Integration",
                "passed": False,
                "error": f"System shutdown test exception: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ==================== UTILITY METHODS ====================
    
    async def _cleanup_test_environment(self):
        """Clean up test environment."""
        try:
            import shutil
            
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 Test environment cleaned up: {self.temp_dir}")
        
        except Exception as e:
            logger.warning(f"[WARN] Error cleaning up test environment: {e}")


async def run_phase_4b_tests():
    """Run Phase 4B integration tests."""
    tester = Phase4BIntegrationTester()
    return await tester.run_comprehensive_tests()


def print_test_summary(results: Dict[str, Any]):
    """Print formatted test summary."""
    print("\n" + "="*80)
    print("[STATS] PHASE 4B INTEGRATION TEST SUMMARY")
    print("="*80)
    
    total_tests = results.get("total_tests", 0)
    passed_tests = results.get("passed_tests", 0)
    failed_tests = results.get("failed_tests", 0)
    success_rate = results.get("success_rate", 0)
    
    print(f"[LOG] Total Tests: {total_tests}")
    print(f"[OK] Passed: {passed_tests}")
    print(f"[ERROR] Failed: {failed_tests}")
    print(f"[PERF] Success Rate: {success_rate:.1f}%")
    print(f"[EMOJI] Test Time: {results.get('timestamp', 'Unknown')}")
    
    if failed_tests > 0:
        print(f"\n[WARN] FAILED TESTS:")
        print("-" * 40)
        
        for result in results.get("all_results", []):
            if not result.get("passed", True):
                print(f"[ERROR] {result.get('test_name', 'Unknown')}")
                print(f"   Category: {result.get('category', 'Unknown')}")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print()
    
    if failed_tests == 0:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("[OK] Phase 4B components are fully operational")
        print("[OK] Ready for production deployment")
    else:
        print(f"\n[WARN] {failed_tests} tests failed")
        print("[FIX] Please review and fix failing components")
    
    print("="*80)


async def main():
    """Main test execution function."""
    print("[BOT] DEX Sniper Pro - Phase 4B Integration Test Suite")
    print("="*60)
    print("Testing: Database Persistence, Transaction Execution,")
    print("         Configuration Management, System Integration")
    print("="*60)
    
    try:
        # Run comprehensive Phase 4B tests
        results = await run_phase_4b_tests()
        
        # Print detailed summary
        print_test_summary(results)
        
        # Return exit code based on results
        if results.get("failed_tests", 0) == 0:
            print("\n[OK] Phase 4B Integration Tests: ALL PASSED")
            return 0
        else:
            print(f"\n[ERROR] Phase 4B Integration Tests: {results.get('failed_tests', 0)} FAILED")
            return 1
    
    except Exception as e:
        print(f"\n[EMOJI] Test suite execution failed: {e}")
        logger.error(f"Test suite error: {e}")
        return 1


if __name__ == "__main__":
    """Run the Phase 4B integration test suite."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[EMOJI] Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[EMOJI] Fatal error in test suite: {e}")
        sys.exit(1)