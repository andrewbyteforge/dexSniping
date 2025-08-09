"""
API Authentication System - Dependency Free
File: app/core/security/api_auth.py
Class: APIAuthManager
Methods: authenticate_request, generate_token, validate_token

Professional API authentication with simple token system (no external dependencies).
"""

import secrets
import hashlib
import hmac
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthLevel(Enum):
    """Authentication levels."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class AuthToken:
    """Authentication token structure."""
    token: str
    user_id: str
    auth_level: AuthLevel
    expires_at: datetime
    permissions: List[str]
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return datetime.utcnow() < self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "token": self.token,
            "user_id": self.user_id,
            "auth_level": self.auth_level.value,
            "expires_at": self.expires_at.isoformat(),
            "permissions": self.permissions
        }


class APIAuthManager:
    """
    Professional API authentication system - Dependency Free.
    
    Features:
    - Simple secure token generation
    - Token validation
    - Permission checking
    - Session management
    - No external dependencies
    """
    
    def __init__(self):
        """Initialize API authentication manager."""
        self.initialized = False
        self.secret_key = secrets.token_hex(32)
        self.active_tokens: Dict[str, AuthToken] = {}
        
        logger.info("[AUTH] APIAuthManager initialized (dependency-free)")
    
    async def initialize(self) -> bool:
        """Initialize the authentication system."""
        try:
            self.initialized = True
            logger.info("[OK] APIAuthManager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] APIAuthManager initialization failed: {e}")
            return False
    
    def _create_simple_token(self, user_id: str, auth_level: AuthLevel, permissions: List[str], expires_at: datetime) -> str:
        """Create a simple secure token without JWT."""
        try:
            # Create payload
            payload = {
                "user_id": user_id,
                "auth_level": auth_level.value,
                "permissions": permissions,
                "expires_at": expires_at.timestamp(),
                "issued_at": datetime.utcnow().timestamp()
            }
            
            # Convert to JSON
            payload_json = json.dumps(payload, sort_keys=True)
            
            # Create signature using HMAC
            signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine payload and signature
            import base64
            payload_b64 = base64.b64encode(payload_json.encode()).decode()
            
            token = f"{payload_b64}.{signature}"
            
            return token
            
        except Exception as e:
            logger.error(f"[ERROR] Token creation failed: {e}")
            raise
    
    def _verify_simple_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a simple token."""
        try:
            if not token or '.' not in token:
                return None
            
            # Split token
            payload_b64, signature = token.split('.', 1)
            
            # Decode payload
            import base64
            payload_json = base64.b64decode(payload_b64.encode()).decode()
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Parse payload
            payload = json.loads(payload_json)
            
            # Check expiration
            if datetime.utcnow().timestamp() > payload["expires_at"]:
                return None
            
            return payload
            
        except Exception as e:
            logger.error(f"[ERROR] Token verification failed: {e}")
            return None
    
    async def generate_token(
        self, 
        user_id: str, 
        auth_level: AuthLevel = AuthLevel.AUTHENTICATED,
        permissions: List[str] = None,
        expires_hours: int = 24
    ) -> str:
        """Generate authentication token."""
        try:
            permissions = permissions or ["read"]
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
            
            token = self._create_simple_token(user_id, auth_level, permissions, expires_at)
            
            # Store token
            auth_token = AuthToken(
                token=token,
                user_id=user_id,
                auth_level=auth_level,
                expires_at=expires_at,
                permissions=permissions
            )
            
            self.active_tokens[token] = auth_token
            
            logger.info(f"[AUTH] Generated token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"[ERROR] Token generation failed: {e}")
            raise
    
    async def validate_token(self, token: str) -> Optional[AuthToken]:
        """Validate authentication token."""
        try:
            if not token:
                return None
            
            # Check active tokens first
            auth_token = self.active_tokens.get(token)
            
            if not auth_token:
                # Try to verify token
                payload = self._verify_simple_token(token)
                
                if not payload:
                    return None
                
                auth_token = AuthToken(
                    token=token,
                    user_id=payload["user_id"],
                    auth_level=AuthLevel(payload["auth_level"]),
                    expires_at=datetime.fromtimestamp(payload["expires_at"]),
                    permissions=payload["permissions"]
                )
            
            # Check if token is still valid
            if not auth_token.is_valid():
                if token in self.active_tokens:
                    del self.active_tokens[token]
                return None
            
            return auth_token
            
        except Exception as e:
            logger.error(f"[ERROR] Token validation failed: {e}")
            return None
    
    async def check_permission(self, token: str, required_permission: str) -> bool:
        """Check if token has required permission."""
        try:
            auth_token = await self.validate_token(token)
            
            if not auth_token:
                return False
            
            return required_permission in auth_token.permissions or "admin" in auth_token.permissions
            
        except Exception as e:
            logger.error(f"[ERROR] Permission check failed: {e}")
            return False
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke authentication token."""
        try:
            if token in self.active_tokens:
                del self.active_tokens[token]
                logger.info("[AUTH] Token revoked")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Token revocation failed: {e}")
            return False
    
    async def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication system status."""
        try:
            active_count = len(self.active_tokens)
            valid_count = sum(1 for token in self.active_tokens.values() if token.is_valid())
            
            return {
                "system_status": "operational",
                "active_tokens": active_count,
                "valid_tokens": valid_count,
                "features": [
                    "Simple secure tokens",
                    "Permission checking",
                    "Token revocation",
                    "HMAC signatures"
                ],
                "dependency_free": True,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get auth status: {e}")
            return {"system_status": "error", "error": str(e)}


# Global instance
api_auth_manager = APIAuthManager()


async def get_api_auth_manager() -> APIAuthManager:
    """Get the global API authentication manager instance."""
    if not api_auth_manager.initialized:
        await api_auth_manager.initialize()
    return api_auth_manager
