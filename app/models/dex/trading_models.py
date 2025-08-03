"""
Trading Database Models
File: app/models/dex/trading_models.py

Complete implementation of trading-related database models with comprehensive
order management, portfolio tracking, and trading analytics support.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, DateTime, Boolean, 
    ForeignKey, Index, Enum as SQLEnum, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime
import json

Base = declarative_base()


# Enums for order management
class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PositionStatus(str, Enum):
    """Position status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FEE = "fee"
    REWARD = "reward"


# Trading Models

class TradingOrder(Base):
    """
    Model for trading orders with comprehensive order management.
    """
    __tablename__ = "trading_orders"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # User identification
    user_wallet = Column(String(255), nullable=False, index=True)
    
    # Order details
    token_address = Column(String(255), nullable=False, index=True)
    token_symbol = Column(String(50), nullable=True)
    side = Column(SQLEnum(OrderSide), nullable=False)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    
    # Quantities and prices
    amount = Column(Numeric(precision=36, scale=18), nullable=False)
    filled_amount = Column(Numeric(precision=36, scale=18), default=0, nullable=False)
    price = Column(Numeric(precision=36, scale=18), nullable=True)  # NULL for market orders
    average_fill_price = Column(Numeric(precision=36, scale=18), nullable=True)
    
    # Order parameters
    slippage_tolerance = Column(Numeric(precision=5, scale=4), default=0.01, nullable=False)
    gas_limit = Column(Integer, nullable=True)
    gas_price = Column(Numeric(precision=20, scale=0), nullable=True)  # Wei
    
    # DEX information
    dex_name = Column(String(50), nullable=False)
    pair_address = Column(String(255), nullable=True)
    router_address = Column(String(255), nullable=True)
    
    # Execution details
    transaction_hash = Column(String(255), nullable=True, index=True)
    block_number = Column(Integer, nullable=True)
    transaction_fee = Column(Numeric(precision=36, scale=18), nullable=True)
    
    # Risk management
    stop_loss_price = Column(Numeric(precision=36, scale=18), nullable=True)
    take_profit_price = Column(Numeric(precision=36, scale=18), nullable=True)
    trailing_stop_distance = Column(Numeric(precision=10, scale=4), nullable=True)  # Percentage
    
    # Timing
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    order_metadata = Column(JSON, nullable=True)  # Strategy info, source, etc.
    error_message = Column(Text, nullable=True)
    
    # Relationships
    fills = relationship("OrderFill", back_populates="order", cascade="all, delete-orphan")
    position = relationship("TradingPosition", back_populates="orders", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_orders_user_status', 'user_wallet', 'status'),
        Index('idx_orders_token_created', 'token_address', 'created_at'),
        Index('idx_orders_dex_status', 'dex_name', 'status'),
        Index('idx_orders_created_status', 'created_at', 'status'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_wallet': self.user_wallet,
            'token_address': self.token_address,
            'token_symbol': self.token_symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'amount': str(self.amount),
            'filled_amount': str(self.filled_amount),
            'price': str(self.price) if self.price else None,
            'average_fill_price': str(self.average_fill_price) if self.average_fill_price else None,
            'slippage_tolerance': float(self.slippage_tolerance),
            'dex_name': self.dex_name,
            'transaction_hash': self.transaction_hash,
            'stop_loss_price': str(self.stop_loss_price) if self.stop_loss_price else None,
            'take_profit_price': str(self.take_profit_price) if self.take_profit_price else None,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'order_metadata': self.order_metadata
        }
    
    @property
    def fill_percentage(self) -> float:
        """Calculate fill percentage."""
        if not self.amount or self.amount == 0:
            return 0.0
        return float(self.filled_amount / self.amount * 100)
    
    @property
    def is_active(self) -> bool:
        """Check if order is active."""
        return self.status in [OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]


class OrderFill(Base):
    """
    Model for order fill records with detailed execution tracking.
    """
    __tablename__ = "order_fills"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    fill_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign key to order
    order_id = Column(Integer, ForeignKey('trading_orders.id'), nullable=False, index=True)
    
    # Fill details
    amount = Column(Numeric(precision=36, scale=18), nullable=False)
    price = Column(Numeric(precision=36, scale=18), nullable=False)
    total_value = Column(Numeric(precision=36, scale=18), nullable=False)
    
    # Execution details
    transaction_hash = Column(String(255), nullable=False, index=True)
    block_number = Column(Integer, nullable=False)
    transaction_index = Column(Integer, nullable=True)
    log_index = Column(Integer, nullable=True)
    
    # Fees
    gas_used = Column(Integer, nullable=True)
    gas_price = Column(Numeric(precision=20, scale=0), nullable=True)
    transaction_fee = Column(Numeric(precision=36, scale=18), nullable=True)
    dex_fee = Column(Numeric(precision=36, scale=18), nullable=True)
    
    # Timing
    filled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Additional data
    fill_metadata = Column(JSON, nullable=True)
    
    # Relationship
    order = relationship("TradingOrder", back_populates="fills")
    
    # Indexes
    __table_args__ = (
        Index('idx_fills_order_filled', 'order_id', 'filled_at'),
        Index('idx_fills_tx_hash', 'transaction_hash'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fill to dictionary."""
        return {
            'id': self.id,
            'fill_id': self.fill_id,
            'order_id': self.order_id,
            'amount': str(self.amount),
            'price': str(self.price),
            'total_value': str(self.total_value),
            'transaction_hash': self.transaction_hash,
            'block_number': self.block_number,
            'transaction_fee': str(self.transaction_fee) if self.transaction_fee else None,
            'filled_at': self.filled_at.isoformat(),
            'fill_metadata': self.fill_metadata
        }


class TradingPosition(Base):
    """
    Model for trading positions with comprehensive position tracking.
    """
    __tablename__ = "trading_positions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # User identification
    user_wallet = Column(String(255), nullable=False, index=True)
    
    # Position details
    token_address = Column(String(255), nullable=False, index=True)
    token_symbol = Column(String(50), nullable=True)
    status = Column(SQLEnum(PositionStatus), default=PositionStatus.OPEN, nullable=False, index=True)
    
    # Position quantities
    total_quantity = Column(Numeric(precision=36, scale=18), nullable=False)
    remaining_quantity = Column(Numeric(precision=36, scale=18), nullable=False)
    average_entry_price = Column(Numeric(precision=36, scale=18), nullable=False)
    average_exit_price = Column(Numeric(precision=36, scale=18), nullable=True)
    
    # Position value
    total_cost = Column(Numeric(precision=36, scale=18), nullable=False)
    total_fees = Column(Numeric(precision=36, scale=18), default=0, nullable=False)
    realized_pnl = Column(Numeric(precision=36, scale=18), default=0, nullable=False)
    unrealized_pnl = Column(Numeric(precision=36, scale=18), default=0, nullable=False)
    
    # Risk management
    stop_loss_price = Column(Numeric(precision=36, scale=18), nullable=True)
    take_profit_price = Column(Numeric(precision=36, scale=18), nullable=True)
    max_drawdown = Column(Numeric(precision=10, scale=4), default=0, nullable=False)  # Percentage
    
    # Timing
    opened_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional data
    strategy_name = Column(String(100), nullable=True)
    position_metadata = Column(JSON, nullable=True)
    
    # Relationships
    orders = relationship("TradingOrder", back_populates="position")
    transactions = relationship("PortfolioTransaction", back_populates="position")
    
    # Indexes
    __table_args__ = (
        Index('idx_positions_user_status', 'user_wallet', 'status'),
        Index('idx_positions_token_opened', 'token_address', 'opened_at'),
        Index('idx_positions_strategy', 'strategy_name'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary."""
        return {
            'id': self.id,
            'position_id': self.position_id,
            'user_wallet': self.user_wallet,
            'token_address': self.token_address,
            'token_symbol': self.token_symbol,
            'status': self.status.value,
            'total_quantity': str(self.total_quantity),
            'remaining_quantity': str(self.remaining_quantity),
            'average_entry_price': str(self.average_entry_price),
            'average_exit_price': str(self.average_exit_price) if self.average_exit_price else None,
            'total_cost': str(self.total_cost),
            'realized_pnl': str(self.realized_pnl),
            'unrealized_pnl': str(self.unrealized_pnl),
            'stop_loss_price': str(self.stop_loss_price) if self.stop_loss_price else None,
            'take_profit_price': str(self.take_profit_price) if self.take_profit_price else None,
            'opened_at': self.opened_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'strategy_name': self.strategy_name,
            'position_metadata': self.position_metadata
        }
    
    @property
    def is_open(self) -> bool:
        """Check if position is open."""
        return self.status == PositionStatus.OPEN
    
    @property
    def total_pnl(self) -> Decimal:
        """Calculate total PnL."""
        return self.realized_pnl + self.unrealized_pnl
    
    @property
    def roi_percentage(self) -> float:
        """Calculate ROI percentage."""
        if not self.total_cost or self.total_cost == 0:
            return 0.0
        return float(self.total_pnl / self.total_cost * 100)


class PortfolioTransaction(Base):
    """
    Model for portfolio transactions with comprehensive transaction tracking.
    """
    __tablename__ = "portfolio_transactions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # User identification
    user_wallet = Column(String(255), nullable=False, index=True)
    
    # Transaction details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    token_address = Column(String(255), nullable=False, index=True)
    token_symbol = Column(String(50), nullable=True)
    
    # Amounts
    amount = Column(Numeric(precision=36, scale=18), nullable=False)
    price_per_token = Column(Numeric(precision=36, scale=18), nullable=True)
    total_value_usd = Column(Numeric(precision=36, scale=18), nullable=True)
    
    # Blockchain details
    transaction_hash = Column(String(255), nullable=True, index=True)
    block_number = Column(Integer, nullable=True)
    dex_name = Column(String(50), nullable=True)
    
    # Fees
    gas_fee = Column(Numeric(precision=36, scale=18), nullable=True)
    dex_fee = Column(Numeric(precision=36, scale=18), nullable=True)
    slippage = Column(Numeric(precision=10, scale=4), nullable=True)  # Percentage
    
    # Position reference
    position_id = Column(Integer, ForeignKey('trading_positions.id'), nullable=True, index=True)
    
    # Timing
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Additional data
    transaction_metadata = Column(JSON, nullable=True)
    
    # Relationship
    position = relationship("TradingPosition", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_transactions_user_type', 'user_wallet', 'transaction_type'),
        Index('idx_transactions_token_executed', 'token_address', 'executed_at'),
        Index('idx_transactions_position', 'position_id'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'user_wallet': self.user_wallet,
            'transaction_type': self.transaction_type.value,
            'token_address': self.token_address,
            'token_symbol': self.token_symbol,
            'amount': str(self.amount),
            'price_per_token': str(self.price_per_token) if self.price_per_token else None,
            'total_value_usd': str(self.total_value_usd) if self.total_value_usd else None,
            'transaction_hash': self.transaction_hash,
            'dex_name': self.dex_name,
            'gas_fee': str(self.gas_fee) if self.gas_fee else None,
            'dex_fee': str(self.dex_fee) if self.dex_fee else None,
            'executed_at': self.executed_at.isoformat(),
            'transaction_metadata': self.transaction_metadata
        }


class TradingStrategy(Base):
    """
    Model for trading strategies with comprehensive strategy management.
    """
    __tablename__ = "trading_strategies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # User identification
    user_wallet = Column(String(255), nullable=False, index=True)
    
    # Strategy details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), nullable=False, index=True)  # dca, grid, arbitrage, etc.
    status = Column(String(20), default="active", nullable=False, index=True)
    
    # Strategy parameters
    parameters = Column(JSON, nullable=False)  # Strategy-specific parameters
    risk_parameters = Column(JSON, nullable=True)  # Risk management settings
    
    # Performance tracking
    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    total_volume = Column(Numeric(precision=36, scale=18), default=0, nullable=False)
    total_pnl = Column(Numeric(precision=36, scale=18), default=0, nullable=False)
    max_drawdown = Column(Numeric(precision=10, scale=4), default=0, nullable=False)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_strategies_user_type', 'user_wallet', 'strategy_type'),
        Index('idx_strategies_status', 'status'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary."""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'user_wallet': self.user_wallet,
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type,
            'status': self.status,
            'parameters': self.parameters,
            'risk_parameters': self.risk_parameters,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': round(win_rate, 2),
            'total_volume': str(self.total_volume),
            'total_pnl': str(self.total_pnl),
            'max_drawdown': float(self.max_drawdown),
            'created_at': self.created_at.isoformat(),
            'last_executed_at': self.last_executed_at.isoformat() if self.last_executed_at else None
        }


class RiskLimit(Base):
    """
    Model for user risk limits and controls.
    """
    __tablename__ = "risk_limits"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User identification
    user_wallet = Column(String(255), nullable=False, index=True)
    
    # Position limits
    max_position_size = Column(Numeric(precision=36, scale=18), nullable=True)  # USD value
    max_position_percentage = Column(Numeric(precision=5, scale=2), nullable=True)  # % of portfolio
    max_open_positions = Column(Integer, nullable=True)
    
    # Risk limits
    max_daily_loss = Column(Numeric(precision=36, scale=18), nullable=True)
    max_drawdown_percentage = Column(Numeric(precision=5, scale=2), nullable=True)
    stop_loss_percentage = Column(Numeric(precision=5, scale=2), nullable=True)
    
    # Trading limits
    max_daily_trades = Column(Integer, nullable=True)
    max_slippage = Column(Numeric(precision=5, scale=4), nullable=True)
    min_liquidity_usd = Column(Numeric(precision=36, scale=18), nullable=True)
    
    # Token restrictions
    blacklisted_tokens = Column(JSON, nullable=True)  # Array of token addresses
    whitelisted_tokens = Column(JSON, nullable=True)  # Array of token addresses
    max_risk_score = Column(Numeric(precision=4, scale=2), nullable=True)
    
    # Settings
    auto_stop_loss = Column(Boolean, default=True, nullable=False)
    auto_take_profit = Column(Boolean, default=False, nullable=False)
    emergency_stop = Column(Boolean, default=False, nullable=False)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_wallet', name='uq_risk_limits_user_wallet'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk limits to dictionary."""
        return {
            'id': self.id,
            'user_wallet': self.user_wallet,
            'max_position_size': str(self.max_position_size) if self.max_position_size else None,
            'max_position_percentage': float(self.max_position_percentage) if self.max_position_percentage else None,
            'max_open_positions': self.max_open_positions,
            'max_daily_loss': str(self.max_daily_loss) if self.max_daily_loss else None,
            'max_drawdown_percentage': float(self.max_drawdown_percentage) if self.max_drawdown_percentage else None,
            'stop_loss_percentage': float(self.stop_loss_percentage) if self.stop_loss_percentage else None,
            'max_daily_trades': self.max_daily_trades,
            'max_slippage': float(self.max_slippage) if self.max_slippage else None,
            'min_liquidity_usd': str(self.min_liquidity_usd) if self.min_liquidity_usd else None,
            'blacklisted_tokens': self.blacklisted_tokens,
            'whitelisted_tokens': self.whitelisted_tokens,
            'max_risk_score': float(self.max_risk_score) if self.max_risk_score else None,
            'auto_stop_loss': self.auto_stop_loss,
            'auto_take_profit': self.auto_take_profit,
            'emergency_stop': self.emergency_stop,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Utility functions for model operations

async def create_order(
    session,
    user_wallet: str,
    token_address: str,
    side: OrderSide,
    amount: Decimal,
    order_type: OrderType = OrderType.MARKET,
    **kwargs
) -> TradingOrder:
    """Create a new trading order."""
    try:
        import uuid
        order_id = f"order_{uuid.uuid4().hex[:16]}"
        
        order = TradingOrder(
            order_id=order_id,
            user_wallet=user_wallet,
            token_address=token_address,
            side=side,
            order_type=order_type,
            amount=amount,
            **kwargs
        )
        
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        return order
        
    except Exception as e:
        await session.rollback()
        raise Exception(f"Failed to create order: {e}")


async def get_user_positions(
    session,
    user_wallet: str,
    status: Optional[PositionStatus] = None
) -> List[TradingPosition]:
    """Get user's trading positions."""
    try:
        query = session.query(TradingPosition).filter(
            TradingPosition.user_wallet == user_wallet
        )
        
        if status:
            query = query.filter(TradingPosition.status == status)
        
        positions = await query.all()
        return positions
        
    except Exception as e:
        raise Exception(f"Failed to get user positions: {e}")


async def calculate_portfolio_metrics(
    session,
    user_wallet: str
) -> Dict[str, Any]:
    """Calculate comprehensive portfolio metrics."""
    try:
        # Get all positions
        positions = await get_user_positions(session, user_wallet)
        
        # Calculate metrics
        total_value = sum(pos.total_cost for pos in positions)
        total_pnl = sum(pos.total_pnl for pos in positions)
        open_positions = len([pos for pos in positions if pos.is_open])
        
        win_rate = 0
        closed_positions = [pos for pos in positions if pos.status == PositionStatus.CLOSED]
        if closed_positions:
            winning_positions = len([pos for pos in closed_positions if pos.total_pnl > 0])
            win_rate = winning_positions / len(closed_positions) * 100
        
        return {
            'total_positions': len(positions),
            'open_positions': open_positions,
            'closed_positions': len(closed_positions),
            'total_value': str(total_value),
            'total_pnl': str(total_pnl),
            'roi_percentage': float(total_pnl / total_value * 100) if total_value > 0 else 0,
            'win_rate': round(win_rate, 2)
        }
        
    except Exception as e:
        raise Exception(f"Failed to calculate portfolio metrics: {e}")