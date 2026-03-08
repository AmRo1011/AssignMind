"""
AssignMind — Pydantic Schemas

API request/response contracts. Import from submodules.
"""

from app.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    IDResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "IDResponse",
    "MessageResponse",
    "PaginatedResponse",
    "PaginationParams",
]
