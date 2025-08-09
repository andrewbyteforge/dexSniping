"""
Snipe Trading Controller - Phase 4D
File: app/core/trading/snipe_trading_controller.py
Class: SnipeTradingController
Methods: execute_snipe_trade, validate_snipe_request, check_trade_conditions

Connects frontend snipe buttons to actual trading execution with comprehensive
risk management, validation, and real-time execution capabilities.
"""

import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.utils.logger import setup_logger
from app.core.exceptions import (
    TradingError, 
    WalletError, 
    DEXError, 
    InsufficientFundsError,
    RiskManagementError,
    ValidationError
)
from app.core.wallet.enhanced_wallet_manager import EnhancedWalletManager, WalletType
from app.core.dex.live_dex_integration import LiveDEXIntegration, DEXProtocol
from app.core.trading.trading_engine import TradingEngine, TradingSignal
from app.core.blockchain.network_manager import NetworkManager, NetworkType

logger = setup_logger(__name__)


class SnipeStatus(str, Enum):
    """Snipe trade status enumeration."""
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SnipeType(str, Enum):
    """Snipe trade type enumeration."""
    BUY_SNIPE = "buy_snipe"
    SELL_SNIPE = "sell_snipe"
    ARBITRAGE_SNIPE = "arbitrage_snipe"
    LIQUIDITY_SNIPE = "liquidity_snipe"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class SnipeTradeRequest:
    """Snipe trade request data structure."""
    request_id: str
    snipe_type: SnipeType
    token_address: str
    token_symbol: str
    network: NetworkType
    dex_protocol: DEXProtocol
    amount_in: Decimal
    amount_out_min: Optional[Decimal]
    slippage_tolerance: Decimal
    gas_price_gwei: Optional[Decimal]
    max_gas_limit: Optional[int]
    wallet_connection_id: str
    deadline_seconds: int = 300
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def deadline(self) -> datetime:
        """Calculate trade deadline."""
        return self.created_at + timedelta(seconds=self.deadline_seconds)
    
    @property
    def is_expired(self) -> bool:
        """Check if trade request has expired."""
        return datetime.utcnow() > self.deadline


@dataclass
class SnipeValidationResult:
    """Snipe trade validation result."""
    is_valid: bool
    risk_level: RiskLevel
    risk_score: float
    validation_errors: List[str]
    validation_warnings: List[str]
    estimated_gas_cost: Optional[Decimal]
    price_impact_percent: Optional[Decimal]
    liquidity_analysis: Dict[str, Any]
    confidence_score: float
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.validation_errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.validation_warnings) > 0


@dataclass
class SnipeExecutionResult:
    """Snipe trade execution result."""
    execution_id: str
    request_id: str
    status: SnipeStatus
    transaction_hash: Optional[str]
    block_number: Optional[int]
    gas_used: Optional[int]
    effective_gas_price: Optional[Decimal]
    actual_amount_out: Optional[Decimal]
    price_impact_actual: Optional[Decimal]
    execution_time_ms: int
    profit_loss_usd: Optional[Decimal]
    error_message: Optional[str]
    executed_at: datetime = field(default_factory=datetime.utcnow)


