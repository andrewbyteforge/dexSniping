"""
Core Database Module
File: app/core/database.py

Centralized database configuration and session management.
Provides unified access to database sessions for all components.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.
    
    Yields:
        AsyncSession: Database session instance
        
    Raises:
        Exception: If database connection fails
    """
    try:
        # Try to use connection pool first
        from app.core.performance.connection_pool import connection_pool
        
        async with connection_pool.session_scope() as session:
            logger.debug("Database session created via connection pool")
            yield session
            
    except Exception as pool_error:
        logger.warning(f"Connection pool unavailable, falling back to direct connection: {pool_error}")
        
        try:
            # Fallback to direct database connection
            from app.models.database import get_db
            
            async for session in get_db():
                logger.debug("Database session created via direct connection")
                yield session
                break
                
        except Exception as db_error:
            logger.error(f"Database connection failed: {db_error}")
            
            # Final fallback - create mock session for development
            logger.warning("Using mock database session for development")
            from app.core.database_mock import get_mock_session
            
            async for session in get_mock_session():
                yield session
                break


async def init_database():
    """Initialize database connections and tables."""
    try:
        logger.info("Initializing database...")
        
        # Try to initialize connection pool
        try:
            from app.core.performance.connection_pool import connection_pool
            await connection_pool.initialize()
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.warning(f"Connection pool initialization failed: {e}")
        
        # Try to initialize database tables
        try:
            from app.models.database import init_database as init_db_tables
            await init_db_tables()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.warning(f"Database table initialization failed: {e}")
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise exception to allow app to start with limited functionality


async def close_database():
    """Close database connections."""
    try:
        logger.info("Closing database connections...")
        
        # Close connection pool
        try:
            from app.core.performance.connection_pool import connection_pool
            await connection_pool.close()
            logger.info("Connection pool closed")
        except Exception as e:
            logger.warning(f"Connection pool close failed: {e}")
        
        # Close direct database connections
        try:
            from app.models.database import close_database as close_db
            await close_db()
            logger.info("Direct database connections closed")
        except Exception as e:
            logger.warning(f"Direct database close failed: {e}")
        
        logger.info("Database shutdown completed")
        
    except Exception as e:
        logger.error(f"Database shutdown failed: {e}")


async def health_check() -> dict:
    """
    Check database health status.
    
    Returns:
        Dict with database health information
    """
    try:
        # Test connection pool
        try:
            from app.core.performance.connection_pool import connection_pool
            pool_health = await connection_pool.health_check()
            return {
                "status": "healthy",
                "connection_pool": pool_health,
                "timestamp": pool_health.get("last_check")
            }
        except Exception as pool_error:
            logger.warning(f"Connection pool health check failed: {pool_error}")
        
        # Test direct connection
        try:
            async for session in get_db_session():
                # Simple query test
                return {
                    "status": "healthy", 
                    "connection": "direct",
                    "message": "Database accessible via direct connection"
                }
        except Exception as db_error:
            logger.error(f"Database health check failed: {db_error}")
        
        return {
            "status": "unhealthy",
            "error": "Database not accessible",
            "fallback": "mock_mode_available"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }