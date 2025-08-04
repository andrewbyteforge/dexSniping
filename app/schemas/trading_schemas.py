"""
Trading API Response Models
File: app/schemas/trading_schemas.py

Comprehensive Pydantic models for trading API responses.
Provides type safety and validation for all trading-related data.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from pydantic import BaseModel, Field, validator


class TradingMode(str, Enum):
    """Trading mode enumeration."""
    MANUAL = "manual"
    SEMI_AUTOMATED = "semi_automated"
    FULLY_AUTOMATED = "fully_automated"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


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


class TradingSessionStatus(str, Enum):
    """Trading session status enumeration."""
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


class WalletInfo(BaseModel):
    """Wallet information model."""
    address: str = Field(..., description="Wallet address")
    network: str = Field(..., description="Blockchain network")
    balance_eth: Decimal = Field(..., description="ETH balance")
    balance_usd: Decimal = Field(..., description="USD balance equivalent")
    connected_at: datetime = Field(..., description="Connection timestamp")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class PositionInfo(BaseModel):
    """Position information model."""
    token_address: str = Field(..., description="Token contract address")
    token_symbol: str = Field(..., description="Token symbol")
    quantity: Decimal = Field(..., description="Position quantity")
    entry_price: Decimal = Field(..., description="Average entry price")
    current_price: Decimal = Field(..., description="Current market price")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    unrealized_pnl_percent: Decimal = Field(..., description="Unrealized P&L percentage")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class OrderInfo(BaseModel):
    """Order information model."""
    order_id: str = Field(..., description="Unique order identifier")
    token_address: str = Field(..., description="Token contract address")
    token_symbol: str = Field(..., description="Token symbol")
    side: OrderSide = Field(..., description="Order side")
    order_type: OrderType = Field(..., description="Order type")
    quantity: Decimal = Field(..., description="Order quantity")
    price: Optional[Decimal] = Field(None, description="Order price")
    filled_quantity: Decimal = Field(Decimal("0"), description="Filled quantity")
    status: OrderStatus = Field(..., description="Order status")
    created_at: datetime = Field(..., description="Order creation time")
    updated_at: datetime = Field(..., description="Last update time")
    expires_at: Optional[datetime] = Field(None, description="Order expiration time")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class TradingStats(BaseModel):
    """Trading statistics model."""
    total_trades: int = Field(0, description="Total number of trades")
    successful_trades: int = Field(0, description="Number of successful trades")
    failed_trades: int = Field(0, description="Number of failed trades")
    total_volume: Decimal = Field(Decimal("0"), description="Total trading volume")
    total_pnl: Decimal = Field(Decimal("0"), description="Total profit/loss")
    total_pnl_percent: Decimal = Field(Decimal("0"), description="Total P&L percentage")
    win_rate: Decimal = Field(Decimal("0"), description="Win rate percentage")
    average_trade_size: Decimal = Field(Decimal("0"), description="Average trade size")
    largest_win: Decimal = Field(Decimal("0"), description="Largest winning trade")
    largest_loss: Decimal = Field(Decimal("0"), description="Largest losing trade")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class TradingSessionResponse(BaseModel):
    """Trading session response model."""
    session_id: str = Field(..., description="Unique session identifier")
    status: TradingSessionStatus = Field(..., description="Session status")
    trading_mode: TradingMode = Field(..., description="Trading mode")
    wallet_info: Optional[WalletInfo] = Field(None, description="Connected wallet information")
    active_positions: List[PositionInfo] = Field([], description="Active trading positions")
    active_orders: List[OrderInfo] = Field([], description="Active orders")
    trading_stats: TradingStats = Field(..., description="Trading statistics")
    session_started_at: Optional[datetime] = Field(None, description="Session start time")
    last_activity_at: datetime = Field(..., description="Last activity timestamp")
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error_code: Optional[str] = Field(None, description="Error code if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TradeExecutionRequest(BaseModel):
    """Trade execution request model."""
    token_address: str = Field(..., description="Token contract address")
    side: OrderSide = Field(..., description="Order side")
    order_type: OrderType = Field(OrderType.MARKET, description="Order type")
    quantity: Decimal = Field(..., gt=0, description="Trade quantity")
    price: Optional[Decimal] = Field(None, description="Price for limit orders")
    slippage_tolerance: Decimal = Field(Decimal("0.01"), ge=0, le=0.1, description="Slippage tolerance")
    
    @validator('token_address')
    def validate_token_address(cls, v):
        """Validate Ethereum address format."""
        if not v or len(v) != 42 or not v.startswith('0x'):
            raise ValueError('Invalid token address format')
        return v.lower()
    
    @validator('price')
    def validate_price_for_limit_orders(cls, v, values):
        """Validate price is provided for limit orders."""
        if values.get('order_type') == OrderType.LIMIT and v is None:
            raise ValueError('Price is required for limit orders')
        return v
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class TradeExecutionResponse(BaseModel):
    """Trade execution response model."""
    success: bool = Field(..., description="Execution success status")
    order_id: Optional[str] = Field(None, description="Created order ID")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    executed_quantity: Decimal = Field(Decimal("0"), description="Actually executed quantity")
    executed_price: Optional[Decimal] = Field(None, description="Execution price")
    gas_used: Optional[int] = Field(None, description="Gas used for transaction")
    gas_price: Optional[Decimal] = Field(None, description="Gas price used")
    total_cost: Optional[Decimal] = Field(None, description="Total transaction cost")
    message: str = Field(..., description="Execution message")
    error_details: Optional[str] = Field(None, description="Error details if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class PortfolioSummary(BaseModel):
    """Portfolio summary model."""
    total_value_usd: Decimal = Field(..., description="Total portfolio value in USD")
    total_value_eth: Decimal = Field(..., description="Total portfolio value in ETH")
    available_balance: Decimal = Field(..., description="Available balance for trading")
    positions_count: int = Field(..., description="Number of active positions")
    daily_pnl: Decimal = Field(..., description="Daily profit/loss")
    daily_pnl_percent: Decimal = Field(..., description="Daily P&L percentage")
    positions: List[PositionInfo] = Field([], description="Position details")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class MarketDataPoint(BaseModel):
    """Market data point model."""
    timestamp: datetime = Field(..., description="Data timestamp")
    price: Decimal = Field(..., description="Token price")
    volume_24h: Decimal = Field(..., description="24h trading volume")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    liquidity: Optional[Decimal] = Field(None, description="Liquidity pool size")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class TokenMetrics(BaseModel):
    """Token metrics model."""
    token_address: str = Field(..., description="Token contract address")
    symbol: str = Field(..., description="Token symbol")
    name: str = Field(..., description="Token name")
    current_price: Decimal = Field(..., description="Current price")
    price_change_24h: Decimal = Field(..., description="24h price change percentage")
    volume_24h: Decimal = Field(..., description="24h trading volume")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    total_supply: Optional[Decimal] = Field(None, description="Total token supply")
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    liquidity_score: Optional[Decimal] = Field(None, description="Liquidity score 0-100")
    risk_score: Optional[Decimal] = Field(None, description="Risk assessment score 0-100")
    
    class Config:
        json_encoders = {
            Decimal: str
        }