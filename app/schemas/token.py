"""
Token Schemas
File: app/schemas/token.py

Pydantic schemas for token data validation.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback BaseModel
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class TokenInfo(BaseModel):
    """Token information schema."""
    address: str
    symbol: str
    name: str
    decimals: int = 18
    total_supply: Optional[str] = None
    circulating_supply: Optional[str] = None
    market_cap_usd: Optional[float] = None
    price_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    liquidity_usd: Optional[float] = None
    is_verified: bool = False
    risk_score: Optional[float] = None
    created_at: Optional[datetime] = None


class TokenCreate(BaseModel):
    """Token creation schema."""
    address: str
    symbol: str
    name: str
    decimals: int = 18
    total_supply: Optional[str] = None


class TokenUpdate(BaseModel):
    """Token update schema."""
    symbol: Optional[str] = None
    name: Optional[str] = None
    market_cap_usd: Optional[float] = None
    price_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    liquidity_usd: Optional[float] = None
    risk_score: Optional[float] = None
