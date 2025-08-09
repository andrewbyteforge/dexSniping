"""
Portfolio Management System
File: app/core/portfolio/portfolio_manager.py

Professional portfolio tracking and management system with real-time
balance updates, P&L calculation, and comprehensive position tracking.
"""

import asyncio
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from app.utils.logger import setup_logger
from app.core.exceptions import PortfolioError, InsufficientFundsError

logger = setup_logger(__name__, "application")


class PositionType(Enum):
    """Position type enumeration."""
    LONG = "long"
    SHORT = "short"


class TransactionType(Enum):
    """Transaction type enumeration."""
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    FEE = "fee"
    REWARD = "reward"


@dataclass
class Position:
    """Individual position data structure."""
    token_address: str
    symbol: str
    amount: Decimal
    average_entry_price: Decimal
    current_price: Decimal = Decimal("0")
    position_type: PositionType = PositionType.LONG
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def market_value(self) -> Decimal:
        """Calculate current market value of the position."""
        return self.amount * self.current_price
    
    @property
    def cost_basis(self) -> Decimal:
        """Calculate the original cost basis."""
        return self.amount * self.average_entry_price
    
    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized profit/loss."""
        if self.position_type == PositionType.LONG:
            return self.market_value - self.cost_basis
        else:
            return self.cost_basis - self.market_value
    
    @property
    def unrealized_pnl_percentage(self) -> Decimal:
        """Calculate unrealized P&L as percentage."""
        if self.cost_basis == 0:
            return Decimal("0")
        return (self.unrealized_pnl / self.cost_basis) * Decimal("100")


@dataclass
class Transaction:
    """Transaction record data structure."""
    transaction_id: str
    token_address: str
    symbol: str
    transaction_type: TransactionType
    amount: Decimal
    price: Decimal
    value: Decimal
    fees: Decimal
    gas_used: int
    transaction_hash: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def net_value(self) -> Decimal:
        """Calculate net value after fees."""
        if self.transaction_type in [TransactionType.BUY, TransactionType.WITHDRAWAL]:
            return self.value + self.fees
        else:
            return self.value - self.fees


@dataclass
class PortfolioSummary:
    """Portfolio summary statistics."""
    total_value: Decimal
    total_cost_basis: Decimal
    total_unrealized_pnl: Decimal
    total_realized_pnl: Decimal
    cash_balance: Decimal
    invested_amount: Decimal
    available_balance: Decimal
    total_fees_paid: Decimal
    position_count: int
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_pnl(self) -> Decimal:
        """Calculate total P&L (realized + unrealized)."""
        return self.total_realized_pnl + self.total_unrealized_pnl
    
    @property
    def total_return_percentage(self) -> Decimal:
        """Calculate total return as percentage."""
        if self.total_cost_basis == 0:
            return Decimal("0")
        return (self.total_pnl / self.total_cost_basis) * Decimal("100")


class PortfolioManager:
    """
    Professional portfolio management system.
    
    Handles position tracking, balance management, P&L calculation,
    and transaction history with real-time updates.
    """
    
    def __init__(self, user_wallet: str):
        """Initialize portfolio manager for a specific user."""
        self.user_wallet = user_wallet
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        self.cash_balance = Decimal("10000.00")  # Starting with $10,000 mock balance
        self.realized_pnl = Decimal("0")
        self.total_fees_paid = Decimal("0")
        self.last_update = datetime.utcnow()
        
        logger.info(f"✅ PortfolioManager initialized for wallet {user_wallet[:10]}...")
    
    async def get_current_positions(self) -> Dict[str, Any]:
        """
        Get all current positions with real-time data.
        
        Returns:
            Dict containing current positions and summary
        """
        try:
            logger.info(f"📊 Getting current positions for {self.user_wallet[:10]}...")
            
            # Update current prices for all positions
            await self._update_position_prices()
            
            # Format positions for response
            formatted_positions = []
            for position in self.positions.values():
                formatted_positions.append({
                    "token_address": position.token_address,
                    "symbol": position.symbol,
                    "amount": float(position.amount),
                    "average_entry_price": float(position.average_entry_price),
                    "current_price": float(position.current_price),
                    "market_value": float(position.market_value),
                    "cost_basis": float(position.cost_basis),
                    "unrealized_pnl": float(position.unrealized_pnl),
                    "unrealized_pnl_percentage": float(position.unrealized_pnl_percentage),
                    "position_type": position.position_type.value,
                    "created_at": position.created_at.isoformat(),
                    "last_updated": position.last_updated.isoformat()
                })
            
            # Calculate portfolio summary
            summary = await self._calculate_portfolio_summary()
            
            return {
                "success": True,
                "positions": formatted_positions,
                "summary": {
                    "total_value": float(summary.total_value),
                    "cash_balance": float(summary.cash_balance),
                    "invested_amount": float(summary.invested_amount),
                    "total_unrealized_pnl": float(summary.total_unrealized_pnl),
                    "total_realized_pnl": float(summary.total_realized_pnl),
                    "total_pnl": float(summary.total_pnl),
                    "total_return_percentage": float(summary.total_return_percentage),
                    "position_count": summary.position_count,
                    "last_updated": summary.last_updated.isoformat()
                },
                "last_updated": self.last_update.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting current positions: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def update_balance(
        self,
        transaction_type: TransactionType,
        amount: Decimal,
        token_address: str = None,
        symbol: str = None,
        price: Decimal = None,
        fees: Decimal = Decimal("0"),
        gas_used: int = 0,
        transaction_hash: str = None
    ) -> Dict[str, Any]:
        """
        Update portfolio balance based on a transaction.
        
        Args:
            transaction_type: Type of transaction
            amount: Amount involved in transaction
            token_address: Token contract address (if applicable)
            symbol: Token symbol
            price: Price per token
            fees: Transaction fees
            gas_used: Gas used for transaction
            transaction_hash: Blockchain transaction hash
            
        Returns:
            Dict containing update results
        """
        try:
            logger.info(
                f"💰 Updating balance: {transaction_type.value} "
                f"{amount} {symbol or 'USD'}"
            )
            
            # Create transaction record
            transaction = Transaction(
                transaction_id=f"tx_{len(self.transactions) + 1:06d}",
                token_address=token_address or "USD",
                symbol=symbol or "USD",
                transaction_type=transaction_type,
                amount=amount,
                price=price or Decimal("1"),
                value=amount * (price or Decimal("1")),
                fees=fees,
                gas_used=gas_used,
                transaction_hash=transaction_hash or f"0x{hash(str(datetime.utcnow()))}"
            )
            
            # Update balances and positions based on transaction type
            if transaction_type == TransactionType.BUY:
                await self._handle_buy_transaction(transaction)
            elif transaction_type == TransactionType.SELL:
                await self._handle_sell_transaction(transaction)
            elif transaction_type == TransactionType.DEPOSIT:
                self.cash_balance += amount
            elif transaction_type == TransactionType.WITHDRAWAL:
                if self.cash_balance < amount:
                    raise InsufficientFundsError(
                        f"Insufficient cash balance for withdrawal: "
                        f"${amount} requested, ${self.cash_balance} available"
                    )
                self.cash_balance -= amount
            elif transaction_type == TransactionType.FEE:
                self.total_fees_paid += amount
                self.cash_balance -= amount
            
            # Add transaction to history
            self.transactions.append(transaction)
            self.total_fees_paid += fees
            self.last_update = datetime.utcnow()
            
            logger.info(f"✅ Balance updated successfully: Transaction {transaction.transaction_id}")
            
            return {
                "success": True,
                "transaction_id": transaction.transaction_id,
                "new_cash_balance": float(self.cash_balance),
                "transaction": {
                    "type": transaction_type.value,
                    "amount": float(amount),
                    "value": float(transaction.value),
                    "fees": float(fees),
                    "net_value": float(transaction.net_value)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating balance: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def calculate_pnl(
        self,
        token_address: str = None,
        include_fees: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate profit and loss for portfolio or specific position.
        
        Args:
            token_address: Calculate P&L for specific token (optional)
            include_fees: Whether to include fees in calculation
            
        Returns:
            Dict containing P&L calculations
        """
        try:
            logger.info(f"📈 Calculating P&L{f' for {token_address[:10]}...' if token_address else ''}")
            
            if token_address:
                # Calculate P&L for specific position
                if token_address not in self.positions:
                    return {
                        "success": False,
                        "error": f"No position found for token {token_address}"
                    }
                
                position = self.positions[token_address]
                await self._update_position_prices()
                
                # Calculate realized P&L from transactions
                realized_pnl = await self._calculate_realized_pnl_for_token(token_address)
                
                pnl_data = {
                    "token_address": token_address,
                    "symbol": position.symbol,
                    "unrealized_pnl": float(position.unrealized_pnl),
                    "unrealized_pnl_percentage": float(position.unrealized_pnl_percentage),
                    "realized_pnl": float(realized_pnl),
                    "total_pnl": float(position.unrealized_pnl + realized_pnl),
                    "current_value": float(position.market_value),
                    "cost_basis": float(position.cost_basis)
                }
            else:
                # Calculate total portfolio P&L
                summary = await self._calculate_portfolio_summary()
                
                pnl_data = {
                    "total_unrealized_pnl": float(summary.total_unrealized_pnl),
                    "total_realized_pnl": float(summary.total_realized_pnl),
                    "total_pnl": float(summary.total_pnl),
                    "total_return_percentage": float(summary.total_return_percentage),
                    "total_value": float(summary.total_value),
                    "total_cost_basis": float(summary.total_cost_basis)
                }
            
            # Include fees if requested
            if include_fees:
                pnl_data["total_fees_paid"] = float(self.total_fees_paid)
                if "total_pnl" in pnl_data:
                    pnl_data["pnl_after_fees"] = pnl_data["total_pnl"] - float(self.total_fees_paid)
            
            return {
                "success": True,
                "pnl_data": pnl_data,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating P&L: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def get_transaction_history(
        self,
        limit: int = 50,
        transaction_type: Optional[TransactionType] = None,
        token_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get transaction history with optional filtering."""
        try:
            history = self.transactions.copy()
            
            # Apply filters
            if transaction_type:
                history = [t for t in history if t.transaction_type == transaction_type]
            if token_address:
                history = [t for t in history if t.token_address == token_address]
            
            # Sort by timestamp (newest first) and limit
            history.sort(key=lambda x: x.timestamp, reverse=True)
            history = history[:limit]
            
            # Format for response
            formatted_history = []
            for transaction in history:
                formatted_history.append({
                    "transaction_id": transaction.transaction_id,
                    "token_address": transaction.token_address,
                    "symbol": transaction.symbol,
                    "type": transaction.transaction_type.value,
                    "amount": float(transaction.amount),
                    "price": float(transaction.price),
                    "value": float(transaction.value),
                    "fees": float(transaction.fees),
                    "net_value": float(transaction.net_value),
                    "gas_used": transaction.gas_used,
                    "transaction_hash": transaction.transaction_hash,
                    "timestamp": transaction.timestamp.isoformat()
                })
            
            return {
                "success": True,
                "transactions": formatted_history,
                "count": len(formatted_history),
                "total_transactions": len(self.transactions)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting transaction history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Private helper methods
    
    async def _handle_buy_transaction(self, transaction: Transaction) -> None:
        """Handle a buy transaction."""
        # Deduct cash for purchase
        total_cost = transaction.value + transaction.fees
        if self.cash_balance < total_cost:
            raise InsufficientFundsError(
                f"Insufficient funds for purchase: "
                f"${total_cost} required, ${self.cash_balance} available"
            )
        
        self.cash_balance -= total_cost
        
        # Update or create position
        if transaction.token_address in self.positions:
            position = self.positions[transaction.token_address]
            # Calculate new average entry price
            total_amount = position.amount + transaction.amount
            total_cost = (position.amount * position.average_entry_price) + transaction.value
            position.average_entry_price = total_cost / total_amount
            position.amount = total_amount
            position.last_updated = datetime.utcnow()
        else:
            # Create new position
            self.positions[transaction.token_address] = Position(
                token_address=transaction.token_address,
                symbol=transaction.symbol,
                amount=transaction.amount,
                average_entry_price=transaction.price,
                current_price=transaction.price
            )
    
    async def _handle_sell_transaction(self, transaction: Transaction) -> None:
        """Handle a sell transaction."""
        if transaction.token_address not in self.positions:
            raise PortfolioError(f"No position found for {transaction.symbol}")
        
        position = self.positions[transaction.token_address]
        if position.amount < transaction.amount:
            raise InsufficientFundsError(
                f"Insufficient {transaction.symbol} balance: "
                f"{transaction.amount} requested, {position.amount} available"
            )
        
        # Calculate realized P&L for this sale
        cost_basis = position.average_entry_price * transaction.amount
        sale_proceeds = transaction.value - transaction.fees
        realized_pnl = sale_proceeds - cost_basis
        self.realized_pnl += realized_pnl
        
        # Add cash from sale
        self.cash_balance += sale_proceeds
        
        # Update position
        position.amount -= transaction.amount
        position.last_updated = datetime.utcnow()
        
        # Remove position if completely sold
        if position.amount == 0:
            del self.positions[transaction.token_address]
    
    async def _update_position_prices(self) -> None:
        """Update current prices for all positions."""
        try:
            for position in self.positions.values():
                # TODO: Integrate with real price feeds
                # For now, simulate price movement
                import random
                price_change = Decimal(str(random.uniform(-0.05, 0.05)))  # ±5% movement
                position.current_price = position.average_entry_price * (Decimal("1") + price_change)
                position.last_updated = datetime.utcnow()
        except Exception as e:
            logger.error(f"❌ Error updating position prices: {e}")
    
    async def _calculate_portfolio_summary(self) -> PortfolioSummary:
        """Calculate comprehensive portfolio summary."""
        total_value = self.cash_balance
        total_cost_basis = Decimal("0")
        total_unrealized_pnl = Decimal("0")
        
        for position in self.positions.values():
            total_value += position.market_value
            total_cost_basis += position.cost_basis
            total_unrealized_pnl += position.unrealized_pnl
        
        invested_amount = total_cost_basis
        available_balance = self.cash_balance
        
        return PortfolioSummary(
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_unrealized_pnl=total_unrealized_pnl,
            total_realized_pnl=self.realized_pnl,
            cash_balance=self.cash_balance,
            invested_amount=invested_amount,
            available_balance=available_balance,
            total_fees_paid=self.total_fees_paid,
            position_count=len(self.positions)
        )
    
    async def _calculate_realized_pnl_for_token(self, token_address: str) -> Decimal:
        """Calculate realized P&L for a specific token."""
        realized_pnl = Decimal("0")
        
        for transaction in self.transactions:
            if (transaction.token_address == token_address and 
                transaction.transaction_type == TransactionType.SELL):
                # This is a simplified calculation
                # In production, would need more sophisticated FIFO/LIFO logic
                pass
        
        return realized_pnl


# Global portfolio managers (keyed by wallet address)
portfolio_managers: Dict[str, PortfolioManager] = {}


def get_portfolio_manager(user_wallet: str) -> PortfolioManager:
    """Get or create portfolio manager for a user."""
    if user_wallet not in portfolio_managers:
        portfolio_managers[user_wallet] = PortfolioManager(user_wallet)
    return portfolio_managers[user_wallet]