"""
Mock Database Session for Development
File: app/core/database_mock.py

Provides a mock database session when real database is unavailable.
Useful for development and testing scenarios.
"""

from typing import AsyncGenerator, Any, Dict, Optional
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MockAsyncSession:
    """Mock async database session for development."""
    
    def __init__(self):
        """Initialize mock session."""
        self.is_active = True
        self.transaction_active = False
        logger.debug("Mock database session created")
    
    async def execute(self, query, params=None):
        """Mock execute method."""
        logger.debug(f"Mock execute: {query}")
        return MockResult()
    
    async def commit(self):
        """Mock commit method."""
        logger.debug("Mock commit")
        self.transaction_active = False
    
    async def rollback(self):
        """Mock rollback method."""
        logger.debug("Mock rollback")
        self.transaction_active = False
    
    async def close(self):
        """Mock close method."""
        logger.debug("Mock session closed")
        self.is_active = False
    
    async def refresh(self, instance):
        """Mock refresh method."""
        logger.debug("Mock refresh")
    
    async def merge(self, instance):
        """Mock merge method."""
        logger.debug("Mock merge")
        return instance
    
    async def add(self, instance):
        """Mock add method."""
        logger.debug("Mock add")
    
    async def delete(self, instance):
        """Mock delete method."""
        logger.debug("Mock delete")
    
    def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()


class MockResult:
    """Mock database query result."""
    
    def __init__(self):
        """Initialize mock result."""
        self.rowcount = 0
    
    def fetchone(self):
        """Mock fetchone method."""
        return None
    
    def fetchall(self):
        """Mock fetchall method."""
        return []
    
    def first(self):
        """Mock first method."""
        return None
    
    def scalars(self):
        """Mock scalars method."""
        return MockScalars()


class MockScalars:
    """Mock scalars result."""
    
    def first(self):
        """Mock first method."""
        return None
    
    def all(self):
        """Mock all method."""
        return []


async def get_mock_session() -> AsyncGenerator[MockAsyncSession, None]:
    """
    Create mock database session for development.
    
    Yields:
        MockAsyncSession: Mock database session
    """
    logger.info("Creating mock database session for development")
    
    session = MockAsyncSession()
    try:
        yield session
    except Exception as e:
        logger.error(f"Mock session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


def create_mock_data() -> Dict[str, Any]:
    """
    Create mock data for development and testing.
    
    Returns:
        Dict containing mock application data
    """
    return {
        "dashboard_stats": {
            "portfolio_value": 125847.32,
            "daily_pnl": 3241.87,
            "daily_pnl_percent": 2.64,
            "trades_today": 47,
            "success_rate": 89.4,
            "volume_24h": 1847293.45,
            "active_pairs": 23,
            "watchlist_alerts": 5,
            "uptime_percent": 99.8,
            "latency_ms": 12,
            "last_updated": datetime.utcnow().isoformat()
        },
        "tokens": [
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "price": 2847.32,
                "price_change_24h": 4.7,
                "volume_24h": 15847293.45,
                "market_cap": 342847293847.32,
                "liquidity": 5847293.45
            },
            {
                "symbol": "USDC",
                "name": "USD Coin", 
                "address": "0xA0b86a33E6c3d8B56DeD28FB8c7E4eE1C3A7De22",
                "price": 1.0001,
                "price_change_24h": 0.01,
                "volume_24h": 8847293.45,
                "market_cap": 28847293847.32,
                "liquidity": 12847293.45
            },
            {
                "symbol": "WBTC",
                "name": "Wrapped Bitcoin",
                "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 
                "price": 43247.89,
                "price_change_24h": -1.2,
                "volume_24h": 3847293.45,
                "market_cap": 8847293847.32,
                "liquidity": 847293.45
            }
        ],
        "trading_metrics": {
            "timeframe": "24h",
            "total_trades": 47,
            "profitable_trades": 42,
            "success_rate": 89.4,
            "total_volume": 1847293.45,
            "total_fees": 245.67,
            "net_profit": 3241.87,
            "average_trade_size": 39303.05,
            "max_drawdown": 2.3,
            "sharpe_ratio": 2.847,
            "generated_at": datetime.utcnow().isoformat()
        }
    }