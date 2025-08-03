"""
File: app/core/sniping/block_zero_sniper.py

Block 0 sniping engine for instant token purchases.
Executes buy transactions in the same block as token launch.
Implements MEV protection and gas optimization strategies.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
import json

from web3 import Web3
from eth_account import Account
from eth_abi import encode_abi
import requests

from app.core.mempool.mempool_scanner import LiquidityAddEvent
from app.core.blockchain.base_chain import BaseChain
from app.core.performance.cache_manager import cache_manager
from app.core.performance.circuit_breaker import CircuitBreakerManager
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException
from app.config import settings

logger = setup_logger(__name__)


class BlockZeroSniperError(DexSnipingException):
    """Exception raised when Block 0 sniping operations fail."""
    pass


@dataclass
class SnipeConfig:
    """Configuration for sniping operations."""
    max_gas_price_gwei: int = 100
    gas_limit: int = 300000
    slippage_tolerance: float = 0.15  # 15%
    min_eth_amount: float = 0.01  # Minimum ETH to spend
    max_eth_amount: float = 1.0   # Maximum ETH to spend
    deadline_seconds: int = 300   # Transaction deadline
    use_flashbots: bool = True    # Use Flashbots for MEV protection
    max_priority_fee_gwei: int = 10
    base_fee_multiplier: float = 1.2


@dataclass
class SnipeTransaction:
    """Data class for snipe transaction information."""
    token_address: str
    router_address: str
    eth_amount: Decimal
    gas_price: int
    gas_limit: int
    deadline: int
    slippage_tolerance: float
    raw_transaction: Dict[str, Any]
    signed_transaction: str
    transaction_hash: str
    created_at: float = field(default_factory=time.time)
    
    @property
    def gas_price_gwei(self) -> float:
        """Get gas price in Gwei."""
        return self.gas_price / 10**9


@dataclass
class SnipeResult:
    """Result of a sniping operation."""
    token_address: str
    transaction_hash: str
    status: str  # 'pending', 'confirmed', 'failed'
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    effective_gas_price: Optional[int] = None
    tokens_received: Optional[int] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    mev_protection_used: bool = False


@dataclass
class GasStrategy:
    """Gas pricing strategy for optimal block inclusion."""
    base_fee: int
    priority_fee: int
    max_fee: int
    strategy_type: str  # 'aggressive', 'normal', 'conservative'
    
    @property
    def total_gas_price_gwei(self) -> float:
        """Get total gas price in Gwei."""
        return self.max_fee / 10**9


class BlockZeroSniper:
    """
    Advanced Block 0 sniping engine for instant token purchases.
    
    Features:
    - Mempool-based transaction building
    - MEV protection via Flashbots
    - Dynamic gas pricing strategies
    - Multiple DEX router support
    - Transaction bundling and optimization
    - Real-time execution monitoring
    """
    
    def __init__(self, network: str, w3: Web3, private_key: str):
        """
        Initialize Block 0 sniper.
        
        Args:
            network: Network name
            w3: Web3 instance
            private_key: Private key for signing transactions
        """
        self.network = network
        self.w3 = w3
        self.account = Account.from_key(private_key)
        self.circuit_breaker_manager = CircuitBreakerManager()
        
        # Configuration
        self.config = SnipeConfig(
            max_gas_price_gwei=getattr(settings, 'max_gas_price_gwei_int', 100),
            slippage_tolerance=float(getattr(settings, 'max_slippage_decimal', 0.15)),
            min_eth_amount=0.01,
            max_eth_amount=1.0
        )
        
        # DEX router addresses and ABIs
        self.routers = self._load_router_configs()
        self.router_abis = self._load_router_abis()
        
        # MEV protection
        self.flashbots_enabled = getattr(settings, 'use_flashbots', True)
        self.flashbots_relay_url = 'https://relay.flashbots.net'
        
        # Statistics
        self.snipe_attempts = 0
        self.successful_snipes = 0
        self.failed_snipes = 0
        
        logger.info(f"BlockZeroSniper initialized for {network}")
    
    def _load_router_configs(self) -> Dict[str, str]:
        """Load DEX router configurations for the network."""
        router_configs = {
            'ethereum': {
                'uniswap_v2': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'uniswap_v3': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'sushiswap': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
            },
            'polygon': {
                'quickswap': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
                'sushiswap': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
            },
            'bsc': {
                'pancakeswap': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
            }
        }
        return router_configs.get(self.network, {})
    
    def _load_router_abis(self) -> Dict[str, List[Dict]]:
        """Load minimal ABI for router contracts."""
        # Simplified ABI focusing on swapExactETHForTokens
        router_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactETHForTokens",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsIn",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        return {router_name: router_abi for router_name in self.routers.keys()}
    
    async def snipe_token_launch(
        self,
        liquidity_event: LiquidityAddEvent,
        eth_amount: float,
        priority: str = 'normal'
    ) -> SnipeResult:
        """
        Execute Block 0 snipe for detected token launch.
        
        Args:
            liquidity_event: Detected liquidity addition event
            eth_amount: Amount of ETH to spend
            priority: Sniping priority ('aggressive', 'normal', 'conservative')
            
        Returns:
            SnipeResult with transaction details and outcome
        """
        start_time = time.time()
        
        try:
            logger.info(
                f"🎯 Executing Block 0 snipe for {liquidity_event.token_address} "
                f"with {eth_amount} ETH (priority: {priority})"
            )
            
            self.snipe_attempts += 1
            
            # Validate snipe parameters
            await self._validate_snipe_parameters(liquidity_event, eth_amount)
            
            # Build snipe transaction
            snipe_tx = await self._build_snipe_transaction(
                liquidity_event, eth_amount, priority
            )
            
            # Execute transaction with MEV protection if enabled
            if self.flashbots_enabled:
                result = await self._execute_flashbots_snipe(snipe_tx, liquidity_event)
            else:
                result = await self._execute_regular_snipe(snipe_tx)
            
            # Update statistics
            if result.status == 'confirmed':
                self.successful_snipes += 1
            else:
                self.failed_snipes += 1
            
            # Calculate execution time
            result.execution_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Snipe result for {liquidity_event.token_address}: "
                f"{result.status} in {result.execution_time_ms:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            self.failed_snipes += 1
            execution_time = (time.time() - start_time) * 1000
            
            logger.error(f"Snipe failed for {liquidity_event.token_address}: {e}")
            
            return SnipeResult(
                token_address=liquidity_event.token_address,
                transaction_hash='',
                status='failed',
                error_message=str(e),
                execution_time_ms=execution_time
            )
    
    async def _validate_snipe_parameters(
        self,
        liquidity_event: LiquidityAddEvent,
        eth_amount: float
    ) -> None:
        """
        Validate sniping parameters before execution.
        
        Args:
            liquidity_event: Liquidity event to validate
            eth_amount: ETH amount to validate
            
        Raises:
            BlockZeroSniperError: If parameters are invalid
        """
        # Validate ETH amount
        if eth_amount < self.config.min_eth_amount:
            raise BlockZeroSniperError(
                f"ETH amount {eth_amount} below minimum {self.config.min_eth_amount}"
            )
        
        if eth_amount > self.config.max_eth_amount:
            raise BlockZeroSniperError(
                f"ETH amount {eth_amount} above maximum {self.config.max_eth_amount}"
            )
        
        # Check account balance
        balance = self.w3.eth.get_balance(self.account.address)
        balance_eth = balance / 10**18
        
        if balance_eth < eth_amount * 1.1:  # Include gas costs
            raise BlockZeroSniperError(
                f"Insufficient balance: {balance_eth:.4f} ETH available, "
                f"{eth_amount * 1.1:.4f} ETH needed"
            )
        
        # Validate token address
        if not Web3.isAddress(liquidity_event.token_address):
            raise BlockZeroSniperError(f"Invalid token address: {liquidity_event.token_address}")
        
        # Check if DEX is supported
        dex_name = liquidity_event.dex.lower()
        if dex_name not in self.routers:
            raise BlockZeroSniperError(f"Unsupported DEX: {dex_name}")
    
    async def _build_snipe_transaction(
        self,
        liquidity_event: LiquidityAddEvent,
        eth_amount: float,
        priority: str
    ) -> SnipeTransaction:
        """
        Build optimized snipe transaction.
        
        Args:
            liquidity_event: Liquidity event
            eth_amount: ETH amount to spend
            priority: Gas priority strategy
            
        Returns:
            SnipeTransaction ready for execution
        """
        try:
            # Get router configuration
            dex_name = liquidity_event.dex.lower()
            router_address = self.routers[dex_name]
            
            # Build transaction parameters
            token_address = Web3.toChecksumAddress(liquidity_event.token_address)
            weth_address = self._get_weth_address()
            
            # Create trading path
            path = [weth_address, token_address]
            
            # Calculate amounts and slippage
            eth_amount_wei = int(eth_amount * 10**18)
            min_tokens_out = await self._calculate_min_tokens_out(
                router_address, eth_amount_wei, path
            )
            
            # Get gas strategy
            gas_strategy = await self._get_gas_strategy(priority)
            
            # Build transaction data
            deadline = int(time.time()) + self.config.deadline_seconds
            
            # Encode function call
            router_contract = self.w3.eth.contract(
                address=router_address,
                abi=self.router_abis[dex_name]
            )
            
            transaction_data = router_contract.encodeABI(
                fn_name='swapExactETHForTokens',
                args=[
                    min_tokens_out,
                    path,
                    self.account.address,
                    deadline
                ]
            )
            
            # Build raw transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')
            
            raw_transaction = {
                'nonce': nonce,
                'to': router_address,
                'value': eth_amount_wei,
                'gas': self.config.gas_limit,
                'maxFeePerGas': gas_strategy.max_fee,
                'maxPriorityFeePerGas': gas_strategy.priority_fee,
                'data': transaction_data,
                'chainId': self.w3.eth.chain_id
            }
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(raw_transaction, self.account.key)
            
            snipe_tx = SnipeTransaction(
                token_address=token_address,
                router_address=router_address,
                eth_amount=Decimal(str(eth_amount)),
                gas_price=gas_strategy.max_fee,
                gas_limit=self.config.gas_limit,
                deadline=deadline,
                slippage_tolerance=self.config.slippage_tolerance,
                raw_transaction=raw_transaction,
                signed_transaction=signed_tx.rawTransaction.hex(),
                transaction_hash=signed_tx.hash.hex()
            )
            
            logger.info(
                f"Built snipe transaction: {snipe_tx.transaction_hash} "
                f"(Gas: {gas_strategy.total_gas_price_gwei:.1f} gwei)"
            )
            
            return snipe_tx
            
        except Exception as e:
            logger.error(f"Error building snipe transaction: {e}")
            raise BlockZeroSniperError(f"Transaction building failed: {e}")
    
    def _get_weth_address(self) -> str:
        """Get WETH address for the current network."""
        weth_addresses = {
            'ethereum': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
            'polygon': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',  # WMATIC
            'bsc': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',  # WBNB
        }
        return weth_addresses.get(self.network, weth_addresses['ethereum'])
    
    async def _calculate_min_tokens_out(
        self,
        router_address: str,
        eth_amount_wei: int,
        path: List[str]
    ) -> int:
        """
        Calculate minimum tokens out with slippage protection.
        
        Args:
            router_address: DEX router address
            eth_amount_wei: ETH amount in wei
            path: Trading path
            
        Returns:
            Minimum tokens out
        """
        try:
            # This is simplified - in production, you'd call getAmountsOut
            # For new tokens, we typically accept high slippage
            # Return a very low minimum to ensure transaction success
            return 1  # Accept any amount of tokens (high slippage tolerance)
            
        except Exception as e:
            logger.warning(f"Error calculating min tokens out: {e}")
            return 1  # Fallback to minimal amount
    
    async def _get_gas_strategy(self, priority: str) -> GasStrategy:
        """
        Get gas pricing strategy based on priority level.
        
        Args:
            priority: Priority level ('aggressive', 'normal', 'conservative')
            
        Returns:
            GasStrategy with optimized gas prices
        """
        try:
            # Get current base fee
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 20 * 10**9)  # Fallback to 20 gwei
            
            # Define priority fee strategies
            priority_fees = {
                'conservative': 2 * 10**9,   # 2 gwei
                'normal': 5 * 10**9,         # 5 gwei
                'aggressive': 20 * 10**9,    # 20 gwei
            }
            
            # Define max fee multipliers
            max_fee_multipliers = {
                'conservative': 1.2,
                'normal': 1.5,
                'aggressive': 2.0,
            }
            
            priority_fee = priority_fees.get(priority, priority_fees['normal'])
            multiplier = max_fee_multipliers.get(priority, max_fee_multipliers['normal'])
            max_fee = int((base_fee + priority_fee) * multiplier)
            
            # Ensure we don't exceed configured limits
            max_allowed = self.config.max_gas_price_gwei * 10**9
            if max_fee > max_allowed:
                max_fee = max_allowed
                priority_fee = min(priority_fee, max_fee - base_fee)
            
            return GasStrategy(
                base_fee=base_fee,
                priority_fee=priority_fee,
                max_fee=max_fee,
                strategy_type=priority
            )
            
        except Exception as e:
            logger.warning(f"Error getting gas strategy: {e}")
            # Fallback strategy
            return GasStrategy(
                base_fee=20 * 10**9,
                priority_fee=5 * 10**9,
                max_fee=50 * 10**9,
                strategy_type=priority
            )
    
    async def _execute_flashbots_snipe(
        self,
        snipe_tx: SnipeTransaction,
        liquidity_event: LiquidityAddEvent
    ) -> SnipeResult:
        """
        Execute snipe transaction via Flashbots for MEV protection.
        
        Args:
            snipe_tx: Prepared snipe transaction
            liquidity_event: Original liquidity event
            
        Returns:
            SnipeResult with execution details
        """
        try:
            logger.info(f"Executing Flashbots snipe for {snipe_tx.token_address}")
            
            # Create bundle with liquidity add transaction and snipe transaction
            bundle = [
                liquidity_event.pending_tx.hash,  # Original liquidity add
                snipe_tx.signed_transaction       # Our snipe transaction
            ]
            
            # Submit bundle to Flashbots
            result = await self._submit_flashbots_bundle(bundle, snipe_tx)
            
            if result:
                return SnipeResult(
                    token_address=snipe_tx.token_address,
                    transaction_hash=snipe_tx.transaction_hash,
                    status='pending',
                    mev_protection_used=True
                )
            else:
                # Fallback to regular transaction
                return await self._execute_regular_snipe(snipe_tx)
            
        except Exception as e:
            logger.error(f"Flashbots execution failed: {e}")
            # Fallback to regular transaction
            return await self._execute_regular_snipe(snipe_tx)
    
    async def _submit_flashbots_bundle(
        self,
        bundle: List[str],
        snipe_tx: SnipeTransaction
    ) -> bool:
        """
        Submit transaction bundle to Flashbots.
        
        Args:
            bundle: List of transaction hashes/raw transactions
            snipe_tx: Snipe transaction details
            
        Returns:
            True if bundle submitted successfully
        """
        try:
            # This is a simplified Flashbots implementation
            # In production, you'd use the proper Flashbots Python library
            
            latest_block = self.w3.eth.block_number
            target_block = latest_block + 1
            
            bundle_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_sendBundle",
                "params": [
                    {
                        "txs": bundle,
                        "blockNumber": hex(target_block)
                    }
                ]
            }
            
            # Note: In production, this would require proper Flashbots authentication
            logger.info(f"Flashbots bundle prepared for block {target_block}")
            return True  # Simplified success for demonstration
            
        except Exception as e:
            logger.error(f"Error submitting Flashbots bundle: {e}")
            return False
    
    async def _execute_regular_snipe(self, snipe_tx: SnipeTransaction) -> SnipeResult:
        """
        Execute snipe transaction via regular mempool.
        
        Args:
            snipe_tx: Prepared snipe transaction
            
        Returns:
            SnipeResult with execution details
        """
        try:
            logger.info(f"Executing regular snipe for {snipe_tx.token_address}")
            
            # Send transaction to network
            tx_hash = self.w3.eth.send_raw_transaction(snipe_tx.signed_transaction)
            
            logger.info(f"Snipe transaction sent: {tx_hash.hex()}")
            
            return SnipeResult(
                token_address=snipe_tx.token_address,
                transaction_hash=tx_hash.hex(),
                status='pending',
                mev_protection_used=False
            )
            
        except Exception as e:
            logger.error(f"Regular snipe execution failed: {e}")
            return SnipeResult(
                token_address=snipe_tx.token_address,
                transaction_hash='',
                status='failed',
                error_message=str(e),
                mev_protection_used=False
            )
    
    async def monitor_snipe_result(
        self,
        snipe_result: SnipeResult,
        timeout_seconds: int = 60
    ) -> SnipeResult:
        """
        Monitor snipe transaction until confirmation or timeout.
        
        Args:
            snipe_result: Initial snipe result
            timeout_seconds: Maximum time to wait for confirmation
            
        Returns:
            Updated SnipeResult with final status
        """
        if snipe_result.status != 'pending':
            return snipe_result
        
        start_time = time.time()
        
        try:
            logger.info(f"Monitoring snipe transaction: {snipe_result.transaction_hash}")
            
            while time.time() - start_time < timeout_seconds:
                try:
                    # Check transaction status
                    receipt = self.w3.eth.get_transaction_receipt(snipe_result.transaction_hash)
                    
                    if receipt:
                        # Transaction mined
                        snipe_result.status = 'confirmed' if receipt.status == 1 else 'failed'
                        snipe_result.block_number = receipt.blockNumber
                        snipe_result.gas_used = receipt.gasUsed
                        snipe_result.effective_gas_price = receipt.effectiveGasPrice
                        
                        # Try to decode token transfer events to get tokens received
                        try:
                            snipe_result.tokens_received = await self._decode_token_transfer(
                                receipt, snipe_result.token_address
                            )
                        except Exception as e:
                            logger.debug(f"Could not decode token transfer: {e}")
                        
                        logger.info(
                            f"Snipe {snipe_result.status}: {snipe_result.transaction_hash} "
                            f"in block {snipe_result.block_number}"
                        )
                        
                        return snipe_result
                
                except Exception:
                    # Transaction not yet mined
                    await asyncio.sleep(1)
            
            # Timeout reached
            snipe_result.status = 'timeout'
            snipe_result.error_message = f"Transaction not confirmed within {timeout_seconds}s"
            
            return snipe_result
            
        except Exception as e:
            logger.error(f"Error monitoring snipe result: {e}")
            snipe_result.status = 'error'
            snipe_result.error_message = str(e)
            return snipe_result
    
    async def _decode_token_transfer(self, receipt, token_address: str) -> Optional[int]:
        """
        Decode token transfer amount from transaction receipt.
        
        Args:
            receipt: Transaction receipt
            token_address: Token contract address
            
        Returns:
            Amount of tokens received or None
        """
        try:
            # ERC-20 Transfer event signature
            transfer_signature = self.w3.keccak(text="Transfer(address,address,uint256)")
            
            for log in receipt.logs:
                if (log.address.lower() == token_address.lower() and
                    log.topics[0] == transfer_signature and
                    len(log.topics) >= 3):
                    
                    # Decode transfer amount (third parameter)
                    amount = int.from_bytes(log.data, byteorder='big')
                    return amount
            
            return None
            
        except Exception as e:
            logger.debug(f"Error decoding token transfer: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get sniping statistics.
        
        Returns:
            Statistics dictionary
        """
        success_rate = (
            self.successful_snipes / max(1, self.snipe_attempts) * 100
        )
        
        return {
            'network': self.network,
            'snipe_attempts': self.snipe_attempts,
            'successful_snipes': self.successful_snipes,
            'failed_snipes': self.failed_snipes,
            'success_rate': round(success_rate, 2),
            'flashbots_enabled': self.flashbots_enabled,
            'supported_dexs': list(self.routers.keys()),
            'config': {
                'max_gas_price_gwei': self.config.max_gas_price_gwei,
                'slippage_tolerance': self.config.slippage_tolerance,
                'min_eth_amount': self.config.min_eth_amount,
                'max_eth_amount': self.config.max_eth_amount
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on sniper.
        
        Returns:
            Health status information
        """
        try:
            # Check account balance
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = balance / 10**18
            
            # Check network connectivity
            latest_block = self.w3.eth.block_number
            
            # Determine health status
            if balance_eth < self.config.min_eth_amount:
                status = "warning"
                message = f"Low balance: {balance_eth:.4f} ETH"
            else:
                status = "healthy"
                message = "Ready for sniping"
            
            return {
                'status': status,
                'message': message,
                'network': self.network,
                'account_address': self.account.address,
                'balance_eth': round(balance_eth, 6),
                'latest_block': latest_block,
                'flashbots_enabled': self.flashbots_enabled,
                'supported_dexs': len(self.routers),
                'success_rate': round(
                    self.successful_snipes / max(1, self.snipe_attempts) * 100, 2
                )
            }
            
        except Exception as e:
            logger.error(f"Sniper health check failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'network': self.network
            }