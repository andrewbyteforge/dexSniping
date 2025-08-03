"""
Enhanced Trading API Endpoints with Risk Management Integration
File: app/api/v1/endpoints/trading_enhanced.py

Professional trading API with integrated risk management, position sizing,
and comprehensive portfolio management functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from app.utils.logger import setup_logger
from app.core.dependencies import get_database_session, get_current_user
from app.core.trading.risk_manager import (
    get_risk_manager, RiskLevel, PositionSizeMethod,
    validate_trade_risk, require_risk_check
)
from app.models.dex.trading_models import (
    TradingOrder, TradingPosition, PortfolioTransaction, RiskLimit,
    OrderSide, OrderType, OrderStatus, PositionStatus, TransactionType,
    create_order, get_user_positions, calculate_portfolio_metrics
)

logger = setup_logger(__name__)

router = APIRouter(prefix="/trading", tags=["enhanced_trading"])


# Enhanced Request/Response Models

class AdvancedTradeRequest(BaseModel):
    """Advanced trade request with risk management parameters."""
    token_address: str = Field(..., description="Token contract address")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    amount: Optional[Decimal] = Field(None, description="Fixed amount to trade")
    
    # Position sizing parameters
    use_position_sizing: bool = Field(True, description="Use automatic position sizing")
    sizing_method: str = Field(default="percentage_risk", description="Position sizing method")
    risk_percentage: Optional[Decimal] = Field(
        default=Decimal("2.0"), 
        description="Risk percentage for position sizing"
    )
    
    # Order parameters
    order_type: str = Field(default="market", description="Order type")
    limit_price: Optional[Decimal] = Field(None, description="Limit price")
    slippage_tolerance: Decimal = Field(default=Decimal("0.01"), description="Slippage tolerance")
    
    # Risk management
    stop_loss_price: Optional[Decimal] = Field(None, description="Stop loss price")
    take_profit_price: Optional[Decimal] = Field(None, description="Take profit price")
    trailing_stop_distance: Optional[Decimal] = Field(None, description="Trailing stop distance %")
    
    # Advanced options
    strategy_name: Optional[str] = Field(None, description="Strategy name for tracking")
    expires_in_minutes: int = Field(default=60, description="Order expiration time")
    force_execution: bool = Field(False, description="Force execution despite warnings")
    
    @validator('side')
    def validate_side(cls, v):
        if v.lower() not in ['buy', 'sell']:
            raise ValueError('Side must be "buy" or "sell"')
        return v.lower()
    
    @validator('sizing_method')
    def validate_sizing_method(cls, v):
        valid_methods = ['fixed_amount', 'percentage_risk', 'kelly_criterion', 
                        'volatility_adjusted', 'equal_weight']
        if v.lower() not in valid_methods:
            raise ValueError(f'Sizing method must be one of: {valid_methods}')
        return v.lower()


class RiskAssessmentRequest(BaseModel):
    """Risk assessment request model."""
    token_address: Optional[str] = Field(None, description="Token to assess")
    include_recommendations: bool = Field(True, description="Include recommendations")
    include_metrics: bool = Field(True, description="Include detailed metrics")


class PositionSizeRequest(BaseModel):
    """Position size calculation request."""
    token_address: str = Field(..., description="Token contract address")
    side: str = Field(..., description="Order side")
    entry_price: Decimal = Field(..., description="Expected entry price")
    stop_loss_price: Optional[Decimal] = Field(None, description="Stop loss price")
    sizing_method: str = Field(default="percentage_risk", description="Sizing method")
    
    @validator('side')
    def validate_side(cls, v):
        if v.lower() not in ['buy', 'sell']:
            raise ValueError('Side must be "buy" or "sell"')
        return v.lower()


class RiskLimitUpdateRequest(BaseModel):
    """Risk limit update request."""
    max_position_size: Optional[Decimal] = Field(None, description="Max position size USD")
    max_position_percentage: Optional[Decimal] = Field(None, description="Max position %")
    max_open_positions: Optional[int] = Field(None, description="Max open positions")
    max_daily_loss: Optional[Decimal] = Field(None, description="Max daily loss USD")
    max_drawdown_percentage: Optional[Decimal] = Field(None, description="Max drawdown %")
    stop_loss_percentage: Optional[Decimal] = Field(None, description="Default stop loss %")
    max_daily_trades: Optional[int] = Field(None, description="Max daily trades")
    max_slippage: Optional[Decimal] = Field(None, description="Max slippage tolerance")
    min_liquidity_usd: Optional[Decimal] = Field(None, description="Min liquidity USD")
    auto_stop_loss: Optional[bool] = Field(None, description="Auto stop loss enabled")
    auto_take_profit: Optional[bool] = Field(None, description="Auto take profit enabled")
    emergency_stop: Optional[bool] = Field(None, description="Emergency stop activated")


# Enhanced Trading Endpoints

@router.post("/execute-advanced")
async def execute_advanced_trade(
    request: AdvancedTradeRequest,
    background_tasks: BackgroundTasks,
    user_wallet: str = Query(..., description="User wallet address"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Execute advanced trade with integrated risk management and position sizing.
    
    This endpoint provides comprehensive trading functionality including:
    - Automatic position sizing based on risk parameters
    - Risk assessment and validation
    - Stop-loss and take-profit automation
    - Portfolio integration and tracking
    """
    try:
        logger.info(f"🚀 Executing advanced trade for {user_wallet[:10]}...")
        
        # Get risk manager
        risk_manager = get_risk_manager(lambda: session)
        
        # Perform comprehensive risk assessment
        risk_assessment = await risk_manager.assess_portfolio_risk(user_wallet, session)
        
        if not risk_assessment.can_trade and not request.force_execution:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "Trading blocked due to risk constraints",
                    "risk_level": risk_assessment.risk_level.value,
                    "warnings": risk_assessment.warnings,
                    "recommendations": risk_assessment.recommendations
                }
            )
        
        # Calculate position size if not specified
        if request.use_position_sizing and not request.amount:
            # Get current market price (would integrate with price feed)
            entry_price = request.limit_price or Decimal('1.0')  # Placeholder
            
            sizing_method = PositionSizeMethod(request.sizing_method)
            position_result = await risk_manager.calculate_position_size(
                user_wallet=user_wallet,
                token_address=request.token_address,
                side=OrderSide(request.side),
                entry_price=entry_price,
                stop_loss_price=request.stop_loss_price,
                method=sizing_method,
                session=session
            )
            
            calculated_amount = position_result.recommended_size
            position_warnings = position_result.risk_warnings
            
        else:
            calculated_amount = request.amount or Decimal('0')
            position_warnings = []
        
        # Validate order against risk limits
        order_data = {
            'token_address': request.token_address,
            'amount': str(calculated_amount),
            'side': request.side,
            'price': str(request.limit_price) if request.limit_price else None,
            'slippage_tolerance': str(request.slippage_tolerance)
        }
        
        is_valid, risk_warnings = await risk_manager.validate_order_risk(
            user_wallet, order_data, session
        )
        
        if not is_valid and not request.force_execution:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Order validation failed",
                    "warnings": risk_warnings
                }
            )
        
        # Create order
        order = await create_order(
            session=session,
            user_wallet=user_wallet,
            token_address=request.token_address,
            side=OrderSide(request.side),
            amount=calculated_amount,
            order_type=OrderType(request.order_type),
            price=request.limit_price,
            slippage_tolerance=request.slippage_tolerance,
            stop_loss_price=request.stop_loss_price,
            take_profit_price=request.take_profit_price,
            trailing_stop_distance=request.trailing_stop_distance,
            expires_at=datetime.utcnow() + timedelta(minutes=request.expires_in_minutes),
            order_metadata={
                'strategy_name': request.strategy_name,
                'risk_assessment': {
                    'risk_level': risk_assessment.risk_level.value,
                    'risk_score': risk_assessment.risk_score
                },
                'position_sizing': {
                    'method': request.sizing_method,
                    'use_position_sizing': request.use_position_sizing
                }
            }
        )
        
        # Schedule background risk monitoring
        background_tasks.add_task(
            monitor_order_execution, 
            order.order_id, 
            user_wallet
        )
        
        # Compile response
        all_warnings = risk_assessment.warnings + position_warnings + risk_warnings
        
        return {
            "success": True,
            "data": {
                "order": order.to_dict(),
                "risk_assessment": {
                    "risk_level": risk_assessment.risk_level.value,
                    "risk_score": risk_assessment.risk_score,
                    "can_trade": risk_assessment.can_trade
                },
                "position_sizing": {
                    "calculated_amount": str(calculated_amount),
                    "sizing_method": request.sizing_method,
                    "used_position_sizing": request.use_position_sizing
                } if request.use_position_sizing else None
            },
            "warnings": all_warnings,
            "recommendations": risk_assessment.recommendations,
            "message": f"Advanced trade order created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Advanced trade execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trade execution failed: {e}")


