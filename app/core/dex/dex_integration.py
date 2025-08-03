"""
DEX Integration Engine
File: app/core/dex/dex_integration.py

Professional DEX integration system supporting multiple exchanges
with comprehensive trading functionality and error handling.
"""

import asyncio
import json
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import math

try:
    from web3 import Web3
    from web3.contract import Contract
    from eth_abi import encode
    WEB3_AVAILABLE = True
except ImportError:
    # Fallback for testing without Web3
    WEB3_AVAILABLE = False
    Web3 = None
    Contract = None

from app.utils.logger import setup_logger
from app.core.exceptions import (
    DEXError,
    InsufficientLiquidityError,
    SlippageExceededError,
    TransactionError
)

logger = setup_logger(__name__)


class DEXProtocol(str, Enum):
    """Supported DEX protocols."""
    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    PANCAKESWAP = "pancakeswap"
    QUICKSWAP = "quickswap"


class SwapType(str, Enum):
    """Types of swap operations."""
    EXACT_TOKENS_FOR_TOKENS = "exact_tokens_for_tokens"
    TOKENS_FOR_EXACT_TOKENS = "tokens_for_exact_tokens"
    EXACT_ETH_FOR_TOKENS = "exact_eth_for_tokens"
    TOKENS_FOR_EXACT_ETH = "tokens_for_exact_eth"
    EXACT_TOKENS_FOR_ETH = "exact_tokens_for_eth"
    ETH_FOR_EXACT_TOKENS = "eth_for_exact_tokens"


