"""
WebSocket Manager - Phase 5B
File: app/utils/websocket_manager.py

WebSocket management for real-time updates.
"""

from typing import List, Dict, Any
import json
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class WebSocketManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: List = []
        self.connection_count = 0
        
        logger.info("[WS] WebSocketManager initialized")
    
    async def connect(self, websocket):
        """Connect a WebSocket."""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.connection_count += 1
            logger.info(f"[WS] WebSocket connected: {self.connection_count} total")
        except Exception as e:
            logger.error(f"[ERROR] WebSocket connection failed: {e}")
    
    def disconnect(self, websocket):
        """Disconnect a WebSocket."""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connection_count -= 1
                logger.info(f"[WS] WebSocket disconnected: {self.connection_count} total")
        except Exception as e:
            logger.error(f"[ERROR] WebSocket disconnect error: {e}")
    
    async def send_personal_message(self, message: str, websocket):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"[ERROR] Failed to send WebSocket message: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSockets."""
        if self.active_connections:
            message_str = json.dumps(message)
            for connection in self.active_connections.copy():
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"[ERROR] Broadcast failed: {e}")
                    self.disconnect(connection)

# Global instance
websocket_manager = WebSocketManager()

# Export
__all__ = ['WebSocketManager', 'websocket_manager']
