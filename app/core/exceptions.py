"""
Custom Exceptions - Custom exception classes cho application.
"""
from typing import Optional, Dict, Any


class BaseAppException(Exception):
    """
    Base exception cho tất cả custom exceptions.
    
    Attributes:
        message: Error message
        status_code: HTTP status code (nếu liên quan đến API)
        details: Additional error details
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAppException):
    """Exception cho validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(BaseAppException):
    """Exception cho resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class DatabaseError(BaseAppException):
    """Exception cho database errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class GraphExecutionError(BaseAppException):
    """Exception cho graph execution errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class LLMError(BaseAppException):
    """Exception cho LLM API errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, details=details)


class ConfigurationError(BaseAppException):
    """Exception cho configuration errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)

