"""
Connection pool manager for efficient HTTP connections and rate limiting.
"""

import aiohttp
import asyncio
from typing import Dict, Optional
from asyncio_throttle import Throttler
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionPoolManager:
    """Manages HTTP connection pools and rate limiting for blockchain RPC calls."""
    
    def __init__(self):
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.throttlers: Dict[str, Throttler] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize connection pools for all networks."""
        if self._initialized:
            return
        
        # Create connection pools with optimized settings
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=20,  # Max connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Create session for blockchain RPC calls
        self.sessions['blockchain'] = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DEXSniping/1.0'}
        )
        
        # Create rate limiters (adjust based on API limits)
        self.throttlers['default'] = Throttler(rate_limit=10, period=1)  # 10 calls per second
        self.throttlers['alchemy'] = Throttler(rate_limit=25, period=1)  # 25 calls per second
        self.throttlers['infura'] = Throttler(rate_limit=10, period=1)   # 10 calls per second
        
        self._initialized = True
        logger.info("Connection pool manager initialized")
    
    async def get_session(self, pool_type: str = 'blockchain') -> aiohttp.ClientSession:
        """Get a connection session."""
        if not self._initialized:
            await self.initialize()
        return self.sessions.get(pool_type, self.sessions['blockchain'])
    
    async def get_throttler(self, provider: str = 'default') -> Throttler:
        """Get rate limiter for specific provider."""
        return self.throttlers.get(provider, self.throttlers['default'])
    
    async def close(self):
        """Close all connection pools."""
        for session in self.sessions.values():
            await session.close()
        self.sessions.clear()
        logger.info("All connection pools closed")


# Global instance
connection_pool = ConnectionPoolManager()