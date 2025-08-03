"""
Core Exceptions
File: app/core/exceptions.py

Custom exceptions for the trading platform.
"""


class TradingError(Exception):
    """Base exception for trading operations."""
    pass


class WalletError(TradingError):
    """Wallet-related errors."""
    pass


class DEXError(TradingError):
    """DEX integration errors."""
    pass


class InsufficientFundsError(TradingError):
    """Insufficient funds for operation."""
    pass


class InvalidAddressError(WalletError):
    """Invalid wallet address format."""
    pass


class TransactionError(TradingError):
    """Transaction execution errors."""
    pass


class SecurityError(WalletError):
    """Security-related errors."""
    pass


class RiskLimitExceededError(TradingError):
    """Risk limit exceeded."""
    pass


class StrategyError(TradingError):
    """Strategy execution errors."""
    pass


class PortfolioError(TradingError):
    """Portfolio management errors."""
    pass


class OrderExecutionError(TradingError):
    """Order execution errors."""
    pass


class InvalidOrderError(TradingError):
    """Invalid order parameters."""
    pass


class SlippageExceededError(TradingError):
    """Slippage exceeded acceptable limits."""
    pass


class InsufficientLiquidityError(DEXError):
    """Insufficient liquidity for trade."""
    pass
