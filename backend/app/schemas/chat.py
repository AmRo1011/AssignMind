"""
AssignMind — Chat Schemas

Pydantic models for group chat functionality.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ChatMessageCreate(BaseModel):
    content: str = Field(..., max_length=5000)

class ChatMessageResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    sender_id: Optional[UUID] = None
    sender_type: str
    sender_name: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
