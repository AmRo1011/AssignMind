"""
AssignMind — Task Schemas
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    deadline: Optional[datetime] = None
    status: str = "todo"
    is_ai_generated: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: UUID
    workspace_id: UUID
    position: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskDistributionRequest(BaseModel):
    manual_constraints: Optional[str] = Field(default=None, max_length=2000)

class TaskFinalizeRequest(BaseModel):
    tasks: List[TaskCreate] = Field(..., max_items=50)

class GeneratedTaskResponse(BaseModel):
    title: str
    description: str
    assigned_to: Optional[str] = None  # Full name or email initially
