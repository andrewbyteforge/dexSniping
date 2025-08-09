"""
WebSocket Manager for Live Dashboard Integration
File: app/core/websocket/websocket_manager.py

Real-time WebSocket connections for live dashboard updates.
Provides real-time trading data, market updates, and system status.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal

from fastapi import WebSocket, WebSocketDisconnect
from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException

logger = setup_logger(__name__, "application")


class WebSocketManagerError(DexSnipingException):
    """Exception raised when WebSocket operations fail."""
    pass


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    type: str
    data: Any
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ClientConnection:
    """Client connection tracking."""
    websocket: WebSocket
    client_id: str
    connected_at: datetime
    subscriptions: Set[str]
    last_heartbeat: datetime
    
    def __post_init__(self):
        """Initialize connection tracking."""
        self.subscriptions = set()
        self.last_heartbeat = datetime.utcnow()


class WebSocketManager:
    """
    WebSocket Manager for Live Dashboard Integration.
    
    Manages real-time connections for:
    - Trading engine status updates
    - Portfolio value changes
    - Token discovery alerts
    - Arbitrage opportunity notifications
    - System health monitoring
    """
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.connections: Dict[str, ClientConnection] = {}
        self.subscription_handlers: Dict[str, Callable] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False
        
        # Message types
        self.MESSAGE_TYPES = {
            'TRADING_STATUS': 'trading_status',
            'PORTFOLIO_UPDATE': 'portfolio_update',
            'TOKEN_DISCOVERY': 'token_discovery',
            'ARBITRAGE_ALERT': 'arbitrage_alert',
            'TRADE_EXECUTION': 'trade_execution',
            'SYSTEM_HEALTH': 'system_health',
            'HEARTBEAT': 'heartbeat',
            'ERROR': 'error'
        }
        
        # Setup subscription handlers
        self._setup_subscription_handlers()
        
        logger.info("[OK] WebSocket Manager initialized")
    
    def _setup_subscription_handlers(self) -> None:
        """Setup subscription handlers for different message types."""
        self.subscription_handlers = {
            'dashboard': self._handle_dashboard_subscription,
            'trading': self._handle_trading_subscription,
            'portfolio': self._handle_portfolio_subscription,
            'alerts': self._handle_alerts_subscription,
            'system': self._handle_system_subscription
        }
    
    async def start(self) -> None:
        """Start WebSocket manager background tasks."""
        if self.is_running:
            logger.warning("WebSocket manager already running")
            return
        
        self.is_running = True
        
        # Start background tasks
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        message_processor_task = asyncio.create_task(self._process_messages())
        connection_cleaner_task = asyncio.create_task(self._clean_connections())
        
        self.background_tasks.update([
            heartbeat_task,
            message_processor_task,
            connection_cleaner_task
        ])
        
        logger.info("[START] WebSocket manager started")
    
    async def stop(self) -> None:
        """Stop WebSocket manager and cleanup."""
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close all connections
        await self._close_all_connections()
        
        logger.info("[EMOJI] WebSocket manager stopped")
    
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Connect a new WebSocket client."""
        try:
            await websocket.accept()
            
            connection = ClientConnection(
                websocket=websocket,
                client_id=client_id,
                connected_at=datetime.utcnow(),
                subscriptions=set(),
                last_heartbeat=datetime.utcnow()
            )
            
            self.connections[client_id] = connection
            
            # Send initial connection message
            await self._send_to_client(
                client_id,
                self.MESSAGE_TYPES['SYSTEM_HEALTH'],
                {
                    'status': 'connected',
                    'client_id': client_id,
                    'server_time': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"[OK] WebSocket client connected: {client_id}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to connect WebSocket client {client_id}: {e}")
            raise WebSocketManagerError(f"Connection failed: {e}")
    
    async def disconnect(self, client_id: str) -> None:
        """Disconnect a WebSocket client."""
        if client_id in self.connections:
            connection = self.connections[client_id]
            try:
                await connection.websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket for {client_id}: {e}")
            
            del self.connections[client_id]
            logger.info(f"[CONNECT] WebSocket client disconnected: {client_id}")
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming message from client."""
        try:
            message_type = message.get('type')
            data = message.get('data', {})
            
            if message_type == 'subscribe':
                await self._handle_subscription(client_id, data)
            elif message_type == 'unsubscribe':
                await self._handle_unsubscription(client_id, data)
            elif message_type == 'heartbeat':
                await self._handle_heartbeat(client_id)
            else:
                logger.warning(f"Unknown message type from {client_id}: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_error(client_id, f"Message handling error: {e}")
    
    async def broadcast_trading_status(self, status_data: Dict[str, Any]) -> None:
        """Broadcast trading engine status to all subscribed clients."""
        await self._broadcast_to_subscribers(
            'trading',
            self.MESSAGE_TYPES['TRADING_STATUS'],
            status_data
        )
    
    async def broadcast_portfolio_update(self, portfolio_data: Dict[str, Any]) -> None:
        """Broadcast portfolio updates to all subscribed clients."""
        await self._broadcast_to_subscribers(
            'portfolio',
            self.MESSAGE_TYPES['PORTFOLIO_UPDATE'],
            portfolio_data
        )
    
    async def broadcast_token_discovery(self, token_data: Dict[str, Any]) -> None:
        """Broadcast new token discovery to all subscribed clients."""
        await self._broadcast_to_subscribers(
            'alerts',
            self.MESSAGE_TYPES['TOKEN_DISCOVERY'],
            token_data
        )
    
    async def broadcast_arbitrage_alert(self, arbitrage_data: Dict[str, Any]) -> None:
        """Broadcast arbitrage opportunity alert to all subscribed clients."""
        await self._broadcast_to_subscribers(
            'alerts',
            self.MESSAGE_TYPES['ARBITRAGE_ALERT'],
            arbitrage_data
        )
    
    async def broadcast_trade_execution(self, trade_data: Dict[str, Any]) -> None:
        """Broadcast trade execution update to all subscribed clients."""
        await self._broadcast_to_subscribers(
            'trading',
            self.MESSAGE_TYPES['TRADE_EXECUTION'],
            trade_data
        )
    
    async def broadcast_system_health(self, health_data: Dict[str, Any]) -> None:
        """Broadcast system health update to all subscribed clients."""
        await self._broadcast_to_subscribers(
            'system',
            self.MESSAGE_TYPES['SYSTEM_HEALTH'],
            health_data
        )
    
    async def _handle_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle client subscription request."""
        subscription_type = data.get('subscription')
        
        if client_id not in self.connections:
            logger.warning(f"Client {client_id} not found for subscription")
            return
        
        if subscription_type in self.subscription_handlers:
            self.connections[client_id].subscriptions.add(subscription_type)
            await self.subscription_handlers[subscription_type](client_id, data)
            
            logger.info(f"[OK] Client {client_id} subscribed to {subscription_type}")
        else:
            await self._send_error(
                client_id,
                f"Unknown subscription type: {subscription_type}"
            )
    
    async def _handle_unsubscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle client unsubscription request."""
        subscription_type = data.get('subscription')
        
        if client_id in self.connections:
            self.connections[client_id].subscriptions.discard(subscription_type)
            logger.info(f"[CONNECT] Client {client_id} unsubscribed from {subscription_type}")
    
    async def _handle_heartbeat(self, client_id: str) -> None:
        """Handle heartbeat from client."""
        if client_id in self.connections:
            self.connections[client_id].last_heartbeat = datetime.utcnow()
            
            await self._send_to_client(
                client_id,
                self.MESSAGE_TYPES['HEARTBEAT'],
                {'timestamp': datetime.utcnow().isoformat()}
            )
    
    async def _handle_dashboard_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle dashboard subscription - send current dashboard data."""
        # Send initial dashboard data
        dashboard_data = await self._get_dashboard_data()
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES['PORTFOLIO_UPDATE'],
            dashboard_data
        )
    
    async def _handle_trading_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle trading subscription - send current trading status."""
        trading_data = await self._get_trading_status()
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES['TRADING_STATUS'],
            trading_data
        )
    
    async def _handle_portfolio_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle portfolio subscription - send current portfolio data."""
        portfolio_data = await self._get_portfolio_data()
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES['PORTFOLIO_UPDATE'],
            portfolio_data
        )
    
    async def _handle_alerts_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle alerts subscription - enable real-time alerts."""
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES['SYSTEM_HEALTH'],
            {'message': 'Alerts subscription activated'}
        )
    
    async def _handle_system_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        """Handle system subscription - send system health data."""
        system_data = await self._get_system_health()
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES['SYSTEM_HEALTH'],
            system_data
        )
    
    async def _broadcast_to_subscribers(
        self,
        subscription_type: str,
        message_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Broadcast message to all clients subscribed to a specific type."""
        subscribers = [
            client_id for client_id, connection in self.connections.items()
            if subscription_type in connection.subscriptions
        ]
        
        if subscribers:
            message = WebSocketMessage(
                type=message_type,
                data=data,
                timestamp=datetime.utcnow()
            )
            
            for client_id in subscribers:
                await self.message_queue.put((client_id, message))
    
    async def _send_to_client(
        self,
        client_id: str,
        message_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Send message to specific client."""
        message = WebSocketMessage(
            type=message_type,
            data=data,
            timestamp=datetime.utcnow()
        )
        
        await self.message_queue.put((client_id, message))
    
    async def _send_error(self, client_id: str, error_message: str) -> None:
        """Send error message to client."""
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES['ERROR'],
            {'error': error_message}
        )
    
    async def _process_messages(self) -> None:
        """Background task to process message queue."""
        while self.is_running:
            try:
                client_id, message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                if client_id in self.connections:
                    connection = self.connections[client_id]
                    try:
                        await connection.websocket.send_text(
                            json.dumps(message.to_dict(), default=str)
                        )
                    except WebSocketDisconnect:
                        await self.disconnect(client_id)
                    except Exception as e:
                        logger.error(f"Error sending message to {client_id}: {e}")
                        await self.disconnect(client_id)
                        
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message processing: {e}")
    
    async def _heartbeat_loop(self) -> None:
        """Background task for heartbeat monitoring."""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                timeout_threshold = current_time - timedelta(minutes=5)
                
                # Check for timed out connections
                timed_out_clients = [
                    client_id for client_id, connection in self.connections.items()
                    if connection.last_heartbeat < timeout_threshold
                ]
                
                for client_id in timed_out_clients:
                    logger.warning(f"Client {client_id} timed out, disconnecting")
                    await self.disconnect(client_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(30)
    
    async def _clean_connections(self) -> None:
        """Background task to clean up dead connections."""
        while self.is_running:
            try:
                dead_connections = []
                
                for client_id, connection in self.connections.items():
                    try:
                        # Try to ping the connection
                        await connection.websocket.ping()
                    except Exception:
                        dead_connections.append(client_id)
                
                for client_id in dead_connections:
                    await self.disconnect(client_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in connection cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _close_all_connections(self) -> None:
        """Close all WebSocket connections."""
        client_ids = list(self.connections.keys())
        for client_id in client_ids:
            await self.disconnect(client_id)
    
    async def _get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data."""
        # This would integrate with actual trading engine data
        return {
            'portfolio_value': 125826.86,
            'daily_pnl': 3241.87,
            'tokens_discovered': 47,
            'active_trades': 8,
            'arbitrage_opportunities': 12,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def _get_trading_status(self) -> Dict[str, Any]:
        """Get current trading engine status."""
        return {
            'is_running': True,
            'strategies_active': ['arbitrage', 'trend_following'],
            'last_trade': '2025-08-03T10:30:00Z',
            'trades_today': 15,
            'success_rate': 84.2
        }
    
    async def _get_portfolio_data(self) -> Dict[str, Any]:
        """Get current portfolio data."""
        return {
            'total_value': 125826.86,
            'available_balance': 45000.00,
            'positions': [
                {
                    'token': 'WETH',
                    'value': 35000.00,
                    'change_24h': 2.3
                },
                {
                    'token': 'USDC',
                    'value': 45826.86,
                    'change_24h': 0.1
                }
            ]
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health data."""
        return {
            'status': 'healthy',
            'uptime': '24h 30m',
            'memory_usage': 45.2,
            'cpu_usage': 23.8,
            'active_connections': len(self.connections)
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()