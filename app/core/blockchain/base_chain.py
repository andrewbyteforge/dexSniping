"""
File: app/core/blockchain/base_chain.py

Abstract base class for blockchain chain implementations.
Defines the interface that all blockchain chains must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum


class ChainType(Enum):
    """Enumeration of supported blockchain types."""
    EVM = "evm"
    SOLANA = "solana"
    STARKNET = "starknet"
    SUI = "sui"
    SEI = "sei"


@dataclass
class TokenInfo:
    """Data class for token information."""
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: Optional[int] = None
    verified: bool = False
    created_at: Optional[int] = None
    creator: Optional[str] = None


@dataclass
class LiquidityInfo:
    """Data class for liquidity information."""
    dex: str
    pair_address: str
    token0: str
    token1: str
    reserve0: Decimal
    reserve1: Decimal
    total_liquidity_usd: Decimal
    volume_24h_usd: Decimal
    price_usd: Decimal


@dataclass
class TransactionInfo:
    """Data class for transaction information."""
    hash: str
    block_number: int
    timestamp: int
    from_address: str
    to_address: str
    value: Decimal
    gas_used: int
    gas_price: Decimal
    status: bool


class BaseChain(ABC):
    """
    Abstract base class for blockchain chain implementations.
    
    This class defines the interface that all blockchain chains must implement
    to ensure consistent behavior across different networks.
    """
    
    def __init__(self, network_name: str, rpc_urls: List[str], **kwargs):
        """
        Initialize the base chain.
        
        Args:
            network_name: Name of the network (e.g., 'ethereum', 'polygon')
            rpc_urls: List of RPC URLs for the network
            **kwargs: Additional network-specific configuration
        """
        self.network_name = network_name
        self.rpc_urls = rpc_urls
        self.config = kwargs
        self._connected = False
    
    @property
    @abstractmethod
    def chain_type(self) -> ChainType:
        """Get the type of blockchain (EVM, Solana, etc.)."""
        pass
    
    @property
    @abstractmethod
    def chain_id(self) -> Union[int, str]:
        """Get the chain ID for this network."""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if the chain connection is active."""
        return self._connected
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the blockchain network.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the blockchain network."""
        pass
    
    @abstractmethod
    async def get_latest_block_number(self) -> int:
        """
        Get the latest block number.
        
        Returns:
            Latest block number
        """
        pass
    
    @abstractmethod
    async def get_block_timestamp(self, block_number: int) -> int:
        """
        Get timestamp for a specific block.
        
        Args:
            block_number: Block number to query
            
        Returns:
            Block timestamp
        """
        pass
    
    @abstractmethod
    async def get_token_info(self, token_address: str) -> Optional[TokenInfo]:
        """
        Get detailed information about a token.
        
        Args:
            token_address: Token contract address
            
        Returns:
            TokenInfo object or None if not found
        """
        pass
    
    @abstractmethod
    async def get_token_liquidity(self, token_address: str) -> List[LiquidityInfo]:
        """
        Get liquidity information for a token across all DEXs.
        
        Args:
            token_address: Token contract address
            
        Returns:
            List of LiquidityInfo objects
        """
        pass
    
    @abstractmethod
    async def get_token_price(self, token_address: str) -> Optional[Decimal]:
        """
        Get current USD price for a token.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Current price in USD or None if not available
        """
        pass
    
    @abstractmethod
    async def scan_new_tokens(
        self,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[TokenInfo]:
        """
        Scan for newly created tokens in a block range.
        
        Args:
            from_block: Starting block number
            to_block: Ending block number (latest if None)
            
        Returns:
            List of newly discovered tokens
        """
        pass
    
    @abstractmethod
    async def get_transaction_info(self, tx_hash: str) -> Optional[TransactionInfo]:
        """
        Get detailed information about a transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            TransactionInfo object or None if not found
        """
        pass
    
    @abstractmethod
    async def estimate_gas(
        self,
        from_address: str,
        to_address: str,
        data: str,
        value: int = 0
    ) -> int:
        """
        Estimate gas required for a transaction.
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            data: Transaction data
            value: Transaction value
            
        Returns:
            Estimated gas amount
        """
        pass
    
    @abstractmethod
    async def get_gas_price(self) -> Decimal:
        """
        Get current gas price for the network.
        
        Returns:
            Current gas price
        """
        pass
    
    @abstractmethod
    async def send_transaction(
        self,
        from_address: str,
        to_address: str,
        data: str,
        value: int = 0,
        gas_limit: Optional[int] = None,
        gas_price: Optional[Decimal] = None
    ) -> str:
        """
        Send a transaction to the network.
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            data: Transaction data
            value: Transaction value
            gas_limit: Gas limit for transaction
            gas_price: Gas price for transaction
            
        Returns:
            Transaction hash
        """
        pass
    
    @abstractmethod
    async def check_contract_security(self, contract_address: str) -> Dict[str, Any]:
        """
        Perform basic security checks on a contract.
        
        Args:
            contract_address: Contract address to check
            
        Returns:
            Dictionary containing security check results
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the chain connection.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            if not self.is_connected:
                await self.connect()
            
            latest_block = await self.get_latest_block_number()
            gas_price = await self.get_gas_price()
            
            return {
                "status": "healthy",
                "network": self.network_name,
                "connected": self.is_connected,
                "latest_block": latest_block,
                "gas_price": float(gas_price),
                "rpc_url": self.rpc_urls[0] if self.rpc_urls else None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "network": self.network_name,
                "connected": False,
                "error": str(e)
            }
    
    def __str__(self) -> str:
        """String representation of the chain."""
        return f"{self.__class__.__name__}({self.network_name})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the chain."""
        return (
            f"{self.__class__.__name__}("
            f"network_name='{self.network_name}', "
            f"connected={self.is_connected})"
        )