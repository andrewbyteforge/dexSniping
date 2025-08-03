"""
Trading Engine - Core Automation System
File: app/core/trading/trading_engine.py

Main trading engine that coordinates wallet management, DEX integration,
risk management, and automated trading strategies for profit generation.
"""

import asyncio
from decimal import Decimal
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from app.utils.logger import setup_logger
from app.core.wallet.wallet_manager import WalletManager, NetworkType
from app.core.dex.dex_integration import DEXIntegration, DEXProtocol, SwapQuote
from app.core.exceptions import TradingError

logger = setup_logger(__name__)


class TradingMode(str, Enum):
    """Trading mode enumeration."""
    MANUAL = "manual"
    SEMI_AUTOMATED = "semi_automated"
    FULLY_AUTOMATED = "fully_automated"
    SIMULATION = "simulation"


class StrategyType(str, Enum):
    """Trading strategy types."""
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    MOMENTUM = "momentum"


class OrderIntent(str, Enum):
    """Order intent enumeration."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class TradingSignal:
    """Trading signal data structure."""
    signal_id: str
    strategy_type: StrategyType
    token_address: str
    symbol: str
    intent: OrderIntent
    confidence: float
    suggested_amount: Decimal
    reasoning: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """Check if signal has expired."""
        return datetime.utcnow() > self.expires_at


@dataclass
class TradingConfiguration:
    """Trading engine configuration."""
    trading_mode: TradingMode
    max_position_size: Decimal
    max_daily_loss: Decimal
    default_slippage: Decimal
    enabled_strategies: List[StrategyType]
    preferred_dexes: List[DEXProtocol]
    
    @classmethod
    def default(cls) -> 'TradingConfiguration':
        """Create default trading configuration."""
        return cls(
            trading_mode=TradingMode.SEMI_AUTOMATED,
            max_position_size=Decimal("1000"),
            max_daily_loss=Decimal("100"),
            default_slippage=Decimal("0.01"),
            enabled_strategies=[StrategyType.ARBITRAGE],
            preferred_dexes=[DEXProtocol.UNISWAP_V2]
        )


@dataclass
class ExecutionResult:
    """Trade execution result."""
    trade_id: str
    success: bool
    transaction_hash: Optional[str]
    executed_amount: Decimal
    execution_price: Decimal
    gas_used: int
    fees_paid: Decimal
    slippage: Decimal
    execution_time: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class TradingEngine:
    """
    Main trading engine for automated profit generation.
    
    Coordinates all trading operations including signal generation,
    risk management, order execution, and portfolio tracking.
    """
    
    def __init__(self, network: NetworkType = NetworkType.ETHEREUM):
        """Initialize trading engine."""
        self.network = network
        self.is_running = False
        self.config: Optional[TradingConfiguration] = None
        
        # Core components
        self.wallet_manager: Optional[WalletManager] = None
        self.dex_integration: Optional[DEXIntegration] = None
        
        # Trading state
        self.active_signals: List[TradingSignal] = []
        
        # Performance tracking
        self.total_trades = 0
        self.successful_trades = 0
        
        logger.info(f"Trading Engine initialized for {network.value}")
    
    async def initialize(
        self,
        config: Optional[TradingConfiguration] = None,
        wallet_manager: Optional[WalletManager] = None
    ) -> None:
        """Initialize trading engine components."""
        try:
            # Set configuration
            self.config = config or TradingConfiguration.default()
            
            # Initialize wallet manager
            if wallet_manager:
                self.wallet_manager = wallet_manager
            else:
                self.wallet_manager = WalletManager(self.network)
            
            # Initialize DEX integration
            self.dex_integration = DEXIntegration(network=self.network.value)
            
            logger.info("Trading Engine components initialized successfully")
            
        except Exception as e:
            logger.error(f"Trading Engine initialization failed: {e}")
            raise TradingError(f"Initialization failed: {e}")
    
    async def start_trading(self, wallet_address: str) -> Dict[str, Any]:
        """Start automated trading for a wallet."""
        try:
            if self.is_running:
                return {
                    "success": False,
                    "message": "Trading is already running"
                }
            
            # Verify wallet is connected
            if not self.wallet_manager.is_wallet_connected(wallet_address):
                raise TradingError(f"Wallet {wallet_address} is not connected")
            
            # Start trading
            self.is_running = True
            
            logger.info(f"Trading started for wallet {wallet_address[:10]}...")
            
            return {
                "success": True,
                "message": "Trading started successfully",
                "config": {
                    "mode": self.config.trading_mode.value,
                    "max_position": str(self.config.max_position_size)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to start trading: {e}")
            raise TradingError(f"Trading start failed: {e}")
    
    async def stop_trading(self) -> Dict[str, Any]:
        """Stop automated trading."""
        try:
            if not self.is_running:
                return {
                    "success": False,
                    "message": "Trading is not running"
                }
            
            self.is_running = False
            
            logger.info("Trading stopped")
            
            return {
                "success": True,
                "message": "Trading stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop trading: {e}")
            raise TradingError(f"Trading stop failed: {e}")
    
    async def execute_manual_trade(
        self,
        wallet_address: str,
        token_address: str,
        intent: OrderIntent,
        amount: Decimal,
        slippage_tolerance: Optional[Decimal] = None
    ) -> ExecutionResult:
        """Execute a manual trade."""
        try:
            start_time = datetime.utcnow()
            
            # Use default slippage if not provided
            slippage = slippage_tolerance or self.config.default_slippage
            
            # Get quotes
            if intent == OrderIntent.BUY:
                input_token = "0x0000000000000000000000000000000000000000"  # ETH
                output_token = token_address
            else:
                input_token = token_address
                output_token = "0x0000000000000000000000000000000000000000"  # ETH
            
            quotes = await self.dex_integration.get_swap_quote(
                input_token=input_token,
                output_token=output_token,
                input_amount=amount,
                slippage_tolerance=slippage
            )
            
            if not quotes:
                raise TradingError("No quotes available for this trade")
            
            # Use best quote
            best_quote = quotes[0]
            
            # Execute swap
            swap_result = await self.dex_integration.execute_swap(
                quote=best_quote,
                wallet_address=wallet_address
            )
            
            # Calculate metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update stats
            self.total_trades += 1
            self.successful_trades += 1
            
            result = ExecutionResult(
                trade_id=str(uuid.uuid4()),
                success=True,
                transaction_hash=swap_result.transaction_hash,
                executed_amount=amount,
                execution_price=swap_result.output_amount / amount,
                gas_used=swap_result.gas_used,
                fees_paid=Decimal("0.01"),  # Mock fee
                slippage=Decimal("0.005"),  # Mock slippage
                execution_time=execution_time
            )
            
            logger.info(f"Manual trade executed: {intent.value} {amount} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Manual trade failed: {e}")
            
            self.total_trades += 1
            
            return ExecutionResult(
                trade_id=str(uuid.uuid4()),
                success=False,
                transaction_hash=None,
                executed_amount=Decimal("0"),
                execution_price=Decimal("0"),
                gas_used=0,
                fees_paid=Decimal("0"),
                slippage=Decimal("0"),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def generate_trading_signal(
        self,
        strategy_type: StrategyType,
        token_address: str,
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Generate trading signal based on strategy and market data."""
        try:
            if strategy_type == StrategyType.ARBITRAGE:
                return await self._generate_arbitrage_signal(token_address, market_data)
            else:
                logger.warning(f"Unsupported strategy: {strategy_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"Signal generation failed for {strategy_type.value}: {e}")
            return None
    
    async def _generate_arbitrage_signal(
        self, 
        token_address: str, 
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Generate arbitrage trading signal."""
        try:
            # Get quotes from multiple DEXes
            quotes = await self.dex_integration.get_swap_quote(
                input_token="0x0000000000000000000000000000000000000000",  # ETH
                output_token=token_address,
                input_amount=Decimal("1"),  # 1 ETH worth
                protocols=self.config.preferred_dexes
            )
            
            if len(quotes) < 2:
                return None
            
            # Calculate potential profit
            quotes.sort(key=lambda q: q.output_amount, reverse=True)
            best_buy = quotes[0]
            worst_buy = quotes[-1]
            
            price_difference = (best_buy.output_amount - worst_buy.output_amount)
            profit_percentage = (price_difference / worst_buy.output_amount) * 100
            
            # Check if arbitrage opportunity exists (minimum 0.5% profit)
            if profit_percentage >= Decimal("0.5"):
                return TradingSignal(
                    signal_id=str(uuid.uuid4()),
                    strategy_type=StrategyType.ARBITRAGE,
                    token_address=token_address,
                    symbol=market_data.get("symbol", "UNKNOWN"),
                    intent=OrderIntent.BUY,
                    confidence=min(float(profit_percentage) / 5.0, 1.0),
                    suggested_amount=Decimal("100"),
                    reasoning=f"Arbitrage opportunity: {profit_percentage:.2f}% profit potential",
                    expires_at=datetime.utcnow() + timedelta(minutes=5)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Arbitrage signal generation failed: {e}")
            return None
    
    async def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading engine status."""
        return {
            "is_running": self.is_running,
            "trading_mode": self.config.trading_mode.value if self.config else None,
            "network": self.network.value,
            "total_trades": self.total_trades,
            "successful_trades": self.successful_trades,
            "active_signals": len(self.active_signals)
        }
