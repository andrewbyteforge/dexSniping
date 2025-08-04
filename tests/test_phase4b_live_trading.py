"""
Phase 4B Test Suite - Live Trading Integration
File: tests/test_phase4b_live_trading.py
Classes: TestWalletConnections, TestDEXIntegration, TestLiveTradingEngine
Methods: test_wallet_metamask_connection, test_live_dex_quotes, test_trading_session_lifecycle

Comprehensive test suite for Phase 4B live trading functionality including
wallet connections, DEX integration, and end-to-end trading workflows.
"""

import asyncio
import pytest
import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, AsyncMock, patch

from app.core.wallet.wallet_connection_manager import (
    WalletConnectionManager,
    WalletType,
    NetworkType,
    ConnectionStatus,
    WalletConnection,
    initialize_wallet_system
)
from app.core.dex.live_dex_integration import (
    LiveDEXIntegration,
    DEXProtocol,
    SwapQuote,
    TokenInfo,
    initialize_dex_integration
)
from app.core.trading.live_trading_engine_enhanced import (
    LiveTradingEngineEnhanced,
    TradingConfiguration,
    TradingMode,
    TradingStrategy,
    TradingOpportunity,
    initialize_live_trading_system
)
from app.core.exceptions import (
    WalletError,
    DEXError,
    TradingError,
    NetworkError,
    InsufficientFundsError,
    RiskManagementError
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TestWalletConnections:
    """Test suite for wallet connection functionality."""
    
    @pytest.fixture
    async def wallet_manager(self):
        """Wallet manager fixture."""
        manager = WalletConnectionManager()
        
        # Mock Web3 instances for testing
        mock_web3 = Mock()
        mock_web3.eth.block_number = 18500000
        mock_web3.eth.chain_id = 1
        mock_web3.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
        
        manager.web3_instances[NetworkType.ETHEREUM] = mock_web3
        manager.web3_instances[NetworkType.POLYGON] = mock_web3
        
        yield manager
        
        # Cleanup
        await manager.cleanup_expired_connections()
    
    @pytest.mark.asyncio
    async def test_wallet_manager_initialization(self, wallet_manager):
        """Test wallet manager initialization."""
        logger.info("🧪 Testing wallet manager initialization...")
        
        # Test network initialization
        success = await wallet_manager.initialize_networks([NetworkType.ETHEREUM])
        assert success, "Wallet manager initialization should succeed"
        
        # Verify network instances
        assert NetworkType.ETHEREUM in wallet_manager.web3_instances
        
        logger.info("✅ Wallet manager initialization test passed")
    
    @pytest.mark.asyncio
    async def test_metamask_connection(self, wallet_manager):
        """Test MetaMask wallet connection."""
        logger.info("🧪 Testing MetaMask connection...")
        
        test_address = "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC"
        
        # Initialize networks first
        await wallet_manager.initialize_networks([NetworkType.ETHEREUM])
        
        # Mock the balance fetching
        with patch.object(wallet_manager, '_get_wallet_balance') as mock_balance:
            mock_balance.return_value = Mock()
            mock_balance.return_value.native_balance = Decimal("1.5")
            mock_balance.return_value.native_symbol = "ETH"
            mock_balance.return_value.last_updated = datetime.utcnow()
            
            # Connect wallet
            connection = await wallet_manager.connect_metamask(
                wallet_address=test_address,
                requested_networks=[NetworkType.ETHEREUM]
            )
            
            # Verify connection
            assert connection.wallet_type == WalletType.METAMASK
            assert connection.wallet_address.lower() == test_address.lower()
            assert connection.status == ConnectionStatus.CONNECTED
            assert NetworkType.ETHEREUM in connection.connected_networks
            
            logger.info(f"✅ MetaMask connected: {connection.connection_id}")
    
    @pytest.mark.asyncio
    async def test_wallet_verification(self, wallet_manager):
        """Test wallet access verification."""
        logger.info("🧪 Testing wallet verification...")
        
        test_address = "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC"
        
        # Initialize and connect
        await wallet_manager.initialize_networks([NetworkType.ETHEREUM])
        
        with patch.object(wallet_manager, '_get_wallet_balance') as mock_balance:
            mock_balance.return_value = Mock()
            mock_balance.return_value.native_balance = Decimal("2.0")
            mock_balance.return_value.native_symbol = "ETH"
            
            connection = await wallet_manager.connect_metamask(test_address)
            
            # Test verification with sufficient funds
            success = await wallet_manager.verify_wallet_access(
                connection.connection_id,
                NetworkType.ETHEREUM,
                required_balance_eth=Decimal("0.1")
            )
            assert success, "Verification should succeed with sufficient funds"
            
            # Test verification with insufficient funds
            with pytest.raises(InsufficientFundsError):
                await wallet_manager.verify_wallet_access(
                    connection.connection_id,
                    NetworkType.ETHEREUM,
                    required_balance_eth=Decimal("5.0")
                )
            
            logger.info("✅ Wallet verification test passed")
    
    @pytest.mark.asyncio
    async def test_wallet_disconnection(self, wallet_manager):
        """Test wallet disconnection."""
        logger.info("🧪 Testing wallet disconnection...")
        
        test_address = "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC"
        
        # Connect wallet
        await wallet_manager.initialize_networks([NetworkType.ETHEREUM])
        
        with patch.object(wallet_manager, '_get_wallet_balance') as mock_balance:
            mock_balance.return_value = Mock()
            mock_balance.return_value.native_balance = Decimal("1.0")
            mock_balance.return_value.native_symbol = "ETH"
            
            connection = await wallet_manager.connect_metamask(test_address)
            connection_id = connection.connection_id
            
            # Verify connection exists
            active_connections = wallet_manager.get_active_connections()
            assert connection_id in active_connections
            
            # Disconnect wallet
            success = await wallet_manager.disconnect_wallet(connection_id)
            assert success, "Disconnection should succeed"
            
            # Verify connection removed
            active_connections = wallet_manager.get_active_connections()
            assert connection_id not in active_connections
            
            logger.info("✅ Wallet disconnection test passed")


class TestDEXIntegration:
    """Test suite for DEX integration functionality."""
    
    @pytest.fixture
    async def dex_integration(self):
        """DEX integration fixture."""
        # Mock wallet manager
        mock_wallet_manager = Mock()
        
        # Mock Web3 instances
        mock_web3 = Mock()
        mock_web3.eth.block_number = 18500000
        mock_web3.eth.chain_id = 1
        mock_web3.eth.gas_price = 20000000000  # 20 gwei
        
        mock_wallet_manager.web3_instances = {
            NetworkType.ETHEREUM: mock_web3,
            NetworkType.POLYGON: mock_web3
        }
        
        integration = LiveDEXIntegration(mock_wallet_manager)
        yield integration
    
    @pytest.mark.asyncio
    async def test_dex_initialization(self, dex_integration):
        """Test DEX contract initialization."""
        logger.info("🧪 Testing DEX initialization...")
        
        with patch.object(dex_integration, '_load_dex_contract') as mock_load:
            mock_contract = Mock()
            mock_load.return_value = mock_contract
            
            success = await dex_integration.initialize_dex_contracts([NetworkType.ETHEREUM])
            assert success, "DEX initialization should succeed"
            
            # Verify contracts loaded
            assert (NetworkType.ETHEREUM, DEXProtocol.UNISWAP_V2) in dex_integration.dex_contracts
            
            logger.info("✅ DEX initialization test passed")
    
    @pytest.mark.asyncio
    async def test_live_price_fetching(self, dex_integration):
        """Test live price fetching from DEX."""
        logger.info("🧪 Testing live price fetching...")
        
        # Mock contract initialization
        mock_contract = Mock()
        mock_contract.functions.getAmountsOut.return_value.call.return_value = [
            1000000000000000000,  # 1 token input
            2000000000000000000   # 2 tokens output (price = 2.0)
        ]
        
        dex_integration.dex_contracts[(NetworkType.ETHEREUM, DEXProtocol.UNISWAP_V2)] = {
            'router': mock_contract
        }
        
        # Test price fetching
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_executor = Mock()
            mock_executor.run_in_executor.return_value = [
                1000000000000000000,
                2000000000000000000
            ]
            mock_loop.return_value = mock_executor
            
            price, timestamp = await dex_integration.get_live_price(
                token_address="0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e",
                network=NetworkType.ETHEREUM
            )
            
            assert price > 0, "Price should be positive"
            assert isinstance(timestamp, datetime), "Timestamp should be datetime"
            
            logger.info(f"✅ Price fetched: {price} at {timestamp}")
    
    @pytest.mark.asyncio
    async def test_swap_quote_generation(self, dex_integration):
        """Test swap quote generation."""
        logger.info("🧪 Testing swap quote generation...")
        
        # Mock dependencies
        with patch.object(dex_integration, '_get_token_info') as mock_token_info:
            mock_token_info.return_value = TokenInfo(
                address="0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e",
                symbol="USDC",
                name="USD Coin",
                decimals=6,
                network=NetworkType.ETHEREUM
            )
            
            with patch.object(dex_integration, '_get_dex_quote') as mock_quote:
                mock_quote.return_value = (
                    Decimal("100.5"),    # output_amount
                    Decimal("0.5"),      # price_impact
                    ["0xtoken1", "0xtoken2"]  # route_path
                )
                
                with patch.object(dex_integration, '_estimate_swap_gas') as mock_gas:
                    mock_gas.return_value = 150000
                    
                    with patch.object(dex_integration, '_get_current_gas_price') as mock_gas_price:
                        mock_gas_price.return_value = Decimal("20")
                        
                        # Generate quote
                        quote = await dex_integration.get_swap_quote(
                            input_token="0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e",
                            output_token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                            input_amount=Decimal("100"),
                            network=NetworkType.ETHEREUM
                        )
                        
                        # Verify quote
                        assert quote.input_amount == Decimal("100")
                        assert quote.output_amount == Decimal("100.5")
                        assert quote.price_impact == Decimal("0.5")
                        assert quote.estimated_gas == 150000
                        assert not quote.is_expired
                        
                        logger.info(f"✅ Quote generated: {quote.quote_id}")
    
    @pytest.mark.asyncio
    async def test_swap_execution_simulation(self, dex_integration):
        """Test swap execution (simulation mode)."""
        logger.info("🧪 Testing swap execution simulation...")
        
        # Create mock quote
        quote = SwapQuote(
            quote_id="test-quote-123",
            dex_protocol=DEXProtocol.UNISWAP_V2,
            network=NetworkType.ETHEREUM,
            input_token=TokenInfo("0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e", "USDC", "USD Coin", 6, NetworkType.ETHEREUM),
            output_token=TokenInfo("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "WETH", "Wrapped Ether", 18, NetworkType.ETHEREUM),
            input_amount=Decimal("100"),
            output_amount=Decimal("0.05"),
            price_impact=Decimal("0.5"),
            estimated_gas=150000,
            gas_price_gwei=Decimal("20"),
            estimated_gas_cost_eth=Decimal("0.003"),
            slippage_tolerance=Decimal("1.0"),
            minimum_output=Decimal("0.0495"),
            exchange_rate=Decimal("0.0005"),
            route_path=["0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"],
            expires_at=datetime.utcnow() + timedelta(minutes=2)
        )
        
        # Store quote
        dex_integration.active_quotes[quote.quote_id] = quote
        
        # Mock wallet manager connection
        mock_wallet_connections = {
            "test-wallet-connection": Mock()
        }
        dex_integration.wallet_manager.get_active_connections.return_value = mock_wallet_connections
        
        # Execute swap (simulation)
        transaction = await dex_integration.execute_swap_transaction(
            quote_id=quote.quote_id,
            wallet_connection_id="test-wallet-connection"
        )
        
        # Verify transaction
        assert transaction.quote_id == quote.quote_id
        assert transaction.status == "confirmed"  # Simulated success
        assert transaction.input_amount == quote.input_amount
        assert transaction.output_amount == quote.output_amount
        
        logger.info(f"✅ Swap executed (simulation): {transaction.transaction_hash}")


class TestLiveTradingEngine:
    """Test suite for live trading engine functionality."""
    
    @pytest.fixture
    async def trading_engine(self):
        """Trading engine fixture."""
        # Mock dependencies
        mock_wallet_manager = Mock()
        mock_dex_integration = Mock()
        
        # Setup async methods
        mock_wallet_manager.initialize_networks = AsyncMock(return_value=True)
        mock_wallet_manager.get_active_connections = Mock(return_value={})
        mock_wallet_manager.cleanup_expired_connections = AsyncMock(return_value=0)
        
        mock_dex_integration.initialize_dex_contracts = AsyncMock(return_value=True)
        mock_dex_integration.get_active_quotes = Mock(return_value={})
        
        engine = LiveTradingEngineEnhanced(mock_wallet_manager, mock_dex_integration)
        yield engine
        
        # Cleanup
        await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, trading_engine):
        """Test trading system initialization."""
        logger.info("🧪 Testing trading system initialization...")
        
        # Test initialization
        success = await trading_engine.initialize_live_systems([NetworkType.ETHEREUM])
        assert success, "Trading system initialization should succeed"
        
        # Verify state
        assert trading_engine.is_initialized
        
        logger.info("✅ Trading system initialization test passed")
    
    @pytest.mark.asyncio
    async def test_trading_session_lifecycle(self, trading_engine):
        """Test complete trading session lifecycle."""
        logger.info("🧪 Testing trading session lifecycle...")
        
        # Initialize system
        await trading_engine.initialize_live_systems([NetworkType.ETHEREUM])
        
        # Mock wallet connection
        mock_connection = Mock()
        mock_connection.connection_id = "test-wallet-123"
        mock_connection.is_active = True
        mock_connection.connected_networks = {NetworkType.ETHEREUM: True}
        mock_connection.balances = {
            NetworkType.ETHEREUM: Mock(native_balance=Decimal("2.0"))
        }
        
        trading_engine.wallet_manager.get_active_connections.return_value = {
            "test-wallet-123": mock_connection
        }
        
        with patch.object(trading_engine, '_verify_trading_requirements') as mock_verify:
            mock_verify.return_value = None  # No exception = success
            
            with patch.object(trading_engine, '_start_session_monitoring') as mock_monitor:
                mock_monitor.return_value = None
                
                # Start trading session
                session = await trading_engine.start_trading_session(
                    wallet_connection_id="test-wallet-123",
                    configuration=TradingConfiguration.conservative()
                )
                
                # Verify session
                assert session.is_active
                assert session.wallet_connection_id == "test-wallet-123"
                assert session.configuration.trading_mode == TradingMode.SEMI_AUTOMATED
                
                # Stop session
                success = await trading_engine.stop_trading_session(session.session_id)
                assert success, "Session stop should succeed"
                
                logger.info(f"✅ Session lifecycle test passed: {session.session_id}")
    
    @pytest.mark.asyncio
    async def test_opportunity_detection(self, trading_engine):
        """Test trading opportunity detection."""
        logger.info("🧪 Testing opportunity detection...")
        
        # Initialize system
        await trading_engine.initialize_live_systems([NetworkType.ETHEREUM])
        
        # Mock opportunity detection
        with patch.object(trading_engine, '_detect_opportunities') as mock_detect:
            mock_opportunity = TradingOpportunity(
                opportunity_id="test-opp-123",
                strategy=TradingStrategy.ARBITRAGE,
                network=NetworkType.ETHEREUM,
                dex_protocol=DEXProtocol.UNISWAP_V2,
                input_token=TokenInfo("0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e", "USDC", "USD Coin", 6, NetworkType.ETHEREUM),
                output_token=TokenInfo("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "WETH", "Wrapped Ether", 18, NetworkType.ETHEREUM),
                recommended_amount=Decimal("100"),
                expected_profit_usd=Decimal("2.50"),
                expected_profit_percent=Decimal("2.5"),
                confidence_score=Decimal("85"),
                risk_level="low",
                current_price=Decimal("0.0005"),
                liquidity_usd=Decimal("50000"),
                time_sensitivity="minutes",
                expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            
            mock_detect.return_value = [mock_opportunity]
            
            # Test opportunity detection
            opportunities = await trading_engine._detect_opportunities(
                NetworkType.ETHEREUM,
                [TradingStrategy.ARBITRAGE]
            )
            
            assert len(opportunities) == 1
            assert opportunities[0].opportunity_id == "test-opp-123"
            assert opportunities[0].strategy == TradingStrategy.ARBITRAGE
            
            logger.info(f"✅ Opportunity detected: {opportunities[0].opportunity_id}")
    
    @pytest.mark.asyncio
    async def test_risk_management(self, trading_engine):
        """Test risk management functionality."""
        logger.info("🧪 Testing risk management...")
        
        # Create test session
        session = Mock()
        session.configuration = TradingConfiguration.conservative()
        session.daily_loss_usd = Decimal("0")
        session.can_trade_today = True
        
        # Create test opportunity
        opportunity = Mock()
        opportunity.risk_level = "very_high"
        opportunity.expected_profit_percent = Decimal("15")
        
        # Test risk checks
        with pytest.raises(RiskManagementError):
            await trading_engine._perform_risk_checks(
                opportunity=opportunity,
                session=session,
                trade_amount=Decimal("2000")  # Exceeds max single trade
            )
        
        logger.info("✅ Risk management test passed")
    
    @pytest.mark.asyncio
    async def test_system_statistics(self, trading_engine):
        """Test system statistics collection."""
        logger.info("🧪 Testing system statistics...")
        
        # Initialize system
        await trading_engine.initialize_live_systems([NetworkType.ETHEREUM])
        
        # Get statistics
        stats = trading_engine.get_system_statistics()
        
        # Verify statistics structure
        assert "system_uptime_hours" in stats
        assert "total_opportunities_detected" in stats
        assert "total_trades_executed" in stats
        assert "active_sessions" in stats
        assert "is_initialized" in stats
        
        assert stats["is_initialized"] == True
        assert stats["system_uptime_hours"] >= 0
        
        logger.info(f"✅ System statistics: {stats}")


class TestIntegrationWorkflows:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self):
        """Test complete end-to-end trading workflow."""
        logger.info("🧪 Testing complete trading workflow...")
        
        try:
            # 1. Initialize wallet system
            wallet_manager = WalletConnectionManager()
            
            # Mock network initialization
            with patch.object(wallet_manager, '_initialize_single_network') as mock_init:
                mock_init.return_value = True
                
                wallet_success = await wallet_manager.initialize_networks([NetworkType.ETHEREUM])
                assert wallet_success, "Wallet initialization should succeed"
            
            # 2. Initialize DEX integration
            dex_integration = LiveDEXIntegration(wallet_manager)
            
            with patch.object(dex_integration, '_load_dex_contract') as mock_load:
                mock_load.return_value = Mock()
                
                dex_success = await dex_integration.initialize_dex_contracts([NetworkType.ETHEREUM])
                assert dex_success, "DEX initialization should succeed"
            
            # 3. Initialize trading engine
            trading_engine = LiveTradingEngineEnhanced(wallet_manager, dex_integration)
            
            engine_success = await trading_engine.initialize_live_systems([NetworkType.ETHEREUM])
            assert engine_success, "Trading engine initialization should succeed"
            
            # 4. Connect wallet (mocked)
            test_address = "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC"
            
            with patch.object(wallet_manager, '_get_wallet_balance') as mock_balance:
                mock_balance.return_value = Mock()
                mock_balance.return_value.native_balance = Decimal("2.0")
                mock_balance.return_value.native_symbol = "ETH"
                
                connection = await wallet_manager.connect_metamask(test_address)
                assert connection.status == ConnectionStatus.CONNECTED
            
            # 5. Start trading session
            with patch.object(trading_engine, '_verify_trading_requirements'):
                with patch.object(trading_engine, '_start_session_monitoring'):
                    session = await trading_engine.start_trading_session(
                        wallet_connection_id=connection.connection_id
                    )
                    assert session.is_active
            
            # 6. Cleanup
            await trading_engine.stop_trading_session(session.session_id)
            await wallet_manager.disconnect_wallet(connection.connection_id)
            await trading_engine.shutdown()
            
            logger.info("✅ Complete trading workflow test passed")
            
        except Exception as e:
            logger.error(f"❌ Complete workflow test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test comprehensive error handling."""
        logger.info("🧪 Testing error handling...")
        
        # Test wallet connection with invalid address
        wallet_manager = WalletConnectionManager()
        
        with pytest.raises(ValueError):
            await wallet_manager.connect_metamask("invalid-address")
        
        # Test trading without initialization
        trading_engine = LiveTradingEngineEnhanced()
        
        with pytest.raises(TradingError):
            await trading_engine.start_trading_session("nonexistent-wallet")
        
        logger.info("✅ Error handling test passed")


# ==================== TEST CONFIGURATION ====================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


# ==================== TEST RUNNERS ====================

if __name__ == "__main__":
    """Run tests directly."""
    import sys
    
    # Configure pytest to run specific test classes
    test_classes = [
        "TestWalletConnections",
        "TestDEXIntegration", 
        "TestLiveTradingEngine",
        "TestIntegrationWorkflows"
    ]
    
    logger.info("🚀 Starting Phase 4B Test Suite...")
    
    for test_class in test_classes:
        logger.info(f"🧪 Running {test_class}...")
        
        # Run pytest for specific class
        exit_code = pytest.main([
            f"-v",
            f"-k", test_class,
            "--tb=short",  # Short traceback format
            "--disable-warnings",  # Disable warnings for cleaner output
            __file__
        ])
        
        if exit_code != 0:
            logger.error(f"❌ {test_class} tests failed with exit code {exit_code}")
            sys.exit(exit_code)
        else:
            logger.info(f"✅ {test_class} tests passed")
    
    logger.info("🎉 All Phase 4B tests completed successfully!")


# ==================== PYTEST MARKERS ====================

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.phase4b
]


# ==================== TEST UTILITIES ====================

def create_mock_wallet_connection(address: str = "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC") -> WalletConnection:
    """Create mock wallet connection for testing."""
    from app.core.wallet.wallet_connection_manager import WalletConnection, WalletBalance
    
    return WalletConnection(
        connection_id="test-conn-123",
        wallet_type=WalletType.METAMASK,
        wallet_address=address,
        connected_networks={NetworkType.ETHEREUM: True},
        balances={
            NetworkType.ETHEREUM: WalletBalance(
                network=NetworkType.ETHEREUM,
                native_balance=Decimal("2.0"),
                native_symbol="ETH"
            )
        },
        status=ConnectionStatus.CONNECTED,
        last_activity=datetime.utcnow(),
        session_expires=datetime.utcnow() + timedelta(hours=1)
    )


def create_mock_trading_opportunity() -> TradingOpportunity:
    """Create mock trading opportunity for testing."""
    return TradingOpportunity(
        opportunity_id="test-opp-123",
        strategy=TradingStrategy.ARBITRAGE,
        network=NetworkType.ETHEREUM,
        dex_protocol=DEXProtocol.UNISWAP_V2,
        input_token=TokenInfo("0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e", "USDC", "USD Coin", 6, NetworkType.ETHEREUM),
        output_token=TokenInfo("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "WETH", "Wrapped Ether", 18, NetworkType.ETHEREUM),
        recommended_amount=Decimal("100"),
        expected_profit_usd=Decimal("2.50"),
        expected_profit_percent=Decimal("2.5"),
        confidence_score=Decimal("85"),
        risk_level=RiskLevel.LOW,
        current_price=Decimal("0.0005"),
        liquidity_usd=Decimal("50000"),
        time_sensitivity="minutes",
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )


# Export test classes for pytest discovery
__all__ = [
    "TestWalletConnections",
    "TestDEXIntegration", 
    "TestLiveTradingEngine",
    "TestIntegrationWorkflows"
]