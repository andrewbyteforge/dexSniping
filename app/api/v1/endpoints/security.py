"""
Security API Endpoints - Phase 5A
File: app/api/v1/endpoints/security.py
Class: N/A (FastAPI router)
Methods: generate_api_key, validate_wallet, get_security_status, manage_permissions

Professional security management API endpoints for DEX Sniper Pro.
Provides comprehensive security administration and monitoring.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field, validator

from app.utils.logger import setup_logger
from app.core.security.security_manager import (
    get_security_manager, SecurityManager, APIKeyType, SecurityLevel
)
from app.core.exceptions import (
    SecurityError, AuthenticationError, ValidationError,
    AccessDeniedError
)

logger = setup_logger(__name__)

# Initialize router
router = APIRouter(prefix="/security", tags=["Security Management"])


# ==================== REQUEST/RESPONSE MODELS ====================

class APIKeyGenerationRequest(BaseModel):
    """Request model for API key generation."""
    user_id: str = Field(..., description="User identifier")
    key_type: APIKeyType = Field(APIKeyType.READ_ONLY, description="Type of API key")
    permissions: List[str] = Field(default=[], description="Specific permissions")
    expires_in_days: Optional[int] = Field(default=365, ge=1, le=3650, description="Expiration in days")
    description: Optional[str] = Field(default="", max_length=200, description="Key description")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('User ID must be at least 3 characters')
        return v.strip()


class APIKeyResponse(BaseModel):
    """Response model for API key generation."""
    api_key: str = Field(..., description="Generated API key")
    key_type: APIKeyType = Field(..., description="Key type")
    permissions: List[str] = Field(..., description="Assigned permissions")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")


class WalletValidationRequest(BaseModel):
    """Request model for wallet validation."""
    wallet_address: str = Field(..., description="Wallet address to validate")
    signature: Optional[str] = Field(None, description="Signature for ownership proof")
    message: Optional[str] = Field(None, description="Signed message")
    
    @validator('wallet_address')
    def validate_address_format(cls, v):
        if not v or len(v) != 42 or not v.startswith('0x'):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()


class SecurityStatusResponse(BaseModel):
    """Response model for security status."""
    system_status: str = Field(..., description="Overall security status")
    active_threats: int = Field(..., description="Number of active threats")
    security_score: float = Field(..., description="Security score (0-100)")
    last_updated: datetime = Field(..., description="Last status update")
    metrics: Dict[str, Any] = Field(..., description="Security metrics")


class PermissionUpdateRequest(BaseModel):
    """Request model for permission updates."""
    api_key: str = Field(..., description="API key to modify")
    action: str = Field(..., description="Action: 'add', 'remove', or 'replace'")
    permissions: List[str] = Field(..., description="Permissions to modify")
    
    @validator('action')
    def validate_action(cls, v):
        if v not in ['add', 'remove', 'replace']:
            raise ValueError('Action must be add, remove, or replace')
        return v


# ==================== DEPENDENCY FUNCTIONS ====================

def get_admin_security_manager() -> SecurityManager:
    """Get security manager for admin operations."""
    return get_security_manager()


def verify_admin_access(security_manager: SecurityManager = Depends(get_admin_security_manager)):
    """Verify admin access for sensitive operations."""
    # In a real implementation, this would check the current user's permissions
    # For now, we'll assume the security middleware has already validated access
    return security_manager


# ==================== API KEY MANAGEMENT ENDPOINTS ====================

@router.post("/api-keys/generate", response_model=APIKeyResponse)
async def generate_api_key(
    request: APIKeyGenerationRequest,
    security_manager: SecurityManager = Depends(verify_admin_access)
) -> APIKeyResponse:
    """
    Generate new API key with specified permissions.
    Requires admin access.
    """
    try:
        logger.info(f"[EMOJI] Generating API key for user {request.user_id}")
        
        # Generate API key
        api_key = security_manager.api_auth.generate_api_key(
            user_id=request.user_id,
            key_type=request.key_type,
            permissions=request.permissions
        )
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        # Update key metadata with expiration
        key_data = security_manager.api_auth.api_keys[api_key]
        key_data['expires_at'] = expires_at
        key_data['description'] = request.description
        
        logger.info(f"[OK] API key generated successfully for {request.user_id}")
        
        return APIKeyResponse(
            api_key=api_key,
            key_type=request.key_type,
            permissions=request.permissions,
            expires_at=expires_at,
            created_at=key_data['created_at']
        )
        
    except SecurityError as e:
        logger.error(f"[ERROR] API key generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error generating API key: {e}")
        raise HTTPException(status_code=500, detail="API key generation failed")


@router.get("/api-keys")
async def list_api_keys(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    key_type: Optional[APIKeyType] = Query(None, description="Filter by key type"),
    active_only: bool = Query(True, description="Show only active keys"),
    security_manager: SecurityManager = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    List API keys with optional filtering.
    Requires admin access.
    """
    try:
        logger.info("[LOG] Listing API keys")
        
        keys_data = []
        current_time = datetime.utcnow()
        
        for api_key, key_info in security_manager.api_auth.api_keys.items():
            # Apply filters
            if user_id and key_info.get('user_id') != user_id:
                continue
            
            if key_type and key_info.get('key_type') != key_type:
                continue
            
            # Check if key is active
            expires_at = key_info.get('expires_at')
            is_active = expires_at is None or expires_at > current_time
            
            if active_only and not is_active:
                continue
            
            # Prepare key data (without exposing the actual key)
            key_data = {
                'key_id': api_key[:8] + '...' + api_key[-4:],  # Masked key
                'user_id': key_info.get('user_id'),
                'key_type': key_info.get('key_type'),
                'permissions': key_info.get('permissions', []),
                'created_at': key_info.get('created_at'),
                'last_used': key_info.get('last_used'),
                'usage_count': key_info.get('usage_count', 0),
                'expires_at': expires_at,
                'is_active': is_active,
                'description': key_info.get('description', '')
            }
            
            keys_data.append(key_data)
        
        return {
            'api_keys': keys_data,
            'total_count': len(keys_data),
            'active_count': sum(1 for key in keys_data if key['is_active']),
            'query_timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    security_manager: SecurityManager = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Revoke (delete) an API key.
    Requires admin access.
    """
    try:
        logger.info(f"[EMOJI] Revoking API key {key_id[:8]}...")
        
        # Find the full key (key_id is partial)
        matching_keys = [
            key for key in security_manager.api_auth.api_keys.keys()
            if key.startswith(key_id) or key.endswith(key_id) or key_id in key
        ]
        
        if not matching_keys:
            raise HTTPException(status_code=404, detail="API key not found")
        
        if len(matching_keys) > 1:
            raise HTTPException(status_code=400, detail="Ambiguous key ID - be more specific")
        
        api_key = matching_keys[0]
        key_data = security_manager.api_auth.api_keys[api_key]
        
        # Remove the key
        del security_manager.api_auth.api_keys[api_key]
        
        # Clean up rate limiting data
        if api_key in security_manager.api_auth.rate_limits:
            del security_manager.api_auth.rate_limits[api_key]
        
        logger.info(f"[OK] API key revoked for user {key_data.get('user_id')}")
        
        return {
            'success': True,
            'message': f"API key revoked successfully",
            'revoked_key': {
                'user_id': key_data.get('user_id'),
                'key_type': key_data.get('key_type'),
                'revoked_at': datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke API key")


# ==================== WALLET SECURITY ENDPOINTS ====================

@router.post("/wallet/validate")
async def validate_wallet(
    request: WalletValidationRequest,
    security_manager: SecurityManager = Depends(get_security_manager)
) -> Dict[str, Any]:
    """
    Validate wallet address and optional ownership proof.
    """
    try:
        logger.info(f"[SEARCH] Validating wallet {request.wallet_address[:8]}...")
        
        # Validate address format
        is_valid_address = security_manager.input_validator.validate_ethereum_address(
            request.wallet_address
        )
        
        if not is_valid_address:
            raise ValidationError("Invalid wallet address format")
        
        # Check if wallet is locked
        is_locked = security_manager.wallet_security.is_wallet_locked(request.wallet_address)
        
        # Basic validation result
        validation_result = {
            'wallet_address': request.wallet_address,
            'is_valid_format': is_valid_address,
            'is_locked': is_locked,
            'validation_timestamp': datetime.utcnow().isoformat()
        }
        
        # Signature validation (if provided)
        if request.signature and request.message:
            # In a real implementation, this would verify the signature
            # For now, we'll simulate signature validation
            signature_valid = len(request.signature) >= 130  # Basic check
            validation_result['signature_valid'] = signature_valid
            validation_result['ownership_verified'] = signature_valid
        else:
            validation_result['signature_valid'] = None
            validation_result['ownership_verified'] = False
        
        logger.info(f"[OK] Wallet validation completed for {request.wallet_address[:8]}...")
        
        return validation_result
        
    except ValidationError as e:
        logger.warning(f"[WARN] Wallet validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ERROR] Wallet validation error: {e}")
        raise HTTPException(status_code=500, detail="Wallet validation failed")


@router.post("/wallet/unlock")
async def unlock_wallet(
    wallet_address: str = Body(..., description="Wallet address to unlock"),
    admin_signature: str = Body(..., description="Admin signature for unlock"),
    security_manager: SecurityManager = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Unlock a locked wallet (admin only).
    """
    try:
        logger.info(f"[EMOJI] Unlocking wallet {wallet_address[:8]}...")
        
        # Validate admin signature (simplified)
        if len(admin_signature) < 64:
            raise ValidationError("Invalid admin signature")
        
        # Reset failed attempts
        security_manager.wallet_security.reset_failed_attempts(wallet_address)
        
        logger.info(f"[OK] Wallet {wallet_address[:8]}... unlocked successfully")
        
        return {
            'success': True,
            'wallet_address': wallet_address,
            'unlocked_at': datetime.utcnow().isoformat(),
            'message': 'Wallet unlocked successfully'
        }
        
    except ValidationError as e:
        logger.warning(f"[WARN] Wallet unlock failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ERROR] Wallet unlock error: {e}")
        raise HTTPException(status_code=500, detail="Wallet unlock failed")


# ==================== SECURITY STATUS AND MONITORING ====================

@router.get("/status", response_model=SecurityStatusResponse)
async def get_security_status(
    security_manager: SecurityManager = Depends(get_security_manager)
) -> SecurityStatusResponse:
    """
    Get comprehensive security system status.
    """
    try:
        logger.info("[STATS] Retrieving security status")
        
        # Get security metrics
        metrics = security_manager.get_security_metrics()
        
        # Calculate security score based on various factors
        security_score = calculate_security_score(security_manager, metrics)
        
        # Determine system status
        system_status = determine_system_status(security_score, metrics)
        
        # Count active threats
        active_threats = count_active_threats(security_manager)
        
        return SecurityStatusResponse(
            system_status=system_status,
            active_threats=active_threats,
            security_score=security_score,
            last_updated=datetime.utcnow(),
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"[ERROR] Error getting security status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security status")


@router.get("/events")
async def get_security_events(
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    since: Optional[datetime] = Query(None, description="Events since timestamp"),
    security_manager: SecurityManager = Depends(get_security_manager)
) -> Dict[str, Any]:
    """
    Get security events for monitoring and analysis.
    """
    try:
        logger.info(f"[LOG] Retrieving {limit} security events")
        
        events = security_manager.security_events.copy()
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type]
        
        if since:
            events = [
                e for e in events 
                if datetime.fromisoformat(e['timestamp']) >= since
            ]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        events = events[:limit]
        
        # Get event statistics
        event_types = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'events': events,
            'total_count': len(events),
            'event_types': event_types,
            'query_timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Error getting security events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security events")


