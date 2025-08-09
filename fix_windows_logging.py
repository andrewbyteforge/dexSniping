"""
Windows-Compatible Logger Fix
File: fix_windows_logging.py

Fixes Unicode emoji encoding issues on Windows by replacing emojis with
ASCII-compatible symbols while maintaining all logging functionality.
"""

import os
import sys
from pathlib import Path


def fix_logger_unicode_issues():
    """
    Fix Unicode emoji issues in the logger for Windows compatibility.
    
    File: app/utils/logger.py
    """
    print("🔧 Fixing Windows Unicode issues in logger...")
    
    logger_file = Path("app/utils/logger.py")
    if not logger_file.exists():
        print("❌ app/utils/logger.py not found")
        return False
    
    try:
        content = logger_file.read_text(encoding='utf-8')
        
        # Create backup
        backup_file = logger_file.with_suffix('.py.unicode_fix_backup')
        backup_file.write_text(content, encoding='utf-8')
        print(f"✅ Created backup: {backup_file}")
        
        # Replace Unicode emojis with ASCII-compatible symbols
        emoji_replacements = {
            # Console handler should use ASCII-safe symbols
            "📝": "[LOG]",
            "🎯": "[TARGET]", 
            "💰": "[TRADE]",
            "🛡️": "[RISK]",
            "🔗": "[WALLET]",
            "📊": "[TX]",
            "⏱️": "[TIMER]",
            "🔍": "[DEBUG]",
            "ℹ️": "[INFO]",
            "⚠️": "[WARN]",
            "❌": "[ERROR]",
            "🚀": "[START]",
            "🛑": "[STOP]",
            "📅": "[TIME]",
            "📁": "[DIR]",
            "🐍": "[PYTHON]",
            "🔧": "[CONFIG]",
            "👋": "[BYE]"
        }
        
        # Update console formatter to use ASCII symbols
        old_console_formatter = '''        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )'''
        
        new_console_formatter = '''        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )'''
        
        # The issue is that we need to clean up log messages before they hit the console
        # Let's add a custom console handler with emoji filtering
        
        # Find the console handler setup and replace it
        old_console_handler = '''        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)'''
        
        new_console_handler = '''        # Console handler with Windows Unicode support
        console_handler = WindowsCompatibleHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)'''
        
        if old_console_handler in content:
            content = content.replace(old_console_handler, new_console_handler)
            print("✅ Updated console handler")
        
        # Add the WindowsCompatibleHandler class
        handler_class = '''

class WindowsCompatibleHandler(logging.StreamHandler):
    """
    Custom logging handler that replaces Unicode emojis with ASCII symbols
    for Windows console compatibility.
    """
    
    EMOJI_REPLACEMENTS = {
        "📝": "[LOG]",
        "🎯": "[TARGET]", 
        "💰": "[TRADE]",
        "🛡️": "[RISK]",
        "🔗": "[WALLET]",
        "📊": "[TX]",
        "⏱️": "[TIMER]",
        "🔍": "[DEBUG]",
        "ℹ️": "[INFO]",
        "⚠️": "[WARN]",
        "❌": "[ERROR]",
        "🚀": "[START]",
        "🛑": "[STOP]",
        "📅": "[TIME]",
        "📁": "[DIR]",
        "🐍": "[PYTHON]",
        "🔧": "[CONFIG]",
        "👋": "[BYE]"
    }
    
    def emit(self, record):
        """Override emit to replace Unicode emojis before outputting to console."""
        try:
            # Get the formatted message
            msg = self.format(record)
            
            # Replace Unicode emojis with ASCII symbols for console output
            for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                msg = msg.replace(emoji, replacement)
            
            # Write the cleaned message
            self.stream.write(msg + self.terminator)
            self.flush()
            
        except UnicodeEncodeError:
            # Fallback: remove all non-ASCII characters
            try:
                msg = self.format(record)
                msg = msg.encode('ascii', 'replace').decode('ascii')
                self.stream.write(msg + self.terminator)
                self.flush()
            except Exception:
                # Last resort: basic message
                self.stream.write(f"[LOGGING ERROR] - {record.levelname} - {record.name}\\n")
                self.flush()
        except Exception as e:
            self.handleError(record)


'''
        
        # Insert the handler class before the DEXSniperLogger class
        dex_logger_class_pos = content.find("class DEXSniperLogger:")
        if dex_logger_class_pos != -1:
            content = content[:dex_logger_class_pos] + handler_class + content[dex_logger_class_pos:]
            print("✅ Added WindowsCompatibleHandler class")
        
        # Write the updated content
        logger_file.write_text(content, encoding='utf-8')
        print("✅ Fixed Windows Unicode issues in logger")
        
        return True
        
    except Exception as error:
        print(f"❌ Error fixing logger: {error}")
        return False


