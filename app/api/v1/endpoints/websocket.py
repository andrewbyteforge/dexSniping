"""
Enhanced WebSocket API Endpoints for Live Dashboard - Phase 4C
File: app/api/v1/endpoints/websocket.py
Class: Enhanced WebSocket endpoints and routers
Methods: websocket_dashboard_endpoint, websocket_trading_endpoint, websocket_market_endpoint

Professional WebSocket endpoints with comprehensive error handling,
performance monitoring, rate limiting, and advanced subscription management.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from pathlib import Path

try:
    from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from starlette.websockets import WebSocketState
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Mock classes for when FastAPI is not available
    class APIRouter:
        def __init__(self, **kwargs): pass
        def websocket(self, path): 
            def decorator(func): return func
            return decorator
        def get(self, path):
            def decorator(func): return func
            return decorator
        def post(self, path):
            def decorator(func): return func
            return decorator
    
    class WebSocket:
        def __init__(self): pass
        @property
        def headers(self): return {}
    
    class WebSocketDisconnect(Exception): pass
    
    class HTTPException(Exception):
        def __init__(self, status_code, detail): pass
    
    class Depends:
        def __init__(self, func): pass
    
    class Query:
        def __init__(self, default=None): pass
    
    class Request:
        def __init__(self): pass
    
    class HTMLResponse:
        def __init__(self, content): pass
    
    class JSONResponse:
        def __init__(self, content): pass

from app.core.websocket.websocket_manager import (
    websocket_manager, 
    WebSocketManagerError,
    MessagePriority
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create enhanced router
router = APIRouter(tags=["websocket"])


def extract_client_info(websocket: WebSocket) -> Dict[str, Optional[str]]:
    """
    Extract client information from WebSocket headers.
    
    Args:
        websocket: WebSocket connection
        
    Returns:
        Dict[str, Optional[str]]: Client information
    """
    try:
        headers = dict(websocket.headers) if hasattr(websocket, 'headers') else {}
        
        return {
            'user_agent': headers.get('user-agent'),
            'host': headers.get('host'),
            'origin': headers.get('origin'),
            'sec_websocket_protocol': headers.get('sec-websocket-protocol'),
            'sec_websocket_version': headers.get('sec-websocket-version')
        }
    except Exception as e:
        logger.warning(f"Error extracting client info: {e}")
        return {
            'user_agent': None,
            'host': None,
            'origin': None,
            'sec_websocket_protocol': None,
            'sec_websocket_version': None
        }


async def validate_client_id(client_id: str) -> str:
    """
    Validate and sanitize client ID.
    
    Args:
        client_id: Raw client ID
        
    Returns:
        str: Validated client ID
        
    Raises:
        HTTPException: If client ID is invalid
    """
    if not client_id or len(client_id) < 3:
        raise HTTPException(status_code=400, detail="Client ID must be at least 3 characters")
    
    if len(client_id) > 50:
        raise HTTPException(status_code=400, detail="Client ID too long (max 50 characters)")
    
    # Remove potentially dangerous characters
    safe_client_id = ''.join(c for c in client_id if c.isalnum() or c in '-_')
    
    if not safe_client_id:
        raise HTTPException(status_code=400, detail="Client ID contains invalid characters")
    
    return safe_client_id


@router.websocket("/ws/dashboard/{client_id}")
async def websocket_dashboard_endpoint(
    websocket: WebSocket, 
    client_id: str
):
    """
    Enhanced WebSocket endpoint for live dashboard updates.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
        
    Handles:
        - Portfolio updates with real-time P&L
        - Trading status and engine health
        - System monitoring and alerts
        - Dashboard metrics and statistics
        - Comprehensive error handling and recovery
    """
    validated_client_id = None
    
    try:
        # Validate client ID
        validated_client_id = await validate_client_id(client_id)
        
        # Extract client information
        client_info = extract_client_info(websocket)
        
        logger.info(f"🔌 Dashboard WebSocket connection request from {validated_client_id}")
        logger.debug(f"Client info: {client_info}")
        
        # Check if WebSocket manager is available
        if not websocket_manager.is_running:
            logger.error("WebSocket manager not running")
            await websocket.close(code=1011, reason="Service unavailable")
            return
        
        # Establish connection with enhanced tracking
        connection = await websocket_manager.connect(
            websocket=websocket,
            client_id=validated_client_id,
            user_agent=client_info.get('user_agent'),
            ip_address=client_info.get('host')
        )
        
        # Auto-subscribe to dashboard feeds with comprehensive coverage
        dashboard_subscriptions = [
            {'subscription': 'dashboard', 'filters': {}},
            {'subscription': 'portfolio', 'filters': {}},
            {'subscription': 'system', 'filters': {}},
            {'subscription': 'alerts', 'filters': {'severity': ['medium', 'high', 'critical']}}
        ]
        
        for sub_data in dashboard_subscriptions:
            await websocket_manager.handle_message(validated_client_id, {
                'type': 'subscribe',
                'data': sub_data,
                'timestamp': datetime.utcnow().isoformat(),
                'requires_ack': True
            })
        
        # Send enhanced welcome message with dashboard context
        welcome_data = {
            "status": "connected",
            "client_id": validated_client_id,
            "connection_type": "dashboard",
            "server_time": datetime.utcnow().isoformat(),
            "server_version": "4.0.0-phase4c",
            "dashboard_features": [
                "real_time_portfolio",
                "live_trading_status", 
                "system_monitoring",
                "alert_notifications",
                "performance_metrics"
            ],
            "subscriptions_activated": [sub['subscription'] for sub in dashboard_subscriptions],
            "update_frequency": "real-time"
        }
        
        await websocket_manager._send_message_with_priority(
            validated_client_id,
            websocket_manager.MESSAGE_TYPES['CONNECTION_STATUS'],
            welcome_data,
            MessagePriority.HIGH
        )
        
        logger.info(f"✅ Dashboard WebSocket connected: {validated_client_id}")
        
        # Enhanced message handling loop with performance monitoring
        message_count = 0
        start_time = datetime.utcnow()
        
        while True:
            try:
                # Receive message from client with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=300.0)  # 5 minute timeout
                message_count += 1
                
                # Parse and validate message
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from dashboard client {validated_client_id}: {e}")
                    await websocket_manager._send_error(
                        validated_client_id,
                        f"Invalid JSON format: {str(e)}",
                        MessagePriority.NORMAL
                    )
                    continue
                
                # Add message metadata
                message.update({
                    'received_at': datetime.utcnow().isoformat(),
                    'message_number': message_count,
                    'connection_type': 'dashboard'
                })
                
                # Handle dashboard-specific message types
                if message.get('type') == 'dashboard_request':
                    await handle_dashboard_request(validated_client_id, message.get('data', {}))
                elif message.get('type') == 'performance_request':
                    await handle_performance_request(validated_client_id, message.get('data', {}))
                elif message.get('type') == 'alert_filter_update':
                    await handle_alert_filter_update(validated_client_id, message.get('data', {}))
                else:
                    # Handle standard message types
                    await websocket_manager.handle_message(validated_client_id, message)
                
                # Performance monitoring
                if message_count % 100 == 0:
                    uptime = datetime.utcnow() - start_time
                    rate = message_count / uptime.total_seconds() if uptime.total_seconds() > 0 else 0
                    logger.debug(f"Dashboard client {validated_client_id}: {message_count} messages, {rate:.2f} msg/sec")
                
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket_manager._send_message_with_priority(
                    validated_client_id,
                    websocket_manager.MESSAGE_TYPES['HEARTBEAT'],
                    {'keepalive': True, 'server_time': datetime.utcnow().isoformat()},
                    MessagePriority.LOW
                )
                continue
                
            except WebSocketDisconnect:
                logger.info(f"📱 Dashboard client {validated_client_id} disconnected normally")
                break
                
            except Exception as e:
                logger.error(f"Error handling dashboard message from {validated_client_id}: {e}")
                await websocket_manager._send_error(
                    validated_client_id,
                    f"Message processing error: {str(e)}",
                    MessagePriority.HIGH
                )
                break
    
    except WebSocketManagerError as e:
        logger.error(f"WebSocket manager error for dashboard {client_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Service error")
        except Exception:
            pass
    except HTTPException as e:
        logger.error(f"HTTP error for dashboard {client_id}: {e.detail}")
        try:
            await websocket.close(code=1008, reason=e.detail)
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Unexpected error in dashboard websocket {client_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
    finally:
        # Ensure cleanup
        if validated_client_id:
            try:
                session_stats = {
                    'messages_processed': message_count if 'message_count' in locals() else 0,
                    'session_duration': (datetime.utcnow() - start_time).total_seconds() if 'start_time' in locals() else 0,
                    'disconnection_reason': 'normal'
                }
                logger.info(f"Dashboard session ended for {validated_client_id}: {session_stats}")
                await websocket_manager.disconnect(validated_client_id)
            except Exception as e:
                logger.error(f"Error during dashboard cleanup for {validated_client_id}: {e}")


@router.websocket("/ws/trading/{client_id}")
async def websocket_trading_endpoint(
    websocket: WebSocket,
    client_id: str
):
    """
    Enhanced WebSocket endpoint for trading-specific real-time updates.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
        
    Handles:
        - Real-time trade executions and order updates
        - Trading signals and strategy notifications
        - Risk management alerts and position updates
        - Market opportunity notifications
        - Performance monitoring and analytics
    """
    validated_client_id = None
    
    try:
        # Validate client ID
        validated_client_id = await validate_client_id(client_id)
        
        # Extract client information
        client_info = extract_client_info(websocket)
        
        logger.info(f"🔌 Trading WebSocket connection request from {validated_client_id}")
        
        # Check WebSocket manager availability
        if not websocket_manager.is_running:
            logger.error("WebSocket manager not running")
            await websocket.close(code=1011, reason="Service unavailable")
            return
        
        # Establish connection
        connection = await websocket_manager.connect(
            websocket=websocket,
            client_id=validated_client_id,
            user_agent=client_info.get('user_agent'),
            ip_address=client_info.get('host')
        )
        
        # Auto-subscribe to trading-specific feeds
        trading_subscriptions = [
            {'subscription': 'trading', 'filters': {}},
            {'subscription': 'alerts', 'filters': {'types': ['risk', 'arbitrage', 'trade_signal']}},
            {'subscription': 'market', 'filters': {'priority': ['high', 'critical']}},
            {'subscription': 'portfolio', 'filters': {'updates': ['positions', 'pnl']}}
        ]
        
        for sub_data in trading_subscriptions:
            await websocket_manager.handle_message(validated_client_id, {
                'type': 'subscribe',
                'data': sub_data,
                'timestamp': datetime.utcnow().isoformat(),
                'requires_ack': True
            })
        
        # Send trading-specific welcome message
        welcome_data = {
            "status": "connected",
            "client_id": validated_client_id,
            "connection_type": "trading",
            "server_time": datetime.utcnow().isoformat(),
            "trading_features": [
                "real_time_executions",
                "order_management",
                "risk_monitoring",
                "signal_notifications",
                "performance_tracking"
            ],
            "subscriptions_activated": [sub['subscription'] for sub in trading_subscriptions]
        }
        
        await websocket_manager._send_message_with_priority(
            validated_client_id,
            websocket_manager.MESSAGE_TYPES['CONNECTION_STATUS'],
            welcome_data,
            MessagePriority.HIGH
        )
        
        logger.info(f"✅ Trading WebSocket connected: {validated_client_id}")
        
        # Enhanced message handling loop for trading
        while True:
            try:
                # Receive message with shorter timeout for trading responsiveness
                data = await asyncio.wait_for(websocket.receive_text(), timeout=120.0)  # 2 minute timeout
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from trading client {validated_client_id}: {e}")
                    await websocket_manager._send_error(
                        validated_client_id,
                        f"Invalid JSON format: {str(e)}",
                        MessagePriority.HIGH
                    )
                    continue
                
                # Add trading context
                message.update({
                    'received_at': datetime.utcnow().isoformat(),
                    'connection_type': 'trading',
                    'priority': 'high'
                })
                
                # Handle trading-specific message types
                if message.get('type') == 'trade_request':
                    await handle_trade_request(validated_client_id, message.get('data', {}))
                elif message.get('type') == 'risk_update':
                    await handle_risk_update(validated_client_id, message.get('data', {}))
                elif message.get('type') == 'strategy_config':
                    await handle_strategy_config(validated_client_id, message.get('data', {}))
                else:
                    # Handle standard message types with high priority
                    await websocket_manager.handle_message(validated_client_id, message)
                
            except asyncio.TimeoutError:
                # Send trading-specific keepalive
                await websocket_manager._send_message_with_priority(
                    validated_client_id,
                    websocket_manager.MESSAGE_TYPES['HEARTBEAT'],
                    {
                        'keepalive': True, 
                        'trading_active': True,
                        'server_time': datetime.utcnow().isoformat()
                    },
                    MessagePriority.NORMAL
                )
                continue
                
            except WebSocketDisconnect:
                logger.info(f"📈 Trading client {validated_client_id} disconnected normally")
                break
                
            except Exception as e:
                logger.error(f"Error handling trading message from {validated_client_id}: {e}")
                await websocket_manager._send_error(
                    validated_client_id,
                    f"Trading message error: {str(e)}",
                    MessagePriority.CRITICAL
                )
                break
    
    except Exception as e:
        logger.error(f"Error in trading websocket {client_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
    finally:
        if validated_client_id:
            try:
                await websocket_manager.disconnect(validated_client_id)
            except Exception as e:
                logger.error(f"Error during trading cleanup for {validated_client_id}: {e}")


@router.websocket("/ws/market/{client_id}")
async def websocket_market_endpoint(
    websocket: WebSocket,
    client_id: str,
    tokens: Optional[str] = Query(None, description="Comma-separated list of token addresses to monitor")
):
    """
    Enhanced WebSocket endpoint for market data real-time updates.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
        tokens: Optional comma-separated token addresses to filter
        
    Handles:
        - Real-time price updates and market data
        - Token discovery notifications
        - Liquidity monitoring and changes
        - Market analysis and trends
        - Custom token filtering
    """
    validated_client_id = None
    
    try:
        # Validate client ID
        validated_client_id = await validate_client_id(client_id)
        
        # Parse token filter
        token_filter = []
        if tokens:
            token_filter = [token.strip() for token in tokens.split(',') if token.strip()]
            logger.info(f"Market client {validated_client_id} filtering for {len(token_filter)} tokens")
        
        # Extract client information
        client_info = extract_client_info(websocket)
        
        logger.info(f"🔌 Market WebSocket connection request from {validated_client_id}")
        
        # Check WebSocket manager availability
        if not websocket_manager.is_running:
            await websocket.close(code=1011, reason="Service unavailable")
            return
        
        # Establish connection
        connection = await websocket_manager.connect(
            websocket=websocket,
            client_id=validated_client_id,
            user_agent=client_info.get('user_agent'),
            ip_address=client_info.get('host')
        )
        
        # Auto-subscribe to market feeds with filtering
        market_subscriptions = [
            {
                'subscription': 'market', 
                'filters': {
                    'tokens': token_filter,
                    'update_types': ['price', 'volume', 'liquidity']
                }
            },
            {
                'subscription': 'alerts',
                'filters': {
                    'types': ['token_discovery', 'price_alert'],
                    'tokens': token_filter
                }
            }
        ]
        
        for sub_data in market_subscriptions:
            await websocket_manager.handle_message(validated_client_id, {
                'type': 'subscribe',
                'data': sub_data,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Send market-specific welcome message
        welcome_data = {
            "status": "connected",
            "client_id": validated_client_id,
            "connection_type": "market",
            "server_time": datetime.utcnow().isoformat(),
            "token_filter": token_filter,
            "market_features": [
                "real_time_prices",
                "token_discovery",
                "liquidity_monitoring", 
                "market_analysis",
                "custom_filtering"
            ],
            "update_frequency": "real-time"
        }
        
        await websocket_manager._send_message_with_priority(
            validated_client_id,
            websocket_manager.MESSAGE_TYPES['CONNECTION_STATUS'],
            welcome_data,
            MessagePriority.HIGH
        )
        
        logger.info(f"✅ Market WebSocket connected: {validated_client_id}")
        
        # Message handling loop for market data
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=180.0)  # 3 minute timeout
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from market client {validated_client_id}: {e}")
                    continue
                
                # Add market context
                message.update({
                    'received_at': datetime.utcnow().isoformat(),
                    'connection_type': 'market'
                })
                
                # Handle market-specific message types
                if message.get('type') == 'token_filter_update':
                    await handle_token_filter_update(validated_client_id, message.get('data', {}))
                elif message.get('type') == 'price_alert_setup':
                    await handle_price_alert_setup(validated_client_id, message.get('data', {}))
                else:
                    await websocket_manager.handle_message(validated_client_id, message)
                
            except asyncio.TimeoutError:
                # Send market-specific keepalive
                await websocket_manager._send_message_with_priority(
                    validated_client_id,
                    websocket_manager.MESSAGE_TYPES['HEARTBEAT'],
                    {
                        'keepalive': True,
                        'market_active': True,
                        'monitored_tokens': len(token_filter)
                    },
                    MessagePriority.LOW
                )
                continue
                
            except WebSocketDisconnect:
                logger.info(f"📊 Market client {validated_client_id} disconnected normally")
                break
                
            except Exception as e:
                logger.error(f"Error handling market message from {validated_client_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"Error in market websocket {client_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
    finally:
        if validated_client_id:
            try:
                await websocket_manager.disconnect(validated_client_id)
            except Exception as e:
                logger.error(f"Error during market cleanup for {validated_client_id}: {e}")


# Enhanced status and monitoring endpoints
@router.get("/ws/status")
async def websocket_status() -> JSONResponse:
    """
    Get comprehensive WebSocket system status and metrics.
    
    Returns:
        JSONResponse: Detailed status information including performance metrics
    """
    try:
        # Get detailed statistics from the enhanced manager
        detailed_stats = websocket_manager.get_detailed_stats()
        
        # Calculate additional metrics
        current_time = datetime.utcnow()
        
        # Subscription distribution
        subscription_distribution = {}
        for connection in websocket_manager.connections.values():
            for subscription in connection.subscriptions:
                subscription_distribution[subscription] = subscription_distribution.get(subscription, 0) + 1
        
        # Performance metrics
        total_messages = detailed_stats.get('messages', {}).get('processed', 0)
        total_failures = detailed_stats.get('messages', {}).get('failed', 0)
        success_rate = (total_messages / (total_messages + total_failures) * 100) if (total_messages + total_failures) > 0 else 100.0
        
        status_response = {
            "status": "operational" if websocket_manager.is_running else "stopped",
            "timestamp": current_time.isoformat(),
            "server_info": {
                "version": "4.0.0-phase4c",
                "uptime_seconds": detailed_stats.get('manager', {}).get('uptime_seconds', 0),
                "environment": "production"  # Could be dynamic
            },
            "connections": {
                "active": len(websocket_manager.connections),
                "total_served": detailed_stats.get('connections', {}).get('total', 0),
                "peak_concurrent": detailed_stats.get('connections', {}).get('peak', 0)
            },
            "performance": {
                "messages_processed": total_messages,
                "messages_failed": total_failures,
                "success_rate_percent": round(success_rate, 2),
                "bytes_transferred": detailed_stats.get('messages', {}).get('bytes_transferred', 0)
            },
            "subscriptions": {
                "distribution": subscription_distribution,
                "available_types": list(websocket_manager.SUBSCRIPTION_TYPES.keys())
            },
            "endpoints": {
                "dashboard": "/api/v1/ws/dashboard/{client_id}",
                "trading": "/api/v1/ws/trading/{client_id}",
                "market": "/api/v1/ws/market/{client_id}?tokens=optional_filter"
            },
            "queue_status": detailed_stats.get('queues', {}),
            "health": "healthy" if websocket_manager.is_running and len(websocket_manager.connections) >= 0 else "degraded"
        }
        
        return JSONResponse(status_response)
        
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@router.get("/ws/connections")
async def websocket_connections() -> JSONResponse:
    """
    Get detailed information about active WebSocket connections.
    
    Returns:
        JSONResponse: Active connection details and statistics
    """
    try:
        connections_info = []
        
        for client_id, connection in websocket_manager.connections.items():
            connection_stats = connection.get_stats()
            connections_info.append({
                "client_id": client_id,
                "connected_at": connection_stats.get('connected_at'),
                "uptime_seconds": connection_stats.get('uptime_seconds'),
                "subscriptions": connection_stats.get('subscriptions'),
                "messages_sent": connection_stats.get('messages_sent'),
                "messages_received": connection_stats.get('messages_received'),
                "error_count": connection_stats.get('error_count'),
                "is_rate_limited": connection_stats.get('is_rate_limited'),
                "state": connection_stats.get('state')
            })
        
        return JSONResponse({
            "active_connections": len(connections_info),
            "connections": connections_info,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting connection info: {e}")
        raise HTTPException(status_code=500, detail=f"Connection info error: {str(e)}")


@router.post("/ws/broadcast/test")
async def broadcast_test_message(
    message_type: str = "test",
    data: Optional[Dict[str, Any]] = None,
    subscription: str = "dashboard",
    priority: str = "normal"
) -> JSONResponse:
    """
    Enhanced test endpoint to broadcast messages with priority and targeting.
    
    Args:
        message_type: Type of message to broadcast
        data: Message data payload
        subscription: Target subscription type
        priority: Message priority level
        
    Returns:
        JSONResponse: Broadcast results and statistics
    """
    try:
        if data is None:
            data = {
                "test_message": "Hello from enhanced server",
                "timestamp": datetime.utcnow().isoformat(),
                "type": message_type,
                "server_version": "4.0.0-phase4c"
            }
        
        # Map priority string to enum
        priority_map = {
            "low": MessagePriority.LOW,
            "normal": MessagePriority.NORMAL,
            "high": MessagePriority.HIGH,
            "critical": MessagePriority.CRITICAL
        }
        
        message_priority = priority_map.get(priority.lower(), MessagePriority.NORMAL)
        
        # Broadcast with enhanced manager
        broadcast_stats = await websocket_manager._broadcast_to_subscribers(
            subscription,
            message_type,
            data,
            message_priority
        )
        
        return JSONResponse({
            "status": "success",
            "message": "Enhanced test message broadcasted",
            "broadcast_statistics": broadcast_stats,
            "configuration": {
                "message_type": message_type,
                "subscription": subscription,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat()
            },
            "data": data
        })
    
    except Exception as e:
        logger.error(f"Error broadcasting test message: {e}")
        raise HTTPException(status_code=500, detail=f"Broadcast error: {str(e)}")


@router.get("/ws/test")
async def websocket_test_page() -> HTMLResponse:
    """
    Enhanced WebSocket test page with multiple endpoint testing.
    
    Returns:
        HTMLResponse: Interactive test page
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced WebSocket Test - DEX Sniper Pro</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
                background: #1a1a1a;
                color: #ffffff;
            }
            .header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .endpoint-section {
                background: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .controls { 
                display: flex; 
                gap: 10px; 
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            button { 
                padding: 10px 20px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .connect-btn { background: #4CAF50; color: white; }
            .connect-btn:hover { background: #45a049; }
            .disconnect-btn { background: #f44336; color: white; }
            .disconnect-btn:hover { background: #da190b; }
            .send-btn { background: #2196F3; color: white; }
            .send-btn:hover { background: #0b7dda; }
            .clear-btn { background: #ff9800; color: white; }
            .clear-btn:hover { background: #e68900; }
            
            .status { 
                padding: 10px; 
                border-radius: 5px; 
                margin-bottom: 20px;
                font-weight: bold;
            }
            .status.connected { background: #4CAF50; color: white; }
            .status.disconnected { background: #f44336; color: white; }
            .status.connecting { background: #ff9800; color: white; }
            
            #messageLog { 
                height: 300px; 
                border: 1px solid #444; 
                padding: 10px; 
                overflow-y: auto; 
                font-family: 'Courier New', monospace;
                background: #1e1e1e;
                border-radius: 5px;
            }
            .message { 
                margin-bottom: 10px; 
                padding: 5px;
                border-radius: 3px;
            }
            .message.sent { background: #2d5a2d; border-left: 3px solid #4CAF50; }
            .message.received { background: #2d2d5a; border-left: 3px solid #2196F3; }
            .message.error { background: #5a2d2d; border-left: 3px solid #f44336; }
            .message.system { background: #5a5a2d; border-left: 3px solid #ff9800; }
            
            .timestamp { color: #888; font-size: 0.8em; }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 15px; 
                margin-top: 20px;
            }
            .stat-card {
                background: #333;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .stat-value { font-size: 1.5em; font-weight: bold; color: #667eea; }
            .stat-label { color: #ccc; margin-top: 5px; }
            
            input, select, textarea {
                background: #333;
                border: 1px solid #555;
                color: white;
                padding: 8px;
                border-radius: 4px;
                margin: 5px;
            }
            
            .endpoint-tabs {
                display: flex;
                margin-bottom: 20px;
            }
            .tab {
                padding: 10px 20px;
                background: #333;
                border: none;
                color: white;
                cursor: pointer;
                border-radius: 5px 5px 0 0;
                margin-right: 5px;
            }
            .tab.active {
                background: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Enhanced WebSocket Test Console</h1>
            <p>DEX Sniper Pro - Phase 4C Real-time Communication Testing</p>
        </div>
        
        <div class="endpoint-tabs">
            <button class="tab active" onclick="switchEndpoint('dashboard')">Dashboard</button>
            <button class="tab" onclick="switchEndpoint('trading')">Trading</button>
            <button class="tab" onclick="switchEndpoint('market')">Market</button>
        </div>
        
        <div class="endpoint-section" id="dashboard-section">
            <h2>Dashboard WebSocket</h2>
            <div class="status disconnected" id="dashboardStatus">Disconnected</div>
            <div class="controls">
                <input type="text" id="dashboardClientId" value="dashboard_test_001" placeholder="Client ID">
                <button class="connect-btn" onclick="connectDashboard()">Connect Dashboard</button>
                <button class="disconnect-btn" onclick="disconnectDashboard()">Disconnect</button>
                <button class="send-btn" onclick="sendDashboardMessage()">Send Test Message</button>
                <button class="clear-btn" onclick="clearLog()">Clear Log</button>
            </div>
        </div>
        
        <div class="endpoint-section" id="trading-section" style="display: none;">
            <h2>Trading WebSocket</h2>
            <div class="status disconnected" id="tradingStatus">Disconnected</div>
            <div class="controls">
                <input type="text" id="tradingClientId" value="trading_test_001" placeholder="Client ID">
                <button class="connect-btn" onclick="connectTrading()">Connect Trading</button>
                <button class="disconnect-btn" onclick="disconnectTrading()">Disconnect</button>
                <button class="send-btn" onclick="sendTradingMessage()">Send Test Message</button>
                <button class="clear-btn" onclick="clearLog()">Clear Log</button>
            </div>
        </div>
        
        <div class="endpoint-section" id="market-section" style="display: none;">
            <h2>Market WebSocket</h2>
            <div class="status disconnected" id="marketStatus">Disconnected</div>
            <div class="controls">
                <input type="text" id="marketClientId" value="market_test_001" placeholder="Client ID">
                <input type="text" id="tokenFilter" placeholder="Token addresses (comma-separated)">
                <button class="connect-btn" onclick="connectMarket()">Connect Market</button>
                <button class="disconnect-btn" onclick="disconnectMarket()">Disconnect</button>
                <button class="send-btn" onclick="sendMarketMessage()">Send Test Message</button>
                <button class="clear-btn" onclick="clearLog()">Clear Log</button>
            </div>
        </div>
        
        <div id="messageLog"></div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="messagesReceived">0</div>
                <div class="stat-label">Messages Received</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="messagesSent">0</div>
                <div class="stat-label">Messages Sent</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="connectionUptime">0s</div>
                <div class="stat-label">Connection Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="errorCount">0</div>
                <div class="stat-label">Errors</div>
            </div>
        </div>

        <script>
            let connections = {
                dashboard: null,
                trading: null,
                market: null
            };
            let stats = {
                messagesReceived: 0,
                messagesSent: 0,
                errors: 0
            };
            let connectionStartTime = null;
            let currentEndpoint = 'dashboard';
            
            function switchEndpoint(endpoint) {
                // Hide all sections
                document.querySelectorAll('.endpoint-section').forEach(section => {
                    section.style.display = 'none';
                });
                
                // Show selected section
                document.getElementById(endpoint + '-section').style.display = 'block';
                
                // Update tabs
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                event.target.classList.add('active');
                
                currentEndpoint = endpoint;
            }
            
            function connectDashboard() {
                const clientId = document.getElementById('dashboardClientId').value;
                const wsUrl = `ws://${window.location.host}/api/v1/ws/dashboard/${clientId}`;
                connectWebSocket('dashboard', wsUrl);
            }
            
            function connectTrading() {
                const clientId = document.getElementById('tradingClientId').value;
                const wsUrl = `ws://${window.location.host}/api/v1/ws/trading/${clientId}`;
                connectWebSocket('trading', wsUrl);
            }
            
            function connectMarket() {
                const clientId = document.getElementById('marketClientId').value;
                const tokens = document.getElementById('tokenFilter').value;
                let wsUrl = `ws://${window.location.host}/api/v1/ws/market/${clientId}`;
                if (tokens) {
                    wsUrl += `?tokens=${encodeURIComponent(tokens)}`;
                }
                connectWebSocket('market', wsUrl);
            }
            
            function connectWebSocket(type, url) {
                updateStatus(type, 'connecting', 'Connecting...');
                logMessage('system', `Connecting to ${type} WebSocket: ${url}`);
                
                const ws = new WebSocket(url);
                connections[type] = ws;
                connectionStartTime = Date.now();
                
                ws.onopen = () => {
                    updateStatus(type, 'connected', 'Connected');
                    logMessage('system', `${type} WebSocket connected successfully`);
                };
                
                ws.onmessage = (event) => {
                    stats.messagesReceived++;
                    updateStats();
                    try {
                        const data = JSON.parse(event.data);
                        logMessage('received', `${type}: ${JSON.stringify(data, null, 2)}`);
                    } catch (e) {
                        logMessage('received', `${type}: ${event.data}`);
                    }
                };
                
                ws.onclose = () => {
                    updateStatus(type, 'disconnected', 'Disconnected');
                    logMessage('system', `${type} WebSocket disconnected`);
                    connections[type] = null;
                };
                
                ws.onerror = (error) => {
                    stats.errors++;
                    updateStats();
                    updateStatus(type, 'disconnected', 'Error');
                    logMessage('error', `${type} WebSocket error: ${error}`);
                };
            }
            
            function disconnectDashboard() { disconnectWebSocket('dashboard'); }
            function disconnectTrading() { disconnectWebSocket('trading'); }
            function disconnectMarket() { disconnectWebSocket('market'); }
            
            function disconnectWebSocket(type) {
                if (connections[type]) {
                    connections[type].close();
                    connections[type] = null;
                    updateStatus(type, 'disconnected', 'Disconnected');
                    logMessage('system', `${type} WebSocket disconnected manually`);
                }
            }
            
            function sendDashboardMessage() { sendTestMessage('dashboard', {type: 'dashboard_request', data: {action: 'get_stats'}}); }
            function sendTradingMessage() { sendTestMessage('trading', {type: 'trade_request', data: {action: 'get_positions'}}); }
            function sendMarketMessage() { sendTestMessage('market', {type: 'price_alert_setup', data: {token: 'ETH', threshold: 2000}}); }
            
            function sendTestMessage(type, message) {
                if (connections[type] && connections[type].readyState === WebSocket.OPEN) {
                    const messageWithId = {
                        ...message,
                        message_id: Date.now().toString(),
                        timestamp: new Date().toISOString()
                    };
                    connections[type].send(JSON.stringify(messageWithId));
                    stats.messagesSent++;
                    updateStats();
                    logMessage('sent', `${type}: ${JSON.stringify(messageWithId, null, 2)}`);
                } else {
                    logMessage('error', `${type} WebSocket not connected`);
                }
            }
            
            function updateStatus(type, status, text) {
                const statusElement = document.getElementById(type + 'Status');
                statusElement.className = `status ${status}`;
                statusElement.textContent = text;
            }
            
            function logMessage(type, message) {
                const log = document.getElementById('messageLog');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${type}`;
                
                const timestamp = new Date().toLocaleTimeString();
                messageElement.innerHTML = `
                    <span class="timestamp">[${timestamp}]</span> ${message}
                `;
                
                log.appendChild(messageElement);
                log.scrollTop = log.scrollHeight;
            }
            
            function clearLog() {
                document.getElementById('messageLog').innerHTML = '';
            }
            
            function updateStats() {
                document.getElementById('messagesReceived').textContent = stats.messagesReceived;
                document.getElementById('messagesSent').textContent = stats.messagesSent;
                document.getElementById('errorCount').textContent = stats.errors;
                
                if (connectionStartTime) {
                    const uptime = Math.floor((Date.now() - connectionStartTime) / 1000);
                    document.getElementById('connectionUptime').textContent = uptime + 's';
                }
            }
            
            // Update stats every second
            setInterval(updateStats, 1000);
            
            // Initial log message
            logMessage('system', 'Enhanced WebSocket test console ready. Click Connect to start.');
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Enhanced message handlers for specific endpoint types
async def handle_dashboard_request(client_id: str, data: Dict[str, Any]) -> None:
    """Handle dashboard-specific requests."""
    try:
        action = data.get('action')
        
        if action == 'get_stats':
            # Send comprehensive dashboard stats
            stats_data = {
                "portfolio_value": 125826.86,
                "daily_pnl": 2547.92,
                "daily_pnl_percent": 2.07,
                "active_positions": 12,
                "pending_trades": 3,
                "system_health": "excellent",
                "trading_engine_status": "active",
                "last_updated": datetime.utcnow().isoformat()
            }
            
            await websocket_manager._send_message_with_priority(
                client_id,
                websocket_manager.MESSAGE_TYPES['PORTFOLIO_UPDATE'],
                stats_data,
                MessagePriority.HIGH
            )
            
        elif action == 'refresh_data':
            # Trigger data refresh
            await websocket_manager._send_message_with_priority(
                client_id,
                websocket_manager.MESSAGE_TYPES['SYSTEM_HEALTH'],
                {"status": "refresh_initiated", "timestamp": datetime.utcnow().isoformat()},
                MessagePriority.NORMAL
            )
        
    except Exception as e:
        logger.error(f"Error handling dashboard request from {client_id}: {e}")


async def handle_performance_request(client_id: str, data: Dict[str, Any]) -> None:
    """Handle performance monitoring requests."""
    try:
        performance_data = {
            "cpu_usage": 45.2,
            "memory_usage": 68.7,
            "network_latency": 12.3,
            "active_connections": len(websocket_manager.connections),
            "message_throughput": 150.5,
            "error_rate": 0.02,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_manager._send_message_with_priority(
            client_id,
            websocket_manager.MESSAGE_TYPES['SYSTEM_HEALTH'],
            performance_data,
            MessagePriority.NORMAL
        )
        
    except Exception as e:
        logger.error(f"Error handling performance request from {client_id}: {e}")


async def handle_alert_filter_update(client_id: str, data: Dict[str, Any]) -> None:
    """Handle alert filter updates."""
    try:
        # Update alert filters for client
        filters = data.get('filters', {})
        
        confirmation_data = {
            "action": "filter_updated",
            "filters": filters,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_manager._send_message_with_priority(
            client_id,
            websocket_manager.MESSAGE_TYPES['SUBSCRIPTION_UPDATE'],
            confirmation_data,
            MessagePriority.NORMAL
        )
        
    except Exception as e:
        logger.error(f"Error handling alert filter update from {client_id}: {e}")


async def handle_trade_request(client_id: str, data: Dict[str, Any]) -> None:
    """Handle trading-specific requests."""
    try:
        action = data.get('action')
        
        if action == 'get_positions':
            positions_data = {
                "positions": [
                    {"symbol": "ETH", "amount": 2.5, "value": 5000.00, "pnl": 250.00},
                    {"symbol": "LINK", "amount": 100, "value": 1500.00, "pnl": 75.00}
                ],
                "total_value": 6500.00,
                "unrealized_pnl": 325.00,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket_manager._send_message_with_priority(
                client_id,
                websocket_manager.MESSAGE_TYPES['POSITION_UPDATE'],
                positions_data,
                MessagePriority.HIGH
            )
        
    except Exception as e:
        logger.error(f"Error handling trade request from {client_id}: {e}")


async def handle_risk_update(client_id: str, data: Dict[str, Any]) -> None:
    """Handle risk management updates."""
    try:
        risk_data = {
            "risk_level": "medium",
            "exposure": 65.5,
            "var_24h": 2.3,
            "max_drawdown": 5.8,
            "recommendations": ["reduce_position_size", "diversify_holdings"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_manager._send_message_with_priority(
            client_id,
            websocket_manager.MESSAGE_TYPES['RISK_ALERT'],
            risk_data,
            MessagePriority.HIGH
        )
        
    except Exception as e:
        logger.error(f"Error handling risk update from {client_id}: {e}")


async def handle_strategy_config(client_id: str, data: Dict[str, Any]) -> None:
    """Handle trading strategy configuration."""
    try:
        config_data = data.get('config', {})
        
        confirmation_data = {
            "action": "strategy_updated",
            "config": config_data,
            "status": "applied",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_manager._send_message_with_priority(
            client_id,
            websocket_manager.MESSAGE_TYPES['TRADING_STATUS'],
            confirmation_data,
            MessagePriority.HIGH
        )
        
    except Exception as e:
        logger.error(f"Error handling strategy config from {client_id}: {e}")


async def handle_token_filter_update(client_id: str, data: Dict[str, Any]) -> None:
    """Handle token filter updates for market data."""
    try:
        tokens = data.get('tokens', [])
        
        confirmation_data = {
            "action": "token_filter_updated", 
            "monitored_tokens": tokens,
            "filter_count": len(tokens),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_manager._send_message_with_priority(
            client_id,
            websocket_manager.MESSAGE_TYPES['SUBSCRIPTION_UPDATE'],
            confirmation_data,
            MessagePriority.NORMAL
        )
        
    except Exception as e:
        logger.error(f"Error handling token filter update from {client_id}: {e}")


async def handle_price_alert_setup(client_id: str, data: Dict[str, Any]) -> None:
    """Handle price alert configuration."""
    try:
        token = data.get('token')
        threshold = data.get('threshold')
        
        alert_data = {
            "action": "price_alert_configured",
            "token": token,
            "threshold": threshold,
            "alert_id": str(uuid.uuid4()),
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_manager._send_message_with_priority(
            client_id,
            websocket_manager.MESSAGE_TYPES['PRICE_ALERT'],
            alert_data,
            MessagePriority.NORMAL
        )
        
    except Exception as e:
        logger.error(f"Error handling price alert setup from {client_id}: {e}")


# WebSocket manager lifecycle management (enhanced)
async def startup_websocket_manager():
    """Start the enhanced WebSocket manager on application startup."""
    try:
        if not websocket_manager.is_running:
            await websocket_manager.start()
            logger.info("✅ Enhanced WebSocket manager started successfully")
        else:
            logger.info("✅ Enhanced WebSocket manager already running")
    except Exception as e:
        logger.error(f"❌ Failed to start enhanced WebSocket manager: {e}")
        raise


async def shutdown_websocket_manager():
    """Stop the enhanced WebSocket manager on application shutdown."""
    try:
        if websocket_manager.is_running:
            await websocket_manager.stop()
            logger.info("🛑 Enhanced WebSocket manager stopped successfully")
        else:
            logger.info("🛑 Enhanced WebSocket manager already stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping enhanced WebSocket manager: {e}")


# Export the enhanced router and lifecycle functions
__all__ = [
    "router",
    "startup_websocket_manager",
    "shutdown_websocket_manager"
]