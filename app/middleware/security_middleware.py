"""
Security Middleware - Phase 5A
File: app/middleware/security_middleware.py
Class: SecurityMiddleware
Methods: dispatch, validate_request, handle_security_error

FastAPI middleware for automatic security validation on all requests.
Integrates with SecurityManager to provide comprehensive protection.
"""

import time
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import setup_logger
from app.core.security.security_manager import (
    get_security_manager, SecurityManager, SecurityLevel
)
from app.core.exceptions import (
    SecurityError, AuthenticationError, AuthorizationError,
    ValidationError, RateLimitError
)

logger = setup_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for comprehensive request security validation.
    
    Features:
    - API key authentication
    - Request rate limiting
    - Input validation
    - Error sanitization
    - Security event logging
    """
    
    def __init__(self, app: ASGIApp, security_manager: Optional[SecurityManager] = None):
        """
        Initialize security middleware.
        
        Args:
            app: FastAPI application
            security_manager: Security manager instance
        """
        super().__init__(app)
        self.security_manager = security_manager or get_security_manager()
        
        # Public endpoints that don't require authentication
        self.public_endpoints = {
            '/',
            '/health',
            '/docs',
            '/openapi.json',
            '/redoc',
            '/dashboard',  # Dashboard has its own auth
        }
        
        # Endpoints that require specific security levels
        self.endpoint_security_levels = {
            '/api/v1/wallet/': SecurityLevel.WALLET_OWNER,
            '/api/v1/trading/': SecurityLevel.AUTHENTICATED,
            '/api/v1/admin/': SecurityLevel.ADMIN,
            '/api/v1/dashboard/': SecurityLevel.AUTHENTICATED,
        }
        
        # Rate limiting configuration
        self.rate_limits = {
            'default': 100,  # requests per minute
            'trading': 30,
            'wallet': 20,
            'admin': 200,
        }
        
        logger.info("🛡️ Security middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through security validation pipeline.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with security headers and validation
        """
        start_time = time.time()
        
        try:
            # Skip security for public endpoints
            if self.is_public_endpoint(request.url.path):
                response = await call_next(request)
                return self.add_security_headers(response)
            
            # Validate request security
            validation_result = await self.validate_request(request)
            if not validation_result['valid']:
                return self.create_error_response(
                    validation_result['error'],
                    validation_result['status_code']
                )
            
            # Add security context to request
            request.state.security_context = validation_result['context']
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self.add_security_headers(response)
            
            # Log successful request
            processing_time = time.time() - start_time
            self.log_request(request, response.status_code, processing_time)
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Security middleware error: {e}")
            
            # Sanitize error for response
            sanitized_error = self.security_manager.error_sanitizer.sanitize_error(
                str(e), 'system_error'
            )
            
            return self.create_error_response(
                sanitized_error,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def is_public_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is public (no auth required).
        
        Args:
            path: Request path
            
        Returns:
            True if public endpoint
        """
        # Exact match for public endpoints
        if path in self.public_endpoints:
            return True
        
        # Check for static file endpoints
        if path.startswith('/static/') or path.startswith('/assets/'):
            return True
        
        # Check for documentation endpoints
        if path.startswith('/docs') or path.startswith('/redoc'):
            return True
        
        return False

    async def validate_request(self, request: Request) -> Dict[str, Any]:
        """
        Comprehensive request validation.
        
        Args:
            request: Incoming request
            
        Returns:
            Validation result with context
        """
        try:
            # Extract API key
            api_key = self.extract_api_key(request)
            if not api_key:
                return {
                    'valid': False,
                    'error': 'API key required',
                    'status_code': status.HTTP_401_UNAUTHORIZED
                }
            
            # Check rate limiting
            if not self.check_rate_limit(request, api_key):
                return {
                    'valid': False,
                    'error': 'Rate limit exceeded',
                    'status_code': status.HTTP_429_TOO_MANY_REQUESTS
                }
            
            # Get request body for validation
            request_data = await self.get_request_data(request)
            
            # Validate with security manager
            is_valid, error_message = self.security_manager.validate_api_request(
                api_key, request.url.path, request_data
            )
            
            if not is_valid:
                return {
                    'valid': False,
                    'error': error_message,
                    'status_code': status.HTTP_400_BAD_REQUEST
                }
            
            # Get API key metadata
            key_data = self.security_manager.api_auth.api_keys.get(api_key, {})
            
            return {
                'valid': True,
                'context': {
                    'user_id': key_data.get('user_id'),
                    'key_type': key_data.get('key_type'),
                    'permissions': key_data.get('permissions', []),
                    'api_key': api_key
                }
            }
            
        except (AuthenticationError, AuthorizationError) as e:
            return {
                'valid': False,
                'error': str(e),
                'status_code': status.HTTP_401_UNAUTHORIZED
            }
        except ValidationError as e:
            return {
                'valid': False,
                'error': str(e),
                'status_code': status.HTTP_400_BAD_REQUEST
            }
        except Exception as e:
            logger.error(f"❌ Request validation error: {e}")
            return {
                'valid': False,
                'error': 'Request validation failed',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }

    def extract_api_key(self, request: Request) -> Optional[str]:
        """
        Extract API key from request headers or query parameters.
        
        Args:
            request: Incoming request
            
        Returns:
            API key or None
        """
        # Check Authorization header (Bearer token)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check X-API-Key header
        api_key_header = request.headers.get('X-API-Key')
        if api_key_header:
            return api_key_header
        
        # Check query parameter
        api_key_param = request.query_params.get('api_key')
        if api_key_param:
            return api_key_param
        
        return None

    async def get_request_data(self, request: Request) -> Dict[str, Any]:
        """
        Extract request data for validation.
        
        Args:
            request: Incoming request
            
        Returns:
            Request data dictionary
        """
        try:
            # Get query parameters
            data = dict(request.query_params)
            
            # Get JSON body if present
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        # Read body without consuming the stream
                        body = await request.body()
                        if body:
                            json_data = json.loads(body.decode())
                            data.update(json_data)
                    except json.JSONDecodeError:
                        logger.warning("⚠️ Invalid JSON in request body")
                    except Exception as e:
                        logger.warning(f"⚠️ Error reading request body: {e}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error extracting request data: {e}")
            return {}

    def check_rate_limit(self, request: Request, api_key: str) -> bool:
        """
        Check if request is within rate limits.
        
        Args:
            request: Incoming request
            api_key: API key for rate limiting
            
        Returns:
            True if within limits
        """
        try:
            # Use security manager's rate limiting
            return self.security_manager.api_auth.check_rate_limit(api_key)
            
        except Exception as e:
            logger.error(f"❌ Rate limit check error: {e}")
            return True  # Allow request on error

    def add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to response.
        
        Args:
            response: Response to modify
            
        Returns:
            Response with security headers
        """
        # Security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' wss: https:"
            ),
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }
        
        # Add headers to response
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Add API version header
        response.headers['X-API-Version'] = '4.0.0'
        
        return response

    def create_error_response(self, error_message: str, status_code: int) -> JSONResponse:
        """
        Create standardized error response.
        
        Args:
            error_message: Error message
            status_code: HTTP status code
            
        Returns:
            JSON error response
        """
        error_response = {
            'error': True,
            'message': error_message,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        response = JSONResponse(
            content=error_response,
            status_code=status_code
        )
        
        return self.add_security_headers(response)

    def log_request(self, request: Request, status_code: int, processing_time: float):
        """
        Log request for security monitoring.
        
        Args:
            request: Request object
            status_code: Response status code
            processing_time: Request processing time
        """
        try:
            # Get security context if available
            security_context = getattr(request.state, 'security_context', {})
            
            # Log request details
            log_data = {
                'method': request.method,
                'path': request.url.path,
                'status_code': status_code,
                'processing_time': round(processing_time, 3),
                'user_id': security_context.get('user_id'),
                'key_type': security_context.get('key_type'),
                'client_ip': request.client.host if request.client else 'unknown',
                'user_agent': request.headers.get('user-agent', 'unknown')
            }
            
            # Log security event
            self.security_manager.log_security_event('api_request', log_data)
            
        except Exception as e:
            logger.error(f"❌ Request logging error: {e}")

    def get_endpoint_security_level(self, path: str) -> SecurityLevel:
        """
        Get required security level for endpoint.
        
        Args:
            path: Request path
            
        Returns:
            Required security level
        """
        for endpoint_prefix, level in self.endpoint_security_levels.items():
            if path.startswith(endpoint_prefix):
                return level
        
        return SecurityLevel.AUTHENTICATED  # Default level


class SecurityConfig:
    """Security configuration for middleware."""
    
    def __init__(self):
        """Initialize security configuration."""
        self.enforce_https = True
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.timeout_seconds = 30
        self.enable_cors = True
        self.cors_origins = ['http://localhost:3000', 'http://localhost:8000']
        
        # Rate limiting
        self.global_rate_limit = 1000  # requests per minute per IP
        self.burst_limit = 50  # burst requests
        
        # Security features
        self.enable_csrf_protection = True
        self.enable_request_logging = True
        self.enable_error_sanitization = True


def create_security_middleware(app: ASGIApp, config: Optional[SecurityConfig] = None) -> SecurityMiddleware:
    """
    Create security middleware with configuration.
    
    Args:
        app: FastAPI application
        config: Security configuration
        
    Returns:
        Configured security middleware
    """
    if config is None:
        config = SecurityConfig()
    
    middleware = SecurityMiddleware(app)
    
    logger.info("🛡️ Security middleware created with full protection")
    return middleware


# Export middleware classes
__all__ = ['SecurityMiddleware', 'SecurityConfig', 'create_security_middleware']