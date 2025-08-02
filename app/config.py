"""
File: app/config.py

Application configuration management with Pydantic settings.
Handles environment variables, API keys, and network configurations.
"""

from typing import Dict, List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """
    Main application settings class.
    
    Manages all configuration parameters including database connections,
    API keys, network configurations, and trading parameters.
    """
    
    # Database Configuration
    database_url: str
    
    # API Keys
    moralis_api_key: Optional[str] = None
    alchemy_api_key: Optional[str] = None
    infura_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    dextools_api_key: Optional[str] = None
    helius_api_key: Optional[str] = None
    quicknode_api_key: Optional[str] = None
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Application Settings
    secret_key: str
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    
    # Network RPC URLs
    ethereum_rpc_url: Optional[str] = None
    arbitrum_rpc_url: Optional[str] = None
    optimism_rpc_url: Optional[str] = None
    base_rpc_url: Optional[str] = None
    polygon_rpc_url: Optional[str] = None
    bnb_rpc_url: str = "https://bsc-dataseed.binance.org/"
    avalanche_rpc_url: str = "https://api.avax.network/ext/bc/C/rpc"
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    
    # Trading Configuration
    max_slippage: float = 0.05
    min_liquidity_usd: float = 10000.0
    max_position_size: float = 0.1
    risk_score_threshold: float = 7.0
    
    # Arbitrage Configuration
    min_profit_threshold: float = 0.02
    max_gas_price_gwei: int = 50
    bridge_timeout_seconds: int = 300
    
    # WebSocket Configuration
    websocket_heartbeat_interval: int = 30
    websocket_max_connections: int = 100
    
    # Rate Limiting
    api_rate_limit: int = 1000  # requests per hour
    websocket_rate_limit: int = 100  # messages per minute
    
    @validator("max_slippage")
    def validate_max_slippage(cls, v):
        """Validate slippage is between 0 and 1."""
        if not 0 < v < 1:
            raise ValueError("Max slippage must be between 0 and 1")
        return v
    
    @validator("risk_score_threshold")
    def validate_risk_score(cls, v):
        """Validate risk score is between 0 and 10."""
        if not 0 <= v <= 10:
            raise ValueError("Risk score threshold must be between 0 and 10")
        return v
    
    @validator("min_profit_threshold")
    def validate_profit_threshold(cls, v):
        """Validate profit threshold is positive."""
        if v <= 0:
            raise ValueError("Minimum profit threshold must be positive")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


