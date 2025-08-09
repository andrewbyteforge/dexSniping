"""
Live Trading API Endpoints
File: app/api/v1/endpoints/live_trading.py

REST API endpoints for controlling the trading engine.
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator

from app.utils.logger import setup_logger, get_performance_logger, get_performance_logger
from app.core.trading.trading_engine import (
    TradingEngine, 
    TradingConfiguration, 
    TradingMode,
    StrategyType,
    OrderIntent
)
from app.core.wallet.wallet_manager import WalletType, NetworkType
from app.core.dex.dex_integration import DEXProtocol

logger = setup_logger(__name__, "api")

# Initialize router
router = APIRouter(prefix="/live-trading", tags=["Live Trading"])

# Global trading engine getter (set by main app)
_trading_engine_getter: Optional[Callable[[], TradingEngine]] = None


def set_trading_engine_getter(getter: Callable[[], TradingEngine]):
    """Set the trading engine getter function."""
    global _trading_engine_getter
    _trading_engine_getter = getter


def get_trading_engine() -> TradingEngine:
    """Get trading engine instance."""
    if _trading_engine_getter is None:
        raise HTTPException(status_code=503, detail="Trading engine not available")
    return _trading_engine_getter()


# ==================== REQUEST/RESPONSE MODELS ====================

class WalletConnectionRequest(BaseModel):
    """Wallet connection request model."""
    wallet_address: str = Field(..., description="Wallet address to connect")
    wallet_type: WalletType = Field(WalletType.METAMASK, description="Type of wallet")
    network: NetworkType = Field(NetworkType.ETHEREUM, description="Blockchain network")
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v or len(v) != 42 or not v.startswith('0x'):
            raise ValueError('Invalid wallet address format')
        return v.lower()


class TradingConfigRequest(BaseModel):
    """Trading configuration request model."""
    trading_mode: TradingMode = Field(TradingMode.SEMI_AUTOMATED, description="Trading mode")
    max_position_size: Decimal = Field(Decimal("1000"), ge=0, description="Maximum position size")
    max_daily_loss: Decimal = Field(Decimal("100"), ge=0, description="Maximum daily loss limit")
    default_slippage: Decimal = Field(Decimal("0.01"), ge=0, le=1, description="Default slippage")
    enabled_strategies: List[StrategyType] = Field([StrategyType.ARBITRAGE], description="Enabled strategies")
    preferred_dexes: List[DEXProtocol] = Field([DEXProtocol.UNISWAP_V2], description="Preferred DEXes")


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


# ==================== WALLET MANAGEMENT ENDPOINTS ====================

@router.post("/wallet/connect")
async def connect_wallet(request: WalletConnectionRequest) -> Dict[str, Any]:
    """Connect a user wallet for trading."""
    try:
        logger.info(f"🔗 Connecting wallet: {request.wallet_address[:10]}...")
        
        engine = get_trading_engine()
        
        result = await engine.wallet_manager.connect_wallet(
            wallet_address=request.wallet_address,
            wallet_type=request.wallet_type
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Wallet connected successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Wallet connection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/balance")
async def get_wallet_balance(
    wallet_address: str = Query(..., description="Wallet address")
) -> Dict[str, Any]:
    """Get wallet balance information."""
    try:
        logger.info(f"💰 Getting balance for: {wallet_address[:10]}...")
        
        engine = get_trading_engine()
        balance = await engine.wallet_manager.get_wallet_balance(wallet_address)
        
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
async def get_connected_wallets() -> Dict[str, Any]:
    """Get list of connected wallets."""
    try:
        engine = get_trading_engine()
        wallets = engine.wallet_manager.get_connected_wallets()
        
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
async def update_trading_config(config_request: TradingConfigRequest) -> Dict[str, Any]:
    """Update trading engine configuration."""
    try:
        logger.info("⚙️ Updating trading configuration...")
        
        engine = get_trading_engine()
        
        # Convert request to configuration object
        config = TradingConfiguration(
            trading_mode=config_request.trading_mode,
            max_position_size=config_request.max_position_size,
            max_daily_loss=config_request.max_daily_loss,
            default_slippage=config_request.default_slippage,
            enabled_strategies=config_request.enabled_strategies,
            preferred_dexes=config_request.preferred_dexes
        )
        
        engine.config = config
        
        return {
            "success": True,
            "data": {
                "trading_mode": config.trading_mode.value,
                "max_position_size": str(config.max_position_size),
                "enabled_strategies": [s.value for s in config.enabled_strategies]
            },
            "message": "Configuration updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Configuration update failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config/current")
async def get_current_config() -> Dict[str, Any]:
    """Get current trading configuration."""
    try:
        engine = get_trading_engine()
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
    wallet_address: str = Query(..., description="Wallet address to trade with")
) -> Dict[str, Any]:
    """Start automated trading."""
    try:
        logger.info(f"🚀 Starting trading for wallet: {wallet_address[:10]}...")
        
        engine = get_trading_engine()
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
async def stop_trading() -> Dict[str, Any]:
    """Stop automated trading."""
    try:
        logger.info("🛑 Stopping automated trading...")
        
        engine = get_trading_engine()
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
async def execute_manual_trade(request: ManualTradeRequest) -> Dict[str, Any]:
    """Execute a manual trade."""
    try:
        logger.info(f"📊 Manual trade: {request.intent.value} {request.amount}")
        
        engine = get_trading_engine()
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
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat(),
                "error_message": result.error_message
            },
            "message": "Trade executed successfully" if result.success else "Trade execution failed"
        }
        
    except Exception as e:
        logger.error(f"❌ Manual trade failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== QUOTES AND MARKET DATA ====================

@router.get("/quotes")
async def get_swap_quotes(
    input_token: str = Query(..., description="Input token address"),
    output_token: str = Query(..., description="Output token address"),
    amount: Decimal = Query(..., gt=0, description="Input amount"),
    slippage: Decimal = Query(Decimal("0.01"), ge=0, le=1, description="Slippage tolerance")
) -> Dict[str, Any]:
    """Get swap quotes from multiple DEXes."""
    try:
        logger.info(f"💱 Getting quotes: {amount} tokens")
        
        engine = get_trading_engine()
        quotes = await engine.dex_integration.get_swap_quote(
            input_token=input_token,
            output_token=output_token,
            input_amount=amount,
            slippage_tolerance=slippage
        )
        
        quotes_data = []
        for quote in quotes:
            quotes_data.append({
                "dex_protocol": quote.dex_protocol.value,
                "input_amount": str(quote.input_amount),
                "output_amount": str(quote.output_amount),
                "price_per_token": str(quote.price_per_token),
                "price_impact": str(quote.price_impact),
                "gas_estimate": quote.gas_estimate,
                "expires_at": quote.expires_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "quotes": quotes_data,
                "best_quote": quotes_data[0] if quotes_data else None,
                "count": len(quotes_data)
            },
            "message": f"Retrieved {len(quotes_data)} quotes"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATUS AND MONITORING ====================

@router.get("/status")
async def get_trading_status() -> Dict[str, Any]:
    """Get current trading engine status."""
    try:
        engine = get_trading_engine()
        status = await engine.get_trading_status()
        
        return {
            "success": True,
            "data": status,
            "message": "Trading status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get trading status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals")
async def get_active_signals() -> Dict[str, Any]:
    """Get active trading signals."""
    try:
        engine = get_trading_engine()
        
        signals_data = []
        for signal in engine.active_signals:
            signals_data.append({
                "signal_id": signal.signal_id,
                "strategy": signal.strategy_type.value,
                "symbol": signal.symbol,
                "intent": signal.intent.value,
                "confidence": signal.confidence,
                "suggested_amount": str(signal.suggested_amount),
                "reasoning": signal.reasoning,
                "expires_at": signal.expires_at.isoformat(),
                "created_at": signal.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "active_signals": signals_data,
                "count": len(signals_data)
            },
            "message": "Active signals retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get active signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TESTING ENDPOINTS ====================

@router.post("/test/generate-signal")
async def test_generate_signal(
    strategy: StrategyType = Query(StrategyType.ARBITRAGE, description="Strategy type"),
    token_address: str = Query("0xabcdefabcdefabcdefabcdefabcdefabcdefabcd", description="Token address")
) -> Dict[str, Any]:
    """Generate a test trading signal."""
    try:
        logger.info(f"🧪 Generating test signal: {strategy.value}")
        
        engine = get_trading_engine()
        
        # Mock market data for testing
        market_data = {
            "symbol": "TEST",
            "current_price": 1.5,
            "price_change_24h": 10.0,
            "volume_24h": 1000000
        }
        
        signal = await engine.generate_trading_signal(
            strategy_type=strategy,
            token_address=token_address,
            market_data=market_data
        )
        
        if signal:
            return {
                "success": True,
                "data": {
                    "signal_id": signal.signal_id,
                    "strategy": signal.strategy_type.value,
                    "symbol": signal.symbol,
                    "intent": signal.intent.value,
                    "confidence": signal.confidence,
                    "suggested_amount": str(signal.suggested_amount),
                    "reasoning": signal.reasoning,
                    "expires_at": signal.expires_at.isoformat()
                },
                "message": "Test signal generated successfully"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "No signal generated for current market conditions"
            }
        
    except Exception as e:
        logger.error(f"❌ Failed to generate test signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))
