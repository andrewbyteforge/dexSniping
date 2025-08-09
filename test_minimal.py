#!/usr/bin/env python3
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
print("\n1. Testing logger...")
try:
    from app.utils.logger import setup_logger
    logger = setup_logger("test")
    print("   [OK] Logger working")
except Exception as e:
    print(f"   [ERROR] Logger failed: {e}")

# Test 2: Exceptions
print("\n2. Testing exceptions...")
try:
    from app.core.exceptions import TradingBotError, DatabaseError
    print("   [OK] Exceptions available")
except Exception as e:
    print(f"   [ERROR] Exceptions failed: {e}")

# Test 3: Database (basic)
print("\n3. Testing database...")
try:
    from app.core.database.persistence_manager import PersistenceManager
    print("   [OK] Database manager importable")
except Exception as e:
    print(f"   [ERROR] Database failed: {e}")

# Test 4: Settings (basic)
print("\n4. Testing settings...")
try:
    from app.core.config.settings_manager import get_settings
    print("   [OK] Settings manager importable")
except Exception as e:
    print(f"   [ERROR] Settings failed: {e}")

# Test 5: Cache (newly created)
print("\n5. Testing cache...")
try:
    from app.core.cache import CacheManager
    cache = CacheManager()
    print("   [OK] Cache manager working")
except Exception as e:
    print(f"   [ERROR] Cache failed: {e}")

print("\n" + "=" * 60)
print("Minimal Test Complete")
print("=" * 60)
print("If all tests show [OK], the core system is working.")
print("Any [ERROR] messages indicate components that need attention.")
print("=" * 60)
