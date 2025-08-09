#!/usr/bin/env python3
"""
Add SlippageExceededError
File: add_slippage_error.py

Add the missing SlippageExceededError to exceptions.py
"""

from pathlib import Path


def add_missing_slippage_exceptions():
    """Add missing slippage-related exceptions to exceptions.py"""
    
    exceptions_file = Path("app/core/exceptions.py")
    
    if not exceptions_file.exists():
        print("❌ exceptions.py not found")
        return False
    
    try:
        content = exceptions_file.read_text(encoding='utf-8')
        
        # List of missing exceptions to add
        missing_exceptions = [
            ('SlippageExceededError', 'SlippageError', 'Slippage tolerance exceeded during trade execution.'),
            ('MaxSlippageError', 'SlippageError', 'Maximum slippage limit exceeded.'),
            ('GasEstimationFailedError', 'GasEstimationError', 'Gas estimation failed for transaction.'),
            ('InsufficientGasError', 'GasEstimationError', 'Insufficient gas for transaction execution.'),
            ('TransactionFailedError', 'TransactionError', 'Transaction execution failed on blockchain.'),
            ('InvalidTokenError', 'TokenAnalysisError', 'Invalid or malformed token address.'),
            ('TokenMetadataError', 'TokenAnalysisError', 'Failed to retrieve token metadata.'),
            ('PriceFeedError', 'DataError', 'Price feed data retrieval failed.'),
            ('LiquidityPoolError', 'LiquidityError', 'Liquidity pool interaction failed.'),
            ('SwapExecutionError', 'ExecutionError', 'Swap execution failed.'),
        ]
        
        added_exceptions = []
        
        for exception_name, parent_class, description in missing_exceptions:
            if f'class {exception_name}' not in content:
                # Find the parent class and add after it
                parent_pattern = f'class {parent_class}'
                if parent_pattern in content:
                    insert_point = content.find(parent_pattern)
                    # Find end of parent class
                    next_class_start = content.find('\nclass ', insert_point + 1)
                    
                    new_exception = f'''

class {exception_name}({parent_class}):
    """{description}"""
    pass
'''
                    
                    if next_class_start != -1:
                        content = content[:next_class_start] + new_exception + content[next_class_start:]
                    else:
                        content += new_exception
                    
                    added_exceptions.append(exception_name)
                else:
                    # Fallback: add after TradingError
                    if 'class TradingError' in content:
                        insert_point = content.find('class TradingError')
                        next_class_start = content.find('\nclass ', insert_point + 1)
                        
                        new_exception = f'''

class {exception_name}(TradingError):
    """{description}"""
    pass
'''
                        
                        if next_class_start != -1:
                            content = content[:next_class_start] + new_exception + content[next_class_start:]
                        else:
                            content += new_exception
                        
                        added_exceptions.append(exception_name)
        
        # Add to __all__ list
        if added_exceptions:
            all_start = content.find("__all__ = [")
            if all_start != -1:
                all_end = content.find("]", all_start)
                if all_end != -1:
                    # Add all new exceptions to the list
                    new_entries = ""
                    for exception in added_exceptions:
                        if f"'{exception}'" not in content[all_start:all_end]:
                            new_entries += f"    '{exception}',\n"
                    
                    if new_entries:
                        content = content[:all_end] + new_entries + content[all_end:]
        
        # Write back to file
        exceptions_file.write_text(content, encoding='utf-8')
        
        if added_exceptions:
            print(f"✅ Added {len(added_exceptions)} missing exceptions:")
            for exc in added_exceptions:
                print(f"   - {exc}")
        else:
            print("✅ All exceptions already exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding exceptions: {e}")
        return False


def test_key_exception_imports():
    """Test importing key exceptions."""
    
    test_exceptions = [
        "SlippageExceededError",
        "InsufficientLiquidityError",
        "SlippageError",
        "TradingError",
        "DatabaseError"
    ]
    
    successful = 0
    
    for exc_name in test_exceptions:
        try:
            # Clear module cache
            import sys
            if 'app.core.exceptions' in sys.modules:
                del sys.modules['app.core.exceptions']
            
            exec(f"from app.core.exceptions import {exc_name}")
            print(f"✅ {exc_name} import successful")
            successful += 1
        except Exception as e:
            print(f"❌ {exc_name} import failed: {e}")
    
    return successful == len(test_exceptions)


def main():
    """Add missing slippage exceptions."""
    print("🔧 Adding Missing Slippage Exceptions")
    print("=" * 50)
    
    # Add missing exceptions
    print("1. Adding missing slippage-related exceptions...")
    added = add_missing_slippage_exceptions()
    
    # Test imports
    print("\\n2. Testing key exception imports...")
    import_works = test_key_exception_imports()
    
    print("\\n" + "=" * 50)
    print("Slippage Exception Fix Summary:")
    print("=" * 50)
    
    if added and import_works:
        print("✅ All missing exceptions added successfully!")
        print("\\nNext steps:")
        print("1. Run: python test_all_features.py")
        print("2. Should now work completely without any import errors")
        print("3. Finally get the comprehensive system status report!")
    else:
        print("❌ Failed to add some exceptions")
    
    return added and import_works


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)