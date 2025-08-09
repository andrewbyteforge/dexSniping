"""
Security Manager Fallback - No Cryptography Required
File: app/core/security/security_manager_fallback.py
Class: SecurityManagerFallback
Methods: validate_api_key, sanitize_error, validate_input, encrypt_wallet_data

Fallback security implementation that works without cryptography library.
Provides basic security features for testing and development.
"""

import hashlib
import hmac
import secrets
import base64
import json
import re
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum

from app.utils.logger import setup_logger
from app.core.exceptions import (
    SecurityError, AuthenticationError, AuthorizationError,
    ValidationError, AccessDeniedError, CredentialError
)

logger = setup_logger(__name__)


class SecurityLevel(Enum):
    """Security clearance levels."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    WALLET_OWNER = "wallet_owner"
    ADMIN = "admin"
    SYSTEM = "system"


class APIKeyType(Enum):
    """API key types for different access levels."""
    READ_ONLY = "read_only"
    TRADING = "trading"
    ADMIN = "admin"
    WEBHOOK = "webhook"


class InputValidatorFallback:
    """Basic input validation without cryptography dependency."""
    
    def __init__(self):
        """Initialize input validator with basic patterns."""
        self.patterns = {
            # Blockchain patterns
            'ethereum_address': re.compile(r'^0x[a-fA-F0-9]{40}$'),
            'tx_hash': re.compile(r'^0x[a-fA-F0-9]{64}$'),
            'private_key': re.compile(r'^[a-fA-F0-9]{64}$'),
            'public_key': re.compile(r'^0x[a-fA-F0-9]{128}$'),
            
            # Trading patterns
            'token_symbol': re.compile(r'^[A-Z0-9]{1,10}$'),
            'amount': re.compile(r'^\d+\.?\d*$'),
            'percentage': re.compile(r'^\d{1,2}(\.\d{1,2})?$'),
            
            # API patterns
            'api_key': re.compile(r'^[a-zA-Z0-9_-]{32,128}$'),
            'uuid': re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'),
            'username': re.compile(r'^[a-zA-Z0-9_]{3,32}$'),
            
            # General patterns
            'safe_string': re.compile(r'^[a-zA-Z0-9\s\-_.@]{1,255}$'),
            'alphanumeric': re.compile(r'^[a-zA-Z0-9]+$'),
        }
        
        # Maximum lengths for different input types
        self.max_lengths = {
            'string': 1000,
            'name': 100,
            'description': 500,
            'url': 2000,
            'message': 1000,
        }
        
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',             # JavaScript injection
            r'on\w+\s*=',              # Event handlers
            r'DROP\s+TABLE',           # SQL injection
            r'UNION\s+SELECT',         # SQL injection
            r'\.\./.*',                # Path traversal
            r'file://',                # Local file access
            r'data:text/html',         # Data URLs
        ]
        
        logger.info("[EMOJI] Input validator (fallback) initialized")

    def validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address format."""
        try:
            if not address or not isinstance(address, str):
                return False
            return self.patterns['ethereum_address'].match(address) is not None
        except Exception as e:
            logger.warning(f"[WARN] Address validation error: {e}")
            return False

    def validate_amount(self, amount: Union[str, float, int], 
                       min_value: float = 0, max_value: float = 1e18) -> Tuple[bool, Optional[float]]:
        """Validate trading amount with bounds checking."""
        try:
            amount_str = str(amount).strip()
            
            if not self.patterns['amount'].match(amount_str):
                return False, None
            
            parsed_amount = float(amount_str)
            
            if not (min_value <= parsed_amount <= max_value):
                return False, None
            
            return True, parsed_amount
            
        except (ValueError, TypeError) as e:
            logger.warning(f"[WARN] Amount validation error: {e}")
            return False, None

    def sanitize_string(self, input_str: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input by removing dangerous patterns."""
        if not input_str or not isinstance(input_str, str):
            return ""
        
        sanitized = input_str.strip()
        
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # Remove dangerous patterns
        for pattern in self.dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Encode special characters
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        
        return sanitized

    def validate_input_dict(self, data: Dict[str, Any], 
                          schema: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate dictionary input against schema."""
        errors = []
        
        try:
            for field, rules in schema.items():
                value = data.get(field)
                
                if rules.get('required', False) and value is None:
                    errors.append(f"Field '{field}' is required")
                    continue
                
                if value is None:
                    continue
                
                expected_type = rules.get('type')
                if expected_type and not isinstance(value, expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
                    continue
                
                if isinstance(value, str):
                    min_len = rules.get('min_length', 0)
                    max_len = rules.get('max_length', self.max_lengths.get('string', 1000))
                    
                    if len(value) < min_len:
                        errors.append(f"Field '{field}' must be at least {min_len} characters")
                    elif len(value) > max_len:
                        errors.append(f"Field '{field}' must be at most {max_len} characters")
                
                if isinstance(value, (int, float)):
                    min_val = rules.get('min_value')
                    max_val = rules.get('max_value')
                    
                    if min_val is not None and value < min_val:
                        errors.append(f"Field '{field}' must be at least {min_val}")
                    elif max_val is not None and value > max_val:
                        errors.append(f"Field '{field}' must be at most {max_val}")
                
                pattern = rules.get('pattern')
                if pattern and isinstance(value, str):
                    if isinstance(pattern, str):
                        pattern = self.patterns.get(pattern)
                    
                    if pattern and not pattern.match(value):
                        errors.append(f"Field '{field}' has invalid format")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"[ERROR] Input validation error: {e}")
            return False, [f"Validation error: {str(e)}"]


class WalletSecurityFallback:
    """Basic wallet security without cryptography dependency."""
    
    def __init__(self):
        """Initialize wallet security fallback."""
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.failed_attempts = {}
        self.locked_wallets = {}
        
        logger.info("[AUTH] Wallet security (fallback) initialized")

    def encrypt_private_key(self, private_key: str, wallet_address: str) -> str:
        """Basic private key encoding (NOT secure - for testing only)."""
        try:
            if not re.match(r'^[a-fA-F0-9]{64}$', private_key):
                raise ValidationError("Invalid private key format")
            
            # Simple base64 encoding (NOT SECURE - testing only)
            payload = {
                'private_key': private_key,
                'wallet_address': wallet_address.lower(),
                'timestamp': datetime.utcnow().isoformat(),
                'checksum': hashlib.sha256(private_key.encode()).hexdigest()[:16]
            }
            
            encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
            logger.warning("[WARN] Using fallback encryption (NOT SECURE)")
            return encoded_data
            
        except Exception as e:
            logger.error(f"[ERROR] Fallback encryption failed: {e}")
            raise SecurityError(f"Encryption failed: {e}")

    def decrypt_private_key(self, encrypted_key: str, wallet_address: str) -> str:
        """Basic private key decoding (NOT secure - for testing only)."""
        try:
            if self.is_wallet_locked(wallet_address):
                raise SecurityError("Wallet is locked due to failed attempts")
            
            # Simple base64 decoding (NOT SECURE)
            try:
                decoded_data = base64.b64decode(encrypted_key.encode())
                payload = json.loads(decoded_data.decode())
            except Exception:
                self.record_failed_attempt(wallet_address)
                raise SecurityError("Invalid encrypted key format")
            
            if payload['wallet_address'] != wallet_address.lower():
                self.record_failed_attempt(wallet_address)
                raise SecurityError("Wallet address mismatch")
            
            private_key = payload['private_key']
            expected_checksum = hashlib.sha256(private_key.encode()).hexdigest()[:16]
            if payload['checksum'] != expected_checksum:
                self.record_failed_attempt(wallet_address)
                raise SecurityError("Private key integrity check failed")
            
            self.reset_failed_attempts(wallet_address)
            logger.warning("[WARN] Using fallback decryption (NOT SECURE)")
            return private_key
            
        except Exception as e:
            logger.error(f"[ERROR] Fallback decryption failed: {e}")
            self.record_failed_attempt(wallet_address)
            raise SecurityError(f"Decryption failed: {e}")

    def record_failed_attempt(self, wallet_address: str):
        """Record failed decryption attempt."""
        address = wallet_address.lower()
        current_time = datetime.utcnow()
        
        if address not in self.failed_attempts:
            self.failed_attempts[address] = []
        
        self.failed_attempts[address].append(current_time)
        
        cutoff_time = current_time - self.lockout_duration
        self.failed_attempts[address] = [
            attempt for attempt in self.failed_attempts[address]
            if attempt > cutoff_time
        ]
        
        if len(self.failed_attempts[address]) >= self.max_failed_attempts:
            self.locked_wallets[address] = current_time + self.lockout_duration
            logger.warning(f"[EMOJI] Wallet {address[:8]}... locked due to failed attempts")

    def is_wallet_locked(self, wallet_address: str) -> bool:
        """Check if wallet is currently locked."""
        address = wallet_address.lower()
        
        if address not in self.locked_wallets:
            return False
        
        if datetime.utcnow() > self.locked_wallets[address]:
            del self.locked_wallets[address]
            self.reset_failed_attempts(address)
            return False
        
        return True

    def reset_failed_attempts(self, wallet_address: str):
        """Reset failed attempts for wallet."""
        address = wallet_address.lower()
        if address in self.failed_attempts:
            del self.failed_attempts[address]
        if address in self.locked_wallets:
            del self.locked_wallets[address]


class APIAuthenticationFallback:
    """Basic API authentication without cryptography dependency."""
    
    def __init__(self):
        """Initialize API authentication fallback."""
        self.api_keys = {}
        self.rate_limits = {}
        self.failed_auth_attempts = {}
        
        self.default_rate_limits = {
            APIKeyType.READ_ONLY: 60,
            APIKeyType.TRADING: 30,
            APIKeyType.ADMIN: 120,
            APIKeyType.WEBHOOK: 10
        }
        
        logger.info("[EMOJI] API authentication (fallback) initialized")

    def generate_api_key(self, user_id: str, key_type: APIKeyType, 
                        permissions: List[str]) -> str:
        """Generate new API key using basic method."""
        try:
            # Generate using built-in secrets module
            api_key = secrets.token_urlsafe(32)
            
            self.api_keys[api_key] = {
                'user_id': user_id,
                'key_type': key_type,
                'permissions': permissions,
                'created_at': datetime.utcnow(),
                'last_used': None,
                'usage_count': 0,
                'rate_limit': self.default_rate_limits.get(key_type, 60)
            }
            
            logger.info(f"[EMOJI] API key generated for user {user_id}, type {key_type.value}")
            return api_key
            
        except Exception as e:
            logger.error(f"[ERROR] API key generation failed: {e}")
            raise SecurityError(f"API key generation failed: {e}")

    def validate_api_key(self, api_key: str, required_permission: str = None) -> Dict[str, Any]:
        """Validate API key and check permissions."""
        try:
            if not api_key or api_key not in self.api_keys:
                self.record_failed_auth(api_key)
                raise AuthenticationError("Invalid API key")
            
            key_data = self.api_keys[api_key]
            
            if not self.check_rate_limit(api_key):
                raise AuthenticationError("Rate limit exceeded")
            
            if required_permission and required_permission not in key_data['permissions']:
                raise AuthorizationError(f"Permission '{required_permission}' required")
            
            key_data['last_used'] = datetime.utcnow()
            key_data['usage_count'] += 1
            
            return key_data
            
        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"[ERROR] API key validation error: {e}")
            raise AuthenticationError(f"API key validation failed: {e}")

    def check_rate_limit(self, api_key: str) -> bool:
        """Check if API key is within rate limits."""
        try:
            current_time = datetime.utcnow()
            current_minute = current_time.replace(second=0, microsecond=0)
            
            if api_key not in self.rate_limits:
                self.rate_limits[api_key] = {}
            
            cutoff_time = current_minute - timedelta(minutes=5)
            self.rate_limits[api_key] = {
                minute: count for minute, count in self.rate_limits[api_key].items()
                if minute > cutoff_time
            }
            
            current_count = self.rate_limits[api_key].get(current_minute, 0)
            key_data = self.api_keys.get(api_key, {})
            rate_limit = key_data.get('rate_limit', 60)
            
            if current_count >= rate_limit:
                return False
            
            self.rate_limits[api_key][current_minute] = current_count + 1
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Rate limit check error: {e}")
            return False

    def record_failed_auth(self, api_key: str):
        """Record failed authentication attempt."""
        current_time = datetime.utcnow()
        
        if api_key not in self.failed_auth_attempts:
            self.failed_auth_attempts[api_key] = []
        
        self.failed_auth_attempts[api_key].append(current_time)
        
        cutoff_time = current_time - timedelta(hours=1)
        self.failed_auth_attempts[api_key] = [
            attempt for attempt in self.failed_auth_attempts[api_key]
            if attempt > cutoff_time
        ]