@dataclass
class SwapQuote:
    """Swap quote data structure."""
    input_token: str
    output_token: str
    input_amount: Decimal
    output_amount: Decimal
    expected_output: Decimal
    minimum_output: Decimal
    price_impact: Decimal
    slippage_tolerance: Decimal
    gas_estimate: int
    route: List[str]
    dex_protocol: DEXProtocol
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """Check if quote has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def price_per_token(self) -> Decimal:
        """Calculate price per output token."""
        if self.output_amount == 0:
            return Decimal("0")
        return self.input_amount / self.output_amount


@dataclass
class SwapResult:
    """Swap execution result."""
    transaction_hash: str
    input_amount: Decimal
    output_amount: Decimal
    actual_price_impact: Decimal
    gas_used: int
    effective_gas_price: int
    block_number: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LiquidityInfo:
    """Liquidity pool information."""
    pool_address: str
    token0: str
    token1: str
    token0_symbol: str
    token1_symbol: str
    reserve0: Decimal
    reserve1: Decimal
    total_supply: Decimal
    fee_rate: Decimal
    volume_24h: Decimal
    tvl_usd: Decimal


class DEXIntegration:
    """
    Professional DEX integration system with multi-protocol support.
    
    Provides unified interface for trading across different DEX protocols
    with comprehensive quote comparison, route optimization, and execution.
    """
    
    def __init__(self, web3: Web3, network: str = "ethereum"):
        """Initialize DEX integration."""
        self.web3 = web3
        self.network = network
        self.protocols: Dict[DEXProtocol, Dict[str, Any]] = {}
        self.contracts: Dict[str, Contract] = {}
        
        # Initialize protocol configurations
        self._load_protocol_configs()
        self._load_contracts()
        
        logger.info(f"🔄 DEX Integration initialized for {network}")
    
    def _load_protocol_configs(self) -> None:
        """Load DEX protocol configurations."""
        configs = {
            "ethereum": {
                DEXProtocol.UNISWAP_V2: {
                    "router_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                    "factory_address": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
                    "fee_rate": Decimal("0.003"),  # 0.3%
                    "init_code_hash": "0x96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f"
                },
                DEXProtocol.UNISWAP_V3: {
                    "router_address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                    "factory_address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                    "quoter_address": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
                    "fee_tiers": [100, 500, 3000, 10000]  # 0.01%, 0.05%, 0.3%, 1%
                },
                DEXProtocol.SUSHISWAP: {
                    "router_address": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
                    "factory_address": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
                    "fee_rate": Decimal("0.003")  # 0.3%
                }
            },
            "polygon": {
                DEXProtocol.QUICKSWAP: {
                    "router_address": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
                    "factory_address": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",
                    "fee_rate": Decimal("0.003")
                },
                DEXProtocol.SUSHISWAP: {
                    "router_address": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
                    "factory_address": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
                    "fee_rate": Decimal("0.003")
                }
            },
            "bsc": {
                DEXProtocol.PANCAKESWAP: {
                    "router_address": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
                    "factory_address": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
                    "fee_rate": Decimal("0.0025")  # 0.25%
                }
            }
        }
        
        self.protocols = configs.get(self.network, {})
        
        if not self.protocols:
            raise DEXError(f"No DEX protocols configured for network: {self.network}")
    
    def _load_contracts(self) -> None:
        """Load smart contract instances."""
        # Load common ABI definitions
        router_abi = self._get_uniswap_v2_router_abi()
        factory_abi = self._get_uniswap_v2_factory_abi()
        pair_abi = self._get_uniswap_v2_pair_abi()
        erc20_abi = self._get_erc20_abi()
        
        # Initialize contract instances for each protocol
        for protocol, config in self.protocols.items():
            try:
                router_address = config.get("router_address")
                factory_address = config.get("factory_address")
                
                if router_address:
                    self.contracts[f"{protocol.value}_router"] = self.web3.eth.contract(
                        address=Web3.to_checksum_address(router_address),
                        abi=router_abi
                    )
                
                if factory_address:
                    self.contracts[f"{protocol.value}_factory"] = self.web3.eth.contract(
                        address=Web3.to_checksum_address(factory_address),
                        abi=factory_abi
                    )
                
                logger.debug(f"✅ Loaded contracts for {protocol.value}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to load contracts for {protocol.value}: {e}")
    
    async def get_swap_quote(
        self,
        input_token: str,
        output_token: str,
        input_amount: Decimal,
        slippage_tolerance: Decimal = Decimal("0.01"),
        protocols: Optional[List[DEXProtocol]] = None
    ) -> List[SwapQuote]:
        """
        Get swap quotes from multiple DEX protocols.
        
        Args:
            input_token: Input token address
            output_token: Output token address
            input_amount: Amount of input tokens
            slippage_tolerance: Maximum acceptable slippage
            protocols: Specific protocols to query (optional)
            
        Returns:
            List of swap quotes sorted by best output amount
        """
        try:
            if protocols is None:
                protocols = list(self.protocols.keys())
            
            quotes = []
            
            # Get quotes from each protocol
            quote_tasks = [
                self._get_protocol_quote(
                    protocol, input_token, output_token, 
                    input_amount, slippage_tolerance
                )
                for protocol in protocols
                if protocol in self.protocols
            ]
            
            results = await asyncio.gather(*quote_tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"⚠️ Quote failed for {protocols[i].value}: {result}")
                    continue
                
                if result:
                    quotes.append(result)
            
            # Sort by best output amount (highest first)
            quotes.sort(key=lambda q: q.output_amount, reverse=True)
            
            logger.info(
                f"💱 Got {len(quotes)} quotes for {input_amount} tokens "
                f"- Best: {quotes[0].output_amount:.6f} ({quotes[0].dex_protocol.value})"
                if quotes else "No quotes available"
            )
            
            return quotes
            
        except Exception as e:
            logger.error(f"❌ Failed to get swap quotes: {e}")
            raise DEXError(f"Quote retrieval failed: {e}")
    
    async def _get_protocol_quote(
        self,
        protocol: DEXProtocol,
        input_token: str,
        output_token: str,
        input_amount: Decimal,
        slippage_tolerance: Decimal
    ) -> Optional[SwapQuote]:
        """Get quote from specific protocol."""
        try:
            if protocol == DEXProtocol.UNISWAP_V2:
                return await self._get_uniswap_v2_quote(
                    input_token, output_token, input_amount, slippage_tolerance
                )
            elif protocol == DEXProtocol.UNISWAP_V3:
                return await self._get_uniswap_v3_quote(
                    input_token, output_token, input_amount, slippage_tolerance
                )
            elif protocol in [DEXProtocol.SUSHISWAP, DEXProtocol.QUICKSWAP, DEXProtocol.PANCAKESWAP]:
                # These use Uniswap V2 compatible interface
                return await self._get_uniswap_v2_compatible_quote(
                    protocol, input_token, output_token, input_amount, slippage_tolerance
                )
            else:
                logger.warning(f"⚠️ Unsupported protocol: {protocol.value}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Protocol quote failed for {protocol.value}: {e}")
            return None
    
    async def _get_uniswap_v2_quote(
        self,
        input_token: str,
        output_token: str,
        input_amount: Decimal,
        slippage_tolerance: Decimal
    ) -> SwapQuote:
        """Get Uniswap V2 quote."""
        try:
            router = self.contracts["uniswap_v2_router"]
            
            # Convert amount to wei
            input_amount_wei = int(input_amount * 10**18)  # Assuming 18 decimals
            
            # Get amounts out
            path = [
                Web3.to_checksum_address(input_token),
                Web3.to_checksum_address(output_token)
            ]
            
            amounts_out = await router.functions.getAmountsOut(
                input_amount_wei, path
            ).call()
            
            output_amount_wei = amounts_out[-1]
            output_amount = Decimal(output_amount_wei) / 10**18
            
            # Calculate minimum output with slippage
            minimum_output = output_amount * (Decimal("1") - slippage_tolerance)
            
            # Estimate gas
            gas_estimate = 150000  # Conservative estimate for V2 swap
            
            # Calculate price impact (simplified)
            price_impact = await self._calculate_price_impact_v2(
                input_token, output_token, input_amount, output_amount
            )
            
            return SwapQuote(
                input_token=input_token,
                output_token=output_token,
                input_amount=input_amount,
                output_amount=output_amount,
                expected_output=output_amount,
                minimum_output=minimum_output,
                price_impact=price_impact,
                slippage_tolerance=slippage_tolerance,
                gas_estimate=gas_estimate,
                route=path,
                dex_protocol=DEXProtocol.UNISWAP_V2,
                expires_at=datetime.utcnow() + timedelta(minutes=2)
            )
            
        except Exception as e:
            logger.error(f"❌ Uniswap V2 quote failed: {e}")
            raise DEXError(f"Uniswap V2 quote failed: {e}")
    
    async def _get_uniswap_v2_compatible_quote(
        self,
        protocol: DEXProtocol,
        input_token: str,
        output_token: str,
        input_amount: Decimal,
        slippage_tolerance: Decimal
    ) -> SwapQuote:
        """Get quote from Uniswap V2 compatible protocol."""
        try:
            router = self.contracts[f"{protocol.value}_router"]
            
            # Convert amount to wei
            input_amount_wei = int(input_amount * 10**18)
            
            # Get amounts out
            path = [
                Web3.to_checksum_address(input_token),
                Web3.to_checksum_address(output_token)
            ]
            
            amounts_out = await router.functions.getAmountsOut(
                input_amount_wei, path
            ).call()
            
            output_amount_wei = amounts_out[-1]
            output_amount = Decimal(output_amount_wei) / 10**18
            
            # Calculate minimum output with slippage
            minimum_output = output_amount * (Decimal("1") - slippage_tolerance)
            
            # Estimate gas
            gas_estimate = 150000
            
            # Calculate price impact
            price_impact = await self._calculate_price_impact_v2(
                input_token, output_token, input_amount, output_amount
            )
            
            return SwapQuote(
                input_token=input_token,
                output_token=output_token,
                input_amount=input_amount,
                output_amount=output_amount,
                expected_output=output_amount,
                minimum_output=minimum_output,
                price_impact=price_impact,
                slippage_tolerance=slippage_tolerance,
                gas_estimate=gas_estimate,
                route=path,
                dex_protocol=protocol,
                expires_at=datetime.utcnow() + timedelta(minutes=2)
            )
            
        except Exception as e:
            logger.error(f"❌ {protocol.value} quote failed: {e}")
            raise DEXError(f"{protocol.value} quote failed: {e}")
    
    async def _get_uniswap_v3_quote(
        self,
        input_token: str,
        output_token: str,
        input_amount: Decimal,
        slippage_tolerance: Decimal
    ) -> SwapQuote:
        """Get Uniswap V3 quote."""
        # TODO: Implement Uniswap V3 quoter integration
        # This requires more complex logic due to concentrated liquidity
        logger.warning("⚠️ Uniswap V3 quotes not yet implemented")
        return None
    
    async def execute_swap(
        self,
        quote: SwapQuote,
        wallet_address: str,
        private_key: Optional[str] = None
    ) -> SwapResult:
        """
        Execute a swap based on a quote.
        
        Args:
            quote: The swap quote to execute
            wallet_address: Wallet address executing the swap
            private_key: Private key for signing (if available)
            
        Returns:
            SwapResult with execution details
        """
        try:
            if quote.is_expired:
                raise DEXError("Quote has expired - please get a new quote")
            
            # Get the appropriate router contract
            router = self.contracts[f"{quote.dex_protocol.value}_router"]
            
            # Build transaction based on swap type
            transaction = await self._build_swap_transaction(
                quote, wallet_address, router
            )
            
            # Sign and send transaction
            if private_key:
                signed_txn = self.web3.eth.account.sign_transaction(
                    transaction, private_key
                )
                tx_hash = await self.web3.eth.send_raw_transaction(
                    signed_txn.rawTransaction
                )
            else:
                # Return transaction for external signing
                return {
                    "transaction": transaction,
                    "requires_signing": True
                }
            
            # Wait for confirmation
            receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse result from transaction logs
            actual_output = await self._parse_swap_result(receipt, quote)
            
            result = SwapResult(
                transaction_hash=tx_hash.hex(),
                input_amount=quote.input_amount,
                output_amount=actual_output,
                actual_price_impact=((quote.input_amount / actual_output) - quote.price_per_token) / quote.price_per_token * 100,
                gas_used=receipt.gasUsed,
                effective_gas_price=receipt.effectiveGasPrice,
                block_number=receipt.blockNumber
            )
            
            logger.info(
                f"✅ Swap executed: {quote.input_amount} -> {actual_output} "
                f"({quote.dex_protocol.value}) - TX: {tx_hash.hex()[:10]}..."
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Swap execution failed: {e}")
            raise DEXError(f"Swap execution failed: {e}")
    
    async def _build_swap_transaction(
        self,
        quote: SwapQuote,
        wallet_address: str,
        router: Contract
    ) -> Dict[str, Any]:
        """Build swap transaction."""
        try:
            # Convert amounts to wei
            input_amount_wei = int(quote.input_amount * 10**18)
            minimum_output_wei = int(quote.minimum_output * 10**18)
            
            # Set deadline (10 minutes from now)
            deadline = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
            
            # Build function call based on token types
            if quote.input_token == "0x0000000000000000000000000000000000000000":
                # ETH to token swap
                function_call = router.functions.swapExactETHForTokens(
                    minimum_output_wei,
                    quote.route,
                    Web3.to_checksum_address(wallet_address),
                    deadline
                )
                value = input_amount_wei
            elif quote.output_token == "0x0000000000000000000000000000000000000000":
                # Token to ETH swap
                function_call = router.functions.swapExactTokensForETH(
                    input_amount_wei,
                    minimum_output_wei,
                    quote.route,
                    Web3.to_checksum_address(wallet_address),
                    deadline
                )
                value = 0
            else:
                # Token to token swap
                function_call = router.functions.swapExactTokensForTokens(
                    input_amount_wei,
                    minimum_output_wei,
                    quote.route,
                    Web3.to_checksum_address(wallet_address),
                    deadline
                )
                value = 0
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': Web3.to_checksum_address(wallet_address),
                'value': value,
                'gas': quote.gas_estimate,
                'gasPrice': await self.web3.eth.gas_price,
                'nonce': await self.web3.eth.get_transaction_count(wallet_address)
            })
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Failed to build swap transaction: {e}")
            raise DEXError(f"Transaction building failed: {e}")
    
    async def _calculate_price_impact_v2(
        self,
        input_token: str,
        output_token: str,
        input_amount: Decimal,
        output_amount: Decimal
    ) -> Decimal:
        """Calculate price impact for V2 style swap."""
        try:
            # Get pair reserves
            pair_address = await self._get_pair_address(input_token, output_token)
            if not pair_address:
                return Decimal("0")
            
            # This is a simplified calculation
            # In production, you'd want more sophisticated price impact calculation
            return Decimal("0.1")  # Placeholder 0.1%
            
        except Exception:
            return Decimal("0")
    
    async def _get_pair_address(self, token0: str, token1: str) -> Optional[str]:
        """Get pair address for two tokens."""
        try:
            factory = self.contracts["uniswap_v2_factory"]
            pair_address = await factory.functions.getPair(
                Web3.to_checksum_address(token0),
                Web3.to_checksum_address(token1)
            ).call()
            
            if pair_address == "0x0000000000000000000000000000000000000000":
                return None
            
            return pair_address
            
        except Exception:
            return None
    
    async def _parse_swap_result(self, receipt, quote: SwapQuote) -> Decimal:
        """Parse actual output amount from transaction receipt."""
        # TODO: Implement log parsing to get actual swap amounts
        # For now, return expected output
        return quote.expected_output
    
    def _get_uniswap_v2_router_abi(self) -> List[Dict]:
        """Get Uniswap V2 Router ABI."""
        return [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForTokens",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            }
            # Add more ABI entries as needed
        ]
    
    def _get_uniswap_v2_factory_abi(self) -> List[Dict]:
        """Get Uniswap V2 Factory ABI."""
        return [
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenA", "type": "address"},
                    {"internalType": "address", "name": "tokenB", "type": "address"}
                ],
                "name": "getPair",
                "outputs": [
                    {"internalType": "address", "name": "pair", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _get_uniswap_v2_pair_abi(self) -> List[Dict]:
        """Get Uniswap V2 Pair ABI."""
        return [
            {
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
                    {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
                    {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _get_erc20_abi(self) -> List[Dict]:
        """Get ERC20 token ABI."""
        return [
            {
                "inputs": [
                    {"internalType": "address", "name": "spender", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [
                    {"internalType": "bool", "name": "", "type": "bool"}
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "account", "type": "address"}
                ],
                "name": "balanceOf",
                "outputs": [
                    {"internalType": "uint256", "name": "", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]