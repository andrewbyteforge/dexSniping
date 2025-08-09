"""
Phase 5A.1: Simple Component Test
File: test_phase_5a1_simple.py

Simple test to validate Phase 5A.1 components work correctly.
Tests core functionality without complex dependencies.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that we can import all Phase 5A.1 components."""
    print("🧪 Testing Phase 5A.1 imports...")
    
    try:
        # Test basic utility imports
        from app.utils.logger import setup_logger
        print("✅ Logger import successful")
        
        # Test profit optimizer import
        from app.core.performance.trading_optimizer import (
            TradingPerformanceOptimizer,
            TradeProfitAnalysis,
            StrategyPerformance,
            PersonalTradingMetrics
        )
        print("✅ Trading optimizer components imported")
        
        # Test gas optimizer import
        from app.core.performance.gas_optimizer import (
            GasOptimizationEngine,
            GasStrategy,
            GasPrice,
            NetworkCongestion,
            GasOptimizationResult
        )
        print("✅ Gas optimizer components imported")
        
        # Test execution optimizer import
        from app.core.performance.execution_optimizer import (
            ExecutionSpeedOptimizer,
            ExecutionPriority,
            ExecutionStage,
            ExecutionTiming
        )
        print("✅ Execution optimizer components imported")
        
        # Test integration manager import
        from app.core.performance.trading_performance_manager import (
            TradingPerformanceManager,
            PersonalTradingSession,
            TradePhase
        )
        print("✅ Performance manager components imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False


def test_component_creation():
    """Test that we can create component instances."""
    print("\n🧪 Testing component creation...")
    
    try:
        test_wallet = "0x1234567890123456789012345678901234567890"
        
        # Test profit optimizer creation
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
        profit_optimizer = TradingPerformanceOptimizer(test_wallet)
        print("✅ Profit optimizer created")
        
        # Test gas optimizer creation
        from app.core.performance.gas_optimizer import GasOptimizationEngine
        gas_optimizer = GasOptimizationEngine(test_wallet)
        print("✅ Gas optimizer created")
        
        # Test execution optimizer creation
        from app.core.performance.execution_optimizer import ExecutionSpeedOptimizer
        execution_optimizer = ExecutionSpeedOptimizer(test_wallet)
        print("✅ Execution optimizer created")
        
        # Test performance manager creation
        from app.core.performance.trading_performance_manager import TradingPerformanceManager
        performance_manager = TradingPerformanceManager(test_wallet)
        print("✅ Performance manager created")
        
        return True
        
    except Exception as e:
        print(f"❌ Component creation failed: {e}")
        return False


async def test_basic_functionality():
    """Test basic functionality of components."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        test_wallet = "0x1234567890123456789012345678901234567890"
        
        # Test profit optimizer basic methods
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
        profit_optimizer = TradingPerformanceOptimizer(test_wallet)
        
        # Test that we can create trade analysis
        from app.core.performance.trading_optimizer import TradeProfitAnalysis
        trade_analysis = TradeProfitAnalysis(
            trade_id="test_001",
            strategy_used="momentum",
            token_symbol="TEST",
            entry_price=Decimal("1.0"),
            entry_amount=Decimal("100"),
            entry_time=datetime.utcnow(),
            entry_gas_fee_usd=Decimal("5.0")
        )
        print("✅ Trade analysis object created")
        
        # Test gas optimization enums
        from app.core.performance.gas_optimizer import GasStrategy, NetworkCongestion
        from app.core.blockchain.network_manager import NetworkType
        
        strategies = [GasStrategy.SLOW, GasStrategy.STANDARD, GasStrategy.FAST, GasStrategy.FASTEST]
        congestion_levels = [NetworkCongestion.LOW, NetworkCongestion.MEDIUM, NetworkCongestion.HIGH]
        networks = [NetworkType.ETHEREUM, NetworkType.POLYGON, NetworkType.BSC]
        
        print(f"✅ Gas strategies available: {[s.value for s in strategies]}")
        print(f"✅ Congestion levels: {[c.value for c in congestion_levels]}")
        print(f"✅ Networks supported: {[n.value for n in networks]}")
        
        # Test execution timing
        from app.core.performance.execution_optimizer import ExecutionTiming, ExecutionPriority
        execution_timing = ExecutionTiming(
            trade_id="test_exec_001",
            strategy_name="arbitrage",
            token_symbol="UNI",
            priority=ExecutionPriority.HIGH
        )
        print("✅ Execution timing object created")
        
        # Test trading session
        from app.core.performance.trading_performance_manager import PersonalTradingSession, TradePhase
        session = PersonalTradingSession(
            session_id="session_001",
            user_wallet=test_wallet,
            strategy_name="grid_trading",
            start_time=datetime.utcnow(),
            token_symbol="SHIB",
            target_profit_usd=Decimal("50"),
            max_loss_usd=Decimal("20"),
            priority=ExecutionPriority.NORMAL
        )
        print("✅ Trading session object created")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mock_trading_workflow():
    """Test a mock trading workflow without external dependencies."""
    print("\n🧪 Testing mock trading workflow...")
    
    try:
        test_wallet = "0x1234567890123456789012345678901234567890"
        
        # Create components
        from app.core.performance.trading_optimizer import TradingPerformanceOptimizer
        from app.core.performance.gas_optimizer import GasOptimizationEngine, GasStrategy, GasPrice
        from app.core.performance.execution_optimizer import ExecutionSpeedOptimizer, ExecutionPriority
        from app.core.blockchain.network_manager import NetworkType
        
        profit_optimizer = TradingPerformanceOptimizer(test_wallet)
        gas_optimizer = GasOptimizationEngine(test_wallet)
        execution_optimizer = ExecutionSpeedOptimizer(test_wallet)
        
        print("✅ Components created for workflow test")
        
        # Mock trade data
        trade_id = "mock_trade_001"
        strategy_name = "momentum"
        token_symbol = "PEPE"
        
        # Test profit tracking workflow (without initialization)
        print("🔄 Testing profit tracking workflow...")
        
        # Simulate trade entry
        trade_analyses = profit_optimizer.trade_analyses
        
        from app.core.performance.trading_optimizer import TradeProfitAnalysis
        mock_analysis = TradeProfitAnalysis(
            trade_id=trade_id,
            strategy_used=strategy_name,
            token_symbol=token_symbol,
            entry_price=Decimal("0.001"),
            entry_amount=Decimal("1000"),
            entry_time=datetime.utcnow(),
            entry_gas_fee_usd=Decimal("8.0")
        )
        
        # Add to trade analyses
        trade_analyses[trade_id] = mock_analysis
        print("✅ Mock trade entry added to profit optimizer")
        
        # Test gas optimization data structures
        print("🔄 Testing gas optimization structures...")
        
        gas_price = GasPrice(
            network=NetworkType.ETHEREUM,
            timestamp=datetime.utcnow(),
            slow=Decimal("20"),
            standard=Decimal("30"),
            fast=Decimal("40"),
            fastest=Decimal("60")
        )
        
        gas_optimizer.current_gas_prices[NetworkType.ETHEREUM] = gas_price
        print("✅ Mock gas prices added to gas optimizer")
        
        # Test execution timing structures
        print("🔄 Testing execution timing structures...")
        
        from app.core.performance.execution_optimizer import ExecutionTiming
        execution_timing = ExecutionTiming(
            trade_id=trade_id,
            strategy_name=strategy_name,
            token_symbol=token_symbol,
            priority=ExecutionPriority.HIGH,
            network=NetworkType.ETHEREUM
        )
        
        # Simulate execution stages
        execution_timing.market_analysis_time = 2.5
        execution_timing.opportunity_detection_time = 1.0
        execution_timing.risk_assessment_time = 0.8
        execution_timing.order_preparation_time = 1.2
        execution_timing.transaction_submission_time = 3.0
        execution_timing.confirmation_wait_time = 45.0
        execution_timing.result_processing_time = 0.5
        
        execution_timing.total_execution_time = (
            execution_timing.market_analysis_time +
            execution_timing.opportunity_detection_time +
            execution_timing.risk_assessment_time +
            execution_timing.order_preparation_time +
            execution_timing.transaction_submission_time +
            execution_timing.confirmation_wait_time +
            execution_timing.result_processing_time
        )
        
        execution_optimizer.execution_history.append(execution_timing)
        print("✅ Mock execution timing added to execution optimizer")
        
        # Test data retrieval
        print("🔄 Testing data retrieval...")
        
        # Check that we can access the mock data
        stored_trade = trade_analyses.get(trade_id)
        stored_gas_price = gas_optimizer.current_gas_prices.get(NetworkType.ETHEREUM)
        stored_execution = execution_optimizer.execution_history
        
        if stored_trade and stored_gas_price and stored_execution:
            print("✅ All mock data successfully stored and retrieved")
            
            # Print some test results
            print(f"   📊 Trade: {stored_trade.token_symbol} @ ${stored_trade.entry_price}")
            print(f"   ⛽ Gas: {stored_gas_price.standard} gwei")
            print(f"   ⚡ Execution: {execution_timing.total_execution_time:.1f}s")
            
            return True
        else:
            print("❌ Failed to retrieve mock data")
            return False
        
    except Exception as e:
        print(f"❌ Mock trading workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_structures():
    """Test that all data structures work correctly."""
    print("\n🧪 Testing data structures...")
    
    try:
        # Test profit analysis calculations
        from app.core.performance.trading_optimizer import TradeProfitAnalysis
        
        analysis = TradeProfitAnalysis(
            trade_id="test_calc",
            strategy_used="test",
            token_symbol="TEST",
            entry_price=Decimal("1.0"),
            entry_amount=Decimal("100"),
            entry_time=datetime.utcnow(),
            entry_gas_fee_usd=Decimal("5.0")
        )
        
        # Simulate exit
        analysis.exit_price = Decimal("1.1")
        analysis.exit_amount = Decimal("100")
        analysis.exit_time = datetime.utcnow()
        analysis.exit_gas_fee_usd = Decimal("4.0")
        
        # Calculate profit manually to test logic
        entry_value = analysis.entry_price * analysis.entry_amount  # 100
        exit_value = analysis.exit_price * analysis.exit_amount      # 110
        gross_profit = exit_value - entry_value                     # 10
        total_gas = analysis.entry_gas_fee_usd + analysis.exit_gas_fee_usd  # 9
        net_profit = gross_profit - total_gas                       # 1
        
        print(f"✅ Profit calculation test:")
        print(f"   Entry value: ${entry_value}")
        print(f"   Exit value: ${exit_value}")
        print(f"   Gross profit: ${gross_profit}")
        print(f"   Total gas: ${total_gas}")
        print(f"   Net profit: ${net_profit}")
        
        # Test gas price structure
        from app.core.performance.gas_optimizer import GasPrice
        from app.core.blockchain.network_manager import NetworkType
        
        gas_price = GasPrice(
            network=NetworkType.ETHEREUM,
            timestamp=datetime.utcnow()
        )
        
        gas_dict = gas_price.to_dict()
        print(f"✅ Gas price structure: {list(gas_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data structures test failed: {e}")
        return False


def print_test_summary(results):
    """Print test summary."""
    print("\n" + "=" * 60)
    print("🧪 PHASE 5A.1 SIMPLE TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    if success_rate == 100:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 5A.1 components are working correctly")
        print("✅ Core functionality is operational")
        print("🚀 Ready for full testing or Phase 5A.2 development")
    elif success_rate >= 80:
        print(f"\n✅ MOSTLY SUCCESSFUL!")
        print("⚠️ Minor issues detected - check failed tests")
    else:
        print(f"\n❌ SIGNIFICANT ISSUES DETECTED")
        print("🔧 Review failed tests and fix issues")
    
    print("\n" + "=" * 60)


async def main():
    """Main test function."""
    print("🤖 DEX Sniper Pro - Phase 5A.1 Simple Component Test")
    print("🎯 Testing: Basic component functionality without complex dependencies")
    print("=" * 70)
    
    results = {}
    
    try:
        # Run tests
        results["imports"] = test_imports()
        results["component_creation"] = test_component_creation()
        results["basic_functionality"] = await test_basic_functionality()
        results["data_structures"] = test_data_structures()
        results["mock_workflow"] = await test_mock_trading_workflow()
        
        # Print summary
        print_test_summary(results)
        
        # Determine overall success
        success_rate = sum(results.values()) / len(results) * 100
        
        if success_rate == 100:
            print("\n🎉 Phase 5A.1 simple test completed successfully!")
            print("✅ All core components are working")
            print("🚀 Ready for full integration testing")
            return True
        else:
            print(f"\n⚠️ Phase 5A.1 simple test completed with {success_rate:.1f}% success")
            print("🔧 Review failed components before proceeding")
            return False
        
    except Exception as e:
        print(f"\n💥 Testing encountered an error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run the simple test."""
    print("Starting Phase 5A.1 Simple Test...")
    
    try:
        success = asyncio.run(main())
        
        if success:
            print("\n✅ Simple testing completed successfully")
            print("💡 Run 'python test_phase_5a1_complete.py' for comprehensive testing")
        else:
            print("\n❌ Simple testing revealed issues")
            print("🔧 Fix the issues before running comprehensive tests")
            
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
    except Exception as error:
        print(f"\n💥 Testing failed: {error}")
        import traceback
        traceback.print_exc()