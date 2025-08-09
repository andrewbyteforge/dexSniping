"""
Fix Missing Classes - Quick Patch
File: fix_missing_classes.py

Adds the missing classes that are causing import failures in Phase 4C tests.
"""

import os
from pathlib import Path

def fix_trading_engine_imports():
    """Add missing TradingSignal class to trading_engine.py"""
    print("Fixing trading_engine.py imports...")
    
    trading_engine_path = Path("app/core/trading/trading_engine.py")
    
    if not trading_engine_path.exists():
        print(f"❌ {trading_engine_path} not found!")
        return False
    
    try:
        # Read current content
        with open(trading_engine_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if TradingSignal is already defined
        if "class TradingSignal" in content:
            print("✅ TradingSignal already exists in trading_engine.py")
            return True
        
        # Add TradingSignal class near the top of the file (after imports)
        trading_signal_class = '''
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import Optional

class OrderIntent(str, Enum):
    """Order intent enumeration."""
    BUY = "buy"
    SELL = "sell"

class StrategyType(str, Enum):
    """Trading strategy types."""
    ARBITRAGE = "arbitrage"
    TREND_FOLLOWING = "trend_following"
    MOMENTUM = "momentum"

@dataclass
class TradingSignal:
    """Trading signal data structure."""
    signal_id: str
    strategy_type: StrategyType
    token_address: str
    symbol: str
    intent: OrderIntent
    confidence: float
    suggested_amount: Decimal
    reasoning: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_expired(self) -> bool:
        """Check if signal has expired."""
        return datetime.utcnow() > self.expires_at

'''
        
        # Find a good place to insert the class (after imports, before main classes)
        lines = content.split('\n')
        insert_index = 0
        
        # Find the end of imports
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                insert_index = i + 1
            elif line.strip() == '' and insert_index > 0:
                insert_index = i + 1
                break
            elif line.startswith('class ') and insert_index > 0:
                insert_index = i
                break
        
        # Insert the TradingSignal class
        lines.insert(insert_index, trading_signal_class)
        
        # Write back to file
        with open(trading_engine_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Added TradingSignal class to trading_engine.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix trading_engine.py: {e}")
        return False

def fix_base_chain_imports():
    """Add missing TokenInfo class to base_chain.py"""
    print("Fixing base_chain.py imports...")
    
    base_chain_path = Path("app/core/blockchain/base_chain.py")
    
    if not base_chain_path.exists():
        print(f"❌ {base_chain_path} not found!")
        return False
    
    try:
        # Read current content
        with open(base_chain_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if TokenInfo is already defined
        if "class TokenInfo" in content:
            print("✅ TokenInfo already exists in base_chain.py")
            return True
        
        # Add TokenInfo class
        token_info_class = '''
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class TokenInfo:
    """Token information data structure."""
    address: str
    symbol: str
    name: str
    decimals: int
    total_supply: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    creator_address: Optional[str] = None
    is_verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LiquidityInfo:
    """Liquidity information data structure."""
    pool_address: str
    token0: str
    token1: str
    reserves0: Decimal
    reserves1: Decimal
    total_liquidity_usd: Decimal
    price_per_token: Decimal
    last_updated: datetime = field(default_factory=datetime.utcnow)

'''
        
        # Find a good place to insert the classes
        lines = content.split('\n')
        insert_index = 0
        
        # Find the end of imports
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                insert_index = i + 1
            elif line.strip() == '' and insert_index > 0:
                insert_index = i + 1
                break
            elif line.startswith('class ') and insert_index > 0:
                insert_index = i
                break
        
        # Insert the classes
        lines.insert(insert_index, token_info_class)
        
        # Write back to file
        with open(base_chain_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ Added TokenInfo and LiquidityInfo classes to base_chain.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix base_chain.py: {e}")
        return False

def fix_logger_levels():
    """Fix the logger configuration to handle custom levels properly."""
    print("Fixing logger level configuration...")
    
    logger_path = Path("app/utils/logger.py")
    
    # Enhanced logger that handles any level name
    enhanced_logger = '''"""
Enhanced Logger Setup - All Levels Supported
File: app/utils/logger.py

Logger that supports any level name and avoids Unicode issues.
"""

import logging
import sys
from typing import Optional

def setup_logger(
    name: str, 
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with flexible level support.
    
    Args:
        name: Logger name (can be any string)
        level: Logging level
        format_string: Custom format string
        
    Returns:
        logging.Logger: Configured logger
    """
    if format_string is None:
        format_string = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    
    # Convert level to standard logging level if it's a string
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with UTF-8 encoding
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set UTF-8 encoding for the handler if possible
    if hasattr(handler.stream, 'reconfigure'):
        try:
            handler.stream.reconfigure(encoding='utf-8')
        except Exception:
            pass
    
    # Create formatter
    formatter = logging.Formatter(format_string, datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

# Alias for backward compatibility
def get_logger(name: str) -> logging.Logger:
    """Get logger with default configuration."""
    return setup_logger(name)
'''
    
    try:
        with open(logger_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_logger)
        
        print("✅ Enhanced logger.py to handle any level name")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix logger.py: {e}")
        return False

def main():
    """Fix all missing classes and logger issues."""
    print("Fixing Missing Classes and Logger Issues")
    print("=" * 50)
    
    success_count = 0
    total_fixes = 3
    
    # Fix trading engine
    if fix_trading_engine_imports():
        success_count += 1
    
    # Fix base chain
    if fix_base_chain_imports():
        success_count += 1
    
    # Fix logger
    if fix_logger_levels():
        success_count += 1
    
    print("\n" + "=" * 50)
    if success_count == total_fixes:
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("✅ TradingSignal class added to trading_engine.py")
        print("✅ TokenInfo class added to base_chain.py") 
        print("✅ Logger enhanced to handle any level")
        print("\nNext: Run the simplified test to verify structure")
        print("Command: python tests/test_phase_4c_simple.py")
        return True
    else:
        print(f"⚠️ Applied {success_count}/{total_fixes} fixes")
        print("Some issues may remain - check the output above")
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)