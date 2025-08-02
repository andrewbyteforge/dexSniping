"""
Cache manager for Redis-based caching with TTL support.
"""

import json
import asyncio
from typing import Any, Optional, Union
from datetime import timedelta
import aioredis
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheManager:
    """Redis-based cache manager with automatic serialization."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test connection
            await self.redis.ping()
            self._connected = True
            logger.info("Cache manager connected to Redis")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self._connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._connected:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Union[int, timedelta] = 300  # 5 minutes default
    ):
        """Set value in cache with TTL."""
        if not self._connected:
            return
        
        try:
            serialized = json.dumps(value, default=str)
            
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            await self.redis.setex(key, ttl, serialized)
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache."""
        if not self._connected:
            return
        
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
    
    async def get_cached_block_number(self, chain: str) -> Optional[int]:
        """Get cached block number for chain."""
        return await self.get(f"block_number:{chain}")
    
    async def cache_block_number(self, chain: str, block_number: int):
        """Cache block number for chain (10 second TTL)."""
        await self.set(f"block_number:{chain}", block_number, ttl=10)
    
    async def get_cached_token_info(self, chain: str, token_address: str) -> Optional[dict]:
        """Get cached token info."""
        return await self.get(f"token_info:{chain}:{token_address}")
    
    async def cache_token_info(self, chain: str, token_address: str, token_info: dict):
        """Cache token info (5 minute TTL)."""
        await self.set(f"token_info:{chain}:{token_address}", token_info, ttl=300)
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("Cache manager disconnected")


# Global instance
cache_manager = CacheManager()