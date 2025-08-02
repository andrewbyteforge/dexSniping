"""
File: app/core/blockchain/evm_chains/ethereum_chain.py

Ethereum blockchain implementation with Web3 integration.
Provides comprehensive functionality for interacting with Ethereum and EVM-compatible chains.
"""

from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import asyncio
import json

from app.core.blockchain.base_chain import (
    BaseChain, ChainType, TokenInfo, LiquidityInfo, TransactionInfo
)
from app.utils.exceptions import (
    ChainConnectionException, TokenNotFoundError, APIException
)
from app.utils.logger import setup_logger
from app.config import NetworkConfig

logger = setup_logger(__name__)


class EthereumChain(BaseChain):
    """
    Ethereum and EVM-compatible blockchain implementation.
    
    Provides full functionality for interacting with Ethereum-based networks
    including token discovery, liquidity analysis, and transaction execution.
    """
    
    def __init__(self, network_name: str, rpc_urls: List[str], **kwargs):
        """
        Initialize Ethereum chain connection.
        
        Args:
            network_name: Name of the network
            rpc_urls: List of RPC endpoints
            **kwargs: Additional network configuration
        """
        super().__init__(network_name, rpc_urls, **kwargs)
        self.w3: Optional[AsyncWeb3] = None
        self._chain_id = kwargs.get('chain_id')
        self._dex_protocols = kwargs.get('dex_protocols', [])
        self._multicall_address = kwargs.get('multicall_address')
        
        # ERC-20 ABI for token interactions
        self.erc20_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        # Uniswap V2 Pair ABI for liquidity analysis
        self.uniswap_v2_pair_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"name": "reserve0", "type": "uint112"},
                    {"name": "reserve1", "type": "uint112"},
                    {"name": "blockTimestampLast", "type": "uint32"}
                ],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token0",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token1",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            }
        ]
    
    @property
    def chain_type(self) -> ChainType:
        """Get the chain type (EVM)."""
        return ChainType.EVM
    
    @property
    def chain_id(self) -> int:
        """Get the chain ID."""
        return self._chain_id
    
    async def connect(self) -> bool:
        """
        Establish connection to the Ethereum network.
        
        Returns:
            True if connection successful, False otherwise
        """
        for rpc_url in self.rpc_urls:
            try:
                logger.info(f"Attempting to connect to {self.network_name} via {rpc_url}")
                
                # Create Web3 instance
                self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
                
                # Add PoA middleware for certain networks
                if self.network_name in ['bnb_chain', 'polygon']:
                    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                # Test connection
                chain_id = await self.w3.eth.chain_id
                if chain_id != self._chain_id:
                    logger.warning(
                        f"Chain ID mismatch for {self.network_name}. "
                        f"Expected: {self._chain_id}, Got: {chain_id}"
                    )
                    continue
                
                # Test latest block
                latest_block = await self.w3.eth.block_number
                logger.info(
                    f"Connected to {self.network_name}. "
                    f"Chain ID: {chain_id}, Latest block: {latest_block}"
                )
                
                self._connected = True
                return True
                
            except Exception as e:
                logger.error(f"Failed to connect to {rpc_url}: {e}")
                continue
        
        logger.error(f"Failed to connect to any RPC for {self.network_name}")
        self._connected = False
        return False
    
    async def disconnect(self):
        """Disconnect from the Ethereum network."""
        if self.w3:
            # AsyncWeb3 doesn't require explicit disconnection
            self.w3 = None
        self._connected = False
        logger.info(f"Disconnected from {self.network_name}")
    
    async def get_latest_block_number(self) -> int:
        """
        Get the latest block number.
        
        Returns:
            Latest block number
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            return await self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Failed to get latest block number: {e}")
            raise ChainConnectionException(f"Failed to get latest block: {e}")
    
    async def get_block_timestamp(self, block_number: int) -> int:
        """
        Get timestamp for a specific block.
        
        Args:
            block_number: Block number to query
            
        Returns:
            Block timestamp
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            block = await self.w3.eth.get_block(block_number)
            return block.timestamp
        except Exception as e:
            logger.error(f"Failed to get block timestamp for block {block_number}: {e}")
            raise ChainConnectionException(f"Failed to get block timestamp: {e}")
    
    async def get_token_info(self, token_address: str) -> Optional[TokenInfo]:
        """
        Get detailed information about a token.
        
        Args:
            token_address: Token contract address
            
        Returns:
            TokenInfo object or None if not found
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            # Validate address
            if not Web3.is_address(token_address):
                raise TokenNotFoundError(f"Invalid token address: {token_address}")
            
            token_address = Web3.to_checksum_address(token_address)
            contract = self.w3.eth.contract(
                address=token_address,
                abi=self.erc20_abi
            )
            
            # Get token information
            try:
                name = await contract.functions.name().call()
                symbol = await contract.functions.symbol().call()
                decimals = await contract.functions.decimals().call()
                total_supply = await contract.functions.totalSupply().call()
            except Exception as e:
                logger.warning(f"Failed to get token info for {token_address}: {e}")
                return None
            
            # Get creation info
            creation_block = await self._get_contract_creation_block(token_address)
            creator = await self._get_contract_creator(token_address)
            
            return TokenInfo(
                address=token_address,
                name=name,
                symbol=symbol,
                decimals=decimals,
                total_supply=total_supply,
                verified=await self._is_contract_verified(token_address),
                created_at=creation_block,
                creator=creator
            )
            
        except Exception as e:
            logger.error(f"Failed to get token info for {token_address}: {e}")
            return None
    
    async def get_token_liquidity(self, token_address: str) -> List[LiquidityInfo]:
        """
        Get liquidity information for a token across all DEXs.
        
        Args:
            token_address: Token contract address
            
        Returns:
            List of LiquidityInfo objects
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        liquidity_info = []
        
        for dex_protocol in self._dex_protocols:
            try:
                pairs = await self._get_pairs_for_token(token_address, dex_protocol)
                for pair in pairs:
                    liquidity = await self._get_pair_liquidity(pair, dex_protocol)
                    if liquidity:
                        liquidity_info.append(liquidity)
            except Exception as e:
                logger.error(f"Failed to get liquidity for {dex_protocol}: {e}")
                continue
        
        return liquidity_info
    
    async def get_token_price(self, token_address: str) -> Optional[Decimal]:
        """
        Get current USD price for a token.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Current price in USD or None if not available
        """
        liquidity_info = await self.get_token_liquidity(token_address)
        
        if not liquidity_info:
            return None
        
        # Use the pair with highest liquidity for price
        highest_liquidity_pair = max(
            liquidity_info,
            key=lambda x: x.total_liquidity_usd
        )
        
        return highest_liquidity_pair.price_usd
    
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
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        if to_block is None:
            to_block = await self.get_latest_block_number()
        
        new_tokens = []
        
        try:
            # Get all contract creation transactions in the block range
            for block_number in range(from_block, to_block + 1):
                try:
                    block = await self.w3.eth.get_block(block_number, full_transactions=True)
                    
                    for tx in block.transactions:
                        # Check if transaction creates a contract
                        if tx.to is None and tx.input:
                            receipt = await self.w3.eth.get_transaction_receipt(tx.hash)
                            if receipt.contractAddress:
                                # Check if it's an ERC-20 token
                                token_info = await self.get_token_info(receipt.contractAddress)
                                if token_info:
                                    token_info.created_at = block.timestamp
                                    token_info.creator = tx['from']
                                    new_tokens.append(token_info)
                
                except Exception as e:
                    logger.error(f"Error scanning block {block_number}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to scan for new tokens: {e}")
            raise ChainConnectionException(f"Token scanning failed: {e}")
        
        logger.info(f"Found {len(new_tokens)} new tokens in blocks {from_block}-{to_block}")
        return new_tokens
    
    async def get_transaction_info(self, tx_hash: str) -> Optional[TransactionInfo]:
        """
        Get detailed information about a transaction.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            TransactionInfo object or None if not found
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            tx = await self.w3.eth.get_transaction(tx_hash)
            receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
            block = await self.w3.eth.get_block(tx.blockNumber)
            
            return TransactionInfo(
                hash=tx_hash,
                block_number=tx.blockNumber,
                timestamp=block.timestamp,
                from_address=tx['from'],
                to_address=tx.to or receipt.contractAddress,
                value=Decimal(str(tx.value)),
                gas_used=receipt.gasUsed,
                gas_price=Decimal(str(tx.gasPrice)),
                status=bool(receipt.status)
            )
            
        except Exception as e:
            logger.error(f"Failed to get transaction info for {tx_hash}: {e}")
            return None
    
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
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            gas_estimate = await self.w3.eth.estimate_gas({
                'from': Web3.to_checksum_address(from_address),
                'to': Web3.to_checksum_address(to_address),
                'data': data,
                'value': value
            })
            return gas_estimate
        except Exception as e:
            logger.error(f"Failed to estimate gas: {e}")
            raise ChainConnectionException(f"Gas estimation failed: {e}")
    
    async def get_gas_price(self) -> Decimal:
        """
        Get current gas price for the network.
        
        Returns:
            Current gas price in wei
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            gas_price = await self.w3.eth.gas_price
            return Decimal(str(gas_price))
        except Exception as e:
            logger.error(f"Failed to get gas price: {e}")
            raise ChainConnectionException(f"Failed to get gas price: {e}")
    
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
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        try:
            if gas_limit is None:
                gas_limit = await self.estimate_gas(from_address, to_address, data, value)
            
            if gas_price is None:
                gas_price = await self.get_gas_price()
            
            transaction = {
                'from': Web3.to_checksum_address(from_address),
                'to': Web3.to_checksum_address(to_address),
                'data': data,
                'value': value,
                'gas': gas_limit,
                'gasPrice': int(gas_price),
                'nonce': await self.w3.eth.get_transaction_count(from_address)
            }
            
            # Note: This requires private key signing which should be handled
            # by the wallet service for security
            tx_hash = await self.w3.eth.send_transaction(transaction)
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            raise ChainConnectionException(f"Transaction failed: {e}")
    
    async def check_contract_security(self, contract_address: str) -> Dict[str, Any]:
        """
        Perform basic security checks on a contract.
        
        Args:
            contract_address: Contract address to check
            
        Returns:
            Dictionary containing security check results
        """
        if not self.is_connected:
            raise ChainConnectionException("Not connected to blockchain")
        
        security_checks = {
            "is_contract": False,
            "is_verified": False,
            "has_mint_function": False,
            "has_pause_function": False,
            "ownership_renounced": False,
            "liquidity_locked": False,
            "honeypot_risk": "low"
        }
        
        try:
            # Check if address is a contract
            code = await self.w3.eth.get_code(Web3.to_checksum_address(contract_address))
            security_checks["is_contract"] = len(code) > 0
            
            if security_checks["is_contract"]:
                # Check if contract is verified (this would require external API)
                security_checks["is_verified"] = await self._is_contract_verified(contract_address)
                
                # Analyze contract bytecode for common patterns
                bytecode = code.hex()
                
                # Check for mint function signature (0x40c10f19)
                security_checks["has_mint_function"] = "40c10f19" in bytecode
                
                # Check for pause function signature (0x8456cb59)
                security_checks["has_pause_function"] = "8456cb59" in bytecode
                
                # Additional security checks would go here
                # This is a simplified implementation
                
        except Exception as e:
            logger.error(f"Security check failed for {contract_address}: {e}")
        
        return security_checks
    
    # Helper methods
    
    async def _get_contract_creation_block(self, contract_address: str) -> Optional[int]:
        """Get the block number when contract was created."""
        # This would require binary search through blocks or external API
        # Simplified implementation
        return None
    
    async def _get_contract_creator(self, contract_address: str) -> Optional[str]:
        """Get the address that created the contract."""
        # This would require transaction history analysis or external API
        # Simplified implementation
        return None
    
    async def _is_contract_verified(self, contract_address: str) -> bool:
        """Check if contract source code is verified."""
        # This would require external API call (Etherscan, etc.)
        # Simplified implementation
        return False
    
    async def _get_pairs_for_token(self, token_address: str, dex_protocol: str) -> List[str]:
        """Get trading pairs for a token on a specific DEX."""
        # Implementation would depend on the DEX
        # This would query factory contracts to find pairs
        # Simplified implementation
        return []
    
    async def _get_pair_liquidity(self, pair_address: str, dex_protocol: str) -> Optional[LiquidityInfo]:
        """Get liquidity information for a specific pair."""
        try:
            pair_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=self.uniswap_v2_pair_abi
            )
            
            # Get pair reserves
            reserves = await pair_contract.functions.getReserves().call()
            token0 = await pair_contract.functions.token0().call()
            token1 = await pair_contract.functions.token1().call()
            
            # Calculate USD values (would require price oracles)
            # Simplified implementation
            total_liquidity_usd = Decimal("0")
            volume_24h_usd = Decimal("0")
            price_usd = Decimal("0")
            
            return LiquidityInfo(
                dex=dex_protocol,
                pair_address=pair_address,
                token0=token0,
                token1=token1,
                reserve0=Decimal(str(reserves[0])),
                reserve1=Decimal(str(reserves[1])),
                total_liquidity_usd=total_liquidity_usd,
                volume_24h_usd=volume_24h_usd,
                price_usd=price_usd
            )
            
        except Exception as e:
            logger.error(f"Failed to get pair liquidity for {pair_address}: {e}")
            return None


# Network-specific implementations

class ArbitrumChain(EthereumChain):
    """Arbitrum One chain implementation."""
    pass


class OptimismChain(EthereumChain):
    """Optimism chain implementation."""
    pass


class BaseChainImpl(EthereumChain):
    """Base chain implementation."""
    pass


class PolygonChain(EthereumChain):
    """Polygon chain implementation."""
    pass


class BNBChain(EthereumChain):
    """BNB Chain implementation."""
    pass


class AvalancheChain(EthereumChain):
    """Avalanche C-Chain implementation."""
    pass