"""
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
