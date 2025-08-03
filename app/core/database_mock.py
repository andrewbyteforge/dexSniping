"""
Mock Database Module
File: app/core/database_mock.py

Mock database session for development and testing.
"""

from typing import AsyncGenerator
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MockAsyncSession:
    """Mock async database session."""
    
    def __init__(self):
        self.is_active = True
        self.in_transaction = False
    
    async def execute(self, query, params=None):
        """Mock execute method."""
        logger.debug(f"Mock execute: {str(query)[:50]}...")
        return MockResult()
    
    async def commit(self):
        """Mock commit method."""
        logger.debug("Mock commit")
        self.in_transaction = False
    
    async def rollback(self):
        """Mock rollback method."""
        logger.debug("Mock rollback")
        self.in_transaction = False
    
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


class MockResult:
    """Mock database query result."""
    
    def __init__(self):
        self.rowcount = 0
    
    def fetchone(self):
        return None
    
    def fetchall(self):
        return []
    
    def first(self):
        return None
    
    def scalars(self):
        return MockScalars()


class MockScalars:
    """Mock scalars result."""
    
    def first(self):
        return None
    
    def all(self):
        return []


async def get_mock_session() -> AsyncGenerator[MockAsyncSession, None]:
    """
    Create mock database session.
    
    Yields:
        MockAsyncSession: Mock database session
    """
    logger.debug("Creating mock database session")
    
    session = MockAsyncSession()
    try:
        yield session
    except Exception as e:
        logger.error(f"Mock session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()
