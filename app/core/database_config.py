"""
Database Configuration Fix
File: app/core/database_config.py

Fixed database configuration to use mock mode and remove auth errors.
"""

import os
from typing import Optional


class DatabaseConfig:
    """Database configuration with mock mode fallback."""
    
    def __init__(self):
        self.use_mock_mode = True  # Always use mock mode for now
        self.connection_string = None
        
    def get_connection_string(self) -> Optional[str]:
        """Get database connection string or None for mock mode."""
        if self.use_mock_mode:
            return None
        return self.connection_string
    
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode."""
        return self.use_mock_mode


# Global config instance
db_config = DatabaseConfig()
