"""
File: app/core/performance/cache_manager.py

Simplified cache manager with in-memory storage and optional Redis support.
"""

import asyncio
import json
import time
from typing import Any, Optional, Dict, List
from dataclasses import dataclass

from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException

logger = setup_logger(__name__)


class CacheError(DexSnipingException):
    """Exception raised when cache operations fail."""
    pass


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    access_count: int = 0
    last_accessed: Optional[float] = None


class SimpleCacheManager:
    """
    Simplified cache manager with in-memory storage.
    
    Features:
    - In-memory caching with TTL support
    - Optional Redis support (when available)
    - Key namespacing
    - Cache statistics
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL (optional)
        """
        self.redis_url = redis_url
        self.redis_client = None
        self.use_redis = False
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
    
    async def connect(self) -> None:
        """Initialize cache connections."""
        logger.info("Initializing cache manager...")
        
        # Try to connect to Redis if URL provided
        if self.redis_url:
            try:
                # Only try Redis if aioredis is available
                try:
                    import aioredis
                    self.redis_client = aioredis.from_url(
                        self.redis_url,
                        encoding="utf-8",
                        decode_responses=True,
                        retry_on_timeout=True,
                        socket_timeout=5
                    )
                    # Test connection
                    await self.redis_client.ping()
                    self.use_redis = True
                    logger.info("Connected to Redis cache")
                except ImportError:
                    logger.info("aioredis not available, using in-memory cache")
                    self.use_redis = False
                except Exception as e:
                    logger.warning(f"Redis connection failed, using in-memory cache: {e}")
                    self.use_redis = False
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.use_redis = False
        else:
            logger.info("No Redis URL provided, using in-memory cache")
        
        if not self.use_redis:
            logger.info("Using in-memory cache")
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 3600,
        namespace: str = "default"
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
            namespace: Key namespace for organization
        """
        try:
            namespaced_key = f"{namespace}:{key}"
            
            if self.use_redis and self.redis_client:
                serialized_value = self._serialize(value)
                if ttl:
                    await self.redis_client.setex(namespaced_key, ttl, serialized_value)
                else:
                    await self.redis_client.set(namespaced_key, serialized_value)
            else:
                # Use in-memory cache
                async with self._lock:
                    current_time = time.time()
                    expires_at = current_time + ttl if ttl else None
                    
                    self._cache[namespaced_key] = CacheEntry(
                        value=value,
                        created_at=current_time,
                        expires_at=expires_at
                    )
                    
                    # Clean up expired entries periodically
                    await self._cleanup_expired()
            
            self._stats["sets"] += 1
            logger.debug(f"Cached value for key: {namespaced_key}")
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache set failed for key {key}: {e}")
            # Don't raise exception for cache failures
    
    async def get(
        self,
        key: str,
        namespace: str = "default",
        default: Any = None
    ) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            namespace: Key namespace
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            namespaced_key = f"{namespace}:{key}"
            
            if self.use_redis and self.redis_client:
                serialized_value = await self.redis_client.get(namespaced_key)
                if serialized_value:
                    value = self._deserialize(serialized_value)
                    self._stats["hits"] += 1
                    return value
            else:
                # Use in-memory cache
                async with self._lock:
                    if namespaced_key in self._cache:
                        entry = self._cache[namespaced_key]
                        current_time = time.time()
                        
                        # Check if expired
                        if entry.expires_at and current_time > entry.expires_at:
                            del self._cache[namespaced_key]
                        else:
                            # Update access statistics
                            entry.access_count += 1
                            entry.last_accessed = current_time
                            self._stats["hits"] += 1
                            return entry.value
            
            self._stats["misses"] += 1
            return default
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache get failed for key {key}: {e}")
            return default
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key
            namespace: Key namespace
            
        Returns:
            True if key was deleted
        """
        try:
            namespaced_key = f"{namespace}:{key}"
            
            if self.use_redis and self.redis_client:
                result = await self.redis_client.delete(namespaced_key)
                deleted = result > 0
            else:
                # Use in-memory cache
                async with self._lock:
                    deleted = namespaced_key in self._cache
                    if deleted:
                        del self._cache[namespaced_key]
            
            if deleted:
                self._stats["deletes"] += 1
            
            return deleted
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: Cache key
            namespace: Key namespace
            
        Returns:
            True if key exists
        """
        try:
            namespaced_key = f"{namespace}:{key}"
            
            if self.use_redis and self.redis_client:
                return await self.redis_client.exists(namespaced_key) > 0
            else:
                # Use in-memory cache
                async with self._lock:
                    if namespaced_key in self._cache:
                        entry = self._cache[namespaced_key]
                        current_time = time.time()
                        
                        # Check if expired
                        if entry.expires_at and current_time > entry.expires_at:
                            del self._cache[namespaced_key]
                            return False
                        return True
                    return False
                
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics
        """
        stats = self._stats.copy()
        stats["cache_type"] = "redis" if self.use_redis else "memory"
        stats["hit_rate"] = (
            stats["hits"] / (stats["hits"] + stats["misses"])
            if (stats["hits"] + stats["misses"]) > 0 else 0
        )
        
        if not self.use_redis:
            async with self._lock:
                stats["total_entries"] = len(self._cache)
                stats["memory_usage"] = len(self._cache)
        
        return stats
    
    async def close(self) -> None:
        """Close cache connections."""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            # Clear in-memory cache
            async with self._lock:
                self._cache.clear()
            
            logger.info("Cache manager closed")
        except Exception as e:
            logger.error(f"Error closing cache manager: {e}")
    
    async def _cleanup_expired(self) -> None:
        """Clean up expired entries from in-memory cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.expires_at and current_time > entry.expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _serialize(self, value: Any) -> str:
        """
        Serialize value for storage.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized string
        """
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            # Fallback to string representation
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """
        Deserialize value from storage.
        
        Args:
            value: Serialized string
            
        Returns:
            Deserialized value
        """
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return value


# Global cache manager instance
cache_manager = SimpleCacheManager()