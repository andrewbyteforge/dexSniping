"""
Phase 5A.1: Trading Performance Integration
File: app/core/performance/trading_performance_manager.py

Integrates all trading performance optimization components for personal trading bot.
Provides unified interface for profit tracking, gas optimization, and execution speed.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from app.utils.logger import setup_logger
from app.core.performance.trading_optimizer import (
    get_trading_performance_optimizer,
    TradingPerformanceOptimizer
)
from app.core.performance.gas_optimizer import (
    get_gas_optimizer,
    GasOptimizationEngine,
    GasStrategy,
    NetworkType
)
from app.core.performance.execution_optimizer import (
    get_execution_optimizer,
    ExecutionSpeedOptimizer,
    ExecutionPriority,
    ExecutionStage
)
from app.core.exceptions import PerformanceError

logger = setup_logger(__name__)


class TradePhase(Enum):
    """Trade execution phases for comprehensive tracking."""
    ANALYSIS = "analysis"
    ENTRY = "entry"
    MONITORING = "monitoring"
    EXIT = "exit"
    COMPLETE = "complete"


@dataclass
class PersonalTradingSession:
    """Personal trading session with comprehensive performance tracking."""
    session_id: str
    user_wallet: str
    strategy_name: str
    start_time: datetime
    
    # Trade details
    token_symbol: str
    target_profit_usd: Decimal
    max_loss_usd: Decimal
    priority: ExecutionPriority
    
    # Current status
    current_phase: TradePhase = TradePhase.ANALYSIS
    is_active: bool = True
    
    # Performance tracking IDs
    trade_id: Optional[str] = None
    execution_timing_id: Optional[str] = None
    
    # Results
    actual_profit_usd: Optional[Decimal] = None
    gas_fees_paid_usd: Optional[Decimal] = None
    total_execution_time: Optional[float] = None
    
    end_time: Optional[datetime] = None


class TradingPerformanceManager:
    """
    Unified trading performance manager for personal trading optimization.
    
    Integrates:
    - Real profit tracking and analysis
    - Gas fee optimization
    - Execution speed optimization
    - Comprehensive performance reporting
    """
    
    def __init__(self, user_wallet: str):
        """Initialize trading performance manager."""
        self.user_wallet = user_wallet
        
        # Component managers
        self.profit_optimizer: Optional[TradingPerformanceOptimizer] = None
        self.gas_optimizer: Optional[GasOptimizationEngine] = None
        self.execution_optimizer: Optional[ExecutionSpeedOptimizer] = None
        
        # Active trading sessions
        self.active_sessions: Dict[str, PersonalTradingSession] = {}
        self.completed_sessions: List[PersonalTradingSession] = []
        
        # Performance metrics
        self.daily_metrics = {
            "trades_today": 0,
            "profit_today": Decimal('0'),
            "gas_fees_today": Decimal('0'),
            "success_rate_today": 0.0
        }
        
        logger.info(f"🎯 Trading Performance Manager initialized for {user_wallet[:10]}...")
    
    async def initialize(self) -> bool:
        """Initialize all performance optimization components."""
        try:
            logger.info("🚀 Initializing Trading Performance Manager...")
            
            # Initialize all optimizers
            initialization_tasks = [
                self._initialize_profit_optimizer(),
                self._initialize_gas_optimizer(),
                self._initialize_execution_optimizer()
            ]
            
            results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
            
            # Check for initialization failures
            failed_components = []
            for i, result in enumerate(results):
                component_names = ["Profit Optimizer", "Gas Optimizer", "Execution Optimizer"]
                if isinstance(result, Exception):
                    failed_components.append(component_names[i])
                    logger.error(f"❌ Failed to initialize {component_names[i]}: {result}")
            
            if failed_components:
                logger.warning(f"⚠️ Some components failed to initialize: {failed_components}")
                # Continue with available components
            
            # Load daily metrics
            await self._load_daily_metrics()
            
            success_rate = (len(results) - len(failed_components)) / len(results) * 100
            logger.info(f"✅ Trading Performance Manager initialized ({success_rate:.0f}% success)")
            
            return len(failed_components) == 0  # True if all components initialized
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Trading Performance Manager: {e}")
            return False
    
    async def start_trading_session(
        self,
        strategy_name: str,
        token_symbol: str,
        target_profit_usd: Decimal,
        max_loss_usd: Decimal,
        priority: ExecutionPriority = ExecutionPriority.NORMAL,
        network: NetworkType = NetworkType.ETHEREUM
    ) -> Dict[str, Any]:
        """Start a new trading session with comprehensive tracking."""
        try:
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{token_symbol}"
            
            logger.info(f"🎯 Starting trading session: {session_id}")
            
            # Create trading session
            session = PersonalTradingSession(
                session_id=session_id,
                user_wallet=self.user_wallet,
                strategy_name=strategy_name,
                start_time=datetime.utcnow(),
                token_symbol=token_symbol,
                target_profit_usd=target_profit_usd,
                max_loss_usd=max_loss_usd,
                priority=priority
            )
            
            # Initialize execution timing
            if self.execution_optimizer:
                execution_timing = await self.execution_optimizer.start_execution_timing(
                    trade_id=session_id,
                    strategy_name=strategy_name,
                    token_symbol=token_symbol,
                    priority=priority,
                    network=network
                )
                session.execution_timing_id = session_id
            
            # Add to active sessions
            self.active_sessions[session_id] = session
            
            # Get gas optimization for this trade
            gas_optimization = None
            if self.gas_optimizer:
                trade_value = target_profit_usd * 10  # Estimate trade value from target profit
                gas_optimization = await self.gas_optimizer.optimize_gas_for_trade(
                    network=network,
                    trade_value_usd=trade_value,
                    urgency=priority.value
                )
            
            return {
                "success": True,
                "session_id": session_id,
                "session_details": {
                    "strategy": strategy_name,
                    "token": token_symbol,
                    "target_profit_usd": float(target_profit_usd),
                    "max_loss_usd": float(max_loss_usd),
                    "priority": priority.value,
                    "network": network.value
                },
                "gas_optimization": gas_optimization.to_dict() if gas_optimization else None,
                "recommendations": await self._get_session_recommendations(session),
                "started_at": session.start_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start trading session: {e}")
            return {"success": False, "error": str(e)}
    
    async def record_trade_entry(
        self,
        session_id: str,
        entry_price: Decimal,
        entry_amount: Decimal,
        gas_fee_usd: Decimal,
        execution_time_seconds: float
    ) -> Dict[str, Any]:
        """Record trade entry with comprehensive performance tracking."""
        try:
            if session_id not in self.active_sessions:
                raise PerformanceError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            session.current_phase = TradePhase.ENTRY
            session.trade_id = f"trade_{session_id}"
            
            logger.info(f"📈 Recording trade entry: {session_id}")
            
            # Record with profit optimizer
            profit_tracking_result = None
            if self.profit_optimizer:
                await self.profit_optimizer.track_trade_entry(
                    trade_id=session.trade_id,
                    strategy_name=session.strategy_name,
                    token_symbol=session.token_symbol,
                    entry_price=entry_price,
                    entry_amount=entry_amount,
                    gas_fee_usd=gas_fee_usd
                )
                profit_tracking_result = {"status": "tracked"}
            
            # Record execution timing
            execution_result = None
            if self.execution_optimizer:
                await self.execution_optimizer.record_stage_timing(
                    trade_id=session_id,
                    stage=ExecutionStage.ORDER_PREPARATION,
                    duration_seconds=execution_time_seconds
                )
                execution_result = {"stage_recorded": True}
            
            # Update session
            session.current_phase = TradePhase.MONITORING
            
            return {
                "success": True,
                "session_id": session_id,
                "trade_id": session.trade_id,
                "entry_details": {
                    "price": float(entry_price),
                    "amount": float(entry_amount),
                    "value_usd": float(entry_price * entry_amount),
                    "gas_fee_usd": float(gas_fee_usd),
                    "execution_time_seconds": execution_time_seconds
                },
                "profit_tracking": profit_tracking_result,
                "execution_tracking": execution_result,
                "current_phase": session.current_phase.value
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to record trade entry: {e}")
            return {"success": False, "error": str(e)}
    
    async def record_trade_exit(
        self,
        session_id: str,
        exit_price: Decimal,
        exit_amount: Decimal,
        gas_fee_usd: Decimal,
        execution_time_seconds: float
    ) -> Dict[str, Any]:
        """Record trade exit and complete comprehensive analysis."""
        try:
            if session_id not in self.active_sessions:
                raise PerformanceError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            session.current_phase = TradePhase.EXIT
            
            logger.info(f"💰 Recording trade exit: {session_id}")
            
            # Record with profit optimizer
            profit_result = None
            if self.profit_optimizer and session.trade_id:
                profit_result = await self.profit_optimizer.track_trade_exit(
                    trade_id=session.trade_id,
                    exit_price=exit_price,
                    exit_amount=exit_amount,
                    gas_fee_usd=gas_fee_usd,
                    execution_time_seconds=execution_time_seconds
                )
            
            # Complete execution timing
            execution_result = None
            if self.execution_optimizer:
                # Calculate profit for execution tracking
                entry_value = exit_amount * exit_price  # Simplified
                exit_value = exit_amount * exit_price
                profit_usd = exit_value - entry_value - gas_fee_usd
                
                execution_result = await self.execution_optimizer.complete_execution_timing(
                    trade_id=session_id,
                    was_successful=profit_usd > 0,
                    profit_loss_usd=profit_usd,
                    gas_price_gwei=Decimal('30'),  # Would get from actual transaction
                    slippage_percentage=1.0  # Would calculate from actual prices
                )
            
            # Update session with results
            total_gas_fees = gas_fee_usd + (session.gas_fees_paid_usd or Decimal('0'))
            session.gas_fees_paid_usd = total_gas_fees
            session.total_execution_time = execution_time_seconds
            session.end_time = datetime.utcnow()
            session.current_phase = TradePhase.COMPLETE
            session.is_active = False
            
            # Calculate actual profit
            if profit_result and profit_result.get("success"):
                analysis = profit_result.get("trade_analysis")
                if analysis:
                    session.actual_profit_usd = analysis.net_profit_usd
            
            # Move to completed sessions
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            
            # Update daily metrics
            await self._update_daily_metrics(session)
            
            # Generate comprehensive analysis
            comprehensive_analysis = await self._generate_comprehensive_analysis(
                session, profit_result, execution_result
            )
            
            logger.info(f"✅ Trade session completed: {session_id} - "
                       f"Profit: ${session.actual_profit_usd:.2f}")
            
            return {
                "success": True,
                "session_completed": True,
                "session_summary": {
                    "session_id": session_id,
                    "strategy": session.strategy_name,
                    "token": session.token_symbol,
                    "duration_minutes": (session.end_time - session.start_time).total_seconds() / 60,
                    "actual_profit_usd": float(session.actual_profit_usd or 0),
                    "gas_fees_usd": float(session.gas_fees_paid_usd or 0),
                    "total_execution_time": session.total_execution_time
                },
                "profit_analysis": profit_result,
                "execution_analysis": execution_result,
                "comprehensive_analysis": comprehensive_analysis,
                "daily_metrics": self.daily_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to record trade exit: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard for personal trading."""
        try:
            logger.info("📊 Generating performance dashboard...")
            
            # Get data from all optimizers
            dashboard_data = {
                "user_wallet": self.user_wallet,
                "dashboard_generated": datetime.utcnow().isoformat(),
                "active_sessions": len(self.active_sessions),
                "completed_sessions": len(self.completed_sessions),
                "daily_metrics": self.daily_metrics
            }
            
            # Profit performance data
            if self.profit_optimizer:
                try:
                    profit_summary = await self.profit_optimizer.get_performance_summary(days=30)
                    dashboard_data["profit_performance"] = profit_summary
                except Exception as e:
                    logger.error(f"❌ Failed to get profit summary: {e}")
                    dashboard_data["profit_performance"] = {"error": str(e)}
            
            # Gas optimization data
            if self.gas_optimizer:
                try:
                    gas_report = await self.gas_optimizer.get_gas_efficiency_report(days=30)
                    dashboard_data["gas_efficiency"] = gas_report
                except Exception as e:
                    logger.error(f"❌ Failed to get gas report: {e}")
                    dashboard_data["gas_efficiency"] = {"error": str(e)}
            
            # Execution performance data
            if self.execution_optimizer:
                try:
                    execution_report = await self.execution_optimizer.get_execution_performance_report(days=30)
                    dashboard_data["execution_performance"] = execution_report
                except Exception as e:
                    logger.error(f"❌ Failed to get execution report: {e}")
                    dashboard_data["execution_performance"] = {"error": str(e)}
            
            # Generate unified recommendations
            dashboard_data["unified_recommendations"] = await self._generate_unified_recommendations()
            
            # Calculate overall performance score
            dashboard_data["overall_performance_score"] = await self._calculate_overall_performance_score()
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate performance dashboard: {e}")
            return {"error": str(e)}
    
    async def optimize_next_trade(
        self,
        strategy_name: str,
        token_symbol: str,
        trade_value_usd: Decimal,
        urgency: str = "normal"
    ) -> Dict[str, Any]:
        """Get optimization recommendations for next trade."""
        try:
            logger.info(f"🎯 Optimizing next trade: {token_symbol} (${trade_value_usd})")
            
            optimizations = {
                "trade_details": {
                    "strategy": strategy_name,
                    "token": token_symbol,
                    "value_usd": float(trade_value_usd),
                    "urgency": urgency
                }
            }
            
            # Get gas optimization
            if self.gas_optimizer:
                try:
                    gas_opt = await self.gas_optimizer.optimize_gas_for_trade(
                        network=NetworkType.ETHEREUM,  # Default network
                        trade_value_usd=trade_value_usd,
                        urgency=urgency
                    )
                    optimizations["gas_optimization"] = {
                        "recommended_strategy": gas_opt.recommended_strategy.value,
                        "recommended_gas_price_gwei": float(gas_opt.recommended_gas_price_gwei),
                        "estimated_cost_usd": float(gas_opt.estimated_cost_usd),
                        "reasoning": gas_opt.reasoning
                    }
                except Exception as e:
                    logger.error(f"❌ Gas optimization failed: {e}")
                    optimizations["gas_optimization"] = {"error": str(e)}
            
            # Get execution optimization
            if self.execution_optimizer:
                try:
                    exec_priority = ExecutionPriority(urgency) if urgency in [p.value for p in ExecutionPriority] else ExecutionPriority.NORMAL
                    exec_opt = await self.execution_optimizer.optimize_execution_speed(
                        strategy_name=strategy_name,
                        priority=exec_priority
                    )
                    optimizations["execution_optimization"] = exec_opt
                except Exception as e:
                    logger.error(f"❌ Execution optimization failed: {e}")
                    optimizations["execution_optimization"] = {"error": str(e)}
            
            # Get strategy-specific recommendations
            if self.profit_optimizer:
                try:
                    strategy_opt = await self.profit_optimizer.optimize_strategy_parameters(strategy_name)
                    optimizations["strategy_optimization"] = strategy_opt
                except Exception as e:
                    logger.error(f"❌ Strategy optimization failed: {e}")
                    optimizations["strategy_optimization"] = {"error": str(e)}
            
            # Generate unified recommendations
            optimizations["unified_recommendations"] = await self._generate_trade_recommendations(
                strategy_name, token_symbol, trade_value_usd, urgency
            )
            
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize next trade: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _initialize_profit_optimizer(self) -> None:
        """Initialize profit optimization component."""
        try:
            self.profit_optimizer = await get_trading_performance_optimizer(self.user_wallet)
            logger.info("✅ Profit optimizer initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize profit optimizer: {e}")
            raise
    
    async def _initialize_gas_optimizer(self) -> None:
        """Initialize gas optimization component."""
        try:
            self.gas_optimizer = await get_gas_optimizer(self.user_wallet)
            logger.info("✅ Gas optimizer initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize gas optimizer: {e}")
            raise
    
    async def _initialize_execution_optimizer(self) -> None:
        """Initialize execution optimization component."""
        try:
            self.execution_optimizer = await get_execution_optimizer(self.user_wallet)
            logger.info("✅ Execution optimizer initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize execution optimizer: {e}")
            raise
    
    async def _load_daily_metrics(self) -> None:
        """Load daily trading metrics."""
        try:
            # TODO: Load from database
            today = datetime.utcnow().date()
            
            # Calculate from completed sessions today
            today_sessions = [
                s for s in self.completed_sessions
                if s.start_time.date() == today
            ]
            
            if today_sessions:
                self.daily_metrics = {
                    "trades_today": len(today_sessions),
                    "profit_today": sum(s.actual_profit_usd or Decimal('0') for s in today_sessions),
                    "gas_fees_today": sum(s.gas_fees_paid_usd or Decimal('0') for s in today_sessions),
                    "success_rate_today": (len([s for s in today_sessions if (s.actual_profit_usd or 0) > 0]) / len(today_sessions)) * 100
                }
            
            logger.debug("📊 Daily metrics loaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to load daily metrics: {e}")
    
    async def _update_daily_metrics(self, session: PersonalTradingSession) -> None:
        """Update daily metrics with completed session."""
        try:
            self.daily_metrics["trades_today"] += 1
            self.daily_metrics["profit_today"] += session.actual_profit_usd or Decimal('0')
            self.daily_metrics["gas_fees_today"] += session.gas_fees_paid_usd or Decimal('0')
            
            # Recalculate success rate
            today_sessions = [
                s for s in self.completed_sessions
                if s.start_time.date() == datetime.utcnow().date()
            ]
            
            successful_today = len([s for s in today_sessions if (s.actual_profit_usd or 0) > 0])
            self.daily_metrics["success_rate_today"] = (successful_today / len(today_sessions)) * 100 if today_sessions else 0
            
            logger.debug("📊 Daily metrics updated")
            
        except Exception as e:
            logger.error(f"❌ Failed to update daily metrics: {e}")
    
    async def _get_session_recommendations(self, session: PersonalTradingSession) -> List[str]:
        """Get recommendations for starting trading session."""
        recommendations = []
        
        try:
            # Strategy-specific recommendations
            if session.strategy_name == "arbitrage":
                recommendations.append("Monitor gas prices closely for arbitrage opportunities")
                recommendations.append("Use fast execution priority for time-sensitive arbitrage")
            elif session.strategy_name == "momentum":
                recommendations.append("Set tight stop-losses for momentum trades")
                recommendations.append("Consider market volatility in position sizing")
            
            # Priority-specific recommendations
            if session.priority == ExecutionPriority.CRITICAL:
                recommendations.append("High gas prices recommended for critical priority")
                recommendations.append("Monitor execution closely for immediate opportunities")
            elif session.priority == ExecutionPriority.LOW:
                recommendations.append("Use patient execution for cost optimization")
                recommendations.append("Consider timing trades during low gas periods")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get session recommendations: {e}")
            return []
    
    async def _generate_comprehensive_analysis(
        self,
        session: PersonalTradingSession,
        profit_result: Optional[Dict[str, Any]],
        execution_result: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis combining all optimization components."""
        try:
            analysis = {
                "session_id": session.session_id,
                "overall_success": (session.actual_profit_usd or 0) > 0,
                "profit_analysis": {},
                "efficiency_analysis": {},
                "recommendations": []
            }
            
            # Profit analysis
            if profit_result and profit_result.get("success"):
                trade_analysis = profit_result.get("trade_analysis", {})
                analysis["profit_analysis"] = {
                    "net_profit_usd": float(session.actual_profit_usd or 0),
                    "gas_fees_usd": float(session.gas_fees_paid_usd or 0),
                    "profit_after_fees": float((session.actual_profit_usd or 0) - (session.gas_fees_paid_usd or 0)),
                    "hold_time_minutes": trade_analysis.get("hold_time_minutes", 0),
                    "execution_speed_seconds": trade_analysis.get("execution_speed_seconds", 0)
                }
            
            # Efficiency analysis
            if execution_result:
                timing_breakdown = execution_result.get("timing_breakdown", {})
                analysis["efficiency_analysis"] = {
                    "total_execution_time": session.total_execution_time,
                    "timing_breakdown": timing_breakdown,
                    "efficiency_score": execution_result.get("performance_analysis", {}).get("speed_score", 0)
                }
            
            # Generate recommendations
            recommendations = []
            
            # Profit-based recommendations
            if (session.actual_profit_usd or 0) <= 0:
                recommendations.append("Consider adjusting strategy parameters to improve profitability")
            
            # Gas efficiency recommendations
            gas_ratio = float(session.gas_fees_paid_usd or 0) / max(float(abs(session.actual_profit_usd or 0.01)), 0.01)
            if gas_ratio > 0.3:  # Gas fees > 30% of profit
                recommendations.append("High gas fees relative to profit - consider larger position sizes or better timing")
            
            # Execution speed recommendations
            if session.total_execution_time and session.total_execution_time > 60:
                recommendations.append("Slow execution detected - consider optimizing for speed")
            
            analysis["recommendations"] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to generate comprehensive analysis: {e}")
            return {"error": str(e)}
    
    async def _generate_unified_recommendations(self) -> List[Dict[str, Any]]:
        """Generate unified recommendations across all optimization components."""
        recommendations = []
        
        try:
            # Get recommendations from each optimizer
            if self.profit_optimizer:
                try:
                    profit_suggestions = await self.profit_optimizer.get_performance_summary()
                    profit_recs = profit_suggestions.get("optimization_suggestions", [])
                    for rec in profit_recs[:3]:  # Top 3 profit recommendations
                        recommendations.append({
                            "type": "profit_optimization",
                            "priority": rec.get("priority", "medium"),
                            "message": rec.get("suggestion", ""),
                            "component": "profit_optimizer"
                        })
                except Exception as e:
                    logger.error(f"❌ Failed to get profit recommendations: {e}")
            
            if self.gas_optimizer:
                try:
                    gas_report = await self.gas_optimizer.get_gas_efficiency_report()
                    gas_recs = gas_report.get("optimization_recommendations", [])
                    for rec in gas_recs[:2]:  # Top 2 gas recommendations
                        recommendations.append({
                            "type": "gas_optimization",
                            "priority": rec.get("priority", "medium"),
                            "message": rec.get("message", ""),
                            "component": "gas_optimizer"
                        })
                except Exception as e:
                    logger.error(f"❌ Failed to get gas recommendations: {e}")
            
            # Add general performance recommendations
            if len(self.completed_sessions) > 0:
                recent_sessions = self.completed_sessions[-10:]  # Last 10 sessions
                success_rate = len([s for s in recent_sessions if (s.actual_profit_usd or 0) > 0]) / len(recent_sessions) * 100
                
                if success_rate < 60:
                    recommendations.append({
                        "type": "strategy_review",
                        "priority": "high",
                        "message": f"Recent success rate is {success_rate:.1f}%. Consider reviewing trading strategies.",
                        "component": "performance_manager"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate unified recommendations: {e}")
            return []
    
    async def _calculate_overall_performance_score(self) -> Dict[str, Any]:
        """Calculate overall performance score across all metrics."""
        try:
            scores = {"profit_score": 0, "efficiency_score": 0, "gas_score": 0, "overall_score": 0}
            
            if len(self.completed_sessions) > 0:
                # Profit score based on success rate and profit amounts
                profitable_sessions = [s for s in self.completed_sessions if (s.actual_profit_usd or 0) > 0]
                profit_score = (len(profitable_sessions) / len(self.completed_sessions)) * 100
                scores["profit_score"] = min(100, profit_score)
                
                # Efficiency score based on execution times
                execution_times = [s.total_execution_time for s in self.completed_sessions if s.total_execution_time]
                if execution_times:
                    avg_execution_time = sum(execution_times) / len(execution_times)
                    efficiency_score = max(0, min(100, (60 / max(avg_execution_time, 1)) * 100))  # 60s target
                    scores["efficiency_score"] = efficiency_score
                
                # Gas score based on gas efficiency
                total_profit = sum(s.actual_profit_usd or Decimal('0') for s in self.completed_sessions)
                total_gas = sum(s.gas_fees_paid_usd or Decimal('0') for s in self.completed_sessions)
                
                if total_profit > 0:
                    gas_efficiency = float(total_gas) / float(total_profit)
                    gas_score = max(0, min(100, (1 - min(gas_efficiency, 1)) * 100))
                    scores["gas_score"] = gas_score
                
                # Overall score (weighted average)
                scores["overall_score"] = (
                    scores["profit_score"] * 0.5 +
                    scores["efficiency_score"] * 0.3 +
                    scores["gas_score"] * 0.2
                )
            
            return scores
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate performance score: {e}")
            return {"error": str(e)}
    
    async def _generate_trade_recommendations(
        self,
        strategy_name: str,
        token_symbol: str,
        trade_value_usd: Decimal,
        urgency: str
    ) -> List[Dict[str, Any]]:
        """Generate unified recommendations for specific trade."""
        recommendations = []
        
        try:
            # Strategy-specific recommendations
            if strategy_name == "arbitrage":
                recommendations.append({
                    "type": "strategy_specific",
                    "message": "For arbitrage: Monitor gas prices and execution speed closely",
                    "priority": "high"
                })
                recommendations.append({
                    "type": "timing",
                    "message": "Execute quickly - arbitrage opportunities are time-sensitive",
                    "priority": "high"
                })
            
            # Value-based recommendations
            if trade_value_usd < 100:
                recommendations.append({
                    "type": "position_sizing",
                    "message": f"Small trade size (${trade_value_usd}) - gas fees may impact profitability significantly",
                    "priority": "medium"
                })
            elif trade_value_usd > 1000:
                recommendations.append({
                    "type": "risk_management",
                    "message": f"Large trade size (${trade_value_usd}) - ensure proper risk management",
                    "priority": "high"
                })
            
            # Urgency-based recommendations
            if urgency == "critical":
                recommendations.append({
                    "type": "execution",
                    "message": "Critical urgency - use highest gas prices and fastest execution",
                    "priority": "critical"
                })
            elif urgency == "low":
                recommendations.append({
                    "type": "cost_optimization",
                    "message": "Low urgency - optimize for cost savings with patient execution",
                    "priority": "medium"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate trade recommendations: {e}")
            return []


# Factory function
async def get_trading_performance_manager(user_wallet: str) -> TradingPerformanceManager:
    """Get initialized trading performance manager."""
    manager = TradingPerformanceManager(user_wallet)
    await manager.initialize()
    return manager