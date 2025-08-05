"""
Configuration Management System - Phase 4B Implementation
File: app/core/config/settings_manager.py
Class: SettingsManager
Methods: load_configuration, validate_settings, get_network_config, update_trading_config

Professional configuration management for trading bot with environment-based settings,
validation, and dynamic configuration updates for different deployment environments.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union, Type
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import yaml

try:
    from pydantic import BaseSettings, Field, validator
    from pydantic.env_settings import SettingsSourceCallable
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Mock BaseSettings for development
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(default=None, **kwargs):
        return default

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class Environment(Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class NetworkEnvironment(Enum):
    """Network environment types."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    LOCAL = "local"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_type: str = "sqlite"
    db_path: str = "data/trading_bot.db"
    connection_pool_size: int = 5
    connection_timeout: int = 30
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    cleanup_days: int = 30
    
    # PostgreSQL specific
    pg_host: Optional[str] = None
    pg_port: int = 5432
    pg_database: Optional[str] = None
    pg_username: Optional[str] = None
    pg_password: Optional[str] = None


@dataclass
class NetworkConfig:
    """Blockchain network configuration."""
    network_name: str
    chain_id: int
    rpc_urls: List[str]
    websocket_urls: List[str] = field(default_factory=list)
    explorer_url: str = ""
    native_currency: str = "ETH"
    gas_price_multiplier: float = 1.2
    max_gas_price_gwei: int = 100
    confirmation_blocks: int = 3
    block_time_seconds: float = 12.0
    is_testnet: bool = False


@dataclass
class TradingConfig:
    """Trading engine configuration."""
    enabled: bool = True
    trading_mode: str = "semi_automated"
    max_position_size_eth: float = 1.0
    max_daily_loss_usd: float = 100.0
    default_slippage_percent: float = 1.0
    auto_approve_tokens: bool = True
    max_gas_price_gwei: int = 50
    minimum_liquidity_usd: float = 10000.0
    profit_threshold_percent: float = 5.0
    stop_loss_percent: float = 10.0
    
    # Strategy settings
    enabled_strategies: List[str] = field(default_factory=lambda: ["arbitrage", "momentum"])
    strategy_weights: Dict[str, float] = field(default_factory=lambda: {"arbitrage": 0.6, "momentum": 0.4})
    risk_tolerance: str = "medium"  # low, medium, high
    
    # DEX preferences
    preferred_dexes: List[str] = field(default_factory=lambda: ["uniswap_v2", "sushiswap"])
    dex_weights: Dict[str, float] = field(default_factory=lambda: {"uniswap_v2": 0.7, "sushiswap": 0.3})


