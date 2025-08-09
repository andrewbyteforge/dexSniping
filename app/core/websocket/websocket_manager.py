#!/usr/bin/env python3
"""
Enhanced WebSocket Manager - Compatible with Existing Implementation
File: app/core/websocket/websocket_manager.py

Maintains backward compatibility while adding Phase 4C enhancements:
- Priority-based message queues
- Advanced connection management & stats
- Rate limiting scaffolding
- Health monitoring and cleanup tasks
"""

from __future__ import annotations

import asyncio
import json
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

try:
    from fastapi import WebSocket
    from starlette.websockets import WebSocketDisconnect, WebSocketState
    FASTAPI_AVAILABLE = True
except Exception:  # pragma: no cover - fallback for non-FastAPI contexts
    FASTAPI_AVAILABLE = False

    class WebSocket:  # type: ignore
        def __init__(self) -> None:
            pass

        async def accept(self) -> None:
            return

        async def send_text(self, _: str) -> None:
            return

        async def close(self) -> None:
            return

        @property
        def client_state(self) -> str:
            return "connected"

    class WebSocketDisconnect(Exception):  # type: ignore
        pass

    class WebSocketState:  # type: ignore
        CONNECTED = "connected"


from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException

logger = setup_logger(__name__)


class WebSocketManagerError(DexSnipingException):
    """Exception raised when WebSocket operations fail."""
    pass


class MessagePriority(Enum):
    """Message priority levels for enhanced queue management."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class WebSocketMessage:
    """Enhanced WebSocket message structure."""
    type: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    client_id: Optional[str] = None
    requires_ack: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id,
            "client_id": self.client_id,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class ClientConnection:
    """Enhanced client connection tracking."""
    websocket: WebSocket
    client_id: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    subscriptions: Set[str] = field(default_factory=set)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)

    # Enhanced fields for Phase 4C
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    message_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    error_count: int = 0
    is_rate_limited: bool = False
    rate_limit_until: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize connection tracking."""
        if self.subscriptions is None:
            self.subscriptions = set()
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.utcnow()

    def add_subscription(self, subscription: str) -> None:
        """Add subscription to this connection."""
        if len(self.subscriptions) >= 20:
            raise WebSocketManagerError("Maximum subscriptions exceeded")
        self.subscriptions.add(subscription)
        logger.debug(
            "Added subscription '%s' to client %s",
            subscription,
            self.client_id,
        )

    def remove_subscription(self, subscription: str) -> None:
        """Remove subscription from this connection."""
        self.subscriptions.discard(subscription)
        logger.debug(
            "Removed subscription '%s' from client %s",
            subscription,
            self.client_id,
        )

    def has_subscription(self, subscription: str) -> bool:
        """Check if client has specific subscription."""
        return subscription in self.subscriptions or "all" in self.subscriptions

    def update_heartbeat(self) -> None:
        """Update last heartbeat timestamp."""
        self.last_heartbeat = datetime.utcnow()

    def is_alive(self, timeout_seconds: int = 60) -> bool:
        """Check if connection is alive based on heartbeat."""
        delta = datetime.utcnow() - self.last_heartbeat
        return delta.total_seconds() < timeout_seconds

    def check_rate_limit(self, messages_per_minute: int = 60) -> bool:
        """Check if client is rate limited."""
        now = datetime.utcnow()
        # Clear expired limit
        if self.rate_limit_until and now > self.rate_limit_until:
            self.is_rate_limited = False
            self.rate_limit_until = None
        # Placeholder: you can plug real counters here
        return not self.is_rate_limited

    def record_message_sent(self, message_size: int) -> None:
        """Record outgoing message statistics."""
        self.message_count += 1
        self.bytes_sent += message_size

    def record_error(self, _: str) -> None:
        """Record connection error."""
        self.error_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        uptime = datetime.utcnow() - self.connected_at
        return {
            "client_id": self.client_id,
            "connected_at": self.connected_at.isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "subscriptions": list(self.subscriptions),
            "message_count": self.message_count,
            "bytes_sent": self.bytes_sent,
            "error_count": self.error_count,
            "is_rate_limited": self.is_rate_limited,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
        }


