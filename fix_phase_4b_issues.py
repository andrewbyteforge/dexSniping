#!/usr/bin/env python3
"""
Phase 4B Critical Fixes Application Script
File: fix_phase_4b_issues.py

This script resolves the critical issues preventing Phase 4B tests from passing:
1. Database SQL syntax fixes (SQLite INDEX creation)
2. Missing __init__.py files
3. Import path corrections
4. Configuration validation fixes

Run this script to resolve all Phase 4B test failures and ensure 100% success rate.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class Phase4BFixer:
    """Professional Phase 4B issue resolution system."""
    
    def __init__(self):
        """Initialize the Phase 4B fixer."""
        self.project_root = Path.cwd()
        self.fixes_applied: List[str] = []
        self.errors_encountered: List[str] = []
        
    def validate_project_structure(self) -> bool:
        """
        Validate that we're in the correct project directory.
        
        Returns:
            bool: True if valid project structure found
        """
        try:
            required_paths = [
                self.project_root / "app",
                self.project_root / "tests",
                self.project_root / "app" / "core",
                self.project_root / "app" / "api"
            ]
            
            missing_paths = [path for path in required_paths if not path.exists()]
            
            if missing_paths:
                self.errors_encountered.append(
                    f"Missing required directories: {[str(p) for p in missing_paths]}"
                )
                return False
            
            print("✅ Project structure validation passed")
            return True
            
        except Exception as error:
            self.errors_encountered.append(f"Project validation error: {error}")
            return False
    
    def fix_database_sql_syntax(self) -> bool:
        """
        Fix database SQL syntax issues in persistence_manager.py.
        
        The main issue: SQLite doesn't support inline INDEX creation in CREATE TABLE.
        Indexes must be created separately.
        
        Returns:
            bool: True if fixes applied successfully
        """
        try:
            persistence_file = self.project_root / "app" / "core" / "database" / "persistence_manager.py"
            
            if not persistence_file.exists():
                self.errors_encountered.append("persistence_manager.py not found")
                return False
            
            # Read current content
            content = persistence_file.read_text(encoding='utf-8')
            
            # Define the corrected _create_tables method
            corrected_method = '''    async def _create_tables(self) -> None:
        """
        Create database tables with proper SQLite syntax.
        
        Raises:
            DatabaseError: If table creation fails
        """
        try:
            # Create trade_records table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS trade_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE NOT NULL,
                    token_address TEXT NOT NULL,
                    network TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    amount_eth REAL NOT NULL,
                    amount_tokens REAL,
                    price_usd REAL NOT NULL,
                    gas_fee_eth REAL NOT NULL,
                    slippage_percent REAL NOT NULL,
                    transaction_hash TEXT,
                    block_number INTEGER,
                    status TEXT NOT NULL DEFAULT 'pending',
                    profit_loss_usd REAL DEFAULT NULL,
                    created_at TEXT NOT NULL,
                    executed_at TEXT,
                    completed_at TEXT
                )
            """)
            
            # Create trade_records indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_token ON trade_records(token_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_created ON trade_records(created_at)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_trade_records_status ON trade_records(status)
            """)
            
            # Create portfolio_snapshots table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id TEXT UNIQUE NOT NULL,
                    wallet_address TEXT NOT NULL,
                    total_value_usd REAL NOT NULL,
                    eth_balance REAL NOT NULL,
                    token_count INTEGER NOT NULL DEFAULT 0,
                    active_trades INTEGER NOT NULL DEFAULT 0,
                    profit_loss_24h REAL DEFAULT 0.0,
                    profit_loss_total REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create portfolio_snapshots indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_portfolio_wallet ON portfolio_snapshots(wallet_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_portfolio_created ON portfolio_snapshots(created_at)
            """)
            
            # Create wallet_sessions table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS wallet_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    wallet_address TEXT NOT NULL,
                    wallet_type TEXT NOT NULL,
                    network TEXT NOT NULL,
                    connected_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    metadata TEXT
                )
            """)
            
            # Create wallet_sessions indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_wallet_sessions_address ON wallet_sessions(wallet_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_wallet_sessions_active ON wallet_sessions(is_active)
            """)
            
            # Create trading_opportunities table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS trading_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id TEXT UNIQUE NOT NULL,
                    token_address TEXT NOT NULL,
                    network TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    liquidity_usd REAL NOT NULL,
                    volume_24h REAL,
                    price_change_1h REAL,
                    risk_score REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    discovered_at TEXT NOT NULL,
                    expires_at TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Create trading_opportunities indexes separately
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_token ON trading_opportunities(token_address)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_discovered ON trading_opportunities(discovered_at)
            """)
            
            await self._connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_risk ON trading_opportunities(risk_score)
            """)
            
            # Create configurations table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    config_type TEXT NOT NULL DEFAULT 'string',
                    description TEXT,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT DEFAULT 'system'
                )
            """)
            
            await self._connection.commit()
            
            logger.info("✅ Database tables created successfully")
            
        except Exception as error:
            logger.error(f"❌ Failed to create database tables: {error}")
            raise DatabaseError(f"Table creation failed: {error}")'''
            
            # Find and replace the _create_tables method
            method_start = content.find("async def _create_tables(self)")
            if method_start == -1:
                self.errors_encountered.append("Could not find _create_tables method")
                return False
            
            # Find the end of the method (next method or class end)
            lines = content[method_start:].split('\n')
            method_lines = []
            indent_level = None
            
            for i, line in enumerate(lines):
                if i == 0 or (indent_level is not None and 
                             (line.strip() == '' or line.startswith(' ' * indent_level) or line.startswith('\t'))):
                    if indent_level is None and line.strip():
                        # Detect indentation level from first non-empty line
                        indent_level = len(line) - len(line.lstrip())
                    method_lines.append(line)
                else:
                    # Found next method or end of class
                    break
            
            method_content = '\n'.join(method_lines)
            
            # Replace the method
            new_content = content.replace(method_content, corrected_method)
            
            # Write back to file
            persistence_file.write_text(new_content, encoding='utf-8')
            
            self.fixes_applied.append("Database SQL syntax fixed in persistence_manager.py")
            print("✅ Database SQL syntax fixes applied")
            return True
            
        except Exception as error:
            self.errors_encountered.append(f"Database SQL fix error: {error}")
            return False
    
    def create_missing_init_files(self) -> bool:
        """
        Create missing __init__.py files for proper Python module imports.
        
        Returns:
            bool: True if all init files created successfully
        """
        try:
            init_locations = [
                "app",
                "app/core",
                "app/core/database", 
                "app/core/trading",
                "app/core/config",
                "app/core/blockchain",
                "app/core/wallet",
                "app/core/dex",
                "app/core/ai",
                "app/core/risk",
                "app/core/analytics",
                "app/api",
                "app/api/v1",
                "app/api/v1/endpoints",
                "app/utils",
                "tests"
            ]
            
            created_files = []
            
            for location in init_locations:
                init_path = self.project_root / location / "__init__.py"
                
                if not init_path.exists():
                    # Create directory if it doesn't exist
                    init_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create appropriate __init__.py content
                    if location == "app":
                        content = '"""DEX Sniper Pro Trading Bot Application Package."""\n'
                    elif location.startswith("app/core"):
                        content = f'"""Core {location.split("/")[-1]} module."""\n'
                    elif location.startswith("app/api"):
                        content = f'"""API {location.split("/")[-1]} module."""\n'
                    else:
                        content = f'"""{location.replace("/", " ").title()} module."""\n'
                    
                    init_path.write_text(content, encoding='utf-8')
                    created_files.append(str(init_path))
            
            if created_files:
                self.fixes_applied.append(f"Created {len(created_files)} missing __init__.py files")
                print(f"✅ Created {len(created_files)} missing __init__.py files")
            else:
                print("✅ All __init__.py files already exist")
            
            return True
            
        except Exception as error:
            self.errors_encountered.append(f"Init files creation error: {error}")
            return False
    
    def fix_import_errors(self) -> bool:
        """
        Fix common import errors in test files and modules.
        
        Returns:
            bool: True if import fixes applied successfully
        """
        try:
            # Common import path fixes for test files
            test_files_to_fix = [
                "tests/test_phase_4b_complete.py",
                "tests/test_phase_4b_integration.py", 
                "tests/test_network_manager_fix.py"
            ]
            
            fixes_made = 0
            
            for test_file_path in test_files_to_fix:
                test_file = self.project_root / test_file_path
                
                if test_file.exists():
                    content = test_file.read_text(encoding='utf-8')
                    
                    # Add proper path setup if missing
                    path_setup = '''import sys
from pathlib import Path

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

'''
                    
                    if "sys.path.insert(0" not in content:
                        # Insert path setup after existing imports but before app imports
                        lines = content.split('\n')
                        insert_index = 0
                        
                        for i, line in enumerate(lines):
                            if line.startswith('import ') or line.startswith('from '):
                                if not line.startswith('from app.') and not line.startswith('import app.'):
                                    insert_index = i + 1
                            elif line.startswith('from app.') or line.startswith('import app.'):
                                break
                        
                        lines.insert(insert_index, path_setup)
                        content = '\n'.join(lines)
                        
                        test_file.write_text(content, encoding='utf-8')
                        fixes_made += 1
            
            if fixes_made > 0:
                self.fixes_applied.append(f"Fixed import paths in {fixes_made} test files")
                print(f"✅ Fixed import paths in {fixes_made} test files")
            else:
                print("✅ Import paths already correct")
            
            return True
            
        except Exception as error:
            self.errors_encountered.append(f"Import fix error: {error}")
            return False
    
    def create_missing_core_modules(self) -> bool:
        """
        Create any missing core module files that are referenced but don't exist.
        
        Returns:
            bool: True if missing modules created successfully
        """
        try:
            # Check for commonly referenced but potentially missing modules
            core_modules = [
                ("app/core/exceptions.py", '''"""Core trading bot exceptions."""

class TradingBotError(Exception):
    """Base exception for trading bot errors."""
    pass

class DatabaseError(TradingBotError):
    """Database operation errors."""
    pass

class NetworkError(TradingBotError):
    """Network connection errors."""
    pass

class TradingError(TradingBotError):
    """Trading operation errors."""
    pass

class InsufficientFundsError(TradingError):
    """Insufficient funds for trading."""
    pass

class ConfigurationError(TradingBotError):
    """Configuration validation errors."""
    pass

class ValidationError(TradingBotError):
    """Data validation errors."""
    pass
'''),
                ("app/utils/helpers.py", '''"""Utility helper functions."""

import json
from typing import Any, Dict, Optional
from datetime import datetime

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime as ISO string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()

def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON with fallback."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Safely dump JSON with fallback."""
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        return default
''')
            ]
            
            created_modules = []
            
            for module_path, module_content in core_modules:
                module_file = self.project_root / module_path
                
                if not module_file.exists():
                    # Create directory if needed
                    module_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write module content
                    module_file.write_text(module_content, encoding='utf-8')
                    created_modules.append(module_path)
            
            if created_modules:
                self.fixes_applied.append(f"Created {len(created_modules)} missing core modules")
                print(f"✅ Created {len(created_modules)} missing core modules")
            else:
                print("✅ All core modules already exist")
            
            return True
            
        except Exception as error:
            self.errors_encountered.append(f"Core modules creation error: {error}")
            return False
    
    def apply_all_fixes(self) -> Dict[str, Any]:
        """
        Apply all Phase 4B fixes in the correct order.
        
        Returns:
            Dict containing fix results and summary
        """
        print("🔧 DEX Sniper Pro - Phase 4B Critical Fixes")
        print("=" * 60)
        
        # Validate project structure first
        if not self.validate_project_structure():
            return {
                "success": False,
                "error": "Invalid project structure",
                "fixes_applied": self.fixes_applied,
                "errors": self.errors_encountered
            }
        
        # Apply fixes in order
        fix_results = {
            "init_files": self.create_missing_init_files(),
            "core_modules": self.create_missing_core_modules(), 
            "import_paths": self.fix_import_errors(),
            "database_sql": self.fix_database_sql_syntax()
        }
        
        # Calculate success
        successful_fixes = sum(1 for success in fix_results.values() if success)
        total_fixes = len(fix_results)
        
        print("\n" + "=" * 60)
        print("📊 Phase 4B Fixes Summary:")
        print("=" * 60)
        print(f"✅ Successful fixes: {successful_fixes}/{total_fixes}")
        print(f"📋 Total fixes applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\n🔧 Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        if self.errors_encountered:
            print("\n❌ Errors Encountered:")
            for error in self.errors_encountered:
                print(f"   • {error}")
        
        overall_success = successful_fixes == total_fixes and len(self.errors_encountered) == 0
        
        if overall_success:
            print("\n🎉 ALL PHASE 4B FIXES APPLIED SUCCESSFULLY!")
            print("✅ Ready to run Phase 4B tests")
            print("\n💡 Next steps:")
            print("   1. Run: python tests/test_phase_4b_complete.py")
            print("   2. Verify: All 20 tests should pass")
            print("   3. Start: uvicorn app.main:app --reload")
        else:
            print(f"\n⚠️ {total_fixes - successful_fixes} fixes failed")
            print("🔧 Review error messages and fix manually")
        
        return {
            "success": overall_success,
            "fixes_applied": self.fixes_applied,
            "errors": self.errors_encountered,
            "fix_results": fix_results,
            "successful_fixes": successful_fixes,
            "total_fixes": total_fixes
        }


def main():
    """Main execution function."""
    try:
        fixer = Phase4BFixer()
        results = fixer.apply_all_fixes()
        
        if results["success"]:
            print("\n🎯 RESULT: Phase 4B fixes completed successfully!")
            return 0
        else:
            print("\n🎯 RESULT: Phase 4B fixes need attention")
            return 1
            
    except Exception as error:
        print(f"\n💥 Fix script error: {error}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    """Run the Phase 4B fixes."""
    sys.exit(main())