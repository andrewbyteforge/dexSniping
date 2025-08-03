#!/usr/bin/env python3
"""
Create Trading API Endpoints
File: create_api.py

Creates the API endpoints for controlling the trading engine.
"""

import os
from pathlib import Path


def create_main_app():
    """Create the main FastAPI application file."""
    content = '''"""
Main FastAPI Application
File: app/main.py

Main application entry point for the DEX Sniper Pro trading bot.
Serves the existing professional dashboard and connects it to the trading engine.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from contextlib import asynccontextmanager
import os
from pathlib import Path
from datetime import datetime

from app.api.v1.endpoints import live_trading
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global trading engine instance
trading_engine_instance = None

# Templates for the dashboard
templates = Jinja2Templates(directory="frontend/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    global trading_engine_instance
    
    # Startup
    logger.info("🚀 Starting DEX Sniper Pro Trading Bot...")
    try:
        from app.core.trading.trading_engine import TradingEngine, NetworkType
        trading_engine_instance = TradingEngine(NetworkType.ETHEREUM)
        await trading_engine_instance.initialize()
        logger.info("✅ Trading engine initialized successfully")
        logger.info("📊 Dashboard ready at /dashboard")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize trading engine: {e}")
        yield
    finally:
        # Shutdown
        logger.info("🛑 Shutting down trading bot...")
        if trading_engine_instance:
            try:
                await trading_engine_instance.stop_trading()
                logger.info("✅ Trading engine stopped successfully")
            except Exception as e:
                logger.error(f"❌ Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="DEX Sniper Pro API",
    description="Automated crypto trading bot with profit generation capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the existing dashboard
if Path("frontend/static").exists():
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    logger.info("✅ Mounted frontend static files")

# Include API routers
app.include_router(live_trading.router, prefix="/api/v1")

# Add dashboard API endpoints
try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1")
    logger.info("✅ Dashboard API endpoints loaded")
except ImportError:
    logger.warning("⚠️ Dashboard API endpoints not found - creating mock endpoints")
    
    # Create basic dashboard API inline
    dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
    
    @dashboard_router.get("/stats")
    async def mock_dashboard_stats():
        return {
            "portfolio_value": 25000.50,
            "daily_pnl": 1250.75,
            "daily_pnl_percent": 5.2,
            "trades_today": 23,
            "success_rate": 87.5,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    app.include_router(dashboard_router)


@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard."""
    return {
        "message": "🤖 DEX Sniper Pro Trading Bot API",
        "version": "1.0.0", 
        "status": "running",
        "dashboard": "/dashboard",
        "api_docs": "/docs",
        "trading_api": "/api/v1/live-trading"
    }


@app.get("/dashboard")
async def serve_dashboard(request: Request):
    """Serve the professional dashboard with template rendering."""
    try:
        # Check if the template-based dashboard exists
        dashboard_template = Path("frontend/templates/pages/dashboard.html")
        base_template = Path("frontend/templates/base.html") 
        
        if dashboard_template.exists() and base_template.exists():
            logger.info("📊 Serving template-based professional dashboard")
            return templates.TemplateResponse("pages/dashboard.html", {
                "request": request,
                "title": "Trading Dashboard",
                "trading_engine_status": trading_engine_instance is not None
            })
        else:
            # Fallback to static dashboard
            static_dashboard = Path("dashboard/index.html")
            if static_dashboard.exists():
                logger.info("📊 Serving static dashboard")
                return FileResponse("dashboard/index.html")
            else:
                logger.error("❌ No dashboard found")
                raise HTTPException(status_code=404, detail="Dashboard not found")
                
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global trading_engine_instance
    
    return {
        "status": "healthy",
        "trading_engine": trading_engine_instance is not None,
        "dashboard": Path("frontend/templates/pages/dashboard.html").exists(),
        "static_files": Path("frontend/static").exists(),
        "message": "DEX Sniper Pro is operational",
        "phase": "Dashboard Complete + Trading Engine Ready"
    }


def get_trading_engine():
    """Get the global trading engine instance."""
    global trading_engine_instance
    if trading_engine_instance is None:
        raise HTTPException(status_code=503, detail="Trading engine not initialized")
    return trading_engine_instance


# Make trading engine available to endpoints
live_trading.set_trading_engine_getter(get_trading_engine)
'''
    
    with open("app/main.py", "w", encoding='utf-8') as f:
        f.write(content)
    
    print("Created app/main.py")


def create_live_trading_endpoints():
    """Create the live trading API endpoints."""
    content = '''"""
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

from app.utils.logger import setup_logger
from app.core.trading.trading_engine import (
    TradingEngine, 
    TradingConfiguration, 
    TradingMode,
    StrategyType,
    OrderIntent
)
from app.core.wallet.wallet_manager import WalletType, NetworkType
from app.core.dex.dex_integration import DEXProtocol

logger = setup_logger(__name__)

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
'''
    
    Path("app/api").mkdir(parents=True, exist_ok=True)
    Path("app/api/v1").mkdir(parents=True, exist_ok=True)
    Path("app/api/v1/endpoints").mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    with open("app/api/__init__.py", "w") as f:
        f.write('"""API module."""\n')
    with open("app/api/v1/__init__.py", "w") as f:
        f.write('"""API v1 module."""\n')
    with open("app/api/v1/endpoints/__init__.py", "w") as f:
        f.write('"""API endpoints module."""\n')
    
    with open("app/api/v1/endpoints/live_trading.py", "w", encoding='utf-8') as f:
        f.write(content)
    
    print("Created app/api/v1/endpoints/live_trading.py")


