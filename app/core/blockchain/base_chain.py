"""
Base Chain
File: app/core/blockchain/base_chain.py

Base blockchain interaction class.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


from enum import Enum

class ChainType(str, Enum):
    """Blockchain network types."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"



from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class TokenInfo:
    """Token information data structure."""
    address: str
    symbol: str
    name: str
    decimals: int
    total_supply: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    creator_address: Optional[str] = None
    is_verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LiquidityInfo:
    """Liquidity information data structure."""
    pool_address: str
    token0: str
    token1: str
    reserves0: Decimal
    reserves1: Decimal
    total_liquidity_usd: Decimal
    price_per_token: Decimal
    last_updated: datetime = field(default_factory=datetime.utcnow)


from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseChain(ABC):
    """
    Abstract base class for blockchain interactions.
    
    This provides a common interface for different blockchain networks.
    """
    
    def __init__(self, network_name: str = "ethereum"):
        """Initialize base chain."""
        self.network_name = network_name
        self.connected = False
        logger.info(f"[OK] BaseChain initialized for {network_name}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the blockchain."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the blockchain."""
        pass
    
    @abstractmethod
    async def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """Get token information."""
        pass
    
    @abstractmethod
    async def get_balance(self, address: str, token_address: Optional[str] = None) -> float:
        """Get token or native balance."""
        pass
    
    def get_network_name(self) -> str:
        """Get network name."""
        return self.network_name
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected


class MockChain(BaseChain):
    """Mock chain implementation for testing."""
    
    def __init__(self, network_name: str = "mock"):
        """Initialize mock chain."""
        super().__init__(network_name)
        self.mock_data = {}
    
    async def connect(self) -> bool:
        """Mock connect."""
        self.connected = True
        logger.info("[OK] Mock chain connected")
        return True
    
    async def disconnect(self) -> bool:
        """Mock disconnect."""
        self.connected = False
        logger.info("[OK] Mock chain disconnected")
        return True
    
    async def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """Get mock token info."""
        return {
            "address": token_address,
            "symbol": "MOCK",
            "name": "Mock Token",
            "decimals": 18,
            "total_supply": "1000000",
            "price_usd": 1.0,
            "liquidity_usd": 100000.0
        }
    
    async def get_balance(self, address: str, token_address: Optional[str] = None) -> float:
        """Get mock balance."""
        return 100.0  # Mock balance


# Default chain instance
def get_default_chain() -> BaseChain:
    """Get default chain instance."""
    return MockChain()
