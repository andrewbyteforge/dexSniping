"""
Trading API Endpoints - Live Trading Integration
File: app/api/v1/endpoints/live_trading.py

Professional API endpoints for live trading functionality including
wallet connection, trade execution, and automated trading management.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator

from app.utils.logger import setup_logger
from app.core.trading.trading_engine import (
    TradingEngine, 
    TradingConfiguration, 
    TradingMode,
    StrategyType,
    OrderIntent
)
from app.core.wallet.wallet_manager import WalletManager, WalletType, NetworkType
from app.core.trading.risk_manager import RiskLevel
from app.core.dex.dex_integration import DEXProtocol

logger = setup_logger(__name__)

# Initialize router
router = APIRouter(prefix="/live-trading", tags=["Live Trading"])

# Global instances (in production, use dependency injection)
trading_engine: Optional[TradingEngine] = None
wallet_manager: Optional[WalletManager] = None


# ==================== REQUEST/RESPONSE MODELS ====================

class WalletConnectionRequest(BaseModel):
    """Wallet connection request model."""
    wallet_address: str = Field(..., description="Wallet address to connect")
    wallet_type: WalletType = Field(..., description="Type of wallet")
    signature: Optional[str] = Field(None, description="Authentication signature")
    message: Optional[str] = Field(None, description="Signed message")
    network: NetworkType = Field(NetworkType.ETHEREUM, description="Blockchain network")
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v or len(v) != 42 or not v.startswith('0x'):
            raise ValueError('Invalid wallet address format')
        return v.lower()


class TradingConfigurationRequest(BaseModel):
    """Trading configuration request model."""
    trading_mode: TradingMode = Field(..., description="Trading mode")
    max_position_size: Decimal = Field(..., ge=0, description="Maximum position size")
    max_daily_loss: Decimal = Field(..., ge=0, description="Maximum daily loss limit")
    max_slippage: Decimal = Field(..., ge=0, le=1, description="Maximum slippage tolerance")
    default_slippage: Decimal = Field(..., ge=0, le=1, description="Default slippage")
    auto_approve_threshold: Decimal = Field(..., ge=0, description="Auto-approve threshold")
    risk_tolerance: RiskLevel = Field(..., description="Risk tolerance level")
    enabled_strategies: List[StrategyType] = Field(..., description="Enabled trading strategies")
    preferred_dexes: List[DEXProtocol] = Field(..., description="Preferred DEX protocols")
    gas_price_limit: int = Field(..., gt=0, description="Gas price limit in gwei")
    confirmation_blocks: int = Field(..., gt=0, description="Required confirmation blocks")


class ManualTradeRequest(BaseModel):
    """Manual trade execution request model."""
    wallet_address: str = Field(..., description="Wallet address")
    token_address: str = Field(..., description="Token contract address")
    intent: OrderIntent = Field(..., description="Trade intent (buy/sell)")
    amount: Decimal = Field(..., gt=0, description="Amount to trade")
    slippage_tolerance: Optional[Decimal] = Field(None, ge=0, le=1, description="Slippage tolerance")
    
    @validator('wallet_address', 'token_address')
    def validate_addresses(cls, v):
        if not v or len(v) != 42 or not v.startswith('0x'):
            raise ValueError('Invalid address format')
        return v.lower()


class SignalExecutionRequest(BaseModel):
    """Signal execution request model."""
    signal_id: str = Field(..., description="Signal ID to execute")
    override_amount: Optional[Decimal] = Field(None, gt=0, description="Override suggested amount")
    force_execute: bool = Field(False, description="Force execution ignoring risk checks")


# ==================== INITIALIZATION ====================

async def get_trading_engine() -> TradingEngine:
    """Get or initialize trading engine."""
    global trading_engine, wallet_manager
    
    if trading_engine is None:
        trading_engine = TradingEngine(NetworkType.ETHEREUM)
        wallet_manager = WalletManager(NetworkType.ETHEREUM)
        await trading_engine.initialize(wallet_manager=wallet_manager)
        logger.info("🤖 Trading Engine initialized for API")
    
    return trading_engine


async def get_wallet_manager() -> WalletManager:
    """Get wallet manager instance."""
    global wallet_manager
    
    if wallet_manager is None:
        wallet_manager = WalletManager(NetworkType.ETHEREUM)
    
    return wallet_manager


# ==================== WALLET MANAGEMENT ENDPOINTS ====================

@router.post("/wallet/connect")
async def connect_wallet(
    request: WalletConnectionRequest,
    wallet_mgr: WalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """Connect a user wallet for trading."""
    try:
        logger.info(f"🔗 Connecting wallet: {request.wallet_address[:10]}...")
        
        result = await wallet_mgr.connect_wallet(
            wallet_address=request.wallet_address,
            wallet_type=request.wallet_type,
            signature=request.signature,
            message=request.message
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Wallet connected successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Wallet connection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wallet/disconnect")
async def disconnect_wallet(
    wallet_address: str = Query(..., description="Wallet address to disconnect"),
    wallet_mgr: WalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """Disconnect a user wallet."""
    try:
        logger.info(f"🔌 Disconnecting wallet: {wallet_address[:10]}...")
        
        result = await wallet_mgr.disconnect_wallet(wallet_address)
        
        return {
            "success": True,
            "data": result,
            "message": "Wallet disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Wallet disconnection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/balance")
async def get_wallet_balance(
    wallet_address: str = Query(..., description="Wallet address"),
    wallet_mgr: WalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """Get wallet balance information."""
    try:
        logger.info(f"💰 Getting balance for: {wallet_address[:10]}...")
        
        balance = await wallet_mgr.get_wallet_balance(wallet_address)
        
        return {
            "success": True,
            "data": {
                "wallet_address": wallet_address,
                "native_balance": str(balance.native_balance),
                "token_balances": {k: str(v) for k, v in balance.token_balances.items()},
                "total_usd_value": str(balance.total_usd_value),
                "last_updated": balance.last_updated.isoformat()
            },
            "message": "Balance retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Balance retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/connected")
async def get_connected_wallets(
    wallet_mgr: WalletManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """Get list of connected wallets."""
    try:
        wallets = wallet_mgr.get_connected_wallets()
        
        return {
            "success": True,
            "data": {
                "connected_wallets": wallets,
                "count": len(wallets)
            },
            "message": "Connected wallets retrieved"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get connected wallets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TRADING CONFIGURATION ====================

@router.post("/config/update")
async def update_trading_config(
    config_request: TradingConfigurationRequest,
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Update trading engine configuration."""
    try:
        logger.info(f"⚙️ Updating trading configuration...")
        
        # Convert request to configuration object
        config = TradingConfiguration(
            trading_mode=config_request.trading_mode,
            max_position_size=config_request.max_position_size,
            max_daily_loss=config_request.max_daily_loss,
            max_slippage=config_request.max_slippage,
            default_slippage=config_request.default_slippage,
            auto_approve_threshold=config_request.auto_approve_threshold,
            risk_tolerance=config_request.risk_tolerance,
            enabled_strategies=config_request.enabled_strategies,
            preferred_dexes=config_request.preferred_dexes,
            gas_price_limit=config_request.gas_price_limit,
            confirmation_blocks=config_request.confirmation_blocks
        )
        
        result = await engine.update_configuration(config)
        
        return {
            "success": True,
            "data": result,
            "message": "Configuration updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Configuration update failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/current")
