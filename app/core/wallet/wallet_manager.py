"""
Wallet Management System
File: app/core/wallet/wallet_manager.py

Professional wallet management system with comprehensive security,
multi-chain support, and secure transaction signing capabilities.
"""

import asyncio
import json
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import secrets
from pathlib import Path

try:
    from web3 import Web3
    from eth_account import Account
    from eth_account.messages import encode_defunct
    import eth_utils
    WEB3_AVAILABLE = True
except ImportError:
    # Fallback for testing without Web3
    WEB3_AVAILABLE = False
    Web3 = None
    Account = None

from app.utils.logger import setup_logger
from app.core.exceptions import (
    WalletError, 
    InsufficientFundsError,
    InvalidAddressError,
    TransactionError,
    SecurityError
)

logger = setup_logger(__name__)


class WalletType(str, Enum):
    """Supported wallet types."""
    METAMASK = "metamask"
    WALLETCONNECT = "walletconnect"
    PRIVATE_KEY = "private_key"
    HARDWARE = "hardware"
    MULTISIG = "multisig"


class NetworkType(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    DROPPED = "dropped"
    REPLACED = "replaced"


@dataclass
class WalletBalance:
    """Wallet balance data structure."""
    native_balance: Decimal
    token_balances: Dict[str, Decimal]
    total_usd_value: Decimal
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TransactionRequest:
    """Transaction request data structure."""
    to_address: str
    value: Decimal
    data: str = ""
    gas_limit: Optional[int] = None
    gas_price: Optional[int] = None
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    nonce: Optional[int] = None


@dataclass
class TransactionResult:
    """Transaction execution result."""
    transaction_hash: str
    status: TransactionStatus
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    effective_gas_price: Optional[int] = None
    confirmations: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class WalletManager:
    """
    Professional wallet management system for DEX trading operations.
    
    Provides secure wallet operations, balance tracking, and transaction
    management across multiple blockchain networks.
    """
    
    def __init__(self, network: NetworkType = NetworkType.ETHEREUM):
        """Initialize wallet manager."""
        self.network = network
        self.web3 = None
        self.connected_wallets: Dict[str, Dict[str, Any]] = {}
        self.network_configs = self._load_network_configs()
        self.session_tokens: Dict[str, str] = {}
        
        # Initialize Web3 connection
        asyncio.create_task(self._initialize_web3())
        
        logger.info(f"🏦 Wallet Manager initialized for {network.value}")
    
    def _load_network_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load network configuration settings."""
        return {
            "ethereum": {
                "chain_id": 1,
                "rpc_url": "https://eth-mainnet.g.alchemy.com/v2/your-api-key",
                "explorer_url": "https://etherscan.io",
                "native_symbol": "ETH",
                "gas_multiplier": 1.2,
                "confirmation_blocks": 3
            },
            "polygon": {
                "chain_id": 137,
                "rpc_url": "https://polygon-mainnet.g.alchemy.com/v2/your-api-key",
                "explorer_url": "https://polygonscan.com",
                "native_symbol": "MATIC",
                "gas_multiplier": 1.1,
                "confirmation_blocks": 10
            },
            "bsc": {
                "chain_id": 56,
                "rpc_url": "https://bsc-dataseed1.binance.org",
                "explorer_url": "https://bscscan.com",
                "native_symbol": "BNB",
                "gas_multiplier": 1.1,
                "confirmation_blocks": 3
            },
            "arbitrum": {
                "chain_id": 42161,
                "rpc_url": "https://arb-mainnet.g.alchemy.com/v2/your-api-key",
                "explorer_url": "https://arbiscan.io",
                "native_symbol": "ETH",
                "gas_multiplier": 1.0,
                "confirmation_blocks": 1
            }
        }
    
    async def _initialize_web3(self) -> None:
        """Initialize Web3 connection for the current network."""
        try:
            if not WEB3_AVAILABLE:
                logger.warning("⚠️ Web3 not available - running in test mode")
                return
            
            config = self.network_configs.get(self.network.value)
            if not config:
                raise WalletError(f"Unsupported network: {self.network.value}")
            
            # Initialize Web3 with proper provider
            self.web3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
            
            # Test connection
            if not self.web3.is_connected():
                raise WalletError(f"Failed to connect to {self.network.value} network")
            
            # Get chain ID and verify
            chain_id = self.web3.eth.chain_id
            expected_chain_id = config["chain_id"]
            
            if chain_id != expected_chain_id:
                raise WalletError(
                    f"Chain ID mismatch: expected {expected_chain_id}, got {chain_id}"
                )
            
            logger.info(
                f"✅ Connected to {self.network.value} - Chain ID: {chain_id}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Web3: {e}")
            # In test mode, continue without Web3
            if not WEB3_AVAILABLE:
                logger.info("🧪 Continuing in test mode without Web3")
                return
            raise WalletError(f"Web3 initialization failed: {e}")
    
    async def connect_wallet(
        self,
        wallet_address: str,
        wallet_type: WalletType,
        signature: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Connect and authenticate a user wallet.
        
        Args:
            wallet_address: The wallet address to connect
            wallet_type: Type of wallet being connected
            signature: Signature for authentication (if required)
            message: Message that was signed (if required)
            
        Returns:
            Connection result with session token
        """
        try:
            # Validate wallet address format
            if not self._is_valid_address(wallet_address):
                raise InvalidAddressError(f"Invalid address format: {wallet_address}")
            
            # Check if wallet is already connected
            if wallet_address in self.connected_wallets:
                logger.info(f"🔄 Wallet {wallet_address[:10]}... already connected")
                return self.connected_wallets[wallet_address]
            
            # Authenticate wallet if signature provided
            if signature and message:
                if not await self._verify_signature(wallet_address, message, signature):
                    raise SecurityError("Invalid signature - authentication failed")
            
            # Get wallet balance and info
            balance_info = await self.get_wallet_balance(wallet_address)
            
            # Generate session token
            session_token = self._generate_session_token(wallet_address)
            
            # Store wallet connection info
            wallet_info = {
                "address": wallet_address,
                "type": wallet_type.value,
                "balance": balance_info,
                "session_token": session_token,
                "connected_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "network": self.network.value
            }
            
            self.connected_wallets[wallet_address] = wallet_info
            self.session_tokens[session_token] = wallet_address
            
            logger.info(
                f"✅ Wallet connected: {wallet_address[:10]}... "
                f"({wallet_type.value}) - Balance: {balance_info.native_balance:.4f} "
                f"{self.network_configs[self.network.value]['native_symbol']}"
            )
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "session_token": session_token,
                "balance": balance_info,
                "network": self.network.value,
                "message": "Wallet connected successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Wallet connection failed: {e}")
            raise WalletError(f"Failed to connect wallet: {e}")
    
    async def disconnect_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Disconnect a wallet and clean up session."""
        try:
            if wallet_address not in self.connected_wallets:
                raise WalletError(f"Wallet {wallet_address} is not connected")
            
            # Get session token to clean up
            wallet_info = self.connected_wallets[wallet_address]
            session_token = wallet_info.get("session_token")
            
            # Remove from connected wallets
            del self.connected_wallets[wallet_address]
            
            # Remove session token
            if session_token and session_token in self.session_tokens:
                del self.session_tokens[session_token]
            
            logger.info(f"👋 Wallet disconnected: {wallet_address[:10]}...")
            
            return {
                "success": True,
                "message": "Wallet disconnected successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Wallet disconnection failed: {e}")
            raise WalletError(f"Failed to disconnect wallet: {e}")
    
    async def get_wallet_balance(self, wallet_address: str) -> WalletBalance:
        """
        Get comprehensive wallet balance information.
        
        Args:
            wallet_address: The wallet address to check
            
        Returns:
            WalletBalance object with native and token balances
        """
        try:
            if not self.web3:
                await self._initialize_web3()
            
            # Get native token balance
            native_balance_wei = await self.web3.eth.get_balance(wallet_address)
            native_balance = Decimal(self.web3.from_wei(native_balance_wei, 'ether'))
            
            # Get ERC-20 token balances (implement based on requirements)
            token_balances = await self._get_token_balances(wallet_address)
            
            # Calculate total USD value (implement price fetching)
            total_usd_value = await self._calculate_total_usd_value(
                native_balance, token_balances
            )
            
            return WalletBalance(
                native_balance=native_balance,
                token_balances=token_balances,
                total_usd_value=total_usd_value
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get wallet balance: {e}")
            raise WalletError(f"Balance retrieval failed: {e}")
    
    async def estimate_gas(self, transaction_request: TransactionRequest) -> int:
        """
        Estimate gas required for a transaction.
        
        Args:
            transaction_request: Transaction details
            
        Returns:
            Estimated gas limit
        """
        try:
            if not self.web3:
                await self._initialize_web3()
            
            # Build transaction for estimation
            tx_params = {
                'to': transaction_request.to_address,
                'value': self.web3.to_wei(transaction_request.value, 'ether'),
                'data': transaction_request.data or '0x'
            }
            
            # Estimate gas
            estimated_gas = await self.web3.eth.estimate_gas(tx_params)
            
            # Apply network-specific multiplier for safety
            config = self.network_configs[self.network.value]
            gas_multiplier = config.get("gas_multiplier", 1.2)
            safe_gas_limit = int(estimated_gas * gas_multiplier)
            
            logger.debug(
                f"⛽ Gas estimation: {estimated_gas} -> {safe_gas_limit} "
                f"(multiplier: {gas_multiplier})"
            )
            
            return safe_gas_limit
            
        except Exception as e:
            logger.error(f"❌ Gas estimation failed: {e}")
            raise TransactionError(f"Failed to estimate gas: {e}")
    
    async def send_transaction(
        self,
        wallet_address: str,
        transaction_request: TransactionRequest,
        private_key: Optional[str] = None
    ) -> TransactionResult:
        """
        Send a transaction from the specified wallet.
        
        Args:
            wallet_address: Sender wallet address
            transaction_request: Transaction details
            private_key: Private key for signing (if available)
            
        Returns:
            TransactionResult with hash and status
        """
        try:
            # Verify wallet is connected
            if wallet_address not in self.connected_wallets:
                raise WalletError(f"Wallet {wallet_address} is not connected")
            
            if not self.web3:
                await self._initialize_web3()
            
            # Get current nonce
            nonce = transaction_request.nonce
            if nonce is None:
                nonce = await self.web3.eth.get_transaction_count(wallet_address)
            
            # Estimate gas if not provided
            gas_limit = transaction_request.gas_limit
            if gas_limit is None:
                gas_limit = await self.estimate_gas(transaction_request)
            
            # Get gas price
            gas_price = transaction_request.gas_price
            if gas_price is None:
                gas_price = await self.web3.eth.gas_price
            
            # Build transaction
            transaction = {
                'to': transaction_request.to_address,
                'value': self.web3.to_wei(transaction_request.value, 'ether'),
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'data': transaction_request.data or '0x'
            }
            
            # Sign and send transaction
            if private_key:
                # Sign with private key
                signed_txn = self.web3.eth.account.sign_transaction(
                    transaction, private_key
                )
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_txn.rawTransaction
                )
            else:
                # For MetaMask/WalletConnect, return unsigned transaction
                # for frontend signing
                return TransactionResult(
                    transaction_hash="pending_signature",
                    status=TransactionStatus.PENDING
                )
            
            # Wait for confirmation
            receipt = await self.web3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=300
            )
            
            # Determine status
            status = (
                TransactionStatus.CONFIRMED if receipt.status == 1 
                else TransactionStatus.FAILED
            )
            
            result = TransactionResult(
                transaction_hash=tx_hash.hex(),
                status=status,
                block_number=receipt.blockNumber,
                gas_used=receipt.gasUsed,
                effective_gas_price=receipt.effectiveGasPrice
            )
            
            logger.info(
                f"✅ Transaction sent: {tx_hash.hex()[:10]}... "
                f"Status: {status.value} - Gas used: {receipt.gasUsed}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            raise TransactionError(f"Failed to send transaction: {e}")
    
    def _is_valid_address(self, address: str) -> bool:
        """Validate Ethereum address format."""
        try:
            if not WEB3_AVAILABLE:
                # Basic validation for testing
                return (
                    isinstance(address, str) and 
                    len(address) == 42 and 
                    address.startswith('0x')
                )
            return Web3.is_address(address)
        except Exception:
            return False
    
    async def _verify_signature(
        self, 
        wallet_address: str, 
        message: str, 
        signature: str
    ) -> bool:
        """Verify message signature for wallet authentication."""
        try:
            # Encode message
            encoded_message = encode_defunct(text=message)
            
            # Recover address from signature
            recovered_address = Account.recover_message(
                encoded_message, signature=signature
            )
            
            # Check if recovered address matches wallet address
            return recovered_address.lower() == wallet_address.lower()
            
        except Exception as e:
            logger.error(f"❌ Signature verification failed: {e}")
            return False
    
    def _generate_session_token(self, wallet_address: str) -> str:
        """Generate secure session token for wallet."""
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_data = secrets.token_hex(16)
        data = f"{wallet_address}{timestamp}{random_data}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def _get_token_balances(self, wallet_address: str) -> Dict[str, Decimal]:
        """Get ERC-20 token balances for wallet."""
        # TODO: Implement ERC-20 balance fetching
        # This would iterate through known tokens and check balances
        return {}
    
    async def _calculate_total_usd_value(
        self, 
        native_balance: Decimal, 
        token_balances: Dict[str, Decimal]
    ) -> Decimal:
        """Calculate total portfolio value in USD."""
        # TODO: Implement USD value calculation using price feeds
        # For now, return 0 as placeholder
        return Decimal("0")
    
    def get_connected_wallets(self) -> List[Dict[str, Any]]:
        """Get list of all connected wallets."""
        return [
            {
                "address": info["address"],
                "type": info["type"],
                "connected_at": info["connected_at"].isoformat(),
                "network": info["network"]
            }
            for info in self.connected_wallets.values()
        ]
    
    def is_wallet_connected(self, wallet_address: str) -> bool:
        """Check if a wallet is currently connected."""
        return wallet_address in self.connected_wallets
    
    def validate_session_token(self, session_token: str) -> Optional[str]:
        """Validate session token and return wallet address."""
        return self.session_tokens.get(session_token)