"""
AssignMind — Common Pydantic Schemas

Shared request/response models used across all API endpoints.
"""

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error detail returned by all error responses."""

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error: ErrorDetail


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(
        default=20, ge=1, le=100, description="Items per page"
    )

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET from page and per_page."""
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")


class HealthResponse(BaseModel):
    """Health check endpoint response."""

    status: str
    database: str
    version: str = "1.0.0"


class MessageResponse(BaseModel):
    """Simple success message response."""

    message: str


class IDResponse(BaseModel):
    """Response containing a single UUID identifier."""

    id: UUID
