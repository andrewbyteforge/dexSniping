"""
Trading Module
File: app/core/trading/__init__.py

Trading engine and order execution components for the DEX Sniper Pro trading bot.
"""

from .order_executor import Order, OrderType, OrderSide, OrderStatus, OrderExecutor, order_executor

__all__ = [
    "Order",
    "OrderType", 
    "OrderSide",
    "OrderStatus",
    "OrderExecutor",
    "order_executor"
]

__version__ = "5.0.0-alpha"
__description__ = "Trading components for DEX Sniper Pro"