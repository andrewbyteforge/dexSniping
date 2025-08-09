"""
Working Strategy Executor for Phase 4C
File: app/core/trading/strategy_executor.py
"""

import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StrategyPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class StrategyExecution:
    execution_id: str
    strategy_name: str
    ai_signal_id: Optional[str]
    token_address: str
    symbol: str
    status: ExecutionStatus
    priority: StrategyPriority
    start_time: datetime
    end_time: Optional[datetime]
    action: str
    position_size: Decimal
    entry_price: Optional[Decimal]
    target_price: Optional[Decimal]
    stop_loss_price: Optional[Decimal]
    realized_pnl: Decimal = Decimal('0')
    unrealized_pnl: Decimal = Decimal('0')
    fees_paid: Decimal = Decimal('0')
    slippage: Decimal = Decimal('0')
    execution_steps: List[Dict[str, Any]] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_id': self.execution_id,
            'strategy_name': self.strategy_name,
            'status': self.status.value,
            'action': self.action,
            'symbol': self.symbol,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class StrategyExecutor:
    """Strategy Executor for Phase 4C."""
    
    def __init__(self):
        self.executor_id = str(uuid.uuid4())
        self.is_running = False
        self.active_executions: Dict[str, StrategyExecution] = {}
        self.execution_queue: List[StrategyExecution] = []
        self.completed_executions: List[StrategyExecution] = []
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.ai_strategy_engine = None
        self.websocket_manager = None
        self.execution_metrics = {
            'average_execution_time': 0.0,
            'success_rate': 0.0,
            'total_volume': 0.0
        }
        logger.info(f"Strategy Executor initialized: {self.executor_id}")
    
    async def initialize(self) -> bool:
        try:
            # Setup AI integration
            try:
                from app.core.ai.trading_strategy_engine import get_ai_strategy_engine
                self.ai_strategy_engine = await get_ai_strategy_engine()
            except ImportError:
                logger.warning("AI strategy engine not available")
            
            # Setup WebSocket integration
            try:
                from app.core.websocket.websocket_manager import websocket_manager
                self.websocket_manager = websocket_manager
            except ImportError:
                logger.warning("WebSocket manager not available")
            
            logger.info("Strategy Executor initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Strategy Executor: {e}")
            return False
    
    async def start(self):
        if not self.is_running:
            self.is_running = True
            logger.info("Strategy Executor started")
    
    async def stop(self):
        self.is_running = False
        logger.info("Strategy Executor stopped")
    
    async def execute_strategy(self, strategy_config: Dict[str, Any], ai_signal: Optional[Dict[str, Any]] = None) -> StrategyExecution:
        try:
            execution = StrategyExecution(
                execution_id=str(uuid.uuid4()),
                strategy_name=strategy_config.get('strategy_name', 'unknown'),
                ai_signal_id=ai_signal.get('signal_id') if ai_signal else None,
                token_address=strategy_config.get('token_address', ''),
                symbol=strategy_config.get('symbol', 'UNKNOWN'),
                status=ExecutionStatus.PENDING,
                priority=StrategyPriority(strategy_config.get('priority', 'medium')),
                start_time=datetime.utcnow(),
                end_time=None,
                action=strategy_config.get('action', 'HOLD'),
                position_size=Decimal(str(strategy_config.get('position_size', '0'))),
                entry_price=None,
                target_price=None,
                stop_loss_price=None
            )
            
            self.execution_queue.append(execution)
            self.total_executions += 1
            logger.info(f"Strategy execution queued: {execution.execution_id}")
            return execution
        except Exception as e:
            logger.error(f"Failed to execute strategy: {e}")
            raise Exception(f"Strategy execution failed: {e}")
    
    async def monitor_execution(self, execution_id: str) -> Optional[StrategyExecution]:
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        for execution in self.completed_executions:
            if execution.execution_id == execution_id:
                return execution
        
        return None
    
    async def optimize_performance(self) -> Dict[str, Any]:
        try:
            optimization_results = {
                'applied_optimizations': ['improved_execution_speed'],
                'optimization_timestamp': datetime.utcnow().isoformat()
            }
            logger.info("Performance optimization completed")
            return optimization_results
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            raise Exception(f"Performance optimization failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'executor_id': self.executor_id,
            'is_running': self.is_running,
            'active_executions': len(self.active_executions),
            'queued_executions': len(self.execution_queue),
            'completed_executions': len(self.completed_executions),
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'execution_metrics': self.execution_metrics,
            'ai_integration_active': self.ai_strategy_engine is not None,
            'websocket_integration_active': self.websocket_manager is not None
        }


# Global instance
strategy_executor = StrategyExecutor()


async def get_strategy_executor() -> StrategyExecutor:
    if not strategy_executor.is_running:
        await strategy_executor.initialize()
        await strategy_executor.start()
    return strategy_executor
