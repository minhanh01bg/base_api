"""
Error Handlers - Global error handlers cho FastAPI application.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import logging

from app.core.exceptions import BaseAppException
from app.schemas.api.errors import ErrorResponse

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Handler cho custom application exceptions.
    
    Args:
        request: FastAPI request
        exc: Custom exception
        
    Returns:
        JSON error response
    """
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "error_type": type(exc).__name__,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
        },
        exc_info=True,
    )
    
    error_response = ErrorResponse(
        success=False,
        error=exc.message,
        error_type=type(exc).__name__,
        status_code=exc.status_code,
        details=exc.details,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler cho Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation exception
        
    Returns:
        JSON error response
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Validation error"),
            "code": error.get("type", "validation_error"),
        })
    
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path},
    )
    
    error_response = ErrorResponse(
        success=False,
        error="Validation error",
        error_type="ValidationError",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler cho HTTP exceptions.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSON error response
    """
    error_response = ErrorResponse(
        success=False,
        error=exc.detail,
        error_type="HTTPException",
        status_code=exc.status_code,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler cho unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON error response
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True,
    )
    
    error_response = ErrorResponse(
        success=False,
        error="Internal server error",
        error_type=type(exc).__name__,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"message": str(exc)} if not isinstance(exc, BaseAppException) else None,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )

