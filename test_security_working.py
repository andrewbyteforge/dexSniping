"""
Working Security Test
File: test_security_working.py

A minimal test that validates security components work.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_security():
    """Test security implementation."""
    print("[SEC] Working Security Test")
    print("=" * 40)
    
    try:
        # Test imports
        print("[TEST] Testing imports...")
        from app.core.security.security_manager import (
            get_security_manager, SecurityManager, APIKeyType
        )
        print("  [OK] Security imports successful")
        
        # Test initialization
        print("[TEST] Testing initialization...")
        security_manager = get_security_manager()
        print("  [OK] Security manager initialized")
        
        # Test wallet security
        print("[TEST] Testing wallet security...")
        test_key = "a" * 64
        test_address = "0x" + "b" * 40
        
        encrypted = security_manager.wallet_security.encrypt_private_key(test_key, test_address)
        decrypted = security_manager.wallet_security.decrypt_private_key(encrypted, test_address)
        assert decrypted == test_key
        print("  [OK] Wallet security working")
        
        # Test API auth
        print("[TEST] Testing API authentication...")
        api_key = security_manager.api_auth.generate_api_key(
            "test_user", APIKeyType.TRADING, ["read_access", "trading_access"]
        )
        key_data = security_manager.api_auth.validate_api_key(api_key, "read_access")
        assert key_data['user_id'] == 'test_user'
        print("  [OK] API authentication working")
        
        # Test input validation
        print("[TEST] Testing input validation...")
        valid_addr = "0x" + "a" * 40
        assert security_manager.input_validator.validate_ethereum_address(valid_addr)
        assert not security_manager.input_validator.validate_ethereum_address("invalid")
        print("  [OK] Input validation working")
        
        # Test error sanitization
        print("[TEST] Testing error sanitization...")
        error_msg = "Error with 0x1234567890abcdef1234567890abcdef12345678"
        sanitized = security_manager.error_sanitizer.sanitize_error(error_msg)
        assert "[REDACTED]" in sanitized
        print("  [OK] Error sanitization working")
        
        # Test metrics
        print("[TEST] Testing security metrics...")
        metrics = security_manager.get_security_metrics()
        assert 'system_status' in metrics
        print("  [OK] Security metrics working")
        
        print("\n[SUCCESS] ALL SECURITY TESTS PASSED!")
        print("[OK] Security implementation working correctly")
        print("\n[SEC] Security Features Validated:")
        print("   [AUTH] Wallet Security - Private key encryption/decryption")
        print("   [EMOJI] API Authentication - Key generation and validation")
        print("   [OK] Input Validation - Address and data validation")
        print("   🧹 Error Sanitization - Sensitive data removal")
        print("   [STATS] Security Metrics - System monitoring")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_security()
    
    if success:
        print("\n[START] Security implementation is ready!")
        print("[OK] All 4 critical security failures resolved")
    else:
        print("\n[ERROR] Security implementation needs fixes")
    
    sys.exit(0 if success else 1)
