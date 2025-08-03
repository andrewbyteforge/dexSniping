"""
File: app/core/discovery/token_scanner.py

Core token discovery engine for scanning blockchain networks and finding new ERC-20 tokens.
Integrates with performance infrastructure for optimal scanning and caching.
"""

import asyncio
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time

from app.core.blockchain.base_chain import BaseChain, TokenInfo
from app.core.blockchain.multi_chain_manager import MultiChainManager
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__)


class TokenScannerError(DexSnipingException):
    """Exception raised when token scanning operations fail."""
    pass


@dataclass
class ScanConfig:
    """Configuration for token scanning operations."""
    max_blocks_per_scan: int = 10
    parallel_chains: int = 3
    min_liquidity_usd: float = 1000.0
    cache_ttl_seconds: int = 300
    retry_attempts: int = 3
    block_confirmation_delay: int = 2


@dataclass
class ScanResult:
    """Result of a token scanning operation."""
    network: str
    tokens_found: List[TokenInfo]
    blocks_scanned: int
    scan_duration_seconds: float
    from_block: int
    to_block: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def tokens_per_block(self) -> float:
        """Calculate tokens found per block scanned."""
        return len(self.tokens_found) / self.blocks_scanned if self.blocks_scanned > 0 else 0


@dataclass
class DiscoveryStats:
    """Statistics for token discovery operations."""
    total_scans: int = 0
    total_tokens_found: int = 0
    total_blocks_scanned: int = 0
    successful_scans: int = 0
    failed_scans: int = 0
    average_scan_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    last_scan_time: Optional[datetime] = None


