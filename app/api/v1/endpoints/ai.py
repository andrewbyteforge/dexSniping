"""
AI API Endpoints
File: app/api/v1/endpoints/ai.py

Professional API endpoints for AI-powered trading operations including
real-time opportunity detection, auto-trading controls, and live feeds.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import json

from app.utils.logger import setup_logger, get_performance_logger, get_performance_logger
from app.core.ai.risk_assessor import AIRiskAssessor
from app.core.ai.honeypot_detector import HoneypotDetector
from app.core.ai.contract_analyzer import ContractAnalyzer
from app.core.trading.auto_trader import AutoTrader
from app.core.discovery.token_discovery import TokenDiscovery
from app.core.database import get_db_session

logger = setup_logger(__name__, "api")

router = APIRouter(prefix="/ai", tags=["AI Trading"])

# Global AI components
risk_assessor: Optional[AIRiskAssessor] = None
honeypot_detector: Optional[HoneypotDetector] = None
contract_analyzer: Optional[ContractAnalyzer] = None
auto_trader: Optional[AutoTrader] = None
token_discovery: Optional[TokenDiscovery] = None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class OpportunityRequest(BaseModel):
    """Request for trading opportunities."""
    network: str = Field(..., description="Blockchain network")
    min_liquidity: float = Field(10000, description="Minimum liquidity in USD")
    max_risk_score: float = Field(5.0, description="Maximum acceptable risk score")
    max_age_minutes: int = Field(30, description="Maximum token age in minutes")
    include_predictions: bool = Field(True, description="Include price predictions")


class AutoTraderConfig(BaseModel):
    """Auto-trader configuration."""
    enabled: bool = Field(..., description="Enable/disable auto-trading")
    networks: List[str] = Field(..., description="Networks to monitor")
    max_position_size: float = Field(0.1, description="Maximum position size in ETH")
    min_liquidity: float = Field(50000, description="Minimum liquidity required")
    max_risk_score: float = Field(3.0, description="Maximum risk score to trade")
    profit_target_percent: float = Field(20.0, description="Profit target percentage")
    stop_loss_percent: float = Field(10.0, description="Stop loss percentage")
    max_slippage_percent: float = Field(5.0, description="Maximum slippage")
    cooldown_minutes: int = Field(5, description="Cooldown between trades")


class TradeExecutionRequest(BaseModel):
    """Manual trade execution request."""
    token_address: str = Field(..., description="Token contract address")
    network: str = Field(..., description="Blockchain network")
    action: str = Field(..., description="buy or sell")
    amount_eth: float = Field(..., description="Amount in ETH")
    max_slippage: float = Field(5.0, description="Maximum slippage percentage")
    force_execute: bool = Field(False, description="Force execution despite warnings")


# ============================================================================
# LIVE OPPORTUNITY FEED
# ============================================================================

@router.get("/opportunities/live")
async def get_live_opportunities(
    request: OpportunityRequest = Depends(),
    db=Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Get live trading opportunities based on AI analysis.
    
    This endpoint provides real-time opportunities for the dashboard feed.
    """
    try:
        logger.info(f"🔍 Fetching live opportunities for {request.network}")
        
        if not token_discovery:
            raise HTTPException(status_code=503, detail="Token discovery service not available")
        
        # Get recently discovered tokens
        recent_tokens = await token_discovery.get_recent_tokens(
            network=request.network,
            max_age_minutes=request.max_age_minutes,
            min_liquidity=request.min_liquidity
        )
        
        opportunities = []
        
        for token in recent_tokens[:20]:  # Limit to top 20
            try:
                # Quick risk assessment
                if risk_assessor:
                    risk_result = await risk_assessor.quick_risk_assessment(
                        token['address'], request.network
                    )
                    
                    if risk_result['risk_score'] <= request.max_risk_score:
                        opportunity = {
                            "token_address": token['address'],
                            "symbol": token.get('symbol', 'Unknown'),
                            "name": token.get('name', 'Unknown'),
                            "network": request.network,
                            "discovery_time": token['discovered_at'],
                            "age_minutes": (datetime.utcnow() - token['discovered_at']).seconds // 60,
                            "current_price": token.get('price_usd', 0),
                            "liquidity_usd": token.get('liquidity_usd', 0),
                            "volume_24h": token.get('volume_24h', 0),
                            "risk_assessment": {
                                "risk_score": risk_result['risk_score'],
                                "risk_level": risk_result['risk_level'],
                                "confidence": risk_result['confidence'],
                                "warnings": risk_result.get('warnings', [])
                            },
                            "trading_signals": {
                                "recommended_action": "monitor" if risk_result['risk_score'] > 2 else "consider_buy",
                                "profit_potential": "medium",
                                "time_sensitivity": "high" if token.get('volume_24h', 0) > 10000 else "medium"
                            }
                        }
                        
                        # Add predictions if requested
                        if request.include_predictions and risk_assessor:
                            predictions = await risk_assessor.get_price_predictions(
                                token['address'], request.network
                            )
                            opportunity["price_predictions"] = predictions
                        
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.warning(f"Failed to assess token {token['address']}: {e}")
                continue
        
        return {
            "opportunities": opportunities,
            "total_found": len(opportunities),
            "scan_timestamp": datetime.utcnow().isoformat(),
            "scan_parameters": {
                "network": request.network,
                "min_liquidity": request.min_liquidity,
                "max_risk_score": request.max_risk_score,
                "max_age_minutes": request.max_age_minutes
            },
            "next_scan_in_seconds": 30
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get live opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch opportunities")


@router.get("/opportunities/stream")
async def stream_opportunities(
    network: str = Query(..., description="Blockchain network"),
    min_liquidity: float = Query(10000, description="Minimum liquidity"),
    max_risk_score: float = Query(5.0, description="Maximum risk score")
):
    """
    Stream live opportunities via Server-Sent Events.
    
    Provides real-time updates for the dashboard.
    """
    async def generate_opportunity_stream():
        """Generate live opportunity stream."""
        while True:
            try:
                # Get current opportunities
                request = OpportunityRequest(
                    network=network,
                    min_liquidity=min_liquidity,
                    max_risk_score=max_risk_score
                )
                
                opportunities = await get_live_opportunities(request)
                
                # Format as SSE
                data = json.dumps(opportunities)
                yield f"data: {data}\n\n"
                
                # Wait before next update
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                await asyncio.sleep(5)
    
    return StreamingResponse(
        generate_opportunity_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


# ============================================================================
# AUTO-TRADER CONTROLS
# ============================================================================

@router.post("/auto-trader/start")
async def start_auto_trader(
    config: AutoTraderConfig,
    background_tasks: BackgroundTasks,
    db=Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Start the auto-trading bot with specified configuration.
    """
    try:
        logger.info("🤖 Starting auto-trader with configuration")
        
        if not auto_trader:
            raise HTTPException(status_code=503, detail="Auto-trader service not available")
        
        # Validate configuration
        if config.max_risk_score > 7.0:
            raise HTTPException(status_code=400, detail="Maximum risk score too high")
        
        if config.max_position_size > 1.0:
            raise HTTPException(status_code=400, detail="Position size too large")
        
        # Configure auto-trader
        await auto_trader.configure(config.dict())
        
        # Start auto-trader in background
        background_tasks.add_task(auto_trader.start_trading)
        
        return {
            "status": "started",
            "message": "Auto-trader started successfully",
            "configuration": config.dict(),
            "start_time": datetime.utcnow().isoformat(),
            "trader_id": auto_trader.trader_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start auto-trader: {e}")
        raise HTTPException(status_code=500, detail="Failed to start auto-trader")


@router.post("/auto-trader/stop")
async def stop_auto_trader(db=Depends(get_db_session)) -> Dict[str, Any]:
    """Stop the auto-trading bot."""
    try:
        logger.info("🛑 Stopping auto-trader")
        
        if not auto_trader:
            raise HTTPException(status_code=503, detail="Auto-trader service not available")
        
        await auto_trader.stop_trading()
        
        return {
            "status": "stopped",
            "message": "Auto-trader stopped successfully",
            "stop_time": datetime.utcnow().isoformat(),
            "final_statistics": await auto_trader.get_statistics()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to stop auto-trader: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop auto-trader")


@router.get("/auto-trader/status")
async def get_auto_trader_status(db=Depends(get_db_session)) -> Dict[str, Any]:
    """Get current auto-trader status and statistics."""
    try:
        if not auto_trader:
            return {
                "status": "unavailable",
                "message": "Auto-trader service not initialized"
            }
        
        status = await auto_trader.get_status()
        statistics = await auto_trader.get_statistics()
        
        return {
            "status": status["status"],
            "is_active": status["is_active"],
            "uptime_seconds": status["uptime_seconds"],
            "current_positions": status["current_positions"],
            "statistics": statistics,
            "last_update": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get auto-trader status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")


# ============================================================================
# MANUAL TRADE EXECUTION
# ============================================================================

@router.post("/trade/execute")
async def execute_trade(
    trade_request: TradeExecutionRequest,
    db=Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Execute a manual trade with AI risk assessment.
    """
    try:
        logger.info(f"📈 Executing {trade_request.action} trade for {trade_request.token_address}")
        
        # Perform AI risk assessment first
        if risk_assessor and not trade_request.force_execute:
            risk_result = await risk_assessor.analyze_contract(
                trade_request.token_address,
                trade_request.network
            )
            
            if risk_result.risk_score > 7.0:
                return {
                    "status": "blocked",
                    "message": "Trade blocked due to high risk",
                    "risk_assessment": {
                        "risk_score": risk_result.risk_score,
                        "risk_level": risk_result.risk_level,
                        "warnings": risk_result.warnings
                    },
                    "recommendation": "Use force_execute=true to override"
                }
        
        # Execute trade via auto-trader
        if not auto_trader:
            raise HTTPException(status_code=503, detail="Trading service not available")
        
        execution_result = await auto_trader.execute_manual_trade(
            token_address=trade_request.token_address,
            network=trade_request.network,
            action=trade_request.action,
            amount_eth=trade_request.amount_eth,
            max_slippage=trade_request.max_slippage
        )
        
        return {
            "status": "executed",
            "trade_result": execution_result,
            "execution_time": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Trade execution failed: {e}")
        raise HTTPException(status_code=500, detail="Trade execution failed")


# ============================================================================
# AI ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/analyze/contract")
async def analyze_contract(
    token_address: str = Body(..., description="Token contract address"),
    network: str = Body(..., description="Blockchain network"),
    deep_analysis: bool = Body(True, description="Perform deep analysis"),
    db=Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Perform comprehensive AI contract analysis.
    """
    try:
        logger.info(f"🔍 Analyzing contract {token_address} on {network}")
        
        if not contract_analyzer:
            raise HTTPException(status_code=503, detail="Contract analyzer not available")
        
        # Get blockchain instance (simplified)
        from app.core.blockchain.ethereum import EthereumChain
        chain = EthereumChain()
        
        # Perform analysis
        analysis_result = await contract_analyzer.analyze_contract(
            token_address, network, chain
        )
        
        return {
            "contract_analysis": {
                "token_address": analysis_result.token_address,
                "network": analysis_result.network,
                "contract_type": analysis_result.contract_type.value,
                "security_risk": analysis_result.security_risk.value,
                "risk_score": analysis_result.risk_score,
                "confidence": analysis_result.confidence,
                
                "token_info": {
                    "name": analysis_result.name,
                    "symbol": analysis_result.symbol,
                    "decimals": analysis_result.decimals,
                    "total_supply": str(analysis_result.total_supply)
                },
                
                "security_flags": {
                    "honeypot_indicators": analysis_result.honeypot_indicators,
                    "rugpull_indicators": analysis_result.rugpull_indicators,
                    "has_mint_function": analysis_result.has_mint_function,
                    "has_pause_function": analysis_result.has_pause_function,
                    "has_blacklist_function": analysis_result.has_blacklist_function
                },
                
                "trading_info": {
                    "can_buy": analysis_result.can_buy,
                    "can_sell": analysis_result.can_sell,
                    "has_transfer_fees": analysis_result.has_transfer_fees,
                    "transfer_fee_percentage": analysis_result.transfer_fee_percentage
                },
                
                "liquidity_info": {
                    "liquidity_locked": analysis_result.liquidity_locked,
                    "current_liquidity_usd": analysis_result.current_liquidity_usd
                },
                
                "warnings": analysis_result.warnings,
                "recommendations": analysis_result.recommendations,
                "analysis_timestamp": analysis_result.analysis_timestamp.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Contract analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Contract analysis failed")


@router.post("/honeypot/detect")
async def detect_honeypot(
    token_address: str = Body(..., description="Token contract address"),
    network: str = Body(..., description="Blockchain network"),
    db=Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Detect honeypot contracts with high accuracy.
    """
    try:
        logger.info(f"🍯 Detecting honeypot for {token_address}")
        
        if not honeypot_detector:
            raise HTTPException(status_code=503, detail="Honeypot detector not available")
        
        # Get blockchain instance (simplified)
        from app.core.blockchain.ethereum import EthereumChain
        chain = EthereumChain()
        
        detection_result = await honeypot_detector.detect_honeypot(
            token_address, network, chain
        )
        
        return {
            "honeypot_detection": {
                "is_honeypot": detection_result.is_honeypot,
                "confidence": detection_result.confidence,
                "risk_level": detection_result.risk_level.value,
                "honeypot_probability": detection_result.honeypot_probability,
                "warning_signals": detection_result.warning_signals,
                "safe_signals": detection_result.safe_signals,
                "recommendation": detection_result.recommendation,
                "analysis_timestamp": detection_result.analysis_timestamp.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Honeypot detection failed: {e}")
        raise HTTPException(status_code=500, detail="Honeypot detection failed")


# ============================================================================
# SYSTEM STATUS & HEALTH
# ============================================================================

@router.get("/status")
async def get_ai_system_status() -> Dict[str, Any]:
    """Get AI system status and health."""
    try:
        return {
            "ai_services": {
                "risk_assessor": "available" if risk_assessor else "unavailable",
                "honeypot_detector": "available" if honeypot_detector else "unavailable",
                "contract_analyzer": "available" if contract_analyzer else "unavailable",
                "auto_trader": "available" if auto_trader else "unavailable",
                "token_discovery": "available" if token_discovery else "unavailable"
            },
            "system_health": "operational",
            "last_updated": datetime.utcnow().isoformat(),
            "uptime_status": "online"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get AI system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


# ============================================================================
# INITIALIZATION
# ============================================================================

async def initialize_ai_services():
    """Initialize AI services on startup."""
    global risk_assessor, honeypot_detector, contract_analyzer, auto_trader, token_discovery
    
    try:
        logger.info("🤖 Initializing AI services...")
        
        # Initialize AI components
        from app.core.ai.risk_assessor import AIRiskAssessor
        from app.core.ai.honeypot_detector import HoneypotDetector
        from app.core.ai.contract_analyzer import create_contract_analyzer
        from app.core.trading.auto_trader import AutoTrader
        from app.core.discovery.token_discovery import TokenDiscovery
        
        risk_assessor = AIRiskAssessor()
        honeypot_detector = HoneypotDetector()
        contract_analyzer = await create_contract_analyzer()
        auto_trader = AutoTrader()
        token_discovery = TokenDiscovery()
        
        # Initialize each service
        await risk_assessor.initialize_models()
        await honeypot_detector.initialize()
        await auto_trader.initialize()
        await token_discovery.initialize()
        
        logger.info("✅ AI services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI services: {e}")
        return False


# Startup event
@router.on_event("startup")
async def startup_ai_services():
    """Initialize AI services on router startup."""
    await initialize_ai_services()