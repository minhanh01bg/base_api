"""
API Schemas - Pydantic models cho FastAPI requests và responses.

Các schemas này được sử dụng cho:
- Request validation
- Response serialization
- API documentation (OpenAPI/Swagger)
"""

from .example import ExampleRequest, ExampleResponse
from .errors import ErrorResponse, ErrorDetail
from .graph import SimpleGraphRequest, SimpleGraphResponse, SimpleGraphResult

__all__ = [
    "ExampleRequest",
    "ExampleResponse",
    "ErrorResponse",
    "ErrorDetail",
    "SimpleGraphRequest",
    "SimpleGraphResponse",
    "SimpleGraphResult",
]

