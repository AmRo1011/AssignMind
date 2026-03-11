"""Remove OTP columns — migrate to Twilio Verify

OTP generation, storage, and expiry are now handled entirely by Twilio Verify.
The otp_code and otp_expires_at columns in the users table are no longer needed.

Revision ID: a1f3c8b2e5d0
Revises: 2d1779c9469f
Create Date: 2026-03-12 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1f3c8b2e5d0"
down_revision: Union[str, Sequence[str], None] = "2d1779c9469f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop OTP columns — Twilio Verify owns this state now."""
    op.drop_column("users", "otp_expires_at")
    op.drop_column("users", "otp_code")


def downgrade() -> None:
    """Restore OTP columns (for rollback only — prefer Twilio Verify)."""
    op.add_column(
        "users",
        sa.Column("otp_code", sa.String(length=6), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "otp_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
