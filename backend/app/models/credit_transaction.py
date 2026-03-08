"""
AssignMind — Credit Transaction ORM Model

Immutable ledger of all credit movements (grants, purchases,
reservations, commits, releases, refunds, forfeits).
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


class CreditTransaction(Base):
    """Single entry in the credit transaction ledger."""

    __tablename__ = "credit_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(
        Text, default=None
    )
    reference_id: Mapped[str | None] = mapped_column(
        String(100), default=None
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"),
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index(
            "idx_credit_tx_user",
            "user_id",
            "created_at",
        ),
        Index("idx_credit_tx_ref", "reference_id"),
    )
