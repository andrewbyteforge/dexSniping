"""
File: app/models/token.py

Database models for token storage and discovery tracking.
FIXED: Removed 'metadata' column names to avoid SQLAlchemy conflict.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.database import Base


class Token(Base):
    """
    Model for storing discovered tokens.
    """
    __tablename__ = "tokens"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Token identification
    address = Column(String(255), nullable=False, index=True)
    network = Column(String(50), nullable=False, index=True)
    
    # Token metadata
    name = Column(String(255), nullable=False)
    symbol = Column(String(50), nullable=False, index=True)
    decimals = Column(Integer, nullable=False)
    total_supply = Column(Numeric(precision=78, scale=0), nullable=True)  # Support very large numbers
    
    # Discovery information
    discovered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    discovery_block = Column(Integer, nullable=True)
    discovery_transaction = Column(String(255), nullable=True)
    creator_address = Column(String(255), nullable=True, index=True)
    
    # Contract information
    is_verified = Column(Boolean, default=False, nullable=False)
    contract_created_at = Column(DateTime(timezone=True), nullable=True)
    
    # Risk and analysis
    initial_risk_score = Column(Numeric(precision=4, scale=2), nullable=True)  # 0.00-10.00
    current_risk_score = Column(Numeric(precision=4, scale=2), nullable=True)
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Liquidity tracking
    initial_liquidity_usd = Column(Numeric(precision=20, scale=2), nullable=True)
    current_liquidity_usd = Column(Numeric(precision=20, scale=2), nullable=True)
    liquidity_pools_count = Column(Integer, default=0)
    
    # Trading status
    is_tradeable = Column(Boolean, default=True, nullable=False)
    is_honeypot = Column(Boolean, default=False, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    
    # Additional data (renamed from metadata to avoid SQLAlchemy conflict)
    additional_data = Column(Text, nullable=True)  # JSON string for additional data
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    price_history = relationship("TokenPrice", back_populates="token", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="token", cascade="all, delete-orphan")
    discovery_sessions = relationship("DiscoverySession", back_populates="tokens")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_token_network_address', 'network', 'address'),
        Index('idx_token_discovered_at', 'discovered_at'),
        Index('idx_token_symbol_network', 'symbol', 'network'),
        Index('idx_token_risk_score', 'current_risk_score'),
        Index('idx_token_creator', 'creator_address'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'address': self.address,
            'network': self.network,
            'name': self.name,
            'symbol': self.symbol,
            'decimals': self.decimals,
            'total_supply': str(self.total_supply) if self.total_supply else None,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'discovery_block': self.discovery_block,
            'creator_address': self.creator_address,
            'is_verified': self.is_verified,
            'contract_created_at': self.contract_created_at.isoformat() if self.contract_created_at else None,
            'current_risk_score': float(self.current_risk_score) if self.current_risk_score else None,
            'risk_level': self.risk_level,
            'current_liquidity_usd': float(self.current_liquidity_usd) if self.current_liquidity_usd else None,
            'liquidity_pools_count': self.liquidity_pools_count,
            'is_tradeable': self.is_tradeable,
            'is_honeypot': self.is_honeypot,
            'is_flagged': self.is_flagged,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Token(address='{self.address}', symbol='{self.symbol}', network='{self.network}')>"


class TokenPrice(Base):
    """
    Model for storing token price history.
    """
    __tablename__ = "token_prices"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to token
    token_id = Column(Integer, ForeignKey('tokens.id'), nullable=False, index=True)
    
    # Price data
    price_usd = Column(Numeric(precision=30, scale=18), nullable=False)  # Support very precise prices
    volume_24h_usd = Column(Numeric(precision=20, scale=2), nullable=True)
    market_cap_usd = Column(Numeric(precision=20, scale=2), nullable=True)
    liquidity_usd = Column(Numeric(precision=20, scale=2), nullable=True)
    
    # DEX information
    dex_name = Column(String(50), nullable=True)
    pair_address = Column(String(255), nullable=True)
    
    # Price change data
    price_change_1h = Column(Numeric(precision=10, scale=4), nullable=True)  # Percentage
    price_change_24h = Column(Numeric(precision=10, scale=4), nullable=True)
    price_change_7d = Column(Numeric(precision=10, scale=4), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    token = relationship("Token", back_populates="price_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_price_token_timestamp', 'token_id', 'timestamp'),
        Index('idx_price_timestamp', 'timestamp'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'token_id': self.token_id,
            'price_usd': str(self.price_usd),
            'volume_24h_usd': float(self.volume_24h_usd) if self.volume_24h_usd else None,
            'market_cap_usd': float(self.market_cap_usd) if self.market_cap_usd else None,
            'liquidity_usd': float(self.liquidity_usd) if self.liquidity_usd else None,
            'dex_name': self.dex_name,
            'pair_address': self.pair_address,
            'price_change_1h': float(self.price_change_1h) if self.price_change_1h else None,
            'price_change_24h': float(self.price_change_24h) if self.price_change_24h else None,
            'price_change_7d': float(self.price_change_7d) if self.price_change_7d else None,
            'timestamp': self.timestamp.isoformat()
        }


class RiskAssessment(Base):
    """
    Model for storing token risk assessments.
    """
    __tablename__ = "risk_assessments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to token
    token_id = Column(Integer, ForeignKey('tokens.id'), nullable=False, index=True)
    
    # Risk scores
    overall_risk_score = Column(Numeric(precision=4, scale=2), nullable=False)  # 0.00-10.00
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Numeric(precision=3, scale=2), nullable=False)  # 0.00-1.00
    
    # Individual risk factors
    liquidity_risk = Column(Numeric(precision=4, scale=2), nullable=True)
    contract_risk = Column(Numeric(precision=4, scale=2), nullable=True)
    market_risk = Column(Numeric(precision=4, scale=2), nullable=True)
    social_risk = Column(Numeric(precision=4, scale=2), nullable=True)
    technical_risk = Column(Numeric(precision=4, scale=2), nullable=True)
    
    # Assessment details
    warnings = Column(Text, nullable=True)  # JSON array of warnings
    recommendations = Column(Text, nullable=True)  # JSON array of recommendations
    additional_data = Column(Text, nullable=True)  # JSON object with additional data (renamed from metadata)
    
    # Assessment info
    assessment_version = Column(String(20), default="1.0", nullable=False)
    assessor = Column(String(50), default="system", nullable=False)
    
    # Timestamps
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    token = relationship("Token", back_populates="risk_assessments")
    
    # Indexes
    __table_args__ = (
        Index('idx_risk_token_assessed', 'token_id', 'assessed_at'),
        Index('idx_risk_score', 'overall_risk_score'),
        Index('idx_risk_level', 'risk_level'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'token_id': self.token_id,
            'overall_risk_score': float(self.overall_risk_score),
            'risk_level': self.risk_level,
            'confidence': float(self.confidence),
            'liquidity_risk': float(self.liquidity_risk) if self.liquidity_risk else None,
            'contract_risk': float(self.contract_risk) if self.contract_risk else None,
            'market_risk': float(self.market_risk) if self.market_risk else None,
            'social_risk': float(self.social_risk) if self.social_risk else None,
            'technical_risk': float(self.technical_risk) if self.technical_risk else None,
            'assessment_version': self.assessment_version,
            'assessor': self.assessor,
            'assessed_at': self.assessed_at.isoformat()
        }


class DiscoverySession(Base):
    """
    Model for tracking token discovery sessions.
    """
    __tablename__ = "discovery_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Session information
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    network = Column(String(50), nullable=False, index=True)
    
    # Scan parameters
    from_block = Column(Integer, nullable=False)
    to_block = Column(Integer, nullable=False)
    blocks_scanned = Column(Integer, nullable=False)
    
    # Results
    tokens_found = Column(Integer, default=0, nullable=False)
    tokens_processed = Column(Integer, default=0, nullable=False)
    tokens_stored = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    scan_duration_seconds = Column(Numeric(precision=10, scale=3), nullable=True)
    processing_duration_seconds = Column(Numeric(precision=10, scale=3), nullable=True)
    
    # Status
    status = Column(String(20), default="running", nullable=False)  # running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tokens = relationship("Token", secondary="discovery_session_tokens", back_populates="discovery_sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_discovery_network_started', 'network', 'started_at'),
        Index('idx_discovery_status', 'status'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'network': self.network,
            'from_block': self.from_block,
            'to_block': self.to_block,
            'blocks_scanned': self.blocks_scanned,
            'tokens_found': self.tokens_found,
            'tokens_processed': self.tokens_processed,
            'tokens_stored': self.tokens_stored,
            'scan_duration_seconds': float(self.scan_duration_seconds) if self.scan_duration_seconds else None,
            'processing_duration_seconds': float(self.processing_duration_seconds) if self.processing_duration_seconds else None,
            'status': self.status,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


# Association table for many-to-many relationship between tokens and discovery sessions
from sqlalchemy import Table
discovery_session_tokens = Table(
    'discovery_session_tokens',
    Base.metadata,
    Column('discovery_session_id', Integer, ForeignKey('discovery_sessions.id'), primary_key=True),
    Column('token_id', Integer, ForeignKey('tokens.id'), primary_key=True),
    Index('idx_session_token', 'discovery_session_id', 'token_id')
)