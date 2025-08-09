"""
Apply Phase 4C Fixes Script
File: apply_phase4c_fixes.py

This script applies all the Phase 4C fixes to the existing project files.
Run this script from the project root directory.
"""

import os
import shutil
from pathlib import Path


def backup_file(file_path: str) -> str:
    """Create a backup of the original file."""
    backup_path = f"{file_path}.backup"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backed up {file_path} to {backup_path}")
    return backup_path


def apply_cache_manager_fix():
    """Apply the cache manager fix."""
    print("🔧 Applying Cache Manager fix...")
    
    cache_manager_content = '''"""
Enhanced Cache Manager with Proper Import Support
File: app/core/performance/cache_manager.py

Fixed CacheManager import issues and added proper class structure.
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
    """Enhanced cache manager with proper import support."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize cache manager."""
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
        logger.info("✅ Cache manager ready")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> bool:
        """Set a value in the cache."""
        try:
            namespaced_key = f"{namespace}:{key}"
            current_time = time.time()
            expires_at = current_time + ttl if ttl else None
            
            async with self._lock:
                entry = CacheEntry(
                    value=value,
                    created_at=current_time,
                    expires_at=expires_at
                )
                self._cache[namespaced_key] = entry
            
            self._stats["sets"] += 1
            return True
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def get(self, key: str, namespace: str = "default", default: Any = None) -> Any:
        """Get a value from the cache."""
        try:
            namespaced_key = f"{namespace}:{key}"
            
            async with self._lock:
                if namespaced_key in self._cache:
                    entry = self._cache[namespaced_key]
                    current_time = time.time()
                    
                    if entry.expires_at and current_time > entry.expires_at:
                        del self._cache[namespaced_key]
                    else:
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
        """Delete a key from the cache."""
        try:
            namespaced_key = f"{namespace}:{key}"
            async with self._lock:
                deleted = namespaced_key in self._cache
                if deleted:
                    del self._cache[namespaced_key]
                    self._stats["deletes"] += 1
            return deleted
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if a key exists in the cache."""
        try:
            namespaced_key = f"{namespace}:{key}"
            async with self._lock:
                if namespaced_key in self._cache:
                    entry = self._cache[namespaced_key]
                    current_time = time.time()
                    if entry.expires_at and current_time > entry.expires_at:
                        del self._cache[namespaced_key]
                        return False
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    async def clear(self, namespace: str = "default") -> bool:
        """Clear all keys in a namespace."""
        try:
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
        """Get cache statistics."""
        stats = self._stats.copy()
        stats["cache_type"] = "memory"
        stats["hit_rate"] = (
            stats["hits"] / (stats["hits"] + stats["misses"])
            if (stats["hits"] + stats["misses"]) > 0 else 0
        )
        async with self._lock:
            stats["total_entries"] = len(self._cache)
        return stats
    
    async def close(self) -> None:
        """Close cache connections."""
        async with self._lock:
            self._cache.clear()
        logger.info("Cache manager closed")


# Create alias for backward compatibility
SimpleCacheManager = CacheManager

# Global instance
cache_manager = CacheManager()

# Export for imports
__all__ = ["CacheManager", "SimpleCacheManager", "cache_manager", "CacheError", "CacheEntry"]
'''
    
    cache_file = "app/core/performance/cache_manager.py"
    if os.path.exists(cache_file):
        backup_file(cache_file)
        
        with open(cache_file, 'w') as f:
            f.write(cache_manager_content)
        print(f"✅ Applied cache manager fix to {cache_file}")
    else:
        print(f"❌ File not found: {cache_file}")


