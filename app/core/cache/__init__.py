"""Cache management module."""

try:
    from .cache_manager import CacheManager, get_cache_manager
    __all__ = ['CacheManager', 'get_cache_manager']
except ImportError:
    # Fallback if import fails
    class CacheManager:
        def __init__(self, *args, **kwargs):
            pass
        def set(self, key, value, ttl=None):
            return True
        def get(self, key, default=None):
            return default
        def clear(self):
            return True
    
    def get_cache_manager():
        return CacheManager()
    
    __all__ = ['CacheManager', 'get_cache_manager']
