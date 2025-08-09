"""
Blockchain Module
File: app/core/blockchain/__init__.py

Blockchain connectivity and network management components.
"""

from .network_manager import NetworkManager, NetworkType, get_network_manager

__all__ = [
    "NetworkManager",
    "NetworkType", 
    "get_network_manager"
]

__version__ = "5.0.0-alpha"
__description__ = "Blockchain connectivity components for DEX Sniper Pro"