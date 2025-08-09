"""
Enhanced Logger Utility
File: app/utils/logger.py

Comprehensive logging system with file output, rotation, and detailed formatting.
Logs to both console and files in the logs/ directory with proper organization.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler




class WindowsCompatibleHandler(logging.StreamHandler):
    """
    Custom logging handler that replaces Unicode emojis with ASCII symbols
    for Windows console compatibility.
    """
    
    EMOJI_REPLACEMENTS = {
        "[LOG]": "[LOG]",
        "[TARGET]": "[TARGET]", 
        "[TRADE]": "[TRADE]",
        "[SECURE]": "[RISK]",
        "[LINK]": "[WALLET]",
        "[STATS]": "[TX]",
        "⏱[EMOJI]": "[TIMER]",
        "[SEARCH]": "[DEBUG]",
        "ℹ[EMOJI]": "[INFO]",
        "[WARN]": "[WARN]",
        "[ERROR]": "[ERROR]",
        "[START]": "[START]",
        "[EMOJI]": "[STOP]",
        "[TIME]": "[TIME]",
        "[DIR]": "[DIR]",
        "[EMOJI]": "[PYTHON]",
        "[FIX]": "[CONFIG]",
        "[EMOJI]": "[BYE]"
    }
    
    def emit(self, record):
        """Override emit to replace Unicode emojis before outputting to console."""
        try:
            # Get the formatted message
            msg = self.format(record)
            
            # Replace Unicode emojis with ASCII symbols for console output
            for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                msg = msg.replace(emoji, replacement)
            
            # Write the cleaned message
            self.stream.write(msg + self.terminator)
            self.flush()
            
        except UnicodeEncodeError:
            # Fallback: remove all non-ASCII characters
            try:
                msg = self.format(record)
                msg = msg.encode('ascii', 'replace').decode('ascii')
                self.stream.write(msg + self.terminator)
                self.flush()
            except Exception:
                # Last resort: basic message
                self.stream.write(f"[LOGGING ERROR] - {record.levelname} - {record.name}\n")
                self.flush()
        except Exception as e:
            self.handleError(record)


class DEXSniperLogger:
    """
    Professional logging system for DEX Sniper Pro.
    
    Features:
    - File-based logging with rotation
    - Console output with colors
    - Organized log files by component
    - Performance logging
    - Error tracking
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False
    
    @classmethod
    def initialize_logging_system(cls):
        """Initialize the logging system once for the entire application."""
        if cls._initialized:
            return
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organized logging
        (logs_dir / "application").mkdir(exist_ok=True)
        (logs_dir / "trading").mkdir(exist_ok=True)
        (logs_dir / "api").mkdir(exist_ok=True)
        (logs_dir / "database").mkdir(exist_ok=True)
        (logs_dir / "errors").mkdir(exist_ok=True)
        
        cls._initialized = True
        print(f"[OK] Logging system initialized - Logs directory: {logs_dir.absolute()}")
    
    @classmethod
    def get_logger(cls, name: str, component: str = "application") -> logging.Logger:
        """
        Get or create a logger for a specific component.
        
        Args:
            name: Logger name (usually __name__)
            component: Component category (application, trading, api, database)
            
        Returns:
            Configured logger instance
        """
        # Initialize logging system if not done
        cls.initialize_logging_system()
        
        # Return existing logger if already created
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create new logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler with Windows Unicode support
        console_handler = WindowsCompatibleHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Main application log file (all levels)
        logs_dir = Path("logs")
        main_log_file = logs_dir / "application" / "dex_sniper.log"
        main_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(detailed_formatter)
        logger.addHandler(main_handler)
        
        # Component-specific log file
        component_log_file = logs_dir / component / f"{component}.log"
        component_handler = RotatingFileHandler(
            component_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        component_handler.setLevel(logging.DEBUG)
        component_handler.setFormatter(detailed_formatter)
        logger.addHandler(component_handler)
        
        # Error-only log file
        error_log_file = logs_dir / "errors" / "errors.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        # Daily rotating log file for historical tracking
        daily_log_file = logs_dir / "application" / "daily.log"
        daily_handler = TimedRotatingFileHandler(
            daily_log_file,
            when='midnight',
            interval=1,
            backupCount=30
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(detailed_formatter)
        logger.addHandler(daily_handler)
        
        # Store logger
        cls._loggers[name] = logger
        
        # Log logger creation
        logger.info(f"[LOG] Logger initialized for {name} (component: {component})")
        
        return logger


def setup_logger(name: str, component: str = None) -> logging.Logger:
    """
    Setup a logger with comprehensive file and console output.
    
    Args:
        name: Logger name (usually __name__)
        component: Component category for organized logging
        
    Returns:
        Configured logger instance
    """
    # Determine component from module name if not provided
    if component is None:
        if "trading" in name or "order" in name or "transaction" in name:
            component = "trading"
        elif "api" in name or "endpoint" in name or "route" in name:
            component = "api"
        elif "database" in name or "persistence" in name:
            component = "database"
        else:
            component = "application"
    
    return DEXSniperLogger.get_logger(name, component)


class PerformanceLogger:
    """
    Performance logging utility for tracking execution times and metrics.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        import time
        self.start_times[operation] = time.time()
        self.logger.debug(f"⏱[EMOJI] Started timing: {operation}")
    
    def end_timer(self, operation: str, log_level: str = "info"):
        """End timing an operation and log the result."""
        import time
        
        if operation not in self.start_times:
            self.logger.warning(f"[WARN] Timer not found for operation: {operation}")
            return
        
        elapsed = time.time() - self.start_times[operation]
        del self.start_times[operation]
        
        log_method = getattr(self.logger, log_level.lower())
        log_method(f"⏱[EMOJI] {operation} completed in {elapsed:.3f}s")
        
        return elapsed
    
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics."""
        self.logger.info(f"[STATS] Performance Metrics: {metrics}")


class TradingLogger:
    """
    Specialized logger for trading operations.
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.performance = PerformanceLogger(logger)
    
    def log_trade_execution(self, trade_data: Dict[str, Any]):
        """Log trade execution details."""
        self.logger.info(f"[TRADE] Trade Executed: {trade_data}")
    
    def log_trade_opportunity(self, opportunity: Dict[str, Any]):
        """Log trading opportunity detection."""
        self.logger.info(f"[TARGET] Opportunity Detected: {opportunity}")
    
    def log_risk_assessment(self, assessment: Dict[str, Any]):
        """Log risk assessment results."""
        self.logger.info(f"[SECURE] Risk Assessment: {assessment}")
    
    def log_wallet_connection(self, wallet_address: str, status: str):
        """Log wallet connection events."""
        self.logger.info(f"[LINK] Wallet {status}: {wallet_address}")
    
    def log_transaction_status(self, tx_hash: str, status: str):
        """Log transaction status updates."""
        self.logger.info(f"[STATS] Transaction {status}: {tx_hash}")


def get_trading_logger(name: str) -> TradingLogger:
    """Get a specialized trading logger."""
    logger = setup_logger(name, "trading")
    return TradingLogger(logger)


def get_performance_logger(name: str) -> PerformanceLogger:
    """Get a performance logger."""
    logger = setup_logger(name)
    return PerformanceLogger(logger)


def log_application_startup():
    """Log application startup information."""
    logger = setup_logger("app.startup")
    
    logger.info("[START] DEX Sniper Pro - Application Starting")
    logger.info(f"[TIME] Startup Time: {datetime.now().isoformat()}")
    logger.info(f"[DIR] Working Directory: {Path.cwd()}")
    logger.info(f"[EMOJI] Python Version: {sys.version}")
    logger.info(f"[LOG] Logs Directory: {Path('logs').absolute()}")
    
    # Log environment information
    env_vars = ["ENVIRONMENT", "TRADING_ENABLED", "LOG_LEVEL"]
    for var in env_vars:
        value = os.getenv(var, "Not Set")
        logger.info(f"[FIX] {var}: {value}")


def log_application_shutdown():
    """Log application shutdown information."""
    logger = setup_logger("app.shutdown")
    
    logger.info("[EMOJI] DEX Sniper Pro - Application Shutting Down")
    logger.info(f"[TIME] Shutdown Time: {datetime.now().isoformat()}")
    logger.info("[EMOJI] Goodbye!")


# Initialize logging on module import
DEXSniperLogger.initialize_logging_system()


# Legacy compatibility function
def setup_logger_legacy(name: str, level: str = "INFO") -> logging.Logger:
    """
    Legacy function for backwards compatibility.
    Use setup_logger() instead.
    """
    return setup_logger(name)