"""
Network configuration for all supported blockchain networks.
Contains chain configurations, RPC endpoints, and DEX protocols.
"""

from typing import Dict, List


class NetworkConfig:
    """Network configuration constants and mappings."""
    
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
            "explorer": "https://etherscan.io"
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
            "explorer": "https://arbiscan.io"
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
            "explorer": "https://optimistic.etherscan.io"
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
            "explorer": "https://basescan.org"
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
            "explorer": "https://polygonscan.com"
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
            "explorer": "https://bscscan.com"
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
            "explorer": "https://snowtrace.io"
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
            "explorer": "https://solscan.io"
        }
    }
    
    @classmethod
    def get_network_config(cls, network_name: str) -> Dict:
        """Get configuration for a specific network."""
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