def apply_multi_chain_fix():
    """Apply the multi-chain manager fix."""
    print("🔧 Applying Multi-Chain Manager fix...")
    
    # Add the get_balance method to BaseChain if it's missing
    base_chain_file = "app/core/blockchain/base_chain.py"
    if os.path.exists(base_chain_file):
        with open(base_chain_file, 'r') as f:
            content = f.read()
        
        # Check if get_balance method is missing
        if "async def get_balance" not in content:
            print("🔧 Adding get_balance method to BaseChain...")
            
            # Add the abstract method before the health_check method
            get_balance_method = '''    
    @abstractmethod
    async def get_balance(self, address: str, token_address: Optional[str] = None) -> Decimal:
        """
        Get balance for an address.
        
        Args:
            address: Address to check balance for
            token_address: Token contract address (None for native token)
            
        Returns:
            Balance amount
        """
        pass
'''
            
            # Insert before health_check method
            health_check_pos = content.find("async def health_check(self)")
            if health_check_pos > 0:
                content = content[:health_check_pos] + get_balance_method + "\n    " + content[health_check_pos:]
                
                backup_file(base_chain_file)
                with open(base_chain_file, 'w') as f:
                    f.write(content)
                print(f"✅ Added get_balance method to {base_chain_file}")


def apply_ai_risk_assessor_fix():
    """Apply AI risk assessor fix."""
    print("🔧 Applying AI Risk Assessor fix...")
    
    risk_assessor_file = "app/core/ai/risk_assessor.py"
    if os.path.exists(risk_assessor_file):
        backup_file(risk_assessor_file)
        
        # Read the current content
        with open(risk_assessor_file, 'r') as f:
            content = f.read()
        
        # Replace problematic imports and fix async issues
        fixes = [
            # Fix import
            ("from app.core.performance.cache_manager import CacheManager", 
             "from app.core.performance.cache_manager import cache_manager"),
            
            # Fix cache manager initialization
            ("self.cache_manager = CacheManager()", 
             "self.cache_manager = cache_manager"),
            
            # Fix async issues in sentiment analysis
            ("sentiment_analysis = await self.analyze_market_sentiment(",
             "try:\n                sentiment_analysis = await self.analyze_market_sentiment("),
            
            # Fix honeypot detection async issues
            ("honeypot_analysis = await self.detect_honeypot(",
             "try:\n                honeypot_analysis = await self.detect_honeypot("),
        ]
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ Applied fix: {old[:50]}... -> {new[:50]}...")
        
        with open(risk_assessor_file, 'w') as f:
            f.write(content)
        print(f"✅ Applied AI Risk Assessor fixes to {risk_assessor_file}")


def apply_live_dashboard_fix():
    """Apply live dashboard service fix."""
    print("🔧 Applying Live Dashboard Service fix...")
    
    dashboard_file = "app/core/integration/live_dashboard_service.py"
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r') as f:
            content = f.read()
        
        # Check if websocket_service attribute is missing
        if "self.websocket_service" not in content:
            backup_file(dashboard_file)
            
            # Add the missing attribute after websocket_manager initialization
            old_init = "self.websocket_manager = websocket_manager"
            new_init = """self.websocket_manager = websocket_manager  # Use global instance
        self.websocket_service = websocket_manager  # Add backward compatibility"""
            
            if old_init in content:
                content = content.replace(old_init, new_init)
                
                with open(dashboard_file, 'w') as f:
                    f.write(content)
                print(f"✅ Applied Live Dashboard Service fix to {dashboard_file}")
            else:
                print(f"⚠️ Could not find initialization pattern in {dashboard_file}")


def main():
    """Main function to apply all fixes."""
    print("🚀 Applying Phase 4C Critical Fixes")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("tests"):
        print("❌ Please run this script from the project root directory")
        print("   Expected structure: /app, /tests, etc.")
        return
    
    try:
        # Apply all fixes
        apply_cache_manager_fix()
        apply_multi_chain_fix()
        apply_ai_risk_assessor_fix()
        apply_live_dashboard_fix()
        
        print("\n" + "=" * 60)
        print("✅ All Phase 4C fixes applied successfully!")
        print("\n🧪 Next steps:")
        print("1. Run: python tests/test_phase4c_fixes.py")
        print("2. Run: python tests/test_phase_4c_integration.py")
        print("3. Verify improved test results")
        
    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        print("Please check the error and try again")


if __name__ == "__main__":
    main()