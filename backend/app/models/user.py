"""
AssignMind — User & Credit ORM Models

Users table: core identity linked to Supabase Auth.
Credits table: per-user balance with reserve-then-commit support.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Registered user linked to Supabase Auth."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    supabase_id: Mapped[uuid.UUID] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    avatar_url: Mapped[str | None] = mapped_column(Text, default=None)
    phone: Mapped[str | None] = mapped_column(
        String(20), unique=True, default=None
    )
    phone_verified: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="UTC"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    credit: Mapped["Credit"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_users_supabase_id", "supabase_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_phone", "phone"),
    )


class Credit(Base):
    """Per-user credit balance with reservation support."""

    __tablename__ = "credits"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    balance: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    free_credits_granted: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="credit")

    __table_args__ = (
        CheckConstraint("balance >= 0", name="chk_balance_gte_zero"),
        CheckConstraint("reserved >= 0", name="chk_reserved_gte_zero"),
        CheckConstraint(
            "reserved <= balance", name="chk_reserved_lte_balance"
        ),
    )
