"""
AssignMind — Workspace Schemas
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse

class WorkspaceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    deadline: Optional[datetime] = None

class WorkspaceUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    deadline: Optional[datetime] = None

class WorkspaceMemberResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class WorkspaceResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    deadline: Optional[datetime]
    is_archived: bool
    archived_at: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    members: Optional[List[WorkspaceMemberResponse]] = None
    role: Optional[str] = None # Injected for context

    class Config:
        from_attributes = True

class TransferLeadershipRequest(BaseModel):
    new_leader_id: UUID
