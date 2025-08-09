"""
Fix Unicode Logging Issue
File: fix_unicode_logging.py

Removes emoji from log messages to fix Windows encoding issues.
"""

import os
import sys
from pathlib import Path

def fix_security_manager_logging():
    """Remove emojis from security manager logging."""
    print("[FIX] Fixing Unicode logging in security manager...")
    
    security_file = Path("app/core/security/security_manager.py")
    
    if not security_file.exists():
        print("[ERROR] Security manager file not found")
        return False
    
    try:
        # Read current content
        content = security_file.read_text(encoding='utf-8')
        
        # Replace emoji log messages with text-only versions
        replacements = {
            'logger.info("[EMOJI] Input validator initialized")': 'logger.info("Input validator initialized")',
            'logger.info("[AUTH] Wallet security initialized")': 'logger.info("Wallet security initialized")',
            'logger.info("[EMOJI] API authentication initialized")': 'logger.info("API authentication initialized")',
            'logger.info("🧹 Error sanitizer initialized")': 'logger.info("Error sanitizer initialized")',
            'logger.info("[SEC] Security manager initialized")': 'logger.info("Security manager initialized")',
        }
        
        updated = False
        for old_text, new_text in replacements.items():
            if old_text in content:
                content = content.replace(old_text, new_text)
                updated = True
                print(f"  [OK] Fixed: {old_text[:30]}...")
        
        if updated:
            # Write back the fixed content
            security_file.write_text(content, encoding='utf-8')
            print("[OK] Security manager logging fixed")
            return True
        else:
            print("ℹ[EMOJI] No emoji logging found to fix")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to fix logging: {e}")
        return False

def main():
    """Main fix function."""
    print("[FIX] Unicode Logging Fix")
    print("=" * 30)
    
    if fix_security_manager_logging():
        print("\n[OK] Unicode logging issues fixed!")
        print("[TEST] Security system should now run without logging warnings")
        return True
    else:
        print("\n[ERROR] Could not fix logging issues")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[EMOJI] Fix script error: {e}")
        sys.exit(1)