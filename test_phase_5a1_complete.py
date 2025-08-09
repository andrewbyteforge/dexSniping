"""
Phase 5A.1: Comprehensive Test Suite
File: test_phase_5a1_complete.py

Complete testing suite for all Phase 5A.1 trading performance optimization components.
Tests real profit tracking, gas optimization, execution speed, and integration.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
import json
import time

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.utils.logger import setup_logger
    from app.core.performance.trading_optimizer import (
        get_trading_performance_optimizer,
        TradingPerformanceOptimizer,
        TradeProfitAnalysis,
        StrategyPerformance
    )
    from app.core.performance.gas_optimizer import (
        get_gas_optimizer,
        GasOptimizationEngine,
        GasStrategy,
        NetworkType
    )
    from app.core.performance.execution_optimizer import (
        get_execution_optimizer,
        ExecutionSpeedOptimizer,
        ExecutionPriority,
        ExecutionStage
    )
    from app.core.performance.trading_performance_manager import (
        get_trading_performance_manager,
        TradingPerformanceManager
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're running from the project root directory")
    sys.exit(1)

logger = setup_logger(__name__)


class Phase5A1TestSuite:
    """Comprehensive test suite for Phase 5A.1 components."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_wallet = "0x1234567890123456789012345678901234567890"
        self.test_results = []
        self.performance_data = {}
        
        # Test components
        self.profit_optimizer = None
        self.gas_optimizer = None
        self.execution_optimizer = None
        self.performance_manager = None
        
        print("🧪 Phase 5A.1 Test Suite Initialized")
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite for all Phase 5A.1 components."""
        print("🚀 Starting Phase 5A.1 Complete Test Suite")
        print("=" * 70)
        
        try:
            # Test component initialization
            await self._test_component_initialization()
            
            # Test profit tracking and optimization
            await self._test_profit_optimization()
            
            # Test gas optimization
            await self._test_gas_optimization()
            
            # Test execution speed optimization
            await self._test_execution_optimization()
            
            # Test integration and performance manager
            await self._test_integration()
            
            # Test complete trading workflow
            await self._test_complete_trading_workflow()
            
            # Generate test summary
            return await self._generate_test_summary()
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _test_component_initialization(self) -> None:
        """Test initialization of all Phase 5A.1 components."""
        print("\n🔧 Testing Component Initialization")
        print("-" * 50)
        
        try:
            # Test profit optimizer initialization
            print("🧪 Testing Profit Optimizer initialization...")
            self.profit_optimizer = TradingPerformanceOptimizer(self.test_wallet)
            init_success = await self.profit_optimizer.initialize()
            
            self._record_test_result(
                "profit_optimizer_init",
                init_success,
                "Profit optimizer initialized successfully" if init_success else "Failed to initialize profit optimizer"
            )
            
            # Test gas optimizer initialization
            print("🧪 Testing Gas Optimizer initialization...")
            self.gas_optimizer = GasOptimizationEngine(self.test_wallet)
            init_success = await self.gas_optimizer.initialize()
            
            self._record_test_result(
                "gas_optimizer_init",
                init_success,
                "Gas optimizer initialized successfully" if init_success else "Failed to initialize gas optimizer"
            )
            
            # Test execution optimizer initialization
            print("🧪 Testing Execution Optimizer initialization...")
            self.execution_optimizer = ExecutionSpeedOptimizer(self.test_wallet)
            init_success = await self.execution_optimizer.initialize()
            
            self._record_test_result(
                "execution_optimizer_init",
                init_success,
                "Execution optimizer initialized successfully" if init_success else "Failed to initialize execution optimizer"
            )
            
            # Test performance manager initialization
            print("🧪 Testing Performance Manager initialization...")
            self.performance_manager = TradingPerformanceManager(self.test_wallet)
            init_success = await self.performance_manager.initialize()
            
            self._record_test_result(
                "performance_manager_init",
                init_success,
                "Performance manager initialized successfully" if init_success else "Failed to initialize performance manager"
            )
            
        except Exception as e:
            logger.error(f"❌ Component initialization test failed: {e}")
            self._record_test_result("component_initialization", False, f"Initialization failed: {e}")
    
    async def _test_profit_optimization(self) -> None:
        """Test profit tracking and optimization functionality."""
        print("\n💰 Testing Profit Optimization")
        print("-" * 50)
        
        try:
            if not self.profit_optimizer:
                print("⚠️ Profit optimizer not available, skipping tests")
                return
            
            # Test trade entry tracking
            print("🧪 Testing trade entry tracking...")
            trade_id = "test_trade_001"
            entry_success = await self.profit_optimizer.track_trade_entry(
                trade_id=trade_id,
                strategy_name="momentum",
                token_symbol="PEPE",
                entry_price=Decimal("0.001"),
                entry_amount=Decimal("1000"),
                gas_fee_usd=Decimal("5.0")
            )
            
            self._record_test_result(
                "trade_entry_tracking",
                entry_success,
                "Trade entry tracked successfully" if entry_success else "Failed to track trade entry"
            )
            
            # Test trade exit tracking with profit calculation
            print("🧪 Testing trade exit tracking...")
            if entry_success:
                exit_result = await self.profit_optimizer.track_trade_exit(
                    trade_id=trade_id,
                    exit_price=Decimal("0.0012"),
                    exit_amount=Decimal("1000"),
                    gas_fee_usd=Decimal("4.5"),
                    execution_time_seconds=15.5
                )
                
                exit_success = exit_result.get("success", False)
                self._record_test_result(
                    "trade_exit_tracking",
                    exit_success,
                    "Trade exit tracked and profit calculated" if exit_success else "Failed to track trade exit"
                )
                
                # Store profit data for analysis
                if exit_success:
                    self.performance_data["sample_trade"] = exit_result
            
            # Test performance summary
            print("🧪 Testing performance summary generation...")
            summary = await self.profit_optimizer.get_performance_summary(days=30)
            summary_success = "error" not in summary
            
            self._record_test_result(
                "performance_summary",
                summary_success,
                "Performance summary generated successfully" if summary_success else f"Failed to generate summary: {summary.get('error', 'Unknown error')}"
            )
            
            # Test strategy optimization
            print("🧪 Testing strategy optimization...")
            strategy_opt = await self.profit_optimizer.optimize_strategy_parameters("momentum")
            opt_success = "error" not in strategy_opt
            
            self._record_test_result(
                "strategy_optimization",
                opt_success,
                "Strategy optimization completed" if opt_success else f"Strategy optimization failed: {strategy_opt.get('error', 'Unknown error')}"
            )
            
        except Exception as e:
            logger.error(f"❌ Profit optimization test failed: {e}")
            self._record_test_result("profit_optimization", False, f"Profit optimization test failed: {e}")
    
    async def _test_gas_optimization(self) -> None:
        """Test gas optimization functionality."""
        print("\n⛽ Testing Gas Optimization")
        print("-" * 50)
        
        try:
            if not self.gas_optimizer:
                print("⚠️ Gas optimizer not available, skipping tests")
                return
            
            # Test gas price monitoring
            print("🧪 Testing gas price monitoring...")
            # Gas prices should be automatically monitored during initialization
            has_gas_prices = len(self.gas_optimizer.current_gas_prices) > 0
            
            self._record_test_result(
                "gas_price_monitoring",
                has_gas_prices,
                "Gas prices monitored successfully" if has_gas_prices else "No gas price data available"
            )
            
            # Test gas optimization for trade
            print("🧪 Testing gas optimization for trade...")
            optimization_result = await self.gas_optimizer.optimize_gas_for_trade(
                network=NetworkType.ETHEREUM,
                trade_value_usd=Decimal("500"),
                urgency="normal",
                max_gas_cost_percent=5.0
            )
            
            opt_success = hasattr(optimization_result, 'recommended_strategy')
            self._record_test_result(
                "gas_trade_optimization",
                opt_success,
                f"Gas optimization successful: {optimization_result.recommended_strategy.value if opt_success else 'Failed'}"
            )
            
            # Test gas usage tracking
            print("🧪 Testing gas usage tracking...")
            tracking_success = await self.gas_optimizer.track_gas_usage(
                transaction_hash="0xtest123456789",
                gas_price_gwei=Decimal("30"),
                gas_used=150000,
                gas_cost_usd=Decimal("7.50"),
                confirmation_time_minutes=3,
                network=NetworkType.ETHEREUM,
                transaction_type="swap",
                was_successful=True,
                user_strategy=GasStrategy.STANDARD
            )
            
            self._record_test_result(
                "gas_usage_tracking",
                tracking_success,
                "Gas usage tracked successfully" if tracking_success else "Failed to track gas usage"
            )
            
            # Test gas efficiency report
            print("🧪 Testing gas efficiency report...")
            efficiency_report = await self.gas_optimizer.get_gas_efficiency_report(days=30)
            report_success = "error" not in efficiency_report
            
            self._record_test_result(
                "gas_efficiency_report",
                report_success,
                "Gas efficiency report generated" if report_success else f"Report failed: {efficiency_report.get('error', 'Unknown error')}"
            )
            
            # Test optimal trading time analysis
            print("🧪 Testing optimal trading time analysis...")
            optimal_times = await self.gas_optimizer.get_optimal_trading_time(
                network=NetworkType.ETHEREUM,
                hours_ahead=24
            )
            
            timing_success = "error" not in optimal_times
            self._record_test_result(
                "optimal_trading_time",
                timing_success,
                "Optimal trading time analysis completed" if timing_success else f"Timing analysis failed: {optimal_times.get('error', 'Unknown error')}"
            )
            
        except Exception as e:
            logger.error(f"❌ Gas optimization test failed: {e}")
            self._record_test_result("gas_optimization", False, f"Gas optimization test failed: {e}")
    
    async def _test_execution_optimization(self) -> None:
        """Test execution speed optimization functionality."""
        print("\n⚡ Testing Execution Optimization")
        print("-" * 50)
        
        try:
            if not self.execution_optimizer:
                print("⚠️ Execution optimizer not available, skipping tests")
                return
            
            # Test execution timing start
            print("🧪 Testing execution timing start...")
            timing = await self.execution_optimizer.start_execution_timing(
                trade_id="test_exec_001",
                strategy_name="arbitrage",
                token_symbol="UNI",
                priority=ExecutionPriority.HIGH,
                network=NetworkType.ETHEREUM
            )
            
            timing_success = timing is not None
            self._record_test_result(
                "execution_timing_start",
                timing_success,
                "Execution timing started successfully" if timing_success else "Failed to start execution timing"
            )
            
            # Test stage timing recording
            print("🧪 Testing stage timing recording...")
            if timing_success:
                stages_to_test = [
                    (ExecutionStage.MARKET_ANALYSIS, 2.5),
                    (ExecutionStage.RISK_ASSESSMENT, 1.0),
                    (ExecutionStage.ORDER_PREPARATION, 0.8),
                    (ExecutionStage.TRANSACTION_SUBMISSION, 3.2),
                    (ExecutionStage.CONFIRMATION_WAIT, 45.0),
                    (ExecutionStage.RESULT_PROCESSING, 0.5)
                ]
                
                stage_success = True
                for stage, duration in stages_to_test:
                    try:
                        await self.execution_optimizer.record_stage_timing(
                            trade_id="test_exec_001",
                            stage=stage,
                            duration_seconds=duration
                        )
                    except Exception as e:
                        logger.error(f"Failed to record {stage.value}: {e}")
                        stage_success = False
                
                self._record_test_result(
                    "stage_timing_recording",
                    stage_success,
                    "All execution stages recorded successfully" if stage_success else "Some stage recordings failed"
                )
            
            # Test execution completion
            print("🧪 Testing execution completion...")
            completion_result = await self.execution_optimizer.complete_execution_timing(
                trade_id="test_exec_001",
                was_successful=True,
                profit_loss_usd=Decimal("25.50"),
                gas_price_gwei=Decimal("35"),
                slippage_percentage=0.8
            )
            
            completion_success = completion_result.get("trade_id") == "test_exec_001"
            self._record_test_result(
                "execution_completion",
                completion_success,
                f"Execution completed: {completion_result.get('total_execution_time', 0):.2f}s" if completion_success else "Failed to complete execution timing"
            )
            
            # Test execution speed optimization
            print("🧪 Testing execution speed optimization...")
            speed_optimization = await self.execution_optimizer.optimize_execution_speed(
                strategy_name="arbitrage",
                priority=ExecutionPriority.HIGH,
                target_improvement_percent=25.0
            )
            
            speed_opt_success = "error" not in speed_optimization
            self._record_test_result(
                "execution_speed_optimization",
                speed_opt_success,
                "Execution speed optimization completed" if speed_opt_success else f"Speed optimization failed: {speed_optimization.get('error', 'Unknown error')}"
            )
            
            # Test performance report
            print("🧪 Testing execution performance report...")
            performance_report = await self.execution_optimizer.get_execution_performance_report(days=30)
            report_success = "error" not in performance_report
            
            self._record_test_result(
                "execution_performance_report",
                report_success,
                "Execution performance report generated" if report_success else f"Report failed: {performance_report.get('error', 'Unknown error')}"
            )
            
            # Test network performance analysis
            print("🧪 Testing network performance analysis...")
            network_analysis = await self.execution_optimizer.get_network_performance_analysis()
            network_success = "error" not in network_analysis
            
            self._record_test_result(
                "network_performance_analysis",
                network_success,
                "Network performance analysis completed" if network_success else f"Network analysis failed: {network_analysis.get('error', 'Unknown error')}"
            )
            
        except Exception as e:
            logger.error(f"❌ Execution optimization test failed: {e}")
            self._record_test_result("execution_optimization", False, f"Execution optimization test failed: {e}")
    
    async def _test_integration(self) -> None:
        """Test integration between all components."""
        print("\n🔗 Testing Component Integration")
        print("-" * 50)
        
        try:
            if not self.performance_manager:
                print("⚠️ Performance manager not available, skipping integration tests")
                return
            
            # Test performance dashboard
            print("🧪 Testing performance dashboard...")
            dashboard = await self.performance_manager.get_performance_dashboard()
            dashboard_success = "error" not in dashboard and "user_wallet" in dashboard
            
            self._record_test_result(
                "performance_dashboard",
                dashboard_success,
                "Performance dashboard generated successfully" if dashboard_success else f"Dashboard failed: {dashboard.get('error', 'Unknown error')}"
            )
            
            # Test trade optimization
            print("🧪 Testing next trade optimization...")
            trade_optimization = await self.performance_manager.optimize_next_trade(
                strategy_name="momentum",
                token_symbol="DOGE",
                trade_value_usd=Decimal("750"),
                urgency="high"
            )
            
            opt_success = "error" not in trade_optimization
            self._record_test_result(
                "trade_optimization",
                opt_success,
                "Trade optimization completed successfully" if opt_success else f"Trade optimization failed: {trade_optimization.get('error', 'Unknown error')}"
            )
            
            # Store integration data
            if dashboard_success:
                self.performance_data["dashboard"] = dashboard
            if opt_success:
                self.performance_data["trade_optimization"] = trade_optimization
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            self._record_test_result("integration", False, f"Integration test failed: {e}")
    
    async def _test_complete_trading_workflow(self) -> None:
        """Test complete end-to-end trading workflow."""
        print("\n🎯 Testing Complete Trading Workflow")
        print("-" * 50)
        
        try:
            if not self.performance_manager:
                print("⚠️ Performance manager not available, skipping workflow test")
                return
            
            # Test trading session start
            print("🧪 Testing trading session start...")
            session_result = await self.performance_manager.start_trading_session(
                strategy_name="grid_trading",
                token_symbol="SHIB",
                target_profit_usd=Decimal("50"),
                max_loss_usd=Decimal("20"),
                priority=ExecutionPriority.NORMAL,
                network=NetworkType.ETHEREUM
            )
            
            session_success = session_result.get("success", False)
            session_id = session_result.get("session_id")
            
            self._record_test_result(
                "trading_session_start",
                session_success,
                f"Trading session started: {session_id}" if session_success else f"Failed to start session: {session_result.get('error', 'Unknown error')}"
            )
            
            if session_success and session_id:
                # Test trade entry recording
                print("🧪 Testing trade entry recording...")
                entry_result = await self.performance_manager.record_trade_entry(
                    session_id=session_id,
                    entry_price=Decimal("0.000025"),
                    entry_amount=Decimal("2000000"),
                    gas_fee_usd=Decimal("8.50"),
                    execution_time_seconds=12.3
                )
                
                entry_success = entry_result.get("success", False)
                self._record_test_result(
                    "trade_entry_recording",
                    entry_success,
                    "Trade entry recorded successfully" if entry_success else f"Failed to record entry: {entry_result.get('error', 'Unknown error')}"
                )
                
                # Simulate some processing time
                await asyncio.sleep(1)
                
                # Test trade exit recording
                print("🧪 Testing trade exit recording...")
                exit_result = await self.performance_manager.record_trade_exit(
                    session_id=session_id,
                    exit_price=Decimal("0.000028"),
                    exit_amount=Decimal("2000000"),
                    gas_fee_usd=Decimal("7.80"),
                    execution_time_seconds=9.7
                )
                
                exit_success = exit_result.get("success", False)
                self._record_test_result(
                    "trade_exit_recording",
                    exit_success,
                    "Trade exit recorded and session completed" if exit_success else f"Failed to record exit: {exit_result.get('error', 'Unknown error')}"
                )
                
                # Store workflow data
                if exit_success:
                    self.performance_data["complete_workflow"] = exit_result
            
        except Exception as e:
            logger.error(f"❌ Complete workflow test failed: {e}")
            self._record_test_result("complete_workflow", False, f"Complete workflow test failed: {e}")
    
    def _record_test_result(self, test_name: str, success: bool, message: str) -> None:
        """Record test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {message}")
    
    async def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        try:
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r["success"]])
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Categorize test results
            categories = {
                "initialization": [r for r in self.test_results if "init" in r["test_name"]],
                "profit_optimization": [r for r in self.test_results if any(keyword in r["test_name"] for keyword in ["profit", "trade_entry", "trade_exit", "strategy"])],
                "gas_optimization": [r for r in self.test_results if "gas" in r["test_name"]],
                "execution_optimization": [r for r in self.test_results if "execution" in r["test_name"] or "network" in r["test_name"]],
                "integration": [r for r in self.test_results if any(keyword in r["test_name"] for keyword in ["integration", "dashboard", "workflow"])]
            }
            
            category_results = {}
            for category, tests in categories.items():
                if tests:
                    category_passed = len([t for t in tests if t["success"]])
                    category_total = len(tests)
                    category_results[category] = {
                        "passed": category_passed,
                        "total": category_total,
                        "success_rate": (category_passed / category_total * 100) if category_total > 0 else 0,
                        "status": "PASSED" if category_passed == category_total else "PARTIAL" if category_passed > 0 else "FAILED"
                    }
            
            # Generate recommendations
            recommendations = []
            
            if success_rate == 100:
                recommendations.extend([
                    "🎉 All Phase 5A.1 components are working perfectly!",
                    "✅ Ready for production use with personal trading",
                    "🚀 Consider proceeding to Phase 5A.2: 24/7 Reliability"
                ])
            elif success_rate >= 80:
                recommendations.extend([
                    "✅ Phase 5A.1 is mostly functional",
                    "⚠️ Address the failed tests before production use",
                    "🔧 Review error messages for specific issues"
                ])
            else:
                recommendations.extend([
                    "❌ Phase 5A.1 needs significant fixes",
                    "🔧 Focus on initialization and core functionality",
                    "📋 Review component dependencies and setup"
                ])
            
            # Determine overall status
            if success_rate == 100:
                overall_status = "COMPLETE"
            elif success_rate >= 80:
                overall_status = "MOSTLY_COMPLETE"
            elif success_rate >= 50:
                overall_status = "PARTIAL"
            else:
                overall_status = "FAILED"
            
            summary = {
                "overall_status": overall_status,
                "success_rate": round(success_rate, 1),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "category_results": category_results,
                "detailed_results": self.test_results,
                "performance_data": self.performance_data,
                "recommendations": recommendations,
                "test_completed_at": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate test summary: {e}")
            return {"error": str(e), "status": "error"}
    
    def print_test_summary(self, summary: Dict[str, Any]) -> None:
        """Print formatted test summary."""
        print("\n" + "=" * 70)
        print("🧪 PHASE 5A.1 TEST SUMMARY")
        print("=" * 70)
        
        overall_status = summary.get("overall_status", "UNKNOWN")
        success_rate = summary.get("success_rate", 0)
        
        status_icons = {
            "COMPLETE": "🎉",
            "MOSTLY_COMPLETE": "✅",
            "PARTIAL": "⚠️",
            "FAILED": "❌"
        }
        
        status_icon = status_icons.get(overall_status, "❓")
        
        print(f"\n{status_icon} OVERALL STATUS: {overall_status}")
        print(f"📊 Success Rate: {success_rate}%")
        print(f"📈 Tests: {summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)} passed")
        
        # Print category results
        print(f"\n📋 CATEGORY BREAKDOWN:")
        category_results = summary.get("category_results", {})
        
        for category, results in category_results.items():
            status = results["status"]
            status_icon = "✅" if status == "PASSED" else "⚠️" if status == "PARTIAL" else "❌"
            
            print(f"   {status_icon} {category.replace('_', ' ').title()}: "
                  f"{results['passed']}/{results['total']} passed ({results['success_rate']:.1f}%)")
        
        # Print recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        recommendations = summary.get("recommendations", [])
        for rec in recommendations:
            print(f"   {rec}")
        
        # Print detailed failures if any
        failed_tests = [r for r in summary.get("detailed_results", []) if not r["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['message']}")
        
        print("\n" + "=" * 70)


async def main():
    """Main testing function."""
    print("🤖 DEX Sniper Pro - Phase 5A.1 Complete Testing Suite")
    print("🎯 Testing: Trading Performance Optimization")
    print("=" * 70)
    
    # Create and run test suite
    test_suite = Phase5A1TestSuite()
    
    try:
        # Run complete test suite
        test_summary = await test_suite.run_complete_test_suite()
        
        # Print results
        test_suite.print_test_summary(test_summary)
        
        # Determine exit status
        overall_status = test_summary.get("overall_status", "FAILED")
        
        if overall_status == "COMPLETE":
            print("🎉 Phase 5A.1 testing completed successfully!")
            print("✅ All trading performance optimization components are working correctly")
            print("🚀 Ready for Phase 5A.2: 24/7 Reliability & Uptime")
        elif overall_status == "MOSTLY_COMPLETE":
            print("✅ Phase 5A.1 testing mostly successful!")
            print("⚠️ Minor issues detected - review failed tests")
            print("🔧 Fix remaining issues before proceeding")
        else:
            print("❌ Phase 5A.1 testing revealed issues")
            print("🔧 Review and fix failed components before proceeding")
            return False
        
        return True
        
    except Exception as e:
        print(f"💥 Testing suite encountered an error: {e}")
        logger.error(f"Test suite error: {e}")
        return False


if __name__ == "__main__":
    """Run the Phase 5A.1 test suite."""
    try:
        success = asyncio.run(main())
        if success:
            print("\n✅ Testing completed successfully")
        else:
            print("\n❌ Testing completed with issues")
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as error:
        print(f"\n💥 Testing failed: {error}")
        import traceback
        traceback.print_exc()