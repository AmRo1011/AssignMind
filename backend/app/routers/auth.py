"""
AssignMind — Auth Router

Authentication endpoints for Supabase OAuth callback,
phone verification, and user profile retrieval.
Every endpoint validates auth (Constitution §V) except where noted.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    AuthCallbackRequest,
    AuthCallbackResponse,
    ResendOtpRequest,
    UserResponse,
    UserWithCreditsResponse,
    VerifyPhoneRequest,
)
from app.services import user_service
from app.utils.rate_limit import RateLimitExceeded, rate_limiter
from app.utils.sanitize import sanitize_and_trim

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/callback",
    response_model=AuthCallbackResponse,
    status_code=status.HTTP_200_OK,
)
async def auth_callback(
    body: AuthCallbackRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AuthCallbackResponse:
    """
    Receive user data after Supabase OAuth and upsert into DB.

    Called by the frontend after a successful Google/GitHub login.
    No Bearer token needed — the callback itself establishes identity.
    """
    user, is_new = await user_service.create_or_update_user(
        db=db,
        supabase_id=body.supabase_id,
        email=body.email,
        full_name=body.full_name,
        avatar_url=body.avatar_url,
    )
    if is_new:
        from app.services import email_service
        background_tasks.add_task(email_service.send_welcome_verification, user.email, user.full_name)
        
    return AuthCallbackResponse(
        user=UserResponse.model_validate(user),
        is_new=is_new,
    )


@router.post(
    "/verify-phone",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_phone(
    body: VerifyPhoneRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Verify phone number with OTP.

    OTP validation is handled via Twilio Verify (backend).
    Allows re-verification of a phone already owned by the same user.
    Rejects with 409 only when the phone belongs to a different user.
    Grants 30 free credits on first successful verification.
    """
    phone = sanitize_and_trim(body.phone, max_length=20)

    from app.services import twilio_service
    if not await twilio_service.verify_otp(phone, body.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_otp",
                "message": "Invalid or expired OTP code.",
            },
        )

    owner = await user_service.get_phone_owner(db, phone)
    if owner is not None and owner.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "phone_already_in_use",
                "message": "Phone number already in use",
            },
        )

    updated = await user_service.verify_phone(db, current_user, phone)
    from app.services import email_service
    background_tasks.add_task(
        email_service.send_account_activated,
        updated.email,
        updated.full_name,
        30,
    )

    return UserResponse.model_validate(updated)


@router.post(
    "/resend-otp",
    status_code=status.HTTP_200_OK,
)
async def resend_otp(
    body: ResendOtpRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Request OTP resend. Rate-limited to 3 per 10 minutes per phone.

    OTP is sent via Twilio Verify API.
    This endpoint enforces server-side rate limiting.
    """
    phone = sanitize_and_trim(body.phone, max_length=20)

    import structlog
    logger = structlog.get_logger()
    logger.info("resend_otp_request_received", phone=phone)

    try:
        rate_limiter.check(
            phone, "resend_otp", max_calls=3, window_seconds=600
        )
    except RateLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "rate_limit_exceeded",
                "message": "Too many OTP requests. Try again later.",
            },
        )

    try:
        from app.services import twilio_service
        await twilio_service.send_otp(phone)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "twilio_error",
                "message": str(e),
            },
        )

    return {"message": "OTP sent successfully"}


@router.get(
    "/me",
    response_model=UserWithCreditsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithCreditsResponse:
    """Return the current user's profile with credit balance."""
    credit = await user_service.get_user_credit(
        db, current_user.id
    )

    data = UserResponse.model_validate(current_user).model_dump()
    data["credit_balance"] = credit.balance if credit else 0
    data["credit_reserved"] = credit.reserved if credit else 0

    return UserWithCreditsResponse(**data)
