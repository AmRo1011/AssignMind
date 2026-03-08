"""
AssignMind — Assignment ORM Model

Uploaded assignment documents with AI-generated structured summaries.
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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Assignment(Base):
    """Uploaded assignment with extracted text and AI summary."""

    __tablename__ = "assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    original_filename: Mapped[str] = mapped_column(String(500))
    file_url: Mapped[str | None] = mapped_column(Text, default=None)
    raw_text: Mapped[str] = mapped_column(Text)
    structured_summary: Mapped[dict] = mapped_column(JSONB)
    detected_language: Mapped[str] = mapped_column(
        String(5), default="en"
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "version", name="uq_assignment_ws_version"
        ),
        Index("idx_assignments_workspace", "workspace_id"),
        Index(
            "idx_assignments_summary",
            "structured_summary",
            postgresql_using="gin",
        ),
    )
