"""
Simple Cache Manager
File: app/core/cache/cache_manager.py

Ultra-simple cache implementation that just works.
"""

import time
from typing import Any, Dict, Optional


class CacheManager:
    """Ultra-simple in-memory cache."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache."""
        self.cache = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value."""
        try:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            self.cache[key] = {"value": value, "expires_at": expires_at}
            return True
        except:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get cache value."""
        try:
            if key not in self.cache:
                return default
            
            entry = self.cache[key]
            if time.time() > entry["expires_at"]:
                del self.cache[key]
                return default
            
            return entry["value"]
        except:
            return default
    
    def clear(self) -> bool:
        """Clear cache."""
        try:
            self.cache.clear()
            return True
        except:
            return False


# Global instance
_cache_instance = None


def get_cache_manager() -> CacheManager:
    """Get cache manager."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance
