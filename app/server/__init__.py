# File: app/server/__init__.py
"""
Server package for FastAPI application components.
"""

from .application import create_application, get_trading_engine
from .middleware import setup_middleware
from .routes import setup_routes

__all__ = [
    "create_application",
    "get_trading_engine", 
    "setup_middleware",
    "setup_routes",
]