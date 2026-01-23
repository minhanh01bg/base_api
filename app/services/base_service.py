"""
Base Service class - Abstract base class cho tất cả services.
"""
from abc import ABC
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base class cho tất cả service implementations.
    
    Cung cấp:
    - Common logging
    - Error handling patterns
    - Validation helpers
    """
    
    def __init__(self):
        """Initialize base service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _validate_input(self, **kwargs) -> None:
        """
        Validate input parameters (override in subclasses).
        
        Args:
            **kwargs: Input parameters to validate
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def _handle_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle errors consistently across services.
        
        Args:
            error: Exception that occurred
            context: Additional context for logging
            
        Returns:
            Error response dictionary
        """
        self.logger.error(
            f"Error in {self.__class__.__name__}: {str(error)}",
            extra=context,
            exc_info=True,
        )
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
        }
    
    def _create_success_response(
        self, data: Any, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized success response.
        
        Args:
            data: Response data
            message: Optional success message
            
        Returns:
            Success response dictionary
        """
        response = {
            "success": True,
            "data": data,
        }
        if message:
            response["message"] = message
        return response

