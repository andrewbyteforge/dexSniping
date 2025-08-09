"""
File: app/core/performance/circuit_breaker.py

Simple circuit breaker implementation for protecting external service calls.
"""

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union, Awaitable
from dataclasses import dataclass, field
from collections import deque

from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException

logger = setup_logger(__name__, "application")


class CircuitBreakerError(DexSnipingException):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, blocking calls
    HALF_OPEN = "half_open" # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5           # Failures before opening
    recovery_timeout: float = 60.0       # Seconds before trying half-open
    success_threshold: int = 3           # Successes to close from half-open
    timeout: float = 30.0                # Request timeout in seconds


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    recent_failures: deque = field(default_factory=lambda: deque(maxlen=50))


class SimpleCircuitBreaker:
    """
    Simple circuit breaker implementation.
    
    Features:
    - Automatic failure detection
    - Configurable thresholds
    - Half-open state for recovery testing
    - Request timeout handling
    - Statistics tracking
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker name for identification
            config: Configuration parameters
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._lock = asyncio.Lock()
        self._last_state_change = time.time()
        self._half_open_successes = 0
    
    async def call(
        self,
        func: Union[Callable[[], Any], Callable[[], Awaitable[Any]]],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original function exceptions
        """
        async with self._lock:
            # Check circuit state
            await self._update_state()
            
            if self.state == CircuitState.OPEN:
                logger.warning(f"Circuit breaker {self.name} is OPEN, blocking call")
                raise CircuitBreakerError(f"Circuit breaker {self.name} is open")
        
        # Execute the function
        try:
            # Handle both sync and async functions
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = func(*args, **kwargs)
            
            # Record success
            await self._record_success()
            return result
            
        except asyncio.TimeoutError:
            await self._record_timeout()
            raise CircuitBreakerError(f"Request timeout after {self.config.timeout}s")
            
        except Exception as e:
            await self._record_failure(e)
            raise
    
    async def _update_state(self) -> None:
        """Update circuit state based on current conditions."""
        current_time = time.time()
        
        if self.state == CircuitState.OPEN:
            # Check if we should try half-open
            if current_time - self._last_state_change >= self.config.recovery_timeout:
                await self._transition_to_half_open()
        
        elif self.state == CircuitState.CLOSED:
            # Check if we should open due to failures
            if self._should_open_circuit():
                await self._transition_to_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Check if we should close (enough successes)
            if self._half_open_successes >= self.config.success_threshold:
                await self._transition_to_closed()
    
    async def _record_success(self) -> None:
        """Record a successful request."""
        async with self._lock:
            self.stats.total_requests += 1
            self.stats.successful_requests += 1
            self.stats.last_success_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
    
    async def _record_failure(self, exception: Exception) -> None:
        """Record a failed request."""
        async with self._lock:
            self.stats.total_requests += 1
            self.stats.failed_requests += 1
            self.stats.last_failure_time = time.time()
            self.stats.recent_failures.append({
                'timestamp': time.time(),
                'exception': str(exception),
                'type': type(exception).__name__
            })
            
            # Reset half-open success counter on failure
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_successes = 0
                await self._transition_to_open()
    
    async def _record_timeout(self) -> None:
        """Record a timeout."""
        async with self._lock:
            self.stats.total_requests += 1
            self.stats.failed_requests += 1
            self.stats.timeouts += 1
            self.stats.last_failure_time = time.time()
            
            # Timeouts count as failures
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_successes = 0
                await self._transition_to_open()
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened based on failure threshold."""
        return len(self.stats.recent_failures) >= self.config.failure_threshold
    
    async def _transition_to_open(self) -> None:
        """Transition circuit to OPEN state."""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self._last_state_change = time.time()
            self.stats.circuit_opens += 1
            logger.warning(f"Circuit breaker {self.name} transitioned to OPEN")
    
    async def _transition_to_half_open(self) -> None:
        """Transition circuit to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self._last_state_change = time.time()
        self._half_open_successes = 0
        logger.info(f"Circuit breaker {self.name} transitioned to HALF_OPEN")
    
    async def _transition_to_closed(self) -> None:
        """Transition circuit to CLOSED state."""
        self.state = CircuitState.CLOSED
        self._last_state_change = time.time()
        self._half_open_successes = 0
        # Clear recent failures on successful recovery
        self.stats.recent_failures.clear()
        logger.info(f"Circuit breaker {self.name} transitioned to CLOSED")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Statistics dictionary
        """
        success_rate = (
            self.stats.successful_requests / self.stats.total_requests
            if self.stats.total_requests > 0 else 0
        )
        
        return {
            "name": self.name,
            "state": self.state.value,
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "timeouts": self.stats.timeouts,
            "circuit_opens": self.stats.circuit_opens,
            "success_rate": round(success_rate * 100, 2),
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time,
            "recent_failures_count": len(self.stats.recent_failures),
            "time_since_last_state_change": time.time() - self._last_state_change
        }


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.
    """
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        self._breakers: Dict[str, SimpleCircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    def get_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> SimpleCircuitBreaker:
        """
        Get or create a circuit breaker.
        
        Args:
            name: Circuit breaker name
            config: Configuration (uses default if None)
            
        Returns:
            SimpleCircuitBreaker instance
        """
        if name not in self._breakers:
            self._breakers[name] = SimpleCircuitBreaker(name, config)
        
        return self._breakers[name]
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all circuit breakers.
        
        Returns:
            Dictionary mapping breaker names to their stats
        """
        async with self._lock:
            return {
                name: breaker.get_stats()
                for name, breaker in self._breakers.items()
            }
    
    def get_breaker_names(self) -> list:
        """Get list of all circuit breaker names."""
        return list(self._breakers.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all circuit breakers.
        
        Returns:
            Health status summary
        """
        stats = await self.get_all_stats()
        
        open_breakers = [name for name, stat in stats.items() if stat["state"] == "open"]
        half_open_breakers = [name for name, stat in stats.items() if stat["state"] == "half_open"]
        
        total_requests = sum(stat["total_requests"] for stat in stats.values())
        total_failures = sum(stat["failed_requests"] for stat in stats.values())
        
        overall_success_rate = (
            ((total_requests - total_failures) / total_requests * 100)
            if total_requests > 0 else 100
        )
        
        return {
            "status": "unhealthy" if open_breakers else "healthy",
            "total_breakers": len(self._breakers),
            "open_breakers": open_breakers,
            "half_open_breakers": half_open_breakers,
            "overall_success_rate": round(overall_success_rate, 2),
            "total_requests": total_requests,
            "total_failures": total_failures
        }