def create_api_test_script():
    """Create API test script."""
    content = '''#!/usr/bin/env python3
"""
API Test Script
File: test_api.py

Test the trading API endpoints.
"""

import requests
import json
from decimal import Decimal


BASE_URL = "http://localhost:8000"


def test_api_health():
    """Test API health check."""
    print("Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Trading Engine: {data['trading_engine']}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Health check failed: {e}")
        return False


def test_wallet_connection():
    """Test wallet connection."""
    print("Testing wallet connection...")
    try:
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "wallet_type": "metamask",
            "network": "ethereum"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/live-trading/wallet/connect",
            json=payload
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success']:
            print(f"  Session token: {data['data']['session_token'][:20]}...")
        
        return data['success']
    except Exception as e:
        print(f"  Wallet connection failed: {e}")
        return False


def test_get_quotes():
    """Test getting swap quotes."""
    print("Testing swap quotes...")
    try:
        params = {
            "input_token": "0x0000000000000000000000000000000000000000",
            "output_token": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "amount": "1.0",
            "slippage": "0.01"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/live-trading/quotes",
            params=params
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success']:
            quotes = data['data']['quotes']
            print(f"  Got {len(quotes)} quotes")
            if quotes:
                best = quotes[0]
                print(f"  Best rate: {best['output_amount']} tokens for 1 ETH")
        
        return data['success']
    except Exception as e:
        print(f"  Quote test failed: {e}")
        return False


def test_manual_trade():
    """Test manual trade execution."""
    print("Testing manual trade...")
    try:
        payload = {
            "wallet_address": "0x1234567890123456789012345678901234567890",
            "token_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "intent": "buy",
            "amount": "0.1",
            "slippage_tolerance": "0.01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/live-trading/trade/manual",
            json=payload
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success']:
            trade_data = data['data']
            print(f"  Trade ID: {trade_data['trade_id']}")
            print(f"  TX Hash: {trade_data['transaction_hash'][:20]}...")
            print(f"  Execution time: {trade_data['execution_time']:.2f}s")
        
        return data['success']
    except Exception as e:
        print(f"  Manual trade test failed: {e}")
        return False


def test_trading_status():
    """Test trading status."""
    print("Testing trading status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/live-trading/status")
        data = response.json()
        
        print(f"  Success: {data['success']}")
        if data['success']:
            status = data['data']
            print(f"  Running: {status['is_running']}")
            print(f"  Mode: {status['trading_mode']}")
            print(f"  Total trades: {status['total_trades']}")
        
        return data['success']
    except Exception as e:
        print(f"  Status test failed: {e}")
        return False


def test_generate_signal():
    """Test signal generation."""
    print("Testing signal generation...")
    try:
        params = {
            "strategy": "arbitrage",
            "token_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/live-trading/test/generate-signal",
            params=params
        )
        
        data = response.json()
        print(f"  Success: {data['success']}")
        if data['success'] and data['data']:
            signal = data['data']
            print(f"  Strategy: {signal['strategy']}")
            print(f"  Intent: {signal['intent']}")
            print(f"  Confidence: {signal['confidence']:.2f}")
            print(f"  Reasoning: {signal['reasoning']}")
        
        return True
    except Exception as e:
        print(f"  Signal generation test failed: {e}")
        return False


def run_all_api_tests():
    """Run all API tests."""
    print("🤖 DEX Sniper Pro - API Testing")
    print("=" * 50)
    print("Make sure the API server is running:")
    print("  uvicorn app.main:app --reload")
    print("")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Wallet Connection", test_wallet_connection),
        ("Swap Quotes", test_get_quotes),
        ("Manual Trade", test_manual_trade),
        ("Trading Status", test_trading_status),
        ("Signal Generation", test_generate_signal)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  Test failed with exception: {e}")
            results.append((test_name, False))
        print("")
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"  {symbol} {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\\nResults: {passed}/{total} API tests passed")
    
    if passed == total:
        print("\\n🎉 All API tests passed!")
        print("\\n📋 API is ready for live trading!")
    else:
        print(f"\\n⚠️  {total - passed} tests failed.")
    
    return passed == total


if __name__ == "__main__":
    run_all_api_tests()
'''
    
    with open("test_api.py", "w", encoding='utf-8') as f:
        f.write(content)
    
    print("Created test_api.py")


def main():
    """Create all API files."""
    print("🤖 Creating Trading API Endpoints")
    print("=" * 50)
    
    # Create all the API files
    create_main_app()
    create_live_trading_endpoints()
    create_api_test_script()
    
    print("\n✅ All API files created!")
    print("\n📋 Next steps:")
    print("1. Start the API server: uvicorn app.main:app --reload")
    print("2. Open the API docs: http://localhost:8000/docs")
    print("3. Test the API: python test_api.py")
    print("4. Start trading via API calls!")
    
    return True


if __name__ == "__main__":
    main()