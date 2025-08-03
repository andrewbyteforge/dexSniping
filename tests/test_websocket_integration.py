"""
WebSocket Integration Test Script
File: tests/test_websocket_integration.py

Comprehensive test suite for Phase 4C WebSocket integration.
Tests real-time dashboard functionality and live data streaming.
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, Any, List
from datetime import datetime
import unittest
from unittest.mock import AsyncMock, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import websockets
from fastapi.testclient import TestClient

# Import application components
try:
    from app.main import app
    from app.core.websocket.websocket_manager import websocket_manager, WebSocketManager
    from app.core.integration.live_dashboard_service import live_dashboard_service
    from app.utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure you're running from the project root directory")
    sys.exit(1)

logger = setup_logger(__name__)


class TestWebSocketIntegration(unittest.TestCase):
    """Test suite for WebSocket integration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.test_client_id = "test_client_123"
        self.websocket_url = f"ws://localhost:8000/api/v1/ws/dashboard/{self.test_client_id}"
        
    def test_websocket_manager_initialization(self):
        """Test WebSocket manager initializes correctly."""
        manager = WebSocketManager()
        
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.connections), 0)
        self.assertIn('TRADING_STATUS', manager.MESSAGE_TYPES.values())
        self.assertIn('PORTFOLIO_UPDATE', manager.MESSAGE_TYPES.values())
        
        logger.info("✅ WebSocket manager initialization test passed")
    
    def test_websocket_message_structure(self):
        """Test WebSocket message structure validation."""
        from app.core.websocket.websocket_manager import WebSocketMessage
        
        message = WebSocketMessage(
            type="test_message",
            data={"key": "value"},
            timestamp=datetime.utcnow()
        )
        
        message_dict = message.to_dict()
        
        self.assertIn('type', message_dict)
        self.assertIn('data', message_dict)
        self.assertIn('timestamp', message_dict)
        self.assertEqual(message_dict['type'], 'test_message')
        self.assertEqual(message_dict['data']['key'], 'value')
        
        logger.info("✅ WebSocket message structure test passed")
    
    def test_live_dashboard_service_initialization(self):
        """Test live dashboard service initializes correctly."""
        service = live_dashboard_service
        
        self.assertIsNotNone(service)
        self.assertIsNotNone(service.trading_metrics)
        self.assertIsNotNone(service.portfolio_metrics)
        
        logger.info("✅ Live dashboard service initialization test passed")
    
    def test_websocket_endpoints_exist(self):
        """Test that all WebSocket endpoints are properly configured."""
        # Test WebSocket status endpoint
        response = self.client.get("/api/v1/ws/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('connected_clients', data)
        self.assertIn('message_types', data)
        
        logger.info("✅ WebSocket endpoints test passed")
    
    def test_websocket_test_page(self):
        """Test WebSocket test page is accessible."""
        response = self.client.get("/api/v1/ws/test")
        self.assertEqual(response.status_code, 200)
        self.assertIn('WebSocket Test', response.text)
        self.assertIn('DEX Sniper Pro', response.text)
        
        logger.info("✅ WebSocket test page test passed")
    
    def test_broadcast_test_endpoint(self):
        """Test broadcast test endpoint functionality."""
        test_data = {
            "test_message": "Hello World",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = self.client.post(
            "/api/v1/ws/broadcast/test",
            params={"message_type": "test"},
            json=test_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('recipients', data)
        
        logger.info("✅ Broadcast test endpoint test passed")
    
    @pytest.mark.asyncio
    async def test_websocket_connection_lifecycle(self):
        """Test complete WebSocket connection lifecycle."""
        manager = WebSocketManager()
        
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        # Test connection
        await manager.connect(mock_websocket, self.test_client_id)
        self.assertIn(self.test_client_id, manager.connections)
        
        # Test disconnection
        await manager.disconnect(self.test_client_id)
        self.assertNotIn(self.test_client_id, manager.connections)
        
        logger.info("✅ WebSocket connection lifecycle test passed")
    
    @pytest.mark.asyncio
    async def test_message_broadcasting(self):
        """Test message broadcasting functionality."""
        manager = WebSocketManager()
        
        # Mock multiple WebSocket connections
        mock_ws1 = AsyncMock()
        mock_ws1.send_text = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws2.send_text = AsyncMock()
        
        # Connect multiple clients
        await manager.connect(mock_ws1, "client1")
        await manager.connect(mock_ws2, "client2")
        
        # Subscribe clients to trading updates
        await manager._handle_subscription("client1", {"subscription": "trading"})
        await manager._handle_subscription("client2", {"subscription": "trading"})
        
        # Broadcast trading status
        test_data = {"status": "running", "trades": 5}
        await manager.broadcast_trading_status(test_data)
        
        # Allow message processing
        await asyncio.sleep(0.1)
        
        logger.info("✅ Message broadcasting test passed")
    
    @pytest.mark.asyncio
    async def test_live_dashboard_service_integration(self):
        """Test live dashboard service integration with WebSocket manager."""
        service = live_dashboard_service
        
        # Test portfolio update broadcasting
        portfolio_data = {
            "total_value": 150000.00,
            "daily_change": 5000.00,
            "positions": [{"symbol": "ETH", "value": 75000.00}]
        }
        
        await service.broadcast_portfolio_update(portfolio_data)
        
        # Test trade execution broadcasting
        trade_data = {
            "symbol": "WETH/USDC",
            "status": "success",
            "profit": 125.50,
            "volume": 1000.00
        }
        
        await service.broadcast_trade_execution(trade_data)
        
        # Test token discovery broadcasting
        token_data = {
            "symbol": "NEWTOKEN",
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "risk_score": 0.25
        }
        
        await service.broadcast_token_discovery(token_data)
        
        logger.info("✅ Live dashboard service integration test passed")
    
    def test_enhanced_dashboard_health_check(self):
        """Test enhanced health check with WebSocket information."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['phase'], '4C - Live Dashboard Integration')
        self.assertIn('websocket', data)
        self.assertIn('active_connections', data['websocket'])
        self.assertIn('message_types', data['websocket'])
        
        logger.info("✅ Enhanced health check test passed")
    
    def test_live_dashboard_endpoint(self):
        """Test live dashboard endpoint with WebSocket integration."""
        response = self.client.get("/dashboard/live")
        self.assertEqual(response.status_code, 200)
        
        content = response.text
        self.assertIn('Live Dashboard', content)
        self.assertIn('WebSocket', content)
        self.assertIn('portfolio-value', content)
        self.assertIn('connection-status', content)
        
        logger.info("✅ Live dashboard endpoint test passed")


class WebSocketClientSimulator:
    """Simulates WebSocket client for integration testing."""
    
    def __init__(self, url: str):
        self.url = url
        self.websocket = None
        self.received_messages: List[Dict[str, Any]] = []
        self.is_connected = False
        
    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.url)
            self.is_connected = True
            logger.info(f"🔌 Simulator connected to {self.url}")
        except Exception as e:
            logger.error(f"❌ Simulator connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("🔌 Simulator disconnected")
    
    async def send_message(self, message: Dict[str, Any]):
        """Send message to server."""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
            logger.info(f"📤 Simulator sent: {message}")
    
    async def receive_message(self, timeout: float = 5.0):
        """Receive message from server with timeout."""
        if self.websocket:
            try:
                message_text = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=timeout
                )
                message = json.loads(message_text)
                self.received_messages.append(message)
                logger.info(f"📨 Simulator received: {message}")
                return message
            except asyncio.TimeoutError:
                logger.warning("⏰ Simulator receive timeout")
                return None
        return None
    
    async def subscribe(self, subscription_type: str):
        """Subscribe to a specific message type."""
        await self.send_message({
            "type": "subscribe",
            "data": {"subscription": subscription_type}
        })
    
    async def send_heartbeat(self):
        """Send heartbeat to server."""
        await self.send_message({
            "type": "heartbeat",
            "data": {"timestamp": datetime.utcnow().isoformat()}
        })


@pytest.mark.asyncio
async def test_end_to_end_websocket_integration():
    """End-to-end test of WebSocket integration."""
    logger.info("🧪 Starting end-to-end WebSocket integration test")
    
    # Start WebSocket manager
    await websocket_manager.start()
    
    try:
        # Create simulator client
        simulator = WebSocketClientSimulator(
            "ws://localhost:8000/api/v1/ws/dashboard/test_e2e_client"
        )
        
        # Connect to server
        await simulator.connect()
        assert simulator.is_connected
        
        # Subscribe to dashboard updates
        await simulator.subscribe("dashboard")
        
        # Wait for initial connection message
        connection_msg = await simulator.receive_message(timeout=10.0)
        assert connection_msg is not None
        assert connection_msg.get("type") == "system_health"
        
        # Subscribe to trading updates
        await simulator.subscribe("trading")
        
        # Subscribe to portfolio updates
        await simulator.subscribe("portfolio")
        
        # Test heartbeat
        await simulator.send_heartbeat()
        heartbeat_response = await simulator.receive_message(timeout=5.0)
        assert heartbeat_response is not None
        assert heartbeat_response.get("type") == "heartbeat"
        
        # Simulate portfolio update broadcast
        await live_dashboard_service.broadcast_portfolio_update({
            "total_value": 125000.00,
            "daily_change": 2500.00
        })
        
        # Wait for portfolio update
        portfolio_msg = await simulator.receive_message(timeout=5.0)
        assert portfolio_msg is not None
        assert portfolio_msg.get("type") == "portfolio_update"
        
        # Simulate trade execution
        await live_dashboard_service.broadcast_trade_execution({
            "trade": {
                "symbol": "WETH/USDC",
                "status": "success",
                "profit": 250.75
            }
        })
        
        # Wait for trade execution message
        trade_msg = await simulator.receive_message(timeout=5.0)
        assert trade_msg is not None
        assert trade_msg.get("type") == "trade_execution"
        
        # Test token discovery alert
        await live_dashboard_service.broadcast_token_discovery({
            "token": {
                "symbol": "TESTTOKEN",
                "address": "0x1234567890abcdef1234567890abcdef12345678"
            }
        })
        
        # Wait for token discovery message
        token_msg = await simulator.receive_message(timeout=5.0)
        assert token_msg is not None
        assert token_msg.get("type") == "token_discovery"
        
        # Test arbitrage alert
        await live_dashboard_service.broadcast_arbitrage_alert({
            "opportunity": {
                "profit_percentage": 3.25,
                "dex_a": "Uniswap",
                "dex_b": "SushiSwap"
            }
        })
        
        # Wait for arbitrage alert
        arb_msg = await simulator.receive_message(timeout=5.0)
        assert arb_msg is not None
        assert arb_msg.get("type") == "arbitrage_alert"
        
        # Disconnect simulator
        await simulator.disconnect()
        assert not simulator.is_connected
        
        logger.info("✅ End-to-end WebSocket integration test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ End-to-end test failed: {e}")
        raise
    
    finally:
        # Cleanup
        await websocket_manager.stop()


class TestLiveDashboardMetrics:
    """Test suite for live dashboard metrics tracking."""
    
    def test_trading_metrics_initialization(self):
        """Test trading metrics are properly initialized."""
        from app.core.integration.live_dashboard_service import TradingMetrics
        
        metrics = TradingMetrics(
            total_trades_today=0,
            successful_trades=0,
            failed_trades=0,
            total_volume=0,
            total_profit=0,
            success_rate=0.0,
            active_strategies=[]
        )
        
        assert metrics.total_trades_today == 0
        assert metrics.success_rate == 0.0
        assert len(metrics.active_strategies) == 0
        
        # Test conversion to dict
        metrics_dict = metrics.to_dict()
        assert 'total_trades_today' in metrics_dict
        assert 'success_rate' in metrics_dict
        
        logger.info("✅ Trading metrics initialization test passed")
    
    def test_portfolio_metrics_initialization(self):
        """Test portfolio metrics are properly initialized."""
        from app.core.integration.live_dashboard_service import PortfolioMetrics
        from decimal import Decimal
        
        metrics = PortfolioMetrics(
            total_value=Decimal('125000.00'),
            available_balance=Decimal('45000.00'),
            invested_amount=Decimal('80000.00'),
            unrealized_pnl=Decimal('2500.00'),
            realized_pnl=Decimal('12000.00'),
            daily_change=Decimal('1500.00'),
            daily_change_percent=1.2,
            top_positions=[]
        )
        
        assert metrics.total_value == Decimal('125000.00')
        assert metrics.daily_change_percent == 1.2
        assert len(metrics.top_positions) == 0
        
        # Test conversion to dict
        metrics_dict = metrics.to_dict()
        assert 'total_value' in metrics_dict
        assert 'daily_change_percent' in metrics_dict
        assert isinstance(metrics_dict['total_value'], float)
        
        logger.info("✅ Portfolio metrics initialization test passed")
    
    @pytest.mark.asyncio
    async def test_metrics_update_from_trade(self):
        """Test metrics update when trade is executed."""
        service = live_dashboard_service
        
        initial_trades = service.trading_metrics.total_trades_today
        initial_successful = service.trading_metrics.successful_trades
        
        # Simulate successful trade
        trade_data = {
            "status": "success",
            "volume": 1000.00,
            "profit": 125.50,
            "symbol": "WETH/USDC"
        }
        
        service._update_trading_metrics_from_trade(trade_data)
        
        assert service.trading_metrics.total_trades_today == initial_trades + 1
        assert service.trading_metrics.successful_trades == initial_successful + 1
        assert service.trading_metrics.total_profit > 0
        
        logger.info("✅ Metrics update from trade test passed")
    
    @pytest.mark.asyncio
    async def test_portfolio_metrics_update(self):
        """Test portfolio metrics update functionality."""
        service = live_dashboard_service
        
        initial_value = service.portfolio_metrics.total_value
        
        # Simulate portfolio update
        portfolio_data = {
            "total_value": 130000.00,
            "available_balance": 50000.00,
            "positions": [
                {"symbol": "WETH", "value": 40000.00, "change_24h": 2.5},
                {"symbol": "USDC", "value": 40000.00, "change_24h": 0.1}
            ]
        }
        
        service._update_portfolio_metrics_from_data(portfolio_data)
        
        assert service.portfolio_metrics.total_value == 130000.00
        assert len(service.portfolio_metrics.top_positions) == 2
        
        logger.info("✅ Portfolio metrics update test passed")


def run_performance_test():
    """Run performance test for WebSocket message handling."""
    logger.info("🚀 Starting WebSocket performance test")
    
    async def performance_test():
        # Start WebSocket manager
        await websocket_manager.start()
        
        try:
            # Create multiple simulator clients
            simulators = []
            num_clients = 10
            
            for i in range(num_clients):
                simulator = WebSocketClientSimulator(
                    f"ws://localhost:8000/api/v1/ws/dashboard/perf_client_{i}"
                )
                simulators.append(simulator)
            
            # Connect all clients
            start_time = time.time()
            await asyncio.gather(*[sim.connect() for sim in simulators])
            connection_time = time.time() - start_time
            
            logger.info(f"⏱️ Connected {num_clients} clients in {connection_time:.2f}s")
            
            # Subscribe all clients to dashboard updates
            await asyncio.gather(*[sim.subscribe("dashboard") for sim in simulators])
            
            # Broadcast multiple messages
            num_messages = 100
            start_time = time.time()
            
            for i in range(num_messages):
                await live_dashboard_service.broadcast_portfolio_update({
                    "total_value": 125000.00 + i,
                    "message_id": i
                })
                await asyncio.sleep(0.01)  # Small delay between messages
            
            broadcast_time = time.time() - start_time
            
            logger.info(f"⏱️ Broadcasted {num_messages} messages in {broadcast_time:.2f}s")
            logger.info(f"📊 Rate: {num_messages / broadcast_time:.1f} messages/second")
            
            # Disconnect all clients
            await asyncio.gather(*[sim.disconnect() for sim in simulators])
            
            logger.info("✅ Performance test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            raise
        
        finally:
            await websocket_manager.stop()
    
    # Run the async performance test
    asyncio.run(performance_test())


def run_all_tests():
    """Run all WebSocket integration tests."""
    logger.info("🧪 Starting comprehensive WebSocket integration tests")
    
    try:
        # Run unit tests
        suite = unittest.TestLoader().loadTestsFromTestCase(TestWebSocketIntegration)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            logger.error("❌ Unit tests failed")
            return False
        
        # Run async tests
        asyncio.run(test_end_to_end_websocket_integration())
        
        # Run metrics tests
        metrics_test = TestLiveDashboardMetrics()
        metrics_test.test_trading_metrics_initialization()
        metrics_test.test_portfolio_metrics_initialization()
        asyncio.run(metrics_test.test_metrics_update_from_trade())
        asyncio.run(metrics_test.test_portfolio_metrics_update())
        
        # Run performance test
        run_performance_test()
        
        logger.info("✅ All WebSocket integration tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "performance":
        run_performance_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "e2e":
        asyncio.run(test_end_to_end_websocket_integration())
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)