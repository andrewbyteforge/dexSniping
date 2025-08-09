"""
Fix Persistence Manager Syntax Error
File: fix_persistence_syntax_error.py

Fixes the syntax error on line 458 of persistence_manager.py.
The error is likely caused by an incorrect line continuation character.
"""

import os
import re
from pathlib import Path


def fix_persistence_manager_syntax():
    """Fix the syntax error in persistence_manager.py."""
    
    print("🔧 Fixing PersistenceManager Syntax Error")
    print("=" * 50)
    
    # Find the persistence manager file
    persistence_file = Path("app/core/database/persistence_manager.py")
    
    if not persistence_file.exists():
        print("❌ Error: persistence_manager.py not found")
        print("💡 Make sure you're running from project root directory")
        return False
    
    try:
        # Read the file with proper encoding
        print("📖 Reading persistence_manager.py...")
        content = persistence_file.read_text(encoding='utf-8')
        
        # Split into lines for analysis
        lines = content.split('\n')
        print(f"✅ File loaded: {len(lines)} lines")
        
        # Check around line 458 for issues
        if len(lines) > 458:
            print(f"\n📍 Checking line 458...")
            problem_line = lines[457]  # 0-indexed
            print(f"Line 458: {repr(problem_line)}")
            
            # Common fixes for line continuation issues
            fixed_content = content
            fixes_applied = []
            
            # Fix 1: Remove stray backslashes not followed by newline
            stray_backslash_pattern = r'\\(?!\n|$)'
            if re.search(stray_backslash_pattern, content):
                fixed_content = re.sub(stray_backslash_pattern, '', fixed_content)
                fixes_applied.append("Removed stray backslashes")
            
            # Fix 2: Fix malformed SQL strings with backslashes
            # Replace invalid backslash sequences in SQL strings
            sql_fixes = [
                (r'\\n', '\\n'),  # Fix newline escapes
                (r'\\"', '"'),    # Fix quote escapes
                (r"\\t", " "),    # Fix tab escapes
                (r'\\', ''),      # Remove other backslashes
            ]
            
            for pattern, replacement in sql_fixes:
                if pattern in fixed_content:
                    fixed_content = fixed_content.replace(pattern, replacement)
                    fixes_applied.append(f"Fixed {pattern} sequences")
            
            # Fix 3: Ensure proper SQL string formatting
            # Look for common SQL syntax issues
            sql_string_fixes = [
                # Fix INDEX syntax issues
                (r'CREATE INDEX ([^"\']+)"([^"]*)"', r'CREATE INDEX \1"\2"'),
                # Fix table creation syntax
                (r'CREATE TABLE ([^"\']+)"([^"]*)"', r'CREATE TABLE \1"\2"'),
                # Fix incomplete SQL statements
                (r'"""\s*\\\s*$', '"""'),
            ]
            
            for pattern, replacement in sql_string_fixes:
                if re.search(pattern, fixed_content, re.MULTILINE):
                    fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.MULTILINE)
                    fixes_applied.append(f"Fixed SQL syntax pattern")
            
            # Fix 4: Common Python syntax issues
            python_fixes = [
                # Fix incomplete string literals
                (r'"""\s*$\s*\\', '"""'),
                # Fix method definitions with backslashes
                (r'def\s+([^(]+)\s*\\\s*\(', r'def \1('),
                # Fix import statements with backslashes
                (r'from\s+([^\s]+)\s*\\\s*import', r'from \1 import'),
            ]
            
            for pattern, replacement in python_fixes:
                if re.search(pattern, fixed_content, re.MULTILINE):
                    fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.MULTILINE)
                    fixes_applied.append(f"Fixed Python syntax")
            
            # Fix 5: Specific line 458 fix if it's in SQL creation
            lines_fixed = fixed_content.split('\n')
            if len(lines_fixed) > 458:
                line_458 = lines_fixed[457]
                if '\\' in line_458 and ('CREATE' in line_458 or 'INSERT' in line_458 or 'SELECT' in line_458):
                    # This is likely a SQL statement with incorrect escaping
                    lines_fixed[457] = line_458.replace('\\', '')
                    fixed_content = '\n'.join(lines_fixed)
                    fixes_applied.append("Fixed line 458 SQL syntax")
            
            # Check if we made any changes
            if fixed_content != content:
                print(f"\n🔨 Applying {len(fixes_applied)} fixes:")
                for fix in fixes_applied:
                    print(f"  ✅ {fix}")
                
                # Create backup
                backup_file = persistence_file.with_suffix('.py.backup')
                backup_file.write_text(content, encoding='utf-8')
                print(f"💾 Backup created: {backup_file}")
                
                # Write fixed content
                persistence_file.write_text(fixed_content, encoding='utf-8')
                print("✅ Fixed content written to file")
                
                # Verify the fix
                print("\n🔍 Verifying syntax...")
                try:
                    import ast
                    ast.parse(fixed_content)
                    print("✅ Python syntax is now valid!")
                    return True
                except SyntaxError as e:
                    print(f"❌ Syntax error still exists: {e}")
                    print(f"   Line {e.lineno}: {e.text}")
                    
                    # Restore backup if syntax is still invalid
                    persistence_file.write_text(content, encoding='utf-8')
                    print("🔄 Restored original file")
                    return False
            else:
                print("ℹ️ No obvious syntax issues found in the file")
                
                # Try to identify the specific issue
                try:
                    import ast
                    ast.parse(content)
                    print("✅ Python syntax appears to be valid")
                    print("💡 The error might be in imports or runtime issues")
                except SyntaxError as e:
                    print(f"❌ Confirmed syntax error: {e}")
                    print(f"   Line {e.lineno}: {e.text}")
                    
                    # Try to fix the specific line
                    if e.lineno and e.lineno <= len(lines):
                        error_line = lines[e.lineno - 1]
                        print(f"   Problematic line: {repr(error_line)}")
                        
                        # Manual fix for common issues
                        if '\\' in error_line and not error_line.endswith('\\'):
                            fixed_line = error_line.replace('\\', '')
                            lines[e.lineno - 1] = fixed_line
                            fixed_content = '\n'.join(lines)
                            
                            persistence_file.write_text(fixed_content, encoding='utf-8')
                            print(f"🔨 Fixed line {e.lineno} by removing backslashes")
                            return True
                
                return False
        else:
            print("❌ File has fewer than 458 lines")
            return False
            
    except Exception as e:
        print(f"❌ Error reading/fixing file: {e}")
        return False


