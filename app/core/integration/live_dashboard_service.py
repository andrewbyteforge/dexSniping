"""
Enhanced Live Dashboard Integration Service - Phase 4C
File: app/core/integration/live_dashboard_service.py
Class: LiveDashboardService
Methods: Enhanced real-time updates, performance monitoring, advanced analytics

Professional live dashboard service with comprehensive real-time data streaming,
intelligent change detection, performance optimization, and advanced analytics.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Union, Set, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, asdict, field
from collections import deque, defaultdict
from enum import Enum
import logging
import time
import statistics
import uuid
from contextlib import asynccontextmanager

try:
    from app.core.websocket.websocket_manager import (
        websocket_manager,
        MessagePriority,
        WebSocketManager
    )
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    class WebSocketManager:
        def __init__(self): pass
        async def broadcast_portfolio_update(self, data, priority=None): return {}
        async def broadcast_trading_status(self, data, priority=None): return {}

try:
    from app.core.trading.trading_engine import TradingEngine
    TRADING_ENGINE_AVAILABLE = True
except ImportError:
    TRADING_ENGINE_AVAILABLE = False
    class TradingEngine:
        def __init__(self): pass

try:
    from app.core.portfolio.portfolio_manager import PortfolioManager
    PORTFOLIO_AVAILABLE = True
except ImportError:
    PORTFOLIO_AVAILABLE = False
    class PortfolioManager:
        def __init__(self): pass

from app.utils.logger import setup_logger
from app.utils.exceptions import DexSnipingException

logger = setup_logger(__name__)


class LiveDashboardServiceError(DexSnipingException):
    """Exception raised when live dashboard service operations fail."""
    pass


class UpdatePriority(Enum):
    """Update priority levels for dashboard streaming."""
    CRITICAL = 1    # Immediate updates (trade executions, alerts)
    HIGH = 2        # Important updates (portfolio changes, system alerts)
    NORMAL = 3      # Regular updates (price changes, status updates)
    LOW = 4         # Background updates (metrics, housekeeping)


class DataChangeType(Enum):
    """Types of data changes for intelligent updates."""
    SIGNIFICANT = "significant"    # Major changes requiring immediate broadcast
    MODERATE = "moderate"          # Moderate changes for normal updates
    MINOR = "minor"                # Minor changes for batch updates
    NONE = "none"                  # No meaningful change


@dataclass
class LiveDashboardUpdate:
    """Enhanced structure for live dashboard update data."""
    update_type: str
    timestamp: datetime
    data: Dict[str, Any]
    priority: str = "normal"
    change_magnitude: float = 0.0
    affected_metrics: List[str] = field(default_factory=list)
    source_component: Optional[str] = None
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requires_acknowledgment: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'update_type': self.update_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'priority': self.priority,
            'change_magnitude': self.change_magnitude,
            'affected_metrics': self.affected_metrics,
            'source_component': self.source_component,
            'update_id': self.update_id,
            'requires_acknowledgment': self.requires_acknowledgment
        }


@dataclass
class EnhancedTradingMetrics:
    """Enhanced real-time trading metrics with analytics."""
    total_trades_today: int
    successful_trades: int
    failed_trades: int
    total_volume: Decimal
    total_profit: Decimal
    success_rate: float
    active_strategies: List[str]
    last_trade_time: Optional[datetime] = None
    
    # Enhanced metrics
    average_trade_size: Decimal = Decimal('0')
    largest_win: Decimal = Decimal('0')
    largest_loss: Decimal = Decimal('0')
    win_loss_ratio: float = 0.0
    trades_per_hour: float = 0.0
    profit_per_hour: Decimal = Decimal('0')
    current_streak: int = 0
    max_drawdown: Decimal = Decimal('0')
    sharpe_ratio: float = 0.0
    
    # Performance tracking
    execution_latency_ms: List[float] = field(default_factory=list)
    slippage_data: List[float] = field(default_factory=list)
    gas_costs: List[Decimal] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            # Basic metrics
            'total_trades_today': self.total_trades_today,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'total_volume': float(self.total_volume),
            'total_profit': float(self.total_profit),
            'success_rate': self.success_rate,
            'active_strategies': self.active_strategies,
            'last_trade_time': self.last_trade_time.isoformat() if self.last_trade_time else None,
            
            # Enhanced metrics
            'average_trade_size': float(self.average_trade_size),
            'largest_win': float(self.largest_win),
            'largest_loss': float(self.largest_loss),
            'win_loss_ratio': self.win_loss_ratio,
            'trades_per_hour': self.trades_per_hour,
            'profit_per_hour': float(self.profit_per_hour),
            'current_streak': self.current_streak,
            'max_drawdown': float(self.max_drawdown),
            'sharpe_ratio': self.sharpe_ratio,
            
            # Performance analytics
            'avg_execution_latency_ms': statistics.mean(self.execution_latency_ms) if self.execution_latency_ms else 0,
            'avg_slippage_percent': statistics.mean(self.slippage_data) if self.slippage_data else 0,
            'total_gas_costs': float(sum(self.gas_costs)) if self.gas_costs else 0
        }
    
    def calculate_enhanced_metrics(self, trade_history: List[Dict[str, Any]]) -> None:
        """Calculate enhanced metrics from trade history."""
        if not trade_history:
            return
        
        try:
            profits = [float(trade.get('profit', 0)) for trade in trade_history]
            sizes = [float(trade.get('size', 0)) for trade in trade_history]
            
            # Calculate win/loss metrics
            wins = [p for p in profits if p > 0]
            losses = [p for p in profits if p < 0]
            
            if wins:
                self.largest_win = Decimal(str(max(wins)))
            if losses:
                self.largest_loss = Decimal(str(min(losses)))  # Will be negative
            
            if losses and wins:
                avg_win = statistics.mean(wins)
                avg_loss = abs(statistics.mean(losses))
                self.win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
            
            # Calculate trade size metrics
            if sizes:
                self.average_trade_size = Decimal(str(statistics.mean(sizes)))
            
            # Calculate hourly metrics
            if trade_history:
                time_span_hours = max(1, len(trade_history) / 24)  # Approximate
                self.trades_per_hour = len(trade_history) / time_span_hours
                self.profit_per_hour = self.total_profit / Decimal(str(time_span_hours))
            
            # Calculate drawdown and other advanced metrics
            self._calculate_drawdown_metrics(profits)
            self._calculate_sharpe_ratio(profits)
            
        except Exception as e:
            logger.error(f"Error calculating enhanced metrics: {e}")
    
    def _calculate_drawdown_metrics(self, profits: List[float]) -> None:
        """Calculate maximum drawdown from profit series."""
        try:
            if not profits:
                return
            
            cumulative = []
            running_total = 0
            for profit in profits:
                running_total += profit
                cumulative.append(running_total)
            
            if cumulative:
                peak = cumulative[0]
                max_dd = 0
                
                for value in cumulative:
                    if value > peak:
                        peak = value
                    drawdown = peak - value
                    if drawdown > max_dd:
                        max_dd = drawdown
                
                self.max_drawdown = Decimal(str(max_dd))
                
        except Exception as e:
            logger.error(f"Error calculating drawdown: {e}")
    
    def _calculate_sharpe_ratio(self, profits: List[float], risk_free_rate: float = 0.02) -> None:
        """Calculate Sharpe ratio for trading performance."""
        try:
            if len(profits) < 2:
                return
            
            mean_return = statistics.mean(profits)
            std_dev = statistics.stdev(profits)
            
            if std_dev > 0:
                # Annualized Sharpe ratio (assuming daily profits)
                excess_return = mean_return - (risk_free_rate / 365)
                self.sharpe_ratio = (excess_return * (365 ** 0.5)) / std_dev
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")


@dataclass
class EnhancedPortfolioMetrics:
    """Enhanced real-time portfolio metrics with advanced analytics."""
    total_value: Decimal
    available_balance: Decimal
    invested_amount: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    daily_change: Decimal
    daily_change_percent: float
    top_positions: List[Dict[str, Any]]
    
    # Enhanced portfolio metrics
    total_return_percent: float = 0.0
    annualized_return: float = 0.0
    portfolio_beta: float = 0.0
    diversification_ratio: float = 0.0
    concentration_risk: float = 0.0
    volatility: float = 0.0
    var_95: Decimal = Decimal('0')  # Value at Risk 95%
    max_position_size: Decimal = Decimal('0')
    position_count: int = 0
    
    # Risk metrics
    risk_score: float = 0.0
    leverage_ratio: float = 0.0
    margin_utilization: float = 0.0
    
    # Historical tracking
    value_history: deque = field(default_factory=lambda: deque(maxlen=1440))  # 24 hours of minutes
    pnl_history: deque = field(default_factory=lambda: deque(maxlen=1440))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            # Basic metrics
            'total_value': float(self.total_value),
            'available_balance': float(self.available_balance),
            'invested_amount': float(self.invested_amount),
            'unrealized_pnl': float(self.unrealized_pnl),
            'realized_pnl': float(self.realized_pnl),
            'daily_change': float(self.daily_change),
            'daily_change_percent': self.daily_change_percent,
            'top_positions': self.top_positions,
            
            # Enhanced metrics
            'total_return_percent': self.total_return_percent,
            'annualized_return': self.annualized_return,
            'portfolio_beta': self.portfolio_beta,
            'diversification_ratio': self.diversification_ratio,
            'concentration_risk': self.concentration_risk,
            'volatility': self.volatility,
            'var_95': float(self.var_95),
            'max_position_size': float(self.max_position_size),
            'position_count': self.position_count,
            
            # Risk metrics
            'risk_score': self.risk_score,
            'leverage_ratio': self.leverage_ratio,
            'margin_utilization': self.margin_utilization,
            
            # Chart data
            'value_chart_data': list(self.value_history)[-60:],  # Last hour for charts
            'pnl_chart_data': list(self.pnl_history)[-60:]
        }
    
    def update_historical_data(self) -> None:
        """Update historical tracking data."""
        current_time = datetime.utcnow()
        
        # Add current values to history
        self.value_history.append({
            'timestamp': current_time.isoformat(),
            'value': float(self.total_value)
        })
        
        self.pnl_history.append({
            'timestamp': current_time.isoformat(),
            'pnl': float(self.unrealized_pnl + self.realized_pnl)
        })
    
    def calculate_risk_metrics(self, positions: List[Dict[str, Any]]) -> None:
        """Calculate advanced risk metrics."""
        try:
            if not positions:
                return
            
            # Calculate concentration risk
            total_value = sum(float(pos.get('value', 0)) for pos in positions)
            if total_value > 0:
                position_weights = [float(pos.get('value', 0)) / total_value for pos in positions]
                # Herfindahl-Hirschman Index for concentration
                hhi = sum(w ** 2 for w in position_weights)
                self.concentration_risk = hhi
                
                # Diversification ratio
                self.diversification_ratio = 1 / hhi if hhi > 0 else 0
            
            # Update position metrics
            self.position_count = len(positions)
            if positions:
                self.max_position_size = Decimal(str(max(float(pos.get('value', 0)) for pos in positions)))
            
            # Calculate portfolio volatility from historical data
            if len(self.value_history) > 1:
                values = [item['value'] for item in self.value_history]
                returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values)) if values[i-1] > 0]
                if len(returns) > 1:
                    self.volatility = statistics.stdev(returns) * (1440 ** 0.5)  # Annualized from minute data
            
            # Calculate Value at Risk (95% confidence)
            if len(self.pnl_history) > 20:
                pnl_values = [item['pnl'] for item in self.pnl_history]
                pnl_values.sort()
                var_index = int(len(pnl_values) * 0.05)  # 5th percentile
                self.var_95 = Decimal(str(abs(pnl_values[var_index])))
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")


@dataclass
class SystemHealthMetrics:
    """System health and performance metrics."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_latency: float = 0.0
    active_connections: int = 0
    error_rate: float = 0.0
    uptime_seconds: float = 0.0
    
    # Trading system specific
    blockchain_sync_status: Dict[str, str] = field(default_factory=dict)
    api_response_times: Dict[str, float] = field(default_factory=dict)
    websocket_message_rate: float = 0.0
    database_response_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'network_latency': self.network_latency,
            'active_connections': self.active_connections,
            'error_rate': self.error_rate,
            'uptime_seconds': self.uptime_seconds,
            'blockchain_sync_status': self.blockchain_sync_status,
            'api_response_times': self.api_response_times,
            'websocket_message_rate': self.websocket_message_rate,
            'database_response_time': self.database_response_time
        }


