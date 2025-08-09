"""
WebSocket API Endpoints for Live Dashboard
File: app/api/v1/endpoints/websocket.py

WebSocket endpoints for real-time dashboard communication.
Handles live trading data, portfolio updates, and system notifications.
"""

import asyncio
import json
import uuid
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import HTMLResponse
from app.core.websocket.websocket_manager import websocket_manager, WebSocketManagerError
from app.utils.logger import setup_logger, get_performance_logger, get_performance_logger

logger = setup_logger(__name__, "api")

router = APIRouter()


@router.websocket("/ws/dashboard/{client_id}")
async def websocket_dashboard_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for live dashboard updates.
    
    Provides real-time data for:
    - Portfolio value updates
    - Trading activity
    - Token discovery alerts
    - System health monitoring
    """
    try:
        # Connect the client
        await websocket_manager.connect(websocket, client_id)
        
        # Automatically subscribe to dashboard updates
        await websocket_manager.handle_message(client_id, {
            'type': 'subscribe',
            'data': {'subscription': 'dashboard'}
        })
        
        logger.info(f"[STATS] Dashboard WebSocket connected: {client_id}")
        
        # Listen for messages from client
        while True:
            try:
                # Receive message from client
                message_text = await websocket.receive_text()
                message = json.loads(message_text)
                
                # Handle the message
                await websocket_manager.handle_message(client_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"[STATS] Dashboard WebSocket disconnected: {client_id}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from {client_id}: {e}")
                await websocket_manager.handle_message(client_id, {
                    'type': 'error',
                    'data': {'error': 'Invalid JSON format'}
                })
            except Exception as e:
                logger.error(f"Error in dashboard WebSocket {client_id}: {e}")
                break
    
    except WebSocketManagerError as e:
        logger.error(f"WebSocket manager error for {client_id}: {e}")
        try:
            await websocket.close(code=1003, reason=str(e))
        except Exception:
            pass
    
    except Exception as e:
        logger.error(f"Unexpected error in dashboard WebSocket {client_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass
    
    finally:
        # Ensure cleanup
        await websocket_manager.disconnect(client_id)


@router.websocket("/ws/trading/{client_id}")
async def websocket_trading_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for live trading updates.
    
    Provides real-time data for:
    - Trade executions
    - Strategy status
    - Risk management alerts
    - Order book updates
    """
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Subscribe to trading updates
        await websocket_manager.handle_message(client_id, {
            'type': 'subscribe',
            'data': {'subscription': 'trading'}
        })
        
        logger.info(f"[REFRESH] Trading WebSocket connected: {client_id}")
        
        while True:
            try:
                message_text = await websocket.receive_text()
                message = json.loads(message_text)
                await websocket_manager.handle_message(client_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"[REFRESH] Trading WebSocket disconnected: {client_id}")
                break
            except Exception as e:
                logger.error(f"Error in trading WebSocket {client_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"Trading WebSocket error for {client_id}: {e}")
    
    finally:
        await websocket_manager.disconnect(client_id)


@router.websocket("/ws/alerts/{client_id}")
async def websocket_alerts_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for live alert notifications.
    
    Provides real-time alerts for:
    - Arbitrage opportunities
    - Token discoveries
    - Risk warnings
    - System notifications
    """
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Subscribe to alerts
        await websocket_manager.handle_message(client_id, {
            'type': 'subscribe',
            'data': {'subscription': 'alerts'}
        })
        
        logger.info(f"[EMOJI] Alerts WebSocket connected: {client_id}")
        
        while True:
            try:
                message_text = await websocket.receive_text()
                message = json.loads(message_text)
                await websocket_manager.handle_message(client_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"[EMOJI] Alerts WebSocket disconnected: {client_id}")
                break
            except Exception as e:
                logger.error(f"Error in alerts WebSocket {client_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"Alerts WebSocket error for {client_id}: {e}")
    
    finally:
        await websocket_manager.disconnect(client_id)


@router.websocket("/ws/portfolio/{client_id}")
async def websocket_portfolio_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for live portfolio updates.
    
    Provides real-time data for:
    - Portfolio value changes
    - Position updates
    - P&L tracking
    - Performance metrics
    """
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Subscribe to portfolio updates
        await websocket_manager.handle_message(client_id, {
            'type': 'subscribe',
            'data': {'subscription': 'portfolio'}
        })
        
        logger.info(f"[PROFIT] Portfolio WebSocket connected: {client_id}")
        
        while True:
            try:
                message_text = await websocket.receive_text()
                message = json.loads(message_text)
                await websocket_manager.handle_message(client_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"[PROFIT] Portfolio WebSocket disconnected: {client_id}")
                break
            except Exception as e:
                logger.error(f"Error in portfolio WebSocket {client_id}: {e}")
                break
    
    except Exception as e:
        logger.error(f"Portfolio WebSocket error for {client_id}: {e}")
    
    finally:
        await websocket_manager.disconnect(client_id)


@router.get("/ws/test")
async def websocket_test_page():
    """
    Test page for WebSocket functionality.
    Provides a simple HTML interface to test WebSocket connections.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test - DEX Sniper Pro</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                font-weight: bold;
            }
            .connected { background-color: #d4edda; color: #155724; }
            .disconnected { background-color: #f8d7da; color: #721c24; }
            .message {
                background-color: #f8f9fa;
                padding: 10px;
                margin: 5px 0;
                border-left: 4px solid #007bff;
                font-family: monospace;
                font-size: 14px;
            }
            button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            button:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            button:hover:not(:disabled) {
                background-color: #0056b3;
            }
            .controls {
                margin: 20px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            .messages {
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>[BOT] DEX Sniper Pro - WebSocket Test</h1>
            <p>Test real-time WebSocket connections for live dashboard updates.</p>
            
            <div class="controls">
                <h3>Connection Controls</h3>
                <button id="connectBtn" onclick="connect()">Connect Dashboard</button>
                <button id="disconnectBtn" onclick="disconnect()" disabled>Disconnect</button>
                <button onclick="subscribeDashboard()">Subscribe Dashboard</button>
                <button onclick="subscribeTrading()">Subscribe Trading</button>
                <button onclick="subscribeAlerts()">Subscribe Alerts</button>
                <button onclick="clearMessages()">Clear Messages</button>
            </div>
            
            <div id="status" class="status disconnected">Disconnected</div>
            
            <div class="controls">
                <h3>Test Actions</h3>
                <button onclick="sendHeartbeat()">Send Heartbeat</button>
                <button onclick="requestDashboardData()">Request Dashboard Data</button>
                <button onclick="simulateTradeUpdate()">Simulate Trade Update</button>
                <button onclick="simulateAlert()">Simulate Alert</button>
            </div>
            
            <h3>Messages</h3>
            <div id="messages" class="messages"></div>
        </div>

        <script>
            let ws = null;
            let clientId = null;
            
            function generateClientId() {
                return 'test_' + Math.random().toString(36).substr(2, 9);
            }
            
            function connect() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    addMessage('Already connected');
                    return;
                }
                
                clientId = generateClientId();
                const wsUrl = `ws://localhost:8000/api/v1/ws/dashboard/${clientId}`;
                
                addMessage(`Connecting to: ${wsUrl}`);
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus(true);
                    addMessage('[OK] Connected to WebSocket');
                    document.getElementById('connectBtn').disabled = true;
                    document.getElementById('disconnectBtn').disabled = false;
                };
                
                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        addMessage(`[EMOJI] Received: ${JSON.stringify(data, null, 2)}`);
                    } catch (e) {
                        addMessage(`[EMOJI] Received (raw): ${event.data}`);
                    }
                };
                
                ws.onclose = function(event) {
                    updateStatus(false);
                    addMessage(`[WS] Connection closed: ${event.code} - ${event.reason}`);
                    document.getElementById('connectBtn').disabled = false;
                    document.getElementById('disconnectBtn').disabled = true;
                };
                
                ws.onerror = function(error) {
                    addMessage(`[ERROR] WebSocket error: ${error}`);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function updateStatus(connected) {
                const statusEl = document.getElementById('status');
                if (connected) {
                    statusEl.textContent = `Connected (Client ID: ${clientId})`;
                    statusEl.className = 'status connected';
                } else {
                    statusEl.textContent = 'Disconnected';
                    statusEl.className = 'status disconnected';
                }
            }
            
            function addMessage(text) {
                const messagesEl = document.getElementById('messages');
                const messageEl = document.createElement('div');
                messageEl.className = 'message';
                messageEl.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
                messagesEl.appendChild(messageEl);
                messagesEl.scrollTop = messagesEl.scrollHeight;
            }
            
            function sendMessage(message) {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify(message));
                    addMessage(`[EMOJI] Sent: ${JSON.stringify(message)}`);
                } else {
                    addMessage('[ERROR] WebSocket not connected');
                }
            }
            
            function subscribeDashboard() {
                sendMessage({
                    type: 'subscribe',
                    data: { subscription: 'dashboard' }
                });
            }
            
            function subscribeTrading() {
                sendMessage({
                    type: 'subscribe',
                    data: { subscription: 'trading' }
                });
            }
            
            function subscribeAlerts() {
                sendMessage({
                    type: 'subscribe',
                    data: { subscription: 'alerts' }
                });
            }
            
            function sendHeartbeat() {
                sendMessage({
                    type: 'heartbeat',
                    data: { timestamp: new Date().toISOString() }
                });
            }
            
            function requestDashboardData() {
                sendMessage({
                    type: 'request',
                    data: { request_type: 'dashboard_data' }
                });
            }
            
            function simulateTradeUpdate() {
                // This would normally come from the server
                addMessage('[REFRESH] Simulating trade update from server...');
            }
            
            function simulateAlert() {
                // This would normally come from the server
                addMessage('[EMOJI] Simulating alert from server...');
            }
            
            function clearMessages() {
                document.getElementById('messages').innerHTML = '';
            }
            
            // Auto-connect on page load for testing
            window.addEventListener('load', function() {
                addMessage('[START] WebSocket test page loaded. Click Connect to start.');
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket manager status and connected clients.
    """
    try:
        return {
            "status": "operational" if websocket_manager.is_running else "stopped",
            "connected_clients": len(websocket_manager.connections),
            "active_subscriptions": {
                client_id: list(connection.subscriptions)
                for client_id, connection in websocket_manager.connections.items()
            },
            "message_types": websocket_manager.MESSAGE_TYPES,
            "uptime": websocket_manager.is_running
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        raise HTTPException(status_code=500, detail=f"Status error: {e}")


@router.post("/ws/broadcast/test")
async def broadcast_test_message(message_type: str = "test", data: Dict[str, Any] = None):
    """
    Test endpoint to broadcast messages to all connected clients.
    Useful for testing WebSocket functionality.
    """
    try:
        if data is None:
            data = {
                "test_message": "Hello from server",
                "timestamp": f"{asyncio.get_event_loop().time()}",
                "type": message_type
            }
        
        # Broadcast to dashboard subscribers
        await websocket_manager._broadcast_to_subscribers(
            'dashboard',
            message_type,
            data
        )
        
        return {
            "status": "success",
            "message": "Test message broadcasted",
            "recipients": len(websocket_manager.connections),
            "data": data
        }
    
    except Exception as e:
        logger.error(f"Error broadcasting test message: {e}")
        raise HTTPException(status_code=500, detail=f"Broadcast error: {e}")


# WebSocket manager lifecycle management
async def startup_websocket_manager():
    """Start the WebSocket manager on application startup."""
    try:
        await websocket_manager.start()
        logger.info("[OK] WebSocket manager started successfully")
    except Exception as e:
        logger.error(f"[ERROR] Failed to start WebSocket manager: {e}")


async def shutdown_websocket_manager():
    """Stop the WebSocket manager on application shutdown."""
    try:
        await websocket_manager.stop()
        logger.info("[EMOJI] WebSocket manager stopped successfully")
    except Exception as e:
        logger.error(f"[ERROR] Error stopping WebSocket manager: {e}")