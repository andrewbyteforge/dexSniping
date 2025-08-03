"""
WebSocket Router
File: app/api/v1/endpoints/websocket.py

WebSocket endpoints for real-time updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Connected to DEX Sniper Pro alerts",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # Send periodic updates
        while True:
            # Send sample alert every 30 seconds
            alert = {
                "type": "alert",
                "data": {
                    "message": "New token detected: SAMPLE",
                    "token_address": "0x" + "a" * 40,
                    "network": "ethereum",
                    "price": 0.000123,
                    "liquidity": 50000,
                    "risk_score": 2.5,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await manager.send_personal_message(json.dumps(alert), websocket)
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send price updates every 5 seconds
            price_update = {
                "type": "price_update",
                "data": {
                    "symbol": "ETH/USD",
                    "price": 1800 + (hash(str(datetime.now())) % 200),
                    "change_24h": -2.5 + (hash(str(datetime.now())) % 10),
                    "volume_24h": 1500000000,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await manager.send_personal_message(json.dumps(price_update), websocket)
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
