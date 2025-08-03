"""
Core Exceptions Module
File: app/core/exceptions.py

Custom exception classes for the DEX Sniping platform with
comprehensive error handling and user-friendly error messages.
"""


class BaseTradingException(Exception):
    """Base exception class for all trading-related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "error_type": self.__class__.__name__,
            "details": self.details
        }


class TradingError(BaseTradingException):
    """General trading operation error."""
    pass


class InsufficientFundsError(BaseTradingException):
    """Raised when user has insufficient funds for operation."""
    
    def __init__(self, message: str, required_amount: float = None, available_amount: float = None):
        details = {}
        if required_amount is not None:
            details["required_amount"] = required_amount
        if available_amount is not None:
            details["available_amount"] = available_amount
        
        super().__init__(message, "INSUFFICIENT_FUNDS", details)


class InvalidOrderError(BaseTradingException):
    """Raised when order parameters are invalid."""
    
    def __init__(self, message: str, field: str = None, value=None):
        details = {}
        if field:
            details["invalid_field"] = field
        if value is not None:
            details["invalid_value"] = value
        
        super().__init__(message, "INVALID_ORDER", details)


class OrderExecutionError(BaseTradingException):
    """Raised when order execution fails."""
    
    def __init__(self, message: str, order_id: str = None, reason: str = None):
        details = {}
        if order_id:
            details["order_id"] = order_id
        if reason:
            details["failure_reason"] = reason
        
        super().__init__(message, "ORDER_EXECUTION_FAILED", details)


class OrderNotFoundError(BaseTradingException):
    """Raised when requested order is not found."""
    
    def __init__(self, order_id: str):
        message = f"Order {order_id} not found"
        details = {"order_id": order_id}
        super().__init__(message, "ORDER_NOT_FOUND", details)


class PortfolioError(BaseTradingException):
    """General portfolio management error."""
    pass


class PositionNotFoundError(BaseTradingException):
    """Raised when requested position is not found."""
    
    def __init__(self, token_address: str):
        message = f"Position for token {token_address} not found"
        details = {"token_address": token_address}
        super().__init__(message, "POSITION_NOT_FOUND", details)


class SlippageExceededError(BaseTradingException):
    """Raised when slippage exceeds tolerance."""
    
    def __init__(self, actual_slippage: float, max_slippage: float):
        message = f"Slippage {actual_slippage:.2%} exceeds maximum tolerance {max_slippage:.2%}"
        details = {
            "actual_slippage": actual_slippage,
            "max_slippage": max_slippage
        }
        super().__init__(message, "SLIPPAGE_EXCEEDED", details)


class NetworkError(BaseTradingException):
    """Raised when blockchain network operations fail."""
    
    def __init__(self, message: str, network: str = None, transaction_hash: str = None):
        details = {}
        if network:
            details["network"] = network
        if transaction_hash:
            details["transaction_hash"] = transaction_hash
        
        super().__init__(message, "NETWORK_ERROR", details)


class ContractError(BaseTradingException):
    """Raised when smart contract operations fail."""
    
    def __init__(self, message: str, contract_address: str = None, function_name: str = None):
        details = {}
        if contract_address:
            details["contract_address"] = contract_address
        if function_name:
            details["function_name"] = function_name
        
        super().__init__(message, "CONTRACT_ERROR", details)


class PriceValidationError(BaseTradingException):
    """Raised when price validation fails."""
    
    def __init__(self, message: str, expected_price: float = None, actual_price: float = None):
        details = {}
        if expected_price is not None:
            details["expected_price"] = expected_price
        if actual_price is not None:
            details["actual_price"] = actual_price
        
        super().__init__(message, "PRICE_VALIDATION_ERROR", details)


class RiskManagementError(BaseTradingException):
    """Raised when risk management rules are violated."""
    
    def __init__(self, message: str, rule_name: str = None, current_value=None, limit_value=None):
        details = {}
        if rule_name:
            details["rule_name"] = rule_name
        if current_value is not None:
            details["current_value"] = current_value
        if limit_value is not None:
            details["limit_value"] = limit_value
        
        super().__init__(message, "RISK_MANAGEMENT_ERROR", details)


class TokenValidationError(BaseTradingException):
    """Raised when token validation fails."""
    
    def __init__(self, message: str, token_address: str = None, validation_type: str = None):
        details = {}
        if token_address:
            details["token_address"] = token_address
        if validation_type:
            details["validation_type"] = validation_type
        
        super().__init__(message, "TOKEN_VALIDATION_ERROR", details)


class DEXError(BaseTradingException):
    """Raised when DEX operations fail."""
    
    def __init__(self, message: str, dex_name: str = None, pool_address: str = None):
        details = {}
        if dex_name:
            details["dex_name"] = dex_name
        if pool_address:
            details["pool_address"] = pool_address
        
        super().__init__(message, "DEX_ERROR", details)


class ArbitrageError(BaseTradingException):
    """Raised when arbitrage operations fail."""
    
    def __init__(self, message: str, opportunity_id: str = None, reason: str = None):
        details = {}
        if opportunity_id:
            details["opportunity_id"] = opportunity_id
        if reason:
            details["reason"] = reason
        
        super().__init__(message, "ARBITRAGE_ERROR", details)


class ConfigurationError(BaseTradingException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, config_value=None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = config_value
        
        super().__init__(message, "CONFIGURATION_ERROR", details)


class AuthenticationError(BaseTradingException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(BaseTradingException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Authorization failed", required_permission: str = None):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class RateLimitError(BaseTradingException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: int = None, limit_type: str = None):
        details = {}
        if retry_after is not None:
            details["retry_after"] = retry_after
        if limit_type:
            details["limit_type"] = limit_type
        
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class DataValidationError(BaseTradingException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field_name: str = None, validation_rule: str = None):
        details = {}
        if field_name:
            details["field_name"] = field_name
        if validation_rule:
            details["validation_rule"] = validation_rule
        
        super().__init__(message, "DATA_VALIDATION_ERROR", details)


class SystemOverloadError(BaseTradingException):
    """Raised when system is overloaded."""
    
    def __init__(self, message: str = "System is currently overloaded, please try again later"):
        super().__init__(message, "SYSTEM_OVERLOAD")


class MaintenanceError(BaseTradingException):
    """Raised when system is under maintenance."""
    
    def __init__(self, message: str = "System is under maintenance", estimated_completion: str = None):
        details = {}
        if estimated_completion:
            details["estimated_completion"] = estimated_completion
        
        super().__init__(message, "MAINTENANCE_ERROR", details)


# Exception mapping for HTTP status codes
EXCEPTION_STATUS_CODES = {
    BaseTradingException: 500,
    TradingError: 400,
    InsufficientFundsError: 400,
    InvalidOrderError: 400,
    OrderExecutionError: 500,
    OrderNotFoundError: 404,
    PortfolioError: 400,
    PositionNotFoundError: 404,
    SlippageExceededError: 400,
    NetworkError: 503,
    ContractError: 502,
    PriceValidationError: 400,
    RiskManagementError: 400,
    TokenValidationError: 400,
    DEXError: 502,
    ArbitrageError: 400,
    ConfigurationError: 500,
    AuthenticationError: 401,
    AuthorizationError: 403,
    RateLimitError: 429,
    DataValidationError: 400,
    SystemOverloadError: 503,
    MaintenanceError: 503
}


def get_http_status_code(exception: Exception) -> int:
    """Get appropriate HTTP status code for an exception."""
    for exception_type, status_code in EXCEPTION_STATUS_CODES.items():
        if isinstance(exception, exception_type):
            return status_code
    return 500  # Default to internal server error


def format_exception_response(exception: Exception) -> dict:
    """Format exception for API response."""
    if isinstance(exception, BaseTradingException):
        return exception.to_dict()
    else:
        return {
            "error": str(exception),
            "error_code": "INTERNAL_ERROR",
            "error_type": type(exception).__name__,
            "details": {}
        }