@dataclass
class SecurityConfig:
    """Security and API configuration."""
    api_rate_limit: int = 100  # requests per minute
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    enable_api_docs: bool = True
    require_wallet_signature: bool = True
    session_timeout_minutes: int = 60
    max_concurrent_trades: int = 5
    
    # Private keys and secrets (loaded from environment)
    wallet_private_key: Optional[str] = None
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    
    # External API keys
    infura_api_key: Optional[str] = None
    alchemy_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration."""
    log_level: str = "INFO"
    log_file_enabled: bool = True
    log_file_path: str = "logs/trading_bot.log"
    log_retention_days: int = 30
    metrics_enabled: bool = True
    health_check_interval_seconds: int = 30
    alert_telegram_enabled: bool = False
    alert_email_enabled: bool = False
    performance_tracking: bool = True


class ApplicationSettings:
    """
    Professional application settings management.
    
    Handles configuration loading from multiple sources:
    - Environment variables
    - Configuration files (JSON/YAML)
    - Command line arguments
    - Default values
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        """Initialize settings manager."""
        self.environment = environment
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration components
        self.database: DatabaseConfig = DatabaseConfig()
        self.trading: TradingConfig = TradingConfig()
        self.security: SecurityConfig = SecurityConfig()
        self.monitoring: MonitoringConfig = MonitoringConfig()
        self.networks: Dict[str, NetworkConfig] = {}
        
        # Load configuration
        self._load_default_networks()
        self._load_from_environment()
        self._load_from_files()
        
        logger.info(f"⚙️ Settings loaded for {environment.value} environment")
    
    def _load_default_networks(self):
        """Load default network configurations."""
        self.networks = {
            "ethereum": NetworkConfig(
                network_name="Ethereum Mainnet",
                chain_id=1,
                rpc_urls=[
                    "https://eth.llamarpc.com",
                    "https://rpc.ankr.com/eth",
                    "https://ethereum.publicnode.com"
                ],
                websocket_urls=["wss://eth.llamarpc.com"],
                explorer_url="https://etherscan.io",
                native_currency="ETH",
                max_gas_price_gwei=100,
                confirmation_blocks=3
            ),
            "polygon": NetworkConfig(
                network_name="Polygon Mainnet",
                chain_id=137,
                rpc_urls=[
                    "https://polygon.llamarpc.com",
                    "https://rpc.ankr.com/polygon"
                ],
                explorer_url="https://polygonscan.com",
                native_currency="MATIC",
                max_gas_price_gwei=1000,
                confirmation_blocks=10,
                block_time_seconds=2.0
            ),
            "bsc": NetworkConfig(
                network_name="BSC Mainnet",
                chain_id=56,
                rpc_urls=[
                    "https://bsc.llamarpc.com",
                    "https://rpc.ankr.com/bsc"
                ],
                explorer_url="https://bscscan.com",
                native_currency="BNB",
                max_gas_price_gwei=20,
                confirmation_blocks=3,
                block_time_seconds=3.0
            )
        }
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Database configuration
        if os.getenv("DATABASE_URL"):
            self.database.db_type = "postgresql"
            # Parse DATABASE_URL for PostgreSQL settings
        
        self.database.db_path = os.getenv("DB_PATH", self.database.db_path)
        
        # Trading configuration
        self.trading.enabled = os.getenv("TRADING_ENABLED", "true").lower() == "true"
        self.trading.trading_mode = os.getenv("TRADING_MODE", self.trading.trading_mode)
        
        if os.getenv("MAX_POSITION_SIZE_ETH"):
            self.trading.max_position_size_eth = float(os.getenv("MAX_POSITION_SIZE_ETH"))
        
        if os.getenv("MAX_DAILY_LOSS_USD"):
            self.trading.max_daily_loss_usd = float(os.getenv("MAX_DAILY_LOSS_USD"))
        
        if os.getenv("DEFAULT_SLIPPAGE_PERCENT"):
            self.trading.default_slippage_percent = float(os.getenv("DEFAULT_SLIPPAGE_PERCENT"))
        
        # Security configuration
        self.security.wallet_private_key = os.getenv("WALLET_PRIVATE_KEY")
        self.security.encryption_key = os.getenv("ENCRYPTION_KEY")
        self.security.jwt_secret = os.getenv("JWT_SECRET")
        self.security.infura_api_key = os.getenv("INFURA_API_KEY")
        self.security.alchemy_api_key = os.getenv("ALCHEMY_API_KEY")
        self.security.coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.security.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Monitoring configuration
        self.monitoring.log_level = os.getenv("LOG_LEVEL", self.monitoring.log_level)
        self.monitoring.log_file_path = os.getenv("LOG_FILE_PATH", self.monitoring.log_file_path)
        
        if os.getenv("METRICS_ENABLED"):
            self.monitoring.metrics_enabled = os.getenv("METRICS_ENABLED").lower() == "true"
        
        # Network-specific overrides
        for network_name in self.networks.keys():
            env_key = f"{network_name.upper()}_RPC_URL"
            if os.getenv(env_key):
                # Replace first RPC URL with environment override
                self.networks[network_name].rpc_urls[0] = os.getenv(env_key)
        
        logger.info("✅ Environment variables loaded")
    
    def _load_from_files(self):
        """Load configuration from files."""
        # Load environment-specific config file
        config_file = self.config_dir / f"{self.environment.value}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                
                self._apply_file_config(file_config)
                logger.info(f"✅ Configuration loaded from {config_file}")
                
            except Exception as e:
                logger.error(f"❌ Error loading config file {config_file}: {e}")
        
        # Load user-specific overrides
        user_config = self.config_dir / "user_config.json"
        if user_config.exists():
            try:
                with open(user_config, 'r') as f:
                    user_overrides = json.load(f)
                
                self._apply_file_config(user_overrides)
                logger.info("✅ User configuration overrides applied")
                
            except Exception as e:
                logger.error(f"❌ Error loading user config: {e}")
    
    def _apply_file_config(self, config: Dict[str, Any]):
        """Apply configuration from file."""
        # Apply database config
        if "database" in config:
            db_config = config["database"]
            for key, value in db_config.items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        # Apply trading config
        if "trading" in config:
            trading_config = config["trading"]
            for key, value in trading_config.items():
                if hasattr(self.trading, key):
                    setattr(self.trading, key, value)
        
        # Apply security config (excluding sensitive data)
        if "security" in config:
            security_config = config["security"]
            sensitive_keys = {"wallet_private_key", "encryption_key", "jwt_secret"}
            for key, value in security_config.items():
                if hasattr(self.security, key) and key not in sensitive_keys:
                    setattr(self.security, key, value)
        
        # Apply monitoring config
        if "monitoring" in config:
            monitoring_config = config["monitoring"]
            for key, value in monitoring_config.items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
        
        # Apply network configs
        if "networks" in config:
            for network_name, network_config in config["networks"].items():
                if network_name in self.networks:
                    # Update existing network config
                    for key, value in network_config.items():
                        if hasattr(self.networks[network_name], key):
                            setattr(self.networks[network_name], key, value)
    
    def validate_configuration(self) -> List[str]:
        """
        Validate all configuration settings.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate trading configuration
        if self.trading.max_position_size_eth <= 0:
            errors.append("Max position size must be positive")
        
        if self.trading.max_daily_loss_usd <= 0:
            errors.append("Max daily loss must be positive")
        
        if not (0 <= self.trading.default_slippage_percent <= 50):
            errors.append("Default slippage must be between 0% and 50%")
        
        if not self.trading.enabled_strategies:
            errors.append("At least one trading strategy must be enabled")
        
        # Validate security configuration
        if self.environment == Environment.PRODUCTION:
            if not self.security.wallet_private_key:
                errors.append("Wallet private key required for production")
            
            if not self.security.encryption_key:
                errors.append("Encryption key required for production")
            
            if self.security.enable_api_docs:
                errors.append("API docs should be disabled in production")
        
        # Validate network configurations
        for network_name, network_config in self.networks.items():
            if not network_config.rpc_urls:
                errors.append(f"No RPC URLs configured for {network_name}")
            
            if network_config.chain_id <= 0:
                errors.append(f"Invalid chain ID for {network_name}")
        
        # Validate database configuration
        if self.database.db_type == "postgresql":
            if not all([self.database.pg_host, self.database.pg_database]):
                errors.append("PostgreSQL host and database name required")
        
        if errors:
            logger.warning(f"⚠️ Configuration validation found {len(errors)} issues")
            for error in errors:
                logger.warning(f"   - {error}")
        else:
            logger.info("✅ Configuration validation passed")
        
        return errors
    
    def get_network_config(self, network_name: str) -> Optional[NetworkConfig]:
        """
        Get configuration for specific network.
        
        Args:
            network_name: Name of the network
            
        Returns:
            NetworkConfig or None if not found
        """
        return self.networks.get(network_name.lower())
    
    def get_active_networks(self) -> List[str]:
        """
        Get list of active/enabled networks.
        
        Returns:
            List of network names
        """
        # For now, return all configured networks
        # In the future, this could filter based on enabled status
        return list(self.networks.keys())
    
    def update_trading_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update trading configuration at runtime.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            bool: True if update successful
        """
        try:
            valid_keys = {attr for attr in dir(self.trading) if not attr.startswith('_')}
            
            for key, value in updates.items():
                if key in valid_keys:
                    setattr(self.trading, key, value)
                    logger.info(f"✅ Updated trading.{key} = {value}")
                else:
                    logger.warning(f"⚠️ Invalid trading config key: {key}")
                    return False
            
            # Validate updated configuration
            errors = self.validate_configuration()
            if errors:
                logger.error("❌ Updated configuration is invalid")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating trading configuration: {e}")
            return False
    
    def save_configuration(self, include_sensitive: bool = False) -> bool:
        """
        Save current configuration to file.
        
        Args:
            include_sensitive: Whether to include sensitive data
            
        Returns:
            bool: True if save successful
        """
        try:
            config_data = {
                "database": asdict(self.database),
                "trading": asdict(self.trading),
                "monitoring": asdict(self.monitoring),
                "networks": {name: asdict(config) for name, config in self.networks.items()}
            }
            
            # Handle security config
            security_dict = asdict(self.security)
            if not include_sensitive:
                # Remove sensitive keys
                sensitive_keys = {
                    "wallet_private_key", "encryption_key", "jwt_secret",
                    "infura_api_key", "alchemy_api_key", "coingecko_api_key",
                    "telegram_bot_token"
                }
                security_dict = {k: v for k, v in security_dict.items() if k not in sensitive_keys}
            
            config_data["security"] = security_dict
            
            # Save to environment-specific file
            config_file = self.config_dir / f"{self.environment.value}.json"
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"✅ Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving configuration: {e}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for display/debugging.
        
        Returns:
            Dict containing configuration summary
        """
        return {
            "environment": self.environment.value,
            "trading_enabled": self.trading.enabled,
            "trading_mode": self.trading.trading_mode,
            "max_position_size_eth": self.trading.max_position_size_eth,
            "enabled_strategies": self.trading.enabled_strategies,
            "active_networks": list(self.networks.keys()),
            "database_type": self.database.db_type,
            "log_level": self.monitoring.log_level,
            "api_docs_enabled": self.security.enable_api_docs,
            "metrics_enabled": self.monitoring.metrics_enabled,
            "has_wallet_key": bool(self.security.wallet_private_key),
            "has_api_keys": bool(self.security.infura_api_key or self.security.alchemy_api_key),
            "config_files_loaded": (self.config_dir / f"{self.environment.value}.json").exists()
        }
    
    def create_sample_config_files(self):
        """Create sample configuration files for different environments."""
        try:
            # Development config
            dev_config = {
                "database": {
                    "db_path": "data/dev_trading_bot.db",
                    "backup_enabled": False
                },
                "trading": {
                    "enabled": True,
                    "trading_mode": "simulation",
                    "max_position_size_eth": 0.1,
                    "max_daily_loss_usd": 10.0
                },
                "security": {
                    "enable_api_docs": True,
                    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
                },
                "monitoring": {
                    "log_level": "DEBUG",
                    "metrics_enabled": True
                }
            }
            
            dev_file = self.config_dir / "development.json"
            with open(dev_file, 'w') as f:
                json.dump(dev_config, f, indent=2)
            
            # Production config template
            prod_config = {
                "database": {
                    "db_type": "postgresql",
                    "backup_enabled": True,
                    "backup_interval_hours": 12
                },
                "trading": {
                    "enabled": True,
                    "trading_mode": "semi_automated",
                    "max_position_size_eth": 1.0,
                    "max_daily_loss_usd": 100.0
                },
                "security": {
                    "enable_api_docs": False,
                    "cors_origins": ["https://yourdomain.com"],
                    "api_rate_limit": 60
                },
                "monitoring": {
                    "log_level": "INFO",
                    "metrics_enabled": True,
                    "alert_telegram_enabled": True
                }
            }
            
            prod_file = self.config_dir / "production.json"
            with open(prod_file, 'w') as f:
                json.dump(prod_config, f, indent=2)
            
            # Create .env template
            env_template = """# DEX Sniper Pro Environment Configuration
