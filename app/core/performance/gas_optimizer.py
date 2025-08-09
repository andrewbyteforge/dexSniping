Add this
"""
Gas Optimization Engine
File: app/core/performance/gas_optimizer.py

Advanced gas optimization system for minimizing transaction costs
while ensuring optimal execution speed and reliability.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta
import statistics

from app.utils.logger import setup_logger
from app.core.exceptions import PerformanceError, NetworkError, GasOptimizationError

logger = setup_logger(__name__)


class GasStrategy(Enum):
    """Gas optimization strategies."""
    ECONOMY = "economy"
    STANDARD = "standard"
    FAST = "fast"
    PRIORITY = "priority"
    ADAPTIVE = "adaptive"


class GasPriceType(Enum):
    """Gas price types."""
    LEGACY = "legacy"
    EIP1559 = "eip1559"


@dataclass
class GasPrice:
    """Gas price data structure."""
    base_fee: Decimal
    priority_fee: Decimal
    max_fee: Decimal
    gas_limit: int
    price_type: GasPriceType
    network: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_cost_wei(self) -> int:
        """Calculate total gas cost in wei."""
        return int(self.max_fee * self.gas_limit)
    
    @property
    def total_cost_eth(self) -> float:
        """Calculate total gas cost in ETH."""
        return float(self.total_cost_wei / 1e18)


@dataclass
class GasOptimizationResult:
    """Gas optimization result."""
    original_gas_price: GasPrice
    optimized_gas_price: GasPrice
    savings_wei: int
    savings_percentage: float
    confidence_score: float
    strategy_used: GasStrategy
    optimization_timestamp: datetime = field(default_factory=datetime.utcnow)


class GasOptimizationEngine:
    """
    Advanced gas optimization engine with multiple strategies.
    
    Features:
    - Real-time gas price monitoring
    - Multiple optimization strategies
    - Network congestion analysis
    - Adaptive pricing algorithms
    - EIP-1559 support
    """
    
    def __init__(self, default_strategy: GasStrategy = GasStrategy.STANDARD):
        """
        Initialize gas optimization engine.
        
        Args:
            default_strategy: Default gas optimization strategy
        """
        self.default_strategy = default_strategy
        self.gas_price_history: List[GasPrice] = []
        self.optimization_results: List[GasOptimizationResult] = []
        
        # Strategy configurations
        self.strategy_configs = {
            GasStrategy.ECONOMY: {
                "speed_multiplier": 0.8,
                "max_wait_time": 300,  # 5 minutes
                "confidence_threshold": 0.9
            },
            GasStrategy.STANDARD: {
                "speed_multiplier": 1.0,
                "max_wait_time": 180,  # 3 minutes
                "confidence_threshold": 0.8
            },
            GasStrategy.FAST: {
                "speed_multiplier": 1.3,
                "max_wait_time": 60,   # 1 minute
                "confidence_threshold": 0.7
            },
            GasStrategy.PRIORITY: {
                "speed_multiplier": 1.8,
                "max_wait_time": 30,   # 30 seconds
                "confidence_threshold": 0.6
            },
            GasStrategy.ADAPTIVE: {
                "speed_multiplier": 1.0,
                "max_wait_time": 120,  # 2 minutes
                "confidence_threshold": 0.75
            }
        }
        
        logger.info(f"🔥 GasOptimizationEngine initialized with {default_strategy.value} strategy")
    
    async def optimize_gas_price(
        self,
        transaction_type: str,
        urgency: str = "normal",
        network: str = "ethereum",
        current_gas_price: Optional[GasPrice] = None
    ) -> GasOptimizationResult:
        """
        Optimize gas price for a transaction.
        
        Args:
            transaction_type: Type of transaction (swap, transfer, etc.)
            urgency: Transaction urgency (low, normal, high, critical)
            network: Blockchain network
            current_gas_price: Current gas price data
            
        Returns:
            GasOptimizationResult: Optimization results
        """
        try:
            logger.debug(f"🔧 Optimizing gas for {transaction_type} on {network}")
            
            # Get current network gas prices
            if current_gas_price is None:
                current_gas_price = await self._get_current_gas_price(network)
            
            # Select optimization strategy based on urgency
            strategy = self._select_strategy(urgency)
            
            # Optimize gas price using selected strategy
            optimized_price = await self._apply_optimization_strategy(
                current_gas_price, strategy, transaction_type
            )
            
            # Calculate savings and confidence
            savings_wei = current_gas_price.total_cost_wei - optimized_price.total_cost_wei
            savings_percentage = (savings_wei / current_gas_price.total_cost_wei) * 100 if current_gas_price.total_cost_wei > 0 else 0
            confidence_score = await self._calculate_confidence_score(optimized_price, strategy)
            
            # Create optimization result
            result = GasOptimizationResult(
                original_gas_price=current_gas_price,
                optimized_gas_price=optimized_price,
                savings_wei=savings_wei,
                savings_percentage=savings_percentage,
                confidence_score=confidence_score,
                strategy_used=strategy
            )
            
            # Store result for analysis
            self.optimization_results.append(result)
            
            logger.debug(f"✅ Gas optimization complete: {savings_percentage:.1f}% savings")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Gas optimization failed: {e}")
            # Return safe fallback
            return await self._create_fallback_result(current_gas_price or await self._get_fallback_gas_price(network))
    
    async def estimate_transaction_cost(
        self,
        gas_limit: int,
        network: str = "ethereum",
        strategy: Optional[GasStrategy] = None
    ) -> Dict[str, Any]:
        """
        Estimate transaction cost with different strategies.
        
        Args:
            gas_limit: Estimated gas limit for transaction
            network: Blockchain network
            strategy: Optimization strategy to use
            
        Returns:
            Dict: Cost estimates for different scenarios
        """
        try:
            strategy = strategy or self.default_strategy
            
            # Get current gas prices
            current_gas_price = await self._get_current_gas_price(network)
            
            # Calculate costs for different strategies
            estimates = {}
            for strat in GasStrategy:
                optimized_price = await self._apply_optimization_strategy(
                    current_gas_price, strat, "estimate"
                )
                optimized_price.gas_limit = gas_limit
                
                estimates[strat.value] = {
                    "cost_wei": optimized_price.total_cost_wei,
                    "cost_eth": optimized_price.total_cost_eth,
                    "cost_usd": optimized_price.total_cost_eth * 2000,  # Mock ETH price
                    "estimated_time": self._estimate_confirmation_time(strat),
                    "gas_price": float(optimized_price.max_fee)
                }
            
            return {
                "network": network,
                "gas_limit": gas_limit,
                "estimates": estimates,
                "recommended_strategy": strategy.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Cost estimation failed: {e}")
            return {"error": str(e)}
    
    async def monitor_gas_prices(self, network: str = "ethereum", duration: int = 300) -> Dict[str, Any]:
        """
        Monitor gas prices over time.
        
        Args:
            network: Blockchain network to monitor
            duration: Monitoring duration in seconds
            
        Returns:
            Dict: Gas price monitoring results
        """
        try:
            logger.info(f"📊 Starting gas price monitoring for {duration}s on {network}")
            
            monitoring_data = []
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(seconds=duration)
            
            while datetime.utcnow() < end_time:
                gas_price = await self._get_current_gas_price(network)
                monitoring_data.append(gas_price)
                
                await asyncio.sleep(30)  # Check every 30 seconds
            
            # Analyze monitoring data
            analysis = await self._analyze_gas_price_trends(monitoring_data)
            
            return {
                "network": network,
                "monitoring_duration": duration,
                "data_points": len(monitoring_data),
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Gas price monitoring failed: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _get_current_gas_price(self, network: str) -> GasPrice:
        """Get current gas price for network."""
        # Mock implementation - in production would fetch from network
        base_fee = Decimal("20") * 1e9  # 20 gwei
        priority_fee = Decimal("2") * 1e9  # 2 gwei
        max_fee = base_fee + priority_fee
        
        return GasPrice(
            base_fee=base_fee,
            priority_fee=priority_fee,
            max_fee=max_fee,
            gas_limit=150000,
            price_type=GasPriceType.EIP1559,
            network=network
        )
    
    async def _get_fallback_gas_price(self, network: str) -> GasPrice:
        """Get safe fallback gas price."""
        return GasPrice(
            base_fee=Decimal("30") * 1e9,  # 30 gwei safe fallback
            priority_fee=Decimal("3") * 1e9,  # 3 gwei
            max_fee=Decimal("33") * 1e9,
            gas_limit=200000,  # Conservative gas limit
            price_type=GasPriceType.EIP1559,
            network=network
        )
    
    def _select_strategy(self, urgency: str) -> GasStrategy:
        """Select optimization strategy based on urgency."""
        urgency_strategy_map = {
            "low": GasStrategy.ECONOMY,
            "normal": GasStrategy.STANDARD,
            "high": GasStrategy.FAST,
            "critical": GasStrategy.PRIORITY
        }
        
        return urgency_strategy_map.get(urgency.lower(), self.default_strategy)
    
    async def _apply_optimization_strategy(
        self,
        current_price: GasPrice,
        strategy: GasStrategy,
        transaction_type: str
    ) -> GasPrice:
        """Apply optimization strategy to gas price."""
        config = self.strategy_configs[strategy]
        multiplier = config["speed_multiplier"]
        
        # Apply strategy-specific adjustments
        if strategy == GasStrategy.ECONOMY:
            # Reduce gas price for economy
            optimized_max_fee = current_price.max_fee * Decimal("0.9")
            optimized_priority_fee = current_price.priority_fee * Decimal("0.8")
        elif strategy == GasStrategy.PRIORITY:
            # Increase gas price for priority
            optimized_max_fee = current_price.max_fee * Decimal("1.5")
            optimized_priority_fee = current_price.priority_fee * Decimal("2.0")
        else:
            # Standard optimization
            optimized_max_fee = current_price.max_fee * Decimal(str(multiplier))
            optimized_priority_fee = current_price.priority_fee * Decimal(str(multiplier))
        
        return GasPrice(
            base_fee=current_price.base_fee,
            priority_fee=optimized_priority_fee,
            max_fee=optimized_max_fee,
            gas_limit=current_price.gas_limit,
            price_type=current_price.price_type,
            network=current_price.network
        )
    
    async def _calculate_confidence_score(self, gas_price: GasPrice, strategy: GasStrategy) -> float:
        """Calculate confidence score for optimized gas price."""
        base_confidence = self.strategy_configs[strategy]["confidence_threshold"]
        
        # Adjust confidence based on recent optimization results
        if len(self.optimization_results) > 0:
            recent_results = self.optimization_results[-10:]  # Last 10 results
            avg_savings = statistics.mean([r.savings_percentage for r in recent_results])
            
            # Higher savings = higher confidence (up to a point)
            confidence_adjustment = min(avg_savings / 100, 0.2)
            return min(base_confidence + confidence_adjustment, 0.95)
        
        return base_confidence
    
    def _estimate_confirmation_time(self, strategy: GasStrategy) -> int:
        """Estimate confirmation time for strategy."""
        time_estimates = {
            GasStrategy.ECONOMY: 300,    # 5 minutes
            GasStrategy.STANDARD: 180,   # 3 minutes
            GasStrategy.FAST: 60,        # 1 minute
            GasStrategy.PRIORITY: 30,    # 30 seconds
            GasStrategy.ADAPTIVE: 120    # 2 minutes
        }
        
        return time_estimates.get(strategy, 180)
    
    async def _analyze_gas_price_trends(self, monitoring_data: List[GasPrice]) -> Dict[str, Any]:
        """Analyze gas price trends from monitoring data."""
        if not monitoring_data:
            return {"error": "No monitoring data available"}
        
        # Extract prices for analysis
        max_fees = [float(gp.max_fee) for gp in monitoring_data]
        priority_fees = [float(gp.priority_fee) for gp in monitoring_data]
        
        # Calculate statistics
        analysis = {
            "max_fee_stats": {
                "min": min(max_fees),
                "max": max(max_fees),
                "avg": statistics.mean(max_fees),
                "median": statistics.median(max_fees),
                "std_dev": statistics.stdev(max_fees) if len(max_fees) > 1 else 0
            },
            "priority_fee_stats": {
                "min": min(priority_fees),
                "max": max(priority_fees),
                "avg": statistics.mean(priority_fees),
                "median": statistics.median(priority_fees),
                "std_dev": statistics.stdev(priority_fees) if len(priority_fees) > 1 else 0
            },
            "trend": "stable",  # Could be "increasing", "decreasing", "volatile"
            "volatility": "low",  # Could be "medium", "high"
            "recommendation": "Gas prices are stable - good time to transact"
        }
        
        return analysis
    
    async def _create_fallback_result(self, gas_price: GasPrice) -> GasOptimizationResult:
        """Create fallback optimization result."""
        return GasOptimizationResult(
            original_gas_price=gas_price,
            optimized_gas_price=gas_price,
            savings_wei=0,
            savings_percentage=0.0,
            confidence_score=0.5,
            strategy_used=GasStrategy.STANDARD
        )


# Export main classes
__all__ = [
    "GasOptimizationEngine",
    "GasStrategy",
    "GasPrice",
    "GasPriceType",
    "GasOptimizationResult"
]


to this
"""
Enhanced Gas Optimization Engine
File: app/core/performance/gas_optimizer.py

