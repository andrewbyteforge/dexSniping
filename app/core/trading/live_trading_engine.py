"""
Live Trading Engine - Phase 4B Integration
File: app/core/trading/live_trading_engine.py
Class: LiveTradingEngine
Methods: initialize_live_connections, execute_live_trade, monitor_blockchain_events

Enhanced trading engine with live blockchain connectivity replacing mock data
with real DEX integration and wallet management for actual profit generation.
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import os

from app.core.blockchain.network_manager import NetworkManager, NetworkType, get_network_manager
from app.core.dex.live_dex_integration import LiveDEXIntegration, DEXProtocol, get_live_dex_integration
from app.core.trading.trading_engine import (
    TradingEngine, TradingMode, StrategyType, OrderIntent, 
    TradingSignal, ExecutionResult, TradingConfiguration
)
from app.core.exceptions import TradingError, NetworkError, InsufficientFundsError
from app.utils.logger import setup_logger, get_trading_logger, get_performance_logger, get_trading_logger, get_performance_logger

logger = setup_logger(__name__, "trading")


@dataclass
class LiveTradingConfiguration:
    """Live trading configuration with blockchain settings."""
    # Inherit from base configuration
    base_config: TradingConfiguration
    
    # Blockchain-specific settings
    default_network: NetworkType
    preferred_dexes: List[DEXProtocol]
    wallet_private_key: str
    wallet_address: str
    
    # Gas and transaction settings
    max_gas_price_gwei: int
    gas_price_strategy: str  # "fast", "standard", "safe"
    transaction_timeout_seconds: int
    
    # Risk management
    max_slippage_percent: Decimal
    min_liquidity_usd: Decimal
    enable_mev_protection: bool
    
    @classmethod
    def from_environment(cls) -> 'LiveTradingConfiguration':
        """Create configuration from environment variables."""
        base_config = TradingConfiguration.default()
        
        return cls(
            base_config=base_config,
            default_network=NetworkType(os.getenv("DEFAULT_NETWORK", "ethereum")),
            preferred_dexes=[
                DEXProtocol.UNISWAP_V2,
                DEXProtocol.SUSHISWAP
            ],
            wallet_private_key=os.getenv("TRADING_WALLET_PRIVATE_KEY", ""),
            wallet_address=os.getenv("TRADING_WALLET_ADDRESS", ""),
            max_gas_price_gwei=int(os.getenv("MAX_GAS_PRICE_GWEI", "100")),
            gas_price_strategy=os.getenv("GAS_PRICE_STRATEGY", "standard"),
            transaction_timeout_seconds=int(os.getenv("TRANSACTION_TIMEOUT", "300")),
            max_slippage_percent=Decimal(os.getenv("MAX_SLIPPAGE_PERCENT", "3.0")),
            min_liquidity_usd=Decimal(os.getenv("MIN_LIQUIDITY_USD", "10000")),
            enable_mev_protection=os.getenv("ENABLE_MEV_PROTECTION", "true").lower() == "true"
        )


@dataclass
class LiveMarketConditions:
    """Live market conditions from blockchain."""
    network_type: NetworkType
    current_gas_price_gwei: Decimal
    network_congestion: str  # "low", "medium", "high"
    block_time_seconds: float
    pending_transactions: int
    arbitrage_opportunities: int
    total_dex_liquidity_usd: Decimal
    last_updated: datetime = field(default_factory=datetime.utcnow)


class LiveTradingEngine(TradingEngine):
    """
    Enhanced trading engine with live blockchain integration.
    
    Connects to real blockchain networks, executes actual trades on DEXes,
    and manages live wallet interactions for profit generation.
    """
    
    def __init__(self, config: LiveTradingConfiguration):
        """Initialize live trading engine."""
        # Initialize base trading engine
        super().__init__(config.default_network)
        
        # Live trading configuration
        self.live_config = config
        self.network_manager = get_network_manager()
        self.live_dex = get_live_dex_integration(self.network_manager)
        
        # Live trading state
        self.active_networks: Dict[NetworkType, bool] = {}
        self.market_conditions: Dict[NetworkType, LiveMarketConditions] = {}
        self.live_positions: Dict[str, Dict[str, Any]] = {}
        self.blockchain_monitors: Dict[NetworkType, asyncio.Task] = {}
        
        # Performance tracking
        self.live_trades_executed = 0
        self.total_profit_usd = Decimal("0")
        self.gas_fees_paid_usd = Decimal("0")
        
    async def initialize_live_connections(self) -> bool:
        """Initialize connections to live blockchain networks."""
        try:
            logger.info("🚀 Initializing live blockchain connections...")
            
            # Validate configuration
            if not self.live_config.wallet_private_key:
                raise TradingError("Wallet private key not configured")
            
            if not self.live_config.wallet_address:
                raise TradingError("Wallet address not configured")
            
            # Connect to primary network
            primary_network = self.live_config.default_network
            logger.info(f"🔗 Connecting to primary network: {primary_network.value}")
            
            success = await self.network_manager.connect_to_network(primary_network)
            if not success:
                raise NetworkError(f"Failed to connect to {primary_network.value}")
            
            self.active_networks[primary_network] = True
            
            # Initialize market conditions
            await self._update_market_conditions(primary_network)
            
            # Start blockchain monitoring
            await self._start_blockchain_monitoring(primary_network)
            
            # Verify wallet access
            await self._verify_wallet_access(primary_network)
            
            # Connect to additional networks
            additional_networks = [
                NetworkType.POLYGON,
                NetworkType.BSC,
                NetworkType.ARBITRUM
            ]
            
            for network in additional_networks:
                if network != primary_network:
                    try:
                        success = await self.network_manager.connect_to_network(network)
                        if success:
                            self.active_networks[network] = True
                            await self._update_market_conditions(network)
                            logger.info(f"✅ Connected to {network.value}")
                        else:
                            logger.warning(f"⚠️ Failed to connect to {network.value}")
                    except Exception as e:
                        logger.warning(f"⚠️ {network.value} connection failed: {e}")
            
            logger.info(f"🎯 Live trading engine initialized with {len(self.active_networks)} networks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize live connections: {e}")
            raise TradingError(f"Live initialization failed: {e}")
    
    async def _verify_wallet_access(self, network_type: NetworkType) -> bool:
        """Verify wallet access and balances."""
        try:
            logger.info(f"🔐 Verifying wallet access on {network_type.value}")
            
            # Check native token balance
            native_balance = await self.network_manager.get_native_balance(
                network_type, self.live_config.wallet_address
            )
            
            logger.info(f"💰 Native balance: {native_balance} {network_type.value}")
            
            # Ensure minimum balance for gas
            min_native_balance = Decimal("0.001")  # Minimum for gas fees
            if native_balance < min_native_balance:
                logger.warning(f"⚠️ Low native balance: {native_balance}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Wallet verification failed: {e}")
            return False
    
    async def _update_market_conditions(self, network_type: NetworkType) -> None:
        """Update live market conditions for a network."""
        try:
            # Get current gas prices
            gas_prices = await self.network_manager.estimate_gas_price(network_type)
            current_gas_gwei = Decimal(str(gas_prices["standard"]))
            
            # Determine network congestion
            max_gas = self.live_config.max_gas_price_gwei
            if current_gas_gwei > max_gas * 0.8:
                congestion = "high"
            elif current_gas_gwei > max_gas * 0.4:
                congestion = "medium"
            else:
                congestion = "low"
            
            # Get network config for block time
            network_config = await self.network_manager.get_network_config(network_type)
            
            # Update market conditions
            self.market_conditions[network_type] = LiveMarketConditions(
                network_type=network_type,
                current_gas_price_gwei=current_gas_gwei,
                network_congestion=congestion,
                block_time_seconds=network_config.block_time_seconds,
                pending_transactions=len(self.live_dex.pending_transactions),
                arbitrage_opportunities=0,  # Will be updated by strategy engine
                total_dex_liquidity_usd=Decimal("1000000")  # Placeholder
            )
            
            logger.debug(f"📊 Updated market conditions for {network_type.value}: Gas {current_gas_gwei} Gwei")
            
        except Exception as e:
            logger.error(f"❌ Failed to update market conditions: {e}")
    
    async def _start_blockchain_monitoring(self, network_type: NetworkType) -> None:
        """Start monitoring blockchain events."""
        try:
            if network_type in self.blockchain_monitors:
                return  # Already monitoring
            
            # Create monitoring task
            monitor_task = asyncio.create_task(
                self._blockchain_monitor_loop(network_type)
            )
            self.blockchain_monitors[network_type] = monitor_task
            
            logger.info(f"👀 Started blockchain monitoring for {network_type.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start blockchain monitoring: {e}")
    
    async def _blockchain_monitor_loop(self, network_type: NetworkType) -> None:
        """Blockchain monitoring loop."""
        while True:
            try:
                # Update market conditions every 30 seconds
                await self._update_market_conditions(network_type)
                
                # Check pending transactions
                await self._check_pending_transactions()
                
                # Look for arbitrage opportunities
                await self._scan_arbitrage_opportunities(network_type)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Blockchain monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _check_pending_transactions(self) -> None:
        """Check status of pending transactions."""
        try:
            for tx_hash in list(self.live_dex.pending_transactions.keys()):
                updated_txn = await self.live_dex.check_transaction_status(tx_hash)
                
                if updated_txn and updated_txn.status in ["confirmed", "failed"]:
                    # Transaction completed
                    if updated_txn.status == "confirmed":
                        logger.info(f"✅ Transaction confirmed: {tx_hash[:10]}...")
                        self.live_trades_executed += 1
                        
                        # Update profit tracking
                        # (Simplified - in production, calculate actual profit)
                        estimated_profit = updated_txn.output_amount * Decimal("0.01")  # 1% profit
                        self.total_profit_usd += estimated_profit
                        
                    else:
                        logger.warning(f"❌ Transaction failed: {tx_hash[:10]}...")
                    
                    # Remove from pending
                    del self.live_dex.pending_transactions[tx_hash]
                    
        except Exception as e:
            logger.error(f"❌ Failed to check pending transactions: {e}")
    
    async def _scan_arbitrage_opportunities(self, network_type: NetworkType) -> None:
        """Scan for arbitrage opportunities."""
        try:
            # Get supported DEXes for this network
            supported_dexes = await self.live_dex.get_supported_dexes(network_type)
            
            if len(supported_dexes) < 2:
                return  # Need at least 2 DEXes for arbitrage
            
            # Common arbitrage pairs
            arbitrage_pairs = [
                ("0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),  # USDC/WETH
                ("0xdAC17F958D2ee523a2206206994597C13D831ec7", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),  # USDT/WETH
            ]
            
            for token0, token1 in arbitrage_pairs:
                try:
                    # Get quotes from different DEXes
                    quotes = []
                    for dex in supported_dexes[:2]:  # Check first 2 DEXes
                        quote = await self.live_dex.get_live_swap_quote(
                            network_type=network_type,
                            dex_protocol=dex,
                            input_token_address=token0,
                            output_token_address=token1,
                            input_amount=Decimal("100")  # Test with 100 tokens
                        )
                        if quote:
                            quotes.append((dex, quote))
                    
                    # Check for arbitrage opportunity
                    if len(quotes) >= 2:
                        quote1 = quotes[0][1]
                        quote2 = quotes[1][1]
                        
                        price_diff = abs(quote1.price_per_token - quote2.price_per_token)
                        avg_price = (quote1.price_per_token + quote2.price_per_token) / 2
                        
                        if avg_price > 0:
                            arbitrage_percent = (price_diff / avg_price) * 100
                            
                            if arbitrage_percent > 1:  # 1% minimum arbitrage
                                logger.info(f"🎯 Arbitrage opportunity: {arbitrage_percent:.2f}% on {network_type.value}")
                                
                                # Generate arbitrage signal
                                await self._generate_arbitrage_signal(
                                    network_type, quotes[0], quotes[1], arbitrage_percent
                                )
                
                except Exception as e:
                    logger.debug(f"⚠️ Arbitrage scan error for pair: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to scan arbitrage opportunities: {e}")
    
    async def _generate_arbitrage_signal(
        self,
        network_type: NetworkType,
        quote1: tuple,
        quote2: tuple,
        profit_percent: Decimal
    ) -> None:
        """Generate arbitrage trading signal."""
        try:
            dex1, q1 = quote1
            dex2, q2 = quote2
            
            # Determine which is cheaper to buy from
            if q1.price_per_token < q2.price_per_token:
                buy_dex, buy_quote = dex1, q1
                sell_dex, sell_quote = dex2, q2
            else:
                buy_dex, buy_quote = dex2, q2
                sell_dex, sell_quote = dex1, q1
            
            # Create arbitrage signal
            signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                strategy_type=StrategyType.ARBITRAGE,
                token_address=buy_quote.input_token.address,
                symbol=buy_quote.input_token.symbol,
                intent=OrderIntent.BUY,
                confidence=min(0.95, profit_percent / 10),  # Higher profit = higher confidence
                suggested_amount=Decimal("100"),  # Start with small amount
                reasoning=f"Arbitrage: Buy on {buy_dex.value} at {buy_quote.price_per_token:.6f}, sell on {sell_dex.value} at {sell_quote.price_per_token:.6f} ({profit_percent:.2f}% profit)",
                expires_at=datetime.utcnow() + timedelta(minutes=2)  # Short expiry for arbitrage
            )
            
            # Add to active signals
            self.active_signals.append(signal)
            
            logger.info(f"📈 Generated arbitrage signal: {profit_percent:.2f}% profit opportunity")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate arbitrage signal: {e}")
    
    async def execute_live_trade(
        self,
        signal: TradingSignal,
        network_type: Optional[NetworkType] = None
    ) -> ExecutionResult:
        """Execute a live trade on the blockchain."""
        try:
            logger.info(f"🔄 Executing live trade: {signal.symbol} {signal.intent.value}")
            
            # Use default network if not specified
            if not network_type:
                network_type = self.live_config.default_network
            
            # Verify network is connected
            if not self.active_networks.get(network_type, False):
                raise TradingError(f"Not connected to {network_type.value}")
            
            # Check market conditions
            market_conditions = self.market_conditions.get(network_type)
            if not market_conditions:
                raise TradingError(f"No market data for {network_type.value}")
            
            # Check if gas price is acceptable
            if market_conditions.current_gas_price_gwei > self.live_config.max_gas_price_gwei:
                raise TradingError(f"Gas price too high: {market_conditions.current_gas_price_gwei} Gwei")
            
            # Determine output token (for now, use USDC)
            usdc_addresses = {
                NetworkType.ETHEREUM: "0xA0b86a33E6441b7ebbe665C7E9F0E5D3e8a50E9e",
                NetworkType.POLYGON: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                NetworkType.BSC: "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
            }
            
            output_token_address = usdc_addresses.get(network_type)
            if not output_token_address:
                raise TradingError(f"No USDC address for {network_type.value}")
            
            # Get best quote across all supported DEXes
            best_quote = None
            best_dex = None
            
            for dex in self.live_config.preferred_dexes:
                try:
                    quote = await self.live_dex.get_live_swap_quote(
                        network_type=network_type,
                        dex_protocol=dex,
                        input_token_address=signal.token_address,
                        output_token_address=output_token_address,
                        input_amount=signal.suggested_amount,
                        slippage_tolerance=self.live_config.max_slippage_percent / 100
                    )
                    
                    if quote and (not best_quote or quote.output_amount > best_quote.output_amount):
                        best_quote = quote
                        best_dex = dex
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get quote from {dex.value}: {e}")
            
            if not best_quote:
                raise TradingError("No valid quotes available")
            
            # Check liquidity
            if best_quote.total_fee_usd > signal.suggested_amount * Decimal("0.1"):  # Max 10% fees
                raise TradingError("Fees too high for trade size")
            
            logger.info(f"💱 Best quote: {best_quote.output_amount} from {best_dex.value}")
            
            # Execute the swap
            swap_result = await self.live_dex.execute_live_swap(
                network_type=network_type,
                quote=best_quote,
                wallet_private_key=self.live_config.wallet_private_key,
                wallet_address=self.live_config.wallet_address
            )
            
            if not swap_result:
                raise TradingError("Swap execution failed")
            
            # Create execution result
            execution_result = ExecutionResult(
                trade_id=str(uuid.uuid4()),
                success=True,
                transaction_hash=swap_result.transaction_hash,
                executed_amount=best_quote.input_amount,
                execution_price=best_quote.price_per_token,
                gas_used=best_quote.gas_estimate,
                fees_paid=best_quote.total_fee_usd,
                slippage=Decimal("0"),  # Will be updated when transaction confirms
                execution_time=0.0  # Placeholder
            )
            
            logger.info(f"✅ Live trade executed: {swap_result.transaction_hash}")
            return execution_result
            
        except Exception as e:
            logger.error(f"❌ Live trade execution failed: {e}")
            return ExecutionResult(
                trade_id=str(uuid.uuid4()),
                success=False,
                transaction_hash=None,
                executed_amount=Decimal("0"),
                execution_price=Decimal("0"),
                gas_used=0,
                fees_paid=Decimal("0"),
                slippage=Decimal("0"),
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def get_live_trading_status(self) -> Dict[str, Any]:
        """Get comprehensive live trading status."""
        try:
            # Get network statuses
            network_statuses = {}
            for network_type, is_active in self.active_networks.items():
                if is_active:
                    status = await self.network_manager.check_network_health(network_type)
                    market_conditions = self.market_conditions.get(network_type)
                    
                    network_statuses[network_type.value] = {
                        "connected": status.is_connected,
                        "latest_block": status.latest_block,
                        "gas_price_gwei": float(status.gas_price_gwei),
                        "response_time_ms": status.response_time_ms,
                        "congestion": market_conditions.network_congestion if market_conditions else "unknown",
                        "pending_transactions": market_conditions.pending_transactions if market_conditions else 0
                    }
            
            # Get wallet balances
            wallet_balances = {}
            for network_type in self.active_networks.keys():
                try:
                    balance = await self.network_manager.get_native_balance(
                        network_type, self.live_config.wallet_address
                    )
                    wallet_balances[network_type.value] = float(balance)
                except Exception as e:
                    wallet_balances[network_type.value] = 0.0
            
            # Performance metrics
            total_signals = len(self.active_signals)
            avg_confidence = sum(s.confidence for s in self.active_signals) / max(1, total_signals)
            
            return {
                "status": "live_trading_active",
                "mode": self.live_config.base_config.trading_mode.value,
                "networks": network_statuses,
                "wallet": {
                    "address": self.live_config.wallet_address,
                    "balances": wallet_balances
                },
                "trading_performance": {
                    "trades_executed": self.live_trades_executed,
                    "total_profit_usd": float(self.total_profit_usd),
                    "gas_fees_paid_usd": float(self.gas_fees_paid_usd),
                    "active_signals": total_signals,
                    "avg_signal_confidence": avg_confidence
                },
                "risk_management": {
                    "max_position_size": float(self.live_config.base_config.max_position_size),
                    "max_daily_loss": float(self.live_config.base_config.max_daily_loss),
                    "max_slippage_percent": float(self.live_config.max_slippage_percent),
                    "max_gas_price_gwei": self.live_config.max_gas_price_gwei
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get live trading status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def shutdown_live_trading(self) -> None:
        """Shutdown live trading and cleanup resources."""
        try:
            logger.info("🛑 Shutting down live trading engine...")
            
            # Cancel blockchain monitoring tasks
            for network_type, task in self.blockchain_monitors.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Stop network health monitoring
            await self.network_manager.stop_health_monitoring()
            
            # Disconnect from all networks
            await self.network_manager.disconnect_all()
            
            # Clear state
            self.active_networks.clear()
            self.market_conditions.clear()
            self.blockchain_monitors.clear()
            
            logger.info("✅ Live trading engine shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


# Global instance
_live_trading_engine: Optional[LiveTradingEngine] = None


def get_live_trading_engine() -> LiveTradingEngine:
    """Get the global live trading engine instance."""
    global _live_trading_engine
    if _live_trading_engine is None:
        config = LiveTradingConfiguration.from_environment()
        _live_trading_engine = LiveTradingEngine(config)
    return _live_trading_engine


async def initialize_live_trading() -> bool:
    """Initialize the live trading engine."""
    try:
        engine = get_live_trading_engine()
        return await engine.initialize_live_connections()
    except Exception as e:
        logger.error(f"❌ Failed to initialize live trading: {e}")
        return False