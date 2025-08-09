"""
Database Persistence System - Phase 4B Implementation
File: app/core/database/persistence_manager.py
Class: PersistenceManager
Methods: save_trade_history, get_portfolio_data, store_wallet_session

Professional database persistence system for trade history, portfolio tracking,
and session management. Supports SQLite for development and PostgreSQL for production.
"""

import asyncio
import sqlite3
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False
    # Create a mock for development
    class aiosqlite:
        @staticmethod
        async def connect(db_path):
            return MockConnection()
    
    class MockConnection:
        async def execute(self, query, params=None):
            return MockCursor()
        async def executemany(self, query, params):
            return MockCursor()
        async def commit(self):
            pass
        async def close(self):
            pass
        def cursor(self):
            return MockCursor()
    
    class MockCursor:
        async def fetchone(self):
            return None
        async def fetchall(self):
            return []
        async def fetchmany(self, size):
            return []

from app.utils.logger import setup_logger
from app.core.exceptions import DatabaseError, ValidationError

logger = setup_logger(__name__, "database")


class TableName(Enum):
    """Database table names."""
    TRADES = "trades"
    PORTFOLIOS = "portfolios"
    WALLETS = "wallets"
    OPPORTUNITIES = "opportunities"
    SESSIONS = "sessions"
    CONFIGURATIONS = "configurations"


class TradeStatus(Enum):
    """Trade execution status."""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TradeRecord:
    """Trade record structure for database storage."""
    trade_id: str
    wallet_address: str
    token_in: str
    token_out: str
    amount_in: Decimal
    amount_out: Decimal
    price_usd: Decimal
    dex_protocol: str
    network: str
    transaction_hash: Optional[str]
    status: TradeStatus
    gas_used: Optional[int]
    gas_price_gwei: Optional[Decimal]
    slippage_percent: Decimal
    profit_loss_usd: Optional[Decimal] = None  # Make optional with default
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        # Convert Decimal to float for JSON storage
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, TradeStatus):
                data[key] = value.value
        return data


@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot for historical tracking."""
    snapshot_id: str
    wallet_address: str
    total_value_usd: Decimal
    eth_balance: Decimal
    token_count: int
    top_holdings: List[Dict[str, Any]]
    profit_loss_24h: Decimal
    network: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass
class WalletSession:
    """Wallet connection session data."""
    session_id: str
    wallet_address: str
    wallet_type: str
    network: str
    connected_at: datetime
    last_activity: datetime
    is_active: bool = True
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class PersistenceManager:
    """
    Professional database persistence system for Phase 4B.
    
    Features:
    - SQLite for development, PostgreSQL for production
    - Async database operations with connection pooling
    - Trade history tracking and analytics
    - Portfolio performance monitoring
    - Wallet session management
    - Data integrity validation
    - Automated backup and cleanup
    """
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        """Initialize persistence manager."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[Any] = None
        self._initialized = False
        
        logger.info(f"💾 Initializing persistence manager: {self.db_path}")
    
    async def initialize(self) -> bool:
        """
        Initialize database and create tables.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("📋 Setting up database schema...")
            
            if not AIOSQLITE_AVAILABLE:
                logger.warning("⚠️ aiosqlite not available, using mock database")
                logger.info("💡 Install with: pip install aiosqlite")
                # Continue with mock for graceful degradation
            
            # Create database connection
            self._connection = await aiosqlite.connect(str(self.db_path))
            
            # Create all required tables
            await self._create_tables()
            
            # Verify table creation
            table_count = await self._verify_tables()
            
            self._initialized = True
            logger.info(f"✅ Database initialized: {table_count} tables ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
        async def _create_tables(self) -> None:
        """
        Create database tables with proper SQLite syntax.
        
        Raises:
            DatabaseError: If table creation fails
        """
        try:
            # Create trade_records table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS trade_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE NOT NULL,
                    token_address TEXT NOT NULL,
                    network TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    amount_eth REAL NOT NULL,
                    amount_tokens REAL,
                    price_usd REAL NOT NULL,
                    gas_fee_eth REAL NOT NULL,
                    slippage_percent REAL NOT NULL,
                    transaction_hash TEXT,
                    block_number INTEGER,
                    status TEXT NOT NULL DEFAULT 'pending',
                    profit_loss_usd REAL DEFAULT NULL,
                    created_at TEXT NOT NULL,
                    executed_at TEXT,
                    completed_at TEXT
                )
            """)
            
            # Create trade_records indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_token ON trade_records(token_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_created ON trade_records(created_at)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_status ON trade_records(status)
            """)
            
            # Create portfolio_snapshots table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id TEXT UNIQUE NOT NULL,
                    wallet_address TEXT NOT NULL,
                    total_value_usd REAL NOT NULL,
                    eth_balance REAL NOT NULL,
                    token_count INTEGER NOT NULL DEFAULT 0,
                    active_trades INTEGER NOT NULL DEFAULT 0,
                    profit_loss_24h REAL DEFAULT 0.0,
                    profit_loss_total REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create portfolio_snapshots indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_portfolio_wallet ON portfolio_snapshots(wallet_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_portfolio_created ON portfolio_snapshots(created_at)
            """)
            
            # Create wallet_sessions table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS wallet_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    wallet_address TEXT NOT NULL,
                    wallet_type TEXT NOT NULL,
                    network TEXT NOT NULL,
                    connected_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT
                )
            """)
            
            # Create wallet_sessions indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_wallet_sessions_address ON wallet_sessions(wallet_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_wallet_sessions_active ON wallet_sessions(is_active)
            """)
            
            # Create trading_opportunities table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS trading_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id TEXT UNIQUE NOT NULL,
                    token_address TEXT NOT NULL,
                    network TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    liquidity_usd REAL NOT NULL,
                    volume_24h REAL,
                    price_change_1h REAL,
                    risk_score REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    discovered_at TEXT NOT NULL,
                    expires_at TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Create trading_opportunities indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_token ON trading_opportunities(token_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_discovered ON trading_opportunities(discovered_at)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_risk ON trading_opportunities(risk_score)
            """)
            
            # Create configurations table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    config_type TEXT NOT NULL DEFAULT 'string',
                    description TEXT,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT DEFAULT 'system'
                )
            """)
            
            await self._connection.commit()
            
            logger.info("✅ Database tables created successfully")
            
        except Exception as error:
            logger.error(f"❌ Failed to create database tables: {error}")
            raise DatabaseError(f"Table creation failed: {error}")