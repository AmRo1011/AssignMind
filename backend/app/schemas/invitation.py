"""
AssignMind — Invitation Schemas 
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# Circular import prevention, we redefine simple workspace response
class MinimalWorkspace(BaseModel):
    id: UUID
    title: str

class InvitationCreate(BaseModel):
    email: EmailStr

class InvitationResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    email: str
    invited_by: UUID
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InvitationWithWorkspaceResponse(InvitationResponse):
    workspace: Optional[MinimalWorkspace] = None

    class Config:
        from_attributes = True
