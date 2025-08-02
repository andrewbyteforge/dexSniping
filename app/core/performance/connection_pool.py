"""
File: app/core/performance/connection_pool.py

Fixed database connection pool manager without recursive initialization loops.
"""

import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import time

from app.config import settings
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException

logger = setup_logger(__name__)


class ConnectionPoolError(DexSnipingException):
    """Exception raised when connection pool operations fail."""
    pass


class ConnectionPoolManager:
    """
    Simplified database connection pool manager.
    
    Features:
    - Async connection pooling
    - Connection health monitoring
    - Resource cleanup
    - Pool statistics tracking
    """
    
    def __init__(self):
        """Initialize the connection pool manager."""
        self.engine: Optional[Any] = None
        self.async_session_factory: Optional[async_sessionmaker] = None
        self._pool_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "connection_errors": 0,
            "last_health_check": None
        }
        self._is_initialized = False
        self._initialization_lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """
        Initialize the database connection pool.
        
        Raises:
            ConnectionPoolError: If initialization fails
        """
        # Prevent recursive initialization
        if self._is_initialized:
            return
            
        async with self._initialization_lock:
            # Double-check after acquiring lock
            if self._is_initialized:
                return
                
            try:
                logger.info("Initializing database connection pool...")
                
                # Database URL configuration
                database_url = getattr(settings, 'database_url', 'sqlite+aiosqlite:///./dex_sniping.db')
                
                # Convert to async URL if needed
                if database_url.startswith('postgresql://'):
                    database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
                elif database_url.startswith('sqlite://'):
                    database_url = database_url.replace('sqlite://', 'sqlite+aiosqlite:///')
                
                # Engine configuration
                engine_kwargs = {
                    'echo': getattr(settings, 'debug', False),
                    'future': True,
                }
                
                # Configure pooling based on database type
                if 'sqlite' in database_url:
                    # SQLite doesn't support connection pooling
                    engine_kwargs['poolclass'] = NullPool
                    engine_kwargs['connect_args'] = {'check_same_thread': False}
                else:
                    # PostgreSQL/MySQL with connection pooling
                    engine_kwargs.update({
                        'poolclass': QueuePool,
                        'pool_size': 5,
                        'max_overflow': 10,
                        'pool_timeout': 30,
                        'pool_recycle': 3600,
                        'pool_pre_ping': True,
                    })
                
                # Create async engine
                self.engine = create_async_engine(database_url, **engine_kwargs)
                
                # Create session factory
                self.async_session_factory = async_sessionmaker(
                    bind=self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autoflush=True,
                    autocommit=False,
                )
                
                # Simple connection test WITHOUT using session_scope
                await self._simple_connection_test()
                
                self._is_initialized = True
                logger.info("Database connection pool initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                raise ConnectionPoolError(f"Connection pool initialization failed: {e}")
    
    async def get_session(self) -> AsyncSession:
        """
        Get a database session from the pool.
        
        Returns:
            AsyncSession: Database session
            
        Raises:
            ConnectionPoolError: If session creation fails
        """
        if not self._is_initialized:
            await self.initialize()
        
        try:
            session = self.async_session_factory()
            self._pool_stats["pool_hits"] += 1
            self._pool_stats["active_connections"] += 1
            return session
            
        except Exception as e:
            self._pool_stats["connection_errors"] += 1
            self._pool_stats["pool_misses"] += 1
            logger.error(f"Failed to get database session: {e}")
            raise ConnectionPoolError(f"Failed to get session: {e}")
    
    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for database sessions with automatic cleanup.
        
        Yields:
            AsyncSession: Database session
        """
        session = await self.get_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            self._pool_stats["active_connections"] -= 1
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a query using a session from the pool.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query result
        """
        async with self.session_scope() as session:
            result = await session.execute(text(query), params or {})
            return result
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the connection pool.
        
        Returns:
            Health status information
        """
        try:
            start_time = time.time()
            
            # Simple health check query
            await self._simple_connection_test()
            
            response_time = time.time() - start_time
            
            # Get pool status
            pool_status = {}
            if hasattr(self.engine, 'pool') and hasattr(self.engine.pool, 'size'):
                try:
                    pool_status = {
                        "pool_size": self.engine.pool.size(),
                        "checked_in": self.engine.pool.checkedin(),
                        "checked_out": self.engine.pool.checkedout(),
                        "overflow": getattr(self.engine.pool, 'overflow', 0),
                    }
                except Exception:
                    pool_status = {"status": "pool_info_unavailable"}
            
            health_info = {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "database_url": str(self.engine.url).split('@')[0] + '@***',  # Hide credentials
                "is_initialized": self._is_initialized,
                "pool_stats": self._pool_stats.copy(),
                "pool_status": pool_status,
                "last_check": time.time()
            }
            
            self._pool_stats["last_health_check"] = time.time()
            return health_info
            
        except Exception as e:
            logger.error(f"Connection pool health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "is_initialized": self._is_initialized,
                "last_check": time.time()
            }
    
    async def close(self) -> None:
        """Close the connection pool and cleanup resources."""
        try:
            logger.info("Closing database connection pool...")
            
            # Close engine
            if self.engine:
                await self.engine.dispose()
            
            self._is_initialized = False
            logger.info("Database connection pool closed")
            
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        
        Returns:
            Pool statistics
        """
        return self._pool_stats.copy()
    
    async def _simple_connection_test(self) -> None:
        """
        Simple connection test that doesn't use session_scope to avoid recursion.
        """
        try:
            # Create a temporary session directly
            temp_session = self.async_session_factory()
            try:
                # Simple test query
                await temp_session.execute(text("SELECT 1"))
                logger.debug("Database connection test successful")
            finally:
                await temp_session.close()
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise


# Global connection pool instance
connection_pool = ConnectionPoolManager()