def test_persistence_manager():
    """Test the persistence manager after fixes."""
    print("\n🧪 Testing PersistenceManager...")
    
    try:
        # Try to import and instantiate
        import sys
        import os
        sys.path.insert(0, os.getcwd())
        
        from app.core.database.persistence_manager import PersistenceManager
        
        # Create instance
        pm = PersistenceManager()
        print("✅ PersistenceManager imported and instantiated successfully")
        
        # Test basic methods
        status = pm.get_database_status()
        print("✅ get_database_status() method works")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error still exists: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        return False


if __name__ == "__main__":
    print("PersistenceManager Syntax Fix")
    print("=" * 30)
    
    # Fix the syntax error
    if fix_persistence_manager_syntax():
        print("\n" + "=" * 50)
        print("✅ SYNTAX FIX COMPLETED")
        
        # Test the fix
        if test_persistence_manager():
            print("✅ PersistenceManager is working correctly")
            print("\n📋 Next steps:")
            print("1. Run the original command again:")
            print("   python fix_persistence_manager_methods.py")
            print("2. If successful, continue with application development")
        else:
            print("❌ PersistenceManager still has issues")
            print("💡 Check the specific error messages above")
    else:
        print("\n" + "=" * 50)
        print("❌ SYNTAX FIX FAILED")
        print("💡 Manual intervention may be required")
        print("💡 Check the specific error messages above")