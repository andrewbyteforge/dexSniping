"""
Order Execution Engine - Live Trading Core
File: app/core/trading/order_executor.py

Professional order execution system with comprehensive error handling,
risk management, and multi-DEX support for the trading bot platform.
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid

from app.utils.logger import setup_logger, get_trading_logger, get_performance_logger, get_trading_logger, get_performance_logger
from app.core.exceptions import (
    TradingError,
    InsufficientFundsError,
    InvalidOrderError,
    OrderExecutionError
)

logger = setup_logger(__name__, "trading")


class OrderType(Enum):
    """Order types supported by the execution engine."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    EXECUTING = "executing"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"
    EXPIRED = "expired"


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class Order:
    """Order data structure."""
    
    def __init__(
        self,
        order_id: str,
        token_address: str,
        side: OrderSide,
        order_type: OrderType,
        amount: Decimal,
        price: Optional[Decimal] = None,
        slippage_tolerance: Decimal = Decimal("0.01"),
        expires_at: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.token_address = token_address
        self.side = side
        self.order_type = order_type
        self.amount = amount
        self.price = price
        self.slippage_tolerance = slippage_tolerance
        self.expires_at = expires_at or datetime.utcnow() + timedelta(minutes=30)
        self.status = OrderStatus.PENDING
        self.created_at = datetime.utcnow()
        self.filled_amount = Decimal("0")
        self.average_fill_price = None
        self.transaction_hashes: List[str] = []
        self.gas_used = 0
        self.fees_paid = Decimal("0")


class OrderExecutor:
    """
    Professional order execution engine with multi-DEX support.
    
    Handles market orders, limit orders, and risk management controls
    with comprehensive error handling and transaction tracking.
    """
    
    def __init__(self):
        """Initialize the order executor."""
        self.active_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []
        self.max_slippage = Decimal("0.05")  # 5% maximum slippage
        self.min_order_value = Decimal("10")  # $10 minimum order value
        self.max_order_value = Decimal("50000")  # $50,000 maximum order value
        
        logger.info("✅ OrderExecutor initialized successfully")
    
    async def execute_market_order(
        self,
        token_address: str,
        side: OrderSide,
        amount: Decimal,
        slippage_tolerance: Optional[Decimal] = None,
        user_wallet: str = None
    ) -> Dict[str, Any]:
        """
        Execute a market order with immediate execution.
        
        Args:
            token_address: Contract address of the token to trade
            side: BUY or SELL
            amount: Amount to trade (in token units for sell, USD for buy)
            slippage_tolerance: Maximum acceptable slippage (optional)
            user_wallet: User wallet address
            
        Returns:
            Dict containing order execution results
        """
        try:
            logger.info(
                f"🚀 Executing market order: {side.value} {amount} "
                f"of {token_address[:10]}..."
            )
            
            # Generate unique order ID
            order_id = f"market_{uuid.uuid4().hex[:8]}"
            
            # Set default slippage if not provided
            if slippage_tolerance is None:
                slippage_tolerance = Decimal("0.01")  # 1% default
            
            # Create order object
            order = Order(
                order_id=order_id,
                token_address=token_address,
                side=side,
                order_type=OrderType.MARKET,
                amount=amount,
                slippage_tolerance=slippage_tolerance
            )
            
            # Validate the order
            validation_result = await self._validate_order(order, user_wallet)
            if not validation_result["valid"]:
                raise InvalidOrderError(validation_result["error"])
            
            # Add to active orders
            self.active_orders[order_id] = order
            order.status = OrderStatus.EXECUTING
            
            # Execute the order
            execution_result = await self._execute_order_on_dex(order, user_wallet)
            
            # Update order with execution results
            order.status = OrderStatus.FILLED
            order.filled_amount = execution_result["filled_amount"]
            order.average_fill_price = execution_result["fill_price"]
            order.transaction_hashes = execution_result["tx_hashes"]
            order.gas_used = execution_result["gas_used"]
            order.fees_paid = execution_result["fees_paid"]
            
            # Move to order history
            self.order_history.append(order)
            del self.active_orders[order_id]
            
            logger.info(
                f"✅ Market order executed successfully: {order_id} "
                f"- Filled {order.filled_amount} at ${order.average_fill_price}"
            )
            
            return {
                "success": True,
                "order_id": order_id,
                "status": order.status.value,
                "filled_amount": float(order.filled_amount),
                "fill_price": float(order.average_fill_price),
                "total_cost": float(order.filled_amount * order.average_fill_price),
                "fees_paid": float(order.fees_paid),
                "gas_used": order.gas_used,
                "transaction_hashes": order.transaction_hashes,
                "executed_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Market order execution failed: {e}")
            
            # Update order status to failed if it exists
            if order_id in self.active_orders:
                self.active_orders[order_id].status = OrderStatus.FAILED
                self.order_history.append(self.active_orders[order_id])
                del self.active_orders[order_id]
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "order_id": order_id if 'order_id' in locals() else None
            }
    
    async def execute_limit_order(
        self,
        token_address: str,
        side: OrderSide,
        amount: Decimal,
        limit_price: Decimal,
        expires_in_minutes: int = 60,
        user_wallet: str = None
    ) -> Dict[str, Any]:
        """
        Execute a limit order that waits for target price.
        
        Args:
            token_address: Contract address of the token to trade
            side: BUY or SELL
            amount: Amount to trade
            limit_price: Target price for execution
            expires_in_minutes: Order expiration time
            user_wallet: User wallet address
            
        Returns:
            Dict containing order creation results
        """
        try:
            logger.info(
                f"📋 Creating limit order: {side.value} {amount} "
                f"of {token_address[:10]} at ${limit_price}"
            )
            
            # Generate unique order ID
            order_id = f"limit_{uuid.uuid4().hex[:8]}"
            
            # Create order object
            order = Order(
                order_id=order_id,
                token_address=token_address,
                side=side,
                order_type=OrderType.LIMIT,
                amount=amount,
                price=limit_price,
                expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            )
            
            # Validate the order
            validation_result = await self._validate_order(order, user_wallet)
            if not validation_result["valid"]:
                raise InvalidOrderError(validation_result["error"])
            
            # Add to active orders (will be monitored for execution)
            self.active_orders[order_id] = order
            
            logger.info(f"✅ Limit order created successfully: {order_id}")
            
            # Start monitoring this order in background
            asyncio.create_task(self._monitor_limit_order(order_id))
            
            return {
                "success": True,
                "order_id": order_id,
                "status": order.status.value,
                "limit_price": float(limit_price),
                "amount": float(amount),
                "expires_at": order.expires_at.isoformat(),
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Limit order creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an active order.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            Dict containing cancellation results
        """
        try:
            if order_id not in self.active_orders:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found or already completed"
                }
            
            order = self.active_orders[order_id]
            order.status = OrderStatus.CANCELLED
            
            # Move to history
            self.order_history.append(order)
            del self.active_orders[order_id]
            
            logger.info(f"✅ Order cancelled successfully: {order_id}")
            
            return {
                "success": True,
                "order_id": order_id,
                "status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Order cancellation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of a specific order."""
        try:
            # Check active orders first
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                return self._format_order_status(order)
            
            # Check order history
            for order in self.order_history:
                if order.order_id == order_id:
                    return self._format_order_status(order)
            
            return {
                "success": False,
                "error": f"Order {order_id} not found"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting order status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_active_orders(self) -> Dict[str, Any]:
        """Get all active orders."""
        try:
            active_orders = []
            for order in self.active_orders.values():
                active_orders.append(self._format_order_status(order))
            
            return {
                "success": True,
                "active_orders": active_orders,
                "count": len(active_orders)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting active orders: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_order_history(
        self, 
        limit: int = 50,
        status_filter: Optional[OrderStatus] = None
    ) -> Dict[str, Any]:
        """Get order history with optional filtering."""
        try:
            history = self.order_history.copy()
            
            # Apply status filter if provided
            if status_filter:
                history = [o for o in history if o.status == status_filter]
            
            # Sort by creation time (newest first) and limit
            history.sort(key=lambda x: x.created_at, reverse=True)
            history = history[:limit]
            
            formatted_history = [self._format_order_status(order) for order in history]
            
            return {
                "success": True,
                "order_history": formatted_history,
                "count": len(formatted_history),
                "total_orders": len(self.order_history)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting order history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Private helper methods
    
    async def _validate_order(self, order: Order, user_wallet: str) -> Dict[str, Any]:
        """Validate an order before execution."""
        try:
            # Check order amount limits
            if order.amount <= 0:
                return {
                    "valid": False,
                    "error": "Order amount must be greater than zero"
                }
            
            # Check slippage tolerance
            if order.slippage_tolerance > self.max_slippage:
                return {
                    "valid": False,
                    "error": f"Slippage tolerance exceeds maximum ({self.max_slippage})"
                }
            
            # Check order expiration
            if order.expires_at <= datetime.utcnow():
                return {
                    "valid": False,
                    "error": "Order has already expired"
                }
            
            # TODO: Add balance validation
            # balance_check = await self._check_user_balance(user_wallet, order)
            # if not balance_check["sufficient"]:
            #     return {"valid": False, "error": balance_check["error"]}
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"❌ Order validation error: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    async def _execute_order_on_dex(
        self, 
        order: Order, 
        user_wallet: str
    ) -> Dict[str, Any]:
        """Execute order on the DEX."""
        try:
            # Simulate order execution for now
            # In production, this would integrate with actual DEX contracts
            
            # Simulate realistic execution delay
            await asyncio.sleep(0.5)
            
            # Generate mock execution results
            fill_price = Decimal("1650.50")  # Mock ETH price
            gas_used = 150000  # Typical swap gas usage
            fees_paid = Decimal("0.01")  # Mock fees
            
            # Generate mock transaction hash
            tx_hash = f"0x{uuid.uuid4().hex[:40]}"
            
            logger.info(
                f"🔗 Order executed on DEX: {order.order_id} "
                f"- TX: {tx_hash[:10]}..."
            )
            
            return {
                "filled_amount": order.amount,
                "fill_price": fill_price,
                "tx_hashes": [tx_hash],
                "gas_used": gas_used,
                "fees_paid": fees_paid
            }
            
        except Exception as e:
            logger.error(f"❌ DEX execution error: {e}")
            raise OrderExecutionError(f"Failed to execute order on DEX: {str(e)}")
    
    async def _monitor_limit_order(self, order_id: str) -> None:
        """Monitor a limit order for execution conditions."""
        try:
            logger.info(f"👁️ Monitoring limit order: {order_id}")
            
            while order_id in self.active_orders:
                order = self.active_orders[order_id]
                
                # Check if order has expired
                if datetime.utcnow() > order.expires_at:
                    order.status = OrderStatus.EXPIRED
                    self.order_history.append(order)
                    del self.active_orders[order_id]
                    logger.info(f"⏰ Limit order expired: {order_id}")
                    break
                
                # TODO: Check current market price and execute if conditions met
                # current_price = await self._get_current_price(order.token_address)
                # if self._should_execute_limit_order(order, current_price):
                #     await self._execute_limit_order_now(order)
                #     break
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            logger.error(f"❌ Error monitoring limit order {order_id}: {e}")
    
    def _format_order_status(self, order: Order) -> Dict[str, Any]:
        """Format order object for API response."""
        return {
            "order_id": order.order_id,
            "token_address": order.token_address,
            "side": order.side.value,
            "type": order.order_type.value,
            "amount": float(order.amount),
            "price": float(order.price) if order.price else None,
            "status": order.status.value,
            "filled_amount": float(order.filled_amount),
            "average_fill_price": float(order.average_fill_price) if order.average_fill_price else None,
            "slippage_tolerance": float(order.slippage_tolerance),
            "created_at": order.created_at.isoformat(),
            "expires_at": order.expires_at.isoformat(),
            "transaction_hashes": order.transaction_hashes,
            "gas_used": order.gas_used,
            "fees_paid": float(order.fees_paid)
        }


# Global order executor instance
order_executor = OrderExecutor()