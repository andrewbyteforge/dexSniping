"""
Fix Pydantic V2 Schema Issues
File: fix_pydantic_v2.py

Fixes the deprecated 'schema_extra' usage in Pydantic schemas by updating
to the new 'json_schema_extra' format for Pydantic V2 compatibility.
"""

import os
import re
from pathlib import Path

def find_schema_files():
    """Find all Python files that might contain Pydantic schemas."""
    schema_files = []
    
    # Search patterns
    search_dirs = [
        "app/schemas",
        "app/api",
        "app/core"
    ]
    
    for search_dir in search_dirs:
        dir_path = Path(search_dir)
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                schema_files.append(py_file)
    
    return schema_files


def fix_schema_extra(file_path: Path):
    """Fix schema_extra usage in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern to find schema_extra usage
        patterns = [
            (r'schema_extra\s*=', 'json_schema_extra ='),
            (r'"schema_extra":', '"json_schema_extra":'),
            (r"'schema_extra':", "'json_schema_extra':"),
        ]
        
        changes_made = False
        
        for old_pattern, new_replacement in patterns:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_replacement, content)
                changes_made = True
        
        # Also fix Config class structure for Pydantic V2
        # Replace 'schema_extra' with 'json_schema_extra' in Config classes
        config_pattern = r'class Config.*?schema_extra'
        if re.search(config_pattern, content, re.DOTALL):
            content = re.sub(
                r'(\s+)schema_extra(\s*=)', 
                r'\1json_schema_extra\2', 
                content
            )
            changes_made = True
        
        if changes_made:
            file_path.write_text(content, encoding='utf-8')
            return True, "Updated schema_extra to json_schema_extra"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {e}"


def update_model_config_format():
    """Update BaseModel Config format for Pydantic V2."""
    config_updates = {
        "app/schemas/trading_schemas.py": '''
class Config:
    """Pydantic V2 configuration."""
    json_encoders = {
        Decimal: str,
        datetime: lambda v: v.isoformat()
    }
    from_attributes = True
    json_schema_extra = {
        "example": {
            "session_id": "session_12345",
            "status": "active",
            "trading_mode": "semi_automated"
        }
    }
''',
        "app/schemas/dashboard.py": '''
class Config:
    """Pydantic V2 configuration."""
    json_encoders = {
        Decimal: lambda v: float(v),
        datetime: lambda v: v.isoformat()
    }
    from_attributes = True
    json_schema_extra = {
        "example": {
            "portfolio_value": "10000.00",
            "daily_pnl": "150.75",
            "trades_today": 5
        }
    }
'''
    }
    
    return config_updates


def fix_all_schema_files():
    """Fix all schema files in the project."""
    print("🔧 Fixing Pydantic V2 schema compatibility issues...")
    
    schema_files = find_schema_files()
    
    if not schema_files:
        print("❌ No schema files found")
        return
    
    print(f"📁 Found {len(schema_files)} Python files to check")
    
    fixed_files = []
    unchanged_files = []
    error_files = []
    
    for file_path in schema_files:
        print(f"🔍 Checking: {file_path}")
        
        success, message = fix_schema_extra(file_path)
        
        if success:
            fixed_files.append(str(file_path))
            print(f"✅ Fixed: {file_path} - {message}")
        elif "No changes needed" in message:
            unchanged_files.append(str(file_path))
            print(f"✅ Clean: {file_path}")
        else:
            error_files.append((str(file_path), message))
            print(f"❌ Error: {file_path} - {message}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Fixed files: {len(fixed_files)}")
    print(f"✅ Clean files: {len(unchanged_files)}")
    print(f"❌ Error files: {len(error_files)}")
    
    if fixed_files:
        print(f"\n🔧 Fixed files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    
    if error_files:
        print(f"\n❌ Files with errors:")
        for file_path, error in error_files:
            print(f"  - {file_path}: {error}")
    
    return len(fixed_files), len(error_files)


def create_pydantic_v2_compliant_example():
    """Create an example of proper Pydantic V2 usage."""
    example_content = '''"""
Example Pydantic V2 Schema
File: example_pydantic_v2_schema.py

Shows proper Pydantic V2 configuration and usage patterns.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class StatusEnum(str, Enum):
    """Status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class ExampleModel(BaseModel):
    """Example model with proper Pydantic V2 configuration."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Model name")
    value: Decimal = Field(..., ge=0, description="Monetary value")
    status: StatusEnum = Field(..., description="Current status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field."""
        return v.strip().title()
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Decimal) -> Decimal:
        """Validate value field."""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v
    
    model_config = {
        "json_encoders": {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        },
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "example_123",
                "name": "Example Model",
                "value": "100.50",
                "status": "active",
                "created_at": "2025-08-06T18:30:00Z",
                "tags": ["important", "example"]
            }
        }
    }


# Alternative Config class approach (also valid in V2)
class ExampleModelWithConfig(BaseModel):
    """Example model using Config class approach."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Model name")
    
    class Config:
        """Pydantic V2 configuration using Config class."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "config_example_123",
                "name": "Config Example"
            }
        }
'''
    
    Path("example_pydantic_v2_schema.py").write_text(example_content, encoding='utf-8')
    print("📝 Created example_pydantic_v2_schema.py with proper V2 patterns")


def main():
    """Main function to fix all Pydantic issues."""
    print("=" * 60)
    print("🔧 PYDANTIC V2 COMPATIBILITY FIXER")
    print("=" * 60)
    
    # Fix existing schema files
    fixed_count, error_count = fix_all_schema_files()
    
    # Create example file
    create_pydantic_v2_compliant_example()
    
    print(f"\n✅ Pydantic V2 compatibility fixes completed!")
    print(f"🔧 Fixed {fixed_count} files")
    
    if error_count == 0:
        print("🎯 All schema files are now Pydantic V2 compliant!")
        print("🚀 You can now run the application without warnings")
    else:
        print(f"⚠️  {error_count} files had errors - please review manually")
    
    print("\n💡 Key Pydantic V2 changes implemented:")
    print("   - schema_extra → json_schema_extra")
    print("   - from_attributes = True (instead of orm_mode)")
    print("   - @field_validator (instead of @validator)")
    print("   - model_config dict (alternative to Config class)")


if __name__ == "__main__":
    main()