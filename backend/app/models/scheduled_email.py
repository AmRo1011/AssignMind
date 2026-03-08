"""
AssignMind — Scheduled Email ORM Model

Queue for deadline reminder and missed-deadline emails.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
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


class ScheduledEmail(Base):
    """Queued email scheduled for future delivery."""

    __tablename__ = "scheduled_emails"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        default=None,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        default=None,
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    email_type: Mapped[str] = mapped_column(String(30))
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(
        Text, default=None
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index(
            "idx_scheduled_pending",
            "scheduled_for",
            postgresql_where="status = 'pending'",
        ),
        Index("idx_scheduled_task", "task_id"),
    )
