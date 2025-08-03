#!/usr/bin/env python3
"""
Final Configuration Fix
File: final_config_fix.py

Fixes the remaining configuration and import issues.
"""

import os
import shutil
from datetime import datetime


def backup_existing_config():
    """Backup existing config if it exists."""
    if os.path.exists("app/config.py"):
        backup_name = f"app/config.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2("app/config.py", backup_name)
        print(f"✅ Backed up existing config to {backup_name}")


def create_fixed_config():
    """Create fixed configuration that handles all existing settings."""
    config_content = '''"""
Application Configuration - Fixed Version
File: app/config.py

Enhanced configuration that accepts all existing settings without validation errors.
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with flexible field handling."""
    
    # Core application settings
    app_name: str = "DEX Sniper Pro"
    app_version: str = "3.1.0"
    debug: bool = True
    secret_key: str = "dex-sniper-secret-key-change-in-production"
    environment: str = "development"
    log_level: str = "INFO"
    
    # Database settings
    database_url: str = "sqlite+aiosqlite:///./dex_sniping.db"
    
    # Redis settings
    redis_url: Optional[str] = None
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    cors_origins: list = ["*"]
    
    # Blockchain RPC URLs
    ethereum_rpc_url: Optional[str] = None
    bsc_rpc_url: Optional[str] = None
    polygon_rpc_url: Optional[str] = None
    arbitrum_rpc_url: Optional[str] = None
    optimism_rpc_url: Optional[str] = None
    base_rpc_url: Optional[str] = None
    bnb_rpc_url: Optional[str] = None
    avalanche_rpc_url: Optional[str] = None
    solana_rpc_url: Optional[str] = None
    
    # External API keys
    etherscan_api_key: Optional[str] = None
    bscscan_api_key: Optional[str] = None
    polygonscan_api_key: Optional[str] = None
    moralis_api_key: Optional[str] = None
    alchemy_api_key: Optional[str] = None
    infura_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    dextools_api_key: Optional[str] = None
    helius_api_key: Optional[str] = None
    quicknode_api_key: Optional[str] = None
    
    # Trading parameters
    max_slippage: float = 0.05
    min_liquidity_usd: float = 10000.0
    max_position_size: float = 0.1
    risk_score_threshold: float = 7.0
    min_profit_threshold: float = 0.02
    max_gas_price_gwei: float = 50.0
    bridge_timeout_seconds: int = 300
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
        # Allow extra fields to prevent validation errors
        extra = "allow"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def get_rpc_url(network: str) -> Optional[str]:
    """
    Get RPC URL for a specific network.
    
    Args:
        network: Network name (ethereum, bsc, polygon, etc.)
        
    Returns:
        RPC URL if configured, None otherwise
    """
    rpc_urls = {
        "ethereum": settings.ethereum_rpc_url,
        "bsc": settings.bsc_rpc_url or settings.bnb_rpc_url,
        "polygon": settings.polygon_rpc_url,
        "arbitrum": settings.arbitrum_rpc_url,
        "optimism": settings.optimism_rpc_url,
        "base": settings.base_rpc_url,
        "avalanche": settings.avalanche_rpc_url,
        "solana": settings.solana_rpc_url
    }
    
    return rpc_urls.get(network.lower())


def get_api_key(service: str) -> Optional[str]:
    """
    Get API key for a specific service.
    
    Args:
        service: Service name (etherscan, moralis, etc.)
        
    Returns:
        API key if configured, None otherwise
    """
    api_keys = {
        "etherscan": settings.etherscan_api_key,
        "bscscan": settings.bscscan_api_key,
        "polygonscan": settings.polygonscan_api_key,
        "moralis": settings.moralis_api_key,
        "alchemy": settings.alchemy_api_key,
        "infura": settings.infura_api_key,
        "coingecko": settings.coingecko_api_key,
        "dextools": settings.dextools_api_key,
        "helius": settings.helius_api_key,
        "quicknode": settings.quicknode_api_key
    }
    
    return api_keys.get(service.lower())


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment.lower() == "development"


# Export commonly used settings for easy access
DEBUG = settings.debug
SECRET_KEY = settings.secret_key
DATABASE_URL = settings.database_url
'''
    
    with open("app/config.py", 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ Fixed configuration created")


def add_missing_exceptions():
    """Add missing exception classes."""
    exceptions_content = '''"""
Application Exceptions - Complete Version
File: app/core/exceptions.py

All custom exception classes for the DEX Sniping Platform.
"""

from typing import Dict, Any, Optional


class DexSnipingException(Exception):
    """Base exception for all DEX Sniping Platform errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "error_type": self.__class__.__name__,
            "details": self.details
        }


# Validation Exceptions
class ValidationError(DexSnipingException):
    """Raised when validation fails."""
    pass


# Database Exceptions
class DatabaseError(DexSnipingException):
    """Raised when database operations fail."""
    pass


# Blockchain Exceptions
class BlockchainError(DexSnipingException):
    """Raised when blockchain operations fail."""
    pass


# Trading Exceptions
class TradingError(DexSnipingException):
    """Raised when trading operations fail."""
    pass


class InsufficientFundsError(TradingError):
    """Raised when insufficient funds for trading."""
    pass


class InvalidOrderError(TradingError):
    """Raised when order parameters are invalid."""
    pass


class OrderExecutionError(TradingError):
    """Raised when order execution fails."""
    pass


# Portfolio Exceptions
class PortfolioError(DexSnipingException):
    """Raised when portfolio operations fail."""
    pass


class PositionError(PortfolioError):
    """Raised when position operations fail."""
    pass


class RiskManagementError(PortfolioError):
    """Raised when risk management operations fail."""
    pass


# Configuration Exceptions
class ConfigurationError(DexSnipingException):
    """Raised when configuration is invalid."""
    pass


# AI and Analysis Exceptions
class AIAnalysisError(DexSnipingException):
    """Raised when AI analysis fails."""
    pass


class ContractAnalysisError(AIAnalysisError):
    """Raised when smart contract analysis fails."""
    pass


class HoneypotDetectionError(AIAnalysisError):
    """Raised when honeypot detection fails."""
    pass


class RiskAssessmentError(AIAnalysisError):
    """Raised when risk assessment fails."""
    pass


# Network and Connectivity Exceptions
class NetworkError(DexSnipingException):
    """Raised when network operations fail."""
    pass


class ConnectionPoolError(NetworkError):
    """Raised when connection pool operations fail."""
    pass


class WebSocketError(NetworkError):
    """Raised when WebSocket operations fail."""
    pass


# DEX-specific Exceptions
class DEXError(DexSnipingException):
    """Raised when DEX operations fail."""
    pass


class LiquidityError(DEXError):
    """Raised when liquidity operations fail."""
    pass


class PriceImpactError(DEXError):
    """Raised when price impact is too high."""
    pass


class SlippageError(DEXError):
    """Raised when slippage exceeds tolerance."""
    pass


# Token and Contract Exceptions
class TokenError(DexSnipingException):
    """Raised when token operations fail."""
    pass


class ContractError(TokenError):
    """Raised when smart contract operations fail."""
    pass


class TokenDiscoveryError(TokenError):
    """Raised when token discovery fails."""
    pass


# Market Data Exceptions
class MarketDataError(DexSnipingException):
    """Raised when market data operations fail."""
    pass


class PriceDataError(MarketDataError):
    """Raised when price data operations fail."""
    pass


class VolumeDataError(MarketDataError):
    """Raised when volume data operations fail."""
    pass


# Authentication and Authorization Exceptions
class AuthenticationError(DexSnipingException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(DexSnipingException):
    """Raised when authorization fails."""
    pass


# Rate Limiting Exceptions
class RateLimitError(DexSnipingException):
    """Raised when rate limits are exceeded."""
    pass


class APIQuotaExceededError(RateLimitError):
    """Raised when API quota is exceeded."""
    pass


# Timeout Exceptions
class TimeoutError(DexSnipingException):
    """Raised when operations timeout."""
    pass


class BlockchainTimeoutError(TimeoutError):
    """Raised when blockchain operations timeout."""
    pass


class APITimeoutError(TimeoutError):
    """Raised when API calls timeout."""
    pass


# Data Processing Exceptions
class DataProcessingError(DexSnipingException):
    """Raised when data processing fails."""
    pass


class DataValidationError(DataProcessingError):
    """Raised when data validation fails."""
    pass


class DataTransformationError(DataProcessingError):
    """Raised when data transformation fails."""
    pass


# Cache Exceptions
class CacheError(DexSnipingException):
    """Raised when cache operations fail."""
    pass


class CacheTimeoutError(CacheError):
    """Raised when cache operations timeout."""
    pass


class CacheInvalidationError(CacheError):
    """Raised when cache invalidation fails."""
    pass


# Circuit Breaker Exceptions
class CircuitBreakerError(DexSnipingException):
    """Raised when circuit breaker operations fail."""
    pass


class CircuitOpenError(CircuitBreakerError):
    """Raised when circuit breaker is open."""
    pass


# Monitoring and Alerting Exceptions
class MonitoringError(DexSnipingException):
    """Raised when monitoring operations fail."""
    pass


class AlertingError(MonitoringError):
    """Raised when alerting operations fail."""
    pass


# Utility function to get HTTP status code for exceptions
EXCEPTION_STATUS_CODES = {
    ValidationError: 400,
    AuthenticationError: 401,
    AuthorizationError: 403,
    RateLimitError: 429,
    TimeoutError: 408,
    DatabaseError: 500,
    BlockchainError: 502,
    NetworkError: 503,
    ConfigurationError: 500,
    AIAnalysisError: 500,
    DEXError: 502,
    TokenError: 500,
    MarketDataError: 503,
    DataProcessingError: 500,
    CacheError: 500,
    CircuitBreakerError: 503,
    MonitoringError: 500,
}


def get_http_status_code(exception: Exception) -> int:
    """
    Get appropriate HTTP status code for an exception.
    
    Args:
        exception: Exception instance
        
    Returns:
        HTTP status code
    """
    for exception_type, status_code in EXCEPTION_STATUS_CODES.items():
        if isinstance(exception, exception_type):
            return status_code
    return 500  # Default to internal server error


def format_exception_response(exception: Exception) -> dict:
    """
    Format exception for API response.
    
    Args:
        exception: Exception instance
        
    Returns:
        Formatted exception dictionary
    """
    if isinstance(exception, DexSnipingException):
        return exception.to_dict()
    else:
        return {
            "error": str(exception),
            "error_code": "INTERNAL_ERROR",
            "error_type": type(exception).__name__,
            "details": {}
        }
'''
    
    with open("app/core/exceptions.py", 'w', encoding='utf-8') as f:
        f.write(exceptions_content)
    print("✅ Complete exceptions module created")


def main():
    """Main execution function."""
    print("🔧 Final Configuration Fix")
    print("=" * 40)
    print("Fixing remaining configuration and import issues...")
    print()
    
    try:
        # Backup existing config
        backup_existing_config()
        
        # Create fixed config
        create_fixed_config()
        
        # Add missing exceptions
        add_missing_exceptions()
        
        print()
        print("🎉 Final fixes completed successfully!")
        print()
        print("📋 What was fixed:")
        print("✅ Configuration validation errors (extra fields now allowed)")
        print("✅ Missing PortfolioError and other exception classes")
        print("✅ Enhanced configuration with all trading parameters")
        print()
        print("🚀 The application should now start without any errors!")
        print()
        print("📋 Next steps:")
        print("1. Start the application: uvicorn app.main:app --reload --port 8001")
        print("2. Validate again: python final_validation.py")
        print("3. Test runtime: python test_application.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Final fix failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)