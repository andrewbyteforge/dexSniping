"""
Package Initialization Files
File: create_init_files.py

Creates all necessary __init__.py files for the refactored package structure.
Run this script to ensure proper Python package initialization.
"""

import os
from pathlib import Path

def create_init_files():
    """Create all necessary __init__.py files."""
    print("Creating __init__.py files for refactored package structure...")
    
    # Define all packages that need __init__.py files
    packages = [
        "app",
        "app/core",
        "app/api", 
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/utils",
        "app/schemas",
        "app/core/blockchain",
        "app/core/wallet",
        "app/core/trading",
        "app/core/dex",
        "app/core/database",
        "app/core/config"
    ]
    
    created_files = []
    existing_files = []
    
    for package in packages:
        init_file = Path(package) / "__init__.py"
        
        if init_file.exists():
            existing_files.append(str(init_file))
            print(f"✅ {init_file} (already exists)")
        else:
            # Create directory if it doesn't exist
            init_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create appropriate __init__.py content
            if package == "app":
                content = '''"""
DEX Sniper Pro - AI-Powered Trading Bot
Main application package.
"""

__version__ = "4.1.0-beta"
__phase__ = "4C - AI Risk Assessment Integration"
'''
            elif package == "app/core":
                content = '''"""
Core application components.
Contains business logic, trading engines, and system managers.
"""
'''
            elif package == "app/api":
                content = '''"""
API layer components.
Contains REST API endpoints and route management.
"""
'''
            elif package == "app/utils":
                content = '''"""
Utility functions and helpers.
Contains logging, configuration, and common utilities.
"""
'''
            else:
                package_name = package.split("/")[-1].replace("_", " ").title()
                content = f'"""{package_name} package."""\n'
            
            init_file.write_text(content)
            created_files.append(str(init_file))
            print(f"✅ {init_file} (created)")
    
    print(f"\n📊 Summary: {len(existing_files)} existing, {len(created_files)} created")
    print(f"📦 Total packages: {len(packages)}")
    
    return len(created_files), len(existing_files)


if __name__ == "__main__":
    created, existing = create_init_files()
    print(f"\n🎯 Package structure ready with {created + existing} initialized packages!")