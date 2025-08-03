"""
Basic Validation Test - Super Simple Phase 3A Check
File: basic_validation_test.py

This is the simplest possible validation test to check our core components.
No complex dependencies or fancy formatting.

Usage: python basic_validation_test.py
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())


def main():
    """Simple synchronous test of core components."""
    print("=" * 50)
    print("BASIC PHASE 3A VALIDATION TEST")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Configuration
    print("\nTesting configuration...")
    try:
        from app.config import settings
        print("   SUCCESS: Configuration imported")
        results['config'] = True
    except Exception as e:
        print(f"   FAILED: Configuration - {e}")
        results['config'] = False
    
    # Test 2: Schemas  
    print("\nTesting schemas...")
    try:
        from app.schemas.token import TokenResponse
        print("   SUCCESS: Token schemas imported")
        results['schemas'] = True
    except Exception as e:
        print(f"   FAILED: Schemas - {e}")
        results['schemas'] = False
    
    # Test 3: Core Discovery
    print("\nTesting discovery components...")
    try:
        from app.core.discovery.token_scanner import TokenScanner
        print("   SUCCESS: Token scanner imported")
        results['discovery'] = True
    except Exception as e:
        print(f"   FAILED: Discovery - {e}")
        results['discovery'] = False
    
    # Test 4: Risk Calculator
    print("\nTesting risk calculator...")
    try:
        from app.core.risk.risk_calculator import RiskCalculator
        print("   SUCCESS: Risk calculator imported")
        results['risk'] = True
    except Exception as e:
        print(f"   FAILED: Risk calculator - {e}")
        results['risk'] = False
    
    # Test 5: Database Models
    print("\nTesting database models...")
    try:
        from app.models.token import Token
        print("   SUCCESS: Database models imported")
        results['models'] = True
    except Exception as e:
        print(f"   FAILED: Models - {e}")
        results['models'] = False
    
    # Test 6: Performance Infrastructure
    print("\nTesting performance components...")
    try:
        from app.core.performance.connection_pool import connection_pool
        print("   SUCCESS: Performance components imported")
        results['performance'] = True
    except Exception as e:
        print(f"   FAILED: Performance - {e}")
        results['performance'] = False
    
    # Test 7: Blockchain Components
    print("\nTesting blockchain components...")
    try:
        from app.core.blockchain.multi_chain_manager import MultiChainManager
        print("   SUCCESS: Blockchain components imported")
        results['blockchain'] = True
    except Exception as e:
        print(f"   FAILED: Blockchain - {e}")
        results['blockchain'] = False
    
    # Results Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\nPassed: {passed}/{total} ({percentage:.0f}%)")
    
    for component, status in results.items():
        status_text = "PASS" if status else "FAIL"
        print(f"   {component}: {status_text}")
    
    # Assessment
    print("\nASSESSMENT:")
    if percentage >= 80:
        print("   EXCELLENT! Core components ready for Phase 3B")
        print("   You can proceed with advanced feature development")
    elif percentage >= 60:
        print("   GOOD! Most components working, minor fixes needed")
        print("   Address failing components before Phase 3B")
    else:
        print("   NEEDS WORK! Major components missing")
        print("   Complete Phase 3A components before Phase 3B")
    
    return percentage >= 60


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nREADY FOR PHASE 3B DEVELOPMENT!")
        else:
            print("\nPLEASE COMPLETE MISSING COMPONENTS FIRST")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        print("Check that all files exist and dependencies are installed")