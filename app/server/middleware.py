"""
Middleware Configuration
File: app/server/middleware.py

Configures all middleware for the FastAPI application including CORS,
security, logging, and error handling.
"""

import time
from typing import Callable, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response: HTTP response
        """
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"in {process_time:.3f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as error:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"in {process_time:.3f}s - {error}"
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to responses.
    """
    
    def __init__(self, app, security_headers: Dict[str, str] = None):
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            security_headers: Custom security headers to add
        """
        super().__init__(app)
        
        self.security_headers = security_headers or {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws://localhost:* wss://localhost:*;"
            ),
        }
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Add security headers to response.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response: HTTP response with security headers
        """
        response = await call_next(request)
        
        # Add security headers
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If middleware setup fails
    """
    try:
        # CORS middleware - must be added first
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify exact origins
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
        logger.info("CORS middleware configured")
        
        # Trusted host middleware for security
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
        )
        logger.info("Trusted host middleware configured")
        
        # Security headers middleware
        app.add_middleware(SecurityHeadersMiddleware)
        logger.info("Security headers middleware configured")
        
        # Request logging middleware
        app.add_middleware(RequestLoggingMiddleware)
        logger.info("Request logging middleware configured")
        
        logger.info("All middleware configured successfully")
        
    except Exception as error:
        logger.error(f"Failed to setup middleware: {error}")
        raise RuntimeError(f"Middleware setup failed: {error}")


def create_cors_middleware_config() -> Dict[str, Any]:
    """
    Create CORS middleware configuration.
    
    Returns:
        Dict[str, Any]: CORS configuration
    """
    return {
        "allow_origins": [
            "http://localhost:3000",  # React dev server
            "http://localhost:8000",  # FastAPI server
            "http://127.0.0.1:8000",  # FastAPI server
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
        ],
    }


def create_security_headers_config() -> Dict[str, str]:
    """
    Create security headers configuration.
    
    Returns:
        Dict[str, str]: Security headers configuration
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        ),
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws://localhost:* wss://localhost:* https://api.coingecko.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "object-src 'none'; "
            "base-uri 'self';"
        ),
    }