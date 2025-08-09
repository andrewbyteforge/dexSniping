"""WebSocket management module."""

try:
    from .websocket_manager import WebSocketManager, get_websocket_manager
    __all__ = ['WebSocketManager', 'get_websocket_manager']
except ImportError:
    # Fallback if websocket_manager not available
    class WebSocketManager:
        def __init__(self):
            pass
        def connect(self, *args, **kwargs):
            return False
        def disconnect(self, *args, **kwargs):
            return True
    
    def get_websocket_manager():
        return WebSocketManager()
    
    __all__ = ['WebSocketManager', 'get_websocket_manager']
