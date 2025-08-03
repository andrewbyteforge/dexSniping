"""
Phase 3B DEX Integration Module
"""

from .uniswap_integration import (
    UniswapV2Integration,
    UniswapV3Integration, 
    DEXAggregator,
    LiquidityPool,
    PriceData,
    ArbitrageOpportunity
)

from .dex_manager import (
    DEXManager,
    TradingPair,
    TradingStrategy,
    PortfolioPosition
)

__all__ = [
    'UniswapV2Integration',
    'UniswapV3Integration',
    'DEXAggregator',
    'LiquidityPool',
    'PriceData',
    'ArbitrageOpportunity',
    'DEXManager',
    'TradingPair',
    'TradingStrategy',
    'PortfolioPosition'
]
