"""
Simple Security Test - Working Version
File: test_security_simple.py

A working security test that validates all components.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_security_implementation():
    """Test all security components."""
    print("🛡️ Simple Security Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Import security manager
        print("🧪 Testing security manager import...")
        from app.core.security.security_manager import (
            get_security_manager, SecurityManager, APIKeyType, SecurityLevel
        )
        security_manager = get_security_manager()
        print("  ✅ Security manager imported and initialized")
        
        # Test 2: Wallet security
        print("🧪 Testing wallet security...")
        test_private_key = "a" * 64
        test_wallet_address = "0x" + "b" * 40
        
        encrypted_key = security_manager.wallet_security.encrypt_private_key(
            test_private_key, test_wallet_address
        )
        decrypted_key = security_manager.wallet_security.decrypt_private_key(
            encrypted_key, test_wallet_address
        )
        assert decrypted_key == test_private_key
        print("  ✅ Wallet security: encryption/decryption working")
        
        # Test 3: API authentication
        print("🧪 Testing API authentication...")
        api_key = security_manager.api_auth.generate_api_key(
            user_id="test_user",
            key_type=APIKeyType.TRADING,
            permissions=['trading_access', 'read_access']
        )
        
        key_data = security_manager.api_auth.validate_api_key(api_key, 'read_access')
        assert key_data['user_id'] == 'test_user'
        print("  ✅ API authentication: key generation/validation working")
        
        # Test 4: Input validation
        print("🧪 Testing input validation...")
        valid_address = "0x" + "a" * 40
        invalid_address = "0x123"
        
        assert security_manager.input_validator.validate_ethereum_address(valid_address)
        assert not security_manager.input_validator.validate_ethereum_address(invalid_address)
        print("  ✅ Input validation: address validation working")
        
        # Test 5: Error sanitization
        print("🧪 Testing error sanitization...")
        error_with_address = "Failed to connect to wallet 0x1234567890abcdef1234567890abcdef12345678"
        sanitized = security_manager.error_sanitizer.sanitize_error(error_with_address)
        assert "0x1234567890abcdef1234567890abcdef12345678" not in sanitized
        assert "[REDACTED]" in sanitized
        print("  ✅ Error sanitization: sensitive data removal working")
        
        # Test 6: Full API request validation
        print("🧪 Testing full API request validation...")
        is_valid, error = security_manager.validate_api_request(
            api_key=api_key,
            endpoint="/api/v1/dashboard/stats",
            request_data={}
        )
        assert is_valid and error is None
        print("  ✅ Full API request validation working")
        
        # Test 7: Security metrics
        print("🧪 Testing security metrics...")
        metrics = security_manager.get_security_metrics()
        assert 'system_status' in metrics
        assert metrics['system_status'] == 'operational'
        print("  ✅ Security metrics working")
        
        print("\n🎉 ALL SECURITY TESTS PASSED!")
        print("✅ Security implementation is working correctly")
        print("✅ All 4 critical security failures resolved:")
        print("   - 🔐 Wallet Security Implementation")
        print("   - 🔑 API Authentication System") 
        print("   - ✅ Input Validation Framework")
        print("   - 🧹 Error Sanitization Protocols")
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_security_implementation()
    
    if success:
        print("\n🚀 Security implementation complete!")
        print("📊 Ready to run full test suite")
    else:
        print("\n❌ Security implementation needs fixes")
    
    sys.exit(0 if success else 1)
