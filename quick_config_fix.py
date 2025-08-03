"""
Quick Configuration Fix
File: quick_config_fix.py

Simple fix to add the ENVIRONMENT property to the Settings class.
"""

def fix_config_environment():
    """Add ENVIRONMENT property to Settings class in config.py."""
    
    config_file = "app/config.py"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if ENVIRONMENT property already exists
        if '@property' in content and 'def ENVIRONMENT' in content:
            print('✅ ENVIRONMENT property already exists')
            return True
        
        # Add the ENVIRONMENT property before the class Config line
        if 'class Config:' in content:
            # Find the position to insert the property
            config_class_pos = content.find('class Config:')
            
            # Insert the ENVIRONMENT property before class Config
            property_code = '''    
    @property
    def ENVIRONMENT(self) -> str:
        """Get environment name for compatibility."""
        return self.environment
    
'''
            
            # Insert the property
            new_content = content[:config_class_pos] + property_code + content[config_class_pos:]
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print('✅ Added ENVIRONMENT property to Settings class')
            return True
        else:
            print('❌ Could not find insertion point in config.py')
            return False
            
    except Exception as e:
        print(f'❌ Failed to fix config: {e}')
        return False


def test_fix():
    """Test if the fix works."""
    try:
        import sys
        import os
        
        # Reload the config module
        if 'app.config' in sys.modules:
            del sys.modules['app.config']
        
        sys.path.insert(0, os.getcwd())
        from app.config import settings
        
        # Test the ENVIRONMENT property
        env_value = getattr(settings, 'ENVIRONMENT', None)
        if env_value:
            print(f'✅ ENVIRONMENT property works: {env_value}')
            return True
        else:
            print('❌ ENVIRONMENT property still not working')
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False


if __name__ == "__main__":
    print('🔧 Quick Config Fix')
    print('=' * 30)
    
    if fix_config_environment():
        print('\n🧪 Testing fix...')
        if test_fix():
            print('\n🎉 Fix successful! ENVIRONMENT property working.')
            print('🚀 Run: python test_complete_system.py')
        else:
            print('\n⚠️ Fix applied but test failed. Manual check needed.')
    else:
        print('\n❌ Fix failed. Manual intervention needed.')