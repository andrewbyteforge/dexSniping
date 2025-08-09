#!/usr/bin/env python3
"""
Add Final Missing Exception
File: add_final_exception.py

Add the missing InsufficientLiquidityError to exceptions.py
"""

from pathlib import Path


def add_insufficient_liquidity_error():
    """Add InsufficientLiquidityError to exceptions.py"""
    
    exceptions_file = Path("app/core/exceptions.py")
    
    if not exceptions_file.exists():
        print("❌ exceptions.py not found")
        return False
    
    try:
        content = exceptions_file.read_text(encoding='utf-8')
        
        # Check if it already exists
        if 'InsufficientLiquidityError' in content:
            print("✅ InsufficientLiquidityError already exists")
            return True
        
        # Find LiquidityError and add after it
        if 'class LiquidityError(TradingError):' in content:
            insert_point = content.find('class LiquidityError(TradingError):')
            # Find end of LiquidityError class
            next_class_start = content.find('\nclass ', insert_point + 1)
            
            new_exception = '''

class InsufficientLiquidityError(LiquidityError):
    """Insufficient liquidity for trade execution."""
    pass
'''
            
            if next_class_start != -1:
                content = content[:next_class_start] + new_exception + content[next_class_start:]
            else:
                content += new_exception
            
            # Add to __all__ list
            all_start = content.find("__all__ = [")
            if all_start != -1:
                all_end = content.find("]", all_start)
                if all_end != -1 and "'InsufficientLiquidityError'" not in content[all_start:all_end]:
                    # Insert before the closing bracket
                    content = content[:all_end] + "    'InsufficientLiquidityError',\n" + content[all_end:]
            
            exceptions_file.write_text(content, encoding='utf-8')
            print("✅ Added InsufficientLiquidityError to exceptions.py")
            return True
        else:
            print("❌ Could not find LiquidityError class")
            return False
            
    except Exception as e:
        print(f"❌ Error adding InsufficientLiquidityError: {e}")
        return False


def test_exception_import():
    """Test if the exception can be imported."""
    
    try:
        # Clear module cache
        import sys
        if 'app.core.exceptions' in sys.modules:
            del sys.modules['app.core.exceptions']
        
        from app.core.exceptions import InsufficientLiquidityError
        print("✅ InsufficientLiquidityError import successful")
        return True
    except Exception as e:
        print(f"❌ InsufficientLiquidityError import failed: {e}")
        return False


def main():
    """Add the final missing exception."""
    print("🔧 Adding Final Missing Exception")
    print("=" * 50)
    
    # Add the exception
    print("1. Adding InsufficientLiquidityError...")
    added = add_insufficient_liquidity_error()
    
    # Test import
    print("2. Testing exception import...")
    import_works = test_exception_import()
    
    print("\\n" + "=" * 50)
    print("Final Exception Fix Summary:")
    print("=" * 50)
    
    if added and import_works:
        print("✅ InsufficientLiquidityError added successfully!")
        print("\\nNext steps:")
        print("1. Run: python test_all_features.py")
        print("2. Should now work completely without any import errors")
        print("3. Get the full comprehensive system status report")
    else:
        print("❌ Failed to add InsufficientLiquidityError")
    
    return added and import_works


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)