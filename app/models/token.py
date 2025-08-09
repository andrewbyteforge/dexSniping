"""
Token Models
File: app/models/token.py

Token data models for the trading system.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

try:
    from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
    from .database import Base
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = object


@dataclass
class TokenInfo:
    """Token information dataclass."""
    address: str
    symbol: str
    name: str
    decimals: int = 18
    total_supply: Optional[Decimal] = None
    circulating_supply: Optional[Decimal] = None
    market_cap_usd: Optional[float] = None
    price_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    liquidity_usd: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "address": self.address,
            "symbol": self.symbol,
            "name": self.name,
            "decimals": self.decimals,
            "total_supply": float(self.total_supply) if self.total_supply else None,
            "circulating_supply": float(self.circulating_supply) if self.circulating_supply else None,
            "market_cap_usd": self.market_cap_usd,
            "price_usd": self.price_usd,
            "volume_24h_usd": self.volume_24h_usd,
            "liquidity_usd": self.liquidity_usd,
            "created_at": self.created_at.isoformat()
        }


if SQLALCHEMY_AVAILABLE:
    class Token(Base):
        """SQLAlchemy Token model."""
        __tablename__ = "tokens"
        
        id = Column(Integer, primary_key=True, index=True)
        address = Column(String(42), unique=True, index=True, nullable=False)
        symbol = Column(String(20), nullable=False)
        name = Column(String(100), nullable=False)
        decimals = Column(Integer, default=18)
        total_supply = Column(String(50))  # Store as string to handle big numbers
        circulating_supply = Column(String(50))
        market_cap_usd = Column(Float)
        price_usd = Column(Float)
        volume_24h_usd = Column(Float)
        liquidity_usd = Column(Float)
        is_verified = Column(Boolean, default=False)
        risk_score = Column(Float)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_token_info(self) -> TokenInfo:
            """Convert to TokenInfo dataclass."""
            return TokenInfo(
                address=self.address,
                symbol=self.symbol,
                name=self.name,
                decimals=self.decimals,
                total_supply=Decimal(self.total_supply) if self.total_supply else None,
                circulating_supply=Decimal(self.circulating_supply) if self.circulating_supply else None,
                market_cap_usd=self.market_cap_usd,
                price_usd=self.price_usd,
                volume_24h_usd=self.volume_24h_usd,
                liquidity_usd=self.liquidity_usd,
                created_at=self.created_at
            )
else:
    # Fallback Token class when SQLAlchemy not available
    class Token:
        """Fallback Token class."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def to_token_info(self) -> TokenInfo:
            """Convert to TokenInfo."""
            return TokenInfo(
                address=getattr(self, 'address', ''),
                symbol=getattr(self, 'symbol', ''),
                name=getattr(self, 'name', ''),
                decimals=getattr(self, 'decimals', 18)
            )
