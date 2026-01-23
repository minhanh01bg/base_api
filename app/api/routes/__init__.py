"""
API Routes module - Tổng hợp tất cả API routes.
"""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Include example router
from .example import router as example_router

api_router.include_router(example_router, prefix="/example", tags=["example"])

# Include graph router (SimpleGraph API)
from .graph import router as graph_router

api_router.include_router(graph_router, prefix="/graph", tags=["graph"])

__all__ = ["api_router"]

