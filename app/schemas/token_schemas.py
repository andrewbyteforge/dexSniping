"""
File: app/schemas/token_schemas.py

Pydantic schemas for token API responses and requests.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal


class TokenBase(BaseModel):
    """Base token schema with common fields."""
    address: str = Field(..., description="Token contract address")
    network: str = Field(..., description="Blockchain network name")
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    decimals: int = Field(..., description="Token decimal places")


class TokenInfo(TokenBase):
    """Token information schema."""
    total_supply: Optional[str] = Field(None, description="Total token supply")
    verified: bool = Field(False, description="Whether contract is verified")
    created_at: Optional[datetime] = Field(None, description="Contract creation timestamp")
    creator: Optional[str] = Field(None, description="Contract creator address")


class LiquiditySource(BaseModel):
    """Liquidity source information."""
    dex: str = Field(..., description="DEX name")
    pair_address: str = Field(..., description="Trading pair address")
    token0: str = Field(..., description="First token in pair")
    token1: str = Field(..., description="Second token in pair")
    reserve0: str = Field(..., description="Reserve of first token")
    reserve1: str = Field(..., description="Reserve of second token")
    liquidity_usd: float = Field(..., description="Liquidity value in USD")
    volume_24h_usd: float = Field(..., description="24-hour trading volume in USD")
    price_usd: float = Field(..., description="Token price in USD")


class LiquidityInfo(BaseModel):
    """Token liquidity information."""
    total_liquidity_usd: float = Field(..., description="Total liquidity across all DEXs")
    price_usd: Optional[float] = Field(None, description="Current token price in USD")
    liquidity_sources: List[LiquiditySource] = Field(default_factory=list, description="Individual liquidity sources")


class RiskFactors(BaseModel):
    """Individual risk factor scores."""
    liquidity_risk: float = Field(..., ge=0, le=10, description="Liquidity risk score (0-10)")
    contract_risk: float = Field(..., ge=0, le=10, description="Contract security risk score (0-10)")
    market_risk: float