class TokenScanner:
    """
    Advanced token discovery engine with performance optimization.
    
    Features:
    - Multi-chain parallel scanning
    - Intelligent block range optimization
    - Performance caching with TTL
    - Circuit breaker protection
    - Comprehensive filtering
    - Real-time statistics
    """
    
    def __init__(self, multi_chain_manager: Optional[MultiChainManager] = None):
        """
        Initialize token scanner.
        
        Args:
            multi_chain_manager: Multi-chain manager instance
        """
        if multi_chain_manager is None:
            from app.core.blockchain.multi_chain_manager import MultiChainManager
            multi_chain_manager = MultiChainManager()

        self.multi_chain_manager = multi_chain_manager
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.config = ScanConfig(
            max_blocks_per_scan=getattr(settings, 'max_blocks_per_scan', 10),
            min_liquidity_usd=getattr(settings, 'min_liquidity_usd_int', 1000),
            cache_ttl_seconds=getattr(settings, 'cache_ttl_seconds', 300)
        )
        self.stats = DiscoveryStats()
        self._scanning = False
        self._last_scanned_blocks: Dict[str, int] = {}
    
    async def scan_all_networks(
        self,
        block_offset: int = 10,
        networks: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ScanResult]:
        """
        Scan all enabled networks for new tokens.
        
        Args:
            block_offset: Number of blocks back from latest to scan
            networks: Specific networks to scan (all if None)
            filters: Additional filtering criteria
            
        Returns:
            Dictionary mapping network names to scan results
        """
        if self._scanning:
            logger.warning("Token scanning already in progress, skipping duplicate request")
            return {}
        
        self._scanning = True
        start_time = time.time()
        
        try:
            logger.info(f"Starting token discovery scan across networks")
            
            # Get target networks
            if networks is None:
                networks = list(await self.multi_chain_manager.get_enabled_networks())
            
            # Validate networks
            enabled_networks = await self.multi_chain_manager.get_enabled_networks()
            valid_networks = [n for n in networks if n in enabled_networks]
            
            if not valid_networks:
                raise TokenScannerError(f"No valid networks to scan from: {networks}")
            
            # Parallel scanning with semaphore for resource management
            semaphore = asyncio.Semaphore(self.config.parallel_chains)
            scan_tasks = []
            
            for network in valid_networks:
                task = self._scan_network_with_protection(
                    semaphore, network, block_offset, filters
                )
                scan_tasks.append(task)
            
            # Execute scans concurrently
            scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
            
            # Process results
            results = {}
            total_tokens = 0
            successful_scans = 0
            
            for i, result in enumerate(scan_results):
                network = valid_networks[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Scan failed for {network}: {result}")
                    self.stats.failed_scans += 1
                    continue
                
                if result:
                    results[network] = result
                    total_tokens += len(result.tokens_found)
                    successful_scans += 1
                    
                    logger.info(
                        f"Scan completed for {network}: "
                        f"{len(result.tokens_found)} tokens in {result.blocks_scanned} blocks"
                    )
            
            # Update statistics
            scan_duration = time.time() - start_time
            self.stats.total_scans += 1
            self.stats.successful_scans += successful_scans
            self.stats.total_tokens_found += total_tokens
            self.stats.average_scan_time = (
                (self.stats.average_scan_time * (self.stats.total_scans - 1) + scan_duration)
                / self.stats.total_scans
            )
            self.stats.last_scan_time = datetime.utcnow()
            
            logger.info(
                f"Multi-network scan completed: {total_tokens} tokens found "
                f"across {successful_scans} networks in {scan_duration:.2f}s"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Multi-network scan failed: {e}")
            self.stats.failed_scans += 1
            raise TokenScannerError(f"Multi-network scan failed: {e}")
        
        finally:
            self._scanning = False
    
    async def scan_network(
        self,
        network: str,
        block_offset: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[ScanResult]:
        """
        Scan a specific network for new tokens.
        
        Args:
            network: Network name to scan
            block_offset: Number of blocks back from latest to scan
            filters: Additional filtering criteria
            
        Returns:
            ScanResult or None if scan failed
        """
        semaphore = asyncio.Semaphore(1)  # Single network scan
        return await self._scan_network_with_protection(
            semaphore, network, block_offset, filters
        )
    
    async def _scan_network_with_protection(
        self,
        semaphore: asyncio.Semaphore,
        network: str,
        block_offset: int,
        filters: Optional[Dict[str, Any]]
    ) -> Optional[ScanResult]:
        """
        Scan network with circuit breaker protection and resource limiting.
        
        Args:
            semaphore: Asyncio semaphore for resource limiting
            network: Network name
            block_offset: Block offset from latest
            filters: Filtering criteria
            
        Returns:
            ScanResult or None if failed
        """
        async with semaphore:
            # Circuit breaker protection
            breaker = self.circuit_breaker_manager.get_breaker(f"token_scan_{network}")
            
            try:
                return await breaker.call(
                    self._perform_network_scan,
                    network,
                    block_offset,
                    filters
                )
            except Exception as e:
                logger.error(f"Protected scan failed for {network}: {e}")
                return None
    
    async def _perform_network_scan(
        self,
        network: str,
        block_offset: int,
        filters: Optional[Dict[str, Any]]
    ) -> ScanResult:
        """
        Perform the actual network scanning operation.
        
        Args:
            network: Network name
            block_offset: Block offset from latest
            filters: Filtering criteria
            
        Returns:
            ScanResult with discovered tokens
        """
        start_time = time.time()
        
        # Get chain instance
        chain = await self.multi_chain_manager.get_chain(network)
        if not chain:
            raise TokenScannerError(f"Chain {network} not available")
        
        # Determine scan range
        latest_block = await chain.get_latest_block_number()
        from_block = max(
            latest_block - block_offset,
            self._last_scanned_blocks.get(network, latest_block - block_offset)
        )
        to_block = latest_block - self.config.block_confirmation_delay  # Wait for confirmations
        
        # Limit scan range
        if to_block - from_block > self.config.max_blocks_per_scan:
            from_block = to_block - self.config.max_blocks_per_scan
        
        logger.info(f"Scanning {network} blocks {from_block} to {to_block}")
        
        # Check cache first
        cache_key = f"token_scan_{network}_{from_block}_{to_block}"
        cached_result = await cache_manager.get(cache_key, namespace="discovery")
        
        if cached_result:
            logger.debug(f"Using cached scan result for {network}")
            self.stats.cache_hits += 1
            # Convert cached data back to ScanResult
            return ScanResult(
                network=cached_result["network"],
                tokens_found=[
                    TokenInfo(**token_data) for token_data in cached_result["tokens_found"]
                ],
                blocks_scanned=cached_result["blocks_scanned"],
                scan_duration_seconds=cached_result["scan_duration_seconds"],
                from_block=cached_result["from_block"],
                to_block=cached_result["to_block"],
                timestamp=datetime.fromisoformat(cached_result["timestamp"])
            )
        
        self.stats.cache_misses += 1
        
        # Perform blockchain scan
        raw_tokens = await chain.scan_new_tokens(from_block, to_block)
        
        # Apply filters
        filtered_tokens = await self._apply_filters(raw_tokens, chain, filters)
        
        # Create result
        scan_duration = time.time() - start_time
        blocks_scanned = max(1, to_block - from_block + 1)
        
        result = ScanResult(
            network=network,
            tokens_found=filtered_tokens,
            blocks_scanned=blocks_scanned,
            scan_duration_seconds=scan_duration,
            from_block=from_block,
            to_block=to_block
        )
        
        # Cache result
        cache_data = {
            "network": result.network,
            "tokens_found": [
                {
                    "address": token.address,
                    "name": token.name,
                    "symbol": token.symbol,
                    "decimals": token.decimals,
                    "total_supply": token.total_supply,
                    "verified": token.verified,
                    "created_at": token.created_at,
                    "creator": token.creator
                }
                for token in result.tokens_found
            ],
            "blocks_scanned": result.blocks_scanned,
            "scan_duration_seconds": result.scan_duration_seconds,
            "from_block": result.from_block,
            "to_block": result.to_block,
            "timestamp": result.timestamp.isoformat()
        }
        
        await cache_manager.set(
            cache_key,
            cache_data,
            ttl=self.config.cache_ttl_seconds,
            namespace="discovery"
        )
        
        # Update last scanned block
        self._last_scanned_blocks[network] = to_block
        
        # Update stats
        self.stats.total_blocks_scanned += blocks_scanned
        
        return result
    
    async def _apply_filters(
        self,
        tokens: List[TokenInfo],
        chain: BaseChain,
        filters: Optional[Dict[str, Any]]
    ) -> List[TokenInfo]:
        """
        Apply filtering criteria to discovered tokens.
        
        Args:
            tokens: Raw discovered tokens
            chain: Blockchain chain instance
            filters: Filtering criteria
            
        Returns:
            Filtered list of tokens
        """
        if not tokens:
            return tokens
        
        filtered_tokens = []
        
        for token in tokens:
            try:
                # Apply basic filters
                if not self._passes_basic_filters(token):
                    continue
                
                # Apply liquidity filter if requested
                if filters and filters.get('check_liquidity', False):
                    liquidity_info = await chain.get_token_liquidity(token.address)
                    total_liquidity = sum(
                        float(li.total_liquidity_usd) for li in liquidity_info
                    ) if liquidity_info else 0
                    
                    if total_liquidity < self.config.min_liquidity_usd:
                        continue
                
                # Apply custom filters
                if filters and not self._passes_custom_filters(token, filters):
                    continue
                
                filtered_tokens.append(token)
                
            except Exception as e:
                logger.warning(f"Filter check failed for token {token.address}: {e}")
                continue
        
        return filtered_tokens
    
    def _passes_basic_filters(self, token: TokenInfo) -> bool:
        """
        Check if token passes basic filtering criteria.
        
        Args:
            token: Token to check
            
        Returns:
            True if token passes basic filters
        """
        # Must have basic token properties
        if not token.name or not token.symbol or token.decimals is None:
            return False
        
        # Symbol length check
        if len(token.symbol) > 20 or len(token.symbol) < 1:
            return False
        
        # Name length check
        if len(token.name) > 100 or len(token.name) < 1:
            return False
        
        # Decimals range check
        if token.decimals < 0 or token.decimals > 18:
            return False
        
        return True
    
    def _passes_custom_filters(
        self,
        token: TokenInfo,
        filters: Dict[str, Any]
    ) -> bool:
        """
        Apply custom filtering criteria.
        
        Args:
            token: Token to check
            filters: Custom filter criteria
            
        Returns:
            True if token passes custom filters
        """
        # Minimum total supply filter
        if 'min_total_supply' in filters:
            if not token.total_supply or token.total_supply < filters['min_total_supply']:
                return False
        
        # Maximum total supply filter
        if 'max_total_supply' in filters:
            if token.total_supply and token.total_supply > filters['max_total_supply']:
                return False
        
        # Symbol pattern filter
        if 'symbol_pattern' in filters:
            import re
            pattern = filters['symbol_pattern']
            if not re.search(pattern, token.symbol, re.IGNORECASE):
                return False
        
        # Verified contracts only filter
        if filters.get('verified_only', False) and not token.verified:
            return False
        
        return True
    
    async def get_discovery_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive discovery statistics.
        
        Returns:
            Dictionary containing discovery statistics
        """
        # Get cache stats
        cache_stats = await cache_manager.get_stats()
        
        # Get circuit breaker stats
        breaker_stats = await self.circuit_breaker_manager.get_all_stats()
        discovery_breakers = {
            name: stats for name, stats in breaker_stats.items()
            if name.startswith('token_scan_')
        }
        
        return {
            "discovery_stats": {
                "total_scans": self.stats.total_scans,
                "successful_scans": self.stats.successful_scans,
                "failed_scans": self.stats.failed_scans,
                "success_rate": (
                    self.stats.successful_scans / self.stats.total_scans * 100
                    if self.stats.total_scans > 0 else 0
                ),
                "total_tokens_found": self.stats.total_tokens_found,
                "total_blocks_scanned": self.stats.total_blocks_scanned,
                "average_scan_time": self.stats.average_scan_time,
                "tokens_per_scan": (
                    self.stats.total_tokens_found / self.stats.successful_scans
                    if self.stats.successful_scans > 0 else 0
                ),
                "last_scan_time": self.stats.last_scan_time.isoformat() if self.stats.last_scan_time else None
            },
            "cache_performance": {
                "hits": self.stats.cache_hits,
                "misses": self.stats.cache_misses,
                "hit_rate": (
                    self.stats.cache_hits / (self.stats.cache_hits + self.stats.cache_misses) * 100
                    if (self.stats.cache_hits + self.stats.cache_misses) > 0 else 0
                ),
                "cache_type": cache_stats.get("cache_type", "unknown")
            },
            "circuit_breakers": discovery_breakers,
            "configuration": {
                "max_blocks_per_scan": self.config.max_blocks_per_scan,
                "parallel_chains": self.config.parallel_chains,
                "min_liquidity_usd": self.config.min_liquidity_usd,
                "cache_ttl_seconds": self.config.cache_ttl_seconds
            },
            "last_scanned_blocks": self._last_scanned_blocks.copy()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the token scanner.
        
        Returns:
            Health status information
        """
        try:
            # Check if multi-chain manager is healthy
            chain_health = await self.multi_chain_manager.get_health_status()
            healthy_chains = sum(
                1 for health in chain_health.values()
                if health.status.value == 'connected'
            )

            # Check circuit breakers
            breaker_health = await self.circuit_breaker_manager.health_check()

            # Determine overall health
            is_healthy = (
                healthy_chains > 0 and
                breaker_health["status"] == "healthy" and
                not self._scanning  # Not stuck in scanning
            )

            return {
                "status": "healthy" if is_healthy else "degraded",
                "connected_chains": healthy_chains,
                "total_configured_chains": len(chain_health),
                "circuit_breaker_status": breaker_health["status"],
                "currently_scanning": self._scanning,
                "last_scan": self.stats.last_scan_time.isoformat() if self.stats.last_scan_time else None,
                "total_scans_completed": self.stats.total_scans,
                "average_scan_duration": self.stats.average_scan_time
            }

        except Exception as e:
            logger.error(f"Token scanner health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "currently_scanning": self._scanning
            }
