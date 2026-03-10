"""Add OTP fields to User

Revision ID: 2d1779c9469f
Revises: 74413c0941c3
Create Date: 2026-03-10 20:29:04.825930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d1779c9469f'
down_revision: Union[str, Sequence[str], None] = '74413c0941c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('otp_code', sa.String(length=6), nullable=True))
    op.add_column('users', sa.Column('otp_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'otp_expires_at')
    op.drop_column('users', 'otp_code')