async def get_current_config(
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Get current trading configuration."""
    try:
        status = await engine.get_trading_status()
        
        return {
            "success": True,
            "data": status,
            "message": "Configuration retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TRADING OPERATIONS ====================

@router.post("/start")
async def start_trading(
    wallet_address: str = Query(..., description="Wallet address to trade with"),
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Start automated trading."""
    try:
        logger.info(f"🚀 Starting trading for wallet: {wallet_address[:10]}...")
        
        result = await engine.start_trading(wallet_address)
        
        return {
            "success": True,
            "data": result,
            "message": "Trading started successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start trading: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stop")
async def stop_trading(
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Stop automated trading."""
    try:
        logger.info("🛑 Stopping automated trading...")
        
        result = await engine.stop_trading()
        
        return {
            "success": True,
            "data": result,
            "message": "Trading stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to stop trading: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trade/manual")
async def execute_manual_trade(
    request: ManualTradeRequest,
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Execute a manual trade."""
    try:
        logger.info(
            f"📊 Manual trade: {request.intent.value} {request.amount} "
            f"from {request.wallet_address[:10]}..."
        )
        
        result = await engine.execute_manual_trade(
            wallet_address=request.wallet_address,
            token_address=request.token_address,
            intent=request.intent,
            amount=request.amount,
            slippage_tolerance=request.slippage_tolerance
        )
        
        return {
            "success": result.success,
            "data": {
                "trade_id": result.trade_id,
                "transaction_hash": result.transaction_hash,
                "executed_amount": str(result.executed_amount),
                "execution_price": str(result.execution_price),
                "gas_used": result.gas_used,
                "fees_paid": str(result.fees_paid),
                "slippage": str(result.slippage),
                "profit_loss": str(result.profit_loss),
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat(),
                "error_message": result.error_message
            },
            "message": "Trade executed successfully" if result.success else "Trade execution failed"
        }
        
    except Exception as e:
        logger.error(f"❌ Manual trade failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== SIGNAL MANAGEMENT ====================

@router.get("/signals/active")
async def get_active_signals(
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Get active trading signals."""
    try:
        signals = await engine.get_active_signals()
        
        return {
            "success": True,
            "data": {
                "active_signals": signals,
                "count": len(signals)
            },
            "message": "Active signals retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get active signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signals/execute")
async def execute_signal(
    request: SignalExecutionRequest,
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Execute a specific trading signal."""
    try:
        logger.info(f"🎯 Executing signal: {request.signal_id}")
        
        result = await engine.force_execute_signal(request.signal_id)
        
        return {
            "success": result.success,
            "data": {
                "trade_id": result.trade_id,
                "transaction_hash": result.transaction_hash,
                "executed_amount": str(result.executed_amount),
                "execution_price": str(result.execution_price),
                "gas_used": result.gas_used,
                "fees_paid": str(result.fees_paid),
                "slippage": str(result.slippage),
                "execution_time": result.execution_time,
                "error_message": result.error_message
            },
            "message": "Signal executed successfully" if result.success else "Signal execution failed"
        }
        
    except Exception as e:
        logger.error(f"❌ Signal execution failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== STATUS AND MONITORING ====================

@router.get("/status")
async def get_trading_status(
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Get current trading engine status."""
    try:
        status = await engine.get_trading_status()
        
        return {
            "success": True,
            "data": status,
            "message": "Trading status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get trading status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for trading system."""
    try:
        global trading_engine, wallet_manager
        
        health_status = {
            "trading_engine": trading_engine is not None,
            "wallet_manager": wallet_manager is not None,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "trading_engine_running": trading_engine.is_running if trading_engine else False,
                "connected_wallets": len(wallet_manager.connected_wallets) if wallet_manager else 0
            }
        }
        
        return {
            "success": True,
            "data": health_status,
            "message": "System health check completed"
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== BACKGROUND TASKS ====================

@router.post("/maintenance/restart")
async def restart_trading_engine(
    background_tasks: BackgroundTasks,
    engine: TradingEngine = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Restart trading engine (admin only)."""
    try:
        logger.info("🔄 Restarting trading engine...")
        
        # Schedule restart in background
        background_tasks.add_task(_restart_engine_task, engine)
        
        return {
            "success": True,
            "message": "Trading engine restart initiated"
        }
        
    except Exception as e:
        logger.error(f"❌ Restart failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _restart_engine_task(engine: TradingEngine) -> None:
    """Background task to restart trading engine."""
    try:
        # Graceful shutdown
        await engine.shutdown()
        
        # Wait a moment
        await asyncio.sleep(5)
        
        # Reinitialize
        global trading_engine, wallet_manager
        trading_engine = TradingEngine(NetworkType.ETHEREUM)
        await trading_engine.initialize(wallet_manager=wallet_manager)
        
        logger.info("✅ Trading engine restarted successfully")
        
    except Exception as e:
        logger.error(f"❌ Engine restart task failed: {e}")


# ==================== STARTUP EVENT ====================

@router.on_event("startup")
async def startup_trading_system():
    """Initialize trading system on startup."""
    try:
        logger.info("🚀 Initializing Live Trading System...")
        
        # Initialize global instances
        await get_trading_engine()
        await get_wallet_manager()
        
        logger.info("✅ Live Trading System initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Trading system startup failed: {e}")


@router.on_event("shutdown")
async def shutdown_trading_system():
    """Cleanup on shutdown."""
    try:
        logger.info("🛑 Shutting down Live Trading System...")
        
        global trading_engine
        if trading_engine:
            await trading_engine.shutdown()
        
        logger.info("✅ Live Trading System shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Trading system shutdown error: {e}")


# ==================== ERROR HANDLERS ====================

@router.exception_handler(Exception)
async def trading_exception_handler(request, exc):
    """Global exception handler for trading endpoints."""
    logger.error(f"❌ Unhandled trading API error: {exc}")
    return HTTPException(
        status_code=500,
        detail="Internal trading system error"
    )