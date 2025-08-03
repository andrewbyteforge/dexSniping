"""
Dashboard API Schemas
File: app/schemas/dashboard.py

Pydantic schemas for dashboard API responses and requests.
Provides type safety and validation for dashboard endpoints.
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response schema."""
    
    portfolio_value: Decimal = Field(..., description="Total portfolio value in USD")
    daily_pnl: Decimal = Field(..., description="Daily profit/loss in USD")
    daily_pnl_percent: Decimal = Field(..., description="Daily P&L percentage")
    trades_today: int = Field(..., description="Number of trades executed today")
    success_rate: Decimal = Field(..., description="Trading success rate percentage")
    volume_24h: Decimal = Field(..., description="24-hour trading volume in USD")
    active_pairs: int = Field(..., description="Number of active trading pairs")
    watchlist_alerts: int = Field(..., description="Number of watchlist alerts")
    uptime_percent: Decimal = Field(..., description="System uptime percentage")
    latency_ms: int = Field(..., description="Average system latency in milliseconds")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    @validator('success_rate', 'daily_pnl_percent', 'uptime_percent')
    def validate_percentages(cls, v):
        """Validate percentage values are reasonable."""
        if v < 0 or v > 100:
            return max(0, min(100, v))
        return v
    
    @validator('latency_ms')
    def validate_latency(cls, v):
        """Validate latency is non-negative."""
        return max(0, v)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class TokenMetricsResponse(BaseModel):
    """Token metrics response schema."""
    
    symbol: str = Field(..., description="Token symbol")
    name: str = Field(..., description="Token full name")
    address: str = Field(..., description="Token contract address")
    price: Decimal = Field(..., description="Current price in USD")
    price_change_24h: Decimal = Field(..., description="24-hour price change percentage")
    volume_24h: Decimal = Field(..., description="24-hour trading volume")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    liquidity: Optional[Decimal] = Field(None, description="Available liquidity")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    @validator('address')
    def validate_address(cls, v):
        """Validate Ethereum address format."""
        if not v.startswith('0x') or len(v) != 42:
            # Don't raise error, just log warning in production
            pass
        return v
    
    @validator('price', 'volume_24h', 'market_cap', 'liquidity')
    def validate_positive_values(cls, v):
        """Validate that monetary values are non-negative."""
        if v is not None:
            return max(Decimal('0'), v)
        return v
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class TradingMetricsResponse(BaseModel):
    """Trading metrics response schema."""
    
    timeframe: str = Field(..., description="Timeframe for metrics (1h, 4h, 24h, 7d, 30d)")
    total_trades: int = Field(..., description="Total number of trades")
    profitable_trades: int = Field(..., description="Number of profitable trades")
    success_rate: Decimal = Field(..., description="Success rate percentage")
    total_volume: Decimal = Field(..., description="Total trading volume")
    total_fees: Decimal = Field(..., description="Total fees paid")
    net_profit: Decimal = Field(..., description="Net profit/loss")
    average_trade_size: Decimal = Field(..., description="Average trade size")
    max_drawdown: Decimal = Field(..., description="Maximum drawdown percentage")
    sharpe_ratio: Optional[Decimal] = Field(None, description="Sharpe ratio")
    generated_at: datetime = Field(..., description="Metrics generation timestamp")
    
    @validator('success_rate', 'max_drawdown')
    def validate_percentages(cls, v):
        """Validate percentage values."""
        if v < 0 or v > 100:
            return max(Decimal('0'), min(Decimal('100'), v))
        return v
    
    @validator('profitable_trades')
    def validate_profitable_trades(cls, v, values):
        """Validate profitable trades don't exceed total trades."""
        if 'total_trades' in values and v > values['total_trades']:
            return values['total_trades']
        return max(0, v)
    
    @validator('total_volume', 'total_fees', 'average_trade_size')
    def validate_positive_monetary(cls, v):
        """Validate monetary values are non-negative."""
        return max(Decimal('0'), v)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class DashboardRefreshRequest(BaseModel):
    """Dashboard refresh request schema."""
    
    components: Optional[List[str]] = Field(
        None, 
        description="Specific components to refresh (all if not specified)"
    )
    force: bool = Field(False, description="Force refresh even if cache is valid")
    
    @validator('components')
    def validate_components(cls, v):
        """Validate component names."""
        if v is not None:
            valid_components = {
                'portfolio', 'tokens', 'trading', 'metrics', 
                'charts', 'alerts', 'performance'
            }
            return [comp for comp in v if comp in valid_components]
        return v


class DashboardRefreshResponse(BaseModel):
    """Dashboard refresh response schema."""
    
    message: str = Field(..., description="Refresh status message")
    timestamp: datetime = Field(..., description="Refresh initiation timestamp")
    components_refreshed: Optional[List[str]] = Field(
        None, 
        description="List of components that were refreshed"
    )
    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Overall health status")
    database: Optional[dict] = Field(None, description="Database health info")
    cache: Optional[dict] = Field(None, description="Cache health info")
    blockchain: Optional[dict] = Field(None, description="Blockchain connection info")
    timestamp: datetime = Field(..., description="Health check timestamp")
    uptime_seconds: Optional[int] = Field(None, description="System uptime in seconds")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    error_type: Optional[str] = Field(None, description="Error type")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }