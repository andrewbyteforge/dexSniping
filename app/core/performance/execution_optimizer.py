"""
Phase 5A.1: Execution Speed Optimizer
File: app/core/performance/execution_optimizer.py

Optimizes trade execution speed for better entry/exit points and profitability.
Focuses on minimizing latency, optimizing network connections, and improving timing.
"""

import asyncio
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics

from app.utils.logger import setup_logger
from app.core.blockchain.network_manager import get_network_manager, NetworkType
from app.core.performance.gas_optimizer import get_gas_optimizer
from app.core.exceptions import ExecutionOptimizationError

logger = setup_logger(__name__)


class ExecutionPriority(Enum):
    """Execution priority levels."""
    LOW = "low"          # Cost-optimized, slower execution
    NORMAL = "normal"    # Balanced execution
    HIGH = "high"        # Speed-optimized execution
    CRITICAL = "critical" # Maximum speed, premium cost


class ExecutionStage(Enum):
    """Trade execution stages for timing analysis."""
    MARKET_ANALYSIS = "market_analysis"
    OPPORTUNITY_DETECTION = "opportunity_detection"
    RISK_ASSESSMENT = "risk_assessment"
    ORDER_PREPARATION = "order_preparation"
    TRANSACTION_SUBMISSION = "transaction_submission"
    CONFIRMATION_WAIT = "confirmation_wait"
    RESULT_PROCESSING = "result_processing"


@dataclass
class ExecutionTiming:
    """Detailed timing information for trade execution."""
    trade_id: str
    strategy_name: str
    token_symbol: str
    priority: ExecutionPriority
    
    # Stage timings (in seconds)
    market_analysis_time: float = 0.0
    opportunity_detection_time: float = 0.0
    risk_assessment_time: float = 0.0
    order_preparation_time: float = 0.0
    transaction_submission_time: float = 0.0
    confirmation_wait_time: float = 0.0
    result_processing_time: float = 0.0
    
    # Total execution time
    total_execution_time: float = 0.0
    
    # Network performance
    network_latency_ms: float = 0.0
    rpc_response_time_ms: float = 0.0
    gas_price_gwei: Decimal = Decimal('0')
    
    # Execution results
    was_successful: bool = False
    profit_loss_usd: Optional[Decimal] = None
    slippage_percentage: Optional[float] = None
    
    # Timing metadata
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    network: NetworkType = NetworkType.ETHEREUM


@dataclass
class SpeedOptimization:
    """Speed optimization recommendations."""
    optimization_type: str
    current_performance: Dict[str, Any]
    recommended_changes: Dict[str, Any]
    estimated_improvement_seconds: float
    estimated_improvement_percentage: float
    implementation_difficulty: str  # 'easy', 'medium', 'hard'
    confidence_score: float


