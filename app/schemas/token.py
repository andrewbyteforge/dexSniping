"""
File: app/schemas/token.py

Pydantic schemas for token API responses and requests.
This file provides the schemas that were being imported in the API endpoints.
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
    market_risk: float = Field(..., ge=0, le=10, description="Market manipulation risk score (0-10)")
    social_risk: float = Field(..., ge=0, le=10, description="Social sentiment risk score (0-10)")
    technical_risk: float = Field(..., ge=0, le=10, description="Technical implementation risk score (0-10)")


class RiskAssessment(BaseModel):
    """Token risk assessment information."""
    risk_score: float = Field(..., ge=0, le=10, description="Overall risk score (0-10)")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    confidence: float = Field(..., ge=0, le=1, description="Assessment confidence (0-1)")
    risk_factors: Optional[RiskFactors] = Field(None, description="Individual risk factor breakdown")
    warnings: List[str] = Field(default_factory=list, description="Risk warnings")
    recommendations: List[str] = Field(default_factory=list, description="Trading recommendations")
    assessment_timestamp: datetime = Field(..., description="When assessment was performed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional assessment data")


class TokenResponse(TokenBase):
    """Complete token response schema."""
    total_supply: Optional[str] = Field(None, description="Total token supply")
    verified: bool = Field(False, description="Whether contract is verified")
    created_at: Optional[datetime] = Field(None, description="Contract creation timestamp")
    creator: Optional[str] = Field(None, description="Contract creator address")
    liquidity: Optional[LiquidityInfo] = Field(None, description="Liquidity information")
    risk: Optional[RiskAssessment] = Field(None, description="Risk assessment")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenDiscoveryResponse(BaseModel):
    """Response schema for token discovery endpoints."""
    tokens: List[Dict[str, Any]] = Field(..., description="List of discovered tokens")
    total_found: int = Field(..., description="Total tokens found in scan")
    total_filtered: int = Field(..., description="Total tokens after filtering")
    networks_scanned: List[str] = Field(..., description="Networks that were scanned")
    block_offset: int = Field(..., description="Block offset used for scanning")
    min_liquidity_filter: float = Field(..., description="Minimum liquidity filter applied")
    pagination: Dict[str, int] = Field(..., description="Pagination information")


class TokenRiskResponse(BaseModel):
    """Response schema for token risk assessment."""
    token_address: str = Field(..., description="Token contract address")
    network: str = Field(..., description="Blockchain network")
    risk_score: float = Field(..., ge=0, le=10, description="Overall risk score")
    risk_level: str = Field(..., description="Risk level category")
    confidence: float = Field(..., ge=0, le=1, description="Assessment confidence")
    risk_factors: Optional[RiskFactors] = Field(None, description="Individual risk factors")
    warnings: List[str] = Field(default_factory=list, description="Risk warnings")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    assessment_timestamp: datetime = Field(..., description="Assessment timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LiquidityMetrics(BaseModel):
    """Liquidity analysis metrics."""
    liquidity_concentration: float = Field(..., description="Liquidity concentration index")
    volume_liquidity_ratio: float = Field(..., description="24h volume to liquidity ratio")
    dex_count: int = Field(..., description="Number of DEXs with liquidity")
    largest_pool_percentage: float = Field(..., description="Percentage of liquidity in largest pool")


class LiquidityResponse(BaseModel):
    """Response schema for token liquidity analysis."""
    token_address: str = Field(..., description="Token contract address")
    network: str = Field(..., description="Blockchain network")
    current_price_usd: Optional[float] = Field(None, description="Current price in USD")
    total_liquidity_usd: float = Field(..., description="Total liquidity in USD")
    total_volume_24h_usd: float = Field(..., description="Total 24h volume in USD")
    liquidity_sources: List[LiquiditySource] = Field(..., description="Individual liquidity sources")
    metrics: LiquidityMetrics = Field(..., description="Liquidity analysis metrics")
    historical: Optional[Dict[str, Any]] = Field(None, description="Historical liquidity data")


class NewTokenScanRequest(BaseModel):
    """Request schema for manual token scanning."""
    networks: List[str] = Field(..., description="Networks to scan")
    from_block_offset: int = Field(default=10, ge=1, le=100, description="Blocks back from latest to start scan")
    to_block_offset: int = Field(default=0, ge=0, le=50, description="Blocks back from latest to end scan")
    min_liquidity_usd: Optional[float] = Field(None, ge=0, description="Minimum liquidity filter")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")
    
    @validator('networks')
    def validate_networks(cls, v):
        if not v:
            raise ValueError("At least one network must be specified")
        return v
    
    @validator('to_block_offset')
    def validate_block_range(cls, v, values):
        if 'from_block_offset' in values and v >= values['from_block_offset']:
            raise ValueError("to_block_offset must be less than from_block_offset")
        return v