"""
Circuit Breaker Manager
File: app/core/performance/circuit_breaker.py

Simple circuit breaker implementation for resilience.
"""

import time
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = Exception


class CircuitBreaker:
    """
    Simple circuit breaker implementation.
    
    Prevents cascading failures by temporarily disabling failing operations.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker name
            config: Configuration settings
        """
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
        logger.info(f"[OK] Circuit breaker '{name}' initialized")
    
    def call(self, func, *args, **kwargs):
        """
        Call function through circuit breaker.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"[INFO] Circuit breaker '{self.name}' moved to HALF_OPEN")
            else:
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # Require 3 successes to close
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info(f"[OK] Circuit breaker '{self.name}' CLOSED")
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"[WARN] Circuit breaker '{self.name}' OPENED")
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if self.last_failure_time is None:
            return False
        
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state information."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "success_count": self.success_count
        }


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers.
    """
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        logger.info("[OK] Circuit breaker manager initialized")
    
    def get_circuit_breaker(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker.
        
        Args:
            name: Circuit breaker name
            config: Configuration (uses default if None)
            
        Returns:
            CircuitBreaker instance
        """
        if name not in self.circuit_breakers:
            config = config or CircuitBreakerConfig()
            self.circuit_breakers[name] = CircuitBreaker(name, config)
        
        return self.circuit_breakers[name]
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers."""
        return {
            name: cb.get_state() 
            for name, cb in self.circuit_breakers.items()
        }


# Global circuit breaker manager
_circuit_breaker_manager = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get global circuit breaker manager."""
    global _circuit_breaker_manager
    
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager()
    
    return _circuit_breaker_manager