class ErrorSanitizerFallback:
    """Basic error sanitization without cryptography dependency."""
    
    def __init__(self):
        """Initialize error sanitizer fallback."""
        self.sensitive_patterns = [
            r'0x[a-fA-F0-9]{40}',      # Ethereum addresses
            r'[a-fA-F0-9]{64}',        # Private keys/hashes
            r'password[=:][\w\d]+',     # Passwords
            r'key[=:][\w\d]+',         # API keys
            r'token[=:][\w\d]+',       # Tokens
            r'/[a-zA-Z0-9_/.-]+\.db',  # Database paths
            r'postgresql://[^\\s]+',    # Database URLs
        ]
        
        self.error_templates = {
            'wallet_error': 'Wallet operation failed',
            'auth_error': 'Authentication failed',
            'network_error': 'Network connectivity issue',
            'validation_error': 'Input validation failed',
            'trading_error': 'Trading operation failed',
            'system_error': 'Internal system error'
        }
        
        logger.info("🧹 Error sanitizer (fallback) initialized")

    def sanitize_error(self, error_message: str, error_type: str = 'system_error') -> str:
        """Sanitize error message for public consumption."""
        try:
            if not error_message:
                return self.error_templates.get(error_type, 'Unknown error')
            
            sanitized = str(error_message)
            
            for pattern in self.sensitive_patterns:
                sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
            
            if len(sanitized) > 200:
                sanitized = sanitized[:200] + '...'
            
            sensitive_keywords = ['private', 'key', 'password', 'secret', 'token']
            if any(keyword in sanitized.lower() for keyword in sensitive_keywords):
                return self.error_templates.get(error_type, 'Security error')
            
            return sanitized
            
        except Exception as e:
            logger.error(f"[ERROR] Error sanitization failed: {e}")
            return self.error_templates.get(error_type, 'Error processing failed')


