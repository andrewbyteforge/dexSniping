"""
Production-ready configuration file that matches your comprehensive .env setup.
File: app/config.py

FIXED VERSION - Removed circular import issue
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from decimal import Decimal


class Settings(BaseSettings):
    """Main application settings class with all production configuration."""
    
    # Core Application Settings
    database_url: str = "sqlite+aiosqlite:///./dex_sniping.db"
    secret_key: str = "your_secret_key_here"
    debug: bool = True
    log_level: str = "INFO"
    environment: str = "development"
    api_rate_limit: int = 1000
    websocket_rate_limit: int = 100
    
    # External API Keys
    moralis_api_key: str = "your_moralis_api_key"
    alchemy_api_key: str = "your_alchemy_api_key"
    infura_api_key: str = "your_infura_api_key"
    coingecko_api_key: str = "your_coingecko_api_key"
    dextools_api_key: str = "your_dextools_api_key"
    helius_api_key: str = "your_helius_api_key"
    quicknode_api_key: str = "your_quicknode_api_key"
    
    # Infrastructure Services
    redis_url: str = "redis://localhost:6379"
    
    # Blockchain RPC URLs
    ethereum_rpc_url: str = "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
    arbitrum_rpc_url: str = "https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY"
    optimism_rpc_url: str = "https://opt-mainnet.g.alchemy.com/v2/YOUR_KEY"
    base_rpc_url: str = "https://base-mainnet.g.alchemy.com/v2/YOUR_KEY"
    polygon_rpc_url: str = "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"
    bnb_rpc_url: str = "https://bsc-dataseed.binance.org/"
    avalanche_rpc_url: str = "https://api.avax.network/ext/bc/C/rpc"
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    
    # Trading Parameters
    max_slippage: str = "0.05"
    min_liquidity_usd: str = "10000"
    max_position_size: str = "0.1"
    risk_score_threshold: str = "7.0"
    min_profit_threshold: str = "0.02"
    max_gas_price_gwei: str = "50"
    bridge_timeout_seconds: str = "300"
    
    # Configuration
    class Config:
        env_file = ".env"
        extra = "allow"
    
    @property
    def ENVIRONMENT(self) -> str:
        """Get environment name for compatibility."""
        return self.environment
    
    @property
    def max_slippage_decimal(self) -> Decimal:
        return Decimal(self.max_slippage)
    
    @property
    def min_liquidity_usd_int(self) -> int:
        return int(self.min_liquidity_usd)
    
    @property
    def max_position_size_decimal(self) -> Decimal:
        return Decimal(self.max_position_size)
    
    @property
    def risk_score_threshold_float(self) -> float:
        return float(self.risk_score_threshold)
    
    @property
    def min_profit_threshold_decimal(self) -> Decimal:
        return Decimal(self.min_profit_threshold)
    
    @property
    def max_gas_price_gwei_int(self) -> int:
        return int(self.max_gas_price_gwei)
    
    @property
    def bridge_timeout_seconds_int(self) -> int:
        return int(self.bridge_timeout_seconds)


class NetworkConfig:
    """Network configuration constants."""
    
    @classmethod
    def get_supported_networks(cls, settings: Settings) -> dict:
        return {
            "ethereum": {
                "chain_id": 1,
                "type": "evm",
                "name": "Ethereum",
                "symbol": "ETH",
                "rpc_urls": [settings.ethereum_rpc_url],
                "dex_protocols": ["uniswap_v3", "uniswap_v2", "sushiswap"],
                "block_time": 12,
                "gas_token": "ETH",
                "explorer": "https://etherscan.io"
            },
            "polygon": {
                "chain_id": 137,
                "type": "evm", 
                "name": "Polygon",
                "symbol": "MATIC",
                "rpc_urls": [settings.polygon_rpc_url],
                "dex_protocols": ["uniswap_v3", "quickswap"],
                "block_time": 2,
                "gas_token": "MATIC",
                "explorer": "https://polygonscan.com"
            }
        }
    
    @classmethod
    def get_all_networks(cls) -> List[str]:
        default_settings = Settings()
        networks = cls.get_supported_networks(default_settings)
        return list(networks.keys())
    
    @classmethod
    def get_network_config(cls, network_name: str, settings: Optional[Settings] = None) -> dict:
        if settings is None:
            settings = Settings()
        networks = cls.get_supported_networks(settings)
        if network_name not in networks:
            raise ValueError(f"Unsupported network: {network_name}")
        return networks[network_name]


# Global settings instance
settings = Settings()


def get_network_config(network_name: str) -> Optional[dict]:
    """Get network configuration by name."""
    return NetworkConfig.get_network_config(network_name)
