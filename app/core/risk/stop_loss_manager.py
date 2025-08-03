"""
Advanced Stop-Loss Management System
File: app/core/risk/stop_loss_manager.py

Professional stop-loss automation with dynamic adjustment and trailing stops.
Implements sophisticated stop-loss strategies for optimal risk management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import math

from app.core.performance.cache_manager import cache_manager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__)


class StopLossType(Enum):
    """Types of stop-loss orders."""
    FIXED = "fixed"
    TRAILING = "trailing"
    DYNAMIC = "dynamic"
    TIME_BASED = "time_based"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    SUPPORT_RESISTANCE = "support_resistance"


class StopLossStatus(Enum):
    """Stop-loss order status."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"


class TriggerCondition(Enum):
    """Conditions for stop-loss triggers."""
    PRICE_BELOW = "price_below"
    PRICE_ABOVE = "price_above"
    PERCENTAGE_LOSS = "percentage_loss"
    TIME_ELAPSED = "time_elapsed"
    VOLATILITY_SPIKE = "volatility_spike"
    VOLUME_THRESHOLD = "volume_threshold"


@dataclass
class StopLossOrder:
    """Stop-loss order configuration."""
    order_id: str
    token_address: str
    position_size: Decimal
    entry_price: Decimal
    stop_price: Decimal
    stop_type: StopLossType
    trigger_condition: TriggerCondition
    
    # Trailing stop parameters
    trail_distance: Optional[Decimal] = None
    trail_activation_price: Optional[Decimal] = None
    highest_price: Optional[Decimal] = None
    
    # Dynamic adjustment parameters
    volatility_multiplier: Decimal = Decimal('1.0')
    time_decay_factor: Decimal = Decimal('1.0')
    support_level: Optional[Decimal] = None
    resistance_level: Optional[Decimal] = None
    
    # Execution parameters
    slippage_tolerance: Decimal = Decimal('0.01')  # 1%
    max_execution_time: int = 300  # 5 minutes
    partial_fill_allowed: bool = True
    
    # Status and metadata
    status: StopLossStatus = StopLossStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    triggered_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Performance tracking
    unrealized_pnl: Decimal = Decimal('0')
    realized_pnl: Optional[Decimal] = None
    max_profit: Decimal = Decimal('0')
    max_loss: Decimal = Decimal('0')
    
    # Callbacks and notifications
    trigger_callbacks: List[Callable] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class StopLossExecution:
    """Stop-loss execution result."""
    order_id: str
    execution_id: str
    executed_price: Decimal
    executed_quantity: Decimal
    execution_fee: Decimal
    slippage: Decimal
    execution_time: datetime
    transaction_hash: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class StopLossManagerException(DexSnipingException):
    """Exception raised when stop-loss management operations fail."""
    pass


