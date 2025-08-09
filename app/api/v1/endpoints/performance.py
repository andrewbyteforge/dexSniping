"""
Phase 5A.1: Trading Performance Optimization API
File: app/api/v1/endpoints/performance.py

Personal trading performance API for real profit tracking and optimization.
Provides endpoints for tracking trades, analyzing performance, and getting optimization suggestions.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from app.core.performance.trading_optimizer import (
    get_trading_performance_optimizer,
    TradingPerformanceOptimizer,
    PerformanceMetric
)
from app.core.dependencies import get_database_session
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/performance", tags=["Performance Optimization"])


# ==================== REQUEST/RESPONSE MODELS ====================

class TradeEntryRequest(BaseModel):
    """Request model for tracking trade entry."""
    trade_id: str = Field(..., description="Unique trade identifier")
    strategy_name: str = Field(..., description="Strategy used for trade")
    token_symbol: str = Field(..., description="Token symbol (e.g., 'PEPE')")
    entry_price: Decimal = Field(..., description="Entry price in USD")
    entry_amount: Decimal = Field(..., description="Amount of tokens purchased")
    gas_fee_usd: Decimal = Field(..., description="Gas fee paid in USD")


class TradeExitRequest(BaseModel):
    """Request model for tracking trade exit."""
    trade_id: str = Field(..., description="Trade identifier")
    exit_price: Decimal = Field(..., description="Exit price in USD")
    exit_amount: Decimal = Field(..., description="Amount of tokens sold")
    gas_fee_usd: Decimal = Field(..., description="Gas fee paid in USD")
    execution_time_seconds: float = Field(..., description="Time taken for execution")


class StrategyOptimizationRequest(BaseModel):
    """Request model for strategy optimization."""
    strategy_name: str = Field(..., description="Strategy to optimize")
    min_trades_required: int = Field(default=10, description="Minimum trades for optimization")


class PerformanceSummaryResponse(BaseModel):
    """Response model for performance summary."""
    user_wallet: str
    summary_period_days: int
    overall_metrics: Dict[str, Any]
    time_based_performance: Dict[str, Any]
    strategy_performance: Dict[str, Any]
    top_performing_strategies: List[Dict[str, Any]]
    optimization_suggestions: List[Dict[str, Any]]
    last_updated: str


# ==================== TRADE TRACKING ENDPOINTS ====================

@router.post("/track/entry")
async def track_trade_entry(
    request: TradeEntryRequest,
    user_wallet: str = Query(..., description="User wallet address"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Track trade entry for profit analysis.
    
    Records trade entry details for later profit/loss calculation
    and performance optimization analysis.
    """
    try:
        logger.info(f"📈 Tracking trade entry: {request.trade_id} for {user_wallet[:10]}...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Track trade entry
        success = await optimizer.track_trade_entry(
            trade_id=request.trade_id,
            strategy_name=request.strategy_name,
            token_symbol=request.token_symbol,
            entry_price=request.entry_price,
            entry_amount=request.entry_amount,
            gas_fee_usd=request.gas_fee_usd
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to track trade entry")
        
        return {
            "success": True,
            "message": f"Trade entry tracked successfully: {request.trade_id}",
            "trade_details": {
                "trade_id": request.trade_id,
                "strategy": request.strategy_name,
                "token": request.token_symbol,
                "entry_price": float(request.entry_price),
                "entry_amount": float(request.entry_amount),
                "gas_fee_usd": float(request.gas_fee_usd),
                "entry_value_usd": float(request.entry_price * request.entry_amount),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to track trade entry: {e}")
        raise HTTPException(status_code=500, detail=f"Trade entry tracking failed: {e}")


@router.post("/track/exit")
async def track_trade_exit(
    request: TradeExitRequest,
    user_wallet: str = Query(..., description="User wallet address"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Track trade exit and calculate profit/loss.
    
    Records trade exit details, calculates actual profit/loss including gas fees,
    and generates optimization suggestions.
    """
    try:
        logger.info(f"💰 Tracking trade exit: {request.trade_id} for {user_wallet[:10]}...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Track trade exit and calculate profit
        result = await optimizer.track_trade_exit(
            trade_id=request.trade_id,
            exit_price=request.exit_price,
            exit_amount=request.exit_amount,
            gas_fee_usd=request.gas_fee_usd,
            execution_time_seconds=request.execution_time_seconds
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error occurred")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Extract analysis results
        analysis = result["trade_analysis"]
        profit_result = result["profit_result"]
        suggestions = result["optimization_suggestions"]
        
        return {
            "success": True,
            "message": f"Trade exit tracked successfully: {request.trade_id}",
            "trade_analysis": {
                "trade_id": analysis.trade_id,
                "strategy_used": analysis.strategy_used,
                "token_symbol": analysis.token_symbol,
                "entry_details": {
                    "price": float(analysis.entry_price),
                    "amount": float(analysis.entry_amount),
                    "value_usd": float(analysis.entry_price * analysis.entry_amount),
                    "gas_fee_usd": float(analysis.entry_gas_fee_usd)
                },
                "exit_details": {
                    "price": float(analysis.exit_price),
                    "amount": float(analysis.exit_amount),
                    "value_usd": float(analysis.exit_price * analysis.exit_amount),
                    "gas_fee_usd": float(analysis.exit_gas_fee_usd)
                },
                "profit_analysis": profit_result,
                "hold_time_minutes": analysis.hold_time_minutes,
                "execution_speed_seconds": analysis.execution_speed_seconds
            },
            "optimization_suggestions": suggestions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to track trade exit: {e}")
        raise HTTPException(status_code=500, detail=f"Trade exit tracking failed: {e}")


# ==================== PERFORMANCE ANALYSIS ENDPOINTS ====================

@router.get("/summary")
async def get_performance_summary(
    user_wallet: str = Query(..., description="User wallet address"),
    days: int = Query(30, description="Days of history to analyze"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> PerformanceSummaryResponse:
    """
    Get comprehensive performance summary.
    
    Returns detailed analysis of trading performance including:
    - Overall profit/loss metrics
    - Strategy-specific performance
    - Time-based analysis
    - Optimization suggestions
    """
    try:
        logger.info(f"📊 Getting performance summary for {user_wallet[:10]} ({days} days)...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Get performance summary
        summary = await optimizer.get_performance_summary(days=days)
        
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        return PerformanceSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get performance summary: {e}")
        raise HTTPException(status_code=500, detail=f"Performance summary failed: {e}")


@router.get("/metrics/detailed")
async def get_detailed_metrics(
    user_wallet: str = Query(..., description="User wallet address"),
    metric_type: str = Query("all", description="Specific metric type to retrieve"),
    period: str = Query("monthly", description="Time period: daily, weekly, monthly"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Get detailed performance metrics.
    
    Provides granular performance data for specific metrics and time periods.
    """
    try:
        logger.info(f"📊 Getting detailed metrics for {user_wallet[:10]}...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Calculate specific metrics based on request
        if metric_type == "profit_analysis":
            metrics = await optimizer._calculate_daily_performance(30)
        elif metric_type == "strategy_breakdown":
            metrics = {
                "strategies": optimizer.current_metrics.strategy_performance
            }
        elif metric_type == "gas_analysis":
            metrics = await _calculate_gas_analysis(optimizer)
        else:
            # Return all metrics
            metrics = await optimizer.get_performance_summary()
        
        return {
            "success": True,
            "metric_type": metric_type,
            "period": period,
            "data": metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get detailed metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Detailed metrics failed: {e}")


# ==================== STRATEGY OPTIMIZATION ENDPOINTS ====================

@router.post("/optimize/strategy")
async def optimize_strategy(
    request: StrategyOptimizationRequest,
    user_wallet: str = Query(..., description="User wallet address"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Optimize specific trading strategy based on performance data.
    
    Analyzes historical performance and provides recommendations
    for improving strategy parameters.
    """
    try:
        logger.info(f"🎯 Optimizing strategy {request.strategy_name} for {user_wallet[:10]}...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Optimize strategy
        optimization_result = await optimizer.optimize_strategy_parameters(request.strategy_name)
        
        if "error" in optimization_result:
            raise HTTPException(status_code=400, detail=optimization_result["error"])
        
        return {
            "success": True,
            "message": f"Strategy optimization completed for {request.strategy_name}",
            "optimization_result": optimization_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to optimize strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Strategy optimization failed: {e}")


@router.get("/suggestions")
async def get_optimization_suggestions(
    user_wallet: str = Query(..., description="User wallet address"),
    priority: Optional[str] = Query(None, description="Filter by priority: high, medium, low"),
    limit: int = Query(10, description="Maximum number of suggestions"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Get personalized optimization suggestions.
    
    Returns actionable recommendations for improving trading performance
    based on recent trading activity and patterns.
    """
    try:
        logger.info(f"💡 Getting optimization suggestions for {user_wallet[:10]}...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Filter suggestions by priority if specified
        suggestions = optimizer.optimization_suggestions
        
        if priority:
            suggestions = [s for s in suggestions if s.get("priority") == priority]
        
        # Limit results
        suggestions = suggestions[-limit:] if suggestions else []
        
        # Generate fresh suggestions based on recent activity
        fresh_suggestions = await _generate_fresh_suggestions(optimizer)
        
        return {
            "success": True,
            "total_suggestions": len(suggestions) + len(fresh_suggestions),
            "historical_suggestions": suggestions,
            "fresh_suggestions": fresh_suggestions,
            "priority_filter": priority,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization suggestions failed: {e}")


# ==================== PROFIT ANALYSIS ENDPOINTS ====================

@router.get("/profit/analysis")
async def get_profit_analysis(
    user_wallet: str = Query(..., description="User wallet address"),
    days: int = Query(30, description="Days to analyze"),
    include_unrealized: bool = Query(True, description="Include unrealized P&L"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Get detailed profit/loss analysis.
    
    Provides comprehensive P&L breakdown including:
    - Realized vs unrealized profits
    - Profit by strategy
    - Gas fee analysis
    - Time-based profit trends
    """
    try:
        logger.info(f"💰 Analyzing profit for {user_wallet[:10]} ({days} days)...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Calculate profit analysis
        analysis = await _calculate_comprehensive_profit_analysis(
            optimizer, days, include_unrealized
        )
        
        return {
            "success": True,
            "analysis_period_days": days,
            "include_unrealized": include_unrealized,
            "profit_analysis": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze profit: {e}")
        raise HTTPException(status_code=500, detail=f"Profit analysis failed: {e}")


@router.get("/gas/optimization")
async def get_gas_optimization_analysis(
    user_wallet: str = Query(..., description="User wallet address"),
    days: int = Query(30, description="Days to analyze"),
    optimizer: TradingPerformanceOptimizer = Depends(lambda: None)
) -> Dict[str, Any]:
    """
    Get gas fee optimization analysis.
    
    Analyzes gas fee patterns and provides recommendations
    for reducing transaction costs.
    """
    try:
        logger.info(f"⛽ Analyzing gas optimization for {user_wallet[:10]}...")
        
        # Get optimizer instance
        if not optimizer:
            optimizer = await get_trading_performance_optimizer(user_wallet)
        
        # Calculate gas analysis
        gas_analysis = await _calculate_gas_analysis(optimizer)
        
        return {
            "success": True,
            "analysis_period_days": days,
            "gas_analysis": gas_analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze gas optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Gas optimization analysis failed: {e}")


# ==================== HELPER FUNCTIONS ====================

async def _calculate_gas_analysis(optimizer: TradingPerformanceOptimizer) -> Dict[str, Any]:
    """Calculate gas fee analysis and optimization recommendations."""
    try:
        total_gas_fees = float(optimizer.current_metrics.total_gas_fees_usd)
        total_profit = float(optimizer.current_metrics.net_profit_usd)
        total_trades = optimizer.current_metrics.total_trades
        
        # Calculate gas efficiency metrics
        avg_gas_per_trade = total_gas_fees / max(total_trades, 1)
        gas_to_profit_ratio = (total_gas_fees / max(abs(total_profit), 1)) * 100
        
        # Generate recommendations
        recommendations = []
        
        if avg_gas_per_trade > 10:  # $10+ average gas
            recommendations.append({
                "type": "reduce_frequency",
                "message": f"High average gas cost (${avg_gas_per_trade:.2f}). Consider fewer, larger trades.",
                "potential_savings_percent": 20
            })
        
        if gas_to_profit_ratio > 25:  # Gas fees > 25% of profit
            recommendations.append({
                "type": "optimize_timing",
                "message": f"Gas fees consume {gas_to_profit_ratio:.1f}% of profit. Trade during low gas periods.",
                "potential_savings_percent": 15
            })
        
        return {
            "total_gas_fees_usd": total_gas_fees,
            "average_gas_per_trade": avg_gas_per_trade,
            "gas_to_profit_ratio": gas_to_profit_ratio,
            "recommendations": recommendations,
            "gas_efficiency_score": max(0, 100 - gas_to_profit_ratio)
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating gas analysis: {e}")
        return {}


async def _calculate_comprehensive_profit_analysis(
    optimizer: TradingPerformanceOptimizer,
    days: int,
    include_unrealized: bool
) -> Dict[str, Any]:
    """Calculate comprehensive profit analysis."""
    try:
        metrics = optimizer.current_metrics
        
        # Basic profit metrics
        profit_analysis = {
            "realized_profit_usd": float(metrics.net_profit_usd),
            "total_gas_fees_usd": float(metrics.total_gas_fees_usd),
            "gross_profit_usd": float(metrics.net_profit_usd + metrics.total_gas_fees_usd),
            "overall_roi_percent": metrics.overall_roi,
            "total_trades": metrics.total_trades,
            "profitable_trades": metrics.profitable_trades,
            "win_rate_percent": (metrics.profitable_trades / max(metrics.total_trades, 1)) * 100
        }
        
        # Strategy breakdown
        strategy_profits = {}
        for name, strategy in metrics.strategy_performance.items():
            strategy_profits[name] = {
                "net_profit_usd": float(strategy.net_profit_usd),
                "win_rate": strategy.win_rate,
                "total_trades": strategy.total_trades,
                "profit_factor": strategy.profit_factor
            }
        
        profit_analysis["strategy_breakdown"] = strategy_profits
        
        # TODO: Add time-based profit trends, unrealized P&L
        
        return profit_analysis
        
    except Exception as e:
        logger.error(f"❌ Error calculating comprehensive profit analysis: {e}")
        return {}


async def _generate_fresh_suggestions(optimizer: TradingPerformanceOptimizer) -> List[Dict[str, Any]]:
    """Generate fresh optimization suggestions based on current performance."""
    suggestions = []
    
    try:
        metrics = optimizer.current_metrics
        
        # Overall performance suggestions
        if metrics.total_trades > 0:
            win_rate = (metrics.profitable_trades / metrics.total_trades) * 100
            
            if win_rate < 50:
                suggestions.append({
                    "type": "strategy_review",
                    "priority": "high",
                    "suggestion": f"Win rate is {win_rate:.1f}%. Consider reviewing strategy parameters or switching to better performing strategies.",
                    "action": "review_strategies"
                })
            
            # Gas efficiency suggestion
            gas_ratio = float(metrics.total_gas_fees_usd) / max(float(abs(metrics.net_profit_usd)), 1) * 100
            if gas_ratio > 30:
                suggestions.append({
                    "type": "gas_optimization",
                    "priority": "medium",
                    "suggestion": f"Gas fees consume {gas_ratio:.1f}% of profits. Consider optimizing trade timing and sizes.",
                    "action": "optimize_gas_usage"
                })
        
        return suggestions
        
    except Exception as e:
        logger.error(f"❌ Error generating fresh suggestions: {e}")
        return []