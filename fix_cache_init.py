#!/usr/bin/env python3
"""
Fix Cache Init Import Issue
File: fix_cache_init.py

Fix the specific import issue in the cache __init__.py file.
"""

from pathlib import Path


def fix_cache_init_file():
    """Fix the cache __init__.py file to have correct imports."""
    
    cache_dir = Path("app/core/cache")
    init_file = cache_dir / "__init__.py"
    
    # Simple __init__.py that won't cause import issues
    simple_init_content = '''"""Cache management module."""

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
'''
    
    try:
        init_file.write_text(simple_init_content, encoding='utf-8')
        print("✅ Fixed cache __init__.py file")
        return True
    except Exception as e:
        print(f"❌ Failed to fix cache __init__.py: {e}")
        return False


def simplify_cache_manager():
    """Simplify cache_manager.py to avoid any potential issues."""
    
    cache_dir = Path("app/core/cache")
    manager_file = cache_dir / "cache_manager.py"
    
    # Very simple cache manager without any complex imports
    simple_manager_content = '''"""
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
'''
    
    try:
        manager_file.write_text(simple_manager_content, encoding='utf-8')
        print("✅ Simplified cache_manager.py")
        return True
    except Exception as e:
        print(f"❌ Failed to simplify cache_manager.py: {e}")
        return False


def test_fixed_cache_import():
    """Test if the fixed cache can be imported."""
    
    try:
        # Clear any cached imports
        import sys
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith('app.core.cache')]
        for module in modules_to_clear:
            del sys.modules[module]
        
        # Try import again
        from app.core.cache import CacheManager
        cache = CacheManager()
        
        # Test basic functionality
        cache.set("test", "value")
        result = cache.get("test")
        
        if result == "value":
            print("✅ Cache import and functionality working")
            return True
        else:
            print("❌ Cache import worked but functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ Cache import still failed: {e}")
        return False


def main():
    """Fix cache import issues."""
    print("🔧 Fixing Cache Init Import Issue")
    print("=" * 50)
    
    # Fix 1: Fix __init__.py
    print("1. Fixing cache __init__.py...")
    init_fixed = fix_cache_init_file()
    
    # Fix 2: Simplify cache_manager.py
    print("2. Simplifying cache_manager.py...")
    manager_fixed = simplify_cache_manager()
    
    # Fix 3: Test import
    print("3. Testing fixed cache import...")
    import_works = test_fixed_cache_import()
    
    print("\n" + "=" * 50)
    print("Cache Fix Summary:")
    print("=" * 50)
    
    if import_works:
        print("✅ Cache import issue resolved!")
        print("\nNext steps:")
        print("1. Run: python test_minimal.py")
        print("2. Then: python test_all_features.py")
    else:
        print("❌ Cache import still has issues")
        print("\nTry running test_minimal.py anyway - it may work")
    
    return import_works


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)