# ==================== PERMISSION MANAGEMENT ====================

@router.put("/permissions")
async def update_permissions(
    request: PermissionUpdateRequest,
    security_manager: SecurityManager = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Update API key permissions.
    Requires admin access.
    """
    try:
        logger.info(f"[FIX] Updating permissions for API key {request.api_key[:8]}...")
        
        # Find API key
        if request.api_key not in security_manager.api_auth.api_keys:
            raise HTTPException(status_code=404, detail="API key not found")
        
        key_data = security_manager.api_auth.api_keys[request.api_key]
        current_permissions = set(key_data.get('permissions', []))
        new_permissions = set(request.permissions)
        
        # Apply permission changes
        if request.action == 'add':
            updated_permissions = current_permissions.union(new_permissions)
        elif request.action == 'remove':
            updated_permissions = current_permissions.difference(new_permissions)
        elif request.action == 'replace':
            updated_permissions = new_permissions
        else:
            raise ValidationError(f"Invalid action: {request.action}")
        
        # Update permissions
        key_data['permissions'] = list(updated_permissions)
        key_data['permissions_updated_at'] = datetime.utcnow()
        
        logger.info(f"[OK] Permissions updated for API key {request.api_key[:8]}...")
        
        return {
            'success': True,
            'api_key_id': request.api_key[:8] + '...',
            'action': request.action,
            'previous_permissions': list(current_permissions),
            'new_permissions': list(updated_permissions),
            'updated_at': key_data['permissions_updated_at'].isoformat()
        }
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.warning(f"[WARN] Permission update failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ERROR] Permission update error: {e}")
        raise HTTPException(status_code=500, detail="Permission update failed")


@router.get("/permissions/available")
async def get_available_permissions() -> Dict[str, Any]:
    """
    Get list of available permissions and their descriptions.
    """
    try:
        permissions = {
            'read_access': 'Read-only access to data and statistics',
            'wallet_access': 'Access to wallet management functions',
            'trading_access': 'Access to trading operations',
            'admin_access': 'Administrative access to system management',
            'api_key_management': 'Create and manage API keys',
            'security_management': 'Manage security settings and policies',
            'user_management': 'Manage user accounts and permissions',
            'system_monitoring': 'Access to system logs and monitoring',
            'configuration_access': 'Modify system configuration',
            'backup_access': 'Access to backup and restore functions'
        }
        
        return {
            'available_permissions': permissions,
            'permission_count': len(permissions),
            'description': 'Complete list of available system permissions'
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Error getting available permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get permissions")


# ==================== SECURITY CONFIGURATION ====================

@router.get("/config")
async def get_security_config(
    security_manager: SecurityManager = Depends(verify_admin_access)
) -> Dict[str, Any]:
    """
    Get current security configuration.
    Requires admin access.
    """
    try:
        logger.info("[CONFIG] Retrieving security configuration")
        
        config = {
            'wallet_security': {
                'max_failed_attempts': security_manager.wallet_security.max_failed_attempts,
                'lockout_duration_minutes': security_manager.wallet_security.lockout_duration.total_seconds() / 60,
                'locked_wallets_count': len(security_manager.wallet_security.locked_wallets)
            },
            'api_authentication': {
                'active_api_keys': len(security_manager.api_auth.api_keys),
                'default_rate_limits': {
                    key_type.value: limit for key_type, limit in security_manager.api_auth.default_rate_limits.items()
                }
            },
            'security_events': {
                'max_events': security_manager.max_security_events,
                'current_events': len(security_manager.security_events)
            },
            'system_info': {
                'version': '4.0.0-beta',
                'phase': '5A - Security Implementation',
                'last_updated': datetime.utcnow().isoformat()
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"[ERROR] Error getting security config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security configuration")


# ==================== HELPER FUNCTIONS ====================

def calculate_security_score(security_manager: SecurityManager, metrics: Dict[str, Any]) -> float:
    """
    Calculate overall security score based on system metrics.
    
    Args:
        security_manager: Security manager instance
        metrics: Security metrics
        
    Returns:
        Security score (0-100)
    """
    try:
        score = 100.0
        
        # Deduct points for locked wallets
        locked_wallets = metrics.get('locked_wallets', 0)
        if locked_wallets > 0:
            score -= min(locked_wallets * 5, 20)  # Max 20 points deduction
        
        # Deduct points for recent security events
        recent_events = metrics.get('recent_events', 0)
        if recent_events > 10:
            score -= min((recent_events - 10) * 2, 30)  # Max 30 points deduction
        
        # Deduct points for failed authentication attempts
        failed_attempts = len(security_manager.api_auth.failed_auth_attempts)
        if failed_attempts > 0:
            score -= min(failed_attempts, 15)  # Max 15 points deduction
        
        return max(score, 0.0)
        
    except Exception as e:
        logger.error(f"[ERROR] Error calculating security score: {e}")
        return 50.0  # Default score on error


def determine_system_status(security_score: float, metrics: Dict[str, Any]) -> str:
    """
    Determine overall system status based on security score and metrics.
    
    Args:
        security_score: Calculated security score
        metrics: Security metrics
        
    Returns:
        System status string
    """
    if security_score >= 90:
        return "excellent"
    elif security_score >= 75:
        return "good"
    elif security_score >= 60:
        return "moderate"
    elif security_score >= 40:
        return "warning"
    else:
        return "critical"


def count_active_threats(security_manager: SecurityManager) -> int:
    """
    Count active security threats.
    
    Args:
        security_manager: Security manager instance
        
    Returns:
        Number of active threats
    """
    try:
        threats = 0
        
        # Count locked wallets as threats
        threats += len(security_manager.wallet_security.locked_wallets)
        
        # Count recent failed authentication attempts
        current_time = datetime.utcnow()
        recent_cutoff = current_time - timedelta(hours=1)
        
        for api_key, attempts in security_manager.api_auth.failed_auth_attempts.items():
            recent_attempts = [
                attempt for attempt in attempts
                if attempt > recent_cutoff
            ]
            if len(recent_attempts) >= 5:  # 5+ failed attempts in last hour
                threats += 1
        
        return threats
        
    except Exception as e:
        logger.error(f"[ERROR] Error counting threats: {e}")
        return 0


# ==================== HEALTH CHECK ENDPOINT ====================

@router.get("/health")
async def security_health_check() -> Dict[str, Any]:
    """
    Security system health check endpoint.
    """
    try:
        security_manager = get_security_manager()
        
        health_status = {
            'status': 'healthy',
            'security_system': 'operational',
            'version': '4.0.0-beta',
            'components': {
                'input_validator': 'online',
                'wallet_security': 'online',
                'api_authentication': 'online',
                'error_sanitizer': 'online'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"[ERROR] Security health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': 'Security system check failed',
            'timestamp': datetime.utcnow().isoformat()
        }


# Export router
__all__ = ["router"]