"""
Enhanced Logger Setup - All Levels Supported
File: app/utils/logger.py

Logger that supports any level name and avoids Unicode issues.
"""

import logging
import sys
from typing import Optional

def setup_logger(
    name: str, 
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with flexible level support.
    
    Args:
        name: Logger name (can be any string)
        level: Logging level
        format_string: Custom format string
        
    Returns:
        logging.Logger: Configured logger
    """
    if format_string is None:
        format_string = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    
    # Convert level to standard logging level if it's a string
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with UTF-8 encoding
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set UTF-8 encoding for the handler if possible
    if hasattr(handler.stream, 'reconfigure'):
        try:
            handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass
    
    # Create formatter
    formatter = logging.Formatter(format_string, datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

# Alias for backward compatibility
def get_logger(name: str) -> logging.Logger:
    """Get logger with default configuration."""
    return setup_logger(name)


# Additional logger functions for backward compatibility
def get_trading_logger(name: str = "trading") -> logging.Logger:
    """Get trading-specific logger."""
    return setup_logger(name)

def get_application_logger(name: str = "application") -> logging.Logger:
    """Get application-specific logger."""
    return setup_logger(name)

def get_websocket_logger(name: str = "websocket") -> logging.Logger:
    """Get websocket-specific logger."""
    return setup_logger(name)

def get_ai_logger(name: str = "ai") -> logging.Logger:
    """Get AI-specific logger."""
    return setup_logger(name)

def get_blockchain_logger(name: str = "blockchain") -> logging.Logger:
    """Get blockchain-specific logger."""
    return setup_logger(name)


# Additional logger functions for backward compatibility
def get_trading_logger(name: str = "trading") -> logging.Logger:
    """Get trading-specific logger."""
    return setup_logger(name)

def get_application_logger(name: str = "application") -> logging.Logger:
    """Get application-specific logger."""
    return setup_logger(name)

def get_websocket_logger(name: str = "websocket") -> logging.Logger:
    """Get websocket-specific logger."""
    return setup_logger(name)

def get_ai_logger(name: str = "ai") -> logging.Logger:
    """Get AI-specific logger."""
    return setup_logger(name)

def get_blockchain_logger(name: str = "blockchain") -> logging.Logger:
    """Get blockchain-specific logger."""
    return setup_logger(name)


def get_performance_logger(name: str = "performance"):
    """Get performance logger."""
    return setup_logger(name)

def get_strategy_logger(name: str = "strategy"):
    """Get strategy logger."""
    return setup_logger(name)

def get_multichain_logger(name: str = "multichain"):
    """Get multichain logger.""" 
    return setup_logger(name)
