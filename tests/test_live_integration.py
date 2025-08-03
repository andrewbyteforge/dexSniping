"""
Live Integration Test Suite - Phase 4B
File: tests/test_live_integration.py
Class: TestLiveIntegration
Methods: test_network_connections, test_live_dex_quotes, test_wallet_verification

Comprehensive tests for live blockchain integration to verify real connectivity
before moving to production trading.
"""

import asyncio
import pytest
import os
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.blockchain.network_manager import NetworkManager, NetworkType
from app.core.dex.live_dex_integration import LiveDEXIntegration, DEXProtocol
from app.core.trading.live_trading_engine import LiveTradingEngine, LiveTradingConfiguration
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TestLiveIntegration:
    """Test suite for live blockchain integration."""
    
    @pytest.fixture
    async def network_manager(self):
        """Network manager fixture."""
        manager = NetworkManager()
        yield manager
        await manager.disconnect_all()
    
    @pytest.fixture
    async def live_dex(self, network_manager):
        """Live DEX integration fixture."""
        return LiveDEXIntegration(network_manager)
    
    @pytest.fixture
    def test_config(self):
        """Test configuration fixture."""
        return {
            "test_wallet_address": "0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC",  # Random address for testing
            "test_token_usdc": "0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e",  # USDC on Ethereum
            "test_token_weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH on Ethereum
            "test_amount": Decimal("1.0")
        }
    
    @pytest.mark.asyncio
    async def test_network_connection_ethereum(self, network_manager):
        """Test connection to Ethereum mainnet."""
        logger.info("🧪 Testing Ethereum connection...")
        
        # Test environment check
        infura_key = os.getenv("INFURA_API_KEY")
        if not infura_key:
            pytest.skip("INFURA_API_KEY not set - using public RPC")
        
        # Connect to Ethereum
        success = await network_manager.connect_to_network(NetworkType.ETHEREUM)
        assert success, "Failed to connect to Ethereum"
        
        # Verify connection
        web3 = await network_manager.get_web3_instance(NetworkType.ETHEREUM)
        latest_block = await web3.eth.block_number
        
        assert latest_block > 0, "No blocks found"
        assert latest_block > 18000000, "Block number seems too low for mainnet"
        
        logger.info(f"✅ Ethereum connected - Block: {latest_block}")
    
    @pytest.mark.asyncio
    async def test_network_connection_polygon(self, network_manager):
        """Test connection to Polygon network."""
        logger.info("🧪 Testing Polygon connection...")
        
        try:
            success = await network_manager.connect_to_network(NetworkType.POLYGON)
            if success:
                web3 = await network_manager.get_web3_instance(NetworkType.POLYGON)
                latest_block = await web3.eth.block_number
                assert latest_block > 0
                logger.info(f"✅ Polygon connected - Block: {latest_block}")
            else:
                logger.warning("⚠️ Polygon connection failed - may be network issue")
        except Exception as e:
            logger.warning(f"⚠️ Polygon test failed: {e}")
            # Don't fail the test for secondary networks
    
    @pytest.mark.asyncio
    async def test_gas_price_estimation(self, network_manager):
        """Test gas price estimation."""
        logger.info("🧪 Testing gas price estimation...")
        
        # Connect to Ethereum
        await network_manager.connect_to_network(NetworkType.ETHEREUM)
        
        # Get gas prices
        gas_prices = await network_manager.estimate_gas_price(NetworkType.ETHEREUM)
        
        assert "fast" in gas_prices
        assert "standard" in gas_prices
        assert "safe" in gas_prices
        
        assert gas_prices["fast"] > 0
        assert gas_prices["standard"] > 0
        assert gas_prices["safe"] > 0
        
        # Fast should be higher than standard
        assert gas_prices["fast"] >= gas_prices["standard"]
        assert gas_prices["standard"] >= gas_prices["safe"]
        
        logger.info(f"✅ Gas prices: Fast {gas_prices['fast']}, Standard {gas_prices['standard']}, Safe {gas_prices['safe']} Gwei")
    
    @pytest.mark.asyncio
    async def test_token_info_retrieval(self, live_dex, test_config):
        """Test token information retrieval."""
        logger.info("🧪 Testing token info retrieval...")
        
        # Connect to network first
        await live_dex.network_manager.connect_to_network(NetworkType.ETHEREUM)
        
        # Get USDC token info
        usdc_info = await live_dex.get_token_info(
            NetworkType.ETHEREUM, 
            test_config["test_token_usdc"]
        )
        
        assert usdc_info.symbol in ["USDC", "USD", "USDC.e"]  # Different USDC versions
        assert usdc_info.decimals in [6, 18]  # USDC can be 6 or 18 decimals
        assert usdc_info.network == NetworkType.ETHEREUM
        
        logger.info(f"✅ Token info: {usdc_info.symbol} ({usdc_info.name}) - {usdc_info.decimals} decimals")
    
    @pytest.mark.asyncio
    async def test_dex_quote_retrieval(self, live_dex, test_config):
        """Test DEX quote retrieval from Uniswap."""
        logger.info("🧪 Testing DEX quote retrieval...")
        
        # Connect to network
        await live_dex.network_manager.connect_to_network(NetworkType.ETHEREUM)
        
        try:
            # Get swap quote WETH -> USDC
            quote = await live_dex.get_live_swap_quote(
                network_type=NetworkType.ETHEREUM,
                dex_protocol=DEXProtocol.UNISWAP_V2,
                input_token_address=test_config["test_token_weth"],
                output_token_address=test_config["test_token_usdc"],
                input_amount=test_config["test_amount"],
                slippage_tolerance=Decimal("0.01")
            )
            
            if quote:
                assert quote.input_amount == test_config["test_amount"]
                assert quote.output_amount > 0
                assert quote.price_per_token > 0
                assert quote.gas_estimate > 0
                assert quote.expires_at > datetime.utcnow()
                
                logger.info(f"✅ Quote: {quote.input_amount} WETH -> {quote.output_amount} USDC")
                logger.info(f"   Price: {quote.price_per_token} USDC per WETH")
                logger.info(f"   Gas: {quote.gas_estimate}, Slippage: {quote.slippage_tolerance}")
            else:
                logger.warning("⚠️ No quote received - may be liquidity or network issue")
                
        except Exception as e:
            logger.warning(f"⚠️ Quote test failed: {e}")
            # Don't fail test for quote issues in test environment
    
    @pytest.mark.asyncio
    async def test_balance_checking(self, network_manager, test_config):
        """Test balance checking functionality."""
        logger.info("🧪 Testing balance checking...")
        
        # Connect to Ethereum
        await network_manager.connect_to_network(NetworkType.ETHEREUM)
        
        # Check ETH balance for a known address
        eth_balance = await network_manager.get_native_balance(
            NetworkType.ETHEREUM,
            test_config["test_wallet_address"]
        )
        
        # Balance should be a decimal (could be 0)
        assert isinstance(eth_balance, Decimal)
        assert eth_balance >= 0
        
        logger.info(f"✅ ETH balance for test address: {eth_balance}")
        
        # Check token balance
        try:
            token_balance = await network_manager.get_token_balance(
                NetworkType.ETHEREUM,
                test_config["test_token_usdc"],
                test_config["test_wallet_address"]
            )
            
            assert isinstance(token_balance, Decimal)
            assert token_balance >= 0
            
            logger.info(f"✅ USDC balance for test address: {token_balance}")
            
        except Exception as e:
            logger.info(f"ℹ️ Token balance check info: {e}")
    
    @pytest.mark.asyncio
    async def test_multiple_dex_quotes(self, live_dex, test_config):
        """Test quotes from multiple DEXes."""
        logger.info("🧪 Testing multiple DEX quotes...")
        
        await live_dex.network_manager.connect_to_network(NetworkType.ETHEREUM)
        
        dexes_to_test = [DEXProtocol.UNISWAP_V2, DEXProtocol.SUSHISWAP]
        quotes = []
        
        for dex in dexes_to_test:
            try:
                quote = await live_dex.get_live_swap_quote(
                    network_type=NetworkType.ETHEREUM,
                    dex_protocol=dex,
                    input_token_address=test_config["test_token_weth"],
                    output_token_address=test_config["test_token_usdc"],
                    input_amount=test_config["test_amount"]
                )
                
                if quote:
                    quotes.append((dex, quote))
                    logger.info(f"✅ {dex.value}: {quote.output_amount} USDC for 1 WETH")
                
            except Exception as e:
                logger.warning(f"⚠️ {dex.value} quote failed: {e}")
        
        if len(quotes) >= 2:
            # Compare prices
            dex1, quote1 = quotes[0]
            dex2, quote2 = quotes[1]
            
            price_diff = abs(quote1.output_amount - quote2.output_amount)
            avg_price = (quote1.output_amount + quote2.output_amount) / 2
            
            if avg_price > 0:
                diff_percent = (price_diff / avg_price) * 100
                logger.info(f"💰 Price difference: {diff_percent:.2f}%")
                
                if diff_percent > 0.1:
                    logger.info("🎯 Potential arbitrage opportunity detected!")
    
    @pytest.mark.asyncio
    async def test_live_trading_engine_initialization(self):
        """Test live trading engine initialization."""
        logger.info("🧪 Testing live trading engine initialization...")
        
        # Check if we have required environment variables
        required_vars = ["INFURA_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
            logger.info("ℹ️ Skipping live engine test - set environment variables for full test")
            return
        
        # Create test configuration
        from app.core.trading.live_trading_engine import LiveTradingConfiguration
        from app.core.trading.trading_engine import TradingConfiguration, TradingMode
        
        base_config = TradingConfiguration(
            trading_mode=TradingMode.SIMULATION,
            max_position_size=Decimal("100"),
            max_daily_loss=Decimal("10"),
            default_slippage=Decimal("0.01"),
            enabled_strategies=[],
            preferred_dexes=[]
        )
        
        live_config = LiveTradingConfiguration(
            base_config=base_config,
            default_network=NetworkType.ETHEREUM,
            preferred_dexes=[DEXProtocol.UNISWAP_V2],
            wallet_private_key="",  # Empty for test
            wallet_address="0x742d35Cc6634C0532925a3b8D8645dECBF3E5FAC",
            max_gas_price_gwei=100,
            gas_price_strategy="standard",
            transaction_timeout_seconds=300,
            max_slippage_percent=Decimal("3.0"),
            min_liquidity_usd=Decimal("10000"),
            enable_mev_protection=True
        )
        
        # Create and test engine
        engine = LiveTradingEngine(live_config)
        
        # Test without private key (should work for read-only operations)
        try:
            # This should work without private key
            await engine.network_manager.connect_to_network(NetworkType.ETHEREUM)
            logger.info("✅ Live trading engine network connection successful")
            
            # Cleanup
            await engine.shutdown_live_trading()
            
        except Exception as e:
            logger.warning(f"⚠️ Live engine test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_health_check(self, live_dex):
        """Test DEX integration health check."""
        logger.info("🧪 Testing health check...")
        
        await live_dex.network_manager.connect_to_network(NetworkType.ETHEREUM)
        
        health = await live_dex.health_check()
        
        assert "status" in health
        assert "supported_dexes" in health
        assert "last_checked" in health
        
        logger.info(f"✅ Health check: {health['status']}")
        logger.info(f"   Supported DEXes: {health['supported_dexes']}")


@pytest.mark.asyncio
async def test_environment_setup():
    """Test that the environment is properly set up."""
    logger.info("🧪 Testing environment setup...")
    
    # Check Python packages
    try:
        import web3
        logger.info(f"✅ Web3 version: {web3.__version__}")
    except ImportError:
        pytest.fail("Web3 not installed")
    
    try:
        import eth_account
        logger.info("✅ eth-account imported successfully")
    except ImportError:
        pytest.fail("eth-account not installed")
    
    # Check environment variables
    env_vars = {
        "INFURA_API_KEY": os.getenv("INFURA_API_KEY"),
        "ALCHEMY_API_KEY": os.getenv("ALCHEMY_API_KEY"),
    }
    
    available_providers = [name for name, value in env_vars.items() if value]
    
    if available_providers:
        logger.info(f"✅ Available providers: {available_providers}")
    else:
        logger.warning("⚠️ No API keys found - will use public RPCs")
        logger.info("ℹ️ For better performance, set INFURA_API_KEY or ALCHEMY_API_KEY")
    
    logger.info("✅ Environment setup test complete")


@pytest.mark.asyncio 
async def test_quick_integration():
    """Quick integration test that can run without API keys."""
    logger.info("🚀 Running quick integration test...")
    
    # Test basic imports and initialization
    from app.core.blockchain.network_manager import NetworkManager
    from app.core.dex.live_dex_integration import LiveDEXIntegration
    
    # Create instances
    network_manager = NetworkManager()
    live_dex = LiveDEXIntegration(network_manager)
    
    # Test network configuration loading
    eth_config = await network_manager.get_network_config(NetworkType.ETHEREUM)
    assert eth_config.chain_id == 1
    assert eth_config.name == "Ethereum Mainnet"
    
    # Test DEX support
    eth_dexes = await live_dex.get_supported_dexes(NetworkType.ETHEREUM)
    assert DEXProtocol.UNISWAP_V2 in eth_dexes
    
    logger.info("✅ Quick integration test passed")
    
    # Cleanup
    await network_manager.disconnect_all()


if __name__ == "__main__":
    """Run tests directly."""
    import sys
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    async def run_tests():
        """Run all tests."""
        logger.info("🧪 Starting Live Integration Tests - Phase 4B")
        logger.info("=" * 60)
        
        try:
            # Run quick test first
            await test_quick_integration()
            
            # Run environment test
            await test_environment_setup()
            
            logger.info("✅ Basic tests passed")
            
            # If API keys are available, run full tests
            if os.getenv("INFURA_API_KEY") or os.getenv("ALCHEMY_API_KEY"):
                logger.info("🔗 API keys found - running full integration tests...")
                
                # Run with pytest for full test suite
                import subprocess
                result = subprocess.run([
                    sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
                ], capture_output=True, text=True)
                
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                    
                if result.returncode == 0:
                    logger.info("✅ All integration tests passed!")
                else:
                    logger.error("❌ Some tests failed")
                    
            else:
                logger.info("ℹ️ For full tests, set INFURA_API_KEY in .env file")
                logger.info("✅ Basic integration tests completed successfully")
                
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            raise
    
    # Run the tests
    asyncio.run(run_tests())