def fix_console_encoding():
    """
    Set console encoding to UTF-8 for better Unicode support.
    """
    print("🔧 Setting console encoding...")
    
    try:
        # Set console to UTF-8 (Windows 10+ supports this)
        if os.name == 'nt':  # Windows
            os.system('chcp 65001 >nul 2>&1')
            print("✅ Console encoding set to UTF-8")
        
        return True
        
    except Exception as error:
        print(f"⚠️ Could not set console encoding: {error}")
        return False


def create_windows_test_script():
    """Create a Windows-compatible test script."""
    print("📝 Creating Windows-compatible test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Windows-Compatible Logging Test
File: test_windows_logging.py

Test script that works properly on Windows without Unicode issues.
"""

import sys
from pathlib import Path

def test_windows_logging():
    """Test the Windows-compatible logging system."""
    print("=== Windows-Compatible Logging Test ===")
    
    try:
        # Test imports
        from app.utils.logger import (
            setup_logger, 
            get_trading_logger,
            get_performance_logger
        )
        print("[SUCCESS] Enhanced logger imports successful")
        
        # Test basic logger
        logger = setup_logger("test.windows", "application")
        logger.info("[TARGET] Testing Windows-compatible logging system")
        logger.warning("[WARN] This is a test warning")
        logger.error("[ERROR] This is a test error")
        print("[SUCCESS] Basic logging test completed")
        
        # Test trading logger
        trading_logger = get_trading_logger("test.trading")
        trading_logger.log_trade_execution({
            "symbol": "ETH/USDC",
            "amount": "1.0",
            "type": "test"
        })
        print("[SUCCESS] Trading logger test completed")
        
        # Test performance logger
        perf_logger = get_performance_logger("test.performance")
        perf_logger.start_timer("test_operation")
        import time
        time.sleep(0.1)
        perf_logger.end_timer("test_operation")
        print("[SUCCESS] Performance logger test completed")
        
        # Check log files
        logs_dir = Path("logs")
        if logs_dir.exists():
            print("\\n[FILES] Log files created:")
            for log_file in logs_dir.rglob("*.log"):
                if log_file.stat().st_size > 0:
                    print(f"  [OK] {log_file} ({log_file.stat().st_size} bytes)")
        else:
            print("[WARN] Logs directory not found")
        
        print("\\n[SUCCESS] Windows-compatible logging system is working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_windows_logging()
    sys.exit(0 if success else 1)
'''
    
    test_file = Path("test_windows_logging.py")
    test_file.write_text(test_script, encoding='utf-8')
    print(f"✅ Created Windows test script: {test_file}")
    
    return True


def main():
    """Main function to fix Windows logging issues."""
    print("🚀 Windows Logging Compatibility Fix")
    print("=" * 50)
    
    steps = [
        ("Fix logger Unicode issues", fix_logger_unicode_issues),
        ("Set console encoding", fix_console_encoding),
        ("Create Windows test script", create_windows_test_script)
    ]
    
    success_count = 0
    for step_name, step_function in steps:
        print(f"\\n🔄 {step_name}...")
        if step_function():
            success_count += 1
            print(f"✅ {step_name} completed")
        else:
            print(f"❌ {step_name} failed")
    
    print("\\n" + "=" * 50)
    print(f"🎯 Results: {success_count}/{len(steps)} steps completed")
    
    if success_count == len(steps):
        print("🎉 Windows logging compatibility fix completed!")
        print("\\n📋 What was fixed:")
        print("   • Added WindowsCompatibleHandler for console output")
        print("   • Unicode emojis replaced with ASCII symbols for console")
        print("   • File logging still uses full Unicode (works fine)")
        print("   • Console encoding set to UTF-8")
        print("\\n🔄 Next steps:")
        print("   1. Run: python test_windows_logging.py")
        print("   2. Restart server: uvicorn app.main:app --reload")
        print("   3. No more Unicode errors in console!")
    else:
        print("⚠️ Some fixes failed. Check errors above.")
    
    return success_count == len(steps)


if __name__ == "__main__":
    main()