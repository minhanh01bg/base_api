"""
Example API Schemas - Mẫu API request/response schemas.

Đây là ví dụ về cách định nghĩa API schemas.
Các schemas này được sử dụng trong FastAPI routes.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ExampleRequest(BaseModel):
    """
    Example request schema cho API endpoint.
    
    Attributes:
        message: Message từ user
        session_id: Optional session ID để track conversation
    """
    message: str = Field(..., description="User message", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class ExampleResponse(BaseModel):
    """
    Example response schema cho API endpoint.
    
    Attributes:
        success: Trạng thái thành công hay không
        message: Response message
        data: Optional data payload
    """
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data payload")