class LiveDashboardService:
    """
    Enhanced Live Dashboard Integration Service.
    
    Features:
    - Real-time data streaming with intelligent change detection
    - Advanced analytics and performance monitoring
    - Configurable update frequencies and priorities
    - Comprehensive error handling and recovery
    - Performance optimization with data caching
    - Multi-source data aggregation
    - Historical data tracking and trend analysis
    """
    
    def __init__(self, trading_engine: Optional[TradingEngine] = None):
        """Initialize enhanced live dashboard service."""
        self.trading_engine = trading_engine
        self.portfolio_manager: Optional[PortfolioManager] = None
        self.is_running = False
        
        # Enhanced configuration
        self.config = {
            'update_intervals': {
                'portfolio': 2.0,       # 2 seconds for portfolio updates
                'trading': 1.0,         # 1 second for trading updates
                'system': 10.0,         # 10 seconds for system health
                'analytics': 30.0       # 30 seconds for advanced analytics
            },
            'change_thresholds': {
                'portfolio_value': 0.01,    # 1% change triggers update
                'pnl': 0.005,              # 0.5% change triggers update
                'trade_count': 1,          # Any new trade triggers update
                'system_health': 5.0       # 5% change in metrics
            },
            'max_history_length': 1440,   # 24 hours of minute data
            'performance_window': 100,     # Performance metrics window
            'batch_update_size': 10        # Batch size for bulk updates
        }
        
        # Enhanced metrics tracking
        self.trading_metrics = EnhancedTradingMetrics(
            total_trades_today=0,
            successful_trades=0,
            failed_trades=0,
            total_volume=Decimal('0'),
            total_profit=Decimal('0'),
            success_rate=0.0,
            active_strategies=[]
        )
        
        self.portfolio_metrics = EnhancedPortfolioMetrics(
            total_value=Decimal('125826.86'),
            available_balance=Decimal('45000.00'),
            invested_amount=Decimal('80826.86'),
            unrealized_pnl=Decimal('3241.87'),
            realized_pnl=Decimal('12485.34'),
            daily_change=Decimal('3241.87'),
            daily_change_percent=2.64,
            top_positions=[]
        )
        
        self.system_metrics = SystemHealthMetrics()
        
        # Background tasks and monitoring
        self.background_tasks: List[asyncio.Task] = []
        self.update_queues: Dict[str, asyncio.Queue] = {
            'critical': asyncio.Queue(maxsize=100),
            'high': asyncio.Queue(maxsize=200),
            'normal': asyncio.Queue(maxsize=500),
            'low': asyncio.Queue(maxsize=1000)
        }
        
        # Performance tracking
        self.performance_stats = {
            'updates_sent': 0,
            'updates_failed': 0,
            'average_latency': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'data_change_events': 0,
            'start_time': datetime.utcnow()
        }
        
        # Data change detection
        self.previous_data = {
            'portfolio': {},
            'trading': {},
            'system': {}
        }
        
        # Event handlers and callbacks
        self.event_handlers: Dict[str, List[Callable]] = {
            'trade_executed': [],
            'portfolio_updated': [],
            'strategy_started': [],
            'strategy_stopped': [],
            'risk_alert': [],
            'arbitrage_found': [],
            'token_discovered': [],
            'system_alert': [],
            'performance_threshold': []
        }
        
        # Real-time analytics
        self.analytics_engine = {
            'price_trends': deque(maxlen=1000),
            'volume_trends': deque(maxlen=1000),
            'performance_metrics': deque(maxlen=100),
            'correlation_matrix': {},
            'risk_indicators': []
        }
        
        logger.info("✅ Enhanced Live Dashboard Service initialized")
    
    async def start(self) -> None:
        """Start the enhanced live dashboard service."""
        if self.is_running:
            logger.warning("Enhanced live dashboard service already running")
            return
        
        try:
            self.is_running = True
            self.performance_stats['start_time'] = datetime.utcnow()
            
            # Start enhanced background tasks
            self.background_tasks = [
                asyncio.create_task(self._enhanced_metrics_update_loop()),
                asyncio.create_task(self._portfolio_analytics_loop()),
                asyncio.create_task(self._trading_analytics_loop()),
                asyncio.create_task(self._system_health_monitor_loop()),
                asyncio.create_task(self._performance_monitor_loop()),
                asyncio.create_task(self._update_queue_processor()),
                asyncio.create_task(self._data_change_detector()),
                asyncio.create_task(self._analytics_engine_loop())
            ]
            
            # Register with trading engine if available
            if self.trading_engine:
                await self._register_enhanced_trading_callbacks()
            
            # Initialize historical data
            await self._initialize_historical_data()
            
            logger.info("🚀 Enhanced Live Dashboard Service started with advanced analytics")
            
        except Exception as e:
            logger.error(f"❌ Failed to start enhanced live dashboard service: {e}")
            await self.stop()
            raise LiveDashboardServiceError(f"Service startup failed: {e}")
    
    async def stop(self) -> None:
        """Stop the enhanced live dashboard service."""
        try:
            self.is_running = False
            
            # Cancel all background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete with timeout
            if self.background_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self.background_tasks, return_exceptions=True),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    logger.warning("Some background tasks didn't finish within timeout")
            
            # Clear queues
            for queue in self.update_queues.values():
                while not queue.empty():
                    try:
                        queue.get_nowait()
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        break
            
            # Log final performance statistics
            uptime = datetime.utcnow() - self.performance_stats['start_time']
            logger.info(
                f"🛑 Enhanced Live Dashboard Service stopped - "
                f"Uptime: {uptime.total_seconds():.0f}s, "
                f"Updates: {self.performance_stats['updates_sent']}, "
                f"Failures: {self.performance_stats['updates_failed']}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error stopping enhanced live dashboard service: {e}")
    
    def set_trading_engine(self, trading_engine: TradingEngine) -> None:
        """Set the trading engine for enhanced monitoring."""
        self.trading_engine = trading_engine
        if self.is_running:
            asyncio.create_task(self._register_enhanced_trading_callbacks())
    
    def set_portfolio_manager(self, portfolio_manager: PortfolioManager) -> None:
        """Set the portfolio manager for enhanced monitoring."""
        self.portfolio_manager = portfolio_manager
    
    async def broadcast_trade_execution(self, trade_data: Dict[str, Any]) -> None:
        """Enhanced trade execution broadcasting with analytics."""
        try:
            start_time = time.time()
            
            # Update enhanced trading metrics
            await self._update_enhanced_trading_metrics(trade_data)
            
            # Calculate change magnitude for prioritization
            change_magnitude = self._calculate_trade_impact(trade_data)
            
            # Prepare enhanced update data
            update_data = {
                'trade': trade_data,
                'metrics': self.trading_metrics.to_dict(),
                'analytics': await self._get_trading_analytics(),
                'impact_analysis': await self._analyze_trade_impact(trade_data),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Create prioritized update
            priority = UpdatePriority.CRITICAL if change_magnitude > 0.05 else UpdatePriority.HIGH
            
            update = LiveDashboardUpdate(
                update_type='trade_execution',
                timestamp=datetime.utcnow(),
                data=update_data,
                priority=priority.name.lower(),
                change_magnitude=change_magnitude,
                affected_metrics=['trading_profit', 'success_rate', 'trade_count'],
                source_component='trading_engine',
                requires_acknowledgment=priority == UpdatePriority.CRITICAL
            )
            
            # Queue for processing
            await self._queue_update(update, priority)
            
            # Update performance stats
            latency = (time.time() - start_time) * 1000
            self._update_performance_stats('trade_execution', latency)
            
            logger.info(f"📊 Enhanced trade execution broadcast queued: {trade_data.get('symbol', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced trade execution broadcast: {e}")
            self.performance_stats['updates_failed'] += 1
    
    async def broadcast_portfolio_update(self, portfolio_data: Dict[str, Any]) -> None:
        """Enhanced portfolio update broadcasting with change detection."""
        try:
            start_time = time.time()
            
            # Update enhanced portfolio metrics
            await self._update_enhanced_portfolio_metrics(portfolio_data)
            
            # Detect significant changes
            change_type = self._detect_portfolio_changes(portfolio_data)
            
            if change_type == DataChangeType.NONE:
                return  # Skip update if no significant change
            
            # Calculate change magnitude
            change_magnitude = self._calculate_portfolio_change_magnitude(portfolio_data)
            
            # Prepare enhanced update data
            update_data = {
                'portfolio': portfolio_data,
                'metrics': self.portfolio_metrics.to_dict(),
                'analytics': await self._get_portfolio_analytics(),
                'risk_analysis': await self._get_risk_analysis(),
                'performance_attribution': await self._get_performance_attribution(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Determine priority based on change magnitude
            if change_magnitude > 0.1:  # 10% change
                priority = UpdatePriority.CRITICAL
            elif change_magnitude > 0.05:  # 5% change
                priority = UpdatePriority.HIGH
            else:
                priority = UpdatePriority.NORMAL
            
            update = LiveDashboardUpdate(
                update_type='portfolio_update',
                timestamp=datetime.utcnow(),
                data=update_data,
                priority=priority.name.lower(),
                change_magnitude=change_magnitude,
                affected_metrics=['portfolio_value', 'pnl', 'risk_score'],
                source_component='portfolio_manager'
            )
            
            # Queue for processing
            await self._queue_update(update, priority)
            
            # Update performance stats
            latency = (time.time() - start_time) * 1000
            self._update_performance_stats('portfolio_update', latency)
            
            logger.debug(f"📈 Enhanced portfolio update queued: change_magnitude={change_magnitude:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced portfolio update broadcast: {e}")
            self.performance_stats['updates_failed'] += 1
    
    async def broadcast_system_health_update(self, system_data: Dict[str, Any]) -> None:
        """Enhanced system health broadcasting with trend analysis."""
        try:
            # Update system metrics
            await self._update_system_metrics(system_data)
            
            # Analyze system trends
            trend_analysis = await self._analyze_system_trends()
            
            # Detect anomalies
            anomalies = await self._detect_system_anomalies()
            
            # Prepare enhanced update data
            update_data = {
                'system_health': system_data,
                'metrics': self.system_metrics.to_dict(),
                'trend_analysis': trend_analysis,
                'anomalies': anomalies,
                'recommendations': await self._get_system_recommendations(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Determine priority based on health status
            if anomalies or self.system_metrics.error_rate > 0.05:
                priority = UpdatePriority.HIGH
            else:
                priority = UpdatePriority.LOW
            
            update = LiveDashboardUpdate(
                update_type='system_health',
                timestamp=datetime.utcnow(),
                data=update_data,
                priority=priority.name.lower(),
                source_component='system_monitor'
            )
            
            await self._queue_update(update, priority)
            
        except Exception as e:
            logger.error(f"❌ Error in system health broadcast: {e}")
    
    # Enhanced background task implementations
    async def _enhanced_metrics_update_loop(self) -> None:
        """Enhanced metrics update loop with intelligent scheduling."""
        while self.is_running:
            try:
                # Get current data from all sources
                portfolio_data = await self._fetch_portfolio_data()
                trading_data = await self._fetch_trading_data()
                
                # Process updates with change detection
                if portfolio_data:
                    await self.broadcast_portfolio_update(portfolio_data)
                
                if trading_data:
                    await self._process_trading_data_update(trading_data)
                
                # Dynamic sleep based on market activity
                sleep_time = self._calculate_dynamic_update_interval()
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in enhanced metrics update loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _portfolio_analytics_loop(self) -> None:
        """Advanced portfolio analytics background task."""
        while self.is_running:
            try:
                # Update historical data
                self.portfolio_metrics.update_historical_data()
                
                # Calculate risk metrics
                positions = await self._get_current_positions()
                self.portfolio_metrics.calculate_risk_metrics(positions)
                
                # Generate analytics insights
                insights = await self._generate_portfolio_insights()
                
                # Broadcast analytics update if significant insights
                if insights.get('significant_changes'):
                    await self._broadcast_analytics_update('portfolio_analytics', insights)
                
                await asyncio.sleep(self.config['update_intervals']['analytics'])
                
            except Exception as e:
                logger.error(f"Error in portfolio analytics loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _trading_analytics_loop(self) -> None:
        """Advanced trading analytics background task."""
        while self.is_running:
            try:
                # Get recent trade history
                trade_history = await self._get_recent_trade_history()
                
                # Calculate enhanced trading metrics
                self.trading_metrics.calculate_enhanced_metrics(trade_history)
                
                # Update performance analytics
                performance_metrics = await self._calculate_performance_metrics()
                
                # Detect trading patterns
                patterns = await self._detect_trading_patterns(trade_history)
                
                # Generate trading insights
                insights = {
                    'performance_metrics': performance_metrics,
                    'patterns': patterns,
                    'recommendations': await self._generate_trading_recommendations()
                }
                
                # Broadcast if significant insights
                if insights.get('recommendations'):
                    await self._broadcast_analytics_update('trading_analytics', insights)
                
                await asyncio.sleep(self.config['update_intervals']['analytics'])
                
            except Exception as e:
                logger.error(f"Error in trading analytics loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _system_health_monitor_loop(self) -> None:
        """Enhanced system health monitoring with predictive analytics."""
        while self.is_running:
            try:
                # Collect comprehensive system metrics
                system_data = await self._collect_system_metrics()
                
                # Update system health
                await self.broadcast_system_health_update(system_data)
                
                # Predictive health analysis
                health_forecast = await self._predict_system_health()
                
                # Alert on potential issues
                if health_forecast.get('warnings'):
                    await self._send_system_alerts(health_forecast['warnings'])
                
                await asyncio.sleep(self.config['update_intervals']['system'])
                
            except Exception as e:
                logger.error(f"Error in system health monitor: {e}")
                await asyncio.sleep(10.0)
    
    async def _performance_monitor_loop(self) -> None:
        """Monitor service performance and optimize operations."""
        while self.is_running:
            try:
                # Calculate performance metrics
                uptime = datetime.utcnow() - self.performance_stats['start_time']
                total_updates = self.performance_stats['updates_sent']
                failed_updates = self.performance_stats['updates_failed']
                
                success_rate = (total_updates - failed_updates) / total_updates if total_updates > 0 else 0
                updates_per_second = total_updates / uptime.total_seconds() if uptime.total_seconds() > 0 else 0
                
                # Log performance summary
                if total_updates > 0 and total_updates % 1000 == 0:
                    logger.info(
                        f"📊 Performance Summary - "
                        f"Updates: {total_updates}, "
                        f"Success Rate: {success_rate:.2%}, "
                        f"Rate: {updates_per_second:.1f}/s, "
                        f"Avg Latency: {self.performance_stats['average_latency']:.1f}ms"
                    )
                
                # Optimize based on performance
                await self._optimize_performance()
                
                await asyncio.sleep(60.0)  # Every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(60.0)
    
    async def _update_queue_processor(self) -> None:
        """Process update queues by priority."""
        while self.is_running:
            try:
                # Process queues in priority order
                for priority_name in ['critical', 'high', 'normal', 'low']:
                    queue = self.update_queues[priority_name]
                    
                    try:
                        # Non-blocking get with short timeout
                        update = await asyncio.wait_for(queue.get(), timeout=0.1)
                        await self._process_dashboard_update(update)
                        queue.task_done()
                        
                        # Brief pause between updates to prevent overwhelming
                        if priority_name == 'low':
                            await asyncio.sleep(0.01)
                            
                    except asyncio.TimeoutError:
                        continue
                
                # Small delay if no updates were processed
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in update queue processor: {e}")
                await asyncio.sleep(1.0)
    
    async def _data_change_detector(self) -> None:
        """Monitor data changes and trigger updates accordingly."""
        while self.is_running:
            try:
                # Check for significant data changes
                current_data = {
                    'portfolio': await self._get_current_portfolio_snapshot(),
                    'trading': await self._get_current_trading_snapshot(),
                    'system': await self._get_current_system_snapshot()
                }
                
                # Compare with previous data and detect changes
                for data_type, current in current_data.items():
                    if self.previous_data.get(data_type):
                        change_magnitude = self._calculate_data_change_magnitude(
                            self.previous_data[data_type], 
                            current
                        )
                        
                        if change_magnitude > 0.01:  # 1% threshold
                            self.performance_stats['data_change_events'] += 1
                            logger.debug(f"Significant {data_type} change detected: {change_magnitude:.4f}")
                
                # Update previous data
                self.previous_data = current_data
                
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in data change detector: {e}")
                await asyncio.sleep(5.0)
    
    async def _analytics_engine_loop(self) -> None:
        """Advanced analytics engine for insights generation."""
        while self.is_running:
            try:
                # Update price and volume trends
                await self._update_market_trends()
                
                # Calculate correlations
                await self._update_correlation_matrix()
                
                # Generate predictive insights
                insights = await self._generate_predictive_insights()
                
                # Update risk indicators
                await self._update_risk_indicators()
                
                # Broadcast insights if significant
                if insights.get('actionable_insights'):
                    await self._broadcast_analytics_update('predictive_insights', insights)
                
                await asyncio.sleep(30.0)  # Every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in analytics engine: {e}")
                await asyncio.sleep(30.0)
    
    # Enhanced helper methods
    async def _queue_update(self, update: LiveDashboardUpdate, priority: UpdatePriority) -> None:
        """Queue update for processing based on priority."""
        try:
            queue_name = priority.name.lower()
            queue = self.update_queues[queue_name]
            
            if queue.full():
                # If queue is full, drop oldest low priority items
                if priority == UpdatePriority.LOW:
                    try:
                        queue.get_nowait()
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        pass
                else:
                    logger.warning(f"Queue {queue_name} is full, dropping update")
                    return
            
            await queue.put(update)
            
        except Exception as e:
            logger.error(f"Error queuing update: {e}")
    
    async def _process_dashboard_update(self, update: LiveDashboardUpdate) -> None:
        """Process individual dashboard update."""
        try:
            start_time = time.time()
            
            # Broadcast via WebSocket manager
            if WEBSOCKET_AVAILABLE and websocket_manager:
                # Map update type to appropriate WebSocket method
                if update.update_type == 'portfolio_update':
                    priority = getattr(MessagePriority, update.priority.upper(), MessagePriority.NORMAL)
                    await websocket_manager.broadcast_portfolio_update(update.data, priority)
                elif update.update_type == 'trade_execution':
                    await websocket_manager.broadcast_trade_execution(update.data)
                elif update.update_type == 'system_health':
                    await websocket_manager.broadcast_system_alert(update.data)
                else:
                    # Generic broadcast
                    await websocket_manager._broadcast_to_subscribers(
                        'dashboard',
                        update.update_type,
                        update.data
                    )
            
            # Update performance stats
            latency = (time.time() - start_time) * 1000
            self.performance_stats['updates_sent'] += 1
            self._update_performance_stats(update.update_type, latency)
            
        except Exception as e:
            logger.error(f"Error processing dashboard update: {e}")
            self.performance_stats['updates_failed'] += 1
    
    def _update_performance_stats(self, operation_type: str, latency: float) -> None:
        """Update performance statistics."""
        try:
            # Update average latency with moving average
            current_avg = self.performance_stats['average_latency']
            if current_avg == 0:
                self.performance_stats['average_latency'] = latency
            else:
                # Exponential moving average
                alpha = 0.1
                self.performance_stats['average_latency'] = (alpha * latency) + ((1 - alpha) * current_avg)
            
        except Exception as e:
            logger.error(f"Error updating performance stats: {e}")
    
    def _calculate_dynamic_update_interval(self) -> float:
        """Calculate dynamic update interval based on market activity."""
        try:
            base_interval = self.config['update_intervals']['portfolio']
            
            # Adjust based on trading activity
            if self.trading_metrics.trades_per_hour > 10:
                return base_interval * 0.5  # Faster updates during high activity
            elif self.trading_metrics.trades_per_hour < 1:
                return base_interval * 2.0  # Slower updates during low activity
            
            return base_interval
            
        except Exception:
            return self.config['update_intervals']['portfolio']
    
    def _detect_portfolio_changes(self, portfolio_data: Dict[str, Any]) -> DataChangeType:
        """Detect type of portfolio changes."""
        try:
            if not self.previous_data.get('portfolio'):
                return DataChangeType.SIGNIFICANT
            
            previous = self.previous_data['portfolio']
            current = portfolio_data
            
            # Check for significant value changes
            prev_value = float(previous.get('total_value', 0))
            curr_value = float(current.get('total_value', 0))
            
            if prev_value > 0:
                change_percent = abs(curr_value - prev_value) / prev_value
                
                if change_percent > 0.05:  # 5% change
                    return DataChangeType.SIGNIFICANT
                elif change_percent > 0.01:  # 1% change
                    return DataChangeType.MODERATE
                elif change_percent > 0.001:  # 0.1% change
                    return DataChangeType.MINOR
            
            return DataChangeType.NONE
            
        except Exception:
            return DataChangeType.MODERATE
    
    def _calculate_portfolio_change_magnitude(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate magnitude of portfolio changes."""
        try:
            if not self.previous_data.get('portfolio'):
                return 0.1  # Default moderate change for first update
            
            previous = self.previous_data['portfolio']
            current = portfolio_data
            
            # Calculate composite change score
            changes = []
            
            # Value change
            prev_value = float(previous.get('total_value', 0))
            curr_value = float(current.get('total_value', 0))
            if prev_value > 0:
                value_change = abs(curr_value - prev_value) / prev_value
                changes.append(value_change)
            
            # PnL change
            prev_pnl = float(previous.get('daily_pnl', 0))
            curr_pnl = float(current.get('daily_pnl', 0))
            if abs(prev_pnl) > 0:
                pnl_change = abs(curr_pnl - prev_pnl) / abs(prev_pnl)
                changes.append(pnl_change)
            
            # Return maximum change as magnitude
            return max(changes) if changes else 0.0
            
        except Exception:
            return 0.01  # Default small change
    
    def _calculate_trade_impact(self, trade_data: Dict[str, Any]) -> float:
        """Calculate impact magnitude of a trade."""
        try:
            profit = float(trade_data.get('profit', 0))
            size = float(trade_data.get('size', 0))
            
            # Calculate impact relative to portfolio
            portfolio_value = float(self.portfolio_metrics.total_value)
            
            if portfolio_value > 0:
                profit_impact = abs(profit) / portfolio_value
                size_impact = size / portfolio_value
                return max(profit_impact, size_impact)
            
            return 0.01  # Default small impact
            
        except Exception:
            return 0.01
    
    def _calculate_data_change_magnitude(self, previous: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Calculate overall data change magnitude."""
        try:
            if not previous or not current:
                return 0.0
            
            changes = []
            
            # Compare numeric values
            for key in current:
                if key in previous and isinstance(current[key], (int, float)):
                    prev_val = float(previous[key])
                    curr_val = float(current[key])
                    
                    if prev_val != 0:
                        change = abs(curr_val - prev_val) / abs(prev_val)
                        changes.append(change)
            
            return max(changes) if changes else 0.0
            
        except Exception:
            return 0.0
    
    # Data fetching methods (to be implemented based on actual data sources)
    async def _fetch_portfolio_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current portfolio data."""
        # Placeholder implementation
        return {
            'total_value': float(self.portfolio_metrics.total_value),
            'daily_pnl': float(self.portfolio_metrics.daily_change),
            'available_balance': float(self.portfolio_metrics.available_balance),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _fetch_trading_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current trading data."""
        # Placeholder implementation
        return {
            'total_trades': self.trading_metrics.total_trades_today,
            'success_rate': self.trading_metrics.success_rate,
            'total_profit': float(self.trading_metrics.total_profit),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _get_current_positions(self) -> List[Dict[str, Any]]:
        """Get current portfolio positions."""
        # Placeholder implementation
        return [
            {'symbol': 'ETH', 'value': 50000.0, 'pnl': 1250.0},
            {'symbol': 'LINK', 'value': 25000.0, 'pnl': 750.0}
        ]
    
    async def _get_recent_trade_history(self) -> List[Dict[str, Any]]:
        """Get recent trade history for analytics."""
        # Placeholder implementation
        return [
            {'symbol': 'ETH', 'profit': 125.0, 'size': 1000.0, 'timestamp': datetime.utcnow()},
            {'symbol': 'LINK', 'profit': -50.0, 'size': 500.0, 'timestamp': datetime.utcnow()}
        ]
    
    # Analytics methods (placeholders for future implementation)
    async def _get_trading_analytics(self) -> Dict[str, Any]:
        """Get trading analytics data."""
        return {'advanced_metrics': 'placeholder'}
    
    async def _get_portfolio_analytics(self) -> Dict[str, Any]:
        """Get portfolio analytics data."""
        return {'risk_metrics': 'placeholder'}
    
    async def _get_risk_analysis(self) -> Dict[str, Any]:
        """Get risk analysis data."""
        return {'risk_score': 0.3, 'recommendations': []}
    
    async def _get_performance_attribution(self) -> Dict[str, Any]:
        """Get performance attribution analysis."""
        return {'attribution': 'placeholder'}
    
    async def _analyze_trade_impact(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact of a trade."""
        return {'impact_analysis': 'placeholder'}
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        return {
            'cpu_usage': 45.2,
            'memory_usage': 68.7,
            'active_connections': len(websocket_manager.connections) if WEBSOCKET_AVAILABLE else 0,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _analyze_system_trends(self) -> Dict[str, Any]:
        """Analyze system performance trends."""
        return {'trends': 'placeholder'}
    
    async def _detect_system_anomalies(self) -> List[Dict[str, Any]]:
        """Detect system anomalies."""
        return []
    
    async def _get_system_recommendations(self) -> List[str]:
        """Get system optimization recommendations."""
        return []
    
    async def _predict_system_health(self) -> Dict[str, Any]:
        """Predict future system health."""
        return {'forecast': 'healthy', 'warnings': []}
    
    async def _optimize_performance(self) -> None:
        """Optimize service performance based on metrics."""
        # Placeholder for performance optimization logic
        pass
    
    async def _initialize_historical_data(self) -> None:
        """Initialize historical data tracking."""
        # Initialize with current data
        self.portfolio_metrics.update_historical_data()
    
    async def _register_enhanced_trading_callbacks(self) -> None:
        """Register enhanced callbacks with trading engine."""
        # Placeholder for trading engine integration
        pass
    
    async def _update_enhanced_trading_metrics(self, trade_data: Dict[str, Any]) -> None:
        """Update enhanced trading metrics from trade data."""
        try:
            # Update basic metrics
            self.trading_metrics.total_trades_today += 1
            
            profit = Decimal(str(trade_data.get('profit', 0)))
            self.trading_metrics.total_profit += profit
            
            if profit > 0:
                self.trading_metrics.successful_trades += 1
            else:
                self.trading_metrics.failed_trades += 1
            
            # Recalculate success rate
            total_trades = self.trading_metrics.successful_trades + self.trading_metrics.failed_trades
            if total_trades > 0:
                self.trading_metrics.success_rate = self.trading_metrics.successful_trades / total_trades
            
            # Update timing
            self.trading_metrics.last_trade_time = datetime.utcnow()
            
            # Add performance data
            if 'execution_time' in trade_data:
                self.trading_metrics.execution_latency_ms.append(float(trade_data['execution_time']))
            
            if 'slippage' in trade_data:
                self.trading_metrics.slippage_data.append(float(trade_data['slippage']))
            
            if 'gas_cost' in trade_data:
                self.trading_metrics.gas_costs.append(Decimal(str(trade_data['gas_cost'])))
            
        except Exception as e:
            logger.error(f"Error updating enhanced trading metrics: {e}")
    
    async def _update_enhanced_portfolio_metrics(self, portfolio_data: Dict[str, Any]) -> None:
        """Update enhanced portfolio metrics from portfolio data."""
        try:
            # Update basic metrics
            if 'total_value' in portfolio_data:
                self.portfolio_metrics.total_value = Decimal(str(portfolio_data['total_value']))
            
            if 'daily_pnl' in portfolio_data:
                self.portfolio_metrics.daily_change = Decimal(str(portfolio_data['daily_pnl']))
            
            if 'available_balance' in portfolio_data:
                self.portfolio_metrics.available_balance = Decimal(str(portfolio_data['available_balance']))
            
            # Update historical data
            self.portfolio_metrics.update_historical_data()
            
        except Exception as e:
            logger.error(f"Error updating enhanced portfolio metrics: {e}")
    
    async def _update_system_metrics(self, system_data: Dict[str, Any]) -> None:
        """Update system metrics from system data."""
        try:
            if 'cpu_usage' in system_data:
                self.system_metrics.cpu_usage = float(system_data['cpu_usage'])
            
            if 'memory_usage' in system_data:
                self.system_metrics.memory_usage = float(system_data['memory_usage'])
            
            if 'active_connections' in system_data:
                self.system_metrics.active_connections = int(system_data['active_connections'])
            
            # Calculate uptime
            uptime = datetime.utcnow() - self.performance_stats['start_time']
            self.system_metrics.uptime_seconds = uptime.total_seconds()
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    # Placeholder methods for future analytics implementation
    async def _get_current_portfolio_snapshot(self) -> Dict[str, Any]:
        """Get current portfolio snapshot."""
        return self.portfolio_metrics.to_dict()
    
    async def _get_current_trading_snapshot(self) -> Dict[str, Any]:
        """Get current trading snapshot."""
        return self.trading_metrics.to_dict()
    
    async def _get_current_system_snapshot(self) -> Dict[str, Any]:
        """Get current system snapshot."""
        return self.system_metrics.to_dict()
    
    async def _process_trading_data_update(self, trading_data: Dict[str, Any]) -> None:
        """Process trading data update."""
        pass
    
    async def _broadcast_analytics_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Broadcast analytics update."""
        update = LiveDashboardUpdate(
            update_type=update_type,
            timestamp=datetime.utcnow(),
            data=data,
            priority='normal',
            source_component='analytics_engine'
        )
        await self._queue_update(update, UpdatePriority.NORMAL)
    
    async def _send_system_alerts(self, warnings: List[Dict[str, Any]]) -> None:
        """Send system alerts."""
        for warning in warnings:
            update = LiveDashboardUpdate(
                update_type='system_alert',
                timestamp=datetime.utcnow(),
                data=warning,
                priority='high',
                source_component='system_monitor',
                requires_acknowledgment=True
            )
            await self._queue_update(update, UpdatePriority.HIGH)
    
    async def _generate_portfolio_insights(self) -> Dict[str, Any]:
        """Generate portfolio insights."""
        return {'significant_changes': False}
    
    async def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        return {}
    
    async def _detect_trading_patterns(self, trade_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect trading patterns."""
        return {}
    
    async def _generate_trading_recommendations(self) -> List[str]:
        """Generate trading recommendations."""
        return []
    
    async def _update_market_trends(self) -> None:
        """Update market trends."""
        pass
    
    async def _update_correlation_matrix(self) -> None:
        """Update correlation matrix."""
        pass
    
    async def _generate_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights."""
        return {'actionable_insights': False}
    
    async def _update_risk_indicators(self) -> None:
        """Update risk indicators."""
        pass
    
    # Enhanced API methods for external access
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        uptime = datetime.utcnow() - self.performance_stats['start_time']
        
        return {
            'service_uptime_seconds': uptime.total_seconds(),
            'total_updates_sent': self.performance_stats['updates_sent'],
            'total_updates_failed': self.performance_stats['updates_failed'],
            'success_rate': (
                (self.performance_stats['updates_sent'] - self.performance_stats['updates_failed']) /
                self.performance_stats['updates_sent']
            ) if self.performance_stats['updates_sent'] > 0 else 0,
            'average_latency_ms': self.performance_stats['average_latency'],
            'data_change_events': self.performance_stats['data_change_events'],
            'cache_hit_rate': (
                self.performance_stats['cache_hits'] /
                (self.performance_stats['cache_hits'] + self.performance_stats['cache_misses'])
            ) if (self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']) > 0 else 0,
            'queue_sizes': {name: queue.qsize() for name, queue in self.update_queues.items()},
            'current_metrics': {
                'portfolio': self.portfolio_metrics.to_dict(),
                'trading': self.trading_metrics.to_dict(),
                'system': self.system_metrics.to_dict()
            }
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        return {
            'portfolio_analytics': {
                'risk_score': self.portfolio_metrics.risk_score,
                'diversification_ratio': self.portfolio_metrics.diversification_ratio,
                'var_95': float(self.portfolio_metrics.var_95),
                'volatility': self.portfolio_metrics.volatility
            },
            'trading_analytics': {
                'sharpe_ratio': self.trading_metrics.sharpe_ratio,
                'win_loss_ratio': self.trading_metrics.win_loss_ratio,
                'max_drawdown': float(self.trading_metrics.max_drawdown),
                'trades_per_hour': self.trading_metrics.trades_per_hour
            },
            'system_analytics': {
                'performance_score': 100 - (self.system_metrics.error_rate * 100),
                'efficiency_rating': 'high' if self.performance_stats['average_latency'] < 100 else 'medium',
                'stability_score': 100 - (self.performance_stats['updates_failed'] / max(self.performance_stats['updates_sent'], 1) * 100)
            }
        }


# Global enhanced instance
live_dashboard_service = LiveDashboardService()


# Export commonly used classes and functions
__all__ = [
    "LiveDashboardService",
    "LiveDashboardUpdate",
    "EnhancedTradingMetrics",
    "EnhancedPortfolioMetrics",
    "SystemHealthMetrics",
    "UpdatePriority",
    "DataChangeType",
    "live_dashboard_service",
    "LiveDashboardServiceError"
]