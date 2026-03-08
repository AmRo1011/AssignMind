"""
AssignMind — Workspace Member ORM Model

Join table linking users to workspaces with role (leader/member).
"""

from __future__ import annotations

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
    from app.models.user import User
    from app.models.workspace import Workspace


class WorkspaceMember(Base):
    """Membership record linking a user to a workspace."""

    __tablename__ = "workspace_members"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(20), default="member")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    workspace: Mapped[Workspace] = relationship(
        back_populates="members"
    )
    user: Mapped[User] = relationship()

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_wm_ws_user"),
        Index("idx_wm_workspace", "workspace_id"),
        Index("idx_wm_user", "user_id"),
    )
