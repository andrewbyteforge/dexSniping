"""
Dashboard API Endpoints
File: app/api/v1/endpoints/dashboard.py
Router: dashboard_router, tokens_router
Methods: get_dashboard_stats, get_tokens, get_active_trades, execute_trade

Updated to use real trading service data instead of mock responses.
Phase 4A Backend Integration implementation.
"""

from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Depends

from app.services import get_trading_service, ServiceError, TradingService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Dashboard router
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Tokens router (separate - matches dashboard expectation)
tokens_router = APIRouter(prefix="/tokens", tags=["tokens"])


def get_service() -> TradingService:
    """
    Dependency to get trading service instance.
    
    Returns:
        TradingService: The trading service instance
        
    Raises:
        HTTPException: If service is not available
    """
    try:
        return get_trading_service()
    except ServiceError as error:
        logger.error(f"Trading service not available: {error}")
        raise HTTPException(
            status_code=503, 
            detail="Trading service unavailable"
        )


@dashboard_router.get("/stats")
async def get_dashboard_stats(
    service: TradingService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Get real-time dashboard statistics from trading engine.
    
    Args:
        service: Trading service dependency
        
    Returns:
        Dict[str, Any]: Real portfolio statistics
        
    Raises:
        HTTPException: If stats cannot be retrieved
    """
    try:
        logger.info("Fetching dashboard stats from trading service...")
        
        # Get real portfolio stats from trading engine
        stats = await service.get_portfolio_stats()
        
        logger.info(f"Dashboard stats retrieved: ${stats.get('portfolio_value', 0):.2f}")
        return stats
        
    except Exception as error:
        logger.error(f"Failed to get dashboard stats: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve dashboard statistics: {str(error)}"
        )


@dashboard_router.get("/trades")
async def get_active_trades(
    service: TradingService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Get currently active trades from trading engine.
    
    Args:
        service: Trading service dependency
        
    Returns:
        Dict[str, Any]: Active trades data
        
    Raises:
        HTTPException: If trades cannot be retrieved
    """
    try:
        logger.info("Fetching active trades from trading service...")
        
        # Get real active trades
        trades = await service.get_active_trades()
        
        logger.info(f"Active trades retrieved: {trades.get('count', 0)} trades")
        return trades
        
    except Exception as error:
        logger.error(f"Failed to get active trades: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve active trades: {str(error)}"
        )


@dashboard_router.get("/health")
async def get_system_health(
    service: TradingService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Get trading system health status.
    
    Args:
        service: Trading service dependency
        
    Returns:
        Dict[str, Any]: System health information
    """
    try:
        health_data = await service.get_system_health()
        return {
            "success": True,
            "data": health_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as error:
        logger.error(f"Health check failed: {error}")
        return {
            "success": False,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }


@tokens_router.get("/discover")
async def get_tokens(
    limit: int = Query(10, ge=1, le=100, description="Number of tokens to return"), 
    offset: int = Query(0, ge=0, description="Offset for pagination"), 
    sort: str = Query("age", description="Sort field (age, volume, price_change)"), 
    order: str = Query("desc", description="Sort order (asc, desc)"),
    service: TradingService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Discover tokens using real market scanner data.
    
    Args:
        limit: Number of tokens to return
        offset: Offset for pagination  
        sort: Sort field
        order: Sort order
        service: Trading service dependency
        
    Returns:
        Dict[str, Any]: Token discovery data from market scanner
        
    Raises:
        HTTPException: If token discovery fails
    """
    try:
        logger.info(f"Discovering tokens: limit={limit}, sort={sort}, order={order}")
        
        # Get real token discoveries from market scanner
        tokens_data = await service.get_token_discoveries(
            limit=limit,
            offset=offset, 
            sort=sort,
            order=order
        )
        
        logger.info(f"Token discovery completed: {tokens_data.get('count', 0)} tokens found")
        return tokens_data
        
    except Exception as error:
        logger.error(f"Token discovery failed: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to discover tokens: {str(error)}"
        )


@dashboard_router.post("/execute-trade")
async def execute_trade(
    symbol: str = Query(..., description="Token symbol to trade"),
    side: str = Query(..., description="Trade side (buy/sell)"),
    amount: float = Query(..., gt=0, description="Amount to trade"),
    network: str = Query("ethereum", description="Blockchain network"),
    service: TradingService = Depends(get_service)
) -> Dict[str, Any]:
    """
    Execute a trade through the trading engine.
    
    Args:
        symbol: Token symbol to trade
        side: Trade side (buy/sell)  
        amount: Amount to trade
        network: Blockchain network
        service: Trading service dependency
        
    Returns:
        Dict[str, Any]: Trade execution result
        
    Raises:
        HTTPException: If trade execution fails
    """
    try:
        logger.info(f"Executing trade: {side} {amount} {symbol} on {network}")
        
        # Validate inputs
        if side.lower() not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Invalid trade side. Use 'buy' or 'sell'")
        
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Trade amount must be positive")
        
        # Execute trade through service
        execution_result = await service.execute_trade_signal(
            symbol=symbol,
            side=side.lower(),
            amount=amount,
            network=network
        )
        
        if execution_result.get("success"):
            logger.info(f"Trade executed successfully: {execution_result.get('trade_id')}")
        else:
            logger.warning(f"Trade execution failed: {execution_result.get('error')}")
        
        return execution_result
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Trade execution error: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Trade execution failed: {str(error)}"
        )


# Export both routers for backwards compatibility
router = dashboard_router