class SecurityManagerFallback:
    """Fallback security manager that works without cryptography."""
    
    def __init__(self):
        """Initialize fallback security manager."""
        try:
            self.input_validator = InputValidatorFallback()
            self.wallet_security = WalletSecurityFallback()
            self.api_auth = APIAuthenticationFallback()
            self.error_sanitizer = ErrorSanitizerFallback()
            
            self.security_events = []
            self.max_security_events = 1000
            
            logger.info("[SEC] Security manager (fallback) initialized")
            logger.warning("[WARN] Using fallback security - install cryptography for full security")
            
        except Exception as e:
            logger.error(f"[ERROR] Fallback security manager initialization failed: {e}")
            raise SecurityError(f"Security system initialization failed: {e}")

    def validate_api_request(self, api_key: str, endpoint: str, 
                           request_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Basic API request validation."""
        try:
            required_permission = self.get_required_permission(endpoint)
            key_data = self.api_auth.validate_api_key(api_key, required_permission)
            
            validation_schema = self.get_validation_schema(endpoint)
            if validation_schema:
                is_valid, errors = self.input_validator.validate_input_dict(
                    request_data, validation_schema
                )
                if not is_valid:
                    return False, f"Validation failed: {'; '.join(errors)}"
            
            self.log_security_event('api_request_validated', {
                'user_id': key_data['user_id'],
                'endpoint': endpoint,
                'key_type': key_data['key_type'].value
            })
            
            return True, None
            
        except (AuthenticationError, AuthorizationError) as e:
            return False, self.error_sanitizer.sanitize_error(str(e), 'auth_error')
        except ValidationError as e:
            return False, self.error_sanitizer.sanitize_error(str(e), 'validation_error')
        except Exception as e:
            logger.error(f"[ERROR] API request validation error: {e}")
            return False, self.error_sanitizer.sanitize_error(str(e), 'system_error')

    def get_required_permission(self, endpoint: str) -> str:
        """Get required permission for API endpoint."""
        permission_map = {
            '/api/v1/wallet/': 'wallet_access',
            '/api/v1/trading/': 'trading_access',
            '/api/v1/dashboard/': 'read_access',
            '/api/v1/admin/': 'admin_access',
        }
        
        for path, permission in permission_map.items():
            if endpoint.startswith(path):
                return permission
        
        return 'read_access'

    def get_validation_schema(self, endpoint: str) -> Optional[Dict[str, Dict[str, Any]]]:
        """Get validation schema for API endpoint."""
        schemas = {
            '/api/v1/trading/execute': {
                'token_address': {'required': True, 'type': str, 'pattern': 'ethereum_address'},
                'amount': {'required': True, 'type': str, 'pattern': 'amount'},
                'side': {'required': True, 'type': str, 'pattern': 'alphanumeric'},
            },
            '/api/v1/wallet/connect': {
                'wallet_address': {'required': True, 'type': str, 'pattern': 'ethereum_address'},
                'signature': {'required': True, 'type': str, 'min_length': 130, 'max_length': 132},
            }
        }
        
        return schemas.get(endpoint)

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event for monitoring."""
        try:
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'details': details
            }
            
            self.security_events.append(event)
            
            if len(self.security_events) > self.max_security_events:
                self.security_events = self.security_events[-self.max_security_events:]
            
            logger.info(f"[SEARCH] Security event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to log security event: {e}")

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security system metrics."""
        try:
            current_time = datetime.utcnow()
            last_hour = current_time - timedelta(hours=1)
            
            recent_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event['timestamp']) > last_hour
            ]
            
            return {
                'total_events': len(self.security_events),
                'recent_events': len(recent_events),
                'active_api_keys': len(self.api_auth.api_keys),
                'locked_wallets': len(self.wallet_security.locked_wallets),
                'system_status': 'operational',
                'security_mode': 'fallback',
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get security metrics: {e}")
            return {'error': 'Failed to retrieve metrics'}


# Global fallback instance
_security_manager_fallback: Optional[SecurityManagerFallback] = None


def get_security_manager_fallback() -> SecurityManagerFallback:
    """Get fallback security manager instance."""
    global _security_manager_fallback
    if _security_manager_fallback is None:
        _security_manager_fallback = SecurityManagerFallback()
    return _security_manager_fallback


def initialize_security_manager_fallback() -> SecurityManagerFallback:
    """Initialize fallback security manager."""
    global _security_manager_fallback
    _security_manager_fallback = SecurityManagerFallback()
    return _security_manager_fallback


# Export fallback classes
__all__ = [
    'SecurityManagerFallback', 'SecurityLevel', 'APIKeyType',
    'InputValidatorFallback', 'WalletSecurityFallback', 
    'APIAuthenticationFallback', 'ErrorSanitizerFallback',
    'get_security_manager_fallback', 'initialize_security_manager_fallback'
]