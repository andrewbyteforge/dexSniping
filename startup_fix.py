#!/usr/bin/env python3
"""
Application Startup Fix Script
File: startup_fix.py

Ensures all required directories and files exist for proper application startup.
Creates missing modules and fixes import issues.
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create required directory structure."""
    directories = [
        "app/core",
        "app/schemas", 
        "app/api/v1/endpoints",
        "frontend/templates/test"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory ensured: {directory}")
        
        # Create __init__.py files for Python packages
        if directory.startswith("app/"):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(f'"""{directory} package initialization."""\n')
                print(f"✅ Created: {init_file}")


def create_core_database_module():
    """Create the core database module."""
    content = '''"""
Core Database Module
File: app/core/database.py
"""

from typing import AsyncGenerator

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def get_db_session() -> AsyncGenerator:
    """Get database session with fallback handling."""
    try:
        from app.core.database_mock import get_mock_session
        async for session in get_mock_session():
            yield session
            break
    except Exception as e:
        logger.error(f"Database session error: {e}")
        yield None
'''
    
    file_path = "app/core/database.py"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {file_path}")


def create_database_mock_module():
    """Create the database mock module."""
    content = '''"""
Database Mock Module
File: app/core/database_mock.py
"""

from typing import AsyncGenerator

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MockSession:
    """Mock database session."""
    
    async def commit(self):
        pass
    
    async def rollback(self):
        pass
    
    async def close(self):
        pass


async def get_mock_session() -> AsyncGenerator:
    """Get mock database session."""
    session = MockSession()
    try:
        yield session
    finally:
        await session.close()
'''
    
    file_path = "app/core/database_mock.py"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {file_path}")


def create_dashboard_schemas():
    """Create dashboard schemas module."""
    content = '''"""
Dashboard Schemas
File: app/schemas/dashboard.py
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    portfolio_value: float
    daily_pnl: float
    daily_pnl_percent: float
    trades_today: int
    success_rate: float
    volume_24h: float
    active_pairs: int
    watchlist_alerts: int
    uptime_percent: float
    latency_ms: int
    last_updated: str


class TokenMetricsResponse(BaseModel):
    """Token metrics response."""
    symbol: str
    name: str
    address: str
    price: float
    price_change_24h: float
    volume_24h: float
    market_cap: Optional[float]
    liquidity: Optional[float]
    last_updated: str


class TradingMetricsResponse(BaseModel):
    """Trading metrics response."""
    timeframe: str
    total_trades: int
    profitable_trades: int
    success_rate: float
    total_volume: float
    total_fees: float
    net_profit: float
    average_trade_size: float
    max_drawdown: float
    sharpe_ratio: Optional[float]
    generated_at: str
'''
    
    file_path = "app/schemas/dashboard.py"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {file_path}")


def check_logger_module():
    """Ensure logger module exists."""
    logger_file = "app/utils/logger.py"
    if not os.path.exists(logger_file):
        os.makedirs("app/utils", exist_ok=True)
        
        content = '''"""
Logger Module
File: app/utils/logger.py
"""

import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with console output."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s [%(name)s]'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
'''
        
        with open(logger_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {logger_file}")
        
        # Create __init__.py for utils
        utils_init = "app/utils/__init__.py"
        if not os.path.exists(utils_init):
            with open(utils_init, 'w', encoding='utf-8') as f:
                f.write('"""Utils package."""\n')
            print(f"✅ Created: {utils_init}")


def main():
    """Main setup function."""
    print("🔧 Application Startup Fix")
    print("=" * 40)
    
    try:
        # Create directory structure
        print("📁 Creating directory structure...")
        create_directory_structure()
        
        # Create missing modules
        print("\n📄 Creating missing modules...")
        create_core_database_module()
        create_database_mock_module() 
        create_dashboard_schemas()
        check_logger_module()
        
        print("\n🎉 Startup fix completed successfully!")
        print("🚀 Ready to start the application with: uvicorn app.main:app --reload --port 8001")
        
        return True
        
    except Exception as e:
        print(f"❌ Startup fix failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)