class NetworkConfig:
    """
    Network configuration constants and mappings.
    
    Contains all supported blockchain networks with their
    configurations, DEX protocols, and connection parameters.
    """
    
    SUPPORTED_NETWORKS = {
        # Ethereum Ecosystem
        "ethereum": {
            "chain_id": 1,
            "type": "evm",
            "name": "Ethereum",
            "symbol": "ETH",
            "rpc_urls": [
                "https://eth-mainnet.g.alchemy.com/v2/",
                "https://mainnet.infura.io/v3/",
                "https://ethereum.publicnode.com"
            ],
            "dex_protocols": ["uniswap_v3", "uniswap_v2", "sushiswap", "1inch"],
            "block_time": 12,
            "gas_token": "ETH",
            "explorer": "https://etherscan.io",
            "multicall_address": "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
        },
        "arbitrum": {
            "chain_id": 42161,
            "type": "evm",
            "name": "Arbitrum One",
            "symbol": "ETH",
            "rpc_urls": [
                "https://arb-mainnet.g.alchemy.com/v2/",
                "https://arbitrum-one.publicnode.com"
            ],
            "dex_protocols": ["uniswap_v3", "sushiswap", "camelot", "gmx"],
            "block_time": 0.25,
            "gas_token": "ETH",
            "explorer": "https://arbiscan.io",
            "multicall_address": "0x842eC2c7D803033Edf55E478F461FC547Bc54EB2"
        },
        "optimism": {
            "chain_id": 10,
            "type": "evm",
            "name": "Optimism",
            "symbol": "ETH",
            "rpc_urls": [
                "https://opt-mainnet.g.alchemy.com/v2/",
                "https://optimism.publicnode.com"
            ],
            "dex_protocols": ["uniswap_v3", "velodrome", "beethoven_x"],
            "block_time": 2,
            "gas_token": "ETH",
            "explorer": "https://optimistic.etherscan.io",
            "multicall_address": "0x2DC0E2aa608532Da689e89e237dF582B783E552C"
        },
        "base": {
            "chain_id": 8453,
            "type": "evm",
            "name": "Base",
            "symbol": "ETH",
            "rpc_urls": [
                "https://base-mainnet.g.alchemy.com/v2/",
                "https://base.publicnode.com"
            ],
            "dex_protocols": ["uniswap_v3", "aerodrome", "baseswap"],
            "block_time": 2,
            "gas_token": "ETH",
            "explorer": "https://basescan.org",
            "multicall_address": "0xcA11bde05977b3631167028862bE2a173976CA11"
        },
        "polygon": {
            "chain_id": 137,
            "type": "evm",
            "name": "Polygon",
            "symbol": "MATIC",
            "rpc_urls": [
                "https://polygon-mainnet.g.alchemy.com/v2/",
                "https://polygon-bor.publicnode.com"
            ],
            "dex_protocols": ["uniswap_v3", "quickswap", "sushiswap", "1inch"],
            "block_time": 2,
            "gas_token": "MATIC",
            "explorer": "https://polygonscan.com",
            "multicall_address": "0xcA11bde05977b3631167028862bE2a173976CA11"
        },
        "bnb_chain": {
            "chain_id": 56,
            "type": "evm",
            "name": "BNB Chain",
            "symbol": "BNB",
            "rpc_urls": [
                "https://bsc-dataseed.binance.org/",
                "https://bsc.publicnode.com"
            ],
            "dex_protocols": ["pancakeswap", "biswap", "1inch"],
            "block_time": 3,
            "gas_token": "BNB",
            "explorer": "https://bscscan.com",
            "multicall_address": "0xcA11bde05977b3631167028862bE2a173976CA11"
        },
        "avalanche": {
            "chain_id": 43114,
            "type": "evm",
            "name": "Avalanche",
            "symbol": "AVAX",
            "rpc_urls": [
                "https://api.avax.network/ext/bc/C/rpc",
                "https://avalanche.publicnode.com"
            ],
            "dex_protocols": ["traderjoe", "pangolin", "sushiswap"],
            "block_time": 2,
            "gas_token": "AVAX",
            "explorer": "https://snowtrace.io",
            "multicall_address": "0xcA11bde05977b3631167028862bE2a173976CA11"
        },
        
        # Non-EVM Chains
        "solana": {
            "type": "solana",
            "name": "Solana",
            "symbol": "SOL",
            "rpc_urls": [
                "https://api.mainnet-beta.solana.com",
                "https://solana-api.projectserum.com"
            ],
            "dex_protocols": ["raydium", "orca", "jupiter", "serum"],
            "block_time": 0.4,
            "gas_token": "SOL",
            "explorer": "https://solscan.io",
            "program_ids": {
                "raydium": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
                "orca": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                "jupiter": "JUP2jxvXaqu7NQY1GmNF4m1vodw12LVXYxbFL2uJvfo"
            }
        }
    }
    
    @classmethod
    def get_network_config(cls, network_name: str) -> Dict:
        """
        Get configuration for a specific network.
        
        Args:
            network_name: Name of the network
            
        Returns:
            Network configuration dictionary
            
        Raises:
            ValueError: If network is not supported
        """
        if network_name not in cls.SUPPORTED_NETWORKS:
            raise ValueError(f"Unsupported network: {network_name}")
        return cls.SUPPORTED_NETWORKS[network_name]
    
    @classmethod
    def get_evm_networks(cls) -> List[str]:
        """Get list of EVM-compatible networks."""
        return [
            name for name, config in cls.SUPPORTED_NETWORKS.items()
            if config.get("type") == "evm"
        ]
    
    @classmethod
    def get_non_evm_networks(cls) -> List[str]:
        """Get list of non-EVM networks."""
        return [
            name for name, config in cls.SUPPORTED_NETWORKS.items()
            if config.get("type") != "evm"
        ]
    
    @classmethod
    def get_all_networks(cls) -> List[str]:
        """Get list of all supported networks."""
        return list(cls.SUPPORTED_NETWORKS.keys())


# Global settings instance
settings = Settings()