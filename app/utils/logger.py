"""
Logger Utility
File: app/utils/logger.py

Centralized logging configuration for the trading platform.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    if LOGURU_AVAILABLE:
        # Use loguru if available
        return LoguruWrapper(name)
    
    # Fallback to standard logging
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger


class LoguruWrapper:
    """Wrapper to make loguru compatible with standard logging interface."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = loguru_logger
    
    def info(self, message: str, *args, **kwargs):
        self.logger.info(f"[{self.name}] {message}", *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.logger.error(f"[{self.name}] {message}", *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(f"[{self.name}] {message}", *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(f"[{self.name}] {message}", *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(f"[{self.name}] {message}", *args, **kwargs)
