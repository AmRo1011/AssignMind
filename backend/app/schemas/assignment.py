"""
AssignMind — Assignment Pydantic Schemas

Schemas for returning uploaded documents and AI analysis summaries.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from app.schemas.ai import AssignmentSummary

class AssignmentResponse(BaseModel):
    """Schema representing an uploaded and analyzed assignment."""
    id: UUID
    workspace_id: UUID
    version: int
    original_filename: str
    file_url: Optional[str] = None
    structured_summary: AssignmentSummary
    detected_language: str
    uploaded_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
