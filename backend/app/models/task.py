"""
AssignMind — Task ORM Model

Kanban board tasks, either AI-generated or manually created.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Task(Base):
    """Kanban task assigned to a workspace member."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(
        Text, default=None
    )
    status: Mapped[str] = mapped_column(String(20), default="todo")
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), default=None
    )
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_ai_generated: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("idx_tasks_workspace", "workspace_id"),
        Index("idx_tasks_assigned", "assigned_to"),
        Index(
            "idx_tasks_deadline",
            "deadline",
            postgresql_where="deadline IS NOT NULL AND status != 'done'",
        ),
    )