# Copy this to .env and fill in your values

# Environment
ENVIRONMENT=development

# Trading Configuration
TRADING_ENABLED=true
TRADING_MODE=simulation
MAX_POSITION_SIZE_ETH=0.1
MAX_DAILY_LOSS_USD=10.0
DEFAULT_SLIPPAGE_PERCENT=1.0

# Security (NEVER commit real keys to version control)
WALLET_PRIVATE_KEY=your_wallet_private_key_here
ENCRYPTION_KEY=your_encryption_key_here
JWT_SECRET=your_jwt_secret_here

# API Keys
INFURA_API_KEY=your_infura_key_here
ALCHEMY_API_KEY=your_alchemy_key_here
COINGECKO_API_KEY=your_coingecko_key_here

# Database
DB_PATH=data/trading_bot.db
# DATABASE_URL=postgresql://user:pass@localhost/trading_bot

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true

# Network Overrides (optional)
# ETHEREUM_RPC_URL=https://your-custom-rpc-url
# POLYGON_RPC_URL=https://your-polygon-rpc-url
"""
            
            env_file = self.config_dir.parent / ".env.template"
            with open(env_file, 'w') as f:
                f.write(env_template)
            
            logger.info("✅ Sample configuration files created")
            logger.info(f"   - {dev_file}")
            logger.info(f"   - {prod_file}")
            logger.info(f"   - {env_file}")
            
        except Exception as e:
            logger.error(f"❌ Error creating sample config files: {e}")


# Global settings instance
_settings_instance: Optional[ApplicationSettings] = None


def get_settings(environment: Optional[Environment] = None) -> ApplicationSettings:
    """
    Get global settings instance.
    
    Args:
        environment: Environment to load (uses current if None)
        
    Returns:
        ApplicationSettings instance
    """
    global _settings_instance
    
    if _settings_instance is None or environment:
        # Determine environment
        if environment is None:
            env_name = os.getenv("ENVIRONMENT", "development").lower()
            try:
                environment = Environment(env_name)
            except ValueError:
                logger.warning(f"⚠️ Invalid environment '{env_name}', using development")
                environment = Environment.DEVELOPMENT
        
        _settings_instance = ApplicationSettings(environment)
    
    return _settings_instance


def initialize_configuration(environment: Optional[Environment] = None) -> ApplicationSettings:
    """
    Initialize configuration system.
    
    Args:
        environment: Target environment
        
    Returns:
        ApplicationSettings instance
    """
    try:
        settings = get_settings(environment)
        
        # Validate configuration
        errors = settings.validate_configuration()
        if errors and settings.environment == Environment.PRODUCTION:
            raise ValueError(f"Configuration validation failed: {errors}")
        
        # Create sample config files if they don't exist
        if not (settings.config_dir / f"{settings.environment.value}.json").exists():
            settings.create_sample_config_files()
        
        logger.info(f"✅ Configuration system initialized for {settings.environment.value}")
        return settings
        
    except Exception as e:
        logger.error(f"❌ Configuration initialization failed: {e}")
        raise


# Export commonly used functions and classes
__all__ = [
    "ApplicationSettings",
    "Environment",
    "NetworkEnvironment", 
    "DatabaseConfig",
    "NetworkConfig",
    "TradingConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "get_settings",
    "initialize_configuration"
]