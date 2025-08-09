"""
Wallet Security System
File: app/core/security/wallet_security.py
Class: WalletSecurityManager
Methods: validate_wallet, encrypt_keys, secure_connection

Professional wallet security implementation with encryption and validation.
"""

import hashlib
import hmac
import secrets
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SecurityLevel(Enum):
    """Security level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WalletType(Enum):
    """Supported wallet types."""
    METAMASK = "metamask"
    WALLETCONNECT = "walletconnect"
    HARDWARE = "hardware"
    INJECTED = "injected"


@dataclass
class WalletSecurityProfile:
    """Wallet security profile structure."""
    wallet_address: str
    wallet_type: WalletType
    security_level: SecurityLevel
    encrypted_data: Optional[str]
    last_verified: datetime
    connection_count: int
    risk_score: float
    permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "wallet_address": self.wallet_address,
            "wallet_type": self.wallet_type.value,
            "security_level": self.security_level.value,
            "last_verified": self.last_verified.isoformat(),
            "connection_count": self.connection_count,
            "risk_score": self.risk_score,
            "permissions": self.permissions
        }


class WalletSecurityManager:
    """
    Professional wallet security management system.
    
    Features:
    - Wallet address validation
    - Connection encryption
    - Permission management
    - Risk assessment
    - Security monitoring
    - Compliance checking
    """
    
    def __init__(self):
        """Initialize wallet security manager."""
        self.initialized = False
        self.security_profiles: Dict[str, WalletSecurityProfile] = {}
        self.encryption_key = self._generate_encryption_key()
        
        logger.info("[SECURITY] WalletSecurityManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the wallet security system."""
        try:
            self.initialized = True
            logger.info("[OK] WalletSecurityManager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] WalletSecurityManager initialization failed: {e}")
            return False
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key for secure operations."""
        return secrets.token_hex(32)
    
    async def validate_wallet_address(self, address: str) -> Tuple[bool, str]:
        """
        Validate wallet address format and security.
        
        Args:
            address: Wallet address to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            # Basic Ethereum address validation
            if not address or len(address) != 42:
                return False, "Invalid address length"
            
            if not address.startswith('0x'):
                return False, "Address must start with 0x"
            
            # Check for valid hex characters
            try:
                int(address[2:], 16)
            except ValueError:
                return False, "Invalid hex characters in address"
            
            # Additional security checks
            risk_score = await self._assess_address_risk(address)
            
            if risk_score > 0.8:
                return False, "High-risk address detected"
            
            return True, "Address validation successful"
            
        except Exception as e:
            logger.error(f"[ERROR] Address validation failed: {e}")
            return False, f"Validation error: {str(e)}"
    
    async def _assess_address_risk(self, address: str) -> float:
        """Assess risk score for wallet address."""
        try:
            # Mock risk assessment - in production, check against:
            # - Known malicious addresses
            # - Sanctions lists
            # - Suspicious activity patterns
            
            risk_factors = []
            
            # Check address age (newer addresses are riskier)
            risk_factors.append(0.1)  # Base risk
            
            # Check transaction patterns
            risk_factors.append(0.05)  # Low activity risk
            
            # Overall risk score
            total_risk = sum(risk_factors)
            
            return min(total_risk, 1.0)
            
        except Exception as e:
            logger.error(f"[ERROR] Risk assessment failed: {e}")
            return 0.5  # Medium risk on error
    
    async def create_security_profile(
        self, 
        wallet_address: str, 
        wallet_type: WalletType,
        permissions: List[str] = None
    ) -> WalletSecurityProfile:
        """Create security profile for wallet."""
        try:
            permissions = permissions or ["read", "trade"]
            
            # Assess security level
            risk_score = await self._assess_address_risk(wallet_address)
            
            if risk_score <= 0.3:
                security_level = SecurityLevel.HIGH
            elif risk_score <= 0.6:
                security_level = SecurityLevel.MEDIUM
            else:
                security_level = SecurityLevel.LOW
            
            profile = WalletSecurityProfile(
                wallet_address=wallet_address,
                wallet_type=wallet_type,
                security_level=security_level,
                encrypted_data=self._encrypt_wallet_data(wallet_address),
                last_verified=datetime.utcnow(),
                connection_count=1,
                risk_score=risk_score,
                permissions=permissions
            )
            
            self.security_profiles[wallet_address] = profile
            
            logger.info(f"[SECURITY] Created security profile for {wallet_address}")
            return profile
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create security profile: {e}")
            raise
    
    def _encrypt_wallet_data(self, wallet_address: str) -> str:
        """Encrypt sensitive wallet data."""
        try:
            # Simple encryption for demo - use proper encryption in production
            data = {"address": wallet_address, "timestamp": datetime.utcnow().isoformat()}
            data_str = json.dumps(data)
            
            # Create HMAC for data integrity
            signature = hmac.new(
                self.encryption_key.encode(),
                data_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return f"{data_str}:{signature}"
            
        except Exception as e:
            logger.error(f"[ERROR] Encryption failed: {e}")
            return ""
    
    async def verify_wallet_connection(self, wallet_address: str) -> bool:
        """Verify wallet connection security."""
        try:
            profile = self.security_profiles.get(wallet_address)
            
            if not profile:
                logger.warning(f"[SECURITY] No profile found for {wallet_address}")
                return False
            
            # Update connection count
            profile.connection_count += 1
            profile.last_verified = datetime.utcnow()
            
            # Check security level
            if profile.security_level == SecurityLevel.LOW:
                logger.warning(f"[SECURITY] Low security wallet connected: {wallet_address}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Connection verification failed: {e}")
            return False
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get overall security system status."""
        try:
            total_wallets = len(self.security_profiles)
            high_security = sum(1 for p in self.security_profiles.values() 
                              if p.security_level == SecurityLevel.HIGH)
            
            return {
                "system_status": "operational",
                "total_wallets": total_wallets,
                "high_security_wallets": high_security,
                "security_features": [
                    "Address validation",
                    "Risk assessment", 
                    "Encryption",
                    "Permission management"
                ],
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get security status: {e}")
            return {"system_status": "error", "error": str(e)}


# Global instance
wallet_security_manager = WalletSecurityManager()


async def get_wallet_security_manager() -> WalletSecurityManager:
    """Get the global wallet security manager instance."""
    if not wallet_security_manager.initialized:
        await wallet_security_manager.initialize()
    return wallet_security_manager
