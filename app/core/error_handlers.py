"""
Error Handlers Module
File: app/core/error_handlers.py

Comprehensive error handling for the FastAPI application.
Provides detailed error responses and logging.
"""

from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Application metadata
__phase__ = "4C - AI Risk Assessment Integration"


def setup_error_handlers(app: FastAPI) -> None:
    """
    Setup comprehensive error handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Raises:
        RuntimeError: If error handler setup fails critically
    """
    try:
        @app.exception_handler(500)
        async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
            """Handle internal server errors with detailed logging."""
            logger.error(f"Internal Server Error: {exc}")
            logger.error(f"Request URL: {request.url}")
            logger.error(f"Request method: {request.method}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An internal error occurred",
                    "type": "InternalServerError",
                    "phase": __phase__,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(404)
        async def not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
            """Handle 404 errors with helpful suggestions."""
            logger.warning(f"404 Not Found: {request.url}")
            
            # Check if AI endpoints are available
            try:
                ai_endpoints = []
                if hasattr(app.state, 'component_status'):
                    component_status = app.state.component_status
                    if component_status.get("ai_api_endpoints"):
                        ai_endpoints = ["/api/v1/ai-risk"]
                
                available_endpoints = [
                    "/", "/health", "/dashboard", "/risk-analysis", "/docs"
                ] + ai_endpoints
                
                return JSONResponse(
                    status_code=404,
                    content={
                        "error": "not_found",
                        "message": "Endpoint not found",
                        "suggestion": "Check /docs for available endpoints",
                        "available_endpoints": available_endpoints,
                        "ai_features": getattr(app.state, 'component_status', {}).get("ai_risk_assessment", False),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as error:
                logger.error(f"Error in 404 handler: {error}")
                return JSONResponse(
                    status_code=404,
                    content={
                        "error": "not_found",
                        "message": "Endpoint not found",
                        "suggestion": "Check /docs for available endpoints"
                    }
                )
        
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
            """Handle request validation errors with detailed information."""
            logger.warning(f"Validation error for {request.url}: {exc.errors()}")
            
            return JSONResponse(
                status_code=422,
                content={
                    "error": "validation_error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "body": exc.body,
                    "phase": __phase__,
                    "help": "Check the API documentation at /docs for correct request format",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
            """Handle general HTTP exceptions."""
            logger.warning(f"HTTP {exc.status_code} error for {request.url}: {exc.detail}")
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": f"http_{exc.status_code}",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "phase": __phase__,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(ValueError)
        async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
            """Handle value errors from business logic."""
            logger.warning(f"Value error for {request.url}: {exc}")
            
            return JSONResponse(
                status_code=400,
                content={
                    "error": "value_error",
                    "message": str(exc),
                    "type": "ValueError",
                    "suggestion": "Check your input parameters and try again",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(KeyError)
        async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
            """Handle key errors from missing parameters or data."""
            logger.warning(f"Key error for {request.url}: {exc}")
            
            return JSONResponse(
                status_code=400,
                content={
                    "error": "missing_parameter",
                    "message": f"Required parameter or data missing: {exc}",
                    "type": "KeyError",
                    "suggestion": "Check the API documentation for required parameters",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(ConnectionError)
        async def connection_error_handler(request: Request, exc: ConnectionError) -> JSONResponse:
            """Handle connection errors (network, database, etc.)."""
            logger.error(f"Connection error for {request.url}: {exc}")
            
            return JSONResponse(
                status_code=503,
                content={
                    "error": "connection_error",
                    "message": "Service temporarily unavailable due to connection issues",
                    "type": "ConnectionError",
                    "suggestion": "Please try again later or check system status at /health",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @app.exception_handler(TimeoutError)
        async def timeout_error_handler(request: Request, exc: TimeoutError) -> JSONResponse:
            """Handle timeout errors."""
            logger.warning(f"Timeout error for {request.url}: {exc}")
            
            return JSONResponse(
                status_code=504,
                content={
                    "error": "timeout_error",
                    "message": "Request timed out",
                    "type": "TimeoutError",
                    "suggestion": "The operation took too long. Please try again with smaller parameters or check system status",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        logger.info("Error handlers configured successfully")
        
    except Exception as error:
        logger.error(f"Error handlers setup failed: {error}")
        raise RuntimeError(f"Error handlers setup failed: {error}")


class ApplicationError(Exception):
    """Base class for application-specific errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        """
        Initialize application error.
        
        Args:
            message: Error message
            error_code: Optional error code
            details: Optional additional error details
        """
        self.message = message
        self.error_code = error_code or "application_error"
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }


class ComponentError(ApplicationError):
    """Error related to component loading or operation."""
    
    def __init__(self, component_name: str, message: str, details: Dict[str, Any] = None):
        """
        Initialize component error.
        
        Args:
            component_name: Name of the component that failed
            message: Error message
            details: Optional additional error details
        """
        self.component_name = component_name
        error_code = f"component_error_{component_name}"
        enhanced_details = details or {}
        enhanced_details["component"] = component_name
        
        super().__init__(message, error_code, enhanced_details)


class AIError(ApplicationError):
    """Error related to AI system operations."""
    
    def __init__(self, ai_system: str, message: str, details: Dict[str, Any] = None):
        """
        Initialize AI error.
        
        Args:
            ai_system: Name of the AI system that failed
            message: Error message
            details: Optional additional error details
        """
        self.ai_system = ai_system
        error_code = f"ai_error_{ai_system}"
        enhanced_details = details or {}
        enhanced_details["ai_system"] = ai_system
        
        super().__init__(message, error_code, enhanced_details)


class TradingError(ApplicationError):
    """Error related to trading operations."""
    
    def __init__(self, operation: str, message: str, details: Dict[str, Any] = None):
        """
        Initialize trading error.
        
        Args:
            operation: Trading operation that failed
            message: Error message
            details: Optional additional error details
        """
        self.operation = operation
        error_code = f"trading_error_{operation}"
        enhanced_details = details or {}
        enhanced_details["operation"] = operation
        
        super().__init__(message, error_code, enhanced_details)


class BlockchainError(ApplicationError):
    """Error related to blockchain operations."""
    
    def __init__(self, network: str, message: str, details: Dict[str, Any] = None):
        """
        Initialize blockchain error.
        
        Args:
            network: Blockchain network that failed
            message: Error message
            details: Optional additional error details
        """
        self.network = network
        error_code = f"blockchain_error_{network}"
        enhanced_details = details or {}
        enhanced_details["network"] = network
        
        super().__init__(message, error_code, enhanced_details)