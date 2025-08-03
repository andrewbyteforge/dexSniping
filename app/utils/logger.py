"""
Enhanced Logger Module
File: app/utils/logger.py

Professional logging configuration with structured output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup logger with enhanced formatting and file output.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5s] %(message)s [%(name)s]',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_application_logger() -> logging.Logger:
    """Get the main application logger."""
    return setup_logger("dex_sniper")