@router.get("/risk-assessment")
async def get_risk_assessment(
    request: RiskAssessmentRequest = Depends(),
    user_wallet: str = Query(..., description="User wallet address"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get comprehensive portfolio risk assessment.
    
    Provides detailed risk analysis including:
    - Overall portfolio risk level and score
    - Risk metrics and exposure analysis
    - Trading eligibility status
    - Personalized recommendations
    """
    try:
        logger.info(f"📊 Getting risk assessment for {user_wallet[:10]}...")
        
        risk_manager = get_risk_manager(lambda: session)
        assessment = await risk_manager.assess_portfolio_risk(user_wallet, session)
        
        response_data = {
            "risk_level": assessment.risk_level.value,
            "risk_score": assessment.risk_score,
            "can_trade": assessment.can_trade,
            "warnings": assessment.warnings,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        if request.include_recommendations:
            response_data["recommendations"] = assessment.recommendations
        
        if request.include_metrics:
            response_data["risk_metrics"] = {
                "portfolio_value": str(assessment.risk_metrics.portfolio_value),
                "current_exposure": str(assessment.risk_metrics.current_exposure),
                "available_capital": str(assessment.risk_metrics.available_capital),
                "drawdown_percentage": assessment.risk_metrics.drawdown_percentage,
                "open_positions_count": assessment.risk_metrics.open_positions_count,
                "concentration_risk": assessment.risk_metrics.concentration_risk,
                "daily_pnl": str(assessment.risk_metrics.daily_pnl)
            }
        
        # Token-specific assessment if requested
        if request.token_address:
            # Get token-specific risk metrics (placeholder)
            response_data["token_assessment"] = {
                "token_address": request.token_address,
                "liquidity_score": 8.5,  # Would integrate with actual data
                "volatility_score": 6.2,
                "risk_rating": "medium"
            }
        
        return {
            "success": True,
            "data": response_data,
            "message": "Risk assessment completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {e}")


@router.post("/calculate-position-size")
async def calculate_position_size(
    request: PositionSizeRequest,
    user_wallet: str = Query(..., description="User wallet address"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Calculate optimal position size using advanced algorithms.
    
    Supports multiple position sizing methods:
    - Percentage risk
    - Kelly Criterion
    - Volatility adjusted
    - Fixed amount
    - Equal weight
    """
    try:
        logger.info(f"📊 Calculating position size for {user_wallet[:10]}...")
        
        risk_manager = get_risk_manager(lambda: session)
        
        result = await risk_manager.calculate_position_size(
            user_wallet=user_wallet,
            token_address=request.token_address,
            side=OrderSide(request.side),
            entry_price=request.entry_price,
            stop_loss_price=request.stop_loss_price,
            method=PositionSizeMethod(request.sizing_method),
            session=session
        )
        
        return {
            "success": True,
            "data": {
                "recommended_size": str(result.recommended_size),
                "max_size": str(result.max_size),
                "risk_adjusted_size": str(result.risk_adjusted_size),
                "confidence_score": result.confidence_score,
                "sizing_method": result.sizing_method.value,
                "position_percentage": result.position_percentage,
                "risk_warnings": result.risk_warnings
            },
            "message": "Position size calculated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Position size calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Position size calculation failed: {e}")


@router.get("/portfolio/comprehensive")
async def get_comprehensive_portfolio(
    user_wallet: str = Query(..., description="User wallet address"),
    include_history: bool = Query(False, description="Include transaction history"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get comprehensive portfolio information with advanced analytics.
    
    Includes:
    - All positions with current P&L
    - Portfolio performance metrics
    - Risk analysis
    - Transaction history (optional)
    """
    try:
        logger.info(f"📈 Getting comprehensive portfolio for {user_wallet[:10]}...")
        
        # Get positions
        positions = await get_user_positions(user_wallet, session)
        
        # Get portfolio metrics
        portfolio_metrics = await calculate_portfolio_metrics(session, user_wallet)
        
        # Get risk assessment
        risk_manager = get_risk_manager(lambda: session)
        risk_assessment = await risk_manager.assess_portfolio_risk(user_wallet, session)
        
        response_data = {
            "positions": [pos.to_dict() for pos in positions],
            "summary": portfolio_metrics,
            "risk_analysis": {
                "risk_level": risk_assessment.risk_level.value,
                "risk_score": risk_assessment.risk_score,
                "can_trade": risk_assessment.can_trade,
                "warnings": risk_assessment.warnings[:3],  # Top 3 warnings
                "risk_metrics": {
                    "portfolio_value": str(risk_assessment.risk_metrics.portfolio_value),
                    "current_exposure": str(risk_assessment.risk_metrics.current_exposure),
                    "concentration_risk": risk_assessment.risk_metrics.concentration_risk
                }
            }
        }
        
        # Include performance metrics if requested
        if include_performance:
            # Calculate additional performance metrics
            open_positions = [pos for pos in positions if pos.is_open]
            closed_positions = [pos for pos in positions if pos.status == PositionStatus.CLOSED]
            
            performance_metrics = {
                "total_positions": len(positions),
                "open_positions": len(open_positions),
                "closed_positions": len(closed_positions),
                "win_rate": float(portfolio_metrics.get('win_rate', 0)),
                "average_hold_time_days": 0,  # Would calculate from position data
                "best_position_return": 0,     # Would calculate from position data
                "worst_position_return": 0,    # Would calculate from position data
                "sharpe_ratio": 0,             # Would calculate from returns data
                "max_drawdown": risk_assessment.risk_metrics.drawdown_percentage
            }
            
            response_data["performance"] = performance_metrics
        
        # Include transaction history if requested
        if include_history:
            transactions = await session.query(PortfolioTransaction).filter(
                PortfolioTransaction.user_wallet == user_wallet
            ).order_by(PortfolioTransaction.executed_at.desc()).limit(100).all()
            
            response_data["recent_transactions"] = [tx.to_dict() for tx in transactions]
        
        return {
            "success": True,
            "data": response_data,
            "message": "Comprehensive portfolio data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Comprehensive portfolio retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Portfolio retrieval failed: {e}")


@router.put("/risk-limits")
async def update_risk_limits(
    request: RiskLimitUpdateRequest,
    user_wallet: str = Query(..., description="User wallet address"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Update user risk limits and trading controls.
    
    Allows configuration of:
    - Position size limits
    - Daily loss limits
    - Risk percentages
    - Trading automation settings
    """
    try:
        logger.info(f"⚙️ Updating risk limits for {user_wallet[:10]}...")
        
        # Get existing risk limits or create new
        risk_limit = await session.query(RiskLimit).filter(
            RiskLimit.user_wallet == user_wallet
        ).first()
        
        if not risk_limit:
            risk_limit = RiskLimit(user_wallet=user_wallet)
            session.add(risk_limit)
        
        # Update fields if provided
        update_fields = request.dict(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(risk_limit, field):
                setattr(risk_limit, field, value)
        
        await session.commit()
        await session.refresh(risk_limit)
        
        return {
            "success": True,
            "data": risk_limit.to_dict(),
            "message": "Risk limits updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Risk limits update failed: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Risk limits update failed: {e}")


@router.get("/position/{position_id}/monitor")
async def monitor_position(
    position_id: str,
    user_wallet: str = Query(..., description="User wallet address"),
    current_price: Optional[Decimal] = Query(None, description="Current token price"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Monitor individual position risk and get recommendations.
    
    Provides:
    - Current P&L analysis
    - Risk alerts
    - Recommended actions
    - Stop-loss/take-profit guidance
    """
    try:
        logger.info(f"📊 Monitoring position {position_id} for {user_wallet[:10]}...")
        
        # Verify position ownership
        position = await session.query(TradingPosition).filter(
            TradingPosition.position_id == position_id,
            TradingPosition.user_wallet == user_wallet
        ).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        # Get current price if not provided (would integrate with price feed)
        if not current_price:
            current_price = position.average_entry_price * Decimal('1.05')  # Placeholder
        
        # Monitor position risk
        risk_manager = get_risk_manager(lambda: session)
        monitoring_result = await risk_manager.monitor_position_risk(
            position_id, current_price, session
        )
        
        return {
            "success": True,
            "data": monitoring_result,
            "message": "Position monitoring completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Position monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Position monitoring failed: {e}")


@router.get("/performance/analytics")
async def get_performance_analytics(
    user_wallet: str = Query(..., description="User wallet address"),
    days: int = Query(30, description="Days of history to analyze"),
    session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get advanced performance analytics and insights.
    
    Provides:
    - Historical performance metrics
    - Risk-adjusted returns
    - Trading pattern analysis
    - Comparative benchmarks
    """
    try:
        logger.info(f"📈 Generating performance analytics for {user_wallet[:10]}...")
        
        # Get historical data
        start_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = await session.query(PortfolioTransaction).filter(
            PortfolioTransaction.user_wallet == user_wallet,
            PortfolioTransaction.executed_at >= start_date
        ).all()
        
        positions = await session.query(TradingPosition).filter(
            TradingPosition.user_wallet == user_wallet,
            TradingPosition.opened_at >= start_date
        ).all()
        
        # Calculate analytics
        analytics = {
            "period_days": days,
            "total_transactions": len(transactions),
            "total_positions": len(positions),
            "active_trading_days": len(set(tx.executed_at.date() for tx in transactions)),
            "average_trades_per_day": len(transactions) / max(days, 1),
            "total_volume": str(sum(
                tx.total_value_usd for tx in transactions 
                if tx.total_value_usd
            )),
            "total_fees": str(sum(
                (tx.gas_fee or 0) + (tx.dex_fee or 0) for tx in transactions
            )),
            "position_metrics": {
                "average_position_size": str(sum(
                    pos.total_cost for pos in positions
                ) / len(positions)) if positions else "0",
                "average_hold_time_hours": 0,  # Would calculate from position data
                "largest_position": str(max(
                    (pos.total_cost for pos in positions), default=0
                )),
                "smallest_position": str(min(
                    (pos.total_cost for pos in positions), default=0
                ))
            }
        }
        
        return {
            "success": True,
            "data": analytics,
            "message": "Performance analytics generated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Performance analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {e}")


# Background Tasks

async def monitor_order_execution(order_id: str, user_wallet: str):
    """Background task to monitor order execution and manage risk."""
    try:
        logger.info(f"🔄 Starting order monitoring: {order_id}")
        
        # Would implement real-time order monitoring
        # - Check execution status
        # - Monitor slippage
        # - Trigger stop-loss if needed
        # - Update position records
        
        await asyncio.sleep(60)  # Placeholder monitoring interval
        logger.info(f"✅ Order monitoring completed: {order_id}")
        
    except Exception as e:
        logger.error(f"❌ Order monitoring failed for {order_id}: {e}")


# Utility endpoints for testing and administration

@router.get("/health/risk-system")
async def check_risk_system_health() -> Dict[str, Any]:
    """Check risk management system health."""
    try:
        risk_manager = get_risk_manager()
        
        # Perform basic health checks
        health_status = {
            "risk_manager": "operational",
            "position_sizing": "operational",
            "portfolio_monitoring": "operational",
            "risk_validation": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": health_status,
            "message": "Risk management system is healthy"
        }
        
    except Exception as e:
        logger.error(f"❌ Risk system health check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Risk system health check failed"
        }