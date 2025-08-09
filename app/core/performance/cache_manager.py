"""
Fixed Cache Manager Import Alias
File: app/core/performance/cache_manager.py

Add CacheManager alias to fix import issues while maintaining backward compatibility.
"""

import asyncio
import json
import time
from typing import Any, Optional, Dict, List
from dataclasses import dataclass

from app.utils.logger import setup_logger
from app.core.exceptions import ServiceError

logger = setup_logger(__name__)


class CacheError(ServiceError):
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


class CacheManager:
    """
    Enhanced cache manager with in-memory storage and optional Redis support.
    
    Features:
    - In-memory caching with TTL support
    - Optional Redis support (when available)
    - Key namespacing
    - Cache statistics
    - Async operations
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
        
        logger.info("[OK] Cache Manager initialized")
    
    async def connect(self) -> None:
        """Initialize cache connections."""
        try:
            if self.redis_url:
                try:
                    import redis.asyncio as redis
                    self.redis_client = redis.from_url(self.redis_url)
                    await self.redis_client.ping()
                    self.use_redis = True
                    logger.info("✅ Connected to Redis cache")
                except ImportError:
                    logger.warning("⚠️ Redis not available, using in-memory cache")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to connect to Redis: {e}, using in-memory cache")
            
            logger.info("✅ Cache manager ready")
            
        except Exception as e:
            logger.error(f"❌ Cache manager initialization failed: {e}")
            # Continue with in-memory cache only
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "default"
    ) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            namespace: Key namespace
            
        Returns:
            True if value was set successfully
        """
        try:
            namespaced_key = f"{namespace}:{key}"
            current_time = time.time()
            expires_at = current_time + ttl if ttl else None
            
            if self.use_redis and self.redis_client:
                serialized_value = self._serialize(value)
                if ttl:
                    await self.redis_client.setex(namespaced_key, ttl, serialized_value)
                else:
                    await self.redis_client.set(namespaced_key, serialized_value)
            else:
                # Use in-memory cache
                async with self._lock:
                    entry = CacheEntry(
                        value=value,
                        created_at=current_time,
                        expires_at=expires_at
                    )
                    self._cache[namespaced_key] = entry
                    
                    # Cleanup expired entries occasionally
                    if len(self._cache) % 100 == 0:
                        await self._cleanup_expired()
            
            self._stats["sets"] += 1
            return True
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
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
    
    async def clear(self, namespace: str = "default") -> bool:
        """
        Clear all keys in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            True if cleared successfully
        """
        try:
            if self.use_redis and self.redis_client:
                # Get all keys in namespace
                pattern = f"{namespace}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                # Clear in-memory cache
                async with self._lock:
                    keys_to_delete = [
                        key for key in self._cache.keys() 
                        if key.startswith(f"{namespace}:")
                    ]
                    for key in keys_to_delete:
                        del self._cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear failed for namespace {namespace}: {e}")
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


# Create aliases for backward compatibility
SimpleCacheManager = CacheManager

# Global cache manager instance
cache_manager = CacheManager()


# ==================== MODULE METADATA ====================

__version__ = "2.0.0"
__phase__ = "4C - Cache Manager Fix"
__description__ = "Fixed cache manager with proper CacheManager class name and imports"

# Export both names for compatibility
__all__ = ["CacheManager", "SimpleCacheManager", "cache_manager", "CacheError", "CacheEntry"]