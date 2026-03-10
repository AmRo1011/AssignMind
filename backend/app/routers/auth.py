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

    OTP validation is handled via Twilio (backend).
    This endpoint records the verified phone, checks uniqueness,
    and grants 30 free credits on first verification.
    """
    phone = sanitize_and_trim(body.phone, max_length=20)

    from app.services import twilio_service
    if not await twilio_service.verify_otp(db, current_user, phone, body.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_otp",
                "message": "Invalid or expired OTP code.",
            },
        )

    is_unique = await user_service.check_phone_unique(
        db, phone, exclude_user_id=current_user.id
    )
    if not is_unique:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "phone_already_registered",
                "message": "This phone number is already registered",
            },
        )

    updated = await user_service.verify_phone(
        db, current_user, phone
    )
    from app.services import email_service
    background_tasks.add_task(email_service.send_account_activated, updated.email, updated.full_name, 30)

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

    OTP is sent via Twilio Programmable SMS.
    This endpoint enforces server-side rate limiting.
    """
    phone = sanitize_and_trim(body.phone, max_length=20)

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
        await twilio_service.send_otp(db, current_user, phone)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "twilio_error",
                "message": str(e),
                "traceback": traceback.format_exc(),
            },
        )

    return {"message": "OTP sent successfully"}


@router.get("/test-twilio")
def test_twilio_debug(phone: str):
    import traceback
    from twilio.rest import Client
    from app.config import get_settings
    settings = get_settings()
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        message = client.messages.create(
            messaging_service_sid=settings.twilio_messaging_service_sid,
            body="Your AssignMind verification code is: 123456",
            to=phone,
        )
        return {"sid": message.sid, "status": message.status}
    except Exception as e:
        return {"error_type": type(e).__name__, "message": str(e), "traceback": traceback.format_exc()}


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
