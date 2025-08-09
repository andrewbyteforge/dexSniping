"""
Fix Encoding Errors Script
File: fix_encoding_errors.py

Removes all emojis from log messages throughout the codebase to fix Windows encoding issues.
This script systematically removes emojis while preserving functionality.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class EncodingFixer:
    """Fix encoding issues by removing emojis from code files."""
    
    def __init__(self):
        self.files_processed = 0
        self.emojis_removed = 0
        self.errors = []
        
        # Common emoji patterns to remove
        self.emoji_patterns = [
            r'[LOG]', r'[WS]', r'[WARN]', r'[OK]', r'[ERROR]', r'[START]', r'[STATS]', r'[DB]', r'[TRADE]',
            r'[API]', r'[UI]', r'[CONFIG]', r'[SEC]', r'[TEST]', r'[TARGET]', r'[FIX]', r'[DIR]',
            r'[SEARCH]', r'[REFRESH]', r'[PERF]', r'[TIME]', r'[SUCCESS]', r'[BOT]', r'[PROFIT]', r'[NOTE]',
            r'[BUILD]', r'[HOT]', r'[TIP]', r'[STAR]', r'[UI]', r'[AUTH]', r'[NET]', r'[TRADE][EMOJI]'
        ]
        
        # Replacement mappings for common emojis
        self.replacements = {
            '[LOG]': '[LOG]',
            '[WS]': '[WS]',
            '[WARN]': '[WARN]',
            '[OK]': '[OK]',
            '[ERROR]': '[ERROR]',
            '[START]': '[START]',
            '[STATS]': '[STATS]',
            '[DB]': '[DB]',
            '[TRADE]': '[TRADE]',
            '[API]': '[API]',
            '[UI]': '[UI]',
            '[CONFIG]': '[CONFIG]',
            '[SEC]': '[SEC]',
            '[TEST]': '[TEST]',
            '[TARGET]': '[TARGET]',
            '[FIX]': '[FIX]',
            '[DIR]': '[DIR]',
            '[SEARCH]': '[SEARCH]',
            '[REFRESH]': '[REFRESH]',
            '[PERF]': '[PERF]',
            '[TIME]': '[TIME]',
            '[SUCCESS]': '[SUCCESS]',
            '[BOT]': '[BOT]',
            '[PROFIT]': '[PROFIT]',
            '[NOTE]': '[NOTE]',
            '[BUILD]': '[BUILD]',
            '[HOT]': '[HOT]',
            '[TIP]': '[TIP]',
            '[STAR]': '[STAR]',
            '[AUTH]': '[AUTH]',
            '[NET]': '[NET]'
        }

    def find_python_files(self, root_dir: str = ".") -> List[Path]:
        """Find all Python files in the project."""
        python_files = []
        
        for root, dirs, files in os.walk(root_dir):
            # Skip certain directories
            if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.venv', 'venv']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files

    def remove_emojis_from_content(self, content: str) -> Tuple[str, int]:
        """Remove emojis from content and return modified content with count."""
        removed_count = 0
        modified_content = content
        
        # Replace known emojis with text equivalents
        for emoji, replacement in self.replacements.items():
            if emoji in modified_content:
                count_before = modified_content.count(emoji)
                modified_content = modified_content.replace(emoji, replacement)
                removed_count += count_before
        
        # Remove any remaining emoji patterns using regex
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251" 
            "]+", 
            flags=re.UNICODE
        )
        
        remaining_emojis = emoji_pattern.findall(modified_content)
        if remaining_emojis:
            modified_content = emoji_pattern.sub('[EMOJI]', modified_content)
            removed_count += len(remaining_emojis)
        
        return modified_content, removed_count

    def fix_file(self, file_path: Path) -> bool:
        """Fix emojis in a single file."""
        try:
            # Read file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Remove emojis
            fixed_content, removed_count = self.remove_emojis_from_content(original_content)
            
            # Only write if changes were made
            if removed_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print(f"  Fixed {file_path}: {removed_count} emojis removed")
                self.emojis_removed += removed_count
                return True
            
            return False
            
        except Exception as e:
            error_msg = f"Error fixing {file_path}: {e}"
            self.errors.append(error_msg)
            print(f"  [ERROR] {error_msg}")
            return False

    def fix_all_files(self) -> None:
        """Fix emojis in all Python files."""
        print("[FIX] DEX Sniper Pro - Encoding Fix")
        print("=" * 40)
        print("Removing emojis from all Python files to fix Windows encoding issues...\n")
        
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files to process\n")
        
        for file_path in python_files:
            if self.fix_file(file_path):
                self.files_processed += 1
        
        print("\n" + "=" * 40)
        print(f"Encoding Fix Results:")
        print(f"  Files processed: {self.files_processed}")
        print(f"  Emojis removed: {self.emojis_removed}")
        print(f"  Errors: {len(self.errors)}")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        
        print(f"\n[OK] Encoding fix complete!")
        print("Next steps:")
        print("1. Run tests: python run_all_tests.py")
        print("2. Check for remaining encoding issues")


def main():
    """Main execution function."""
    try:
        fixer = EncodingFixer()
        fixer.fix_all_files()
        return True
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)