class StopLossManager:
    """
    Advanced stop-loss management system with professional automation.
    
    Features:
    - Multiple stop-loss types (fixed, trailing, dynamic)
    - Volatility-adjusted stop levels
    - Support/resistance level integration
    - Time-based stop adjustments
    - Automated execution with slippage protection
    - Real-time monitoring and alerts
    """
    
    def __init__(self):
        self.active_orders: Dict[str, StopLossOrder] = {}
        self.executed_orders: Dict[str, StopLossOrder] = {}
        self.price_feeds: Dict[str, Decimal] = {}
        self.volatility_data: Dict[str, Decimal] = {}
        
        # Monitoring and execution
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        self.check_interval = 1.0  # Check every second
        
        # Execution callbacks
        self.execution_callbacks: List[Callable] = []
        self.price_update_callbacks: List[Callable] = []
        
        # Default parameters
        self.default_slippage = Decimal('0.01')  # 1%
        self.default_trail_distance = Decimal('0.05')  # 5%
        self.max_orders_per_token = 5
        
        logger.info("✅ StopLossManager initialized with professional automation")

    async def set_stop_loss(
        self,
        token_address: str,
        position_size: Decimal,
        entry_price: Decimal,
        stop_price: Optional[Decimal] = None,
        stop_type: StopLossType = StopLossType.FIXED,
        trail_distance: Optional[Decimal] = None,
        **kwargs
    ) -> str:
        """
        Set stop-loss order for a position.
        
        Method: set_stop_loss()
        
        Args:
            token_address: Token contract address
            position_size: Size of the position
            entry_price: Entry price of the position
            stop_price: Stop-loss price (calculated if not provided)
            stop_type: Type of stop-loss order
            trail_distance: Trailing distance for trailing stops
            **kwargs: Additional parameters
            
        Returns:
            Stop-loss order ID
        """
        try:
            # Generate order ID
            order_id = f"sl_{token_address[:8]}_{int(datetime.utcnow().timestamp())}"
            
            # Calculate stop price if not provided
            if stop_price is None:
                stop_price = await self._calculate_default_stop_price(
                    token_address, entry_price, stop_type
                )
            
            # Validate stop price
            await self._validate_stop_price(entry_price, stop_price, position_size)
            
            # Create stop-loss order
            stop_order = StopLossOrder(
                order_id=order_id,
                token_address=token_address,
                position_size=position_size,
                entry_price=entry_price,
                stop_price=stop_price,
                stop_type=stop_type,
                trigger_condition=TriggerCondition.PRICE_BELOW,
                trail_distance=trail_distance or self.default_trail_distance,
                slippage_tolerance=kwargs.get('slippage_tolerance', self.default_slippage),
                max_execution_time=kwargs.get('max_execution_time', 300),
                expires_at=kwargs.get('expires_at'),
                notification_channels=kwargs.get('notification_channels', [])
            )
            
            # Initialize trailing stop parameters
            if stop_type == StopLossType.TRAILING:
                stop_order.highest_price = entry_price
                stop_order.trail_activation_price = entry_price * (1 + trail_distance)
            
            # Add to active orders
            self.active_orders[order_id] = stop_order
            
            # Start monitoring if not already running
            if not self.is_monitoring:
                await self.start_monitoring()
            
            # Cache order
            await self._cache_stop_order(stop_order)
            
            logger.info(f"✅ Stop-loss set: {order_id} for {token_address} "
                       f"@ ${stop_price} ({stop_type.value})")
            
            return order_id
            
        except Exception as e:
            logger.error(f"Error setting stop-loss: {e}")
            raise StopLossManagerException(f"Failed to set stop-loss: {e}")

    async def adjust_trailing_stop(
        self,
        order_id: str,
        current_price: Optional[Decimal] = None
    ) -> bool:
        """
        Adjust trailing stop-loss based on current price.
        
        Method: adjust_trailing_stop()
        
        Args:
            order_id: Stop-loss order ID
            current_price: Current token price (fetched if not provided)
            
        Returns:
            True if adjustment was made, False otherwise
        """
        try:
            stop_order = self.active_orders.get(order_id)
            if not stop_order or stop_order.stop_type != StopLossType.TRAILING:
                return False
            
            # Get current price
            if current_price is None:
                current_price = await self._get_current_price(stop_order.token_address)
            
            if current_price is None:
                logger.warning(f"Could not get current price for {stop_order.token_address}")
                return False
            
            # Check if price has reached activation level
            if (stop_order.trail_activation_price and 
                current_price < stop_order.trail_activation_price):
                return False
            
            # Update highest price if current price is higher
            if current_price > (stop_order.highest_price or stop_order.entry_price):
                old_highest = stop_order.highest_price
                stop_order.highest_price = current_price
                
                # Calculate new stop price
                new_stop_price = current_price * (1 - stop_order.trail_distance)
                
                # Only adjust if new stop is higher than current stop
                if new_stop_price > stop_order.stop_price:
                    old_stop = stop_order.stop_price
                    stop_order.stop_price = new_stop_price
                    stop_order.updated_at = datetime.utcnow()
                    
                    # Update cache
                    await self._cache_stop_order(stop_order)
                    
                    logger.info(f"📈 Trailing stop adjusted: {order_id} "
                               f"${old_stop:.6f} → ${new_stop_price:.6f} "
                               f"(High: ${old_highest:.6f} → ${current_price:.6f})")
                    
                    # Trigger callbacks
                    await self._trigger_adjustment_callbacks(stop_order, old_stop, new_stop_price)
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adjusting trailing stop {order_id}: {e}")
            return False

    async def execute_stop_loss(
        self,
        order_id: str,
        trigger_price: Decimal,
        execution_reason: str = "stop_triggered"
    ) -> Optional[StopLossExecution]:
        """
        Execute stop-loss order.
        
        Method: execute_stop_loss()
        
        Args:
            order_id: Stop-loss order ID
            trigger_price: Price that triggered the stop
            execution_reason: Reason for execution
            
        Returns:
            Execution result or None if failed
        """
        try:
            stop_order = self.active_orders.get(order_id)
            if not stop_order or stop_order.status != StopLossStatus.ACTIVE:
                logger.warning(f"Cannot execute stop-loss {order_id}: order not active")
                return None
            
            logger.info(f"⚡ Executing stop-loss: {order_id} @ ${trigger_price} ({execution_reason})")
            
            # Update order status
            stop_order.status = StopLossStatus.TRIGGERED
            stop_order.triggered_at = datetime.utcnow()
            
            # Execute the trade
            execution_result = await self._execute_stop_trade(stop_order, trigger_price)
            
            if execution_result and execution_result.success:
                # Mark as executed
                stop_order.status = StopLossStatus.TRIGGERED
                stop_order.executed_at = datetime.utcnow()
                stop_order.realized_pnl = self._calculate_realized_pnl(
                    stop_order, execution_result.executed_price
                )
                
                # Move to executed orders
                self.executed_orders[order_id] = stop_order
                del self.active_orders[order_id]
                
                # Update cache
                await self._cache_executed_order(stop_order)
                
                # Trigger callbacks
                await self._trigger_execution_callbacks(stop_order, execution_result)
                
                logger.info(f"✅ Stop-loss executed: {order_id} "
                           f"@ ${execution_result.executed_price} "
                           f"(PnL: ${stop_order.realized_pnl})")
                
            else:
                # Execution failed
                stop_order.status = StopLossStatus.ACTIVE  # Revert to active
                stop_order.triggered_at = None
                
                logger.error(f"❌ Stop-loss execution failed: {order_id}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing stop-loss {order_id}: {e}")
            return None

    async def update_dynamic_stop(
        self,
        order_id: str,
        volatility: Optional[Decimal] = None,
        support_level: Optional[Decimal] = None
    ) -> bool:
        """Update dynamic stop-loss based on market conditions."""
        try:
            stop_order = self.active_orders.get(order_id)
            if not stop_order or stop_order.stop_type != StopLossType.DYNAMIC:
                return False
            
            # Get current market data
            current_price = await self._get_current_price(stop_order.token_address)
            if volatility is None:
                volatility = await self._get_token_volatility(stop_order.token_address)
            
            if current_price is None:
                return False
            
            # Calculate dynamic stop price
            base_distance = abs(stop_order.entry_price - stop_order.stop_price) / stop_order.entry_price
            
            # Adjust for volatility
            volatility_adjustment = 1 + (volatility * stop_order.volatility_multiplier)
            adjusted_distance = base_distance * volatility_adjustment
            
            # Adjust for support levels
            if support_level and support_level < current_price:
                support_distance = abs(current_price - support_level) / current_price
                adjusted_distance = min(adjusted_distance, support_distance * Decimal('1.1'))
            
            new_stop_price = current_price * (1 - adjusted_distance)
            
            # Only update if new stop is better (higher for long positions)
            if new_stop_price > stop_order.stop_price:
                old_stop = stop_order.stop_price
                stop_order.stop_price = new_stop_price
                stop_order.updated_at = datetime.utcnow()
                
                await self._cache_stop_order(stop_order)
                
                logger.info(f"🔄 Dynamic stop updated: {order_id} "
                           f"${old_stop:.6f} → ${new_stop_price:.6f}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating dynamic stop {order_id}: {e}")
            return False

    async def cancel_stop_loss(self, order_id: str, reason: str = "manual_cancel") -> bool:
        """Cancel an active stop-loss order."""
        try:
            stop_order = self.active_orders.get(order_id)
            if not stop_order:
                logger.warning(f"Stop-loss order {order_id} not found")
                return False
            
            # Update status
            stop_order.status = StopLossStatus.CANCELLED
            stop_order.updated_at = datetime.utcnow()
            
            # Move to executed orders (for history)
            self.executed_orders[order_id] = stop_order
            del self.active_orders[order_id]
            
            # Update cache
            await self._cache_executed_order(stop_order)
            
            logger.info(f"🚫 Stop-loss cancelled: {order_id} ({reason})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling stop-loss {order_id}: {e}")
            return False

    async def start_monitoring(self) -> None:
        """Start monitoring active stop-loss orders."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🔍 Stop-loss monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop monitoring active stop-loss orders."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ Stop-loss monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for stop-loss orders."""
        while self.is_monitoring:
            try:
                # Check all active orders
                orders_to_check = list(self.active_orders.values())
                
                for stop_order in orders_to_check:
                    await self._check_stop_order(stop_order)
                
                # Remove expired orders
                await self._cleanup_expired_orders()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_stop_order(self, stop_order: StopLossOrder) -> None:
        """Check individual stop-loss order for triggers."""
        try:
            # Skip if not active
            if stop_order.status != StopLossStatus.ACTIVE:
                return
            
            # Check expiration
            if stop_order.expires_at and datetime.utcnow() > stop_order.expires_at:
                await self.cancel_stop_loss(stop_order.order_id, "expired")
                return
            
            # Get current price
            current_price = await self._get_current_price(stop_order.token_address)
            if current_price is None:
                return
            
            # Update unrealized PnL
            stop_order.unrealized_pnl = (current_price - stop_order.entry_price) * stop_order.position_size
            stop_order.max_profit = max(stop_order.max_profit, stop_order.unrealized_pnl)
            stop_order.max_loss = min(stop_order.max_loss, stop_order.unrealized_pnl)
            
            # Check for trailing stop adjustment
            if stop_order.stop_type == StopLossType.TRAILING:
                await self.adjust_trailing_stop(stop_order.order_id, current_price)
            
            # Check for dynamic stop adjustment
            elif stop_order.stop_type == StopLossType.DYNAMIC:
                await self.update_dynamic_stop(stop_order.order_id)
            
            # Check trigger conditions
            should_trigger = await self._check_trigger_conditions(stop_order, current_price)
            
            if should_trigger:
                await self.execute_stop_loss(
                    stop_order.order_id, 
                    current_price,
                    "price_trigger"
                )
            
        except Exception as e:
            logger.error(f"Error checking stop order {stop_order.order_id}: {e}")

    async def _check_trigger_conditions(
        self, 
        stop_order: StopLossOrder, 
        current_price: Decimal
    ) -> bool:
        """Check if stop-loss should be triggered."""
        try:
            if stop_order.trigger_condition == TriggerCondition.PRICE_BELOW:
                return current_price <= stop_order.stop_price
            
            elif stop_order.trigger_condition == TriggerCondition.PERCENTAGE_LOSS:
                loss_pct = (stop_order.entry_price - current_price) / stop_order.entry_price
                return loss_pct >= stop_order.stop_price  # stop_price as percentage
            
            elif stop_order.trigger_condition == TriggerCondition.TIME_ELAPSED:
                if stop_order.expires_at:
                    return datetime.utcnow() >= stop_order.expires_at
            
            elif stop_order.trigger_condition == TriggerCondition.VOLATILITY_SPIKE:
                volatility = await self._get_token_volatility(stop_order.token_address)
                return volatility > stop_order.stop_price  # stop_price as volatility threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trigger conditions: {e}")
            return False

    async def _execute_stop_trade(
        self, 
        stop_order: StopLossOrder, 
        trigger_price: Decimal
    ) -> Optional[StopLossExecution]:
        """Execute the actual stop-loss trade."""
        try:
            execution_id = f"exec_{stop_order.order_id}_{int(datetime.utcnow().timestamp())}"
            
            # Simulate trade execution (placeholder)
            # In production, this would integrate with actual DEX trading
            
            # Calculate slippage
            slippage = min(stop_order.slippage_tolerance, abs(trigger_price - stop_order.stop_price) / stop_order.stop_price)
            executed_price = trigger_price * (1 - slippage)
            
            # Calculate fees (0.3% example)
            execution_fee = stop_order.position_size * executed_price * Decimal('0.003')
            
            execution = StopLossExecution(
                order_id=stop_order.order_id,
                execution_id=execution_id,
                executed_price=executed_price,
                executed_quantity=stop_order.position_size,
                execution_fee=execution_fee,
                slippage=slippage,
                execution_time=datetime.utcnow(),
                transaction_hash=f"0x{'a' * 64}",  # Placeholder
                success=True
            )
            
            return execution
            
        except Exception as e:
            logger.error(f"Error executing stop trade: {e}")
            return StopLossExecution(
                order_id=stop_order.order_id,
                execution_id="failed",
                executed_price=Decimal('0'),
                executed_quantity=Decimal('0'),
                execution_fee=Decimal('0'),
                slippage=Decimal('0'),
                execution_time=datetime.utcnow(),
                success=False,
                error_message=str(e)
            )

    async def _calculate_default_stop_price(
        self, 
        token_address: str, 
        entry_price: Decimal, 
        stop_type: StopLossType
    ) -> Decimal:
        """Calculate default stop price based on token characteristics."""
        try:
            if stop_type == StopLossType.VOLATILITY_ADJUSTED:
                volatility = await self._get_token_volatility(token_address)
                # Higher volatility = wider stop
                stop_distance = Decimal('0.05') + (volatility * Decimal('0.1'))
            else:
                # Default 8% stop loss
                stop_distance = Decimal('0.08')
            
            return entry_price * (1 - stop_distance)
            
        except Exception as e:
            logger.error(f"Error calculating default stop price: {e}")
            return entry_price * Decimal('0.92')  # 8% default

    async def _get_current_price(self, token_address: str) -> Optional[Decimal]:
        """Get current price for a token."""
        try:
            # Check cache first
            cached_price = self.price_feeds.get(token_address)
            if cached_price:
                return cached_price
            
            # Placeholder: In production, fetch from price feed
            # For now, return a simulated price
            return Decimal('1.50')  # Placeholder price
            
        except Exception as e:
            logger.error(f"Error getting current price for {token_address}: {e}")
            return None

    async def _get_token_volatility(self, token_address: str) -> Decimal:
        """Get token volatility from cache or calculate."""
        try:
            cached_volatility = self.volatility_data.get(token_address)
            if cached_volatility:
                return cached_volatility
            
            # Placeholder: In production, calculate from price history
            return Decimal('0.3')  # 30% default volatility
            
        except Exception as e:
            logger.error(f"Error getting volatility for {token_address}: {e}")
            return Decimal('0.5')  # Default high volatility

    def _calculate_realized_pnl(
        self, 
        stop_order: StopLossOrder, 
        execution_price: Decimal
    ) -> Decimal:
        """Calculate realized P&L from stop-loss execution."""
        try:
            price_diff = execution_price - stop_order.entry_price
            return price_diff * stop_order.position_size
        except Exception:
            return Decimal('0')

    async def _validate_stop_price(
        self, 
        entry_price: Decimal, 
        stop_price: Decimal, 
        position_size: Decimal
    ) -> None:
        """Validate stop-loss parameters."""
        if stop_price >= entry_price:
            raise StopLossManagerException("Stop price must be below entry price for long positions")
        
        if position_size <= 0:
            raise StopLossManagerException("Position size must be positive")
        
        # Check if stop is too close (minimum 0.1%)
        stop_distance = (entry_price - stop_price) / entry_price
        if stop_distance < Decimal('0.001'):
            raise StopLossManagerException("Stop price too close to entry price")

    async def _cache_stop_order(self, stop_order: StopLossOrder) -> None:
        """Cache stop-loss order."""
        try:
            cache_key = f"stop_order_{stop_order.order_id}"
            cache_data = {
                'order_id': stop_order.order_id,
                'token_address': stop_order.token_address,
                'stop_price': float(stop_order.stop_price),
                'stop_type': stop_order.stop_type.value,
                'status': stop_order.status.value,
                'created_at': stop_order.created_at.isoformat()
            }
            
            await cache_manager.set(
                cache_key, cache_data, ttl=3600, namespace='stop_loss'
            )
            
        except Exception as e:
            logger.error(f"Error caching stop order: {e}")

    async def _cache_executed_order(self, stop_order: StopLossOrder) -> None:
        """Cache executed stop-loss order."""
        try:
            cache_key = f"executed_stop_{stop_order.order_id}"
            cache_data = {
                'order_id': stop_order.order_id,
                'token_address': stop_order.token_address,
                'entry_price': float(stop_order.entry_price),
                'stop_price': float(stop_order.stop_price),
                'realized_pnl': float(stop_order.realized_pnl or 0),
                'status': stop_order.status.value,
                'executed_at': stop_order.executed_at.isoformat() if stop_order.executed_at else None
            }
            
            await cache_manager.set(
                cache_key, cache_data, ttl=86400, namespace='stop_loss'  # 24 hours
            )
            
        except Exception as e:
            logger.error(f"Error caching executed order: {e}")

    async def _cleanup_expired_orders(self) -> None:
        """Remove expired stop-loss orders."""
        try:
            current_time = datetime.utcnow()
            expired_orders = []
            
            for order_id, stop_order in self.active_orders.items():
                if stop_order.expires_at and current_time > stop_order.expires_at:
                    expired_orders.append(order_id)
            
            for order_id in expired_orders:
                await self.cancel_stop_loss(order_id, "expired")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired orders: {e}")

    async def _update_performance_metrics(self) -> None:
        """Update performance metrics for all orders."""
        try:
            for stop_order in self.active_orders.values():
                current_price = await self._get_current_price(stop_order.token_address)
                if current_price:
                    stop_order.unrealized_pnl = (current_price - stop_order.entry_price) * stop_order.position_size
                    stop_order.max_profit = max(stop_order.max_profit, stop_order.unrealized_pnl)
                    stop_order.max_loss = min(stop_order.max_loss, stop_order.unrealized_pnl)
                    
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    async def _trigger_adjustment_callbacks(
        self, 
        stop_order: StopLossOrder, 
        old_price: Decimal, 
        new_price: Decimal
    ) -> None:
        """Trigger callbacks for stop adjustment."""
        try:
            for callback in stop_order.trigger_callbacks:
                try:
                    await callback(stop_order, 'adjustment', {
                        'old_price': old_price,
                        'new_price': new_price
                    })
                except Exception as e:
                    logger.error(f"Error in adjustment callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering adjustment callbacks: {e}")

    async def _trigger_execution_callbacks(
        self, 
        stop_order: StopLossOrder, 
        execution: StopLossExecution
    ) -> None:
        """Trigger callbacks for stop execution."""
        try:
            for callback in stop_order.trigger_callbacks:
                try:
                    await callback(stop_order, 'execution', execution.__dict__)
                except Exception as e:
                    logger.error(f"Error in execution callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering execution callbacks: {e}")

    def update_price_feed(self, token_address: str, price: Decimal) -> None:
        """Update price feed for real-time monitoring."""
        self.price_feeds[token_address] = price

    def add_execution_callback(self, callback: Callable) -> None:
        """Add callback for stop-loss executions."""
        self.execution_callbacks.append(callback)

    def get_active_orders(self, token_address: Optional[str] = None) -> List[StopLossOrder]:
        """Get active stop-loss orders."""
        if token_address:
            return [order for order in self.active_orders.values() 
                   if order.token_address == token_address]
        return list(self.active_orders.values())

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of a specific order."""
        stop_order = self.active_orders.get(order_id) or self.executed_orders.get(order_id)
        
        if not stop_order:
            return {'error': 'Order not found'}
        
        return {
            'order_id': stop_order.order_id,
            'token_address': stop_order.token_address,
            'status': stop_order.status.value,
            'stop_price': float(stop_order.stop_price),
            'entry_price': float(stop_order.entry_price),
            'position_size': float(stop_order.position_size),
            'unrealized_pnl': float(stop_order.unrealized_pnl),
            'realized_pnl': float(stop_order.realized_pnl) if stop_order.realized_pnl else None,
            'created_at': stop_order.created_at.isoformat(),
            'updated_at': stop_order.updated_at.isoformat()
        }

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all stop-loss orders."""
        try:
            total_orders = len(self.active_orders) + len(self.executed_orders)
            triggered_orders = len([o for o in self.executed_orders.values() 
                                  if o.status == StopLossStatus.TRIGGERED])
            
            total_realized_pnl = sum(
                float(order.realized_pnl or 0) 
                for order in self.executed_orders.values()
            )
            
            total_unrealized_pnl = sum(
                float(order.unrealized_pnl) 
                for order in self.active_orders.values()
            )
            
            return {
                'total_orders': total_orders,
                'active_orders': len(self.active_orders),
                'triggered_orders': triggered_orders,
                'cancelled_orders': len(self.executed_orders) - triggered_orders,
                'trigger_rate': (triggered_orders / total_orders * 100) if total_orders > 0 else 0,
                'total_realized_pnl': total_realized_pnl,
                'total_unrealized_pnl': total_unrealized_pnl,
                'is_monitoring': self.is_monitoring
            }
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {}

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            await self.stop_monitoring()
            self.active_orders.clear()
            self.executed_orders.clear()
            self.price_feeds.clear()
            logger.info("✅ StopLossManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during StopLossManager cleanup: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def test_stop_loss_manager():
        """Test stop-loss manager functionality."""
        manager = StopLossManager()
        
        try:
            # Set a trailing stop-loss
            order_id = await manager.set_stop_loss(
                token_address="0x1234567890123456789012345678901234567890",
                position_size=Decimal('1000'),
                entry_price=Decimal('1.50'),
                stop_type=StopLossType.TRAILING,
                trail_distance=Decimal('0.05')  # 5% trailing distance
            )
            
            print(f"✅ Stop-loss order created: {order_id}")
            
            # Simulate price movement
            manager.update_price_feed(
                "0x1234567890123456789012345678901234567890", 
                Decimal('1.60')
            )
            
            # Check adjustment
            adjusted = await manager.adjust_trailing_stop(order_id, Decimal('1.60'))
            print(f"📈 Trailing stop adjusted: {adjusted}")
            
            # Get status
            status = manager.get_order_status(order_id)
            print(f"📊 Order status: {status}")
            
            # Get performance summary
            summary = await manager.get_performance_summary()
            print(f"📈 Performance summary: {summary}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            await manager.cleanup()
    
    # Run test
    asyncio.run(test_stop_loss_manager())