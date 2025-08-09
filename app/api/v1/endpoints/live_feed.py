"""
Dashboard Live Feed Integration
File: app/api/v1/endpoints/live_feed.py

Real-time dashboard feed showing live opportunities, auto-trader status,
and trading controls for the DEX sniping platform.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.utils.logger import setup_logger, get_performance_logger, get_performance_logger
from app.core.discovery.token_scanner import TokenScanner
from app.core.ai.risk_assessor import AIRiskAssessor
from app.core.trading.auto_trader import AutoTrader, AutoTraderConfig
from app.core.database import get_db_session

logger = setup_logger(__name__, "api")

router = APIRouter(prefix="/live", tags=["Live Feed"])

# Global services
token_scanner: Optional[TokenScanner] = None
risk_assessor: Optional[AIRiskAssessor] = None
auto_trader: Optional[AutoTrader] = None

# Live feed cache
live_opportunities_cache = []
last_cache_update = datetime.utcnow()
cache_ttl_seconds = 30


class LiveFeedRequest(BaseModel):
    """Request for live feed configuration."""
    networks: List[str] = Field(default=["ethereum"], description="Networks to monitor")
    min_liquidity: float = Field(default=10000, description="Minimum liquidity in USD")
    max_risk_score: float = Field(default=5.0, description="Maximum risk score")
    update_interval: int = Field(default=30, description="Update interval in seconds")


class TradingControlRequest(BaseModel):
    """Trading control request."""
    action: str = Field(..., description="start, stop, pause, resume")
    config: Optional[AutoTraderConfig] = Field(None, description="Trading configuration")


@router.get("/opportunities")
async def get_live_opportunities(
    network: str = Query("ethereum", description="Blockchain network"),
    min_liquidity: float = Query(10000, description="Minimum liquidity USD"),
    max_risk_score: float = Query(5.0, description="Maximum risk score"),
    limit: int = Query(20, description="Maximum opportunities to return")
) -> Dict[str, Any]:
    """
    Get current live trading opportunities.
    
    This is the main endpoint for the dashboard opportunity feed.
    """
    try:
        global live_opportunities_cache, last_cache_update
        
        # Check if cache is still valid
        cache_age = (datetime.utcnow() - last_cache_update).total_seconds()
        
        if cache_age < cache_ttl_seconds and live_opportunities_cache:
            logger.debug("Returning cached opportunities")
            filtered_opportunities = [
                opp for opp in live_opportunities_cache
                if (opp.get('network') == network and 
                    opp.get('liquidity_usd', 0) >= min_liquidity and
                    opp.get('risk_score', 10) <= max_risk_score)
            ][:limit]
            
            return {
                "opportunities": filtered_opportunities,
                "total_found": len(filtered_opportunities),
                "last_updated": last_cache_update.isoformat(),
                "cache_hit": True,
                "scan_status": "cached"
            }
        
        # Refresh opportunities
        opportunities = await _scan_for_opportunities(
            network, min_liquidity, max_risk_score, limit
        )
        
        # Update cache
        live_opportunities_cache = opportunities
        last_cache_update = datetime.utcnow()
        
        return {
            "opportunities": opportunities,
            "total_found": len(opportunities),
            "last_updated": last_cache_update.isoformat(),
            "cache_hit": False,
            "scan_status": "fresh_scan"
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to get live opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch opportunities")


@router.get("/stream")
async def stream_live_feed(
    network: str = Query("ethereum", description="Network to monitor"),
    min_liquidity: float = Query(10000, description="Minimum liquidity"),
    max_risk_score: float = Query(5.0, description="Maximum risk score")
):
    """
    Stream live opportunities via Server-Sent Events for real-time dashboard updates.
    """
    async def event_generator():
        """Generate live events for the dashboard."""
        last_update = datetime.utcnow()
        
        while True:
            try:
                # Get current opportunities
                opportunities = await _scan_for_opportunities(
                    network, min_liquidity, max_risk_score, 20
                )
                
                # Get auto-trader status
                trader_status = await _get_auto_trader_status()
                
                # Get system health
                system_health = await _get_system_health()
                
                # Create event data
                event_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "opportunities": opportunities,
                    "trader_status": trader_status,
                    "system_health": system_health,
                    "feed_config": {
                        "network": network,
                        "min_liquidity": min_liquidity,
                        "max_risk_score": max_risk_score
                    }
                }
                
                yield {
                    "event": "live_update",
                    "data": json.dumps(event_data)
                }
                
                # Wait for next update
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"[ERROR] Stream error: {e}")
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e), "timestamp": datetime.utcnow().isoformat()})
                }
                await asyncio.sleep(5)
    
    return EventSourceResponse(event_generator())


@router.post("/trading/control")
async def control_auto_trader(
    request: TradingControlRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Control auto-trader (start, stop, pause, resume).
    
    This is the main control interface for the auto-trading bot.
    """
    try:
        if not auto_trader:
            raise HTTPException(status_code=503, detail="Auto-trader service not available")
        
        action = request.action.lower()
        
        if action == "start":
            if not request.config:
                raise HTTPException(status_code=400, detail="Configuration required for start action")
            
            # Configure and start auto-trader
            await auto_trader.configure(request.config.dict())
            background_tasks.add_task(auto_trader.start_trading)
            
            return {
                "status": "started",
                "message": "Auto-trader started successfully",
                "configuration": request.config.dict(),
                "trader_id": auto_trader.trader_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        elif action == "stop":
            await auto_trader.stop_trading()
            
            return {
                "status": "stopped",
                "message": "Auto-trader stopped successfully",
                "final_stats": await auto_trader.get_statistics(),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        elif action == "pause":
            await auto_trader.pause_trading()
            
            return {
                "status": "paused",
                "message": "Auto-trader paused successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        elif action == "resume":
            await auto_trader.resume_trading()
            
            return {
                "status": "resumed",
                "message": "Auto-trader resumed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
        
    except Exception as e:
        logger.error(f"[ERROR] Auto-trader control failed: {e}")
        raise HTTPException(status_code=500, detail="Auto-trader control failed")


@router.get("/trading/status")
async def get_trading_status() -> Dict[str, Any]:
    """Get comprehensive trading status including positions and statistics."""
    try:
        if not auto_trader:
            return {
                "auto_trader": "unavailable",
                "message": "Auto-trader service not initialized"
            }
        
        # Get auto-trader status
        status = await auto_trader.get_status()
        statistics = await auto_trader.get_statistics()
        active_positions = await auto_trader.get_active_positions()
        recent_trades = await auto_trader.get_trade_history(limit=10)
        
        return {
            "auto_trader": {
                "status": status["status"],
                "is_active": status["is_active"],
                "uptime_seconds": status["uptime_seconds"],
                "trader_id": status["trader_id"],
                "enabled_networks": status["enabled_networks"],
                "configuration": status["configuration"]
            },
            "statistics": statistics,
            "active_positions": active_positions,
            "recent_trades": recent_trades,
            "position_summary": {
                "total_positions": len(active_positions),
                "profitable_positions": len([p for p in active_positions if p.get('current_pnl', 0) > 0]),
                "losing_positions": len([p for p in active_positions if p.get('current_pnl', 0) < 0]),
                "total_unrealized_pnl": sum(p.get('current_pnl', 0) for p in active_positions)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to get trading status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trading status")


@router.get("/system/health")
async def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health status."""
    try:
        health_status = await _get_system_health()
        
        return {
            "system_health": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post("/scan/trigger")
async def trigger_manual_scan(
    network: str = Query("ethereum", description="Network to scan"),
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Trigger manual token discovery scan."""
    try:
        if not token_scanner:
            raise HTTPException(status_code=503, detail="Token scanner not available")
        
        # Trigger scan in background
        background_tasks.add_task(_perform_manual_scan, network)
        
        return {
            "status": "triggered",
            "message": f"Manual scan initiated for {network}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Manual scan trigger failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger scan")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _scan_for_opportunities(
    network: str,
    min_liquidity: float,
    max_risk_score: float,
    limit: int
) -> List[Dict[str, Any]]:
    """Scan for trading opportunities with AI analysis."""
    opportunities = []
    
    try:
        if not token_scanner:
            logger.warning("Token scanner not available")
            return []
        
        # Scan for new tokens
        scan_results = await token_scanner.scan_network(
            network,
            block_offset=10,
            filters={"check_liquidity": True, "min_liquidity_usd": min_liquidity}
        )
        
        # Analyze each token with AI
        for token in scan_results.tokens_found[:limit]:
            try:
                if risk_assessor:
                    # Quick risk assessment
                    risk_result = await risk_assessor.quick_risk_assessment(
                        token.address, network
                    )
                    
                    if risk_result['risk_score'] <= max_risk_score:
                        opportunity = {
                            "token_address": token.address,
                            "symbol": token.symbol,
                            "name": token.name,
                            "network": network,
                            "price_usd": 0.001,  # Mock price - replace with real price
                            "liquidity_usd": 50000,  # Mock liquidity - replace with real
                            "age_minutes": 5,  # Mock age - calculate from creation time
                            "risk_score": risk_result['risk_score'],
                            "risk_level": risk_result['risk_level'],
                            "confidence": risk_result['confidence'],
                            "ai_signals": {
                                "recommended_action": "monitor" if risk_result['risk_score'] > 2 else "consider_buy",
                                "profit_potential": "medium",
                                "time_sensitivity": "high"
                            },
                            "discovered_at": datetime.utcnow().isoformat()
                        }
                        
                        opportunities.append(opportunity)
                
            except Exception as e:
                logger.warning(f"Failed to analyze token {token.address}: {e}")
                continue
        
        # Sort by risk score (lowest risk first)
        opportunities.sort(key=lambda x: x['risk_score'])
        
        return opportunities
        
    except Exception as e:
        logger.error(f"[ERROR] Opportunity scanning failed: {e}")
        return []


async def _get_auto_trader_status() -> Dict[str, Any]:
    """Get auto-trader status summary."""
    try:
        if not auto_trader:
            return {"status": "unavailable"}
        
        status = await auto_trader.get_status()
        statistics = await auto_trader.get_statistics()
        
        return {
            "status": status["status"],
            "is_active": status["is_active"],
            "current_positions": status["current_positions"],
            "total_trades": statistics["total_trades"],
            "success_rate": statistics["success_rate"],
            "total_profit_loss": statistics["total_profit_loss"]
        }
        
    except Exception as e:
        logger.warning(f"Failed to get auto-trader status: {e}")
        return {"status": "error", "error": str(e)}


async def _get_system_health() -> Dict[str, Any]:
    """Get system health summary."""
    health = {
        "overall_status": "healthy",
        "services": {}
    }
    
    try:
        # Check token scanner
        if token_scanner:
            scanner_health = await token_scanner.health_check()
            health["services"]["token_scanner"] = scanner_health["status"]
        else:
            health["services"]["token_scanner"] = "unavailable"
        
        # Check auto-trader
        if auto_trader:
            health["services"]["auto_trader"] = "available"
        else:
            health["services"]["auto_trader"] = "unavailable"
        
        # Check risk assessor
        if risk_assessor:
            health["services"]["risk_assessor"] = "available"
        else:
            health["services"]["risk_assessor"] = "unavailable"
        
        # Determine overall status
        unhealthy_services = [
            name for name, status in health["services"].items()
            if status in ["unavailable", "unhealthy", "error"]
        ]
        
        if len(unhealthy_services) > 2:
            health["overall_status"] = "unhealthy"
        elif len(unhealthy_services) > 0:
            health["overall_status"] = "degraded"
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health["overall_status"] = "error"
        health["error"] = str(e)
    
    return health


async def _perform_manual_scan(network: str):
    """Perform manual scan in background."""
    try:
        if token_scanner:
            logger.info(f"[SEARCH] Performing manual scan for {network}")
            
            results = await token_scanner.scan_network(network, block_offset=20)
            
            logger.info(f"[OK] Manual scan complete: {len(results.tokens_found)} tokens found")
            
            # Clear cache to force fresh data
            global last_cache_update
            last_cache_update = datetime.utcnow() - timedelta(minutes=5)
        
    except Exception as e:
        logger.error(f"[ERROR] Manual scan failed: {e}")


# ============================================================================
# INITIALIZATION
# ============================================================================

async def initialize_live_feed_services():
    """Initialize live feed services."""
    global token_scanner, risk_assessor, auto_trader
    
    try:
        logger.info("[START] Initializing live feed services...")
        
        # Initialize services
        from app.core.discovery.token_scanner import TokenScanner
        from app.core.ai.risk_assessor import AIRiskAssessor
        from app.core.trading.auto_trader import create_auto_trader
        
        token_scanner = TokenScanner()
        risk_assessor = AIRiskAssessor()
        auto_trader = await create_auto_trader()
        
        logger.info("[OK] Live feed services initialized")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize live feed services: {e}")
        return False


# Startup event
@router.on_event("startup")
async def startup_live_feed():
    """Initialize live feed on startup."""
    await initialize_live_feed_services()