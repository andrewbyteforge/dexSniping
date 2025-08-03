"""
Auto Trading Bot
File: app/core/trading/auto_trader.py

Professional automated trading bot with AI-powered decision making,
risk management, and real-time execution capabilities.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from app.utils.logger import setup_logger
from app.core.exceptions import TradingError, InsufficientFundsError
from app.core.ai.risk_assessor import AIRiskAssessor
from app.core.trading.order_executor import OrderExecutor, Order, OrderSide, OrderType
from app.core.risk.position_sizer import PositionSizer
from app.core.risk.stop_loss_manager import StopLossManager

logger = setup_logger(__name__)


class TraderStatus(Enum):
    """Auto-trader status states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class TradeAction(Enum):
    """Trade action types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class TradingOpportunity:
    """Trading opportunity identified by AI."""
    token_address: str
    network: str
    symbol: str
    name: str
    current_price: float
    liquidity_usd: float
    risk_score: float
    confidence: float
    recommended_action: TradeAction
    profit_potential: float
    time_sensitivity: str
    ai_signals: Dict[str, Any]
    discovered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TradeExecution:
    """Trade execution record."""
    trade_id: str
    token_address: str
    network: str
    action: TradeAction
    amount_eth: float
    price_usd: float
    slippage_percent: float
    gas_fee_eth: float
    status: str
    transaction_hash: Optional[str]
    executed_at: datetime
    profit_loss: Optional[float] = None
    closed_at: Optional[datetime] = None


@dataclass
class TradingStatistics:
    """Trading performance statistics."""
    total_trades: int = 0
    profitable_trades: int = 0
    losing_trades: int = 0
    total_profit_loss: float = 0.0
    largest_profit: float = 0.0
    largest_loss: float = 0.0
    average_trade_size: float = 0.0
    success_rate: float = 0.0
    total_fees_paid: float = 0.0
    active_positions: int = 0
    total_volume: float = 0.0


class AutoTrader:
    """
    Professional automated trading bot with AI integration.
    
    Features:
    - AI-powered opportunity detection
    - Real-time risk assessment
    - Automated position sizing
    - Dynamic stop-loss management
    - Multi-network support
    - Comprehensive logging and statistics
    """
    
    def __init__(self):
        """Initialize auto-trader."""
        self.trader_id = str(uuid.uuid4())
        self.status = TraderStatus.STOPPED
        self.start_time: Optional[datetime] = None
        
        # Configuration
        self.config = {}
        self.enabled_networks: Set[str] = set()
        self.max_position_size = 0.1
        self.min_liquidity = 50000
        self.max_risk_score = 3.0
        self.profit_target_percent = 20.0
        self.stop_loss_percent = 10.0
        self.max_slippage_percent = 5.0
        self.cooldown_minutes = 5
        
        # Components
        self.risk_assessor: Optional[AIRiskAssessor] = None
        self.order_executor: Optional[OrderExecutor] = None
        self.position_sizer: Optional[PositionSizer] = None
        self.stop_loss_manager: Optional[StopLossManager] = None
        
        # State management
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[TradeExecution] = []
        self.statistics = TradingStatistics()
        self.last_trade_time: Optional[datetime] = None
        self.running = False
        
        logger.info(f"✅ AutoTrader initialized with ID: {self.trader_id}")
    
    async def initialize(self) -> bool:
        """Initialize auto-trader components."""
        try:
            logger.info("🚀 Initializing auto-trader components...")
            
            # Initialize AI components
            from app.core.ai.risk_assessor import AIRiskAssessor
            self.risk_assessor = AIRiskAssessor()
            await self.risk_assessor.initialize_models()
            
            # Initialize trading components
            self.order_executor = OrderExecutor()
            await self.order_executor.initialize()
            
            self.position_sizer = PositionSizer()
            self.stop_loss_manager = StopLossManager()
            
            logger.info("✅ Auto-trader components initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize auto-trader: {e}")
            self.status = TraderStatus.ERROR
            return False
    
    async def configure(self, config: Dict[str, Any]) -> None:
        """Configure auto-trader settings."""
        try:
            self.config = config
            self.enabled_networks = set(config.get('networks', ['ethereum']))
            self.max_position_size = config.get('max_position_size', 0.1)
            self.min_liquidity = config.get('min_liquidity', 50000)
            self.max_risk_score = config.get('max_risk_score', 3.0)
            self.profit_target_percent = config.get('profit_target_percent', 20.0)
            self.stop_loss_percent = config.get('stop_loss_percent', 10.0)
            self.max_slippage_percent = config.get('max_slippage_percent', 5.0)
            self.cooldown_minutes = config.get('cooldown_minutes', 5)
            
            logger.info(f"✅ Auto-trader configured for networks: {self.enabled_networks}")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure auto-trader: {e}")
            raise TradingError(f"Configuration failed: {e}")
    
    async def start_trading(self) -> None:
        """Start the auto-trading loop."""
        try:
            if self.status == TraderStatus.RUNNING:
                logger.warning("Auto-trader is already running")
                return
            
            logger.info("🤖 Starting auto-trading bot...")
            self.status = TraderStatus.STARTING
            self.start_time = datetime.utcnow()
            self.running = True
            
            # Main trading loop
            while self.running:
                try:
                    self.status = TraderStatus.RUNNING
                    
                    # Scan for opportunities
                    opportunities = await self._scan_for_opportunities()
                    
                    # Process opportunities
                    for opportunity in opportunities:
                        if not self.running:
                            break
                        
                        await self._process_opportunity(opportunity)
                    
                    # Manage existing positions
                    await self._manage_positions()
                    
                    # Update statistics
                    await self._update_statistics()
                    
                    # Wait before next cycle
                    await asyncio.sleep(30)  # 30-second cycles
                    
                except Exception as e:
                    logger.error(f"❌ Error in trading loop: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
            
            self.status = TraderStatus.STOPPED
            logger.info("🛑 Auto-trading stopped")
            
        except Exception as e:
            logger.error(f"❌ Auto-trading failed: {e}")
            self.status = TraderStatus.ERROR
            self.running = False
    
    async def stop_trading(self) -> None:
        """Stop the auto-trading bot."""
        logger.info("🛑 Stopping auto-trading bot...")
        self.running = False
        self.status = TraderStatus.STOPPED
    
    async def pause_trading(self) -> None:
        """Pause auto-trading temporarily."""
        logger.info("⏸️ Pausing auto-trading...")
        self.status = TraderStatus.PAUSED
    
    async def resume_trading(self) -> None:
        """Resume auto-trading."""
        logger.info("▶️ Resuming auto-trading...")
        self.status = TraderStatus.RUNNING
    
    async def execute_manual_trade(
        self,
        token_address: str,
        network: str,
        action: str,
        amount_eth: float,
        max_slippage: float
    ) -> Dict[str, Any]:
        """Execute a manual trade."""
        try:
            logger.info(f"📈 Executing manual {action} for {token_address}")
            
            if not self.order_executor:
                raise TradingError("Order executor not initialized")
            
            # Create order
            order = Order(
                order_id=str(uuid.uuid4()),
                token_address=token_address,
                side=OrderSide.BUY if action.lower() == 'buy' else OrderSide.SELL,
                order_type=OrderType.MARKET,
                amount=Decimal(str(amount_eth)),
                slippage_tolerance=Decimal(str(max_slippage / 100))
            )
            
            # Execute order
            execution_result = await self.order_executor.execute_order(order, network)
            
            # Record trade
            trade = TradeExecution(
                trade_id=str(uuid.uuid4()),
                token_address=token_address,
                network=network,
                action=TradeAction.BUY if action.lower() == 'buy' else TradeAction.SELL,
                amount_eth=amount_eth,
                price_usd=float(execution_result.get('average_price', 0)),
                slippage_percent=float(execution_result.get('slippage', 0)),
                gas_fee_eth=float(execution_result.get('gas_fee', 0)),
                status=execution_result.get('status', 'completed'),
                transaction_hash=execution_result.get('transaction_hash'),
                executed_at=datetime.utcnow()
            )
            
            self.trade_history.append(trade)
            
            return {
                "trade_id": trade.trade_id,
                "status": "executed",
                "transaction_hash": trade.transaction_hash,
                "execution_details": execution_result
            }
            
        except Exception as e:
            logger.error(f"❌ Manual trade execution failed: {e}")
            raise TradingError(f"Trade execution failed: {e}")
    
    async def _scan_for_opportunities(self) -> List[TradingOpportunity]:
        """Scan for trading opportunities using AI."""
        opportunities = []
        
        try:
            # Get recent token discoveries for each network
            for network in self.enabled_networks:
                # Mock token discovery - replace with actual implementation
                recent_tokens = await self._get_recent_tokens(network)
                
                for token in recent_tokens:
                    if await self._is_in_cooldown():
                        continue
                    
                    # AI risk assessment
                    if self.risk_assessor:
                        risk_result = await self.risk_assessor.quick_risk_assessment(
                            token['address'], network
                        )
                        
                        if (risk_result['risk_score'] <= self.max_risk_score and
                            token.get('liquidity_usd', 0) >= self.min_liquidity):
                            
                            opportunity = TradingOpportunity(
                                token_address=token['address'],
                                network=network,
                                symbol=token.get('symbol', 'Unknown'),
                                name=token.get('name', 'Unknown'),
                                current_price=token.get('price_usd', 0),
                                liquidity_usd=token.get('liquidity_usd', 0),
                                risk_score=risk_result['risk_score'],
                                confidence=risk_result['confidence'],
                                recommended_action=TradeAction.BUY,
                                profit_potential=self._calculate_profit_potential(token),
                                time_sensitivity="high",
                                ai_signals=risk_result
                            )
                            
                            opportunities.append(opportunity)
            
            logger.info(f"🔍 Found {len(opportunities)} trading opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Opportunity scanning failed: {e}")
            return []
    
    async def _process_opportunity(self, opportunity: TradingOpportunity) -> None:
        """Process a trading opportunity."""
        try:
            if opportunity.recommended_action != TradeAction.BUY:
                return
            
            # Check if we should trade this opportunity
            if not await self._should_trade_opportunity(opportunity):
                return
            
            # Calculate position size
            position_size = await self._calculate_position_size(opportunity)
            
            if position_size <= 0:
                return
            
            logger.info(f"💰 Trading opportunity: {opportunity.symbol} "
                       f"(Risk: {opportunity.risk_score:.2f}, Size: {position_size:.4f} ETH)")
            
            # Execute buy order
            execution_result = await self.execute_manual_trade(
                token_address=opportunity.token_address,
                network=opportunity.network,
                action="buy",
                amount_eth=position_size,
                max_slippage=self.max_slippage_percent
            )
            
            # Track position
            if execution_result['status'] == 'executed':
                await self._track_new_position(opportunity, execution_result, position_size)
            
        except Exception as e:
            logger.error(f"❌ Failed to process opportunity {opportunity.symbol}: {e}")
    
    async def _manage_positions(self) -> None:
        """Manage existing trading positions."""
        try:
            for position_id, position in list(self.active_positions.items()):
                # Check profit/loss
                current_pnl = await self._calculate_position_pnl(position)
                
                # Check stop-loss
                if current_pnl <= -self.stop_loss_percent:
                    await self._close_position(position_id, "stop_loss")
                
                # Check profit target
                elif current_pnl >= self.profit_target_percent:
                    await self._close_position(position_id, "profit_target")
                
                # Check time-based exit (24h max hold)
                elif (datetime.utcnow() - position['opened_at']).hours >= 24:
                    await self._close_position(position_id, "time_exit")
            
        except Exception as e:
            logger.error(f"❌ Position management failed: {e}")
    
    async def _should_trade_opportunity(self, opportunity: TradingOpportunity) -> bool:
        """Determine if we should trade an opportunity."""
        try:
            # Check cooldown
            if await self._is_in_cooldown():
                return False
            
            # Check if already holding this token
            for position in self.active_positions.values():
                if position['token_address'] == opportunity.token_address:
                    return False
            
            # Check maximum positions limit
            if len(self.active_positions) >= 10:  # Max 10 concurrent positions
                return False
            
            # Check risk score
            if opportunity.risk_score > self.max_risk_score:
                return False
            
            # Check liquidity
            if opportunity.liquidity_usd < self.min_liquidity:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate opportunity: {e}")
            return False
    
    async def _calculate_position_size(self, opportunity: TradingOpportunity) -> float:
        """Calculate position size for an opportunity."""
        try:
            if self.position_sizer:
                return await self.position_sizer.calculate_position_size(
                    risk_score=opportunity.risk_score,
                    confidence=opportunity.confidence,
                    max_position_size=self.max_position_size
                )
            else:
                # Simple position sizing based on risk
                base_size = self.max_position_size
                risk_multiplier = max(0.1, 1.0 - (opportunity.risk_score / 10.0))
                return base_size * risk_multiplier
            
        except Exception as e:
            logger.error(f"❌ Position sizing failed: {e}")
            return 0.0
    
    async def _track_new_position(
        self, 
        opportunity: TradingOpportunity, 
        execution_result: Dict[str, Any], 
        position_size: float
    ) -> None:
        """Track a new position."""
        try:
            position_id = str(uuid.uuid4())
            
            position = {
                "position_id": position_id,
                "token_address": opportunity.token_address,
                "network": opportunity.network,
                "symbol": opportunity.symbol,
                "entry_price": float(execution_result.get('average_price', 0)),
                "amount_eth": position_size,
                "opened_at": datetime.utcnow(),
                "transaction_hash": execution_result.get('transaction_hash'),
                "stop_loss_price": 0.0,
                "profit_target_price": 0.0,
                "current_pnl": 0.0
            }
            
            # Set stop-loss and profit targets
            entry_price = position['entry_price']
            position['stop_loss_price'] = entry_price * (1 - self.stop_loss_percent / 100)
            position['profit_target_price'] = entry_price * (1 + self.profit_target_percent / 100)
            
            self.active_positions[position_id] = position
            self.last_trade_time = datetime.utcnow()
            
            logger.info(f"📊 New position opened: {opportunity.symbol} "
                       f"(Entry: ${entry_price:.6f}, Size: {position_size:.4f} ETH)")
            
        except Exception as e:
            logger.error(f"❌ Failed to track position: {e}")
    
    async def _close_position(self, position_id: str, reason: str) -> None:
        """Close a trading position."""
        try:
            if position_id not in self.active_positions:
                return
            
            position = self.active_positions[position_id]
            
            logger.info(f"🔒 Closing position {position['symbol']} - Reason: {reason}")
            
            # Execute sell order
            execution_result = await self.execute_manual_trade(
                token_address=position['token_address'],
                network=position['network'],
                action="sell",
                amount_eth=position['amount_eth'],
                max_slippage=self.max_slippage_percent
            )
            
            # Calculate final P&L
            if execution_result['status'] == 'executed':
                exit_price = float(execution_result['execution_details'].get('average_price', 0))
                entry_price = position['entry_price']
                pnl_percent = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
                
                # Update trade record
                for trade in self.trade_history:
                    if (trade.token_address == position['token_address'] and 
                        trade.action == TradeAction.BUY and 
                        trade.closed_at is None):
                        trade.profit_loss = pnl_percent
                        trade.closed_at = datetime.utcnow()
                        break
                
                # Update statistics
                if pnl_percent > 0:
                    self.statistics.profitable_trades += 1
                else:
                    self.statistics.losing_trades += 1
                
                self.statistics.total_profit_loss += pnl_percent
                
                logger.info(f"💹 Position closed: {position['symbol']} "
                           f"(P&L: {pnl_percent:.2f}%, Exit: ${exit_price:.6f})")
            
            # Remove from active positions
            del self.active_positions[position_id]
            
        except Exception as e:
            logger.error(f"❌ Failed to close position: {e}")
    
    async def _calculate_position_pnl(self, position: Dict[str, Any]) -> float:
        """Calculate current P&L for a position."""
        try:
            # Mock current price - replace with actual price fetching
            current_price = await self._get_current_price(
                position['token_address'], 
                position['network']
            )
            
            if current_price > 0 and position['entry_price'] > 0:
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
                position['current_pnl'] = pnl_percent
                return pnl_percent
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ P&L calculation failed: {e}")
            return 0.0
    
    async def _is_in_cooldown(self) -> bool:
        """Check if we're in trading cooldown period."""
        if not self.last_trade_time:
            return False
        
        cooldown_duration = timedelta(minutes=self.cooldown_minutes)
        return datetime.utcnow() - self.last_trade_time < cooldown_duration
    
    async def _get_recent_tokens(self, network: str) -> List[Dict[str, Any]]:
        """Get recently discovered tokens (mock implementation)."""
        # Mock data - replace with actual token discovery service
        return [
            {
                "address": "0x1234567890123456789012345678901234567890",
                "symbol": "NEWTOKEN",
                "name": "New Token",
                "price_usd": 0.001,
                "liquidity_usd": 75000,
                "volume_24h": 50000,
                "discovered_at": datetime.utcnow() - timedelta(minutes=5)
            },
            {
                "address": "0x0987654321098765432109876543210987654321",
                "symbol": "MOON",
                "name": "Moon Token",
                "price_usd": 0.0001,
                "liquidity_usd": 120000,
                "volume_24h": 25000,
                "discovered_at": datetime.utcnow() - timedelta(minutes=10)
            }
        ]
    
    async def _get_current_price(self, token_address: str, network: str) -> float:
        """Get current token price (mock implementation)."""
        # Mock price - replace with actual price fetching
        import random
        return random.uniform(0.0001, 0.01)
    
    def _calculate_profit_potential(self, token: Dict[str, Any]) -> float:
        """Calculate profit potential for a token."""
        # Simple heuristic based on liquidity and volume
        liquidity = token.get('liquidity_usd', 0)
        volume = token.get('volume_24h', 0)
        
        if liquidity > 100000 and volume > 50000:
            return 15.0  # High potential
        elif liquidity > 50000 and volume > 25000:
            return 10.0  # Medium potential
        else:
            return 5.0   # Low potential
    
    async def _update_statistics(self) -> None:
        """Update trading statistics."""
        try:
            total_trades = len(self.trade_history)
            profitable = sum(1 for t in self.trade_history if t.profit_loss and t.profit_loss > 0)
            
            self.statistics.total_trades = total_trades
            self.statistics.profitable_trades = profitable
            self.statistics.losing_trades = total_trades - profitable
            self.statistics.success_rate = (profitable / total_trades * 100) if total_trades > 0 else 0
            self.statistics.active_positions = len(self.active_positions)
            
            # Calculate total P&L
            total_pnl = sum(t.profit_loss for t in self.trade_history if t.profit_loss)
            self.statistics.total_profit_loss = total_pnl
            
            # Calculate largest profit/loss
            profits = [t.profit_loss for t in self.trade_history if t.profit_loss and t.profit_loss > 0]
            losses = [t.profit_loss for t in self.trade_history if t.profit_loss and t.profit_loss < 0]
            
            self.statistics.largest_profit = max(profits) if profits else 0.0
            self.statistics.largest_loss = min(losses) if losses else 0.0
            
        except Exception as e:
            logger.error(f"❌ Statistics update failed: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current auto-trader status."""
        try:
            uptime = 0
            if self.start_time:
                uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                "trader_id": self.trader_id,
                "status": self.status.value,
                "is_active": self.running,
                "uptime_seconds": int(uptime),
                "enabled_networks": list(self.enabled_networks),
                "current_positions": len(self.active_positions),
                "configuration": self.config,
                "last_trade_time": self.last_trade_time.isoformat() if self.last_trade_time else None
            }
            
        except Exception as e:
            logger.error(f"❌ Status retrieval failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get trading statistics."""
        try:
            await self._update_statistics()
            
            return {
                "total_trades": self.statistics.total_trades,
                "profitable_trades": self.statistics.profitable_trades,
                "losing_trades": self.statistics.losing_trades,
                "success_rate": round(self.statistics.success_rate, 2),
                "total_profit_loss": round(self.statistics.total_profit_loss, 2),
                "largest_profit": round(self.statistics.largest_profit, 2),
                "largest_loss": round(self.statistics.largest_loss, 2),
                "active_positions": self.statistics.active_positions,
                "total_volume": round(self.statistics.total_volume, 4),
                "total_fees_paid": round(self.statistics.total_fees_paid, 6)
            }
            
        except Exception as e:
            logger.error(f"❌ Statistics retrieval failed: {e}")
            return {}
    
    async def get_active_positions(self) -> List[Dict[str, Any]]:
        """Get all active trading positions."""
        try:
            positions = []
            
            for position_id, position in self.active_positions.items():
                # Update current P&L
                current_pnl = await self._calculate_position_pnl(position)
                
                position_data = {
                    "position_id": position_id,
                    "symbol": position['symbol'],
                    "token_address": position['token_address'],
                    "network": position['network'],
                    "entry_price": position['entry_price'],
                    "amount_eth": position['amount_eth'],
                    "current_pnl": round(current_pnl, 2),
                    "stop_loss_price": position['stop_loss_price'],
                    "profit_target_price": position['profit_target_price'],
                    "opened_at": position['opened_at'].isoformat(),
                    "holding_time_minutes": int((datetime.utcnow() - position['opened_at']).total_seconds() / 60)
                }
                
                positions.append(position_data)
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ Failed to get active positions: {e}")
            return []
    
    async def get_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trade history."""
        try:
            recent_trades = self.trade_history[-limit:] if limit > 0 else self.trade_history
            
            history = []
            for trade in reversed(recent_trades):
                trade_data = {
                    "trade_id": trade.trade_id,
                    "token_address": trade.token_address,
                    "network": trade.network,
                    "action": trade.action.value,
                    "amount_eth": trade.amount_eth,
                    "price_usd": trade.price_usd,
                    "slippage_percent": trade.slippage_percent,
                    "gas_fee_eth": trade.gas_fee_eth,
                    "status": trade.status,
                    "transaction_hash": trade.transaction_hash,
                    "executed_at": trade.executed_at.isoformat(),
                    "profit_loss": trade.profit_loss,
                    "closed_at": trade.closed_at.isoformat() if trade.closed_at else None
                }
                
                history.append(trade_data)
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get trade history: {e}")
            return []


# Factory function
async def create_auto_trader() -> AutoTrader:
    """Create and initialize auto-trader."""
    trader = AutoTrader()
    await trader.initialize()
    return trader