Advanced gas optimization system combining multiple strategies for minimizing
transaction costs while ensuring optimal execution speed and reliability.
Features intelligent timing, personal usage tracking, and multi-network support.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta
import statistics
import aiohttp

from app.utils.logger import setup_logger
from app.core.blockchain.network_manager import get_network_manager, NetworkType
from app.core.exceptions import PerformanceError, NetworkError, GasOptimizationError

logger = setup_logger(__name__)


class GasStrategy(Enum):
    """Gas optimization strategies."""
    ECONOMY = "economy"      # Maximum savings, slower execution
    SLOW = "slow"           # Patient execution, lower cost
    STANDARD = "standard"   # Balanced approach
    FAST = "fast"          # Quick execution, moderate cost
    PRIORITY = "priority"   # High priority, higher cost
    FASTEST = "fastest"    # Immediate execution, highest cost
    ADAPTIVE = "adaptive"  # AI-driven strategy selection
    CUSTOM = "custom"      # User-defined gas price


class GasPriceType(Enum):
    """Gas price types."""
    LEGACY = "legacy"
    EIP1559 = "eip1559"


class NetworkCongestion(Enum):
    """Network congestion levels."""
    LOW = "low"        # < 50 gwei
    MEDIUM = "medium"  # 50-100 gwei
    HIGH = "high"      # 100-200 gwei
    EXTREME = "extreme" # > 200 gwei


@dataclass
class GasPrice:
    """Enhanced gas price data structure."""
    # Core price data
    base_fee: Decimal
    priority_fee: Decimal
    max_fee: Decimal
    gas_limit: int
    price_type: GasPriceType
    network: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Speed-based pricing
    slow: Decimal = field(default_factory=lambda: Decimal('0'))
    standard: Decimal = field(default_factory=lambda: Decimal('0'))
    fast: Decimal = field(default_factory=lambda: Decimal('0'))
    fastest: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Confirmation time estimates
    slow_time_minutes: int = 0
    standard_time_minutes: int = 0
    fast_time_minutes: int = 0
    fastest_time_minutes: int = 0
    
    # Network status
    congestion_level: NetworkCongestion = NetworkCongestion.MEDIUM
    pending_transactions: int = 0
    
    @property
    def total_cost_wei(self) -> int:
        """Calculate total gas cost in wei."""
        return int(self.max_fee * self.gas_limit)
    
    @property
    def total_cost_eth(self) -> float:
        """Calculate total gas cost in ETH."""
        return float(self.total_cost_wei / 1e18)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "network": self.network,
            "timestamp": self.timestamp.isoformat(),
            "base_fee_gwei": float(self.base_fee / 1e9),
            "priority_fee_gwei": float(self.priority_fee / 1e9),
            "max_fee_gwei": float(self.max_fee / 1e9),
            "prices_gwei": {
                "slow": float(self.slow),
                "standard": float(self.standard),
                "fast": float(self.fast),
                "fastest": float(self.fastest)
            },
            "confirmation_times_minutes": {
                "slow": self.slow_time_minutes,
                "standard": self.standard_time_minutes,
                "fast": self.fast_time_minutes,
                "fastest": self.fastest_time_minutes
            },
            "congestion_level": self.congestion_level.value,
            "pending_transactions": self.pending_transactions,
            "total_cost_eth": self.total_cost_eth
        }


@dataclass
class GasOptimizationResult:
    """Enhanced gas optimization result."""
    # Core recommendations
    recommended_strategy: GasStrategy
    recommended_gas_price_gwei: Decimal
    estimated_cost_usd: Decimal
    estimated_confirmation_minutes: int
    
    # Original data for comparison
    original_gas_price: GasPrice
    optimized_gas_price: GasPrice
    
    # Savings analysis
    savings_wei: int = 0
    savings_percentage: float = 0.0
    cost_savings_usd: Decimal = field(default_factory=lambda: Decimal('0'))
    time_tradeoff_minutes: int = 0
    
    # Optimization metadata
    confidence_score: float = 0.0
    strategy_used: GasStrategy = GasStrategy.STANDARD
    optimization_timestamp: datetime = field(default_factory=datetime.utcnow)
    reasoning: str = ""
    
    # Alternative options
    alternatives: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GasUsageHistory:
    """Historical gas usage for learning optimization."""
    transaction_hash: str
    timestamp: datetime
    gas_price_gwei: Decimal
    gas_used: int
    gas_cost_usd: Decimal
    confirmation_time_minutes: int
    network: str
    transaction_type: str  # 'swap', 'approval', etc.
    was_successful: bool
    user_strategy: GasStrategy


