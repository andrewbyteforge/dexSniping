"""
Safe Configuration Fix
File: safe_config_fix.py

Safely adds the ENVIRONMENT property with proper indentation.
"""

def fix_config_safely():
    """Safely fix the config.py file with proper indentation."""
    
    config_file = "app/config.py"
    backup_file = "app/config.py.backup"
    
    try:
        # Create backup
        with open(config_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print(f'✅ Created backup: {backup_file}')
        
        # Parse the file line by line
        lines = original_content.split('\n')
        new_lines = []
        
        # Find the Settings class and add ENVIRONMENT property
        in_settings_class = False
        class_indent = ""
        environment_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Detect Settings class
            if 'class Settings(' in line:
                in_settings_class = True
                class_indent = line[:len(line) - len(line.lstrip())]  # Get indentation
                print(f'Found Settings class at line {i+1}')
                continue
            
            # If we're in Settings class and find class Config, add ENVIRONMENT before it
            if (in_settings_class and 'class Config:' in line and not environment_added):
                # Add ENVIRONMENT property before Config class
                property_lines = [
                    '',
                    f'{class_indent}    @property',
                    f'{class_indent}    def ENVIRONMENT(self) -> str:',
                    f'{class_indent}        """Get environment name for compatibility."""',
                    f'{class_indent}        return self.environment',
                    ''
                ]
                
                # Insert before the current line (class Config)
                new_lines = new_lines[:-1] + property_lines + [line]
                environment_added = True
                print('✅ Added ENVIRONMENT property before Config class')
                continue
        
        if not environment_added:
            # If we couldn't find Config class, add at the end of Settings class
            # Find the end of Settings class
            for i in range(len(new_lines) - 1, -1, -1):
                line = new_lines[i]
                if line.strip() and not line.startswith('#') and not line.startswith('class '):
                    # This might be the last line of Settings class
                    if class_indent:
                        property_lines = [
                            '',
                            f'{class_indent}    @property',
                            f'{class_indent}    def ENVIRONMENT(self) -> str:',
                            f'{class_indent}        """Get environment name for compatibility."""',
                            f'{class_indent}        return self.environment',
                            ''
                        ]
                        new_lines = new_lines[:i+1] + property_lines + new_lines[i+1:]
                        environment_added = True
                        print('✅ Added ENVIRONMENT property at end of Settings class')
                        break
        
        if environment_added:
            # Write the fixed content
            new_content = '\n'.join(new_lines)
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f'✅ Updated {config_file}')
            return True
        else:
            print('❌ Could not find suitable location to add ENVIRONMENT property')
            return False
            
    except Exception as e:
        print(f'❌ Error fixing config: {e}')
        
        # Restore backup if something went wrong
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f'✅ Restored from backup due to error')
        except:
            pass
        
        return False


def validate_python_syntax():
    """Validate that the config.py file has valid Python syntax."""
    try:
        with open('app/config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the code
        compile(content, 'app/config.py', 'exec')
        print('✅ Python syntax is valid')
        return True
        
    except SyntaxError as e:
        print(f'❌ Syntax error: {e}')
        print(f'   Line {e.lineno}: {e.text}')
        return False
    except Exception as e:
        print(f'❌ Validation error: {e}')
        return False


def test_environment_property():
    """Test if the ENVIRONMENT property works."""
    try:
        import sys
        import os
        
        # Clear any cached modules
        modules_to_clear = [key for key in sys.modules.keys() if key.startswith('app.config')]
        for module in modules_to_clear:
            del sys.modules[module]
        
        sys.path.insert(0, os.getcwd())
        
        # Import and test
        from app.config import settings
        
        # Test both properties
        env_lower = getattr(settings, 'environment', None)
        env_upper = getattr(settings, 'ENVIRONMENT', None)
        
        print(f'environment (lowercase): {env_lower}')
        print(f'ENVIRONMENT (uppercase): {env_upper}')
        
        if env_upper:
            print('✅ ENVIRONMENT property is working!')
            return True
        else:
            print('❌ ENVIRONMENT property still not accessible')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print('🔧 SAFE CONFIG FIX')
    print('=' * 40)
    
    print('\n1. Fixing config.py with proper indentation...')
    if fix_config_safely():
        print('\n2. Validating Python syntax...')
        if validate_python_syntax():
            print('\n3. Testing ENVIRONMENT property...')
            if test_environment_property():
                print('\n🎉 SUCCESS! Config fix complete.')
                print('🚀 Run: python test_complete_system.py')
                print('🎯 Expected: 100% success rate!')
                return True
            else:
                print('\n⚠️ Property added but not accessible. Manual check needed.')
        else:
            print('\n❌ Syntax error in config.py. Check the backup file.')
    else:
        print('\n❌ Could not fix config.py. Check manually.')
    
    print('\n📝 Manual fix option:')
    print('   Add this to Settings class in app/config.py:')
    print('   ')
    print('   @property')
    print('   def ENVIRONMENT(self) -> str:')
    print('       """Get environment name for compatibility."""')
    print('       return self.environment')
    
    return False


if __name__ == "__main__":
    success = main()
    if not success:
        print('\n💡 If automatic fix failed, edit app/config.py manually.')