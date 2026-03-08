"""
AssignMind — Payment Transaction ORM Model

Lemon Squeezy payment records for credit purchases.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PaymentTransaction(Base):
    """Record of a completed Lemon Squeezy payment."""

    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    lemon_squeezy_order_id: Mapped[str] = mapped_column(
        String(100), unique=True
    )
    package_name: Mapped[str] = mapped_column(String(50))
    credits_amount: Mapped[int] = mapped_column(Integer)
    amount_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(
        String(20), default="completed"
    )
    webhook_payload: Mapped[dict | None] = mapped_column(
        JSONB, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_payment_user", "user_id"),
    )
