"""
Example API Route - Mẫu cách tạo API routes với base structure.
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_settings
from app.services.base_service import BaseService
from app.schemas.api.example import ExampleRequest, ExampleResponse

router = APIRouter()


@router.post("/example", response_model=ExampleResponse)
async def example_endpoint(
    request: ExampleRequest,
    settings=Depends(get_settings),
):
    """
    Example endpoint sử dụng base structure.
    
    Args:
        request: Request body
        settings: Settings dependency
        
    Returns:
        Example response
    """
    try:
        # Example logic
        result = {
            "processed_message": request.message.upper(),
            "app_name": settings.app_name,
        }
        
        return ExampleResponse(
            success=True,
            message="Request processed successfully",
            data=result,
        )
    except Exception as e:
        return ExampleResponse(
            success=False,
            message=f"Error: {str(e)}",
            data=None,
        )


@router.get("/example/health")
async def example_health():
    """Example health check endpoint."""
    return {"status": "ok", "service": "example"}

