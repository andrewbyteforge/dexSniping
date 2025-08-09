#!/usr/bin/env python3
"""
Add Missing ContractAnalysisError
File: add_missing_exception.py

Quick fix to add the missing ContractAnalysisError to exceptions.py
"""

from pathlib import Path


def add_missing_contract_analysis_error():
    """Add ContractAnalysisError to the exceptions file."""
    
    exceptions_file = Path("app/core/exceptions.py")
    
    if not exceptions_file.exists():
        print("❌ exceptions.py not found")
        return False
    
    try:
        content = exceptions_file.read_text(encoding='utf-8')
        
        # Check if ContractAnalysisError already exists
        if 'ContractAnalysisError' in content:
            print("✅ ContractAnalysisError already exists")
            return True
        
        # Find where to insert the new exception (after ContractError)
        if 'class ContractError(BlockchainError):' in content:
            # Insert after ContractError
            insert_point = content.find('class ContractError(BlockchainError):')
            next_class = content.find('\nclass ', insert_point + 1)
            
            if next_class != -1:
                # Insert new exception before next class
                new_exception = '''

class ContractAnalysisError(ContractError):
    """Smart contract analysis specific errors."""
    pass
'''
                content = content[:next_class] + new_exception + content[next_class:]
            else:
                # Insert at end of file
                new_exception = '''

class ContractAnalysisError(ContractError):
    """Smart contract analysis specific errors."""
    pass
'''
                content += new_exception
        else:
            # Insert after AIAnalysisError as fallback
            insert_point = content.find('class AIAnalysisError(TradingBotError):')
            if insert_point != -1:
                next_class = content.find('\nclass ', insert_point + 1)
                if next_class != -1:
                    new_exception = '''

class ContractAnalysisError(AIAnalysisError):
    """Smart contract analysis specific errors."""
    pass
'''
                    content = content[:next_class] + new_exception + content[next_class:]
        
        # Also update the __all__ list if it exists
        if '__all__ = [' in content:
            # Find the __all__ list and add the new exception
            all_start = content.find("__all__ = [")
            all_end = content.find("]", all_start)
            
            if all_start != -1 and all_end != -1:
                # Insert before the closing bracket
                all_content = content[all_start:all_end]
                if "'ContractAnalysisError'" not in all_content:
                    # Add to the list
                    insert_pos = all_end
                    new_entry = "    'ContractAnalysisError',\n    "
                    content = content[:insert_pos] + new_entry + content[insert_pos:]
        
        # Write back to file
        exceptions_file.write_text(content, encoding='utf-8')
        
        print("✅ Added ContractAnalysisError to exceptions.py")
        return True
        
    except Exception as e:
        print(f"❌ Error adding ContractAnalysisError: {e}")
        return False


def test_exception_import():
    """Test if the exception can be imported."""
    
    try:
        from app.core.exceptions import ContractAnalysisError
        print("✅ ContractAnalysisError import successful")
        return True
    except Exception as e:
        print(f"❌ ContractAnalysisError import failed: {e}")
        return False


def main():
    """Add the missing exception and test it."""
    print("🔧 Adding Missing ContractAnalysisError")
    print("=" * 50)
    
    # Add the exception
    print("1. Adding ContractAnalysisError to exceptions.py...")
    added = add_missing_contract_analysis_error()
    
    # Test the import
    print("2. Testing exception import...")
    import_works = test_exception_import()
    
    print("\n" + "=" * 50)
    print("Exception Fix Summary:")
    print("=" * 50)
    
    if added and import_works:
        print("✅ ContractAnalysisError added successfully!")
        print("\nNext steps:")
        print("1. Run: python test_all_features.py")
        print("2. Verify: All exception imports work")
    else:
        print("❌ Failed to add ContractAnalysisError")
        print("Manual addition may be required")
    
    return added and import_works


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)