class EnhancedGasOptimizationEngine:
    """
    Advanced gas optimization engine combining multiple optimization strategies.
    
    Features:
    - Real-time gas price monitoring across multiple networks
    - Multiple optimization strategies (economy, speed, adaptive)
    - Personal usage tracking and learning
    - EIP-1559 support with legacy fallback
    - Network congestion analysis
    - Intelligent timing recommendations
    - Cost-benefit analysis for trades
    - Historical pattern analysis
    """
    
    def __init__(self, user_wallet: str = None, default_strategy: GasStrategy = GasStrategy.STANDARD):
        """
        Initialize enhanced gas optimization engine.
        
        Args:
            user_wallet: User wallet address for personalized optimization
            default_strategy: Default gas optimization strategy
        """
        self.user_wallet = user_wallet
        self.default_strategy = default_strategy
        self.network_manager = get_network_manager() if user_wallet else None
        
        # Gas price tracking
        self.current_gas_prices: Dict[str, GasPrice] = {}
        self.gas_price_history: List[GasPrice] = []
        self.optimization_results: List[GasOptimizationResult] = []
        self.user_gas_history: List[GasUsageHistory] = []
        
        # Monitoring configuration
        self.update_interval_seconds = 30
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Strategy configurations
        self.strategy_configs = {
            GasStrategy.ECONOMY: {
                "speed_multiplier": 0.7,
                "max_wait_time": 600,  # 10 minutes
                "confidence_threshold": 0.9
            },
            GasStrategy.SLOW: {
                "speed_multiplier": 0.8,
                "max_wait_time": 300,  # 5 minutes
                "confidence_threshold": 0.85
            },
            GasStrategy.STANDARD: {
                "speed_multiplier": 1.0,
                "max_wait_time": 180,  # 3 minutes
                "confidence_threshold": 0.8
            },
            GasStrategy.FAST: {
                "speed_multiplier": 1.3,
                "max_wait_time": 60,   # 1 minute
                "confidence_threshold": 0.7
            },
            GasStrategy.PRIORITY: {
                "speed_multiplier": 1.6,
                "max_wait_time": 45,   # 45 seconds
                "confidence_threshold": 0.65
            },
            GasStrategy.FASTEST: {
                "speed_multiplier": 1.8,
                "max_wait_time": 30,   # 30 seconds
                "confidence_threshold": 0.6
            },
            GasStrategy.ADAPTIVE: {
                "speed_multiplier": 1.0,
                "max_wait_time": 120,  # 2 minutes
                "confidence_threshold": 0.75
            }
        }
        
        # User preferences for personalized optimization
        self.user_preferences = {
            "max_gas_price_gwei": 200,
            "preferred_confirmation_time": 5,  # minutes
            "cost_sensitivity": 0.7,  # 0-1, higher = more cost sensitive
            "time_sensitivity": 0.3   # 0-1, higher = more time sensitive
        }
        
        logger.info(f"🔥 Enhanced Gas Optimization Engine initialized with {default_strategy.value} strategy")
        if user_wallet:
            logger.info(f"👤 Personalized optimization enabled for {user_wallet[:10]}...")
    
    async def initialize(self) -> bool:
        """Initialize the gas optimization engine."""
        try:
            # Load historical data if user wallet provided
            if self.user_wallet:
                await self._load_gas_history()
            
            # Start gas price monitoring
            await self.start_monitoring()
            
            # Get initial gas prices for supported networks
            await self._update_all_gas_prices()
            
            logger.info("✅ Enhanced Gas Optimization Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize gas optimization engine: {e}")
            return False
    
    async def start_monitoring(self) -> None:
        """Start real-time gas price monitoring."""
        try:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._gas_price_monitor())
            
            logger.info("🔍 Gas price monitoring started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start gas monitoring: {e}")
    
    async def stop_monitoring(self) -> None:
        """Stop gas price monitoring."""
        try:
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("🛑 Gas price monitoring stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping gas monitoring: {e}")
    
    async def optimize_gas_price(
        self,
        transaction_type: str,
        urgency: str = "normal",
        network: str = "ethereum",
        current_gas_price: Optional[GasPrice] = None,
        trade_value_usd: Optional[Decimal] = None,
        max_gas_cost_percent: float = 5.0
    ) -> GasOptimizationResult:
        """
        Comprehensive gas price optimization.
        
        Args:
            transaction_type: Type of transaction (swap, transfer, etc.)
            urgency: Transaction urgency (low, normal, high, critical)
            network: Blockchain network
            current_gas_price: Current gas price data
            trade_value_usd: USD value of the trade for cost analysis
            max_gas_cost_percent: Maximum gas cost as % of trade value
            
        Returns:
            GasOptimizationResult: Comprehensive optimization results
        """
        try:
            logger.debug(f"🔧 Optimizing gas for {transaction_type} on {network}")
            
            # Get current network gas prices
            if current_gas_price is None:
                current_gas_price = await self._get_current_gas_price(network)
            
            # Select optimization strategy based on urgency and trade value
            strategy = self._select_strategy(urgency, trade_value_usd)
            
            # Perform trade-aware optimization if trade value provided
            if trade_value_usd:
                return await self._optimize_for_trade(
                    current_gas_price, strategy, transaction_type, 
                    trade_value_usd, max_gas_cost_percent, urgency
                )
            
            # Standard optimization
            optimized_price = await self._apply_optimization_strategy(
                current_gas_price, strategy, transaction_type
            )
            
            # Calculate savings and confidence
            savings_wei = current_gas_price.total_cost_wei - optimized_price.total_cost_wei
            savings_percentage = (savings_wei / current_gas_price.total_cost_wei) * 100 if current_gas_price.total_cost_wei > 0 else 0
            confidence_score = await self._calculate_confidence_score(optimized_price, strategy)
            
            # Generate reasoning
            reasoning = self._generate_optimization_reasoning_basic(
                strategy, optimized_price, current_gas_price
            )
            
            # Create optimization result
            result = GasOptimizationResult(
                recommended_strategy=strategy,
                recommended_gas_price_gwei=optimized_price.max_fee / Decimal('1e9'),
                estimated_cost_usd=Decimal(str(optimized_price.total_cost_eth * 2000)),  # Mock ETH price
                estimated_confirmation_minutes=self._estimate_confirmation_time(strategy),
                original_gas_price=current_gas_price,
                optimized_gas_price=optimized_price,
                savings_wei=savings_wei,
                savings_percentage=savings_percentage,
                confidence_score=confidence_score,
                strategy_used=strategy,
                reasoning=reasoning
            )
            
            # Store result for analysis
            self.optimization_results.append(result)
            
            logger.debug(f"✅ Gas optimization complete: {savings_percentage:.1f}% savings")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Gas optimization failed: {e}")
            # Return safe fallback
            return await self._create_fallback_result(current_gas_price or await self._get_fallback_gas_price(network))
    
    async def optimize_gas_for_trade(
        self,
        network: str,
        trade_value_usd: Decimal,
        urgency: str = "normal",
        max_gas_cost_percent: float = 5.0
    ) -> GasOptimizationResult:
        """
        Optimize gas settings specifically for trading with enhanced analysis.
        
        Args:
            network: Blockchain network
            trade_value_usd: USD value of the trade
            urgency: 'low', 'normal', 'high', 'critical'
            max_gas_cost_percent: Maximum gas cost as % of trade value
            
        Returns:
            Gas optimization recommendations
        """
        try:
            logger.info(f"⛽ Optimizing gas for ${trade_value_usd} trade on {network}...")
            
            # Get current gas prices
            if network not in self.current_gas_prices:
                await self._update_gas_prices(network)
            
            gas_prices = self.current_gas_prices[network]
            
            # Calculate maximum acceptable gas cost
            max_gas_cost_usd = trade_value_usd * Decimal(str(max_gas_cost_percent / 100))
            
            # Analyze different strategies
            strategies = await self._analyze_gas_strategies(
                network, gas_prices, max_gas_cost_usd, urgency
            )
            
            # Select optimal strategy
            optimal_strategy = self._select_optimal_strategy(strategies, urgency)
            
            # Generate comprehensive optimization result
            result = await self._generate_comprehensive_optimization_result(
                optimal_strategy, strategies, gas_prices, trade_value_usd
            )
            
            logger.info(f"💡 Gas optimization: {result.recommended_strategy.value} "
                       f"@ {result.recommended_gas_price_gwei} gwei "
                       f"(${result.estimated_cost_usd:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Gas optimization failed: {e}")
            raise GasOptimizationError(f"Gas optimization failed: {e}")
    
    async def estimate_transaction_cost(
        self,
        gas_limit: int,
        network: str = "ethereum",
        strategy: Optional[GasStrategy] = None
    ) -> Dict[str, Any]:
        """
        Estimate transaction cost with different strategies.
        
        Args:
            gas_limit: Estimated gas limit for transaction
            network: Blockchain network
            strategy: Optimization strategy to use
            
        Returns:
            Dict: Cost estimates for different scenarios
        """
        try:
            strategy = strategy or self.default_strategy
            
            # Get current gas prices
            current_gas_price = await self._get_current_gas_price(network)
            
            # Calculate costs for different strategies
            estimates = {}
            for strat in GasStrategy:
                if strat == GasStrategy.CUSTOM:
                    continue
                    
                optimized_price = await self._apply_optimization_strategy(
                    current_gas_price, strat, "estimate"
                )
                optimized_price.gas_limit = gas_limit
                
                estimates[strat.value] = {
                    "cost_wei": optimized_price.total_cost_wei,
                    "cost_eth": optimized_price.total_cost_eth,
                    "cost_usd": optimized_price.total_cost_eth * 2000,  # Mock ETH price
                    "estimated_time": self._estimate_confirmation_time(strat),
                    "gas_price_gwei": float(optimized_price.max_fee / 1e9),
                    "confidence": self.strategy_configs.get(strat, {}).get("confidence_threshold", 0.7)
                }
            
            return {
                "network": network,
                "gas_limit": gas_limit,
                "estimates": estimates,
                "recommended_strategy": strategy.value,
                "current_congestion": current_gas_price.congestion_level.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Cost estimation failed: {e}")
            return {"error": str(e)}
    
    async def get_optimal_trading_time(
        self,
        network: str,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Predict optimal trading times for lower gas costs.
        
        Args:
            network: Blockchain network to analyze
            hours_ahead: Hours to look ahead for predictions
            
        Returns:
            Optimal trading time recommendations
        """
        try:
            logger.info(f"🕐 Analyzing optimal trading times for {network}...")
            
            # Analyze historical patterns
            historical_analysis = await self._analyze_historical_gas_patterns(network)
            
            # Get current gas trends
            current_trends = await self._analyze_current_gas_trends(network)
            
            # Generate predictions
            predictions = await self._predict_gas_prices(network, hours_ahead)
            
            # Find optimal windows
            optimal_windows = self._find_optimal_trading_windows(
                predictions, historical_analysis
            )
            
            return {
                "network": network,
                "analysis_period_hours": hours_ahead,
                "current_gas_gwei": float(self.current_gas_prices[network].standard),
                "current_congestion": self.current_gas_prices[network].congestion_level.value,
                "optimal_windows": optimal_windows,
                "historical_patterns": historical_analysis,
                "predictions": predictions,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze optimal trading time: {e}")
            return {"error": str(e)}
    
    async def monitor_gas_prices(self, network: str = "ethereum", duration: int = 300) -> Dict[str, Any]:
        """
        Monitor gas prices over time with enhanced analysis.
        
        Args:
            network: Blockchain network to monitor
            duration: Monitoring duration in seconds
            
        Returns:
            Dict: Gas price monitoring results with trend analysis
        """
        try:
            logger.info(f"📊 Starting gas price monitoring for {duration}s on {network}")
            
            monitoring_data = []
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(seconds=duration)
            
            while datetime.utcnow() < end_time:
                gas_price = await self._get_current_gas_price(network)
                monitoring_data.append(gas_price)
                
                await asyncio.sleep(30)  # Check every 30 seconds
            
            # Analyze monitoring data
            analysis = await self._analyze_gas_price_trends(monitoring_data)
            
            # Calculate volatility metrics
            volatility_analysis = self._calculate_volatility_metrics(monitoring_data)
            
            return {
                "network": network,
                "monitoring_duration": duration,
                "data_points": len(monitoring_data),
                "analysis": analysis,
                "volatility": volatility_analysis,
                "recommendations": self._generate_monitoring_recommendations(analysis, volatility_analysis),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Gas price monitoring failed: {e}")
            return {"error": str(e)}
    
    async def track_gas_usage(
        self,
        transaction_hash: str,
        gas_price_gwei: Decimal,
        gas_used: int,
        gas_cost_usd: Decimal,
        confirmation_time_minutes: int,
        network: str,
        transaction_type: str,
        was_successful: bool,
        user_strategy: GasStrategy
    ) -> bool:
        """
        Track gas usage for learning optimization patterns.
        """
        try:
            logger.info(f"📊 Tracking gas usage: {transaction_hash[:10]}... "
                       f"{gas_price_gwei} gwei, ${gas_cost_usd:.2f}")
            
            # Create gas usage record
            usage_record = GasUsageHistory(
                transaction_hash=transaction_hash,
                timestamp=datetime.utcnow(),
                gas_price_gwei=gas_price_gwei,
                gas_used=gas_used,
                gas_cost_usd=gas_cost_usd,
                confirmation_time_minutes=confirmation_time_minutes,
                network=network,
                transaction_type=transaction_type,
                was_successful=was_successful,
                user_strategy=user_strategy
            )
            
            # Add to history
            self.user_gas_history.append(usage_record)
            
            # Keep only recent history (last 1000 transactions)
            if len(self.user_gas_history) > 1000:
                self.user_gas_history = self.user_gas_history[-1000:]
            
            # Update user preferences based on usage patterns
            await self._update_user_preferences()
            
            # Save to database
            await self._save_gas_usage_record(usage_record)
            
            logger.debug(f"✅ Gas usage tracked successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to track gas usage: {e}")
            return False
    
    async def get_gas_efficiency_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive gas efficiency report.
        """
        try:
            logger.info(f"📈 Generating gas efficiency report ({days} days)...")
            
            # Filter recent gas usage
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_usage = [
                usage for usage in self.user_gas_history
                if usage.timestamp >= cutoff_date
            ]
            
            if not recent_usage:
                return {
                    "message": f"No gas usage data for the last {days} days",
                    "recommendations": ["Start trading to build gas efficiency data"]
                }
            
            # Calculate efficiency metrics
            efficiency_metrics = await self._calculate_efficiency_metrics(recent_usage)
            
            # Analyze spending patterns
            spending_analysis = await self._analyze_gas_spending_patterns(recent_usage)
            
            # Generate optimization recommendations
            recommendations = await self._generate_gas_recommendations(recent_usage)
            
            # Calculate potential savings
            potential_savings = await self._calculate_potential_savings(recent_usage)
            
            return {
                "analysis_period_days": days,
                "total_transactions": len(recent_usage),
                "efficiency_metrics": efficiency_metrics,
                "spending_analysis": spending_analysis,
                "optimization_recommendations": recommendations,
                "potential_savings": potential_savings,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate gas efficiency report: {e}")
            return {"error": str(e)}
    
    # Private helper methods (core functionality)
    
    async def _gas_price_monitor(self) -> None:
        """Background task to monitor gas prices."""
        while self.monitoring_active:
            try:
                await self._update_all_gas_prices()
                await asyncio.sleep(self.update_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Gas price monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_all_gas_prices(self) -> None:
        """Update gas prices for all supported networks."""
        try:
            networks = ["ethereum", "polygon", "bsc"]
            tasks = [self._update_gas_prices(network) for network in networks]
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to update all gas prices: {e}")
    
    async def _update_gas_prices(self, network: str) -> None:
        """Update gas prices for specific network."""
        try:
            if network == "ethereum":
                gas_data = await self._fetch_ethereum_gas_prices()
            elif network == "polygon":
                gas_data = await self._fetch_polygon_gas_prices()
            elif network == "bsc":
                gas_data = await self._fetch_bsc_gas_prices()
            else:
                logger.warning(f"Gas price updates not implemented for {network}")
                return
            
            # Create enhanced gas price object
            gas_price = GasPrice(
                base_fee=Decimal(str(gas_data.get('base_fee', 20))) * Decimal('1e9'),
                priority_fee=Decimal(str(gas_data.get('priority_fee', 2))) * Decimal('1e9'),
                max_fee=Decimal(str(gas_data.get('standard', 30))) * Decimal('1e9'),
                gas_limit=150000,
                price_type=GasPriceType.EIP1559,
                network=network,
                slow=Decimal(str(gas_data.get('slow', 20))),
                standard=Decimal(str(gas_data.get('standard', 30))),
                fast=Decimal(str(gas_data.get('fast', 40))),
                fastest=Decimal(str(gas_data.get('fastest', 60))),
                slow_time_minutes=gas_data.get('slow_time', 10),
                standard_time_minutes=gas_data.get('standard_time', 5),
                fast_time_minutes=gas_data.get('fast_time', 2),
                fastest_time_minutes=gas_data.get('fastest_time', 1),
                congestion_level=self._determine_congestion_level(gas_data.get('standard', 30)),
                pending_transactions=gas_data.get('pending_txs', 0)
            )
            
            self.current_gas_prices[network] = gas_price
            self.gas_price_history.append(gas_price)
            
            # Keep only recent history
            if len(self.gas_price_history) > 1000:
                self.gas_price_history = self.gas_price_history[-1000:]
            
            logger.debug(f"🔄 Updated {network} gas prices: {gas_price.standard} gwei")
            
        except Exception as e:
            logger.error(f"❌ Failed to update {network} gas prices: {e}")
    
    async def _get_current_gas_price(self, network: str) -> GasPrice:
        """Get current gas price for network."""
        if network in self.current_gas_prices:
            return self.current_gas_prices[network]
        
        # Fetch if not cached
        await self._update_gas_prices(network)
        return self.current_gas_prices.get(network, await self._get_fallback_gas_price(network))
    
    async def _get_fallback_gas_price(self, network: str) -> GasPrice:
        """Get safe fallback gas price."""
        fallback_configs = {
            "ethereum": {"base": 30, "priority": 3, "gas_limit": 200000},
            "polygon": {"base": 35, "priority": 5, "gas_limit": 200000},
            "bsc": {"base": 8, "priority": 2, "gas_limit": 200000}
        }
        
        config = fallback_configs.get(network, {"base": 30, "priority": 3, "gas_limit": 200000})
        
        return GasPrice(
            base_fee=Decimal(str(config["base"])) * Decimal('1e9'),
            priority_fee=Decimal(str(config["priority"])) * Decimal('1e9'),
            max_fee=Decimal(str(config["base"] + config["priority"])) * Decimal('1e9'),
            gas_limit=config["gas_limit"],
            price_type=GasPriceType.EIP1559,
            network=network,
            standard=Decimal(str(config["base"])),
            congestion_level=NetworkCongestion.MEDIUM
        )
    
    def _select_strategy(self, urgency: str, trade_value_usd: Optional[Decimal] = None) -> GasStrategy:
        """Enhanced strategy selection with trade value consideration."""
        urgency_strategy_map = {
            "low": GasStrategy.ECONOMY,
            "normal": GasStrategy.STANDARD,
            "high": GasStrategy.FAST,
            "critical": GasStrategy.FASTEST
        }
        
        base_strategy = urgency_strategy_map.get(urgency.lower(), self.default_strategy)
        
        # Adjust strategy based on trade value if provided
        if trade_value_usd:
            if trade_value_usd > Decimal('10000'):  # Large trades
                if base_strategy in [GasStrategy.ECONOMY, GasStrategy.SLOW]:
                    base_strategy = GasStrategy.STANDARD  # Upgrade for large trades
            elif trade_value_usd < Decimal('100'):  # Small trades
                if base_strategy in [GasStrategy.FAST, GasStrategy.FASTEST]:
                    base_strategy = GasStrategy.STANDARD  # Downgrade for small trades
        
        return base_strategy
    
    async def _apply_optimization_strategy(
        self,
        current_price: GasPrice,
        strategy: GasStrategy,
        transaction_type: str
    ) -> GasPrice:
        """Enhanced strategy application with network-specific optimizations."""
        config = self.strategy_configs.get(strategy, self.strategy_configs[GasStrategy.STANDARD])
        multiplier = Decimal(str(config["speed_multiplier"]))
        
        # Strategy-specific adjustments
        if strategy == GasStrategy.ECONOMY:
            optimized_max_fee = current_price.max_fee * Decimal("0.7")
            optimized_priority_fee = current_price.priority_fee * Decimal("0.6")
        elif strategy == GasStrategy.SLOW:
            optimized_max_fee = current_price.max_fee * Decimal("0.8")
            optimized_priority_fee = current_price.priority_fee * Decimal("0.7")
        elif strategy == GasStrategy.FASTEST:
            optimized_max_fee = current_price.max_fee * Decimal("1.8")
            optimized_priority_fee = current_price.priority_fee * Decimal("2.5")
        elif strategy == GasStrategy.PRIORITY:
            optimized_max_fee = current_price.max_fee * Decimal("1.6")
            optimized_priority_fee = current_price.priority_fee * Decimal("2.0")
        elif strategy == GasStrategy.ADAPTIVE:
            # AI-driven optimization based on network conditions
            congestion_multiplier = self._get_congestion_multiplier(current_price.congestion_level)
            optimized_max_fee = current_price.max_fee * congestion_multiplier
            optimized_priority_fee = current_price.priority_fee * congestion_multiplier
        else:
            # Standard optimization
            optimized_max_fee = current_price.max_fee * multiplier
            optimized_priority_fee = current_price.priority_fee * multiplier
        
        # Create optimized gas price
        optimized_price = GasPrice(
            base_fee=current_price.base_fee,
            priority_fee=optimized_priority_fee,
            max_fee=optimized_max_fee,
            gas_limit=current_price.gas_limit,
            price_type=current_price.price_type,
            network=current_price.network,
            congestion_level=current_price.congestion_level
        )
        
        return optimized_price
    
    def _get_congestion_multiplier(self, congestion: NetworkCongestion) -> Decimal:
        """Get gas price multiplier based on network congestion."""
        multipliers = {
            NetworkCongestion.LOW: Decimal("0.8"),
            NetworkCongestion.MEDIUM: Decimal("1.0"),
            NetworkCongestion.HIGH: Decimal("1.3"),
            NetworkCongestion.EXTREME: Decimal("1.6")
        }
        return multipliers.get(congestion, Decimal("1.0"))
    
    async def _calculate_confidence_score(self, gas_price: GasPrice, strategy: GasStrategy) -> float:
        """Enhanced confidence score calculation."""
        base_confidence = self.strategy_configs[strategy]["confidence_threshold"]
        
        # Adjust confidence based on recent optimization results
        if len(self.optimization_results) > 0:
            recent_results = self.optimization_results[-10:]  # Last 10 results
            avg_savings = statistics.mean([r.savings_percentage for r in recent_results])
            
            # Higher savings = higher confidence (up to a point)
            confidence_adjustment = min(avg_savings / 100, 0.2)
            return min(base_confidence + confidence_adjustment, 0.95)
        
        # Adjust based on network congestion
        congestion_adjustment = {
            NetworkCongestion.LOW: 0.1,
            NetworkCongestion.MEDIUM: 0.0,
            NetworkCongestion.HIGH: -0.05,
            NetworkCongestion.EXTREME: -0.1
        }.get(gas_price.congestion_level, 0.0)
        
        return min(max(base_confidence + congestion_adjustment, 0.3), 0.95)
    
    def _estimate_confirmation_time(self, strategy: GasStrategy) -> int:
        """Enhanced confirmation time estimation."""
        base_times = {
            GasStrategy.ECONOMY: 600,    # 10 minutes
            GasStrategy.SLOW: 300,       # 5 minutes
            GasStrategy.STANDARD: 180,   # 3 minutes
            GasStrategy.FAST: 60,        # 1 minute
            GasStrategy.PRIORITY: 45,    # 45 seconds
            GasStrategy.FASTEST: 30,     # 30 seconds
            GasStrategy.ADAPTIVE: 120    # 2 minutes
        }
        
        return base_times.get(strategy, 180)
    
    # Network-specific gas price fetching
    
    async def _fetch_ethereum_gas_prices(self) -> Dict[str, Any]:
        """Fetch Ethereum gas prices from multiple sources."""
        try:
            # Try multiple gas price APIs
            sources = [
                "https://api.etherscan.io/api?module=gastracker&action=gasoracle",
                "https://gas-api.metaswap.codefi.network/networks/1/suggestedGasFees"
            ]
            
            for source_url in sources:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(source_url, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                return self._parse_ethereum_gas_data(data, source_url)
                except Exception as e:
                    logger.debug(f"Gas price source failed: {source_url} - {e}")
                    continue
            
            # Fallback to default values
            logger.warning("All gas price sources failed, using fallback values")
            return {
                'slow': 20, 'standard': 30, 'fast': 40, 'fastest': 60,
                'slow_time': 10, 'standard_time': 5, 'fast_time': 2, 'fastest_time': 1,
                'base_fee': 20, 'priority_fee': 2
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch Ethereum gas prices: {e}")
            return {'slow': 20, 'standard': 30, 'fast': 40, 'fastest': 60, 'base_fee': 20, 'priority_fee': 2}
    
    async def _fetch_polygon_gas_prices(self) -> Dict[str, Any]:
        """Fetch Polygon gas prices."""
        return {
            'slow': 30, 'standard': 35, 'fast': 40, 'fastest': 50,
            'slow_time': 5, 'standard_time': 3, 'fast_time': 2, 'fastest_time': 1,
            'base_fee': 30, 'priority_fee': 5
        }
    
    async def _fetch_bsc_gas_prices(self) -> Dict[str, Any]:
        """Fetch BSC gas prices."""
        return {
            'slow': 5, 'standard': 8, 'fast': 10, 'fastest': 15,
            'slow_time': 5, 'standard_time': 3, 'fast_time': 2, 'fastest_time': 1,
            'base_fee': 5, 'priority_fee': 2
        }
    
    def _parse_ethereum_gas_data(self, data: Dict[str, Any], source_url: str) -> Dict[str, Any]:
        """Parse gas data from different Ethereum APIs."""
        try:
            if "etherscan" in source_url:
                result = data.get('result', {})
                base_fee = int(result.get('SafeGasPrice', 20))
                return {
                    'slow': base_fee, 'standard': int(result.get('ProposeGasPrice', 30)),
                    'fast': int(result.get('FastGasPrice', 40)), 'fastest': int(result.get('FastGasPrice', 40)) + 10,
                    'slow_time': 10, 'standard_time': 5, 'fast_time': 2, 'fastest_time': 1,
                    'base_fee': base_fee, 'priority_fee': 2
                }
            elif "metaswap" in source_url:
                base_fee = int(float(data.get('medium', {}).get('suggestedMaxFeePerGas', 30)))
                return {
                    'slow': int(float(data.get('low', {}).get('suggestedMaxFeePerGas', 20))),
                    'standard': base_fee, 'fast': int(float(data.get('high', {}).get('suggestedMaxFeePerGas', 40))),
                    'fastest': int(float(data.get('high', {}).get('suggestedMaxFeePerGas', 40))) + 10,
                    'slow_time': 10, 'standard_time': 5, 'fast_time': 2, 'fastest_time': 1,
                    'base_fee': base_fee, 'priority_fee': 2
                }
            
            return {'slow': 20, 'standard': 30, 'fast': 40, 'fastest': 60, 'base_fee': 20, 'priority_fee': 2}
            
        except Exception as e:
            logger.error(f"❌ Failed to parse gas data: {e}")
            return {'slow': 20, 'standard': 30, 'fast': 40, 'fastest': 60, 'base_fee': 20, 'priority_fee': 2}
    
    def _determine_congestion_level(self, standard_gas_gwei: float) -> NetworkCongestion:
        """Determine network congestion level based on gas prices."""
        if standard_gas_gwei < 50:
            return NetworkCongestion.LOW
        elif standard_gas_gwei < 100:
            return NetworkCongestion.MEDIUM
        elif standard_gas_gwei < 200:
            return NetworkCongestion.HIGH
        else:
            return NetworkCongestion.EXTREME
    
    # Enhanced analysis methods
    
    async def _analyze_gas_price_trends(self, monitoring_data: List[GasPrice]) -> Dict[str, Any]:
        """Enhanced gas price trend analysis."""
        if not monitoring_data:
            return {"error": "No monitoring data available"}
        
        # Extract prices for analysis
        max_fees = [float(gp.max_fee / 1e9) for gp in monitoring_data]  # Convert to gwei
        priority_fees = [float(gp.priority_fee / 1e9) for gp in monitoring_data]
        
        # Calculate enhanced statistics
        analysis = {
            "max_fee_stats": {
                "min": min(max_fees), "max": max(max_fees),
                "avg": statistics.mean(max_fees), "median": statistics.median(max_fees),
                "std_dev": statistics.stdev(max_fees) if len(max_fees) > 1 else 0,
                "trend": self._calculate_trend(max_fees)
            },
            "priority_fee_stats": {
                "min": min(priority_fees), "max": max(priority_fees),
                "avg": statistics.mean(priority_fees), "median": statistics.median(priority_fees),
                "std_dev": statistics.stdev(priority_fees) if len(priority_fees) > 1 else 0,
                "trend": self._calculate_trend(priority_fees)
            },
            "volatility": self._calculate_volatility(max_fees),
            "congestion_changes": self._analyze_congestion_changes(monitoring_data),
            "recommendation": self._generate_trend_recommendation(max_fees, monitoring_data)
        }
        
        return analysis
    
    def _calculate_trend(self, prices: List[float]) -> str:
        """Calculate price trend direction."""
        if len(prices) < 2:
            return "stable"
        
        # Simple linear trend
        start_avg = statistics.mean(prices[:len(prices)//3])
        end_avg = statistics.mean(prices[-len(prices)//3:])
        
        change_percent = ((end_avg - start_avg) / start_avg) * 100
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_volatility(self, prices: List[float]) -> str:
        """Calculate price volatility level."""
        if len(prices) < 2:
            return "low"
        
        std_dev = statistics.stdev(prices)
        mean_price = statistics.mean(prices)
        
        volatility_ratio = std_dev / mean_price if mean_price > 0 else 0
        
        if volatility_ratio > 0.2:
            return "high"
        elif volatility_ratio > 0.1:
            return "medium"
        else:
            return "low"
    
    def _analyze_congestion_changes(self, monitoring_data: List[GasPrice]) -> Dict[str, Any]:
        """Analyze network congestion level changes."""
        congestion_levels = [gp.congestion_level.value for gp in monitoring_data]
        
        return {
            "most_common": max(set(congestion_levels), key=congestion_levels.count),
            "changes": len(set(congestion_levels)),
            "current": monitoring_data[-1].congestion_level.value if monitoring_data else "unknown"
        }
    
    def _generate_trend_recommendation(self, prices: List[float], monitoring_data: List[GasPrice]) -> str:
        """Generate recommendation based on trend analysis."""
        trend = self._calculate_trend(prices)
        volatility = self._calculate_volatility(prices)
        current_congestion = monitoring_data[-1].congestion_level if monitoring_data else NetworkCongestion.MEDIUM
        
        if trend == "decreasing" and volatility == "low":
            return "Good time to transact - gas prices are stable and decreasing"
        elif trend == "increasing" and current_congestion == NetworkCongestion.HIGH:
            return "Consider waiting - gas prices are rising and network is congested"
        elif volatility == "high":
            return "Volatile gas prices - wait for stabilization or use adaptive strategy"
        else:
            return "Normal gas price conditions - proceed with standard strategy"
    
    def _calculate_volatility_metrics(self, monitoring_data: List[GasPrice]) -> Dict[str, Any]:
        """Calculate detailed volatility metrics."""
        if not monitoring_data:
            return {}
        
        prices = [float(gp.max_fee / 1e9) for gp in monitoring_data]
        
        # Calculate price changes
        price_changes = []
        for i in range(1, len(prices)):
            change = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
            price_changes.append(abs(change))
        
        return {
            "average_absolute_change": statistics.mean(price_changes) if price_changes else 0,
            "max_change": max(price_changes) if price_changes else 0,
            "volatility_score": min(statistics.mean(price_changes) * 10, 100) if price_changes else 0,
            "stability_rating": "high" if statistics.mean(price_changes) < 2 else "medium" if statistics.mean(price_changes) < 5 else "low"
        }
    
    def _generate_monitoring_recommendations(self, analysis: Dict[str, Any], volatility: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on monitoring analysis."""
        recommendations = []
        
        trend = analysis.get("max_fee_stats", {}).get("trend", "stable")
        volatility_level = volatility.get("stability_rating", "medium")
        
        if trend == "increasing" and volatility_level == "low":
            recommendations.append("Gas prices are steadily increasing - consider transacting soon")
        elif trend == "decreasing":
            recommendations.append("Gas prices are decreasing - good time for non-urgent transactions")
        elif volatility_level == "low":
            recommendations.append("Gas prices are stable - safe to proceed with transactions")
        else:
            recommendations.append("High volatility detected - consider using adaptive strategy")
        
        return recommendations
    
    # Trade optimization methods
    
    async def _optimize_for_trade(
        self,
        current_price: GasPrice,
        strategy: GasStrategy,
        transaction_type: str,
        trade_value_usd: Decimal,
        max_gas_cost_percent: float,
        urgency: str
    ) -> GasOptimizationResult:
        """Trade-specific optimization with cost-benefit analysis."""
        # Calculate maximum acceptable gas cost
        max_gas_cost_usd = trade_value_usd * Decimal(str(max_gas_cost_percent / 100))
        
        # Analyze different strategies for this trade
        strategies = await self._analyze_gas_strategies(
            current_price.network, current_price, max_gas_cost_usd, urgency
        )
        
        # Select optimal strategy
        optimal_strategy = self._select_optimal_strategy(strategies, urgency)
        
        # Generate comprehensive result
        return await self._generate_comprehensive_optimization_result(
            optimal_strategy, strategies, current_price, trade_value_usd
        )
    
    async def _analyze_gas_strategies(
        self,
        network: str,
        gas_prices: GasPrice,
        max_gas_cost_usd: Decimal,
        urgency: str
    ) -> Dict[GasStrategy, Dict[str, Any]]:
        """Analyze different gas strategies for trade optimization."""
        try:
            # Estimate gas usage for typical swap (150,000 gas)
            estimated_gas_units = 150000
            
            # Get current ETH price for cost calculation (simplified)
            eth_price_usd = Decimal('2000')  # Placeholder - should fetch real price
            
            strategies = {}
            
            for strategy in GasStrategy:
                if strategy == GasStrategy.CUSTOM:
                    continue
                
                # Get gas price for strategy based on speed levels
                if strategy == GasStrategy.ECONOMY:
                    gas_price_gwei = gas_prices.slow * Decimal('0.8')  # Even lower than slow
                elif strategy == GasStrategy.SLOW:
                    gas_price_gwei = gas_prices.slow
                elif strategy == GasStrategy.STANDARD:
                    gas_price_gwei = gas_prices.standard
                elif strategy == GasStrategy.FAST:
                    gas_price_gwei = gas_prices.fast
                elif strategy in [GasStrategy.PRIORITY, GasStrategy.FASTEST]:
                    gas_price_gwei = gas_prices.fastest
                elif strategy == GasStrategy.ADAPTIVE:
                    # Adaptive strategy based on congestion
                    multiplier = self._get_congestion_multiplier(gas_prices.congestion_level)
                    gas_price_gwei = gas_prices.standard * multiplier
                
                # Calculate cost
                gas_cost_eth = (gas_price_gwei * estimated_gas_units) / Decimal('1000000000')
                gas_cost_usd = gas_cost_eth * eth_price_usd
                
                # Determine if affordable
                is_affordable = gas_cost_usd <= max_gas_cost_usd
                
                # Get confirmation time
                confirmation_time = self._estimate_confirmation_time(strategy)
                
                strategies[strategy] = {
                    'gas_price_gwei': float(gas_price_gwei),
                    'estimated_cost_usd': float(gas_cost_usd),
                    'confirmation_time_minutes': confirmation_time,
                    'is_affordable': is_affordable,
                    'urgency_match': self._calculate_urgency_match(strategy, urgency),
                    'efficiency_score': self._calculate_efficiency_score(gas_cost_usd, confirmation_time, urgency)
                }
            
            return strategies
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze gas strategies: {e}")
            return {}
    
    def _calculate_urgency_match(self, strategy: GasStrategy, urgency: str) -> float:
        """Calculate how well strategy matches urgency requirements."""
        urgency_scores = {
            'low': {
                GasStrategy.ECONOMY: 1.0, GasStrategy.SLOW: 0.9, GasStrategy.STANDARD: 0.7,
                GasStrategy.FAST: 0.3, GasStrategy.PRIORITY: 0.1, GasStrategy.FASTEST: 0.1, GasStrategy.ADAPTIVE: 0.8
            },
            'normal': {
                GasStrategy.ECONOMY: 0.5, GasStrategy.SLOW: 0.7, GasStrategy.STANDARD: 1.0,
                GasStrategy.FAST: 0.8, GasStrategy.PRIORITY: 0.4, GasStrategy.FASTEST: 0.2, GasStrategy.ADAPTIVE: 0.9
            },
            'high': {
                GasStrategy.ECONOMY: 0.1, GasStrategy.SLOW: 0.3, GasStrategy.STANDARD: 0.5,
                GasStrategy.FAST: 1.0, GasStrategy.PRIORITY: 0.9, GasStrategy.FASTEST: 0.8, GasStrategy.ADAPTIVE: 0.8
            },
            'critical': {
                GasStrategy.ECONOMY: 0.0, GasStrategy.SLOW: 0.1, GasStrategy.STANDARD: 0.2,
                GasStrategy.FAST: 0.7, GasStrategy.PRIORITY: 0.9, GasStrategy.FASTEST: 1.0, GasStrategy.ADAPTIVE: 0.6
            }
        }
        
        return urgency_scores.get(urgency, {}).get(strategy, 0.5)
    
    def _calculate_efficiency_score(self, gas_cost_usd: Decimal, confirmation_time: int, urgency: str) -> float:
        """Calculate efficiency score for strategy."""
        # Normalize cost (assuming $50 is high cost)
        cost_score = max(0, 1 - (float(gas_cost_usd) / 50))
        
        # Normalize time (assuming 300 seconds is slow)
        time_score = max(0, 1 - (confirmation_time / 300))
        
        # Weight based on urgency
        if urgency == "low":
            return cost_score * 0.8 + time_score * 0.2
        elif urgency == "high" or urgency == "critical":
            return cost_score * 0.2 + time_score * 0.8
        else:
            return cost_score * 0.5 + time_score * 0.5
    
    def _select_optimal_strategy(
        self,
        strategies: Dict[GasStrategy, Dict[str, Any]],
        urgency: str
    ) -> GasStrategy:
        """Select optimal gas strategy based on comprehensive analysis."""
        try:
            # Filter to affordable strategies
            affordable_strategies = {
                strategy: data for strategy, data in strategies.items()
                if data.get('is_affordable', False)
            }
            
            if not affordable_strategies:
                # If none affordable, pick cheapest
                cheapest = min(strategies.items(), key=lambda x: x[1].get('estimated_cost_usd', float('inf')))
                return cheapest[0]
            
            # Score strategies based on multiple factors
            best_strategy = None
            best_score = -1
            
            for strategy, data in affordable_strategies.items():
                # Calculate composite score
                efficiency_score = data.get('efficiency_score', 0.5)
                urgency_score = data.get('urgency_match', 0.5)
                
                # Weight based on user preferences
                composite_score = (
                    efficiency_score * 0.4 +
                    urgency_score * 0.3 +
                    (1 - data['estimated_cost_usd'] / max(s['estimated_cost_usd'] for s in affordable_strategies.values())) * self.user_preferences['cost_sensitivity'] * 0.2 +
                    (1 - data['confirmation_time_minutes'] / max(s['confirmation_time_minutes'] for s in affordable_strategies.values())) * self.user_preferences['time_sensitivity'] * 0.1
                )
                
                if composite_score > best_score:
                    best_score = composite_score
                    best_strategy = strategy
            
            return best_strategy or GasStrategy.STANDARD
            
        except Exception as e:
            logger.error(f"❌ Failed to select optimal strategy: {e}")
            return GasStrategy.STANDARD
    
    async def _generate_comprehensive_optimization_result(
        self,
        optimal_strategy: GasStrategy,
        strategies: Dict[GasStrategy, Dict[str, Any]],
        gas_prices: GasPrice,
        trade_value_usd: Decimal
    ) -> GasOptimizationResult:
        """Generate comprehensive optimization result."""
        try:
            optimal_data = strategies[optimal_strategy]
            
            # Calculate savings compared to fastest strategy
            fastest_cost = strategies.get(GasStrategy.FASTEST, {}).get('estimated_cost_usd', 0)
            optimal_cost = optimal_data['estimated_cost_usd']
            cost_savings = Decimal(str(fastest_cost - optimal_cost))
            
            # Generate detailed reasoning
            reasoning = self._generate_optimization_reasoning(
                optimal_strategy, optimal_data, trade_value_usd
            )
            
            # Create alternatives list
            alternatives = []
            for strategy, data in strategies.items():
                if strategy != optimal_strategy:
                    alternatives.append({
                        'strategy': strategy.value,
                        'gas_price_gwei': data['gas_price_gwei'],
                        'cost_usd': data['estimated_cost_usd'],
                        'confirmation_time_minutes': data['confirmation_time_minutes'],
                        'is_affordable': data['is_affordable'],
                        'efficiency_score': data.get('efficiency_score', 0.5)
                    })
            
            # Sort alternatives by efficiency score
            alternatives.sort(key=lambda x: x['efficiency_score'], reverse=True)
            
            # Create optimized gas price object
            optimized_gas_price = GasPrice(
                base_fee=gas_prices.base_fee,
                priority_fee=Decimal(str(optimal_data['gas_price_gwei'] * 0.1)) * Decimal('1e9'),  # Estimate priority fee
                max_fee=Decimal(str(optimal_data['gas_price_gwei'])) * Decimal('1e9'),
                gas_limit=gas_prices.gas_limit,
                price_type=gas_prices.price_type,
                network=gas_prices.network,
                congestion_level=gas_prices.congestion_level
            )
            
            return GasOptimizationResult(
                recommended_strategy=optimal_strategy,
                recommended_gas_price_gwei=Decimal(str(optimal_data['gas_price_gwei'])),
                estimated_cost_usd=Decimal(str(optimal_cost)),
                estimated_confirmation_minutes=optimal_data['confirmation_time_minutes'],
                original_gas_price=gas_prices,
                optimized_gas_price=optimized_gas_price,
                cost_savings_usd=cost_savings,
                reasoning=reasoning,
                confidence_score=0.85,  # Based on data quality and analysis depth
                alternatives=alternatives
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate comprehensive optimization result: {e}")
            raise GasOptimizationError(f"Optimization result generation failed: {e}")
    
    def _generate_optimization_reasoning(
        self,
        strategy: GasStrategy,
        data: Dict[str, Any],
        trade_value_usd: Decimal
    ) -> str:
        """Generate detailed human-readable reasoning for optimization choice."""
        cost_percent = (data['estimated_cost_usd'] / float(trade_value_usd)) * 100
        
        reasoning = f"Selected {strategy.value} strategy for optimal trade execution: "
        reasoning += f"${data['estimated_cost_usd']:.2f} gas cost ({cost_percent:.1f}% of trade value), "
        reasoning += f"~{data['confirmation_time_minutes']} minute confirmation. "
        
        if cost_percent < 1:
            reasoning += "Minimal gas impact on trade profitability - focus on execution speed. "
        elif cost_percent < 3:
            reasoning += "Balanced gas cost optimization with reasonable execution time. "
        else:
            reasoning += "High gas impact relative to trade value - consider timing optimization. "
        
        # Add strategy-specific reasoning
        if strategy == GasStrategy.ECONOMY:
            reasoning += "Prioritizing maximum cost savings over speed."
        elif strategy == GasStrategy.FASTEST:
            reasoning += "Prioritizing immediate execution over cost optimization."
        elif strategy == GasStrategy.ADAPTIVE:
            reasoning += "Using AI-driven optimization based on current network conditions."
        else:
            reasoning += f"Balancing cost and speed for {strategy.value} execution."
        
        return reasoning
    
    def _generate_optimization_reasoning_basic(
        self,
        strategy: GasStrategy,
        optimized_price: GasPrice,
        original_price: GasPrice
    ) -> str:
        """Generate basic reasoning for non-trade optimizations."""
        savings_percent = ((original_price.total_cost_wei - optimized_price.total_cost_wei) / original_price.total_cost_wei) * 100
        
        reasoning = f"Applied {strategy.value} optimization strategy. "
        
        if savings_percent > 0:
            reasoning += f"Reduced gas cost by {savings_percent:.1f}% while maintaining {strategy.value} execution speed. "
        else:
            reasoning += f"Increased gas price for {strategy.value} execution with higher confirmation probability. "
        
        reasoning += f"Network congestion: {optimized_price.congestion_level.value}."
        
        return reasoning
    
    async def _create_fallback_result(self, gas_price: GasPrice) -> GasOptimizationResult:
        """Create fallback optimization result."""
        return GasOptimizationResult(
            recommended_strategy=GasStrategy.STANDARD,
            recommended_gas_price_gwei=gas_price.max_fee / Decimal('1e9'),
            estimated_cost_usd=Decimal(str(gas_price.total_cost_eth * 2000)),
            estimated_confirmation_minutes=180,
            original_gas_price=gas_price,
            optimized_gas_price=gas_price,
            savings_wei=0,
            savings_percentage=0.0,
            confidence_score=0.5,
            strategy_used=GasStrategy.STANDARD,
            reasoning="Fallback optimization due to analysis error - using safe standard settings."
        )
    
    # User learning and preference methods (from second file)
    
    async def _calculate_efficiency_metrics(self, usage_history: List[GasUsageHistory]) -> Dict[str, Any]:
        """Calculate gas efficiency metrics from usage history."""
        try:
            if not usage_history:
                return {}
            
            total_gas_cost = sum(float(usage.gas_cost_usd) for usage in usage_history)
            avg_gas_cost = total_gas_cost / len(usage_history)
            
            # Calculate success rate
            successful_txs = sum(1 for usage in usage_history if usage.was_successful)
            success_rate = (successful_txs / len(usage_history)) * 100
            
            # Average confirmation time
            avg_confirmation_time = sum(usage.confirmation_time_minutes for usage in usage_history) / len(usage_history)
            
            # Gas price distribution
            gas_prices = [float(usage.gas_price_gwei) for usage in usage_history]
            avg_gas_price = statistics.mean(gas_prices)
            median_gas_price = statistics.median(gas_prices)
            
            return {
                'total_transactions': len(usage_history),
                'total_gas_cost_usd': round(total_gas_cost, 2),
                'average_gas_cost_usd': round(avg_gas_cost, 2),
                'success_rate_percent': round(success_rate, 1),
                'average_confirmation_time_minutes': round(avg_confirmation_time, 1),
                'average_gas_price_gwei': round(avg_gas_price, 1),
                'median_gas_price_gwei': round(median_gas_price, 1),
                'efficiency_score': min(100, round((success_rate + (100 - min(avg_confirmation_time * 10, 100))) / 2, 1))
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate efficiency metrics: {e}")
            return {}
    
    async def _analyze_gas_spending_patterns(self, usage_history: List[GasUsageHistory]) -> Dict[str, Any]:
        """Analyze gas spending patterns for optimization insights."""
        try:
            # Group by strategy
            strategy_spending = {}
            for usage in usage_history:
                strategy = usage.user_strategy.value
                if strategy not in strategy_spending:
                    strategy_spending[strategy] = []
                strategy_spending[strategy].append(float(usage.gas_cost_usd))
            
            # Calculate strategy efficiency
            strategy_analysis = {}
            for strategy, costs in strategy_spending.items():
                strategy_analysis[strategy] = {
                    'total_spent': round(sum(costs), 2),
                    'average_cost': round(sum(costs) / len(costs), 2),
                    'transaction_count': len(costs),
                    'percentage_of_total': round((sum(costs) / sum(float(u.gas_cost_usd) for u in usage_history)) * 100, 1)
                }
            
            return {
                'strategy_breakdown': strategy_analysis,
                'most_used_strategy': max(strategy_spending.keys(), key=lambda k: len(strategy_spending[k])) if strategy_spending else 'standard',
                'most_expensive_strategy': max(strategy_spending.keys(), key=lambda k: sum(strategy_spending[k])) if strategy_spending else 'standard',
                'recommendations': self._generate_spending_recommendations(strategy_analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze spending patterns: {e}")
            return {}
    
    def _generate_spending_recommendations(self, strategy_analysis: Dict[str, Any]) -> List[str]:
        """Generate spending optimization recommendations."""
        recommendations = []
        
        try:
            if not strategy_analysis:
                return recommendations
                
            # Find most expensive strategy
            most_expensive = max(strategy_analysis.items(), key=lambda x: x[1]['average_cost'])
            if most_expensive[1]['average_cost'] > 10:  # $10+ average
                recommendations.append(f"Consider reducing use of {most_expensive[0]} strategy - average cost ${most_expensive[1]['average_cost']:.2f}")
            
            # Check for overuse of fast strategies
            fast_strategies = ['fast', 'fastest', 'priority']
            fast_usage = sum(
                data['percentage_of_total'] for strategy, data in strategy_analysis.items()
                if strategy in fast_strategies
            )
            
            if fast_usage > 50:
                recommendations.append(f"High usage of fast strategies ({fast_usage:.1f}% of transactions). Consider using slower, cheaper options when not urgent.")
            
            # Check for underuse of economy strategies
            economy_usage = sum(
                data['percentage_of_total'] for strategy, data in strategy_analysis.items()
                if strategy in ['slow', 'economy']
            )
            if economy_usage < 20:
                recommendations.append("Consider using economy/slow strategies more often for non-urgent transactions to save on gas costs.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate spending recommendations: {e}")
            return []
    
    async def _generate_gas_recommendations(self, usage_history: List[GasUsageHistory]) -> List[Dict[str, Any]]:
        """Generate personalized gas optimization recommendations."""
        recommendations = []
        
        try:
            # Analyze recent high gas transactions
            high_gas_txs = [u for u in usage_history if float(u.gas_cost_usd) > 15]
            if len(high_gas_txs) > len(usage_history) * 0.3:  # >30% high gas
                recommendations.append({
                    'type': 'reduce_high_gas',
                    'priority': 'high',
                    'message': f"{len(high_gas_txs)} transactions had gas costs >$15. Consider timing trades during lower gas periods.",
                    'potential_savings_usd': round(sum(float(u.gas_cost_usd) - 10 for u in high_gas_txs), 2)
                })
            
            # Check for failed transactions
            failed_txs = [u for u in usage_history if not u.was_successful]
            if failed_txs:
                recommendations.append({
                    'type': 'reduce_failures',
                    'priority': 'medium',
                    'message': f"{len(failed_txs)} transactions failed, wasting ${sum(float(u.gas_cost_usd) for u in failed_txs):.2f} in gas.",
                    'action': 'Use higher gas prices for important transactions'
                })
            
            # Analyze strategy efficiency
            strategy_costs = {}
            for usage in usage_history:
                strategy = usage.user_strategy.value
                if strategy not in strategy_costs:
                    strategy_costs[strategy] = []
                strategy_costs[strategy].append(float(usage.gas_cost_usd))
            
            # Find inefficient strategies
            for strategy, costs in strategy_costs.items():
                if len(costs) > 5 and statistics.mean(costs) > 20:  # More than $20 average
                    recommendations.append({
                        'type': 'strategy_optimization',
                        'priority': 'medium',
                        'message': f"Your {strategy} strategy averages ${statistics.mean(costs):.2f} per transaction. Consider alternative strategies.",
                        'action': 'Review strategy selection for different transaction types'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate gas recommendations: {e}")
            return []
    
    async def _calculate_potential_savings(self, usage_history: List[GasUsageHistory]) -> Dict[str, Any]:
        """Calculate potential gas savings from optimization."""
        try:
            total_spent = sum(float(u.gas_cost_usd) for u in usage_history)
            
            # Estimate savings from better timing (20% reduction)
            timing_savings = total_spent * 0.2
            
            # Estimate savings from strategy optimization (15% reduction)
            strategy_savings = total_spent * 0.15
            
            # Estimate savings from avoiding failures
            failed_cost = sum(float(u.gas_cost_usd) for u in usage_history if not u.was_successful)
            
            # Estimate savings from using adaptive strategies (10% reduction)
            adaptive_savings = total_spent * 0.1
            
            total_potential_savings = timing_savings + strategy_savings + failed_cost + adaptive_savings
            
            return {
                'total_spent_usd': round(total_spent, 2),
                'potential_savings': {
                    'better_timing': round(timing_savings, 2),
                    'strategy_optimization': round(strategy_savings, 2),
                    'avoiding_failures': round(failed_cost, 2),
                    'adaptive_strategies': round(adaptive_savings, 2),
                    'total_potential': round(total_potential_savings, 2)
                },
                'savings_percentage': round((total_potential_savings / max(total_spent, 1)) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate potential savings: {e}")
            return {}
    
    async def _load_gas_history(self) -> None:
        """Load historical gas usage data."""
        try:
            # TODO: Load from database
            # This would typically load user's historical gas usage from a database
            logger.debug("📊 Loaded gas usage history")
            
        except Exception as e:
            logger.error(f"❌ Failed to load gas history: {e}")
    
    async def _save_gas_usage_record(self, usage_record: GasUsageHistory) -> None:
        """Save gas usage record to database."""
        try:
            # TODO: Save to database
            # This would typically save the gas usage record to a database
            logger.debug(f"💾 Saved gas usage record: {usage_record.transaction_hash[:10]}...")
            
        except Exception as e:
            logger.error(f"❌ Failed to save gas usage record: {e}")
    
    async def _update_user_preferences(self) -> None:
        """Update user preferences based on usage patterns."""
        try:
            if len(self.user_gas_history) < 10:
                return
            
            # Analyze recent usage to update preferences
            recent_usage = self.user_gas_history[-50:]  # Last 50 transactions
            
            # Calculate cost vs speed preferences
            fast_txs = [u for u in recent_usage if u.user_strategy in [GasStrategy.FAST, GasStrategy.FASTEST, GasStrategy.PRIORITY]]
            slow_txs = [u for u in recent_usage if u.user_strategy in [GasStrategy.SLOW, GasStrategy.ECONOMY, GasStrategy.STANDARD]]
            
            if len(fast_txs) > len(slow_txs):
                # User prefers speed
                self.user_preferences['time_sensitivity'] = min(0.8, self.user_preferences['time_sensitivity'] + 0.1)
                self.user_preferences['cost_sensitivity'] = max(0.2, self.user_preferences['cost_sensitivity'] - 0.1)
            else:
                # User prefers cost savings
                self.user_preferences['cost_sensitivity'] = min(0.8, self.user_preferences['cost_sensitivity'] + 0.1)
                self.user_preferences['time_sensitivity'] = max(0.2, self.user_preferences['time_sensitivity'] - 0.1)
            
            # Update preferred confirmation time based on actual usage
            avg_confirmation_time = statistics.mean([u.confirmation_time_minutes for u in recent_usage])
            self.user_preferences['preferred_confirmation_time'] = int(avg_confirmation_time)
            
            # Update max gas price based on usage patterns
            max_used_gas_price = max([float(u.gas_price_gwei) for u in recent_usage])
            if max_used_gas_price > self.user_preferences['max_gas_price_gwei']:
                self.user_preferences['max_gas_price_gwei'] = int(max_used_gas_price * 1.2)  # 20% buffer
            
            logger.debug("🎯 Updated user gas preferences based on usage patterns")
            
        except Exception as e:
            logger.error(f"❌ Failed to update user preferences: {e}")
    
    # Advanced prediction and analysis methods
    
    async def _analyze_historical_gas_patterns(self, network: str) -> Dict[str, Any]:
        """Analyze historical gas patterns for timing optimization."""
        try:
            # TODO: Implement comprehensive historical pattern analysis
            # This would analyze patterns like:
            # - Peak hours vs low gas hours
            # - Weekend vs weekday patterns
            # - Seasonal variations
            # - Major event impacts
            
            return {
                'peak_hours_utc': [14, 15, 16, 20, 21, 22],  # Common high-activity hours
                'low_gas_hours_utc': [2, 3, 4, 5, 6, 7],    # Early morning UTC
                'weekend_vs_weekday': 'weekends_typically_lower',
                'average_savings_timing': 25,  # percentage savings from optimal timing
                'best_days': ['Saturday', 'Sunday'],
                'worst_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze historical gas patterns: {e}")
            return {}
    
    async def _analyze_current_gas_trends(self, network: str) -> Dict[str, Any]:
        """Analyze current gas price trends."""
        try:
            # Use recent gas price history to analyze trends
            recent_prices = [gp for gp in self.gas_price_history if gp.network == network][-20:]  # Last 20 data points
            
            if len(recent_prices) < 2:
                return {'trend_direction': 'stable', 'trend_strength': 0.5, 'confidence': 0.3}
            
            # Calculate trend
            prices = [float(gp.standard) for gp in recent_prices]
            trend_direction = self._calculate_trend(prices)
            
            # Calculate trend strength
            if len(prices) > 1:
                price_changes = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
                trend_strength = min(statistics.mean(price_changes) / statistics.mean(prices), 1.0)
            else:
                trend_strength = 0.5
            
            # Predict short-term change
            if trend_direction == 'increasing':
                predicted_change_1h = min(trend_strength * 10, 15)  # Max 15% increase
            elif trend_direction == 'decreasing':
                predicted_change_1h = -min(trend_strength * 10, 15)  # Max 15% decrease
            else:
                predicted_change_1h = 0
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 2),
                'predicted_change_1h': round(predicted_change_1h, 1),
                'confidence': min(len(recent_prices) / 20, 0.9)  # Higher confidence with more data
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze current gas trends: {e}")
            return {'trend_direction': 'stable', 'trend_strength': 0.5, 'confidence': 0.3}
    
    async def _predict_gas_prices(self, network: str, hours_ahead: int) -> List[Dict[str, Any]]:
        """Predict gas prices for future hours using simple trend analysis."""
        try:
            current_price = self.current_gas_prices.get(network)
            if not current_price:
                return []
            
            current_gas_gwei = float(current_price.standard)
            trend_analysis = await self._analyze_current_gas_trends(network)
            
            predictions = []
            
            for hour in range(hours_ahead):
                # Simple prediction model - in production, use ML models
                base_change = trend_analysis.get('predicted_change_1h', 0) / 100
                
                # Add some cyclical variation (daily patterns)
                hour_of_day = (datetime.utcnow().hour + hour) % 24
                if hour_of_day in [14, 15, 16, 20, 21, 22]:  # Peak hours
                    cyclical_multiplier = 1.1
                elif hour_of_day in [2, 3, 4, 5, 6, 7]:  # Low hours
                    cyclical_multiplier = 0.9
                else:
                    cyclical_multiplier = 1.0
                
                # Add some randomness for volatility
                volatility_factor = 1 + (hash(f"{network}{hour}") % 21 - 10) / 1000  # ±1% random variation
                
                predicted_price = current_gas_gwei * (1 + base_change * hour) * cyclical_multiplier * volatility_factor
                predicted_price = max(predicted_price, current_gas_gwei * 0.5)  # Don't predict below 50% of current
                predicted_price = min(predicted_price, current_gas_gwei * 3.0)   # Don't predict above 300% of current
                
                is_recommended = predicted_price < current_gas_gwei * 0.9  # Recommend if 10% lower
                
                predictions.append({
                    'hour_offset': hour,
                    'predicted_gas_gwei': round(predicted_price, 1),
                    'confidence': max(0.3, trend_analysis.get('confidence', 0.5) - (hour * 0.02)),  # Decrease confidence over time
                    'recommended_for_trading': is_recommended,
                    'expected_savings_percent': round(((current_gas_gwei - predicted_price) / current_gas_gwei) * 100, 1) if predicted_price < current_gas_gwei else 0
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Failed to predict gas prices: {e}")
            return []
    
    def _find_optimal_trading_windows(
        self,
        predictions: List[Dict[str, Any]],
        historical_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find optimal trading time windows based on predictions and historical data."""
        try:
            if not predictions:
                return []
            
            optimal_windows = []
            current_window = None
            
            for i, prediction in enumerate(predictions):
                is_good_time = (
                    prediction.get('recommended_for_trading', False) or
                    prediction.get('expected_savings_percent', 0) > 10
                )
                
                if is_good_time:
                    if current_window is None:
                        # Start new window
                        current_window = {
                            'start_hour_offset': prediction['hour_offset'],
                            'end_hour_offset': prediction['hour_offset'],
                            'min_gas_gwei': prediction['predicted_gas_gwei'],
                            'max_gas_gwei': prediction['predicted_gas_gwei'],
                            'average_savings_percent': prediction.get('expected_savings_percent', 0),
                            'confidence': prediction['confidence']
                        }
                    else:
                        # Extend current window
                        current_window['end_hour_offset'] = prediction['hour_offset']
                        current_window['min_gas_gwei'] = min(current_window['min_gas_gwei'], prediction['predicted_gas_gwei'])
                        current_window['max_gas_gwei'] = max(current_window['max_gas_gwei'], prediction['predicted_gas_gwei'])
                        current_window['average_savings_percent'] = (current_window['average_savings_percent'] + prediction.get('expected_savings_percent', 0)) / 2
                        current_window['confidence'] = min(current_window['confidence'], prediction['confidence'])
                else:
                    if current_window is not None:
                        # End current window
                        current_window['duration_hours'] = current_window['end_hour_offset'] - current_window['start_hour_offset'] + 1
                        if current_window['duration_hours'] >= 1:  # Only include windows of at least 1 hour
                            optimal_windows.append(current_window)
                        current_window = None
            
            # Close final window if it exists
            if current_window is not None:
                current_window['duration_hours'] = current_window['end_hour_offset'] - current_window['start_hour_offset'] + 1
                if current_window['duration_hours'] >= 1:
                    optimal_windows.append(current_window)
            
            # Sort by savings potential
            optimal_windows.sort(key=lambda w: w['average_savings_percent'], reverse=True)
            
            return optimal_windows[:5]  # Return top 5 windows
            
        except Exception as e:
            logger.error(f"❌ Failed to find optimal trading windows: {e}")
            return []


# Factory functions and utilities

async def get_gas_optimizer(user_wallet: str = None) -> EnhancedGasOptimizationEngine:
    """Get initialized enhanced gas optimization engine."""
    optimizer = EnhancedGasOptimizationEngine(user_wallet)
    await optimizer.initialize()
    return optimizer


def create_gas_optimizer(user_wallet: str = None, default_strategy: GasStrategy = GasStrategy.STANDARD) -> EnhancedGasOptimizationEngine:
    """Create gas optimization engine without initialization."""
    return EnhancedGasOptimizationEngine(user_wallet, default_strategy)


# Export main classes and functions
__all__ = [
    "EnhancedGasOptimizationEngine",
    "GasStrategy",
    "GasPrice",
    "GasPriceType",
    "NetworkCongestion",
    "GasOptimizationResult",
    "GasUsageHistory",
    "get_gas_optimizer",
    "create_gas_optimizer"
]