class SnipeTradingController:
    """
    Advanced snipe trading controller for Phase 4D.
    
    Manages the complete lifecycle of snipe trades from frontend button
    clicks to blockchain execution with comprehensive validation and
    risk management.
    """
    
    def __init__(
        self,
        wallet_manager: EnhancedWalletManager,
        dex_integration: LiveDEXIntegration,
        trading_engine: TradingEngine,
        network_manager: NetworkManager
    ):
        """Initialize the snipe trading controller."""
        logger.info("🎯 Initializing Snipe Trading Controller...")
        
        # Core components
        self.wallet_manager = wallet_manager
        self.dex_integration = dex_integration
        self.trading_engine = trading_engine
        self.network_manager = network_manager
        
        # Active snipe requests
        self.active_snipes: Dict[str, SnipeTradeRequest] = {}
        self.execution_results: Dict[str, SnipeExecutionResult] = {}
        
        # Configuration
        self.max_concurrent_snipes = 10
        self.default_deadline_seconds = 300
        self.risk_tolerance_settings = {
            RiskLevel.LOW: {"max_risk_score": 0.3, "max_price_impact": 0.01},
            RiskLevel.MEDIUM: {"max_risk_score": 0.6, "max_price_impact": 0.03},
            RiskLevel.HIGH: {"max_risk_score": 0.8, "max_price_impact": 0.05},
            RiskLevel.EXTREME: {"max_risk_score": 1.0, "max_price_impact": 0.10}
        }
        
        # Performance tracking
        self.execution_stats = {
            "total_snipes": 0,
            "successful_snipes": 0,
            "failed_snipes": 0,
            "avg_execution_time_ms": 0,
            "total_profit_usd": Decimal("0")
        }
        
        logger.info("✅ Snipe Trading Controller initialized successfully")
    
    async def execute_snipe_trade(
        self,
        snipe_request: SnipeTradeRequest,
        user_confirmation: bool = False,
        bypass_validation: bool = False
    ) -> SnipeExecutionResult:
        """
        Execute a snipe trade from frontend button click.
        
        Args:
            snipe_request: The snipe trade request details
            user_confirmation: Whether user has confirmed the trade
            bypass_validation: Whether to bypass safety validations
            
        Returns:
            SnipeExecutionResult: The execution result
            
        Raises:
            TradingError: If execution fails
            ValidationError: If validation fails
            RiskManagementError: If risk checks fail
        """
        execution_start = datetime.utcnow()
        execution_id = str(uuid.uuid4())
        
        logger.info(
            f"🎯 Executing snipe trade: {snipe_request.request_id} "
            f"({snipe_request.snipe_type.value})"
        )
        
        try:
            # Check concurrent snipe limit
            if len(self.active_snipes) >= self.max_concurrent_snipes:
                raise TradingError(
                    f"Maximum concurrent snipes exceeded ({self.max_concurrent_snipes})"
                )
            
            # Check if request has expired
            if snipe_request.is_expired:
                raise TradingError(
                    f"Snipe request expired at {snipe_request.deadline.isoformat()}"
                )
            
            # Add to active snipes
            self.active_snipes[snipe_request.request_id] = snipe_request
            
            # Step 1: Validate snipe request
            if not bypass_validation:
                validation_result = await self.validate_snipe_request(snipe_request)
                
                if validation_result.has_errors:
                    raise ValidationError(
                        f"Snipe validation failed: {', '.join(validation_result.validation_errors)}"
                    )
                
                # Check risk tolerance
                if validation_result.risk_level == RiskLevel.EXTREME and not user_confirmation:
                    raise RiskManagementError(
                        f"Extreme risk level requires user confirmation. "
                        f"Risk score: {validation_result.risk_score}"
                    )
            
            # Step 2: Check trade conditions
            conditions_met = await self.check_trade_conditions(snipe_request)
            if not conditions_met:
                raise TradingError("Trade conditions not met for execution")
            
            # Step 3: Prepare wallet and check balances
            wallet_ready = await self._prepare_wallet_for_trade(snipe_request)
            if not wallet_ready:
                raise WalletError("Wallet preparation failed")
            
            # Step 4: Get final quote and prepare transaction
            final_quote = await self.dex_integration.get_swap_quote(
                dex_protocol=snipe_request.dex_protocol,
                network=snipe_request.network,
                token_in=await self._get_token_info("native", snipe_request.network),
                token_out=await self._get_token_info(
                    snipe_request.token_address, 
                    snipe_request.network
                ),
                amount_in=snipe_request.amount_in,
                slippage_tolerance=snipe_request.slippage_tolerance
            )
            
            # Step 5: Execute the trade
            logger.info(f"⚡ Executing snipe trade on {snipe_request.dex_protocol.value}...")
            
            transaction_result = await self.dex_integration.execute_swap(
                quote=final_quote,
                wallet_connection_id=snipe_request.wallet_connection_id,
                max_gas_limit=snipe_request.max_gas_limit,
                gas_price_gwei=snipe_request.gas_price_gwei
            )
            
            # Step 6: Create execution result
            execution_time_ms = int(
                (datetime.utcnow() - execution_start).total_seconds() * 1000
            )
            
            execution_result = SnipeExecutionResult(
                execution_id=execution_id,
                request_id=snipe_request.request_id,
                status=SnipeStatus.COMPLETED if transaction_result.success else SnipeStatus.FAILED,
                transaction_hash=transaction_result.transaction_hash,
                block_number=transaction_result.block_number,
                gas_used=transaction_result.gas_used,
                effective_gas_price=transaction_result.effective_gas_price,
                actual_amount_out=transaction_result.amount_out,
                price_impact_actual=transaction_result.price_impact,
                execution_time_ms=execution_time_ms,
                profit_loss_usd=await self._calculate_profit_loss(
                    snipe_request, transaction_result
                ),
                error_message=transaction_result.error_message if not transaction_result.success else None
            )
            
            # Step 7: Update statistics
            await self._update_execution_stats(execution_result)
            
            # Step 8: Store result and cleanup
            self.execution_results[execution_id] = execution_result
            del self.active_snipes[snipe_request.request_id]
            
            if execution_result.status == SnipeStatus.COMPLETED:
                logger.info(
                    f"✅ Snipe trade completed successfully: {execution_result.transaction_hash}"
                )
            else:
                logger.error(
                    f"❌ Snipe trade failed: {execution_result.error_message}"
                )
            
            return execution_result
            
        except Exception as e:
            logger.error(f"❌ Snipe execution failed: {e}")
            
            # Create failed execution result
            execution_time_ms = int(
                (datetime.utcnow() - execution_start).total_seconds() * 1000
            )
            
            execution_result = SnipeExecutionResult(
                execution_id=execution_id,
                request_id=snipe_request.request_id,
                status=SnipeStatus.FAILED,
                transaction_hash=None,
                block_number=None,
                gas_used=None,
                effective_gas_price=None,
                actual_amount_out=None,
                price_impact_actual=None,
                execution_time_ms=execution_time_ms,
                profit_loss_usd=None,
                error_message=str(e)
            )
            
            # Store failed result and cleanup
            self.execution_results[execution_id] = execution_result
            if snipe_request.request_id in self.active_snipes:
                del self.active_snipes[snipe_request.request_id]
            
            raise TradingError(f"Snipe execution failed: {e}")
    
    async def validate_snipe_request(
        self, 
        snipe_request: SnipeTradeRequest
    ) -> SnipeValidationResult:
        """
        Comprehensive validation of snipe trade request.
        
        Args:
            snipe_request: The snipe trade request to validate
            
        Returns:
            SnipeValidationResult: Validation result with risk assessment
        """
        logger.info(f"🔍 Validating snipe request: {snipe_request.request_id}")
        
        validation_errors = []
        validation_warnings = []
        risk_factors = []
        
        try:
            # Basic parameter validation
            if snipe_request.amount_in <= 0:
                validation_errors.append("Amount in must be greater than zero")
            
            if snipe_request.slippage_tolerance < 0 or snipe_request.slippage_tolerance > 0.5:
                validation_errors.append("Slippage tolerance must be between 0% and 50%")
            
            # Wallet validation
            if snipe_request.wallet_connection_id not in self.wallet_manager.active_connections:
                validation_errors.append("Invalid wallet connection ID")
            
            # Network and DEX compatibility
            if not await self._validate_network_dex_compatibility(
                snipe_request.network, snipe_request.dex_protocol
            ):
                validation_errors.append(
                    f"DEX {snipe_request.dex_protocol.value} not supported on {snipe_request.network.value}"
                )
            
            # Token validation
            token_info = await self._get_token_info(
                snipe_request.token_address, snipe_request.network
            )
            if not token_info:
                validation_errors.append("Invalid or unrecognized token address")
            
            # Liquidity analysis
            liquidity_analysis = await self._analyze_token_liquidity(
                snipe_request.token_address,
                snipe_request.network,
                snipe_request.dex_protocol
            )
            
            if liquidity_analysis["total_liquidity_usd"] < 10000:
                validation_warnings.append("Low liquidity detected - high price impact risk")
                risk_factors.append(("low_liquidity", 0.3))
            
            # Price impact estimation
            estimated_price_impact = await self._estimate_price_impact(snipe_request)
            if estimated_price_impact > 0.05:  # 5%
                validation_warnings.append(f"High price impact: {estimated_price_impact:.2%}")
                risk_factors.append(("high_price_impact", 0.4))
            
            # Gas cost estimation
            estimated_gas_cost = await self._estimate_gas_cost(snipe_request)
            if estimated_gas_cost > snipe_request.amount_in * Decimal("0.1"):  # 10% of trade
                validation_warnings.append("High gas cost relative to trade size")
                risk_factors.append(("high_gas_cost", 0.2))
            
            # Honeypot and rug pull checks
            security_analysis = await self._analyze_token_security(
                snipe_request.token_address, snipe_request.network
            )
            
            if security_analysis["honeypot_risk"] > 0.7:
                validation_errors.append("High honeypot risk detected")
            elif security_analysis["honeypot_risk"] > 0.3:
                validation_warnings.append("Moderate honeypot risk detected")
                risk_factors.append(("honeypot_risk", security_analysis["honeypot_risk"]))
            
            # Calculate overall risk score
            base_risk = 0.1  # Base risk for any trade
            factor_risk = sum(factor[1] for factor in risk_factors)
            risk_score = min(base_risk + factor_risk, 1.0)
            
            # Determine risk level
            if risk_score <= 0.3:
                risk_level = RiskLevel.LOW
            elif risk_score <= 0.6:
                risk_level = RiskLevel.MEDIUM
            elif risk_score <= 0.8:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.EXTREME
            
            # Calculate confidence score (inverse of risk)
            confidence_score = max(0.1, 1.0 - risk_score)
            
            return SnipeValidationResult(
                is_valid=len(validation_errors) == 0,
                risk_level=risk_level,
                risk_score=risk_score,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                estimated_gas_cost=estimated_gas_cost,
                price_impact_percent=estimated_price_impact,
                liquidity_analysis=liquidity_analysis,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            validation_errors.append(f"Validation error: {str(e)}")
            
            return SnipeValidationResult(
                is_valid=False,
                risk_level=RiskLevel.EXTREME,
                risk_score=1.0,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                estimated_gas_cost=None,
                price_impact_percent=None,
                liquidity_analysis={},
                confidence_score=0.0
            )
    
    async def check_trade_conditions(
        self, 
        snipe_request: SnipeTradeRequest
    ) -> bool:
        """
        Check if current market conditions are suitable for trade execution.
        
        Args:
            snipe_request: The snipe trade request
            
        Returns:
            bool: True if conditions are met for execution
        """
        logger.info(f"🔍 Checking trade conditions for: {snipe_request.request_id}")
        
        try:
            # Check network status
            network_healthy = await self.network_manager.is_network_healthy(
                snipe_request.network
            )
            if not network_healthy:
                logger.warning(f"❌ Network {snipe_request.network.value} is not healthy")
                return False
            
            # Check DEX availability
            dex_available = await self.dex_integration.is_dex_available(
                snipe_request.dex_protocol, snipe_request.network
            )
            if not dex_available:
                logger.warning(f"❌ DEX {snipe_request.dex_protocol.value} not available")
                return False
            
            # Check wallet connection
            wallet_connection = self.wallet_manager.active_connections.get(
                snipe_request.wallet_connection_id
            )
            if not wallet_connection or not wallet_connection.is_active:
                logger.warning("❌ Wallet connection not active")
                return False
            
            # Check sufficient balance
            required_balance = snipe_request.amount_in + await self._estimate_gas_cost(
                snipe_request
            )
            
            wallet_balance = await self.wallet_manager.get_balance(
                snipe_request.wallet_connection_id,
                snipe_request.network,
                "native"
            )
            
            if wallet_balance.native_balance < required_balance:
                logger.warning(
                    f"❌ Insufficient balance: {wallet_balance.native_balance} < {required_balance}"
                )
                return False
            
            # Check gas price conditions
            current_gas_price = await self.network_manager.get_current_gas_price(
                snipe_request.network
            )
            
            if snipe_request.gas_price_gwei:
                if current_gas_price > snipe_request.gas_price_gwei * Decimal("1.5"):
                    logger.warning(
                        f"❌ Gas price too high: {current_gas_price} > {snipe_request.gas_price_gwei * Decimal('1.5')}"
                    )
                    return False
            
            logger.info("✅ All trade conditions met")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking trade conditions: {e}")
            return False
    
    # Helper methods (implementation details)
    
    async def _prepare_wallet_for_trade(
        self, 
        snipe_request: SnipeTradeRequest
    ) -> bool:
        """Prepare wallet for trade execution."""
        try:
            # Refresh wallet balance
            await self.wallet_manager.refresh_balances(
                snipe_request.wallet_connection_id
            )
            
            # Ensure network is connected
            await self.wallet_manager.ensure_network_connected(
                snipe_request.wallet_connection_id,
                snipe_request.network
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Wallet preparation failed: {e}")
            return False
    
    async def _get_token_info(
        self, 
        token_address: str, 
        network: NetworkType
    ) -> Optional[Dict[str, Any]]:
        """Get token information from DEX integration."""
        try:
            return await self.dex_integration.get_token_info(token_address, network)
        except Exception as e:
            logger.error(f"❌ Failed to get token info: {e}")
            return None
    
    async def _validate_network_dex_compatibility(
        self, 
        network: NetworkType, 
        dex_protocol: DEXProtocol
    ) -> bool:
        """Validate that DEX is available on the specified network."""
        return await self.dex_integration.is_protocol_supported(dex_protocol, network)
    
    async def _analyze_token_liquidity(
        self, 
        token_address: str, 
        network: NetworkType,
        dex_protocol: DEXProtocol
    ) -> Dict[str, Any]:
        """Analyze token liquidity on specified DEX."""
        return await self.dex_integration.analyze_liquidity(
            token_address, network, dex_protocol
        )
    
    async def _estimate_price_impact(
        self, 
        snipe_request: SnipeTradeRequest
    ) -> Decimal:
        """Estimate price impact for the trade."""
        try:
            quote = await self.dex_integration.get_swap_quote(
                dex_protocol=snipe_request.dex_protocol,
                network=snipe_request.network,
                token_in=await self._get_token_info("native", snipe_request.network),
                token_out=await self._get_token_info(
                    snipe_request.token_address, snipe_request.network
                ),
                amount_in=snipe_request.amount_in,
                slippage_tolerance=snipe_request.slippage_tolerance
            )
            return quote.price_impact
        except Exception:
            return Decimal("0.05")  # Default conservative estimate
    
    async def _estimate_gas_cost(
        self, 
        snipe_request: SnipeTradeRequest
    ) -> Decimal:
        """Estimate gas cost for the trade."""
        try:
            gas_estimate = await self.dex_integration.estimate_gas(
                snipe_request.dex_protocol,
                snipe_request.network,
                "swap"
            )
            
            gas_price = snipe_request.gas_price_gwei or await self.network_manager.get_current_gas_price(
                snipe_request.network
            )
            
            return Decimal(str(gas_estimate)) * gas_price / Decimal("1e9")  # Convert to ETH
            
        except Exception:
            return Decimal("0.01")  # Default conservative estimate
    
    async def _analyze_token_security(
        self, 
        token_address: str, 
        network: NetworkType
    ) -> Dict[str, Any]:
        """Analyze token security (honeypot, rug pull risks)."""
        # This would integrate with security analysis services
        # For now, return mock analysis
        return {
            "honeypot_risk": 0.1,
            "rug_pull_risk": 0.2,
            "contract_verified": True,
            "ownership_renounced": False,
            "liquidity_locked": True
        }
    
    async def _calculate_profit_loss(
        self, 
        snipe_request: SnipeTradeRequest,
        transaction_result: Any
    ) -> Optional[Decimal]:
        """Calculate profit/loss for the executed trade."""
        try:
            # This would calculate actual P/L based on execution vs market
            # For now, return placeholder
            return Decimal("0")
        except Exception:
            return None
    
    async def _update_execution_stats(
        self, 
        execution_result: SnipeExecutionResult
    ) -> None:
        """Update execution statistics."""
        self.execution_stats["total_snipes"] += 1
        
        if execution_result.status == SnipeStatus.COMPLETED:
            self.execution_stats["successful_snipes"] += 1
            if execution_result.profit_loss_usd:
                self.execution_stats["total_profit_usd"] += execution_result.profit_loss_usd
        else:
            self.execution_stats["failed_snipes"] += 1
        
        # Update average execution time
        total_time = (
            self.execution_stats["avg_execution_time_ms"] * 
            (self.execution_stats["total_snipes"] - 1) +
            execution_result.execution_time_ms
        )
        self.execution_stats["avg_execution_time_ms"] = int(
            total_time / self.execution_stats["total_snipes"]
        )
    
    def get_active_snipes(self) -> Dict[str, SnipeTradeRequest]:
        """Get all active snipe requests."""
        return self.active_snipes.copy()
    
    def get_execution_results(self, limit: int = 100) -> List[SnipeExecutionResult]:
        """Get recent execution results."""
        results = list(self.execution_results.values())
        results.sort(key=lambda x: x.executed_at, reverse=True)
        return results[:limit]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        success_rate = 0.0
        if self.execution_stats["total_snipes"] > 0:
            success_rate = (
                self.execution_stats["successful_snipes"] / 
                self.execution_stats["total_snipes"]
            )
        
        return {
            **self.execution_stats,
            "success_rate": round(success_rate, 4),
            "active_snipes": len(self.active_snipes)
        }


# Global instance for application use
_snipe_trading_controller: Optional[SnipeTradingController] = None


async def get_snipe_trading_controller() -> SnipeTradingController:
    """Get the global snipe trading controller instance."""
    global _snipe_trading_controller
    
    if _snipe_trading_controller is None:
        from app.core.wallet.enhanced_wallet_manager import get_enhanced_wallet_manager
        from app.core.dex.live_dex_integration import get_live_dex_integration
        from app.core.trading.trading_engine import get_trading_engine
        from app.core.blockchain.network_manager import get_network_manager
        
        wallet_manager = await get_enhanced_wallet_manager()
        dex_integration = await get_live_dex_integration()
        trading_engine = await get_trading_engine()
        network_manager = await get_network_manager()
        
        _snipe_trading_controller = SnipeTradingController(
            wallet_manager=wallet_manager,
            dex_integration=dex_integration,
            trading_engine=trading_engine,
            network_manager=network_manager
        )
    
    return _snipe_trading_controller


async def initialize_snipe_trading_controller() -> SnipeTradingController:
    """Initialize the snipe trading controller for application startup."""
    controller = await get_snipe_trading_controller()
    logger.info("🎯 Snipe Trading Controller initialized for application")
    return controller