"""Utility helper functions."""

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
