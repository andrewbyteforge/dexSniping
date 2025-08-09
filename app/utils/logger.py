"""
Logger Utility Module
File: app/utils/logger.py

Professional logging system for the DEX Sniper Pro trading bot with
structured logging, performance monitoring, and configurable output formats.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        return super().format(record)


class TradingLogger:
    """Professional trading logger with structured logging capabilities."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """
        Initialize trading logger.
        
        Args:
            name: Logger name (usually __name__)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        
        # Handle custom log levels
        if level.upper() == "APPLICATION":
            level = "INFO"  # Map APPLICATION to INFO
        
        # Validate logging level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            level = "INFO"  # Default to INFO for invalid levels
            
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers."""
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - [LOG] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler (if logs directory exists)
        logs_dir = Path("logs")
        if logs_dir.exists() or self._create_logs_dir():
            file_handler = logging.FileHandler(
                logs_dir / "dex_sniper.log",
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            file_formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.addHandler(console_handler)
    
    def _create_logs_dir(self) -> bool:
        """Create logs directory if it doesn't exist."""
        try:
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            return True
        except Exception:
            return False
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.logger.debug(message, extra=extra or {})
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.logger.error(message, extra=extra or {})
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.logger.critical(message, extra=extra or {})
    
    def trade_execution(self, action: str, token: str, amount: float, price: float, success: bool):
        """Log trade execution with structured data."""
        status = "SUCCESS" if success else "FAILED"
        message = f"TRADE {status}: {action} {amount} {token} @ {price}"
        
        extra = {
            'action': action,
            'token': token,
            'amount': amount,
            'price': price,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if success:
            self.info(message, extra=extra)
        else:
            self.error(message, extra=extra)
    
    def performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metrics."""
        message = f"PERFORMANCE: {metric_name} = {value} {unit}".strip()
        
        extra = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.info(message, extra=extra)
    
    def exception(self, message: str, exc_info: bool = True):
        """Log exception with traceback."""
        self.logger.error(message, exc_info=exc_info)


def setup_logger(name: str, level: str = "INFO") -> TradingLogger:
    """
    Setup and return a trading logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        TradingLogger: Configured logger instance
    """
    # Handle custom log levels
    if level.upper() == "APPLICATION":
        level = "INFO"  # Map APPLICATION to INFO
    
    return TradingLogger(name, level)


# Global logger configuration
def configure_global_logging(level: str = "INFO", format_style: str = "detailed"):
    """
    Configure global logging settings for the entire application.
    
    Args:
        level: Global logging level
        format_style: Format style ('simple', 'detailed', 'json')
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Setup new handlers based on format style
    if format_style == "simple":
        formatter = logging.Formatter('%(levelname)s: %(message)s')
    elif format_style == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:  # detailed
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


# Convenience functions for quick logging
def get_logger(name: str) -> TradingLogger:
    """Get a logger instance (alias for setup_logger)."""
    return setup_logger(name)


def log_trade(action: str, token: str, amount: float, price: float, success: bool, logger_name: str = "trading"):
    """Quick trade logging function."""
    logger = setup_logger(logger_name)
    logger.trade_execution(action, token, amount, price, success)


def log_performance(metric_name: str, value: float, unit: str = "", logger_name: str = "performance"):
    """Quick performance logging function."""
    logger = setup_logger(logger_name)
    logger.performance_metric(metric_name, value, unit)


# Export main functions
__all__ = [
    "setup_logger",
    "TradingLogger", 
    "configure_global_logging",
    "get_logger",
    "log_trade",
    "log_performance"
]