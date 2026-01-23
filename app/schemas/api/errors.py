"""
Error Response Schemas - Pydantic models cho error responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ErrorDetail(BaseModel):
    """Error detail schema."""
    field: Optional[str] = Field(None, description="Field name if validation error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """
    Standard error response schema cho API.
    
    Attributes:
        success: Always False for errors
        error: Error message
        error_type: Type of error (exception class name)
        status_code: HTTP status code
        details: Additional error details
        errors: List of error details (for validation errors)
    """
    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    status_code: int = Field(..., description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    errors: Optional[list[ErrorDetail]] = Field(None, description="List of validation errors")

