"""
Fix Indentation Error in route_manager.py
File: fix_indentation.py

Fix the indentation error at line 138.
"""

import os
from pathlib import Path
import shutil
from datetime import datetime


def fix_indentation_error():
    """
    Fix the indentation error in route_manager.py.
    """
    print("\n🔧 Fixing Indentation Error in route_manager.py...")
    print("=" * 60)
    
    route_manager_path = Path("app/api/route_manager.py")
    
    if not route_manager_path.exists():
        print("❌ route_manager.py not found!")
        return False
    
    # Backup
    backup_path = route_manager_path.with_suffix('.py.indent_backup')
    shutil.copy2(route_manager_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")
    
    with open(route_manager_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check around line 138 for indentation issues
    if len(lines) > 137:
        print(f"\nChecking around line 138...")
        for i in range(max(0, 135), min(len(lines), 145)):
            print(f"Line {i+1}: {repr(lines[i][:50])}")
    
    # Fix common indentation issues
    fixed = False
    
    # Look for the problem area
    for i in range(max(0, 125), min(len(lines), 150)):
        line = lines[i]
        
        # Check for mixed tabs and spaces
        if '\t' in line:
            lines[i] = line.replace('\t', '    ')  # Replace tabs with 4 spaces
            print(f"Fixed tabs at line {i+1}")
            fixed = True
        
        # Check for inconsistent indentation around line 138
        if i == 137:  # Line 138 (0-indexed)
            # Get the indentation of surrounding lines
            prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip()) if i > 0 else 0
            curr_indent = len(line) - len(line.lstrip())
            next_indent = len(lines[i+1]) - len(lines[i+1].lstrip()) if i < len(lines)-1 else 0
            
            print(f"\nLine 137 indent: {prev_indent}")
            print(f"Line 138 indent: {curr_indent}")
            print(f"Line 139 indent: {next_indent}")
            
            # Fix if current line has unexpected indent
            if line.strip() and curr_indent % 4 != 0:
                # Round to nearest multiple of 4
                new_indent = round(curr_indent / 4) * 4
                lines[i] = ' ' * new_indent + line.lstrip()
                print(f"Fixed indent at line 138: {curr_indent} -> {new_indent}")
                fixed = True
    
    # Write the fixed file
    with open(route_manager_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    if fixed:
        print("✅ Fixed indentation issues")
    else:
        print("⚠️ No obvious indentation issues found")
    
    return True


def validate_python_syntax():
    """
    Validate Python syntax of route_manager.py.
    """
    print("\n🧪 Validating Python Syntax...")
    print("=" * 60)
    
    route_manager_path = Path("app/api/route_manager.py")
    
    try:
        with open(route_manager_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Try to compile the code
        compile(code, str(route_manager_path), 'exec')
        print("✅ Python syntax is valid!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
        print(f"   Text: {e.text}")
        
        # Try to fix the specific error
        if e.lineno:
            with open(route_manager_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if e.lineno <= len(lines):
                problem_line = lines[e.lineno - 1]
                print(f"\nProblem line {e.lineno}: {repr(problem_line)}")
                
                # Common fixes
                if e.msg == "unexpected indent":
                    # Fix the indentation
                    # Get expected indent from previous non-empty line
                    expected_indent = 0
                    for i in range(e.lineno - 2, max(0, e.lineno - 10), -1):
                        if lines[i].strip():
                            expected_indent = len(lines[i]) - len(lines[i].lstrip())
                            # If previous line ends with :, increase indent
                            if lines[i].rstrip().endswith(':'):
                                expected_indent += 4
                            break
                    
                    lines[e.lineno - 1] = ' ' * expected_indent + problem_line.lstrip()
                    
                    with open(route_manager_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    print(f"✅ Fixed indentation at line {e.lineno}")
                    return validate_python_syntax()  # Recursive check
        
        return False
        
    except Exception as e:
        print(f"❌ Error validating syntax: {e}")
        return False


def restore_working_route_manager():
    """
    Restore a working version of route_manager.py.
    """
    print("\n🔧 Restoring Working route_manager.py...")
    print("=" * 60)
    
    # Look for backups
    backups = list(Path("app/api").glob("route_manager.py.backup*"))
    backups.extend(list(Path("app/api").glob("route_manager.py.*backup")))
    
    if backups:
        # Sort by modification time, newest first
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print("Found backups:")
        for i, backup in enumerate(backups[:5]):  # Show last 5 backups
            mod_time = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"{i+1}. {backup.name} - {mod_time}")
        
        choice = input("\nSelect backup to restore (1-5) or 'skip': ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= min(5, len(backups)):
            selected = backups[int(choice) - 1]
            
            # Test if the backup has valid syntax
            try:
                with open(selected, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(selected), 'exec')
                
                # Backup current broken version
                current = Path("app/api/route_manager.py")
                broken_backup = current.with_suffix('.py.broken_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
                shutil.copy2(current, broken_backup)
                
                # Restore the backup
                shutil.copy2(selected, current)
                print(f"✅ Restored from {selected.name}")
                return True
                
            except SyntaxError:
                print(f"❌ Selected backup also has syntax errors")
    
    print("No suitable backup found")
    return False


def main():
    """
    Main function to fix indentation error.
    """
    print("🚀 DEX Sniper Pro - Fix Indentation Error")
    print("=" * 60)
    
    # Try to fix indentation
    fix_indentation_error()
    
    # Validate syntax
    if validate_python_syntax():
        print("\n" + "=" * 60)
        print("✅ All syntax errors fixed!")
        print("\n📝 Start your server now:")
        print("   uvicorn app.main:app --reload")
        print("\nThen navigate to:")
        print("   http://127.0.0.1:8000/dashboard")
    else:
        print("\n⚠️ Syntax errors remain")
        print("\nWould you like to restore from a backup?")
        
        if input("Restore from backup? (yes/no): ").lower() == 'yes':
            if restore_working_route_manager():
                print("\n✅ Restored working version!")
                print("Start your server: uvicorn app.main:app --reload")
            else:
                print("\n❌ Could not restore")
                print("You may need to manually fix route_manager.py")
                print("Check line 138 for indentation issues")


if __name__ == "__main__":
    main()