"""
Snipe Trading API Endpoints - Phase 4D
File: app/api/v1/endpoints/snipe_trading.py
Class: N/A (FastAPI router endpoints)
Methods: execute_snipe, validate_snipe, get_snipe_status, cancel_snipe

API endpoints that connect frontend snipe buttons to the backend trading
execution system with real-time status updates and comprehensive validation.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from app.utils.logger import setup_logger
from app.core.exceptions import (
    TradingError, 
    ValidationError, 
    RiskManagementError,
    WalletError,
    DEXError
)
from app.core.trading.snipe_trading_controller import (
    get_snipe_trading_controller,
    SnipeTradingController,
    SnipeTradeRequest,
    SnipeType,
    SnipeStatus,
    RiskLevel
)
from app.core.blockchain.network_manager import NetworkType
from app.core.dex.live_dex_integration import DEXProtocol

logger = setup_logger(__name__)

# Create FastAPI router
router = APIRouter(prefix="/snipe", tags=["Snipe Trading"])


# ==================== REQUEST/RESPONSE MODELS ====================

class SnipeTradeRequestModel(BaseModel):
    """Snipe trade request model for API."""
    snipe_type: SnipeType
    token_address: str = Field(..., min_length=42, max_length=42)
    token_symbol: str = Field(..., min_length=1, max_length=20)
    network: NetworkType
    dex_protocol: DEXProtocol
    amount_in: Decimal = Field(..., gt=0, description="Amount to trade in native token")
    amount_out_min: Optional[Decimal] = Field(None, ge=0)
    slippage_tolerance: Decimal = Field(..., ge=0, le=0.5, description="Slippage tolerance (0.01 = 1%)")
    gas_price_gwei: Optional[Decimal] = Field(None, gt=0)
    max_gas_limit: Optional[int] = Field(None, gt=0)
    wallet_connection_id: str = Field(..., min_length=1)
    deadline_seconds: int = Field(300, ge=30, le=3600)
    user_confirmation: bool = Field(False, description="User confirmed high-risk trade")
    
    @validator('token_address')
    def validate_token_address(cls, v):
        """Validate Ethereum address format."""
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid token address format')
        return v.lower()
    
    @validator('slippage_tolerance')
    def validate_slippage(cls, v):
        """Validate slippage tolerance."""
        if v < 0.001:  # 0.1%
            raise ValueError('Slippage tolerance too low (minimum 0.1%)')
        if v > 0.5:    # 50%
            raise ValueError('Slippage tolerance too high (maximum 50%)')
        return v
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            Decimal: str
        }


class SnipeValidationRequestModel(BaseModel):
    """Request model for snipe validation."""
    snipe_request: SnipeTradeRequestModel
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class SnipeExecutionResponseModel(BaseModel):
    """Response model for snipe execution."""
    execution_id: str
    request_id: str
    status: SnipeStatus
    transaction_hash: Optional[str]
    estimated_completion: Optional[datetime]
    validation_result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class SnipeValidationResponseModel(BaseModel):
    """Response model for snipe validation."""
    request_id: str
    is_valid: bool
    risk_level: RiskLevel
    risk_score: float
    confidence_score: float
    validation_errors: List[str]
    validation_warnings: List[str]
    estimated_gas_cost_eth: Optional[Decimal]
    price_impact_percent: Optional[Decimal]
    liquidity_analysis: Dict[str, Any]
    recommendations: List[str]
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            Decimal: str
        }


class SnipeStatusResponseModel(BaseModel):
    """Response model for snipe status."""
    execution_id: str
    request_id: str
    status: SnipeStatus
    transaction_hash: Optional[str]
    block_number: Optional[int]
    gas_used: Optional[int]
    effective_gas_price_gwei: Optional[Decimal]
    actual_amount_out: Optional[Decimal]
    price_impact_actual_percent: Optional[Decimal]
    execution_time_ms: int
    profit_loss_usd: Optional[Decimal]
    error_message: Optional[str]
    executed_at: datetime
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            Decimal: str
        }


class SnipeStatsResponseModel(BaseModel):
    """Response model for snipe statistics."""
    total_snipes: int
    successful_snipes: int
    failed_snipes: int
    success_rate: float
    avg_execution_time_ms: int
    total_profit_usd: Decimal
    active_snipes: int
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            Decimal: str
        }


# ==================== DEPENDENCY INJECTION ====================

async def get_controller() -> SnipeTradingController:
    """Get snipe trading controller dependency."""
    return await get_snipe_trading_controller()


# ==================== API ENDPOINTS ====================

@router.post("/execute", response_model=SnipeExecutionResponseModel)
async def execute_snipe_trade(
    request: SnipeTradeRequestModel,
    background_tasks: BackgroundTasks,
    controller: SnipeTradingController = Depends(get_controller)
) -> SnipeExecutionResponseModel:
    """
    Execute a snipe trade from frontend button click.
    
    This endpoint handles the complete snipe trade execution workflow:
    1. Validates the trade request
    2. Checks risk parameters
    3. Executes the trade if conditions are met
    4. Returns real-time execution status
    """
    try:
        logger.info(f"🎯 Received snipe trade request: {request.snipe_type.value}")
        
        # Generate unique request ID
        request_id = str(uuid4())
        
        # Convert API model to internal model
        snipe_request = SnipeTradeRequest(
            request_id=request_id,
            snipe_type=request.snipe_type,
            token_address=request.token_address,
            token_symbol=request.token_symbol,
            network=request.network,
            dex_protocol=request.dex_protocol,
            amount_in=request.amount_in,
            amount_out_min=request.amount_out_min,
            slippage_tolerance=request.slippage_tolerance,
            gas_price_gwei=request.gas_price_gwei,
            max_gas_limit=request.max_gas_limit,
            wallet_connection_id=request.wallet_connection_id,
            deadline_seconds=request.deadline_seconds
        )
        
        # Execute snipe trade in background
        execution_result = await controller.execute_snipe_trade(
            snipe_request=snipe_request,
            user_confirmation=request.user_confirmation,
            bypass_validation=False
        )
        
        return SnipeExecutionResponseModel(
            execution_id=execution_result.execution_id,
            request_id=execution_result.request_id,
            status=execution_result.status,
            transaction_hash=execution_result.transaction_hash,
            estimated_completion=execution_result.executed_at + timedelta(minutes=5),
            validation_result=None,  # Can include validation details if needed
            error_message=execution_result.error_message,
            created_at=execution_result.executed_at
        )
        
    except ValidationError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}"
        )
    
    except RiskManagementError as e:
        logger.error(f"❌ Risk management error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Risk check failed: {str(e)}"
        )
    
    except WalletError as e:
        logger.error(f"❌ Wallet error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wallet error: {str(e)}"
        )
    
    except DEXError as e:
        logger.error(f"❌ DEX error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"DEX error: {str(e)}"
        )
    
    except TradingError as e:
        logger.error(f"❌ Trading error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trading execution failed: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during snipe execution"
        )


@router.post("/validate", response_model=SnipeValidationResponseModel)
async def validate_snipe_trade(
    request: SnipeValidationRequestModel,
    controller: SnipeTradingController = Depends(get_controller)
) -> SnipeValidationResponseModel:
    """
    Validate a snipe trade request before execution.
    
    Performs comprehensive validation including:
    - Parameter validation
    - Risk assessment
    - Liquidity analysis
    - Security checks
    - Gas estimation
    """
    try:
        logger.info("🔍 Validating snipe trade request...")
        
        # Generate request ID for validation
        request_id = str(uuid4())
        
        # Convert API model to internal model
        snipe_request = SnipeTradeRequest(
            request_id=request_id,
            snipe_type=request.snipe_request.snipe_type,
            token_address=request.snipe_request.token_address,
            token_symbol=request.snipe_request.token_symbol,
            network=request.snipe_request.network,
            dex_protocol=request.snipe_request.dex_protocol,
            amount_in=request.snipe_request.amount_in,
            amount_out_min=request.snipe_request.amount_out_min,
            slippage_tolerance=request.snipe_request.slippage_tolerance,
            gas_price_gwei=request.snipe_request.gas_price_gwei,
            max_gas_limit=request.snipe_request.max_gas_limit,
            wallet_connection_id=request.snipe_request.wallet_connection_id,
            deadline_seconds=request.snipe_request.deadline_seconds
        )
        
        # Perform validation
        validation_result = await controller.validate_snipe_request(snipe_request)
        
        # Generate recommendations based on validation
        recommendations = []
        
        if validation_result.risk_level == RiskLevel.HIGH:
            recommendations.append("Consider reducing trade size due to high risk")
        
        if validation_result.price_impact_percent and validation_result.price_impact_percent > 0.03:
            recommendations.append("High price impact detected - consider splitting trade")
        
        if validation_result.estimated_gas_cost and validation_result.estimated_gas_cost > snipe_request.amount_in * Decimal("0.05"):
            recommendations.append("Gas cost is high relative to trade size")
        
        if validation_result.liquidity_analysis.get("total_liquidity_usd", 0) < 50000:
            recommendations.append("Low liquidity - proceed with caution")
        
        if not recommendations:
            recommendations.append("Trade parameters look good for execution")
        
        return SnipeValidationResponseModel(
            request_id=request_id,
            is_valid=validation_result.is_valid,
            risk_level=validation_result.risk_level,
            risk_score=validation_result.risk_score,
            confidence_score=validation_result.confidence_score,
            validation_errors=validation_result.validation_errors,
            validation_warnings=validation_result.validation_warnings,
            estimated_gas_cost_eth=validation_result.estimated_gas_cost,
            price_impact_percent=validation_result.price_impact_percent,
            liquidity_analysis=validation_result.liquidity_analysis,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/status/{execution_id}", response_model=SnipeStatusResponseModel)
async def get_snipe_status(
    execution_id: str,
    controller: SnipeTradingController = Depends(get_controller)
) -> SnipeStatusResponseModel:
    """
    Get the status of a snipe trade execution.
    
    Provides real-time status updates for ongoing snipe trades
    including transaction details and execution results.
    """
    try:
        logger.info(f"📊 Getting snipe status: {execution_id}")
        
        # Get execution result from controller
        execution_results = controller.get_execution_results()
        execution_result = None
        
        for result in execution_results:
            if result.execution_id == execution_id:
                execution_result = result
                break
        
        if not execution_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution ID {execution_id} not found"
            )
        
        return SnipeStatusResponseModel(
            execution_id=execution_result.execution_id,
            request_id=execution_result.request_id,
            status=execution_result.status,
            transaction_hash=execution_result.transaction_hash,
            block_number=execution_result.block_number,
            gas_used=execution_result.gas_used,
            effective_gas_price_gwei=execution_result.effective_gas_price,
            actual_amount_out=execution_result.actual_amount_out,
            price_impact_actual_percent=execution_result.price_impact_actual,
            execution_time_ms=execution_result.execution_time_ms,
            profit_loss_usd=execution_result.profit_loss_usd,
            error_message=execution_result.error_message,
            executed_at=execution_result.executed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting snipe status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve snipe status"
        )


@router.delete("/cancel/{request_id}")
async def cancel_snipe_trade(
    request_id: str,
    controller: SnipeTradingController = Depends(get_controller)
) -> JSONResponse:
    """
    Cancel a pending snipe trade.
    
    Allows users to cancel snipe trades that are still in validation
    or waiting for execution.
    """
    try:
        logger.info(f"🚫 Canceling snipe trade: {request_id}")
        
        # Get active snipes
        active_snipes = controller.get_active_snipes()
        
        if request_id not in active_snipes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active snipe request {request_id} not found"
            )
        
        # Remove from active snipes (this cancels it)
        del controller.active_snipes[request_id]
        
        logger.info(f"✅ Snipe trade canceled: {request_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Snipe trade canceled successfully",
                "request_id": request_id,
                "canceled_at": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error canceling snipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel snipe trade"
        )


@router.get("/active", response_model=List[Dict[str, Any]])
async def get_active_snipes(
    controller: SnipeTradingController = Depends(get_controller)
) -> List[Dict[str, Any]]:
    """
    Get all currently active snipe trades.
    
    Returns a list of snipe trades that are currently being processed
    or waiting for execution.
    """
    try:
        logger.info("📋 Getting active snipe trades...")
        
        active_snipes = controller.get_active_snipes()
        
        # Convert to JSON-serializable format
        active_list = []
        for request_id, snipe_request in active_snipes.items():
            active_list.append({
                "request_id": snipe_request.request_id,
                "snipe_type": snipe_request.snipe_type.value,
                "token_symbol": snipe_request.token_symbol,
                "network": snipe_request.network.value,
                "dex_protocol": snipe_request.dex_protocol.value,
                "amount_in": str(snipe_request.amount_in),
                "created_at": snipe_request.created_at.isoformat(),
                "deadline": snipe_request.deadline.isoformat(),
                "is_expired": snipe_request.is_expired
            })
        
        return active_list
        
    except Exception as e:
        logger.error(f"❌ Error getting active snipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active snipes"
        )


@router.get("/history", response_model=List[SnipeStatusResponseModel])
async def get_snipe_history(
    limit: int = 50,
    controller: SnipeTradingController = Depends(get_controller)
) -> List[SnipeStatusResponseModel]:
    """
    Get snipe trade execution history.
    
    Returns recent snipe trade executions with their results and statistics.
    """
    try:
        logger.info(f"📚 Getting snipe history (limit: {limit})...")
        
        execution_results = controller.get_execution_results(limit=limit)
        
        history = []
        for result in execution_results:
            history.append(SnipeStatusResponseModel(
                execution_id=result.execution_id,
                request_id=result.request_id,
                status=result.status,
                transaction_hash=result.transaction_hash,
                block_number=result.block_number,
                gas_used=result.gas_used,
                effective_gas_price_gwei=result.effective_gas_price,
                actual_amount_out=result.actual_amount_out,
                price_impact_actual_percent=result.price_impact_actual,
                execution_time_ms=result.execution_time_ms,
                profit_loss_usd=result.profit_loss_usd,
                error_message=result.error_message,
                executed_at=result.executed_at
            ))
        
        return history
        
    except Exception as e:
        logger.error(f"❌ Error getting snipe history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve snipe history"
        )


@router.get("/stats", response_model=SnipeStatsResponseModel)
async def get_snipe_statistics(
    controller: SnipeTradingController = Depends(get_controller)
) -> SnipeStatsResponseModel:
    """
    Get snipe trading statistics.
    
    Returns comprehensive statistics about snipe trading performance
    including success rates, execution times, and profitability.
    """
    try:
        logger.info("📊 Getting snipe statistics...")
        
        stats = controller.get_execution_stats()
        
        return SnipeStatsResponseModel(
            total_snipes=stats["total_snipes"],
            successful_snipes=stats["successful_snipes"],
            failed_snipes=stats["failed_snipes"],
            success_rate=stats["success_rate"],
            avg_execution_time_ms=stats["avg_execution_time_ms"],
            total_profit_usd=stats["total_profit_usd"],
            active_snipes=stats["active_snipes"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting snipe statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve snipe statistics"
        )


# ==================== WEBSOCKET ENDPOINTS ====================

@router.websocket("/ws/{request_id}")
async def snipe_websocket(
    websocket,
    request_id: str,
    controller: SnipeTradingController = Depends(get_controller)
):
    """
    WebSocket endpoint for real-time snipe trade updates.
    
    Provides real-time status updates for snipe trades including
    validation results, execution progress, and final results.
    """
    await websocket.accept()
    
    try:
        logger.info(f"🔌 WebSocket connected for snipe: {request_id}")
        
        # Send initial status
        await websocket.send_json({
            "type": "connection_established",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Monitor snipe progress
        while True:
            # Check if snipe is still active
            active_snipes = controller.get_active_snipes()
            
            if request_id in active_snipes:
                # Send progress update
                snipe_request = active_snipes[request_id]
                await websocket.send_json({
                    "type": "progress_update",
                    "request_id": request_id,
                    "status": "processing",
                    "token_symbol": snipe_request.token_symbol,
                    "deadline": snipe_request.deadline.isoformat(),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                # Check execution results
                execution_results = controller.get_execution_results()
                execution_result = None
                
                for result in execution_results:
                    if result.request_id == request_id:
                        execution_result = result
                        break
                
                if execution_result:
                    # Send final result
                    await websocket.send_json({
                        "type": "execution_complete",
                        "request_id": request_id,
                        "execution_id": execution_result.execution_id,
                        "status": execution_result.status.value,
                        "transaction_hash": execution_result.transaction_hash,
                        "error_message": execution_result.error_message,
                        "timestamp": execution_result.executed_at.isoformat()
                    })
                    break
                else:
                    # Snipe not found - may have been canceled
                    await websocket.send_json({
                        "type": "snipe_not_found",
                        "request_id": request_id,
                        "message": "Snipe request not found or canceled",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    break
            
            # Wait before next update
            await asyncio.sleep(2)
    
    except Exception as e:
        logger.error(f"❌ WebSocket error for snipe {request_id}: {e}")
        await websocket.send_json({
            "type": "error",
            "request_id": request_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    finally:
        await websocket.close()
        logger.info(f"🔌 WebSocket disconnected for snipe: {request_id}")


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def snipe_trading_health(
    controller: SnipeTradingController = Depends(get_controller)
) -> JSONResponse:
    """Health check for snipe trading system."""
    try:
        stats = controller.get_execution_stats()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "service": "Snipe Trading Controller",
                "active_snipes": stats["active_snipes"],
                "total_executions": stats["total_snipes"],
                "success_rate": f"{stats['success_rate']:.2%}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Snipe trading health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "Snipe Trading Controller",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )