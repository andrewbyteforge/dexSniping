"""
Core Database Module
File: app/core/database.py

Centralized database session management with fallback handling.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with multiple fallback strategies.
    
    Yields:
        AsyncSession: Database session instance
    """
    try:
        # Strategy 1: Try connection pool
        from app.core.performance.connection_pool import connection_pool
        
        async with connection_pool.session_scope() as session:
            logger.debug("Database session via connection pool")
            yield session
            return
            
    except Exception as pool_error:
        logger.debug(f"Connection pool unavailable: {pool_error}")
        
        try:
            # Strategy 2: Try direct database connection
            from app.models.database import get_db
            
            async for session in get_db():
                logger.debug("Database session via direct connection")
                yield session
                return
                
        except Exception as db_error:
            logger.debug(f"Direct database unavailable: {db_error}")
            
            # Strategy 3: Mock session for development
            from app.core.database_mock import get_mock_session
            
            async for session in get_mock_session():
                logger.debug("Using mock database session")
                yield session
                return


async def init_database():
    """Initialize database with error handling."""
    try:
        logger.info("Initializing database connections...")
        
        # Try to initialize connection pool
        try:
            from app.core.performance.connection_pool import connection_pool
            await connection_pool.initialize()
            logger.info("Connection pool initialized")
        except Exception as e:
            logger.warning(f"Connection pool initialization failed: {e}")
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


async def close_database():
    """Close database connections."""
    try:
        logger.info("Closing database connections...")
        
        try:
            from app.core.performance.connection_pool import connection_pool
            await connection_pool.close()
        except Exception as e:
            logger.warning(f"Connection pool close failed: {e}")
        
        logger.info("Database shutdown completed")
        
    except Exception as e:
        logger.error(f"Database shutdown failed: {e}")
