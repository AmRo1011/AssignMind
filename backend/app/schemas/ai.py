"""
AssignMind — AI Schemas

Pydantic models for structured output from the Prompt Engine.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

class AssignmentSummary(BaseModel):
    """
    Structured metadata representing an analyzed assignment document.
    Stored inside PostgreSQL JSONB.
    """
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    deadlines: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)

class GeneratedTask(BaseModel):
    """A task generated from a task distribution prompt."""
    title: str
    description: str
    assigned_to: Optional[str] = None