@dataclass
class ExecutionBenchmark:
    """Execution performance benchmarks."""
    strategy_name: str
    priority_level: ExecutionPriority
    
    # Timing benchmarks (in seconds)
    target_total_time: float = 30.0
    average_total_time: float = 0.0
    best_total_time: float = float('inf')
    worst_total_time: float = 0.0
    
    # Success metrics
    success_rate: float = 0.0
    total_executions: int = 0
    successful_executions: int = 0
    
    # Performance scores
    speed_score: float = 0.0      # 0-100
    reliability_score: float = 0.0 # 0-100
    efficiency_score: float = 0.0  # 0-100
    
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ExecutionSpeedOptimizer:
    """
    Execution speed optimizer for personal trading bot.
    
    Features:
    - Real-time execution timing analysis
    - Performance bottleneck identification
    - Network latency optimization
    - Execution strategy tuning
    - Speed vs cost optimization
    """
    
    def __init__(self, user_wallet: str):
        """Initialize execution speed optimizer."""
        self.user_wallet = user_wallet
        self.network_manager = get_network_manager()
        self.gas_optimizer = None
        
        # Performance tracking
        self.execution_history: List[ExecutionTiming] = []
        self.benchmarks: Dict[str, ExecutionBenchmark] = {}
        self.current_optimizations: List[SpeedOptimization] = []
        
        # Network performance tracking
        self.network_latencies: Dict[NetworkType, List[float]] = {}
        self.rpc_performance: Dict[NetworkType, Dict[str, float]] = {}
        
        # Optimization settings
        self.optimization_targets = {
            ExecutionPriority.CRITICAL: {'max_time': 15.0, 'target_time': 10.0},
            ExecutionPriority.HIGH: {'max_time': 30.0, 'target_time': 20.0},
            ExecutionPriority.NORMAL: {'max_time': 60.0, 'target_time': 45.0},
            ExecutionPriority.LOW: {'max_time': 120.0, 'target_time': 90.0}
        }
        
        logger.info(f"⚡ Execution Speed Optimizer initialized for {user_wallet[:10]}...")
    
    async def initialize(self) -> bool:
        """Initialize execution speed optimizer."""
        try:
            # Initialize gas optimizer
            self.gas_optimizer = await get_gas_optimizer(self.user_wallet)
            
            # Load historical execution data
            await self._load_execution_history()
            
            # Initialize network performance monitoring
            await self._initialize_network_monitoring()
            
            # Calculate initial benchmarks
            await self._calculate_benchmarks()
            
            logger.info("✅ Execution Speed Optimizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize execution speed optimizer: {e}")
            return False
    
    async def start_execution_timing(
        self,
        trade_id: str,
        strategy_name: str,
        token_symbol: str,
        priority: ExecutionPriority,
        network: NetworkType
    ) -> ExecutionTiming:
        """Start timing a new trade execution."""
        try:
            logger.info(f"⏱️ Starting execution timing: {trade_id} ({priority.value})")
            
            timing = ExecutionTiming(
                trade_id=trade_id,
                strategy_name=strategy_name,
                token_symbol=token_symbol,
                priority=priority,
                network=network,
                start_time=datetime.utcnow()
            )
            
            # Measure initial network latency
            timing.network_latency_ms = await self._measure_network_latency(network)
            
            self.execution_history.append(timing)
            
            return timing
            
        except Exception as e:
            logger.error(f"❌ Failed to start execution timing: {e}")
            raise ExecutionOptimizationError(f"Execution timing failed: {e}")
    
    async def record_stage_timing(
        self,
        trade_id: str,
        stage: ExecutionStage,
        duration_seconds: float
    ) -> None:
        """Record timing for specific execution stage."""
        try:
            # Find the execution timing record
            timing = next((t for t in self.execution_history if t.trade_id == trade_id), None)
            if not timing:
                logger.warning(f"⚠️ Execution timing not found for trade {trade_id}")
                return
            
            # Record stage timing
            if stage == ExecutionStage.MARKET_ANALYSIS:
                timing.market_analysis_time = duration_seconds
            elif stage == ExecutionStage.OPPORTUNITY_DETECTION:
                timing.opportunity_detection_time = duration_seconds
            elif stage == ExecutionStage.RISK_ASSESSMENT:
                timing.risk_assessment_time = duration_seconds
            elif stage == ExecutionStage.ORDER_PREPARATION:
                timing.order_preparation_time = duration_seconds
            elif stage == ExecutionStage.TRANSACTION_SUBMISSION:
                timing.transaction_submission_time = duration_seconds
            elif stage == ExecutionStage.CONFIRMATION_WAIT:
                timing.confirmation_wait_time = duration_seconds
            elif stage == ExecutionStage.RESULT_PROCESSING:
                timing.result_processing_time = duration_seconds
            
            logger.debug(f"📊 Recorded {stage.value}: {duration_seconds:.2f}s for {trade_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record stage timing: {e}")
    
    async def complete_execution_timing(
        self,
        trade_id: str,
        was_successful: bool,
        profit_loss_usd: Optional[Decimal] = None,
        gas_price_gwei: Optional[Decimal] = None,
        slippage_percentage: Optional[float] = None
    ) -> Dict[str, Any]:
        """Complete execution timing and calculate performance metrics."""
        try:
            # Find the execution timing record
            timing = next((t for t in self.execution_history if t.trade_id == trade_id), None)
            if not timing:
                logger.warning(f"⚠️ Execution timing not found for trade {trade_id}")
                return {"error": "Timing record not found"}
            
            # Complete timing record
            timing.end_time = datetime.utcnow()
            timing.was_successful = was_successful
            timing.profit_loss_usd = profit_loss_usd
            timing.slippage_percentage = slippage_percentage
            
            if gas_price_gwei:
                timing.gas_price_gwei = gas_price_gwei
            
            # Calculate total execution time
            timing.total_execution_time = (
                timing.market_analysis_time +
                timing.opportunity_detection_time +
                timing.risk_assessment_time +
                timing.order_preparation_time +
                timing.transaction_submission_time +
                timing.confirmation_wait_time +
                timing.result_processing_time
            )
            
            # Analyze performance
            performance_analysis = await self._analyze_execution_performance(timing)
            
            # Update benchmarks
            await self._update_benchmarks(timing)
            
            # Generate optimization suggestions
            optimizations = await self._generate_execution_optimizations(timing)
            
            # Save timing data
            await self._save_execution_timing(timing)
            
            logger.info(f"⏱️ Execution completed: {trade_id} - {timing.total_execution_time:.2f}s "
                       f"({'✅ SUCCESS' if was_successful else '❌ FAILED'})")
            
            return {
                "trade_id": trade_id,
                "total_execution_time": timing.total_execution_time,
                "was_successful": was_successful,
                "performance_analysis": performance_analysis,
                "optimization_suggestions": optimizations,
                "timing_breakdown": {
                    "market_analysis": timing.market_analysis_time,
                    "opportunity_detection": timing.opportunity_detection_time,
                    "risk_assessment": timing.risk_assessment_time,
                    "order_preparation": timing.order_preparation_time,
                    "transaction_submission": timing.transaction_submission_time,
                    "confirmation_wait": timing.confirmation_wait_time,
                    "result_processing": timing.result_processing_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to complete execution timing: {e}")
            return {"error": str(e)}
    
    async def optimize_execution_speed(
        self,
        strategy_name: str,
        priority: ExecutionPriority,
        target_improvement_percent: float = 20.0
    ) -> Dict[str, Any]:
        """Optimize execution speed for specific strategy and priority."""
        try:
            logger.info(f"🚀 Optimizing execution speed for {strategy_name} ({priority.value})...")
            
            # Analyze current performance
            current_performance = await self._analyze_strategy_performance(strategy_name, priority)
            
            if not current_performance:
                return {
                    "message": f"No execution data available for {strategy_name} at {priority.value} priority"
                }
            
            # Identify bottlenecks
            bottlenecks = await self._identify_execution_bottlenecks(strategy_name, priority)
            
            # Generate optimization recommendations
            optimizations = await self._generate_speed_optimizations(
                current_performance, bottlenecks, target_improvement_percent
            )
            
            # Calculate potential improvements
            potential_improvement = await self._calculate_potential_improvement(optimizations)
            
            return {
                "strategy_name": strategy_name,
                "priority": priority.value,
                "current_performance": current_performance,
                "identified_bottlenecks": bottlenecks,
                "optimization_recommendations": optimizations,
                "potential_improvement": potential_improvement,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize execution speed: {e}")
            return {"error": str(e)}
    
    async def get_execution_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive execution performance report."""
        try:
            logger.info(f"📊 Generating execution performance report ({days} days)...")
            
            # Filter recent executions
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_executions = [
                timing for timing in self.execution_history
                if timing.start_time >= cutoff_date and timing.end_time
            ]
            
            if not recent_executions:
                return {
                    "message": f"No execution data for the last {days} days",
                    "recommendations": ["Execute some trades to build performance data"]
                }
            
            # Calculate overall metrics
            overall_metrics = await self._calculate_overall_performance_metrics(recent_executions)
            
            # Analyze by strategy
            strategy_analysis = await self._analyze_performance_by_strategy(recent_executions)
            
            # Analyze by priority
            priority_analysis = await self._analyze_performance_by_priority(recent_executions)
            
            # Identify trends
            performance_trends = await self._analyze_performance_trends(recent_executions)
            
            # Generate recommendations
            recommendations = await self._generate_performance_recommendations(recent_executions)
            
            return {
                "report_period_days": days,
                "total_executions": len(recent_executions),
                "overall_metrics": overall_metrics,
                "strategy_analysis": strategy_analysis,
                "priority_analysis": priority_analysis,
                "performance_trends": performance_trends,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate performance report: {e}")
            return {"error": str(e)}
    
    async def get_network_performance_analysis(self) -> Dict[str, Any]:
        """Analyze network performance for execution optimization."""
        try:
            logger.info("🌐 Analyzing network performance...")
            
            network_analysis = {}
            
            for network in NetworkType:
                if network in self.network_latencies:
                    latencies = self.network_latencies[network]
                    
                    if latencies:
                        network_analysis[network.value] = {
                            "average_latency_ms": round(statistics.mean(latencies), 2),
                            "median_latency_ms": round(statistics.median(latencies), 2),
                            "min_latency_ms": round(min(latencies), 2),
                            "max_latency_ms": round(max(latencies), 2),
                            "latency_std_dev": round(statistics.stdev(latencies) if len(latencies) > 1 else 0, 2),
                            "performance_score": self._calculate_network_performance_score(latencies),
                            "recommendation": self._get_network_recommendation(latencies)
                        }
            
            # Overall network recommendations
            overall_recommendations = await self._generate_network_recommendations(network_analysis)
            
            return {
                "network_performance": network_analysis,
                "overall_recommendations": overall_recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze network performance: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _measure_network_latency(self, network: NetworkType) -> float:
        """Measure network latency for specific blockchain network."""
        try:
            start_time = time.time()
            
            # Perform a simple RPC call to measure latency
            # This would call the actual network manager
            await asyncio.sleep(0.05)  # Simulated network call
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Store latency for analysis
            if network not in self.network_latencies:
                self.network_latencies[network] = []
            
            self.network_latencies[network].append(latency_ms)
            
            # Keep only recent latency measurements
            if len(self.network_latencies[network]) > 100:
                self.network_latencies[network] = self.network_latencies[network][-100:]
            
            return latency_ms
            
        except Exception as e:
            logger.error(f"❌ Failed to measure network latency: {e}")
            return 100.0  # Default latency
    
    async def _analyze_execution_performance(self, timing: ExecutionTiming) -> Dict[str, Any]:
        """Analyze performance of completed execution."""
        try:
            target_time = self.optimization_targets[timing.priority]['target_time']
            max_time = self.optimization_targets[timing.priority]['max_time']
            
            # Calculate performance scores
            speed_score = max(0, min(100, (target_time / max(timing.total_execution_time, 0.1)) * 100))
            
            # Identify slowest stage
            stage_times = {
                'market_analysis': timing.market_analysis_time,
                'opportunity_detection': timing.opportunity_detection_time,
                'risk_assessment': timing.risk_assessment_time,
                'order_preparation': timing.order_preparation_time,
                'transaction_submission': timing.transaction_submission_time,
                'confirmation_wait': timing.confirmation_wait_time,
                'result_processing': timing.result_processing_time
            }
            
            slowest_stage = max(stage_times.items(), key=lambda x: x[1])
            
            # Performance classification
            if timing.total_execution_time <= target_time:
                performance_rating = "excellent"
            elif timing.total_execution_time <= max_time:
                performance_rating = "good"
            elif timing.total_execution_time <= max_time * 1.5:
                performance_rating = "poor"
            else:
                performance_rating = "critical"
            
            return {
                "total_execution_time": timing.total_execution_time,
                "target_time": target_time,
                "speed_score": round(speed_score, 1),
                "performance_rating": performance_rating,
                "slowest_stage": slowest_stage[0],
                "slowest_stage_time": slowest_stage[1],
                "network_latency_impact": timing.network_latency_ms / 1000,
                "recommendations": self._get_performance_recommendations(timing, slowest_stage)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze execution performance: {e}")
            return {}
    
    def _get_performance_recommendations(
        self, 
        timing: ExecutionTiming, 
        slowest_stage: Tuple[str, float]
    ) -> List[str]:
        """Get performance improvement recommendations."""
        recommendations = []
        
        try:
            stage_name, stage_time = slowest_stage
            
            if stage_name == 'confirmation_wait' and stage_time > 30:
                recommendations.append("Consider using higher gas prices for faster confirmations")
            elif stage_name == 'market_analysis' and stage_time > 5:
                recommendations.append("Optimize market analysis algorithms for faster processing")
            elif stage_name == 'transaction_submission' and stage_time > 3:
                recommendations.append("Check network connectivity and RPC endpoint performance")
            elif stage_name == 'risk_assessment' and stage_time > 2:
                recommendations.append("Simplify risk assessment for faster decision making")
            
            if timing.network_latency_ms > 200:
                recommendations.append("High network latency detected - consider using faster RPC endpoints")
            
            if timing.total_execution_time > self.optimization_targets[timing.priority]['max_time']:
                recommendations.append(f"Execution time exceeded maximum for {timing.priority.value} priority")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance recommendations: {e}")
            return []
    
    async def _calculate_overall_performance_metrics(self, executions: List[ExecutionTiming]) -> Dict[str, Any]:
        """Calculate overall performance metrics from execution list."""
        try:
            if not executions:
                return {}
            
            total_times = [e.total_execution_time for e in executions if e.total_execution_time > 0]
            successful_executions = [e for e in executions if e.was_successful]
            
            return {
                "total_executions": len(executions),
                "successful_executions": len(successful_executions),
                "success_rate_percent": round((len(successful_executions) / len(executions)) * 100, 1),
                "average_execution_time": round(statistics.mean(total_times), 2) if total_times else 0,
                "median_execution_time": round(statistics.median(total_times), 2) if total_times else 0,
                "fastest_execution": round(min(total_times), 2) if total_times else 0,
                "slowest_execution": round(max(total_times), 2) if total_times else 0,
                "execution_time_std_dev": round(statistics.stdev(total_times), 2) if len(total_times) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate overall performance metrics: {e}")
            return {}
    
    def _calculate_network_performance_score(self, latencies: List[float]) -> float:
        """Calculate network performance score based on latencies."""
        try:
            if not latencies:
                return 0.0
            
            avg_latency = statistics.mean(latencies)
            
            # Score based on average latency
            if avg_latency < 50:
                return 100.0
            elif avg_latency < 100:
                return 90.0
            elif avg_latency < 200:
                return 75.0
            elif avg_latency < 500:
                return 50.0
            else:
                return 25.0
                
        except Exception:
            return 50.0
    
    def _get_network_recommendation(self, latencies: List[float]) -> str:
        """Get network optimization recommendation."""
        try:
            if not latencies:
                return "No latency data available"
            
            avg_latency = statistics.mean(latencies)
            
            if avg_latency < 100:
                return "Excellent network performance"
            elif avg_latency < 200:
                return "Good network performance"
            elif avg_latency < 500:
                return "Consider switching to faster RPC endpoint"
            else:
                return "Network performance is poor - optimize connection"
                
        except Exception:
            return "Unable to analyze network performance"
    
    # Additional helper methods for loading/saving data
    
    async def _load_execution_history(self) -> None:
        """Load historical execution timing data."""
        try:
            # TODO: Load from database
            logger.debug("📊 Loaded execution history")
            
        except Exception as e:
            logger.error(f"❌ Failed to load execution history: {e}")
    
    async def _save_execution_timing(self, timing: ExecutionTiming) -> None:
        """Save execution timing to database."""
        try:
            # TODO: Save to database
            logger.debug(f"💾 Saved execution timing: {timing.trade_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save execution timing: {e}")
    
    async def _initialize_network_monitoring(self) -> None:
        """Initialize network performance monitoring."""
        try:
            # Initialize network latency tracking for all networks
            for network in NetworkType:
                self.network_latencies[network] = []
                self.rpc_performance[network] = {
                    'average_response_time': 0.0,
                    'success_rate': 100.0,
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            logger.debug("🌐 Network monitoring initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize network monitoring: {e}")
    
    async def _calculate_benchmarks(self) -> None:
        """Calculate performance benchmarks from historical data."""
        try:
            # TODO: Calculate benchmarks from execution history
            logger.debug("📊 Calculated performance benchmarks")
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate benchmarks: {e}")
    
    async def _update_benchmarks(self, timing: ExecutionTiming) -> None:
        """Update performance benchmarks with new execution data."""
        try:
            benchmark_key = f"{timing.strategy_name}_{timing.priority.value}"
            
            if benchmark_key not in self.benchmarks:
                self.benchmarks[benchmark_key] = ExecutionBenchmark(
                    strategy_name=timing.strategy_name,
                    priority_level=timing.priority
                )
            
            benchmark = self.benchmarks[benchmark_key]
            
            # Update statistics
            benchmark.total_executions += 1
            if timing.was_successful:
                benchmark.successful_executions += 1
            
            benchmark.success_rate = (benchmark.successful_executions / benchmark.total_executions) * 100
            
            # Update timing statistics
            if timing.total_execution_time > 0:
                if benchmark.average_total_time == 0:
                    benchmark.average_total_time = timing.total_execution_time
                else:
                    # Running average
                    benchmark.average_total_time = (
                        (benchmark.average_total_time * (benchmark.total_executions - 1) + timing.total_execution_time) /
                        benchmark.total_executions
                    )
                
                benchmark.best_total_time = min(benchmark.best_total_time, timing.total_execution_time)
                benchmark.worst_total_time = max(benchmark.worst_total_time, timing.total_execution_time)
            
            benchmark.last_updated = datetime.utcnow()
            
            logger.debug(f"📊 Updated benchmark for {benchmark_key}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update benchmarks: {e}")
    
    # Placeholder methods for future implementation
    
    async def _identify_execution_bottlenecks(self, strategy_name: str, priority: ExecutionPriority) -> List[Dict[str, Any]]:
        """Identify execution bottlenecks for strategy/priority combination."""
        # TODO: Implement bottleneck analysis
        return []
    
    async def _generate_speed_optimizations(
        self, 
        performance: Dict[str, Any], 
        bottlenecks: List[Dict[str, Any]], 
        target_improvement: float
    ) -> List[SpeedOptimization]:
        """Generate speed optimization recommendations."""
        optimizations = []
        
        try:
            current_avg_time = performance.get('average_execution_time', 60.0)
            
            # Network optimization
            if performance.get('network_latency_ms', 0) > 200:
                optimizations.append(SpeedOptimization(
                    optimization_type="network_optimization",
                    current_performance={"average_latency_ms": performance.get('network_latency_ms', 0)},
                    recommended_changes={
                        "action": "Switch to faster RPC endpoint",
                        "expected_latency_reduction": "50-70%",
                        "implementation": "Update network configuration"
                    },
                    estimated_improvement_seconds=current_avg_time * 0.3,
                    estimated_improvement_percentage=30.0,
                    implementation_difficulty="easy",
                    confidence_score=0.85
                ))
            
            # Gas price optimization
            if performance.get('confirmation_wait_time', 0) > 30:
                optimizations.append(SpeedOptimization(
                    optimization_type="gas_price_optimization",
                    current_performance={"avg_confirmation_time": performance.get('confirmation_wait_time', 0)},
                    recommended_changes={
                        "action": "Use higher gas prices for faster confirmations",
                        "recommended_strategy": "Use 'fast' gas strategy instead of 'standard'",
                        "cost_increase": "15-25%"
                    },
                    estimated_improvement_seconds=current_avg_time * 0.4,
                    estimated_improvement_percentage=40.0,
                    implementation_difficulty="easy",
                    confidence_score=0.9
                ))
            
            # Algorithm optimization
            if performance.get('market_analysis_time', 0) > 5:
                optimizations.append(SpeedOptimization(
                    optimization_type="algorithm_optimization",
                    current_performance={"market_analysis_time": performance.get('market_analysis_time', 0)},
                    recommended_changes={
                        "action": "Optimize market analysis algorithms",
                        "specific_changes": [
                            "Cache frequently accessed data",
                            "Parallelize independent calculations",
                            "Reduce API calls through batching"
                        ]
                    },
                    estimated_improvement_seconds=current_avg_time * 0.2,
                    estimated_improvement_percentage=20.0,
                    implementation_difficulty="medium",
                    confidence_score=0.75
                ))
            
            # Parallel processing optimization
            optimizations.append(SpeedOptimization(
                optimization_type="parallel_processing",
                current_performance={"sequential_processing": True},
                recommended_changes={
                    "action": "Implement parallel processing for independent operations",
                    "areas_for_parallelization": [
                        "Risk assessment and market analysis",
                        "Multiple network price checking",
                        "Gas price fetching and order preparation"
                    ]
                },
                estimated_improvement_seconds=current_avg_time * 0.25,
                estimated_improvement_percentage=25.0,
                implementation_difficulty="hard",
                confidence_score=0.7
            ))
            
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate speed optimizations: {e}")
            return []
    
    async def _calculate_potential_improvement(self, optimizations: List[SpeedOptimization]) -> Dict[str, Any]:
        """Calculate potential improvement from all optimizations."""
        try:
            if not optimizations:
                return {"total_improvement_seconds": 0, "total_improvement_percentage": 0}
            
            # Calculate combined improvement (not additive due to overlaps)
            total_time_saved = sum(opt.estimated_improvement_seconds for opt in optimizations)
            max_percentage_improvement = max(opt.estimated_improvement_percentage for opt in optimizations)
            
            # Realistic combined improvement (diminishing returns)
            realistic_improvement = min(max_percentage_improvement * 1.2, 60.0)  # Cap at 60%
            
            # Prioritize optimizations by impact/difficulty ratio
            optimization_priority = sorted(
                optimizations,
                key=lambda x: (x.estimated_improvement_percentage / 
                             (1 if x.implementation_difficulty == "easy" else 
                              2 if x.implementation_difficulty == "medium" else 3)),
                reverse=True
            )
            
            return {
                "total_improvement_seconds": round(total_time_saved, 2),
                "realistic_improvement_percentage": round(realistic_improvement, 1),
                "optimization_priority": [
                    {
                        "type": opt.optimization_type,
                        "improvement_percentage": opt.estimated_improvement_percentage,
                        "difficulty": opt.implementation_difficulty,
                        "confidence": opt.confidence_score
                    }
                    for opt in optimization_priority
                ],
                "implementation_order": [opt.optimization_type for opt in optimization_priority],
                "estimated_timeline": self._estimate_implementation_timeline(optimization_priority)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate potential improvement: {e}")
            return {}
    
    def _estimate_implementation_timeline(self, optimizations: List[SpeedOptimization]) -> Dict[str, str]:
        """Estimate implementation timeline for optimizations."""
        timeline = {}
        
        try:
            current_week = 1
            
            for opt in optimizations:
                if opt.implementation_difficulty == "easy":
                    timeline[opt.optimization_type] = f"Week {current_week}"
                elif opt.implementation_difficulty == "medium":
                    timeline[opt.optimization_type] = f"Week {current_week}-{current_week + 1}"
                    current_week += 2
                else:  # hard
                    timeline[opt.optimization_type] = f"Week {current_week}-{current_week + 2}"
                    current_week += 3
            
            return timeline
            
        except Exception:
            return {}
    
    async def _analyze_strategy_performance(self, strategy_name: str, priority: ExecutionPriority) -> Optional[Dict[str, Any]]:
        """Analyze performance for specific strategy and priority."""
        try:
            # Filter executions for this strategy and priority
            relevant_executions = [
                timing for timing in self.execution_history
                if (timing.strategy_name == strategy_name and 
                    timing.priority == priority and 
                    timing.total_execution_time > 0)
            ]
            
            if not relevant_executions:
                return None
            
            total_times = [e.total_execution_time for e in relevant_executions]
            successful_executions = [e for e in relevant_executions if e.was_successful]
            
            # Calculate stage averages
            stage_averages = {
                'market_analysis_time': statistics.mean([e.market_analysis_time for e in relevant_executions]),
                'opportunity_detection_time': statistics.mean([e.opportunity_detection_time for e in relevant_executions]),
                'risk_assessment_time': statistics.mean([e.risk_assessment_time for e in relevant_executions]),
                'order_preparation_time': statistics.mean([e.order_preparation_time for e in relevant_executions]),
                'transaction_submission_time': statistics.mean([e.transaction_submission_time for e in relevant_executions]),
                'confirmation_wait_time': statistics.mean([e.confirmation_wait_time for e in relevant_executions]),
                'result_processing_time': statistics.mean([e.result_processing_time for e in relevant_executions])
            }
            
            return {
                "total_executions": len(relevant_executions),
                "successful_executions": len(successful_executions),
                "success_rate": (len(successful_executions) / len(relevant_executions)) * 100,
                "average_execution_time": statistics.mean(total_times),
                "median_execution_time": statistics.median(total_times),
                "fastest_execution": min(total_times),
                "slowest_execution": max(total_times),
                "stage_averages": stage_averages,
                "network_latency_ms": statistics.mean([e.network_latency_ms for e in relevant_executions])
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze strategy performance: {e}")
            return None
    
    async def _analyze_performance_by_strategy(self, executions: List[ExecutionTiming]) -> Dict[str, Any]:
        """Analyze performance breakdown by strategy."""
        try:
            strategy_performance = {}
            
            # Group executions by strategy
            strategies = set(e.strategy_name for e in executions)
            
            for strategy in strategies:
                strategy_executions = [e for e in executions if e.strategy_name == strategy]
                total_times = [e.total_execution_time for e in strategy_executions if e.total_execution_time > 0]
                successful = [e for e in strategy_executions if e.was_successful]
                
                if total_times:
                    strategy_performance[strategy] = {
                        "total_executions": len(strategy_executions),
                        "success_rate": (len(successful) / len(strategy_executions)) * 100,
                        "average_time": statistics.mean(total_times),
                        "median_time": statistics.median(total_times),
                        "fastest_time": min(total_times),
                        "slowest_time": max(total_times)
                    }
            
            return strategy_performance
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze performance by strategy: {e}")
            return {}
    
    async def _analyze_performance_by_priority(self, executions: List[ExecutionTiming]) -> Dict[str, Any]:
        """Analyze performance breakdown by priority level."""
        try:
            priority_performance = {}
            
            # Group executions by priority
            priorities = set(e.priority for e in executions)
            
            for priority in priorities:
                priority_executions = [e for e in executions if e.priority == priority]
                total_times = [e.total_execution_time for e in priority_executions if e.total_execution_time > 0]
                successful = [e for e in priority_executions if e.was_successful]
                
                if total_times:
                    target_time = self.optimization_targets[priority]['target_time']
                    meeting_target = len([t for t in total_times if t <= target_time])
                    
                    priority_performance[priority.value] = {
                        "total_executions": len(priority_executions),
                        "success_rate": (len(successful) / len(priority_executions)) * 100,
                        "average_time": statistics.mean(total_times),
                        "target_time": target_time,
                        "meeting_target_percentage": (meeting_target / len(total_times)) * 100,
                        "fastest_time": min(total_times),
                        "slowest_time": max(total_times)
                    }
            
            return priority_performance
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze performance by priority: {e}")
            return {}
    
    async def _analyze_performance_trends(self, executions: List[ExecutionTiming]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        try:
            if len(executions) < 10:
                return {"message": "Need at least 10 executions to analyze trends"}
            
            # Sort by time
            sorted_executions = sorted(executions, key=lambda x: x.start_time)
            
            # Split into first and second half
            mid_point = len(sorted_executions) // 2
            first_half = sorted_executions[:mid_point]
            second_half = sorted_executions[mid_point:]
            
            # Calculate averages for each half
            first_half_avg = statistics.mean([e.total_execution_time for e in first_half if e.total_execution_time > 0])
            second_half_avg = statistics.mean([e.total_execution_time for e in second_half if e.total_execution_time > 0])
            
            # Calculate trend
            if second_half_avg < first_half_avg:
                trend = "improving"
                improvement_percent = ((first_half_avg - second_half_avg) / first_half_avg) * 100
            else:
                trend = "declining"
                improvement_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            return {
                "trend_direction": trend,
                "change_percentage": round(improvement_percent, 1),
                "first_half_average": round(first_half_avg, 2),
                "second_half_average": round(second_half_avg, 2),
                "analysis_period": f"{first_half[0].start_time.date()} to {second_half[-1].start_time.date()}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze performance trends: {e}")
            return {}
    
    async def _generate_performance_recommendations(self, executions: List[ExecutionTiming]) -> List[Dict[str, Any]]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        try:
            if not executions:
                return recommendations
            
            # Calculate overall metrics
            total_times = [e.total_execution_time for e in executions if e.total_execution_time > 0]
            successful_executions = [e for e in executions if e.was_successful]
            
            avg_time = statistics.mean(total_times)
            success_rate = (len(successful_executions) / len(executions)) * 100
            
            # Generate recommendations based on performance
            if avg_time > 60:  # Average execution time > 1 minute
                recommendations.append({
                    "type": "execution_speed",
                    "priority": "high",
                    "message": f"Average execution time is {avg_time:.1f}s. Consider optimizing for faster execution.",
                    "actions": [
                        "Use higher gas prices for faster confirmations",
                        "Optimize market analysis algorithms",
                        "Switch to faster RPC endpoints"
                    ]
                })
            
            if success_rate < 90:
                recommendations.append({
                    "type": "reliability",
                    "priority": "high",
                    "message": f"Success rate is {success_rate:.1f}%. Improve execution reliability.",
                    "actions": [
                        "Add retry mechanisms for failed transactions",
                        "Implement better error handling",
                        "Use more reliable RPC endpoints"
                    ]
                })
            
            # Network-specific recommendations
            high_latency_networks = []
            for network, latencies in self.network_latencies.items():
                if latencies and statistics.mean(latencies) > 200:
                    high_latency_networks.append(network.value)
            
            if high_latency_networks:
                recommendations.append({
                    "type": "network_optimization",
                    "priority": "medium",
                    "message": f"High latency detected on networks: {', '.join(high_latency_networks)}",
                    "actions": [
                        "Switch to faster RPC endpoints",
                        "Consider using multiple RPC endpoints for redundancy",
                        "Optimize network connection settings"
                    ]
                })
            
            # Stage-specific recommendations
            stage_times = {}
            for execution in executions:
                for stage in ['market_analysis_time', 'confirmation_wait_time', 'transaction_submission_time']:
                    value = getattr(execution, stage, 0)
                    if stage not in stage_times:
                        stage_times[stage] = []
                    stage_times[stage].append(value)
            
            for stage, times in stage_times.items():
                avg_stage_time = statistics.mean(times) if times else 0
                
                if stage == 'confirmation_wait_time' and avg_stage_time > 30:
                    recommendations.append({
                        "type": "confirmation_optimization",
                        "priority": "medium",
                        "message": f"Long confirmation wait times (avg: {avg_stage_time:.1f}s)",
                        "actions": ["Use higher gas prices", "Monitor network congestion"]
                    })
                elif stage == 'market_analysis_time' and avg_stage_time > 5:
                    recommendations.append({
                        "type": "analysis_optimization",
                        "priority": "medium",
                        "message": f"Slow market analysis (avg: {avg_stage_time:.1f}s)",
                        "actions": ["Cache market data", "Optimize analysis algorithms"]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate performance recommendations: {e}")
            return []
    
    async def _generate_network_recommendations(self, network_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate network-specific optimization recommendations."""
        recommendations = []
        
        try:
            for network, metrics in network_analysis.items():
                avg_latency = metrics.get('average_latency_ms', 0)
                performance_score = metrics.get('performance_score', 0)
                
                if performance_score < 50:
                    recommendations.append({
                        "network": network,
                        "type": "network_optimization",
                        "priority": "high",
                        "message": f"{network} network performance is poor (score: {performance_score})",
                        "current_latency": f"{avg_latency:.1f}ms",
                        "actions": [
                            "Switch to a faster RPC endpoint",
                            "Use multiple RPC endpoints for redundancy",
                            "Consider using a different network for time-sensitive trades"
                        ]
                    })
                elif performance_score < 75:
                    recommendations.append({
                        "network": network,
                        "type": "network_optimization",
                        "priority": "medium",
                        "message": f"{network} network performance could be improved (score: {performance_score})",
                        "current_latency": f"{avg_latency:.1f}ms",
                        "actions": [
                            "Monitor for faster RPC endpoints",
                            "Implement connection pooling"
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate network recommendations: {e}")
            return []
    
    async def _generate_execution_optimizations(self, timing: ExecutionTiming) -> List[Dict[str, Any]]:
        """Generate optimizations specific to this execution."""
        optimizations = []
        
        try:
            # Network latency optimization
            if timing.network_latency_ms > 200:
                optimizations.append({
                    "type": "network_latency",
                    "message": f"High network latency ({timing.network_latency_ms:.1f}ms)",
                    "recommendation": "Switch to faster RPC endpoint",
                    "potential_improvement": "30-50% faster execution"
                })
            
            # Gas price optimization
            if timing.confirmation_wait_time > 30:
                optimizations.append({
                    "type": "gas_optimization",
                    "message": f"Long confirmation wait ({timing.confirmation_wait_time:.1f}s)",
                    "recommendation": "Use higher gas price strategy",
                    "potential_improvement": "Faster confirmations"
                })
            
            # Stage-specific optimizations
            if timing.market_analysis_time > 5:
                optimizations.append({
                    "type": "analysis_optimization",
                    "message": f"Slow market analysis ({timing.market_analysis_time:.1f}s)",
                    "recommendation": "Cache market data and optimize algorithms",
                    "potential_improvement": "2-3x faster analysis"
                })
            
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate execution optimizations: {e}")
            return []


# Factory function
async def get_execution_optimizer(user_wallet: str) -> ExecutionSpeedOptimizer:
    """Get initialized execution speed optimizer."""
    optimizer = ExecutionSpeedOptimizer(user_wallet)
    await optimizer.initialize()
    return optimizer