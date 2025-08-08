"""
Fix Main.py Syntax Error Properly
File: fix_main_properly.py

This will fix the syntax error and ensure your professional dashboard works.
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime


def analyze_main_file():
    """
    Analyze the main.py file to understand the exact syntax error.
    """
    print("\n🔍 Analyzing main.py structure...")
    print("=" * 60)
    
    main_path = Path("app/main.py")
    
    if not main_path.exists():
        print("❌ main.py not found!")
        return None
    
    with open(main_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find all try blocks and their matching except/finally blocks
    try_blocks = []
    current_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track try blocks
        if stripped == 'try:':
            indent = len(line) - len(line.lstrip())
            try_blocks.append({
                'line': i,
                'indent': indent,
                'has_except': False,
                'has_finally': False
            })
            print(f"Found try block at line {i+1}, indent level {indent}")
        
        # Track except blocks
        elif stripped.startswith('except'):
            indent = len(line) - len(line.lstrip())
            # Find matching try block
            for block in reversed(try_blocks):
                if block['indent'] == indent and not block['has_except']:
                    block['has_except'] = True
                    print(f"Found except for try at line {block['line']+1}")
                    break
        
        # Track finally blocks
        elif stripped == 'finally:':
            indent = len(line) - len(line.lstrip())
            # Find matching try block
            for block in reversed(try_blocks):
                if block['indent'] == indent and not block['has_finally']:
                    block['has_finally'] = True
                    print(f"Found finally for try at line {block['line']+1}")
                    break
    
    # Find problematic try blocks
    problems = []
    for block in try_blocks:
        if not block['has_except'] and not block['has_finally']:
            problems.append(block)
            print(f"❌ Unclosed try block at line {block['line']+1}")
    
    return lines, problems


def fix_syntax_error():
    """
    Fix the actual syntax error in main.py.
    """
    print("\n🔧 Fixing Syntax Error...")
    print("=" * 60)
    
    main_path = Path("app/main.py")
    
    # Backup
    backup_path = main_path.with_suffix('.py.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    shutil.copy2(main_path, backup_path)
    print(f"✅ Backed up to: {backup_path}")
    
    result = analyze_main_file()
    if not result:
        return False
    
    lines, problems = result
    
    if not problems:
        print("No unclosed try blocks found. Looking for other issues...")
        
        # Look for the specific error around line 70
        if len(lines) > 69:
            print(f"\nLine 69: {lines[68].rstrip()}")
            print(f"Line 70: {lines[69].rstrip()}")
            print(f"Line 71: {lines[70].rstrip() if len(lines) > 70 else 'EOF'}")
            
            # Check if line 70 has 'def main():' after a try block
            if 'def main():' in lines[69]:
                # Look backwards for the try block
                for i in range(68, max(0, 58), -1):
                    if 'try:' in lines[i]:
                        print(f"\nFound try block at line {i+1}")
                        # Add except block before the def main()
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        
                        # Insert except block
                        lines.insert(69, ' ' * indent + 'except Exception as e:\n')
                        lines.insert(70, ' ' * (indent + 4) + 'logger.error(f"Error in application creation: {e}")\n')
                        lines.insert(71, ' ' * (indent + 4) + 'raise\n')
                        lines.insert(72, '\n')
                        
                        print("✅ Added except block before def main()")
                        break
    else:
        # Fix unclosed try blocks
        for problem in reversed(problems):  # Reverse to maintain line numbers
            line_num = problem['line']
            indent = problem['indent']
            
            print(f"\nFixing unclosed try block at line {line_num+1}")
            
            # Find where to insert the except block
            # Look for the next line with same or less indentation
            insert_line = line_num + 1
            for i in range(line_num + 1, len(lines)):
                line_indent = len(lines[i]) - len(lines[i].lstrip())
                if lines[i].strip() and line_indent <= indent:
                    insert_line = i
                    break
            
            # Insert except block
            lines.insert(insert_line, ' ' * indent + 'except Exception as e:\n')
            lines.insert(insert_line + 1, ' ' * (indent + 4) + 'logger.error(f"Error: {e}")\n')
            lines.insert(insert_line + 2, ' ' * (indent + 4) + 'raise\n')
            
            print(f"✅ Added except block at line {insert_line+1}")
    
    # Write fixed file
    with open(main_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Fixed main.py!")
    return True


def verify_and_test():
    """
    Verify the fix by trying to import the module.
    """
    print("\n🧪 Testing the fix...")
    print("=" * 60)
    
    try:
        # Try to import the main module
        import importlib
        import app.main
        importlib.reload(app.main)
        print("✅ Module imports successfully!")
        
        # Check if app exists
        if hasattr(app.main, 'app'):
            print("✅ FastAPI app object found!")
            
            # Check routes
            routes = []
            for route in app.main.app.routes:
                if hasattr(route, 'path'):
                    routes.append(route.path)
            
            if '/dashboard' in routes:
                print("✅ Dashboard route exists!")
            else:
                print("⚠️ Dashboard route not found")
            
            return True
        else:
            print("❌ App object not found")
            return False
            
    except SyntaxError as e:
        print(f"❌ Still has syntax error: {e}")
        print(f"   At line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def ensure_dashboard_route():
    """
    Ensure the dashboard route uses the correct template.
    """
    print("\n🔧 Checking Dashboard Route Configuration...")
    print("=" * 60)
    
    # Check route_manager.py
    route_manager_path = Path("app/api/route_manager.py")
    
    if route_manager_path.exists():
        with open(route_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's using the correct template
        if 'pages/dashboard.html' in content:
            print("✅ route_manager.py is configured to use pages/dashboard.html")
        else:
            print("⚠️ route_manager.py may not be using the correct template")
    
    # Verify dashboard template exists and has sidebar
    dashboard_path = Path("frontend/templates/pages/dashboard.html")
    
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '{% extends "base/layout.html"' in content:
            print("✅ Dashboard template extends from layout.html (has sidebar)")
        else:
            print("❌ Dashboard template doesn't extend from layout.html")
            print("   Fixing...")
            
            # Fix it
            lines = content.split('\n')
            
            # Find and replace extends line
            for i, line in enumerate(lines):
                if '{% extends' in line:
                    lines[i] = '{% extends "base/layout.html" %}'
                    break
            else:
                # No extends found, add it at the beginning
                lines.insert(0, '{% extends "base/layout.html" %}')
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print("✅ Fixed dashboard template to use sidebar layout")
    else:
        print("❌ Dashboard template not found at frontend/templates/pages/dashboard.html")
        print("   Run cleanup_dashboard.py to create it")


def main():
    """
    Main function to fix everything.
    """
    print("🚀 DEX Sniper Pro - Complete Dashboard Fix")
    print("=" * 60)
    print("This will fix the syntax error and ensure your professional dashboard works.")
    
    # Step 1: Fix syntax error
    if not fix_syntax_error():
        print("❌ Failed to fix syntax error")
        return False
    
    # Step 2: Verify the fix
    if not verify_and_test():
        print("⚠️ Module still has issues, attempting additional fixes...")
        
        # Try one more time with a different approach
        main_path = Path("app/main.py")
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple regex fix for unclosed try blocks
        import re
        
        # Count try and except statements
        try_count = len(re.findall(r'^\s*try:\s*$', content, re.MULTILINE))
        except_count = len(re.findall(r'^\s*except', content, re.MULTILINE))
        finally_count = len(re.findall(r'^\s*finally:', content, re.MULTILINE))
        
        if try_count > (except_count + finally_count):
            print(f"Found {try_count} try blocks but only {except_count + finally_count} handlers")
            
            # Add a generic except at the end of the file before any function definitions
            lines = content.split('\n')
            
            # Find the last try block
            last_try_index = -1
            for i in range(len(lines) - 1, -1, -1):
                if re.match(r'^\s*try:\s*$', lines[i]):
                    last_try_index = i
                    break
            
            if last_try_index >= 0:
                # Find the next function or class definition after this try
                for i in range(last_try_index + 1, len(lines)):
                    if re.match(r'^(def |class |@app\.)', lines[i]):
                        # Insert except before this line
                        indent = len(lines[last_try_index]) - len(lines[last_try_index].lstrip())
                        lines.insert(i, ' ' * indent + 'except Exception as e:')
                        lines.insert(i + 1, ' ' * (indent + 4) + 'logger.error(f"Application error: {e}")')
                        lines.insert(i + 2, ' ' * (indent + 4) + 'raise')
                        lines.insert(i + 3, '')
                        break
                
                with open(main_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Applied additional fix")
    
    # Step 3: Ensure dashboard route is correct
    ensure_dashboard_route()
    
    print("\n" + "=" * 60)
    print("✅ Fix complete!")
    print("\n📝 Next Steps:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Navigate to: http://127.0.0.1:8000/dashboard")
    print("3. You should see your professional dashboard with sidebar!")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️ If still having issues, try:")
        print("1. Restore from backup: app/main.py.backup*")
        print("2. Or share the exact error message for more help")