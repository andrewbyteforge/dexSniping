"""
Input Validation System
File: app/core/security/input_validator.py
Class: InputValidator
Methods: validate_data, sanitize_input, check_sql_injection

Professional input validation and sanitization system.
"""

import re
import html
import json
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidationError(Exception):
    """Input validation error."""
    pass


class InputValidator:
    """
    Professional input validation and sanitization system.
    
    Features:
    - Data type validation
    - SQL injection prevention
    - XSS protection
    - Format validation
    - Range checking
    - Sanitization
    """
    
    def __init__(self):
        """Initialize input validator."""
        self.initialized = False
        
        # Dangerous patterns to detect
        self.sql_patterns = [
            r"union\s+select", r"drop\s+table", r"delete\s+from",
            r"insert\s+into", r"update\s+set", r"create\s+table",
            r"alter\s+table", r"exec\s*\(", r"script\s*>",
            r"<\s*script", r"javascript:", r"vbscript:"
        ]
        
        logger.info("[VALIDATION] InputValidator initialized")
    
    async def initialize(self) -> bool:
        """Initialize the input validation system."""
        try:
            self.initialized = True
            logger.info("[OK] InputValidator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] InputValidator initialization failed: {e}")
            return False
    
    def validate_wallet_address(self, address: str) -> str:
        """Validate and sanitize wallet address."""
        try:
            if not isinstance(address, str):
                raise ValidationError("Address must be a string")
            
            # Remove whitespace
            address = address.strip()
            
            # Check length
            if len(address) != 42:
                raise ValidationError("Invalid address length")
            
            # Check format
            if not address.startswith('0x'):
                raise ValidationError("Address must start with 0x")
            
            # Validate hex characters
            try:
                int(address[2:], 16)
            except ValueError:
                raise ValidationError("Invalid hex characters")
            
            return address.lower()
            
        except Exception as e:
            logger.error(f"[ERROR] Address validation failed: {e}")
            raise ValidationError(f"Address validation failed: {str(e)}")
    
    def validate_amount(self, amount: Union[str, int, float, Decimal]) -> Decimal:
        """Validate and convert amount to Decimal."""
        try:
            if amount is None:
                raise ValidationError("Amount cannot be None")
            
            # Convert to Decimal
            if isinstance(amount, str):
                # Remove common formatting
                amount = amount.replace(',', '').strip()
                
                # Check for dangerous patterns
                if self._contains_dangerous_patterns(amount):
                    raise ValidationError("Invalid characters in amount")
            
            decimal_amount = Decimal(str(amount))
            
            # Validate range
            if decimal_amount < 0:
                raise ValidationError("Amount cannot be negative")
            
            if decimal_amount > Decimal('1000000'):
                raise ValidationError("Amount too large")
            
            return decimal_amount
            
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid amount format: {str(e)}")
        except Exception as e:
            logger.error(f"[ERROR] Amount validation failed: {e}")
            raise ValidationError(f"Amount validation failed: {str(e)}")
    
    def validate_token_symbol(self, symbol: str) -> str:
        """Validate token symbol."""
        try:
            if not isinstance(symbol, str):
                raise ValidationError("Symbol must be a string")
            
            symbol = symbol.strip().upper()
            
            # Check length
            if len(symbol) < 1 or len(symbol) > 10:
                raise ValidationError("Symbol length must be 1-10 characters")
            
            # Check format (alphanumeric only)
            if not re.match(r'^[A-Z0-9]+$', symbol):
                raise ValidationError("Symbol must contain only alphanumeric characters")
            
            return symbol
            
        except Exception as e:
            logger.error(f"[ERROR] Symbol validation failed: {e}")
            raise ValidationError(f"Symbol validation failed: {str(e)}")
    
    def sanitize_string(self, text: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            # Remove dangerous patterns
            if self._contains_dangerous_patterns(text):
                logger.warning("[SECURITY] Dangerous pattern detected in input")
                text = self._remove_dangerous_patterns(text)
            
            # HTML escape
            text = html.escape(text)
            
            # Limit length
            if len(text) > max_length:
                text = text[:max_length]
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"[ERROR] String sanitization failed: {e}")
            return ""
    
    def _contains_dangerous_patterns(self, text: str) -> bool:
        """Check if text contains dangerous SQL/XSS patterns."""
        try:
            text_lower = text.lower()
            
            for pattern in self.sql_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception:
            return True  # Assume dangerous on error
    
    def _remove_dangerous_patterns(self, text: str) -> str:
        """Remove dangerous patterns from text."""
        try:
            for pattern in self.sql_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            return text
            
        except Exception:
            return ""  # Return empty on error
    
    def validate_json_input(self, data: str) -> Dict[str, Any]:
        """Validate and parse JSON input."""
        try:
            if not isinstance(data, str):
                raise ValidationError("JSON data must be a string")
            
            # Check for dangerous patterns
            if self._contains_dangerous_patterns(data):
                raise ValidationError("Dangerous patterns detected in JSON")
            
            # Parse JSON
            parsed_data = json.loads(data)
            
            # Validate structure
            if not isinstance(parsed_data, dict):
                raise ValidationError("JSON must be an object")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            logger.error(f"[ERROR] JSON validation failed: {e}")
            raise ValidationError(f"JSON validation failed: {str(e)}")
    
    def validate_trading_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trading parameters."""
        try:
            validated_params = {}
            
            # Validate required fields
            required_fields = ['token_address', 'amount', 'action']
            
            for field in required_fields:
                if field not in params:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Validate each field
            validated_params['token_address'] = self.validate_wallet_address(params['token_address'])
            validated_params['amount'] = self.validate_amount(params['amount'])
            validated_params['action'] = self.sanitize_string(params['action'], 20)
            
            # Validate optional fields
            if 'slippage' in params:
                slippage = self.validate_amount(params['slippage'])
                if slippage > Decimal('50'):
                    raise ValidationError("Slippage too high (max 50%)")
                validated_params['slippage'] = slippage
            
            if 'deadline' in params:
                validated_params['deadline'] = self.sanitize_string(params['deadline'], 50)
            
            return validated_params
            
        except Exception as e:
            logger.error(f"[ERROR] Trading params validation failed: {e}")
            raise ValidationError(f"Trading params validation failed: {str(e)}")
    
    async def get_validation_status(self) -> Dict[str, Any]:
        """Get validation system status."""
        try:
            return {
                "system_status": "operational",
                "features": [
                    "SQL injection prevention",
                    "XSS protection",
                    "Data type validation",
                    "Range checking",
                    "Input sanitization"
                ],
                "patterns_checked": len(self.sql_patterns),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get validation status: {e}")
            return {"system_status": "error", "error": str(e)}


# Global instance
input_validator = InputValidator()


async def get_input_validator() -> InputValidator:
    """Get the global input validator instance."""
    if not input_validator.initialized:
        await input_validator.initialize()
    return input_validator
