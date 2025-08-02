from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Main application settings class."""
    
    database_url: str = "postgresql://localhost/dex_sniping"
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

class NetworkConfig:
    """Network configuration constants."""
    
    SUPPORTED_NETWORKS = {
        "ethereum": {
            "chain_id": 1,
            "type": "evm",
            "name": "Ethereum"
        },
        "polygon": {
            "chain_id": 137,
            "type": "evm", 
            "name": "Polygon"
        }
    }
    
    @classmethod
    def get_all_networks(cls) -> List[str]:
        return list(cls.SUPPORTED_NETWORKS.keys())
    

settings = Settings()