class WebSocketManager:
    """
    Enhanced WebSocket Manager - Compatible with existing implementation.

    Backward compatibility:
    - Keeps legacy `message_queue` and `_process_messages` loop.
    - `connect()` and `disconnect()` aliases retained.
    """

    def __init__(self) -> None:
        # Connections & handlers
        self.connections: Dict[str, ClientConnection] = {}
        self.subscription_handlers: Dict[str, Callable[[str, Dict[str, Any]], Any]] = {}

        # Legacy queue for backward compatibility
        self.message_queue: asyncio.Queue = asyncio.Queue()

        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False

        # Priority queues
        self.message_queues: Dict[MessagePriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=1000) for priority in MessagePriority
        }

        # Statistics
        self.stats: Dict[str, Any] = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            "bytes_transferred": 0,
            "average_response_time": 0.0,
            "last_reset": datetime.utcnow(),
        }

        # Configuration
        self.config: Dict[str, Any] = {
            "max_connections": 1000,
            "max_message_size": 1024 * 64,  # 64KB
            "heartbeat_interval": 30,       # seconds
            "cleanup_interval": 60,         # seconds
            "rate_limit_messages_per_minute": 60,
            "connection_timeout": 300,      # seconds
        }

        # Message types
        self.MESSAGE_TYPES: Dict[str, str] = {
            "TRADING_STATUS": "trading_status",
            "PORTFOLIO_UPDATE": "portfolio_update",
            "TOKEN_DISCOVERY": "token_discovery",
            "ARBITRAGE_ALERT": "arbitrage_alert",
            "TRADE_EXECUTION": "trade_execution",
            "SYSTEM_HEALTH": "system_health",
            "HEARTBEAT": "heartbeat",
            "ERROR": "error",
            # Enhanced
            "PRICE_UPDATE": "price_update",
            "MARKET_DATA": "market_data",
            "ORDER_UPDATE": "order_update",
            "RISK_ALERT": "risk_alert",
            "CONNECTION_STATUS": "connection_status",
            "SUBSCRIPTION_UPDATE": "subscription_update",
            "ACKNOWLEDGMENT": "acknowledgment",
        }

        # Subscription groups
        self.SUBSCRIPTION_TYPES: Dict[str, List[str]] = {
            "dashboard": ["portfolio_update", "trading_status", "system_health"],
            "trading": ["trade_execution", "order_update", "trading_status"],
            "portfolio": ["portfolio_update", "position_update", "balance_update"],
            "alerts": ["arbitrage_alert", "risk_alert", "system_alert"],
            "market": ["price_update", "market_data", "token_discovery"],
            "system": ["system_health", "network_status", "api_status"],
            "all": list(self.MESSAGE_TYPES.values()),
        }

        self._setup_subscription_handlers()
        logger.info("Enhanced WebSocket Manager initialized")

    def _setup_subscription_handlers(self) -> None:
        """Setup subscription handlers for different message types."""
        self.subscription_handlers = {
            "dashboard": self._handle_dashboard_subscription,
            "trading": self._handle_trading_subscription,
            "portfolio": self._handle_portfolio_subscription,
            "alerts": self._handle_alerts_subscription,
            "system": self._handle_system_subscription,
            "market": self._handle_market_subscription,
        }

    async def start(self) -> None:
        """Start background tasks."""
        if self.is_running:
            logger.warning("WebSocket manager already running")
            return

        try:
            self.is_running = True
            tasks = [
                asyncio.create_task(
                    self._process_priority_messages(), name="priority_processor"
                ),
                asyncio.create_task(self._process_messages(), name="legacy_processor"),
                asyncio.create_task(self._heartbeat_loop(), name="heartbeat"),
                asyncio.create_task(self._cleanup_loop(), name="cleanup"),
                asyncio.create_task(self._stats_collector(), name="stats"),
                asyncio.create_task(self._health_monitor(), name="health"),
            ]
            self.background_tasks.update(tasks)
            logger.info(
                "Enhanced WebSocket manager started with %d background tasks",
                len(tasks),
            )
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to start WebSocket manager: %s", exc)
            await self.stop()
            raise WebSocketManagerError(f"Manager startup failed: {exc}") from exc

    async def stop(self) -> None:
        """Stop the manager and cleanup resources."""
        try:
            self.is_running = False

            for task in list(self.background_tasks):
                if not task.done():
                    task.cancel()

            if self.background_tasks:
                await asyncio.gather(
                    *self.background_tasks, return_exceptions=True
                )
            self.background_tasks.clear()

            await self._close_all_connections()

            for queue in self.message_queues.values():
                while not queue.empty():
                    try:
                        queue.get_nowait()
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        break

            logger.info("WebSocket manager stopped")
        except Exception as exc:  # pragma: no cover
            logger.error("Error stopping WebSocket manager: %s", exc)

    # --- Backward compatibility aliases -------------------------------------

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        **kwargs: Any,
    ) -> ClientConnection:
        """Connect a new client with enhanced tracking."""
        try:
            if len(self.connections) >= self.config["max_connections"]:
                raise WebSocketManagerError("Maximum connections exceeded")

            await websocket.accept()

            connection = ClientConnection(
                websocket=websocket,
                client_id=client_id,
                connected_at=datetime.utcnow(),
                subscriptions=set(),
                last_heartbeat=datetime.utcnow(),
            )
            connection.user_agent = kwargs.get("user_agent")
            connection.ip_address = kwargs.get("ip_address")

            self.connections[client_id] = connection
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = len(self.connections)

            welcome = {
                "status": "connected",
                "client_id": client_id,
                "server_time": datetime.utcnow().isoformat(),
                "available_subscriptions": list(self.SUBSCRIPTION_TYPES.keys()),
                "message_types": list(self.MESSAGE_TYPES.values()),
            }
            await self._send_to_client(
                client_id, self.MESSAGE_TYPES["CONNECTION_STATUS"], welcome
            )

            logger.info(
                "WebSocket connection added: %s (%d total)",
                client_id,
                len(self.connections),
            )
            return connection
        except Exception as exc:
            logger.error("Failed to add WebSocket connection %s: %s", client_id, exc)
            raise WebSocketManagerError(
                f"Connection setup failed: {exc}"
            ) from exc

    async def add_connection(  # legacy name
        self,
        websocket: WebSocket,
        client_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> ClientConnection:
        """Legacy-compatible wrapper for connect()."""
        return await self.connect(
            websocket,
            client_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

    async def disconnect(self, client_id: str) -> None:
        """Disconnect a client (alias for remove_connection)."""
        await self.remove_connection(client_id)

    async def remove_connection(self, client_id: str) -> bool:
        """Safely remove a connection."""
        try:
            connection = self.connections.get(client_id)
            if not connection:
                logger.warning("Attempted to remove non-existent connection: %s",
                               client_id)
                return False

            try:
                if connection.websocket.client_state == WebSocketState.CONNECTED:
                    await connection.websocket.close()
            except Exception as exc:
                logger.warning("Error closing WebSocket for %s: %s", client_id, exc)

            del self.connections[client_id]
            self.stats["active_connections"] = len(self.connections)

            logger.info(
                "WebSocket connection removed: %s (%d remaining)",
                client_id,
                len(self.connections),
            )
            return True
        except Exception as exc:  # pragma: no cover
            logger.error("Error removing connection %s: %s", client_id, exc)
            return False

    # --- Message handling -----------------------------------------------------

    async def handle_message(self, client_id: str, message: Dict[str, Any]) -> None:
        """Enhanced message handling with validation and rate limiting."""
        if client_id not in self.connections:
            logger.warning("Message from unknown client: %s", client_id)
            return

        connection = self.connections[client_id]
        try:
            if not connection.check_rate_limit(
                self.config["rate_limit_messages_per_minute"]
            ):
                await self._send_error(client_id, "Rate limit exceeded")
                return

            if not isinstance(message, dict) or "type" not in message:
                await self._send_error(client_id, "Invalid message format")
                return

            msg_type = message.get("type")
            data = message.get("data", {})

            # record size (basic)
            _size = len(json.dumps(message, default=str))
            connection.record_message_sent(_size)

            if msg_type == "subscribe":
                await self._handle_subscription(client_id, data)
            elif msg_type == "unsubscribe":
                await self._handle_unsubscription(client_id, data)
            elif msg_type == "heartbeat":
                await self._handle_heartbeat(client_id)
            elif msg_type == "ping":
                await self._handle_ping(client_id, data)
            else:
                logger.warning("Unknown message type from %s: %s", client_id, msg_type)
                await self._send_error(client_id, f"Unknown message type: {msg_type}")
        except Exception as exc:
            logger.error("Error handling message from %s: %s", client_id, exc)
            connection.record_error(str(exc))
            await self._send_error(client_id, f"Message handling error: {exc}")

    # --- Broadcasting convenience methods ------------------------------------

    async def broadcast_portfolio_update(
        self,
        portfolio_data: Dict[str, Any],
        priority: Optional[MessagePriority] = None,
    ) -> Dict[str, int]:
        priority = priority or MessagePriority.HIGH
        return await self._broadcast_to_subscribers(
            "portfolio",
            self.MESSAGE_TYPES["PORTFOLIO_UPDATE"],
            portfolio_data,
            priority,
        )

    async def broadcast_trading_status(
        self,
        status_data: Dict[str, Any],
        priority: Optional[MessagePriority] = None,
    ) -> Dict[str, int]:
        priority = priority or MessagePriority.NORMAL
        return await self._broadcast_to_subscribers(
            "trading",
            self.MESSAGE_TYPES["TRADING_STATUS"],
            status_data,
            priority,
        )

    async def broadcast_trade_execution(
        self, trade_data: Dict[str, Any]
    ) -> Dict[str, int]:
        return await self._broadcast_to_subscribers(
            "trading",
            self.MESSAGE_TYPES["TRADE_EXECUTION"],
            trade_data,
            MessagePriority.CRITICAL,
        )

    async def broadcast_system_alert(
        self, alert_data: Dict[str, Any]
    ) -> Dict[str, int]:
        return await self._broadcast_to_subscribers(
            "alerts",
            self.MESSAGE_TYPES["SYSTEM_HEALTH"],
            alert_data,
            MessagePriority.CRITICAL,
        )

    # --- Internal send/broadcast ---------------------------------------------

    async def _broadcast_to_subscribers(
        self,
        subscription_type: str,
        message_type: str,
        data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> Dict[str, int]:
        """Broadcast with priority and basic stats."""
        stats = {"queued": 0, "filtered": 0, "rate_limited": 0}

        for client_id, connection in self.connections.items():
            if not connection.has_subscription(subscription_type):
                continue
            if not connection.check_rate_limit():
                stats["rate_limited"] += 1
                continue
            await self._queue_message(client_id, message_type, data, priority)
            stats["queued"] += 1

        logger.debug(
            "Broadcast '%s' to %d subscribers",
            message_type,
            stats["queued"],
        )
        return stats

    async def _queue_message(
        self,
        client_id: str,
        message_type: str,
        data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> None:
        """Queue a message with priority handling."""
        try:
            msg = WebSocketMessage(
                type=message_type,
                data=data,
                priority=priority,
                client_id=client_id,
            )
            queue = self.message_queues[priority]
            if queue.qsize() >= 1000:
                logger.warning("Message queue full for priority %s", priority.name)
                return
            await queue.put((priority.value, time.time(), msg))
        except Exception as exc:  # pragma: no cover
            logger.error("Error queuing message: %s", exc)

    async def _send_to_client(
        self, client_id: str, message_type: str, data: Dict[str, Any]
    ) -> None:
        """Backward-compatible send via legacy queue."""
        msg = WebSocketMessage(type=message_type, data=data, client_id=client_id)
        await self.message_queue.put((client_id, msg))

    async def _send_error(self, client_id: str, error_message: str) -> None:
        """Send error message to a client."""
        await self._send_to_client(
            client_id,
            self.MESSAGE_TYPES["ERROR"],
            {"error": error_message, "timestamp": datetime.utcnow().isoformat()},
        )

    # --- Background tasks -----------------------------------------------------

    async def _process_priority_messages(self) -> None:
        """Process messages by priority."""
        while self.is_running:
            try:
                for priority in MessagePriority:
                    queue = self.message_queues[priority]
                    try:
                        _, _, msg = await asyncio.wait_for(queue.get(), timeout=0.1)
                        await self._deliver_message(msg)
                        queue.task_done()
                        if priority == MessagePriority.LOW:
                            await asyncio.sleep(0.01)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as exc:
                        logger.error(
                            "Error processing %s message: %s",
                            priority.name,
                            exc,
                        )
                        self.stats["messages_failed"] += 1
                await asyncio.sleep(0.01)
            except Exception as exc:  # pragma: no cover
                logger.error("Error in priority message processor: %s", exc)
                await asyncio.sleep(1)

    async def _deliver_message(self, message: WebSocketMessage) -> None:
        """Deliver a prepared message to its client."""
        client_id = message.client_id
        if client_id is None:
            return
        connection = self.connections.get(client_id)
        if not connection:
            return
        try:
            payload = message.to_json()
            await connection.websocket.send_text(payload)
            connection.record_message_sent(len(payload))
            self.stats["messages_processed"] += 1
        except WebSocketDisconnect:
            logger.info("Client %s disconnected during delivery", client_id)
            await self.remove_connection(client_id)
        except Exception as exc:
            logger.error("Error delivering message to %s: %s", client_id, exc)
            connection.record_error(str(exc))
            self.stats["messages_failed"] += 1

    async def _process_messages(self) -> None:
        """Legacy processor for the old per-client queue."""
        while self.is_running:
            try:
                client_id, msg = await asyncio.wait_for(self.message_queue.get(),
                                                        timeout=1.0)
                connection = self.connections.get(client_id)
                if not connection:
                    continue
                try:
                    await connection.websocket.send_text(
                        json.dumps(msg.to_dict(), default=str)
                    )
                    self.stats["messages_processed"] += 1
                except WebSocketDisconnect:
                    await self.remove_connection(client_id)
                except Exception as exc:
                    logger.error("Error sending message to %s: %s", client_id, exc)
                    await self.remove_connection(client_id)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:  # pragma: no cover
                logger.error("Error in legacy message processing: %s", exc)

    async def _heartbeat_loop(self) -> None:
        """Send heartbeats and remove stale connections."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config["heartbeat_interval"])
                if not self.connections:
                    continue

                stale: List[str] = []
                for client_id, conn in self.connections.items():
                    if not conn.is_alive(self.config["connection_timeout"]):
                        stale.append(client_id)

                for client_id in stale:
                    logger.warning("Removing stale connection: %s", client_id)
                    await self.remove_connection(client_id)

                if self.connections:
                    heartbeat = {
                        "server_time": datetime.utcnow().isoformat(),
                        "active_connections": len(self.connections),
                    }
                    await self._broadcast_to_subscribers(
                        "all",
                        self.MESSAGE_TYPES["HEARTBEAT"],
                        heartbeat,
                        MessagePriority.LOW,
                    )
            except Exception as exc:  # pragma: no cover
                logger.error("Error in heartbeat loop: %s", exc)

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup and queue size logging."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config["cleanup_interval"])
                total_queued = sum(q.qsize() for q in self.message_queues.values())
                if total_queued > 0:
                    info = {
                        prio.name: q.qsize()
                        for prio, q in self.message_queues.items()
                        if q.qsize() > 0
                    }
                    logger.debug("Message queues: %s", info)
            except Exception as exc:  # pragma: no cover
                logger.error("Error in cleanup loop: %s", exc)

    async def _stats_collector(self) -> None:
        """Log basic stats periodically."""
        while self.is_running:
            try:
                await asyncio.sleep(300)
                logger.info(
                    "WS Stats - Connections: %d, Messages: %d, Failures: %d",
                    len(self.connections),
                    self.stats["messages_processed"],
                    self.stats["messages_failed"],
                )
            except Exception as exc:  # pragma: no cover
                logger.error("Error in stats collector: %s", exc)

    async def _health_monitor(self) -> None:
        """Monitor health (queue pressure, error rates)."""
        while self.is_running:
            try:
                await asyncio.sleep(60)
                warnings: List[str] = []

                for prio, queue in self.message_queues.items():
                    if queue.qsize() > 800:
                        warnings.append(
                            f"{prio.name} queue high ({queue.qsize()})"
                        )

                total = len(self.connections)
                if total > 0:
                    errors = sum(c.error_count for c in self.connections.values())
                    error_rate = errors / total
                    if error_rate > 5:
                        warnings.append(
                            f"High error rate: {error_rate:.1f} errors/conn"
                        )

                if warnings:
                    logger.warning("Health alerts: %s", "; ".join(warnings))
            except Exception as exc:  # pragma: no cover
                logger.error("Error in health monitor: %s", exc)

    async def _close_all_connections(self) -> None:
        """Close all connections safely."""
        tasks: List[asyncio.Task] = []
        for client_id in list(self.connections.keys()):
            tasks.append(asyncio.create_task(self.remove_connection(client_id)))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    # --- Subscription handlers (placeholders) --------------------------------

    async def _handle_subscription(self, client_id: str, data: Dict[str, Any]) -> None:
        subscription = data.get("subscription")
        if not subscription or subscription not in self.SUBSCRIPTION_TYPES:
            await self._send_error(client_id, f"Invalid subscription: {subscription}")
            return

        connection = self.connections.get(client_id)
        if not connection:
            return

        try:
            connection.add_subscription(subscription)
            handler = self.subscription_handlers.get(subscription)
            if handler:
                await handler(client_id, data.get("filters", {}))
            await self._send_to_client(
                client_id,
                self.MESSAGE_TYPES["SUBSCRIPTION_UPDATE"],
                {
                    "action": "subscribed",
                    "subscription": subscription,
                    "active_subscriptions": list(connection.subscriptions),
                },
            )
            logger.info("Client %s subscribed to '%s'", client_id, subscription)
        except Exception as exc:
            logger.error("Subscription error for %s: %s", client_id, exc)
            await self._send_error(client_id, f"Subscription error: {exc}")

    async def _handle_unsubscription(
        self, client_id: str, data: Dict[str, Any]
    ) -> None:
        subscription = data.get("subscription")
        connection = self.connections.get(client_id)
        if connection and subscription:
            connection.remove_subscription(subscription)
            await self._send_to_client(
                client_id,
                self.MESSAGE_TYPES["SUBSCRIPTION_UPDATE"],
                {
                    "action": "unsubscribed",
                    "subscription": subscription,
                    "active_subscriptions": list(connection.subscriptions),
                },
            )

    async def _handle_heartbeat(self, client_id: str) -> None:
        connection = self.connections.get(client_id)
        if connection:
            connection.update_heartbeat()
            await self._send_to_client(
                client_id,
                self.MESSAGE_TYPES["HEARTBEAT"],
                {"server_time": datetime.utcnow().isoformat(), "status": "healthy"},
            )

    async def _handle_ping(self, client_id: str, data: Dict[str, Any]) -> None:
        await self._send_to_client(
            client_id,
            "pong",
            {"timestamp": datetime.utcnow().isoformat(), "ping_data": data},
        )

    # Placeholders for specialized handlers
    async def _handle_dashboard_subscription(
        self, client_id: str, filters: Dict[str, Any]
    ) -> None:
        _ = (client_id, filters)

    async def _handle_trading_subscription(
        self, client_id: str, filters: Dict[str, Any]
    ) -> None:
        _ = (client_id, filters)

    async def _handle_portfolio_subscription(
        self, client_id: str, filters: Dict[str, Any]
    ) -> None:
        _ = (client_id, filters)

    async def _handle_alerts_subscription(
        self, client_id: str, filters: Dict[str, Any]
    ) -> None:
        _ = (client_id, filters)

    async def _handle_system_subscription(
        self, client_id: str, filters: Dict[str, Any]
    ) -> None:
        _ = (client_id, filters)

    async def _handle_market_subscription(
        self, client_id: str, filters: Dict[str, Any]
    ) -> None:
        _ = (client_id, filters)

    # --- Public API -----------------------------------------------------------

    def get_detailed_stats(self) -> Dict[str, Any]:
        """Return comprehensive manager and connection statistics."""
        conn_stats = [c.get_stats() for c in self.connections.values()]
        queue_stats = {
            prio.name: {"size": q.qsize(), "max_size": 1000}
            for prio, q in self.message_queues.items()
        }
        return {
            "manager": {
                "is_running": self.is_running,
                "background_tasks": len(self.background_tasks),
            },
            "connections": {
                "active": len(self.connections),
                "total": self.stats["total_connections"],
                "details": conn_stats,
            },
            "messages": {
                "processed": self.stats["messages_processed"],
                "failed": self.stats["messages_failed"],
            },
            "queues": queue_stats,
            "config": self.config,
        }


# Global instance
websocket_manager = WebSocketManager()


# Compatibility helper for lazy-start access
async def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance, starting it if needed."""
    if not websocket_manager.is_running:
        await websocket_manager.start()
    return websocket_manager


__all__ = [
    "WebSocketManager",
    "WebSocketMessage",
    "ClientConnection",
    "MessagePriority",
    "websocket_manager",
    "get_websocket_manager",
    "WebSocketManagerError",
]
