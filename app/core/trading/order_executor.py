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

from app.utils.logger import setup_logger
from app.core.exceptions import (
    TradingError,
    InsufficientFundsError,
    InvalidOrderError,
    OrderExecutionError
)

logger = setup_logger(__name__)


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
        expires_at: Optional[datetime] = None,
        symbol: str = "UNKNOWN"
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
        self.symbol = symbol
    
    def __repr__(self) -> str:
        return f"Order({self.order_id}, {self.side.value}, {self.amount}, {self.symbol})"


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
        user_wallet: str = None,
        symbol: str = "UNKNOWN"
    ) -> Dict[str, Any]:
        """
        Execute a market order with immediate execution.
        
        Args:
            token_address: Contract address of the token to trade
            side: BUY or SELL
            amount: Amount to trade (in token units for sell, USD for buy)
            slippage_tolerance: Maximum acceptable slippage (optional)
            user_wallet: User wallet address
            symbol: Token symbol for logging
            
        Returns:
            Dict containing order execution results
        """
        try:
            logger.info(
                f"🚀 Executing market order: {side.value} {amount} "
                f"of {symbol} ({token_address[:10]}...)"
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
                slippage_tolerance=slippage_tolerance,
                symbol=symbol
            )
            
            # Validate the order
            validation_result = await self._validate_order(order, user_wallet)
            if not validation_result["valid"]:
                raise InvalidOrderError(validation_result["error"])
            
            # Add to active orders
            self.active_orders[order_id] = order
            
            # Simulate order execution (in production, this would execute on DEX)
            execution_result = await self._execute_order_on_dex(order)
            
            # Update order status
            if execution_result["success"]:
                order.status = OrderStatus.FILLED
                order.filled_amount = order.amount
                order.average_fill_price = execution_result.get("fill_price", Decimal("0"))
                order.transaction_hashes = execution_result.get("transaction_hashes", [])
                order.gas_used = execution_result.get("gas_used", 0)
                order.fees_paid = execution_result.get("fees_paid", Decimal("0"))
                
                logger.info(f"✅ Order {order_id} executed successfully")
            else:
                order.status = OrderStatus.FAILED
                logger.error(f"❌ Order {order_id} execution failed: {execution_result.get('error')}")
            
            # Move to history
            self.order_history.append(order)
            del self.active_orders[order_id]
            
            return {
                "success": execution_result["success"],
                "order_id": order_id,
                "status": order.status.value,
                "filled_amount": float(order.filled_amount),
                "average_fill_price": float(order.average_fill_price) if order.average_fill_price else None,
                "transaction_hashes": order.transaction_hashes,
                "gas_used": order.gas_used,
                "fees_paid": float(order.fees_paid),
                "execution_time": execution_result.get("execution_time", 0),
                "message": execution_result.get("message", "Order executed")
            }
            
        except Exception as e:
            logger.error(f"❌ Market order execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id if 'order_id' in locals() else None
            }
    
    async def execute_limit_order(
        self,
        token_address: str,
        side: OrderSide,
        amount: Decimal,
        limit_price: Decimal,
        slippage_tolerance: Optional[Decimal] = None,
        user_wallet: str = None,
        symbol: str = "UNKNOWN"
    ) -> Dict[str, Any]:
        """
        Execute a limit order.
        
        Args:
            token_address: Contract address of the token to trade
            side: BUY or SELL
            amount: Amount to trade
            limit_price: Limit price for the order
            slippage_tolerance: Maximum acceptable slippage (optional)
            user_wallet: User wallet address
            symbol: Token symbol for logging
            
        Returns:
            Dict containing order execution results
        """
        try:
            logger.info(
                f"📝 Creating limit order: {side.value} {amount} "
                f"of {symbol} at {limit_price}"
            )
            
            # Generate unique order ID
            order_id = f"limit_{uuid.uuid4().hex[:8]}"
            
            # Set default slippage if not provided
            if slippage_tolerance is None:
                slippage_tolerance = Decimal("0.005")  # 0.5% default for limit orders
            
            # Create order object
            order = Order(
                order_id=order_id,
                token_address=token_address,
                side=side,
                order_type=OrderType.LIMIT,
                amount=amount,
                price=limit_price,
                slippage_tolerance=slippage_tolerance,
                symbol=symbol
            )
            
            # Validate the order
            validation_result = await self._validate_order(order, user_wallet)
            if not validation_result["valid"]:
                raise InvalidOrderError(validation_result["error"])
            
            # Add to active orders (limit orders stay active until filled/cancelled)
            self.active_orders[order_id] = order
            
            logger.info(f"✅ Limit order {order_id} created and added to active orders")
            
            return {
                "success": True,
                "order_id": order_id,
                "status": order.status.value,
                "message": "Limit order created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Limit order creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": order_id if 'order_id' in locals() else None
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
            history = self.order_history
            
            # Apply status filter if provided
            if status_filter:
                history = [order for order in history if order.status == status_filter]
            
            # Apply limit
            history = history[-limit:] if len(history) > limit else history
            
            # Format for response
            formatted_history = []
            for order in history:
                formatted_history.append(self._format_order_status(order))
            
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
    
    async def _validate_order(self, order: Order, user_wallet: str = None) -> Dict[str, Any]:
        """Validate order parameters."""
        try:
            # Basic validation
            if order.amount <= 0:
                return {"valid": False, "error": "Order amount must be positive"}
            
            if order.slippage_tolerance < 0 or order.slippage_tolerance > self.max_slippage:
                return {"valid": False, "error": f"Slippage tolerance must be between 0 and {self.max_slippage}"}
            
            # Validate token address format (basic check)
            if not order.token_address or len(order.token_address) < 10:
                return {"valid": False, "error": "Invalid token address format"}
            
            # Limit order specific validation
            if order.order_type == OrderType.LIMIT and not order.price:
                return {"valid": False, "error": "Limit orders require a price"}
            
            if order.order_type == OrderType.LIMIT and order.price <= 0:
                return {"valid": False, "error": "Limit price must be positive"}
            
            # Additional validations could be added here (wallet balance, etc.)
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    async def _execute_order_on_dex(self, order: Order) -> Dict[str, Any]:
        """Execute order on DEX (simulated for now)."""
        try:
            # Simulate execution time
            await asyncio.sleep(0.1)
            
            # Simulate execution result
            # In production, this would interact with actual DEX contracts
            execution_result = {
                "success": True,
                "fill_price": order.price if order.price else Decimal("100.0"),  # Mock price
                "transaction_hashes": [f"0x{uuid.uuid4().hex}"],
                "gas_used": 150000,
                "fees_paid": Decimal("0.05"),
                "execution_time": 2500,  # milliseconds
                "message": f"Order executed on mock DEX"
            }
            
            logger.info(f"📈 Mock DEX execution: {order.side.value} {order.amount} {order.symbol}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"❌ DEX execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0
            }
    
    def _format_order_status(self, order: Order) -> Dict[str, Any]:
        """Format order status for API response."""
        return {
            "order_id": order.order_id,
            "token_address": order.token_address,
            "symbol": order.symbol,
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


# Global order executor instance for easy access
order_executor = OrderExecutor()

# Export classes for easy importing
__all__ = [
    "Order",
    "OrderType", 
    "OrderSide",
    "OrderStatus",
    "OrderExecutor",
    "order_executor"
]