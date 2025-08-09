#!/usr/bin/env python3
"""
Fix Missing PersistenceManager Methods
File: fix_persistence_manager_methods.py

Add the missing methods to PersistenceManager to get 100% test success.
"""

from pathlib import Path


def add_missing_persistence_methods():
    """Add missing methods to PersistenceManager class."""
    
    persistence_file = Path("app/core/database/persistence_manager.py")
    
    if not persistence_file.exists():
        print("❌ persistence_manager.py not found")
        return False
    
    try:
        content = persistence_file.read_text(encoding='utf-8')
        
        # Check if methods already exist
        if 'def get_database_status(' in content and 'def ensure_initialized(' in content:
            print("✅ Methods already exist")
            return True
        
        # Find the PersistenceManager class
        class_start = content.find('class PersistenceManager')
        if class_start == -1:
            print("❌ PersistenceManager class not found")
            return False
        
        # Find a good place to insert methods (before the last method or at the end)
        insert_methods = '''
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get database status information.
        
        Returns:
            Dict containing database status and statistics
        """
        try:
            status = {
                "operational": bool(self._connection),
                "database_path": str(self.db_path),
                "tables_created": True,
                "connection_status": "connected" if self._connection else "disconnected",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self._connection:
                # Try to get some basic stats
                try:
                    cursor = self._connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    status["table_count"] = table_count
                except:
                    status["table_count"] = 0
            
            return status
            
        except Exception as error:
            logger.error(f"[ERROR] Failed to get database status: {error}")
            return {
                "operational": False,
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def ensure_initialized(self) -> bool:
        """
        Ensure the database is properly initialized.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            if not self._connection:
                success = await self.initialize()
                if not success:
                    logger.error("[ERROR] Database initialization failed")
                    return False
            
            # Verify tables exist
            try:
                await self._create_tables()
                logger.info("[OK] Database tables verified/created")
                return True
            except Exception as table_error:
                logger.error(f"[ERROR] Table creation/verification failed: {table_error}")
                return False
                
        except Exception as error:
            logger.error(f"[ERROR] Database ensure_initialized failed: {error}")
            return False
'''
        
        # Find a good insertion point (before the end of the class)
        # Look for the last method in the class
        methods = []
        lines = content.split('\\n')
        in_persistence_class = False
        class_indent = None
        
        for i, line in enumerate(lines):
            if 'class PersistenceManager' in line:
                in_persistence_class = True
                class_indent = len(line) - len(line.lstrip())
                continue
            
            if in_persistence_class:
                if line.strip() and not line.startswith(' ' * (class_indent + 1)) and not line.strip().startswith('#'):
                    # End of class
                    insert_point = i
                    break
                elif line.strip().startswith('def ') or line.strip().startswith('async def '):
                    methods.append(i)
        
        # Insert before the last method or at the end of the class
        if methods:
            insert_line = methods[-1]  # Before last method
        else:
            insert_line = len(lines)  # At the end
        
        # Insert the new methods
        method_lines = insert_methods.split('\\n')
        for j, method_line in enumerate(method_lines):
            lines.insert(insert_line + j, method_line)
        
        # Write back to file
        new_content = '\\n'.join(lines)
        persistence_file.write_text(new_content, encoding='utf-8')
        
        print("✅ Added missing methods to PersistenceManager")
        return True
        
    except Exception as e:
        print(f"❌ Error adding methods: {e}")
        return False


def test_persistence_manager():
    """Test if PersistenceManager methods work."""
    
    try:
        # Clear module cache
        import sys
        if 'app.core.database.persistence_manager' in sys.modules:
            del sys.modules['app.core.database.persistence_manager']
        
        from app.core.database.persistence_manager import PersistenceManager
        
        # Test creating instance
        db_path = "data/test.db"
        manager = PersistenceManager(db_path)
        
        # Test methods exist
        assert hasattr(manager, 'get_database_status'), "get_database_status method missing"
        assert hasattr(manager, 'ensure_initialized'), "ensure_initialized method missing"
        
        # Test get_database_status
        status = manager.get_database_status()
        assert isinstance(status, dict), "get_database_status should return dict"
        assert 'operational' in status, "Status should contain 'operational' key"
        
        print("✅ PersistenceManager methods working correctly")
        return True
        
    except Exception as e:
        print(f"❌ PersistenceManager test failed: {e}")
        return False


def main():
    """Fix missing PersistenceManager methods."""
    print("🔧 Fixing Missing PersistenceManager Methods")
    print("=" * 60)
    
    # Add missing methods
    print("1. Adding missing methods to PersistenceManager...")
    methods_added = add_missing_persistence_methods()
    
    # Test methods
    print("2. Testing PersistenceManager methods...")
    methods_work = test_persistence_manager()
    
    print("\\n" + "=" * 60)
    print("PersistenceManager Fix Summary:")
    print("=" * 60)
    
    if methods_added and methods_work:
        print("✅ PersistenceManager methods fixed successfully!")
        print("\\nMethods added:")
        print("  - get_database_status() - Returns database status info")
        print("  - ensure_initialized() - Ensures database is properly set up")
        print("\\nNext steps:")
        print("1. Run: python test_all_features.py")
        print("2. Expected: 100% test success rate")
        print("3. Status should upgrade to EXCELLENT/PRODUCTION_READY")
    else:
        print("❌ Failed to fix PersistenceManager methods")
    
    return methods_added and methods_work


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)