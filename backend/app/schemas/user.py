"""
AssignMind — User Pydantic Schemas

Request/response contracts for authentication and user endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Requests ──


class AuthCallbackRequest(BaseModel):
    """Data received after Supabase OAuth callback."""

    supabase_id: UUID
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=200)
    avatar_url: str | None = None


class VerifyPhoneRequest(BaseModel):
    """Phone verification with OTP code."""

    phone: str = Field(
        min_length=7,
        max_length=20,
        pattern=r"^\+\d{7,15}$",
        description="E.164 format: +[country][number]",
    )
    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit OTP code",
    )


class ResendOtpRequest(BaseModel):
    """Request to resend phone verification OTP."""

    phone: str = Field(
        min_length=7,
        max_length=20,
        pattern=r"^\+\d{7,15}$",
    )


class UpdateProfileRequest(BaseModel):
    """Update editable profile fields."""

    full_name: str | None = Field(
        default=None, min_length=1, max_length=200
    )
    timezone: str | None = Field(default=None, max_length=50)


# ── Responses ──


class UserResponse(BaseModel):
    """Public user profile returned by API."""

    id: UUID
    email: str
    full_name: str
    avatar_url: str | None
    phone: str | None
    phone_verified: bool
    timezone: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


from pydantic import computed_field

class UserWithCreditsResponse(UserResponse):
    """User profile with credit balance."""

    credit_balance: int = 0
    credit_reserved: int = 0

    @computed_field
    def credit_available(self) -> int:
        """Credits available for new operations."""
        return self.credit_balance - self.credit_reserved

    @computed_field
    def low_credit_warning(self) -> bool:
        """Flag indicating ≤10 available credits."""
        return self.credit_available <= 10


class AuthCallbackResponse(BaseModel):
    """Response after successful auth callback."""

    user: UserResponse
    is_new: bool
