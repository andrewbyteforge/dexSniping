"""
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
