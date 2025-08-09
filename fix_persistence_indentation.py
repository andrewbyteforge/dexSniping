"""
Fix Persistence Manager Indentation Error
File: fix_persistence_indentation.py

Fixes the indentation error around line 458-460 in persistence_manager.py.
The error shows line 458 has '\n' and line 460 has unexpected indent.
"""

import os
import re
from pathlib import Path


def fix_persistence_indentation():
    """Fix the indentation error in persistence_manager.py."""
    
    print("🔧 Fixing PersistenceManager Indentation Error")
    print("=" * 50)
    
    persistence_file = Path("app/core/database/persistence_manager.py")
    
    if not persistence_file.exists():
        print("❌ Error: persistence_manager.py not found")
        return False
    
    try:
        # Read the file
        print("📖 Reading persistence_manager.py...")
        content = persistence_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        print(f"✅ File loaded: {len(lines)} lines")
        
        # Examine the problematic area around line 458-460
        print(f"\n📍 Examining lines 455-465...")
        for i in range(454, min(466, len(lines))):
            line_num = i + 1
            line = lines[i]
            print(f"  {line_num:3d}: {repr(line)}")
        
        # The issue is likely:
        # - Line 458 contains just '\n' (probably should be empty or removed)
        # - Line 460 has unexpected indent for get_database_status method
        
        # Let's fix this step by step
        fixed_lines = lines.copy()
        fixes_applied = []
        
        # Fix 1: Remove or fix line 458 if it's just '\n'
        if len(fixed_lines) > 457:
            line_458 = fixed_lines[457]  # 0-indexed
            if line_458.strip() == '' or line_458 == '\\n':
                # This line should probably be completely empty
                fixed_lines[457] = ''
                fixes_applied.append("Fixed line 458 (removed stray content)")
        
        # Fix 2: Check indentation consistency around the get_database_status method
        # Find the get_database_status method definition
        for i, line in enumerate(fixed_lines):
            if 'def get_database_status(self)' in line:
                method_line = i
                print(f"\n🔍 Found get_database_status at line {method_line + 1}")
                
                # Check if this method is properly indented as a class method
                # It should have 4 spaces (class method level)
                if not line.startswith('    def '):
                    # Fix the indentation
                    fixed_lines[i] = '    ' + line.lstrip()
                    fixes_applied.append(f"Fixed indentation for line {method_line + 1}")
                
                # Check the lines before this method
                # There should be proper spacing and no stray content
                prev_line_idx = method_line - 1
                if prev_line_idx >= 0:
                    prev_line = fixed_lines[prev_line_idx]
                    
                    # If previous line has weird content, clean it up
                    if prev_line.strip() == '\\n' or prev_line.strip() == 'n':
                        fixed_lines[prev_line_idx] = ''
                        fixes_applied.append(f"Cleaned up line {prev_line_idx + 1}")
                
                # Check if there are multiple empty lines before the method
                # Clean up excessive empty lines
                empty_count = 0
                for j in range(method_line - 1, -1, -1):
                    if fixed_lines[j].strip() == '':
                        empty_count += 1
                    else:
                        break
                
                if empty_count > 2:
                    # Remove excessive empty lines, keep only 1
                    for j in range(method_line - empty_count, method_line - 1):
                        if j >= 0:
                            fixed_lines[j] = ''
                    fixes_applied.append("Cleaned up excessive empty lines")
                
                break
        
        # Fix 3: Look for any other indentation issues in the class
        # All methods should start with exactly 4 spaces
        in_class = False
        class_indent_level = 0
        
        for i, line in enumerate(fixed_lines):
            stripped = line.strip()
            
            # Track if we're inside the PersistenceManager class
            if stripped.startswith('class PersistenceManager'):
                in_class = True
                class_indent_level = len(line) - len(line.lstrip())
                continue
            elif stripped.startswith('class ') and in_class:
                in_class = False
                continue
            
            if in_class and stripped.startswith('def '):
                # This is a method definition, should be indented 4 spaces from class
                expected_indent = class_indent_level + 4
                current_indent = len(line) - len(line.lstrip())
                
                if current_indent != expected_indent:
                    # Fix the indentation
                    fixed_lines[i] = ' ' * expected_indent + stripped
                    fixes_applied.append(f"Fixed method indentation at line {i + 1}")
        
        # Fix 4: Clean up any remaining stray backslash-n sequences
        for i, line in enumerate(fixed_lines):
            if line.strip() == '\\n' or line.strip() == 'n':
                fixed_lines[i] = ''
                fixes_applied.append(f"Cleaned up stray content at line {i + 1}")
        
        # Apply fixes if any were made
        if fixes_applied:
            fixed_content = '\n'.join(fixed_lines)
            
            print(f"\n🔨 Applying {len(fixes_applied)} fixes:")
            for fix in fixes_applied:
                print(f"  ✅ {fix}")
            
            # Create backup
            backup_file = persistence_file.with_suffix('.py.backup2')
            backup_file.write_text(content, encoding='utf-8')
            print(f"💾 Backup created: {backup_file}")
            
            # Write fixed content
            persistence_file.write_text(fixed_content, encoding='utf-8')
            print("✅ Fixed content written to file")
            
            # Show the fixed area
            fixed_file_lines = fixed_content.split('\n')
            print(f"\n📍 Lines 455-465 after fix:")
            for i in range(454, min(466, len(fixed_file_lines))):
                line_num = i + 1
                line = fixed_file_lines[i]
                print(f"  {line_num:3d}: {repr(line)}")
            
            # Verify syntax
            print("\n🔍 Verifying syntax...")
            try:
                import ast
                ast.parse(fixed_content)
                print("✅ Python syntax is now valid!")
                return True
            except SyntaxError as e:
                print(f"❌ Syntax error still exists: {e}")
                print(f"   Line {e.lineno}: {e.text}")
                return False
        else:
            print("\nℹ️ No indentation issues found to fix")
            
            # Let's try a more aggressive approach - rebuild the problematic section
            print("🔨 Attempting aggressive fix...")
            return aggressive_fix_persistence(persistence_file, content)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def aggressive_fix_persistence(persistence_file, original_content):
    """More aggressive fix by rebuilding the problematic section."""
    
    lines = original_content.split('\n')
    
    # Find the get_database_status method and rebuild it properly
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # If we hit the problematic area around line 458
        if i >= 455 and i <= 465:
            # Skip any malformed lines and rebuild this section
            if 'def get_database_status(self)' in line:
                # Add proper spacing before method
                if new_lines and new_lines[-1].strip() != '':
                    new_lines.append('')
                
                # Add the method with proper indentation
                new_lines.append('    def get_database_status(self) -> Dict[str, Any]:')
                i += 1
                continue
            elif line.strip() in ['\\n', 'n', ''] and i < 460:
                # Skip malformed lines before the method
                i += 1
                continue
        
        # Add normal lines
        new_lines.append(line)
        i += 1
    
    # Write the fixed content
    fixed_content = '\n'.join(new_lines)
    
    try:
        import ast
        ast.parse(fixed_content)
        
        # Create backup
        backup_file = persistence_file.with_suffix('.py.aggressive_backup')
        backup_file.write_text(original_content, encoding='utf-8')
        
        # Write fix
        persistence_file.write_text(fixed_content, encoding='utf-8')
        
        print("✅ Aggressive fix applied successfully!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Aggressive fix failed: {e}")
        return False


def test_import():
    """Test if the persistence manager can be imported."""
    print("\n🧪 Testing import...")
    
    try:
        import sys
        import os
        
        # Add current directory to path
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        # Try to import
        from app.core.database.persistence_manager import PersistenceManager
        print("✅ Import successful!")
        
        # Try to instantiate
        pm = PersistenceManager()
        print("✅ Instantiation successful!")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        return False


if __name__ == "__main__":
    print("PersistenceManager Indentation Fix")
    print("=" * 35)
    
    if fix_persistence_indentation():
        print("\n" + "=" * 50)
        print("✅ INDENTATION FIX COMPLETED")
        
        if test_import():
            print("✅ PersistenceManager is working!")
            print("\n📋 Next steps:")
            print("1. Run: python fix_persistence_manager_methods.py")
            print("2. Continue with development")
        else:
            print("❌ Still has issues - check error details above")
    else:
        print("\n" + "=" * 50)
        print("❌ INDENTATION FIX FAILED")
        print("💡 Manual file editing may be required")
        