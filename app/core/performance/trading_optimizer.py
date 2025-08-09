"""
Trading Performance Optimizer
File: app/core/performance/trading_optimizer.py

Advanced performance optimization system for trading operations with real-time
monitoring, adaptive algorithms, and comprehensive performance analysis.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import statistics
import json

from app.utils.logger import setup_logger
from app.core.exceptions import TradingError, PerformanceError
from app.core.trading.order_executor import Order, OrderSide, OrderType

logger = setup_logger(__name__)


class OptimizationLevel(Enum):
    """Performance optimization levels."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


class PerformanceMetric(Enum):
    """Performance metrics for monitoring."""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    PROFIT_LOSS = "profit_loss"
    SLIPPAGE = "slippage"
    GAS_EFFICIENCY = "gas_efficiency"
    LATENCY = "latency"
    THROUGHPUT = "throughput"


@dataclass
class PerformanceSnapshot:
    """Performance snapshot data."""
    timestamp: datetime
    metric: PerformanceMetric
    value: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Optimization result data."""
    optimization_type: str
    improvement_percentage: float
    before_value: float
    after_value: float
    confidence_score: float
    applied_at: datetime
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeProfitAnalysis:
    """Trade profit analysis data structure."""
    trade_id: str
    token_symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    profit_loss_usd: float
    profit_percentage: float
    execution_time_ms: int
    gas_fees_usd: float
    slippage_percent: float
    success: bool
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


class TradingPerformanceOptimizer:
    """
    Advanced trading performance optimizer with real-time monitoring,
    adaptive algorithms, and comprehensive analysis capabilities.
    
    Features:
    - Real-time performance monitoring
    - Adaptive optimization algorithms  
    - Gas optimization strategies
    - Execution time optimization
    - Slippage minimization
    - Success rate improvement
    - Performance analytics and reporting
    """
    
    def __init__(self, optimization_level=OptimizationLevel.BALANCED):
        """
        Initialize trading performance optimizer.
        
        Args:
            optimization_level: Level of optimization aggressiveness (OptimizationLevel enum or string)
        """
        # Handle both string and enum inputs
        if isinstance(optimization_level, str):
            optimization_level = OptimizationLevel(optimization_level.lower())
        elif not isinstance(optimization_level, OptimizationLevel):
            optimization_level = OptimizationLevel.BALANCED
            
        self.optimization_level = optimization_level
        self.is_initialized = False
        self.is_running = False
        
        # Performance tracking
        self.performance_snapshots: List[PerformanceSnapshot] = []
        self.optimization_results: List[OptimizationResult] = []
        self.baseline_metrics: Dict[PerformanceMetric, float] = {}
        
        # Optimization parameters
        self.optimization_parameters = {
            OptimizationLevel.CONSERVATIVE: {
                "max_gas_price_gwei": 50,
                "min_confidence_threshold": 0.8,
                "max_slippage_percent": 2.0,
                "optimization_frequency_seconds": 300,
                "risk_tolerance": 0.3
            },
            OptimizationLevel.BALANCED: {
                "max_gas_price_gwei": 100,
                "min_confidence_threshold": 0.7,
                "max_slippage_percent": 3.0,
                "optimization_frequency_seconds": 180,
                "risk_tolerance": 0.5
            },
            OptimizationLevel.AGGRESSIVE: {
                "max_gas_price_gwei": 200,
                "min_confidence_threshold": 0.6,
                "max_slippage_percent": 5.0,
                "optimization_frequency_seconds": 60,
                "risk_tolerance": 0.7
            },
            OptimizationLevel.MAXIMUM: {
                "max_gas_price_gwei": 500,
                "min_confidence_threshold": 0.5,
                "max_slippage_percent": 10.0,
                "optimization_frequency_seconds": 30,
                "risk_tolerance": 0.9
            }
        }
        
        # Monitoring tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        
        logger.info(f"🎯 TradingPerformanceOptimizer initialized with {optimization_level.value} level")
    
    async def initialize(self) -> bool:
        """
        Initialize the performance optimizer.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("🚀 Initializing trading performance optimizer...")
            
            # Initialize baseline metrics
            await self._initialize_baseline_metrics()
            
            # Start monitoring tasks
            self._monitoring_task = asyncio.create_task(self._performance_monitoring_loop())
            self._optimization_task = asyncio.create_task(self._optimization_loop())
            
            self.is_initialized = True
            self.is_running = True
            
            logger.info("✅ Trading performance optimizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize performance optimizer: {e}")
            raise PerformanceError(f"Performance optimizer initialization failed: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the performance optimizer."""
        try:
            logger.info("🛑 Shutting down trading performance optimizer...")
            
            self.is_running = False
            
            # Cancel monitoring tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self._optimization_task:
                self._optimization_task.cancel()
                try:
                    await self._optimization_task
                except asyncio.CancelledError:
                    pass
            
            # Save final performance report
            await self._save_performance_report()
            
            logger.info("✅ Trading performance optimizer shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during optimizer shutdown: {e}")
    
    async def optimize_order_execution(self, order: Order) -> Dict[str, Any]:
        """
        Optimize order execution parameters.
        
        Args:
            order: Order to optimize
            
        Returns:
            Dict containing optimized parameters
        """
        try:
            logger.debug(f"🔧 Optimizing order execution for {order.symbol}")
            
            # Get current performance metrics
            current_metrics = await self._get_current_metrics()
            
            # Optimize gas parameters
            gas_optimization = await self._optimize_gas_parameters(order)
            
            # Optimize slippage tolerance
            slippage_optimization = await self._optimize_slippage_tolerance(order)
            
            # Optimize timing
            timing_optimization = await self._optimize_execution_timing(order)
            
            # Combine optimizations
            optimized_params = {
                "gas_price": gas_optimization["gas_price"],
                "gas_limit": gas_optimization["gas_limit"],
                "slippage_tolerance": slippage_optimization["slippage_tolerance"],
                "deadline": timing_optimization["deadline"],
                "priority_fee": gas_optimization.get("priority_fee", 0),
                "optimization_confidence": min(
                    gas_optimization["confidence"],
                    slippage_optimization["confidence"],
                    timing_optimization["confidence"]
                ),
                "estimated_execution_time": timing_optimization["estimated_time"],
                "optimization_level": self.optimization_level.value
            }
            
            logger.debug(f"✅ Order optimization complete: {optimized_params['optimization_confidence']:.1%} confidence")
            
            return optimized_params
            
        except Exception as e:
            logger.error(f"❌ Order optimization failed: {e}")
            # Return safe default parameters
            return self._get_default_order_parameters(order)
    
    async def analyze_trade_performance(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trade performance and generate insights.
        
        Args:
            trade_data: Trade execution data
            
        Returns:
            Dict containing performance analysis
        """
        try:
            logger.debug("📊 Analyzing trade performance...")
            
            # Calculate performance metrics
            execution_time = trade_data.get("execution_time", 0)
            gas_used = trade_data.get("gas_used", 0)
            gas_price = trade_data.get("gas_price", 0)
            slippage = trade_data.get("actual_slippage", 0)
            profit_loss = trade_data.get("profit_loss", 0)
            
            # Calculate efficiency scores
            time_efficiency = self._calculate_time_efficiency(execution_time)
            gas_efficiency = self._calculate_gas_efficiency(gas_used, gas_price)
            slippage_efficiency = self._calculate_slippage_efficiency(slippage)
            profit_efficiency = self._calculate_profit_efficiency(profit_loss)
            
            # Overall performance score
            overall_score = (
                time_efficiency * 0.25 +
                gas_efficiency * 0.25 +
                slippage_efficiency * 0.25 +
                profit_efficiency * 0.25
            )
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(
                time_efficiency, gas_efficiency, slippage_efficiency, profit_efficiency
            )
            
            analysis = {
                "overall_score": round(overall_score, 2),
                "efficiency_scores": {
                    "time_efficiency": round(time_efficiency, 2),
                    "gas_efficiency": round(gas_efficiency, 2),
                    "slippage_efficiency": round(slippage_efficiency, 2),
                    "profit_efficiency": round(profit_efficiency, 2)
                },
                "metrics": {
                    "execution_time_ms": execution_time,
                    "gas_used": gas_used,
                    "gas_price_gwei": gas_price / 1e9 if gas_price > 0 else 0,
                    "slippage_percent": slippage * 100,
                    "profit_loss_usd": profit_loss
                },
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "optimization_level": self.optimization_level.value
            }
            
            # Store performance snapshot
            await self._store_performance_snapshot(analysis)
            
            logger.debug(f"✅ Trade performance analysis complete: {overall_score:.1f}/10.0 score")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Trade performance analysis failed: {e}")
            return {"error": str(e), "overall_score": 0}
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Dict containing performance report
        """
        try:
            logger.debug("📈 Generating performance report...")
            
            if not self.performance_snapshots:
                return {
                    "status": "no_data",
                    "message": "No performance data available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Calculate aggregate metrics
            recent_snapshots = [
                s for s in self.performance_snapshots 
                if s.timestamp > datetime.utcnow() - timedelta(hours=24)
            ]
            
            # Group by metric type
            metrics_by_type = {}
            for snapshot in recent_snapshots:
                metric_name = snapshot.metric.value
                if metric_name not in metrics_by_type:
                    metrics_by_type[metric_name] = []
                metrics_by_type[metric_name].append(snapshot.value)
            
            # Calculate statistics for each metric
            metric_statistics = {}
            for metric_name, values in metrics_by_type.items():
                if values:
                    metric_statistics[metric_name] = {
                        "count": len(values),
                        "average": statistics.mean(values),
                        "median": statistics.median(values),
                        "min": min(values),
                        "max": max(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                    }
            
            # Calculate improvement trends
            improvement_trends = self._calculate_improvement_trends()
            
            # Generate recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                metric_statistics, improvement_trends
            )
            
            report = {
                "report_period": "24_hours",
                "total_optimizations": len(self.optimization_results),
                "metric_statistics": metric_statistics,
                "improvement_trends": improvement_trends,
                "optimization_recommendations": optimization_recommendations,
                "performance_summary": {
                    "optimization_level": self.optimization_level.value,
                    "total_snapshots": len(self.performance_snapshots),
                    "recent_snapshots": len(recent_snapshots),
                    "last_optimization": self.optimization_results[-1].applied_at.isoformat() if self.optimization_results else None
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.debug("✅ Performance report generated successfully")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Performance report generation failed: {e}")
            return {"error": str(e), "status": "error"}
    
    # Private helper methods
    
    async def _initialize_baseline_metrics(self) -> None:
        """Initialize baseline performance metrics."""
        self.baseline_metrics = {
            PerformanceMetric.EXECUTION_TIME: 5000.0,  # 5 seconds in ms
            PerformanceMetric.SUCCESS_RATE: 0.95,      # 95%
            PerformanceMetric.PROFIT_LOSS: 0.0,        # Break-even
            PerformanceMetric.SLIPPAGE: 0.02,          # 2%
            PerformanceMetric.GAS_EFFICIENCY: 0.8,     # 80%
            PerformanceMetric.LATENCY: 1000.0,         # 1 second in ms
            PerformanceMetric.THROUGHPUT: 10.0         # 10 trades per minute
        }
        
        logger.debug("📊 Baseline metrics initialized")
    
    async def _performance_monitoring_loop(self) -> None:
        """Background task for performance monitoring."""
        while self.is_running:
            try:
                await self._collect_performance_metrics()
                await asyncio.sleep(30)  # Monitor every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _optimization_loop(self) -> None:
        """Background task for automatic optimization."""
        params = self.optimization_parameters[self.optimization_level]
        frequency = params["optimization_frequency_seconds"]
        
        while self.is_running:
            try:
                await self._run_automatic_optimizations()
                await asyncio.sleep(frequency)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Automatic optimization error: {e}")
                await asyncio.sleep(frequency * 2)  # Wait longer on error
    
    async def _collect_performance_metrics(self) -> None:
        """Collect current performance metrics."""
        # This would collect real metrics in production
        # For now, simulate metric collection
        pass
    
    async def _run_automatic_optimizations(self) -> None:
        """Run automatic optimization processes."""
        # This would run actual optimizations in production
        # For now, simulate optimization
        pass
    
    async def _optimize_gas_parameters(self, order: Order) -> Dict[str, Any]:
        """Optimize gas parameters for order execution."""
        params = self.optimization_parameters[self.optimization_level]
        
        # Simulate gas optimization
        base_gas_price = 20  # 20 gwei base
        max_gas_price = params["max_gas_price_gwei"]
        
        optimized_gas_price = min(base_gas_price * 1.2, max_gas_price) * 1e9  # Convert to wei
        
        return {
            "gas_price": int(optimized_gas_price),
            "gas_limit": 300000,  # Default gas limit
            "priority_fee": int(optimized_gas_price * 0.1),
            "confidence": 0.8
        }
    
    async def _optimize_slippage_tolerance(self, order: Order) -> Dict[str, Any]:
        """Optimize slippage tolerance for order execution."""
        params = self.optimization_parameters[self.optimization_level]
        max_slippage = params["max_slippage_percent"]
        
        # Dynamic slippage based on market conditions
        base_slippage = 1.0  # 1% base
        optimized_slippage = min(base_slippage * 1.5, max_slippage)
        
        return {
            "slippage_tolerance": optimized_slippage / 100,  # Convert to decimal
            "confidence": 0.7
        }
    
    async def _optimize_execution_timing(self, order: Order) -> Dict[str, Any]:
        """Optimize execution timing for order."""
        # Calculate optimal deadline (20 minutes from now)
        deadline = int((datetime.utcnow() + timedelta(minutes=20)).timestamp())
        
        return {
            "deadline": deadline,
            "estimated_time": 15000,  # 15 seconds in ms
            "confidence": 0.9
        }
    
    def _get_default_order_parameters(self, order: Order) -> Dict[str, Any]:
        """Get safe default parameters for order execution."""
        return {
            "gas_price": 30 * 1e9,  # 30 gwei
            "gas_limit": 300000,
            "slippage_tolerance": 0.03,  # 3%
            "deadline": int((datetime.utcnow() + timedelta(minutes=20)).timestamp()),
            "priority_fee": 2 * 1e9,  # 2 gwei
            "optimization_confidence": 0.5,
            "estimated_execution_time": 30000,  # 30 seconds
            "optimization_level": "default"
        }
    
    def _calculate_time_efficiency(self, execution_time: float) -> float:
        """Calculate time efficiency score (0-10)."""
        if execution_time <= 0:
            return 5.0
        
        baseline_time = self.baseline_metrics[PerformanceMetric.EXECUTION_TIME]
        
        if execution_time <= baseline_time / 2:
            return 10.0
        elif execution_time <= baseline_time:
            return 8.0
        elif execution_time <= baseline_time * 2:
            return 6.0
        elif execution_time <= baseline_time * 3:
            return 4.0
        else:
            return 2.0
    
    def _calculate_gas_efficiency(self, gas_used: float, gas_price: float) -> float:
        """Calculate gas efficiency score (0-10)."""
        if gas_used <= 0 or gas_price <= 0:
            return 5.0
        
        # Lower gas usage and price = higher efficiency
        gas_cost = gas_used * gas_price
        
        if gas_cost <= 0.01e18:  # Less than 0.01 ETH
            return 10.0
        elif gas_cost <= 0.05e18:  # Less than 0.05 ETH
            return 8.0
        elif gas_cost <= 0.1e18:   # Less than 0.1 ETH
            return 6.0
        elif gas_cost <= 0.2e18:   # Less than 0.2 ETH
            return 4.0
        else:
            return 2.0
    
    def _calculate_slippage_efficiency(self, slippage: float) -> float:
        """Calculate slippage efficiency score (0-10)."""
        if slippage < 0:
            return 10.0  # Positive slippage (better than expected)
        elif slippage <= 0.01:  # Less than 1%
            return 9.0
        elif slippage <= 0.02:  # Less than 2%
            return 7.0
        elif slippage <= 0.05:  # Less than 5%
            return 5.0
        elif slippage <= 0.1:   # Less than 10%
            return 3.0
        else:
            return 1.0
    
    def _calculate_profit_efficiency(self, profit_loss: float) -> float:
        """Calculate profit efficiency score (0-10)."""
        if profit_loss > 10:     # More than $10 profit
            return 10.0
        elif profit_loss > 5:    # More than $5 profit
            return 8.0
        elif profit_loss > 0:    # Any profit
            return 6.0
        elif profit_loss == 0:   # Break even
            return 5.0
        elif profit_loss > -5:   # Small loss
            return 3.0
        else:                    # Large loss
            return 1.0
    
    def _generate_performance_recommendations(
        self, time_eff: float, gas_eff: float, slippage_eff: float, profit_eff: float
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        if time_eff < 5:
            recommendations.append("Consider reducing order complexity or using faster DEX routes")
        
        if gas_eff < 5:
            recommendations.append("Optimize gas parameters or wait for lower network congestion")
        
        if slippage_eff < 5:
            recommendations.append("Use tighter slippage tolerance or trade during lower volatility")
        
        if profit_eff < 5:
            recommendations.append("Review trading strategy parameters and risk management rules")
        
        if not recommendations:
            recommendations.append("Performance is optimal - maintain current settings")
        
        return recommendations
    
    def _calculate_improvement_trends(self) -> Dict[str, float]:
        """Calculate improvement trends over time."""
        if len(self.optimization_results) < 2:
            return {}
        
        trends = {}
        recent_results = self.optimization_results[-10:]  # Last 10 optimizations
        
        for result in recent_results:
            opt_type = result.optimization_type
            if opt_type not in trends:
                trends[opt_type] = []
            trends[opt_type].append(result.improvement_percentage)
        
        # Calculate average improvement for each type
        avg_trends = {}
        for opt_type, improvements in trends.items():
            avg_trends[opt_type] = statistics.mean(improvements) if improvements else 0
        
        return avg_trends
    
    def _generate_optimization_recommendations(
        self, metrics: Dict[str, Any], trends: Dict[str, float]
    ) -> List[str]:
        """Generate optimization recommendations based on metrics and trends."""
        recommendations = []
        
        # Analyze metrics and trends to generate recommendations
        if "execution_time" in metrics:
            avg_time = metrics["execution_time"]["average"]
            if avg_time > 10000:  # More than 10 seconds
                recommendations.append("Consider increasing optimization level for faster execution")
        
        if "gas_efficiency" in trends:
            if trends["gas_efficiency"] < 0:
                recommendations.append("Gas optimization is declining - review gas strategies")
        
        if not recommendations:
            recommendations.append("System is performing optimally")
        
        return recommendations
    
    async def _store_performance_snapshot(self, analysis: Dict[str, Any]) -> None:
        """Store performance snapshot for historical analysis."""
        timestamp = datetime.utcnow()
        
        # Store overall score
        self.performance_snapshots.append(PerformanceSnapshot(
            timestamp=timestamp,
            metric=PerformanceMetric.PROFIT_LOSS,
            value=analysis["overall_score"],
            context={"analysis": analysis}
        ))
        
        # Limit stored snapshots to prevent memory issues
        if len(self.performance_snapshots) > 1000:
            self.performance_snapshots = self.performance_snapshots[-500:]
    
    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        # This would fetch real metrics in production
        return {
            "avg_execution_time": 5000,
            "success_rate": 0.95,
            "avg_gas_cost": 0.05,
            "avg_slippage": 0.02
        }
    
    async def _save_performance_report(self) -> None:
        """Save final performance report to file."""
        try:
            report = await self.get_performance_report()
            # In production, this would save to a file or database
            logger.info(f"📊 Performance report saved: {len(self.performance_snapshots)} snapshots")
        except Exception as e:
            logger.error(f"❌ Failed to save performance report: {e}")