"""
Git Status Analyzer
File: analyze_git_changes.py

Analyzes the 134 git changes and categorizes them for organized commits.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set


def get_git_status() -> List[str]:
    """Get git status output."""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return []


def categorize_changes(git_lines: List[str]) -> Dict[str, List[str]]:
    """Categorize git changes by type and purpose."""
    categories = {
        'dashboard_core': [],
        'logging_system': [],
        'api_endpoints': [],
        'core_components': [],
        'server_cleanup': [],
        'test_scripts': [],
        'documentation': [],
        'backup_files': [],
        'config_files': [],
        'other': []
    }
    
    for line in git_lines:
        if len(line) < 3:
            continue
            
        status = line[:2]
        filepath = line[3:]
        
        # Categorize by file path and purpose
        if 'main.py' in filepath:
            categories['dashboard_core'].append(f"{status} {filepath}")
        elif 'logger.py' in filepath or filepath.startswith('logs/'):
            categories['logging_system'].append(f"{status} {filepath}")
        elif 'api/v1/endpoints' in filepath:
            categories['api_endpoints'].append(f"{status} {filepath}")
        elif 'app/core/' in filepath:
            categories['core_components'].append(f"{status} {filepath}")
        elif 'app/server/' in filepath:
            categories['server_cleanup'].append(f"{status} {filepath}")
        elif filepath.startswith('test_') or 'test' in filepath.lower():
            categories['test_scripts'].append(f"{status} {filepath}")
        elif filepath.endswith('.md') or 'README' in filepath:
            categories['documentation'].append(f"{status} {filepath}")
        elif 'backup' in filepath or filepath.endswith('.backup'):
            categories['backup_files'].append(f"{status} {filepath}")
        elif filepath.endswith('.json') or filepath.endswith('.env'):
            categories['config_files'].append(f"{status} {filepath}")
        else:
            categories['other'].append(f"{status} {filepath}")
    
    return categories


def print_analysis(categories: Dict[str, List[str]]):
    """Print analysis of categorized changes."""
    total = sum(len(files) for files in categories.values())
    
    print(f"📊 Git Changes Analysis - {total} total files")
    print("=" * 60)
    
    category_descriptions = {
        'dashboard_core': '🎯 Professional Dashboard Core',
        'logging_system': '📝 Enhanced Logging System',
        'api_endpoints': '📡 API Endpoint Updates',
        'core_components': '🔧 Core Component Updates',
        'server_cleanup': '🧹 Server Code Cleanup',
        'test_scripts': '🧪 Test Scripts & Utilities',
        'documentation': '📚 Documentation Updates',
        'backup_files': '💾 Backup Files',
        'config_files': '⚙️ Configuration Files',
        'other': '📦 Other Changes'
    }
    
    for category, files in categories.items():
        if files:
            count = len(files)
            description = category_descriptions.get(category, category)
            print(f"\n{description} ({count} files):")
            
            # Show first few files as examples
            for file in files[:3]:
                print(f"  {file}")
            
            if count > 3:
                print(f"  ... and {count - 3} more files")


def generate_commit_commands(categories: Dict[str, List[str]]) -> List[str]:
    """Generate git commit commands for organized commits."""
    commands = []
    
    # Commit 1: Dashboard Core (Most Important)
    if categories['dashboard_core']:
        commands.append("# Commit 1: Professional Dashboard Working")
        for file in categories['dashboard_core']:
            filepath = file[3:]  # Remove status prefix
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "feat: Professional dashboard with sidebar working"')
        commands.append("")
    
    # Commit 2: Logging System
    if categories['logging_system']:
        commands.append("# Commit 2: Enhanced Logging System")
        for file in categories['logging_system']:
            filepath = file[3:]
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "feat: Comprehensive file-based logging system"')
        commands.append("")
    
    # Commit 3: API Endpoints
    if categories['api_endpoints']:
        commands.append("# Commit 3: API Endpoint Logging Integration")
        for file in categories['api_endpoints']:
            filepath = file[3:]
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "feat: Enhanced logging in API endpoints"')
        commands.append("")
    
    # Commit 4: Core Components
    if categories['core_components']:
        commands.append("# Commit 4: Core Component Logging Integration")
        for file in categories['core_components']:
            filepath = file[3:]
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "feat: Enhanced logging in core components"')
        commands.append("")
    
    # Commit 5: Server Cleanup
    if categories['server_cleanup']:
        commands.append("# Commit 5: Server Code Cleanup")
        for file in categories['server_cleanup']:
            filepath = file[3:]
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "refactor: Clean up fallback routes and server code"')
        commands.append("")
    
    # Commit 6: Test Scripts
    if categories['test_scripts']:
        commands.append("# Commit 6: Test Scripts and Utilities")
        for file in categories['test_scripts']:
            filepath = file[3:]
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "feat: Testing and utility scripts"')
        commands.append("")
    
    # Commit 7: Documentation
    if categories['documentation']:
        commands.append("# Commit 7: Documentation Updates")
        for file in categories['documentation']:
            filepath = file[3:]
            commands.append(f"git add \"{filepath}\"")
        commands.append('git commit -m "docs: Updated project documentation and status"')
        commands.append("")
    
    # Optional: Backup files (or add to .gitignore)
    if categories['backup_files']:
        commands.append("# Optional: Add backup files to .gitignore instead of committing")
        commands.append("echo '*.backup' >> .gitignore")
        commands.append("echo '*_backup*' >> .gitignore") 
        commands.append("echo '*.logging_backup' >> .gitignore")
        commands.append("git add .gitignore")
        commands.append('git commit -m "chore: Ignore backup files from development"')
        commands.append("")
    
    return commands


def create_commit_script(commands: List[str]):
    """Create a script file with commit commands."""
    script_content = "#!/bin/bash\n"
    script_content += "# Organized Git Commits for DEX Sniper Pro\n"
    script_content += "# Generated from 134 changes analysis\n\n"
    script_content += "\n".join(commands)
    
    script_file = Path("organize_commits.sh")
    script_file.write_text(script_content, encoding='utf-8')
    
    print(f"\n✅ Created commit script: {script_file}")
    print("🔄 Run with: bash organize_commits.sh")


def main():
    """Analyze git changes and suggest organization strategy."""
    print("🔍 Analyzing Git Changes for DEX Sniper Pro")
    print("=" * 50)
    
    # Get git status
    git_lines = get_git_status()
    
    if not git_lines:
        print("✅ No changes detected in git status")
        return
    
    # Categorize changes
    categories = categorize_changes(git_lines)
    
    # Print analysis
    print_analysis(categories)
    
    # Generate commit commands
    commands = generate_commit_commands(categories)
    
    # Create script
    create_commit_script(commands)
    
    print("\n📋 Recommended Strategy:")
    print("1. Review the generated organize_commits.sh script")
    print("2. Run individual commits or the full script")
    print("3. Consider adding backup files to .gitignore")
    print("4. Push organized commits to maintain clean history")
    
    print("\n🎯 Benefits of this approach:")
    print("✅ Clean, meaningful commit messages")
    print("✅ Logical grouping of related changes") 
    print("✅ Easy to review and rollback if needed")
    print("✅ Professional git history")


if __name__ == "__main__":
    main()