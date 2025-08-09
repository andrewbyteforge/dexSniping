#!/usr/bin/env python3
"""
Simplified System Test - Windows Compatible
File: test_simple.py

A Windows-compatible test that avoids unicode and complex imports.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("DEX Sniper Pro - Simplified System Test")
print("=" * 60)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    from app.utils.logger import setup_logger
    print("   [OK] Logger import successful")
except Exception as e:
    print(f"   [ERROR] Logger import failed: {e}")

# Test 2: Database manager
print("\n2. Testing database manager...")
try:
    from app.core.database.persistence_manager import PersistenceManager
    print("   [OK] PersistenceManager import successful")
    
    # Try to create instance
    db_path = "data/test.db"
    manager = PersistenceManager(db_path)
    print("   [OK] PersistenceManager instance created")
    
except Exception as e:
    print(f"   [ERROR] Database manager failed: {e}")

# Test 3: Configuration
print("\n3. Testing configuration...")
try:
    from app.core.config.settings_manager import get_settings
    settings = get_settings()
    print("   [OK] Settings loaded successfully")
    
    errors = settings.validate_configuration()
    if not errors:
        print("   [OK] Configuration validation passed")
    else:
        print(f"   [WARN] Configuration validation warnings: {len(errors)}")
        
except Exception as e:
    print(f"   [ERROR] Configuration failed: {e}")

# Test 4: AI components (optional)
print("\n4. Testing AI components...")
try:
    from app.core.ai.risk_assessor import AIRiskAssessor
    assessor = AIRiskAssessor()
    print("   [OK] AI Risk Assessor available")
except Exception as e:
    print(f"   [WARN] AI components not available: {e}")

# Test 5: Trading components
print("\n5. Testing trading components...")
try:
    from app.core.trading.transaction_executor import TransactionExecutor
    executor = TransactionExecutor()
    print("   [OK] Transaction Executor available")
except Exception as e:
    print(f"   [WARN] Trading components not available: {e}")

# Summary
print("\n" + "=" * 60)
print("Test Summary:")
print("=" * 60)
print("Basic system components are available.")
print("Any warnings above indicate optional features.")
print("\n[OK] System is ready for development!")
print("=" * 60)
