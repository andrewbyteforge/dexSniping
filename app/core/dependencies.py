"""
File: app/api/dependencies.py

FastAPI dependencies for authentication, rate limiting, and database sessions.
Provides reusable dependency functions for API endpoints.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Generator, Dict, Any
import time
from collections import defaultdict, deque

from app.models.database import get_db
from app.core.blockchain.multi_chain_manager import MultiChainManager
from app.config import settings
from app.utils.exceptions import APIRateLimitError, APIUnauthorizedError
from app.utils.logger import setup_logger
from app.models.database import get_db

logger = setup_logger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# Rate limiting storage
rate_limit_storage: Dict[str, deque] = defaultdict(deque)


async def get_database_session() -> Generator[AsyncSession, None, None]:
    """
    Database session dependency.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


async def get_multi_chain_manager(request: Request) -> MultiChainManager:
    """
    Get multi-chain manager from application state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        MultiChainManager instance
        
    Raises:
        HTTPException: If multi-chain manager not available
    """
    if not hasattr(request.app.state, 'multi_chain_manager'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-chain manager not available"
        )
    return request.app.state.multi_chain_manager


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Verify API key authentication.
    
    Args:
        credentials: HTTP bearer credentials
        
    Returns:
        API key if valid, None for public endpoints
        
    Raises:
        HTTPException: If authentication fails
    """
    # For single user application, we'll use a simple approach
    # In production, this would integrate with a proper auth system
    
    if credentials is None:
        return None  # Allow unauthenticated access for public endpoints
    
    # Verify the token (simplified for single user)
    if credentials.credentials == settings.secret_key:
        return credentials.credentials
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def rate_limiter(request: Request) -> None:
    """
    Rate limiting dependency.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries (older than 1 hour)
    hour_ago = current_time - 3600
    rate_limit_storage[client_ip] = deque(
        timestamp for timestamp in rate_limit_storage[client_ip]
        if timestamp > hour_ago
    )
    
    # Check rate limit
    if len(rate_limit_storage[client_ip]) >= settings.api_rate_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": "3600"}
        )
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)


async def websocket_rate_limiter(client_ip: str) -> bool:
    """
    Rate limiting for WebSocket connections.
    
    Args:
        client_ip: Client IP address
        
    Returns:
        True if request is allowed, False if rate limited
    """
    current_time = time.time()
    ws_key = f"ws_{client_ip}"
    
    # Clean old entries (older than 1 minute)
    minute_ago = current_time - 60
    rate_limit_storage[ws_key] = deque(
        timestamp for timestamp in rate_limit_storage[ws_key]
        if timestamp > minute_ago
    )
    
    # Check rate limit
    if len(rate_limit_storage[ws_key]) >= settings.websocket_rate_limit:
        return False
    
    # Add current request
    rate_limit_storage[ws_key].append(current_time)
    return True


async def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> Dict[str, int]:
    """
    Pagination parameters dependency.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Dictionary with pagination parameters
    """
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 1000:
        limit = 100
    
    return {"skip": skip, "limit": limit}


class RequireAuth:
    """Dependency class for endpoints that require authentication."""
    
    def __init__(self, required: bool = True):
        self.required = required
    
    async def __call__(
        self,
        api_key: Optional[str] = Depends(verify_api_key)
    ) -> Optional[str]:
        if self.required and api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return api_key


# Common dependency instances
require_auth = RequireAuth(required=True)
optional_auth = RequireAuth(required=False)


# File: app/api/v1/api.py

"""
API router configuration for version 1 endpoints.
Combines all endpoint routers into a single API router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    tokens,
    trading,
    portfolio,
    arbitrage,
    websocket
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    tokens.router,
    prefix="/tokens",
    tags=["tokens"]
)

api_router.include_router(
    trading.router,
    prefix="/trading",
    tags=["trading"]
)

api_router.include_router(
    portfolio.router,
    prefix="/portfolio",
    tags=["portfolio"]
)

api_router.include_router(
    arbitrage.router,
    prefix="/arbitrage",
    tags=["arbitrage"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)


@api_router.get("/")
async def api_root():
    """API root endpoint with basic information."""
    return {
        "message": "DEX Sniping API v1",
        "version": "1.0.0",
        "documentation": "/api/docs",
        "endpoints": {
            "tokens": "/api/v1/tokens",
            "trading": "/api/v1/trading",
            "portfolio": "/api/v1/portfolio",
            "arbitrage": "/api/v1/arbitrage",
            "websocket": "/api/v1/ws"
        }
    }


@api_router.get("/health")
async def api_health():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": "2025-01-01T00:00:00Z"
    }