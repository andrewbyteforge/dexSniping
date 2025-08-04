"""
Live Trading API Endpoints - Phase 4B Implementation
File: app/api/v1/endpoints/live_trading_api.py

REST API endpoints for live trading functionality including wallet connections,
trading sessions, opportunity monitoring, and real-time trade execution.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from sse_starlette.sse import EventSourceResponse
import json

from app.core.trading.live_trading_engine_enhanced import (
    LiveTradingEngineEnhanced,
    TradingConfiguration,
    TradingMode,
    TradingStrategy,
    TradingSession,
    TradingOpportunity,
    get_live_trading_engine
)
from app.core.wallet.wallet_connection_manager import (
    WalletConnectionManager,
    WalletType,
    NetworkType,
    WalletConnection,
    get_wallet_connection_manager
)
from app.core.dex.live_dex_integration import (
    LiveDEXIntegration,
    DEXProtocol,
    SwapQuote,
    get_live_dex_integration
)
from app.utils.logger import setup_logger
from app.core.exceptions import TradingError, WalletError, DEXError

logger = setup_logger(__name__)

# Initialize router
router = APIRouter(prefix="/live-trading", tags=["Live Trading"])

# ==================== REQUEST/RESPONSE MODELS ====================

class WalletConnectionRequest(BaseModel):
    """Wallet connection request."""
    wallet_address: str = Field(..., description="Wallet address to connect")
    wallet_type: WalletType = Field(WalletType.METAMASK, description="Wallet type")
    requested_networks: List[NetworkType] = Field(
        default=[NetworkType.ETHEREUM], 
        description="Networks to connect"
    )
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not v or len(v) != 42 or not v.startswith('0x'):
            raise ValueError('Invalid wallet address format')
        return v.lower()


class TradingConfigRequest(BaseModel):
    """Trading configuration request."""
    trading_mode: TradingMode = Field(TradingMode.SEMI_AUTOMATED, description="Trading mode")
    enabled_strategies: List[TradingStrategy] = Field(
        default=[TradingStrategy.ARBITRAGE], 
        description="Enabled strategies"
    )
    enabled_networks: List[NetworkType] = Field(
        default=[NetworkType.ETHEREUM], 
        description="Enabled networks"
    )
    max_position_size_usd: Decimal = Field(
        default=Decimal("1000"), 
        ge=0, 
        description="Maximum position size USD"
    )
    max_daily_loss_usd: Decimal = Field(
        default=Decimal("100"), 
        ge=0, 
        description="Maximum daily loss USD"
    )
    default_slippage_percent: Decimal = Field(
        default=Decimal("1.0"), 
        ge=0, 
        le=10, 
        description="Default slippage percentage"
    )


class ManualTradeRequest(BaseModel):
    """Manual trade execution request."""
    input_token: str = Field(..., description="Input token address")
    output_token: str = Field(..., description="Output token address")
    input_amount: Decimal = Field(..., gt=0, description="Input amount")
    network: NetworkType = Field(..., description="Network for trade")
    dex_protocol: Optional[DEXProtocol] = Field(None, description="Specific DEX to use")
    slippage_percent: Optional[Decimal] = Field(None, ge=0, le=10, description="Slippage tolerance")
    max_gas_price_gwei: Optional[Decimal] = Field(None, gt=0, description="Maximum gas price")


class WalletConnectionResponse(BaseModel):
    """Wallet connection response."""
    connection_id: str
    wallet_address: str
    wallet_type: WalletType
    connected_networks: List[NetworkType]
    balances: Dict[str, Dict[str, Any]]
    status: str
    session_expires: Optional[datetime]


class TradingSessionResponse(BaseModel):
    """Trading session response."""
    session_id: str
    wallet_connection_id: str
    configuration: Dict[str, Any]
    start_time: datetime
    is_active: bool
    performance_metrics: Dict[str, Any]


class OpportunityResponse(BaseModel):
    """Trading opportunity response."""
    opportunity_id: str
    strategy: TradingStrategy
    network: NetworkType
    dex_protocol: DEXProtocol
    input_token: Dict[str, Any]
    output_token: Dict[str, Any]
    recommended_amount: Decimal
    expected_profit_usd: Decimal
    expected_profit_percent: Decimal
    confidence_score: Decimal
    risk_level: str
    time_sensitivity: str
    expires_at: datetime


class SwapQuoteResponse(BaseModel):
    """Swap quote response."""
    quote_id: str
    dex_protocol: DEXProtocol
    network: NetworkType
    input_amount: Decimal
    output_amount: Decimal
    price_impact: Decimal
    estimated_gas: int
    gas_price_gwei: Decimal
    estimated_gas_cost_eth: Decimal
    exchange_rate: Decimal
    expires_at: datetime


# ==================== DEPENDENCY INJECTION ====================

def get_trading_engine() -> LiveTradingEngineEnhanced:
    """Get trading engine dependency."""
    return get_live_trading_engine()


def get_wallet_manager() -> WalletConnectionManager:
    """Get wallet manager dependency."""
    return get_wallet_connection_manager()


def get_dex_integration() -> LiveDEXIntegration:
    """Get DEX integration dependency."""
    return get_live_dex_integration()


# ==================== WALLET CONNECTION ENDPOINTS ====================

@router.post("/wallet/connect", response_model=WalletConnectionResponse)
async def connect_wallet(
    request: WalletConnectionRequest,
    wallet_manager: WalletConnectionManager = Depends(get_wallet_manager)
) -> WalletConnectionResponse:
    """
    Connect wallet for trading.
    
    Establishes connection to user's wallet (MetaMask, WalletConnect, etc.)
    and verifies access across requested networks.
    """
    try:
        logger.info(f"🔗 Connecting wallet: {request.wallet_address[:10]}...")
        
        # Connect wallet based on type
        if request.wallet_type == WalletType.METAMASK:
            connection = await wallet_manager.connect_metamask(
                wallet_address=request.wallet_address,
                requested_networks=request.requested_networks
            )
        elif request.wallet_type == WalletType.WALLET_CONNECT:
            connection = await wallet_manager.connect_wallet_connect(
                wallet_address=request.wallet_address
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Wallet type {request.wallet_type} not supported"
            )
        
        # Format response
        connected_networks = [
            network for network, is_connected in connection.connected_networks.items()
            if is_connected
        ]
        
        balances = {}
        for network, balance in connection.balances.items():
            balances[network.value] = {
                "native_balance": str(balance.native_balance),
                "native_symbol": balance.native_symbol,
                "usd_value": str(balance.usd_value) if balance.usd_value else None,
                "last_updated": balance.last_updated.isoformat()
            }
        
        return WalletConnectionResponse(
            connection_id=connection.connection_id,
            wallet_address=connection.wallet_address,
            wallet_type=connection.wallet_type,
            connected_networks=connected_networks,
            balances=balances,
            status=connection.status.value,
            session_expires=connection.session_expires
        )
        
    except WalletError as e:
        logger.error(f"❌ Wallet connection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected wallet connection error: {e}")
        raise HTTPException(status_code=500, detail="Wallet connection failed")


@router.get("/wallet/connections")
async def get_wallet_connections(
    wallet_manager: WalletConnectionManager = Depends(get_wallet_manager)
) -> Dict[str, WalletConnectionResponse]:
    """Get all active wallet connections."""
    try:
        connections = wallet_manager.get_active_connections()
        
        response = {}
        for conn_id, connection in connections.items():
            connected_networks = [
                network for network, is_connected in connection.connected_networks.items()
                if is_connected
            ]
            
            balances = {}
            for network, balance in connection.balances.items():
                balances[network.value] = {
                    "native_balance": str(balance.native_balance),
                    "native_symbol": balance.native_symbol,
                    "last_updated": balance.last_updated.isoformat()
                }
            
            response[conn_id] = WalletConnectionResponse(
                connection_id=connection.connection_id,
                wallet_address=connection.wallet_address,
                wallet_type=connection.wallet_type,
                connected_networks=connected_networks,
                balances=balances,
                status=connection.status.value,
                session_expires=connection.session_expires
            )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get wallet connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve connections")


@router.delete("/wallet/disconnect/{connection_id}")
async def disconnect_wallet(
    connection_id: str,
    wallet_manager: WalletConnectionManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """Disconnect wallet."""
    try:
        success = await wallet_manager.disconnect_wallet(connection_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Connection {connection_id} not found"
            )
        
        return {"message": "Wallet disconnected successfully", "connection_id": connection_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to disconnect wallet: {e}")
        raise HTTPException(status_code=500, detail="Wallet disconnection failed")


# ==================== TRADING SESSION ENDPOINTS ====================

@router.post("/session/start", response_model=TradingSessionResponse)
async def start_trading_session(
    wallet_connection_id: str = Field(..., description="Wallet connection ID"),
    config_request: Optional[TradingConfigRequest] = None,
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> TradingSessionResponse:
    """
    Start new trading session.
    
    Creates active trading session with specified configuration
    and begins monitoring for opportunities.
    """
    try:
        logger.info(f"🎯 Starting trading session for wallet: {wallet_connection_id}")
        
        # Convert request to configuration
        configuration = None
        if config_request:
            configuration = TradingConfiguration(
                trading_mode=config_request.trading_mode,
                enabled_strategies=config_request.enabled_strategies,
                enabled_networks=config_request.enabled_networks,
                preferred_dexes=[DEXProtocol.UNISWAP_V2, DEXProtocol.SUSHISWAP],
                max_position_size_usd=config_request.max_position_size_usd,
                max_daily_loss_usd=config_request.max_daily_loss_usd,
                max_single_trade_usd=config_request.max_position_size_usd / 5,
                max_slippage_percent=config_request.default_slippage_percent * 2,
                max_price_impact_percent=Decimal("5.0"),
                default_slippage_percent=config_request.default_slippage_percent,
                gas_price_strategy="standard",
                max_gas_price_gwei=Decimal("100"),
                transaction_timeout_seconds=300,
                reserve_balance_percent=Decimal("10"),
                rebalance_threshold_percent=Decimal("5"),
                profit_taking_percent=Decimal("15"),
                stop_loss_percent=Decimal("5")
            )
        
        # Start session
        session = await trading_engine.start_trading_session(
            wallet_connection_id=wallet_connection_id,
            configuration=configuration
        )
        
        # Format response
        return TradingSessionResponse(
            session_id=session.session_id,
            wallet_connection_id=session.wallet_connection_id,
            configuration={
                "trading_mode": session.configuration.trading_mode.value,
                "enabled_strategies": [s.value for s in session.configuration.enabled_strategies],
                "enabled_networks": [n.value for n in session.configuration.enabled_networks],
                "max_position_size_usd": str(session.configuration.max_position_size_usd),
                "max_daily_loss_usd": str(session.configuration.max_daily_loss_usd)
            },
            start_time=session.start_time,
            is_active=session.is_active,
            performance_metrics={
                "total_trades": session.total_trades,
                "successful_trades": session.successful_trades,
                "success_rate": str(session.success_rate),
                "net_profit_usd": str(session.net_profit_usd),
                "daily_loss_usd": str(session.daily_loss_usd)
            }
        )
        
    except TradingError as e:
        logger.error(f"❌ Trading session start failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected session start error: {e}")
        raise HTTPException(status_code=500, detail="Session start failed")


@router.get("/session/active")
async def get_active_sessions(
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, TradingSessionResponse]:
    """Get all active trading sessions."""
    try:
        sessions = trading_engine.get_active_sessions()
        
        response = {}
        for session_id, session in sessions.items():
            response[session_id] = TradingSessionResponse(
                session_id=session.session_id,
                wallet_connection_id=session.wallet_connection_id,
                configuration={
                    "trading_mode": session.configuration.trading_mode.value,
                    "enabled_strategies": [s.value for s in session.configuration.enabled_strategies],
                    "max_position_size_usd": str(session.configuration.max_position_size_usd)
                },
                start_time=session.start_time,
                is_active=session.is_active,
                performance_metrics={
                    "total_trades": session.total_trades,
                    "successful_trades": session.successful_trades,
                    "success_rate": str(session.success_rate),
                    "net_profit_usd": str(session.net_profit_usd)
                }
            )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get active sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


@router.delete("/session/stop/{session_id}")
async def stop_trading_session(
    session_id: str,
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """Stop trading session."""
    try:
        success = await trading_engine.stop_trading_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {"message": "Trading session stopped", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to stop session: {e}")
        raise HTTPException(status_code=500, detail="Session stop failed")


# ==================== OPPORTUNITY MONITORING ENDPOINTS ====================

@router.get("/opportunities")
async def get_trading_opportunities(
    network: Optional[NetworkType] = Query(None, description="Filter by network"),
    strategy: Optional[TradingStrategy] = Query(None, description="Filter by strategy"),
    min_confidence: Optional[int] = Query(80, description="Minimum confidence score"),
    limit: Optional[int] = Query(20, description="Maximum opportunities to return"),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> List[OpportunityResponse]:
    """
    Get current trading opportunities.
    
    Returns detected trading opportunities that match the specified filters.
    Opportunities are automatically detected by the monitoring system.
    """
    try:
        all_opportunities = trading_engine.get_detected_opportunities()
        
        # Apply filters
        filtered_opportunities = []
        for opportunity in all_opportunities.values():
            # Network filter
            if network and opportunity.network != network:
                continue
            
            # Strategy filter
            if strategy and opportunity.strategy != strategy:
                continue
            
            # Confidence filter
            if min_confidence and opportunity.confidence_score < min_confidence:
                continue
            
            # Skip expired opportunities
            if opportunity.is_expired:
                continue
            
            filtered_opportunities.append(opportunity)
        
        # Sort by risk-adjusted score
        filtered_opportunities.sort(
            key=lambda x: x.risk_adjusted_score,
            reverse=True
        )
        
        # Apply limit
        if limit:
            filtered_opportunities = filtered_opportunities[:limit]
        
        # Format response
        response = []
        for opportunity in filtered_opportunities:
            response.append(OpportunityResponse(
                opportunity_id=opportunity.opportunity_id,
                strategy=opportunity.strategy,
                network=opportunity.network,
                dex_protocol=opportunity.dex_protocol,
                input_token={
                    "address": opportunity.input_token.address,
                    "symbol": opportunity.input_token.symbol,
                    "name": opportunity.input_token.name,
                    "decimals": opportunity.input_token.decimals
                },
                output_token={
                    "address": opportunity.output_token.address,
                    "symbol": opportunity.output_token.symbol,
                    "name": opportunity.output_token.name,
                    "decimals": opportunity.output_token.decimals
                },
                recommended_amount=opportunity.recommended_amount,
                expected_profit_usd=opportunity.expected_profit_usd,
                expected_profit_percent=opportunity.expected_profit_percent,
                confidence_score=opportunity.confidence_score,
                risk_level=opportunity.risk_level.value,
                time_sensitivity=opportunity.time_sensitivity,
                expires_at=opportunity.expires_at
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve opportunities")


@router.get("/opportunities/stream")
async def stream_opportunities(
    network: Optional[NetworkType] = Query(None, description="Filter by network"),
    min_confidence: Optional[int] = Query(80, description="Minimum confidence score"),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> EventSourceResponse:
    """
    Stream live trading opportunities.
    
    Provides real-time server-sent events stream of trading opportunities
    as they are detected by the monitoring system.
    """
    async def opportunity_generator():
        """Generate opportunity events."""
        last_sent_opportunities = set()
        
        while True:
            try:
                current_opportunities = trading_engine.get_detected_opportunities()
                
                # Find new opportunities
                current_ids = set(current_opportunities.keys())
                new_opportunity_ids = current_ids - last_sent_opportunities
                
                # Send new opportunities
                for opp_id in new_opportunity_ids:
                    opportunity = current_opportunities[opp_id]
                    
                    # Apply filters
                    if network and opportunity.network != network:
                        continue
                    
                    if min_confidence and opportunity.confidence_score < min_confidence:
                        continue
                    
                    if opportunity.is_expired:
                        continue
                    
                    # Format event data
                    event_data = {
                        "opportunity_id": opportunity.opportunity_id,
                        "strategy": opportunity.strategy.value,
                        "network": opportunity.network.value,
                        "expected_profit_usd": str(opportunity.expected_profit_usd),
                        "confidence_score": str(opportunity.confidence_score),
                        "risk_level": opportunity.risk_level.value,
                        "expires_at": opportunity.expires_at.isoformat()
                    }
                    
                    yield {
                        "event": "opportunity_detected",
                        "data": json.dumps(event_data)
                    }
                
                last_sent_opportunities = current_ids
                
                # Wait before next check
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Opportunity stream error: {e}")
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)})
                }
                await asyncio.sleep(10)
    
    return EventSourceResponse(opportunity_generator())


# ==================== TRADING EXECUTION ENDPOINTS ====================

@router.post("/trade/quote", response_model=SwapQuoteResponse)
async def get_swap_quote(
    input_token: str = Field(..., description="Input token address"),
    output_token: str = Field(..., description="Output token address"),
    input_amount: Decimal = Field(..., gt=0, description="Input amount"),
    network: NetworkType = Field(..., description="Network"),
    dex_protocol: Optional[DEXProtocol] = Query(None, description="Specific DEX"),
    slippage_percent: Optional[Decimal] = Query(None, ge=0, le=10, description="Slippage"),
    dex_integration: LiveDEXIntegration = Depends(get_dex_integration)
) -> SwapQuoteResponse:
    """
    Get swap quote for token pair.
    
    Returns detailed quote including price impact, gas estimates,
    and minimum output amount with slippage protection.
    """
    try:
        logger.info(f"💹 Getting swap quote: {input_amount} {input_token[:10]}... → {output_token[:10]}...")
        
        quote = await dex_integration.get_swap_quote(
            input_token=input_token,
            output_token=output_token,
            input_amount=input_amount,
            network=network,
            dex_protocol=dex_protocol,
            slippage_percent=slippage_percent
        )
        
        return SwapQuoteResponse(
            quote_id=quote.quote_id,
            dex_protocol=quote.dex_protocol,
            network=quote.network,
            input_amount=quote.input_amount,
            output_amount=quote.output_amount,
            price_impact=quote.price_impact,
            estimated_gas=quote.estimated_gas,
            gas_price_gwei=quote.gas_price_gwei,
            estimated_gas_cost_eth=quote.estimated_gas_cost_eth,
            exchange_rate=quote.exchange_rate,
            expires_at=quote.expires_at
        )
        
    except DEXError as e:
        logger.error(f"❌ Quote generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected quote error: {e}")
        raise HTTPException(status_code=500, detail="Quote generation failed")


@router.post("/trade/execute")
async def execute_trade(
    opportunity_id: str = Field(..., description="Opportunity ID to execute"),
    session_id: str = Field(..., description="Trading session ID"),
    override_amount: Optional[Decimal] = Field(None, description="Override recommended amount"),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """
    Execute trade based on opportunity.
    
    Executes actual blockchain transaction for detected opportunity
    using the specified trading session configuration.
    """
    try:
        logger.info(f"⚡ Executing trade: {opportunity_id}")
        
        transaction = await trading_engine.execute_live_trade(
            opportunity_id=opportunity_id,
            session_id=session_id,
            override_amount=override_amount
        )
        
        return {
            "transaction_hash": transaction.transaction_hash,
            "quote_id": transaction.quote_id,
            "status": transaction.status,
            "input_amount": str(transaction.input_amount),
            "estimated_output": str(transaction.output_amount) if transaction.output_amount else None,
            "created_at": transaction.created_at.isoformat()
        }
        
    except TradingError as e:
        logger.error(f"❌ Trade execution failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected execution error: {e}")
        raise HTTPException(status_code=500, detail="Trade execution failed")


@router.post("/trade/manual")
async def execute_manual_trade(
    request: ManualTradeRequest,
    session_id: str = Field(..., description="Trading session ID"),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine),
    dex_integration: LiveDEXIntegration = Depends(get_dex_integration)
) -> Dict[str, Any]:
    """
    Execute manual trade.
    
    Allows manual execution of trades outside of detected opportunities
    with full control over parameters and execution.
    """
    try:
        logger.info(f"🔧 Executing manual trade: {request.input_amount} {request.input_token[:10]}...")
        
        # Get quote first
        quote = await dex_integration.get_swap_quote(
            input_token=request.input_token,
            output_token=request.output_token,
            input_amount=request.input_amount,
            network=request.network,
            dex_protocol=request.dex_protocol,
            slippage_percent=request.slippage_percent
        )
        
        # Get session to get wallet connection
        sessions = trading_engine.get_active_sessions()
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Execute swap
        transaction = await dex_integration.execute_swap_transaction(
            quote_id=quote.quote_id,
            wallet_connection_id=session.wallet_connection_id,
            max_gas_price_gwei=request.max_gas_price_gwei
        )
        
        return {
            "transaction_hash": transaction.transaction_hash,
            "quote_id": quote.quote_id,
            "status": transaction.status,
            "input_amount": str(request.input_amount),
            "estimated_output": str(quote.output_amount),
            "price_impact": str(quote.price_impact),
            "estimated_gas_cost": str(quote.estimated_gas_cost_eth),
            "created_at": transaction.created_at.isoformat()
        }
        
    except DEXError as e:
        logger.error(f"❌ Manual trade failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected manual trade error: {e}")
        raise HTTPException(status_code=500, detail="Manual trade failed")


# ==================== SYSTEM STATUS ENDPOINTS ====================

@router.get("/system/status")
async def get_system_status(
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine),
    wallet_manager: WalletConnectionManager = Depends(get_wallet_manager),
    dex_integration: LiveDEXIntegration = Depends(get_dex_integration)
) -> Dict[str, Any]:
    """
    Get live trading system status.
    
    Returns comprehensive status information about all trading system components
    including connections, sessions, and performance metrics.
    """
    try:
        # Get system statistics
        system_stats = trading_engine.get_system_statistics()
        
        # Get wallet connections
        active_connections = wallet_manager.get_active_connections()
        
        # Get active quotes
        active_quotes = dex_integration.get_active_quotes()
        
        return {
            "system": {
                "is_initialized": system_stats["is_initialized"],
                "uptime_hours": system_stats["system_uptime_hours"],
                "monitoring_tasks": system_stats["monitoring_tasks"]
            },
            "trading": {
                "total_opportunities_detected": system_stats["total_opportunities_detected"],
                "total_trades_executed": system_stats["total_trades_executed"],
                "active_sessions": system_stats["active_sessions"],
                "active_opportunities": system_stats["active_opportunities"]
            },
            "wallet": {
                "active_connections": len(active_connections),
                "connected_addresses": [
                    conn.wallet_address for conn in active_connections.values()
                ]
            },
            "dex": {
                "active_quotes": len(active_quotes),
                "pending_transactions": system_stats["pending_transactions"]
            },
            "timestamp": datetime.utcnow().isoformat(),
            "version": "4B-Live-Trading"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")


@router.post("/system/initialize")
async def initialize_system(
    networks: List[NetworkType] = Field(
        default=[NetworkType.ETHEREUM], 
        description="Networks to initialize"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """
    Initialize live trading system.
    
    Initializes wallet connections, DEX integration, and starts monitoring
    for the specified networks.
    """
    try:
        logger.info(f"🚀 Initializing system for networks: {[n.value for n in networks]}")
        
        # Initialize in background
        success = await trading_engine.initialize_live_systems(networks)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="System initialization failed"
            )
        
        # Start monitoring in background
        background_tasks.add_task(
            trading_engine.monitor_market_opportunities,
            networks=networks
        )
        
        return {
            "message": "Live trading system initialized successfully",
            "initialized_networks": [n.value for n in networks],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        raise HTTPException(status_code=500, detail="System initialization failed")


# ==================== PRICE AND MARKET DATA ENDPOINTS ====================

@router.get("/market/price/{token_address}")
async def get_token_price(
    token_address: str,
    network: NetworkType = Query(..., description="Network"),
    base_token: Optional[str] = Query(None, description="Base token address"),
    dex_protocol: Optional[DEXProtocol] = Query(None, description="Specific DEX"),
    dex_integration: LiveDEXIntegration = Depends(get_dex_integration)
) -> Dict[str, Any]:
    """
    Get live token price from DEX.
    
    Returns current token price with timestamp from specified DEX or best available.
    """
    try:
        price, timestamp = await dex_integration.get_live_price(
            token_address=token_address,
            network=network,
            base_token=base_token,
            dex_protocol=dex_protocol
        )
        
        return {
            "token_address": token_address,
            "network": network.value,
            "price": str(price),
            "base_token": base_token or "native",
            "dex_protocol": dex_protocol.value if dex_protocol else "best_available",
            "timestamp": timestamp.isoformat(),
            "cache_age_seconds": (datetime.utcnow() - timestamp).total_seconds()
        }
        
    except DEXError as e:
        logger.error(f"❌ Price retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected price error: {e}")
        raise HTTPException(status_code=500, detail="Price retrieval failed")


@router.get("/market/liquidity/{token_address}")
async def get_token_liquidity(
    token_address: str,
    network: NetworkType = Query(..., description="Network"),
    dex_protocol: Optional[DEXProtocol] = Query(None, description="Specific DEX")
) -> Dict[str, Any]:
    """
    Get token liquidity information.
    
    Returns liquidity data across available DEXes for the specified token.
    """
    try:
        # This would implement actual liquidity fetching
        # For now, return simulated data
        
        return {
            "token_address": token_address,
            "network": network.value,
            "total_liquidity_usd": "125000.50",
            "pools": [
                {
                    "dex_protocol": "uniswap_v2",
                    "pool_address": "0x123...",
                    "liquidity_usd": "75000.30",
                    "volume_24h_usd": "25000.00"
                },
                {
                    "dex_protocol": "sushiswap",
                    "pool_address": "0x456...",
                    "liquidity_usd": "50000.20",
                    "volume_24h_usd": "15000.00"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Liquidity data error: {e}")
        raise HTTPException(status_code=500, detail="Liquidity data retrieval failed")


# ==================== PORTFOLIO AND PERFORMANCE ENDPOINTS ====================

@router.get("/portfolio/{wallet_connection_id}")
async def get_portfolio_summary(
    wallet_connection_id: str,
    wallet_manager: WalletConnectionManager = Depends(get_wallet_manager)
) -> Dict[str, Any]:
    """
    Get portfolio summary for connected wallet.
    
    Returns balance information and portfolio value across all connected networks.
    """
    try:
        connections = wallet_manager.get_active_connections()
        
        if wallet_connection_id not in connections:
            raise HTTPException(
                status_code=404,
                detail="Wallet connection not found"
            )
        
        connection = connections[wallet_connection_id]
        
        # Calculate total portfolio value
        total_value_usd = Decimal("0")
        network_balances = {}
        
        for network, balance in connection.balances.items():
            network_balances[network.value] = {
                "native_balance": str(balance.native_balance),
                "native_symbol": balance.native_symbol,
                "usd_value": str(balance.usd_value) if balance.usd_value else "0",
                "last_updated": balance.last_updated.isoformat()
            }
            
            if balance.usd_value:
                total_value_usd += balance.usd_value
        
        return {
            "wallet_address": connection.wallet_address,
            "connection_id": wallet_connection_id,
            "total_value_usd": str(total_value_usd),
            "network_balances": network_balances,
            "connected_networks": len(connection.connected_networks),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Portfolio summary error: {e}")
        raise HTTPException(status_code=500, detail="Portfolio summary failed")


@router.get("/performance/{session_id}")
async def get_session_performance(
    session_id: str,
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """
    Get detailed performance metrics for trading session.
    
    Returns comprehensive performance analysis including P&L, success rates,
    and trade history for the specified session.
    """
    try:
        sessions = trading_engine.get_active_sessions()
        
        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Trading session not found"
            )
        
        session = sessions[session_id]
        
        # Calculate performance metrics
        session_duration = datetime.utcnow() - session.start_time
        
        return {
            "session_id": session_id,
            "start_time": session.start_time.isoformat(),
            "duration_hours": round(session_duration.total_seconds() / 3600, 2),
            "is_active": session.is_active,
            "trading_metrics": {
                "total_trades": session.total_trades,
                "successful_trades": session.successful_trades,
                "failed_trades": session.failed_trades,
                "success_rate_percent": str(session.success_rate)
            },
            "financial_metrics": {
                "total_profit_usd": str(session.total_profit_usd),
                "total_loss_usd": str(session.total_loss_usd),
                "net_profit_usd": str(session.net_profit_usd),
                "largest_profit_usd": str(session.largest_profit_usd),
                "largest_loss_usd": str(session.largest_loss_usd),
                "total_gas_spent_eth": str(session.total_gas_spent_eth)
            },
            "daily_limits": {
                "daily_loss_usd": str(session.daily_loss_usd),
                "daily_loss_limit_usd": str(session.configuration.max_daily_loss_usd),
                "can_trade_today": session.can_trade_today,
                "daily_trades": session.daily_trades
            },
            "configuration": {
                "trading_mode": session.configuration.trading_mode.value,
                "max_position_size_usd": str(session.configuration.max_position_size_usd),
                "enabled_strategies": [s.value for s in session.configuration.enabled_strategies]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail="Performance metrics failed")


# ==================== TRANSACTION MONITORING ENDPOINTS ====================

@router.get("/transactions/{transaction_hash}")
async def get_transaction_status(
    transaction_hash: str,
    dex_integration: LiveDEXIntegration = Depends(get_dex_integration)
) -> Dict[str, Any]:
    """
    Get transaction status and details.
    
    Returns current status of blockchain transaction including confirmation
    status, gas usage, and execution results.
    """
    try:
        transaction = dex_integration.get_transaction_status(transaction_hash)
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )
        
        return {
            "transaction_hash": transaction.transaction_hash,
            "quote_id": transaction.quote_id,
            "status": transaction.status,
            "input_amount": str(transaction.input_amount),
            "output_amount": str(transaction.output_amount) if transaction.output_amount else None,
            "gas_used": transaction.actual_gas_used,
            "gas_price_gwei": str(transaction.actual_gas_price) if transaction.actual_gas_price else None,
            "gas_cost_eth": str(transaction.actual_gas_cost) if transaction.actual_gas_cost else None,
            "block_number": transaction.block_number,
            "confirmation_time": transaction.confirmation_time.isoformat() if transaction.confirmation_time else None,
            "created_at": transaction.created_at.isoformat(),
            "error_message": transaction.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Transaction status error: {e}")
        raise HTTPException(status_code=500, detail="Transaction status failed")


@router.get("/transactions/session/{session_id}")
async def get_session_transactions(
    session_id: str,
    limit: Optional[int] = Query(50, description="Maximum transactions to return"),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine),
    dex_integration: LiveDEXIntegration = Depends(get_dex_integration)
) -> List[Dict[str, Any]]:
    """
    Get transaction history for trading session.
    
    Returns chronological list of all transactions executed within
    the specified trading session.
    """
    try:
        sessions = trading_engine.get_active_sessions()
        
        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Trading session not found"
            )
        
        # Get all transactions (in production, would filter by session)
        all_transactions = dex_integration.pending_transactions
        
        # Format response (simplified for demonstration)
        transactions = []
        count = 0
        
        for tx_hash, transaction in all_transactions.items():
            if limit and count >= limit:
                break
            
            transactions.append({
                "transaction_hash": transaction.transaction_hash,
                "status": transaction.status,
                "input_amount": str(transaction.input_amount),
                "output_amount": str(transaction.output_amount) if transaction.output_amount else None,
                "created_at": transaction.created_at.isoformat(),
                "confirmation_time": transaction.confirmation_time.isoformat() if transaction.confirmation_time else None
            })
            count += 1
        
        # Sort by creation time (newest first)
        transactions.sort(key=lambda x: x["created_at"], reverse=True)
        
        return transactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session transactions error: {e}")
        raise HTTPException(status_code=500, detail="Session transactions failed")


# ==================== RISK MANAGEMENT ENDPOINTS ====================

@router.get("/risk/assessment/{opportunity_id}")
async def get_risk_assessment(
    opportunity_id: str,
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """
    Get detailed risk assessment for opportunity.
    
    Returns comprehensive risk analysis including market conditions,
    liquidity risks, and recommended position sizing.
    """
    try:
        opportunities = trading_engine.get_detected_opportunities()
        
        if opportunity_id not in opportunities:
            raise HTTPException(
                status_code=404,
                detail="Opportunity not found"
            )
        
        opportunity = opportunities[opportunity_id]
        
        # Calculate risk metrics
        risk_factors = []
        
        if opportunity.liquidity_usd < 50000:
            risk_factors.append("Low liquidity pool")
        
        if opportunity.expected_profit_percent > 10:
            risk_factors.append("High profit expectation may indicate high risk")
        
        if opportunity.time_sensitivity == "immediate":
            risk_factors.append("Time-sensitive opportunity requires quick execution")
        
        return {
            "opportunity_id": opportunity_id,
            "risk_level": opportunity.risk_level.value,
            "confidence_score": str(opportunity.confidence_score),
            "risk_adjusted_score": str(opportunity.risk_adjusted_score),
            "risk_factors": risk_factors,
            "market_conditions": {
                "liquidity_usd": str(opportunity.liquidity_usd),
                "volume_24h_usd": str(opportunity.volume_24h_usd) if opportunity.volume_24h_usd else None,
                "price_stability": "stable"  # Would calculate actual stability
            },
            "recommendations": {
                "max_position_size": str(opportunity.recommended_amount),
                "suggested_slippage": "1.5%",
                "execution_timing": opportunity.time_sensitivity,
                "stop_loss_percent": "5%"
            },
            "expires_at": opportunity.expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Risk assessment error: {e}")
        raise HTTPException(status_code=500, detail="Risk assessment failed")


@router.post("/risk/limits/{session_id}")
async def update_risk_limits(
    session_id: str,
    max_daily_loss_usd: Optional[Decimal] = Field(None, description="Maximum daily loss"),
    max_single_trade_usd: Optional[Decimal] = Field(None, description="Maximum single trade size"),
    max_slippage_percent: Optional[Decimal] = Field(None, description="Maximum slippage"),
    trading_engine: LiveTradingEngineEnhanced = Depends(get_trading_engine)
) -> Dict[str, Any]:
    """
    Update risk management limits for trading session.
    
    Allows dynamic adjustment of risk parameters during active trading session
    to respond to changing market conditions.
    """
    try:
        sessions = trading_engine.get_active_sessions()
        
        if session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Trading session not found"
            )
        
        session = sessions[session_id]
        config = session.configuration
        
        # Update limits
        if max_daily_loss_usd is not None:
            config.max_daily_loss_usd = max_daily_loss_usd
        
        if max_single_trade_usd is not None:
            config.max_single_trade_usd = max_single_trade_usd
        
        if max_slippage_percent is not None:
            config.max_slippage_percent = max_slippage_percent
        
        return {
            "session_id": session_id,
            "message": "Risk limits updated successfully",
            "updated_limits": {
                "max_daily_loss_usd": str(config.max_daily_loss_usd),
                "max_single_trade_usd": str(config.max_single_trade_usd),
                "max_slippage_percent": str(config.max_slippage_percent)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Risk limits update error: {e}")
        raise HTTPException(status_code=500, detail="Risk limits update failed")


# Export router for inclusion in main application
__all__ = ["router"]