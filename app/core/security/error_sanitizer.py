"""
Error Sanitization System
File: app/core/security/error_sanitizer.py
Class: ErrorSanitizer
Methods: sanitize_error, safe_error_response, log_secure

Professional error sanitization to prevent information leakage.
"""

import re
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ErrorLevel(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorSanitizer:
    """
    Professional error sanitization system.
    
    Features:
    - Sensitive data removal
    - Safe error messages
    - Stack trace sanitization
    - Information leakage prevention
    - Secure logging
    """
    
    def __init__(self):
        """Initialize error sanitizer."""
        self.initialized = False
        
        # Sensitive patterns to remove from errors
        self.sensitive_patterns = [
            r'password[=:\s]+[^\s]+',
            r'api[_-]?key[=:\s]+[^\s]+',
            r'secret[=:\s]+[^\s]+',
            r'token[=:\s]+[^\s]+',
            r'private[_-]?key[=:\s]+[^\s]+',
            r'0x[a-fA-F0-9]{40}',  # Ethereum addresses
            r'[a-fA-F0-9]{64}',    # Potential private keys
            r'/home/[^\s]+',       # File paths
            r'C:\\[^\s]+',       # Windows paths
        ]
        
        logger.info("[SANITIZER] ErrorSanitizer initialized")
    
    async def initialize(self) -> bool:
        """Initialize the error sanitization system."""
        try:
            self.initialized = True
            logger.info("[OK] ErrorSanitizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] ErrorSanitizer initialization failed: {e}")
            return False
    
    def sanitize_error_message(self, error: Exception) -> str:
        """Sanitize error message for safe public display."""
        try:
            error_str = str(error)
            
            # Remove sensitive information
            sanitized = self._remove_sensitive_data(error_str)
            
            # Provide generic messages for common errors
            sanitized = self._genericize_common_errors(sanitized)
            
            # Limit length
            if len(sanitized) > 200:
                sanitized = sanitized[:200] + "..."
            
            return sanitized
            
        except Exception:
            return "An error occurred while processing your request"
    
    def _remove_sensitive_data(self, text: str) -> str:
        """Remove sensitive data patterns from text."""
        try:
            for pattern in self.sensitive_patterns:
                text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
            
            return text
            
        except Exception:
            return "[ERROR SANITIZATION FAILED]"
    
    def _genericize_common_errors(self, error_msg: str) -> str:
        """Convert specific errors to generic safe messages."""
        try:
            error_lower = error_msg.lower()
            
            # Database errors
            if any(db_term in error_lower for db_term in ['database', 'sql', 'connection']):
                return "Database operation failed"
            
            # Network errors
            if any(net_term in error_lower for net_term in ['network', 'timeout', 'connection']):
                return "Network operation failed"
            
            # Authentication errors
            if any(auth_term in error_lower for auth_term in ['unauthorized', 'forbidden', 'permission']):
                return "Authentication failed"
            
            # File system errors
            if any(file_term in error_lower for file_term in ['file', 'directory', 'path']):
                return "File operation failed"
            
            # Trading errors
            if any(trade_term in error_lower for trade_term in ['balance', 'insufficient', 'slippage']):
                return "Trading operation failed"
            
            return error_msg
            
        except Exception:
            return "Operation failed"
    
    def create_safe_error_response(
        self, 
        error: Exception, 
        error_level: ErrorLevel = ErrorLevel.ERROR,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Create a safe error response for API endpoints."""
        try:
            # Generate error ID for tracking
            error_id = self._generate_error_id()
            
            # Sanitize error message
            safe_message = self.sanitize_error_message(error)
            
            response = {
                "success": False,
                "error": {
                    "message": safe_message,
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": error_level.value
                }
            }
            
            # Only include details in development/debug mode
            if include_details:
                response["error"]["type"] = type(error).__name__
            
            # Log detailed error securely
            self._log_error_securely(error, error_id)
            
            return response
            
        except Exception as e:
            # Fallback error response
            return {
                "success": False,
                "error": {
                    "message": "An unexpected error occurred",
                    "error_id": "FALLBACK",
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": ErrorLevel.ERROR.value
                }
            }
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID for tracking."""
        import uuid
        return str(uuid.uuid4())[:8].upper()
    
    def _log_error_securely(self, error: Exception, error_id: str) -> None:
        """Log error with full details for debugging (secure internal log)."""
        try:
            # Get stack trace
            stack_trace = traceback.format_exc()
            
            # Sanitize stack trace for logging
            sanitized_trace = self._remove_sensitive_data(stack_trace)
            
            # Log with error ID for correlation
            logger.error(f"[ERROR-{error_id}] {type(error).__name__}: {str(error)}")
            logger.error(f"[TRACE-{error_id}] {sanitized_trace}")
            
        except Exception:
            logger.error(f"[ERROR-{error_id}] Failed to log error details")
    
    def sanitize_log_message(self, message: str) -> str:
        """Sanitize log message before writing to logs."""
        try:
            return self._remove_sensitive_data(message)
            
        except Exception:
            return "[LOG SANITIZATION FAILED]"
    
    async def get_sanitization_status(self) -> Dict[str, Any]:
        """Get error sanitization system status."""
        try:
            return {
                "system_status": "operational",
                "features": [
                    "Error message sanitization",
                    "Sensitive data removal",
                    "Stack trace cleaning",
                    "Safe error responses",
                    "Secure logging"
                ],
                "patterns_monitored": len(self.sensitive_patterns),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get sanitization status: {e}")
            return {"system_status": "error", "error": str(e)}


# Global instance
error_sanitizer = ErrorSanitizer()


async def get_error_sanitizer() -> ErrorSanitizer:
    """Get the global error sanitizer instance."""
    if not error_sanitizer.initialized:
        await error_sanitizer.initialize()
    return error_sanitizer
