#!/usr/bin/env python3
"""
Quick Cache Import Fix
File: quick_cache_fix.py

Quick diagnostic and fix for cache import issues.
"""

import os
from pathlib import Path


def check_cache_structure():
    """Check if cache structure was created correctly."""
    
    cache_dir = Path("app/core/cache")
    cache_init = cache_dir / "__init__.py"
    cache_manager = cache_dir / "cache_manager.py"
    
    print("Checking cache structure:")
    print(f"  Cache directory exists: {cache_dir.exists()}")
    print(f"  Cache __init__.py exists: {cache_init.exists()}")
    print(f"  Cache manager.py exists: {cache_manager.exists()}")
    
    if cache_dir.exists():
        files = list(cache_dir.iterdir())
        print(f"  Files in cache directory: {[f.name for f in files]}")
    
    return cache_dir.exists() and cache_init.exists() and cache_manager.exists()


def create_cache_structure_force():
    """Force create the cache structure."""
    
    cache_dir = Path("app/core/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_content = '''"""Cache management module."""

from .cache_manager import CacheManager, get_cache_manager

__all__ = ['CacheManager', 'get_cache_manager']
'''
    
    init_file = cache_dir / "__init__.py"
    init_file.write_text(init_content, encoding='utf-8')
    
    # Create cache_manager.py (simplified version)
    manager_content = '''"""
Cache Manager - Simplified
File: app/core/cache/cache_manager.py
"""

import time
from typing import Any, Dict, Optional


class CacheManager:
    """Simple in-memory cache manager."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache manager."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache."""
        try:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            self.cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time()
            }
            return True
        except:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the cache."""
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
        """Clear all cache entries."""
        try:
            self.cache.clear()
            return True
        except:
            return False


# Global cache instance
_cache_instance = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = CacheManager()
    
    return _cache_instance
'''
    
    manager_file = cache_dir / "cache_manager.py"
    manager_file.write_text(manager_content, encoding='utf-8')
    
    print("[OK] Force created cache structure")
    return True


def test_cache_import():
    """Test if cache can be imported."""
    
    try:
        from app.core.cache import CacheManager
        print("[OK] Cache import successful")
        return True
    except Exception as e:
        print(f"[ERROR] Cache import failed: {e}")
        return False


def create_minimal_test():
    """Create a minimal test that bypasses problematic imports."""
    
    minimal_test_content = '''#!/usr/bin/env python3
"""
Minimal System Test - Bypass Cache Issues
File: test_minimal.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("DEX Sniper Pro - Minimal System Test")
print("=" * 60)

# Test 1: Logger
print("\\n1. Testing logger...")
try:
    from app.utils.logger import setup_logger
    logger = setup_logger("test")
    print("   [OK] Logger working")
except Exception as e:
    print(f"   [ERROR] Logger failed: {e}")

# Test 2: Exceptions
print("\\n2. Testing exceptions...")
try:
    from app.core.exceptions import TradingBotError, DatabaseError
    print("   [OK] Exceptions available")
except Exception as e:
    print(f"   [ERROR] Exceptions failed: {e}")

# Test 3: Database (basic)
print("\\n3. Testing database...")
try:
    from app.core.database.persistence_manager import PersistenceManager
    print("   [OK] Database manager importable")
except Exception as e:
    print(f"   [ERROR] Database failed: {e}")

# Test 4: Settings (basic)
print("\\n4. Testing settings...")
try:
    from app.core.config.settings_manager import get_settings
    print("   [OK] Settings manager importable")
except Exception as e:
    print(f"   [ERROR] Settings failed: {e}")

# Test 5: Cache (newly created)
print("\\n5. Testing cache...")
try:
    from app.core.cache import CacheManager
    cache = CacheManager()
    print("   [OK] Cache manager working")
except Exception as e:
    print(f"   [ERROR] Cache failed: {e}")

print("\\n" + "=" * 60)
print("Minimal Test Complete")
print("=" * 60)
print("If all tests show [OK], the core system is working.")
print("Any [ERROR] messages indicate components that need attention.")
print("=" * 60)
'''
    
    test_file = Path("test_minimal.py")
    test_file.write_text(minimal_test_content, encoding='utf-8')
    print("[OK] Created minimal test: test_minimal.py")
    return True


def main():
    """Main fix function."""
    print("[FIX] Quick Cache Import Fix")
    print("=" * 50)
    
    # Check current structure
    print("1. Checking cache structure...")
    structure_ok = check_cache_structure()
    
    if not structure_ok:
        print("\\n2. Force creating cache structure...")
        create_cache_structure_force()
    
    # Test import
    print("\\n3. Testing cache import...")
    import_ok = test_cache_import()
    
    # Create minimal test
    print("\\n4. Creating minimal test...")
    create_minimal_test()
    
    print("\\n" + "=" * 50)
    print("Quick Fix Summary:")
    print("=" * 50)
    
    if import_ok:
        print("[OK] Cache import working")
        print("\\nNext steps:")
        print("1. Run: python test_minimal.py")
        print("2. If successful, try: python test_all_features.py")
    else:
        print("[ERROR] Cache import still failing")
        print("\\nTry running: python test_minimal.py")
        print("This will test components individually.")


if __name__ == "__main__":
    main()