"""
AssignMind — Invitation ORM Model

Workspace invitations sent by leaders to potential members.
"""

import uuid
from datetime import datetime

from typing import TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.workspace import Workspace

class Invitation(Base):
    """Pending invitation to join a workspace."""

    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    email: Mapped[str] = mapped_column(String(320))
    invited_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "email", name="uq_invitation_ws_email"
        ),
        Index("idx_invitations_email", "email"),
        Index("idx_invitations_workspace", "workspace_id"),
    )
