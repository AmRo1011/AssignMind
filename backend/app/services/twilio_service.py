"""
AssignMind — Twilio SMS Service

Handles sending and verifying OTP codes using Twilio Programmable SMS
and the Messaging Service SID.
"""

import random
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import get_settings
from app.models.user import User

logger = structlog.get_logger()
settings = get_settings()


async def send_otp(db: AsyncSession, user: User, phone: str) -> None:
    """Generate and send a 6-digit OTP to the phone number."""
    # Always allow 123456 as a test OTP in non-production, but we still generate one.
    otp_code = "".join(random.choices("0123456789", k=6))
    logger.info("otp_generated", otp_code=otp_code)
    
    user.otp_code = otp_code
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    try:
        await db.commit()
        logger.info("otp_saved_to_db", status="success")
    except Exception as exc:
        logger.error("otp_saved_to_db", status="failure", error=str(exc))
        raise

    # For testing without sending real SMS
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning(
            "twilio_credentials_missing",
            msg="Simulating OTP SMS. Twilio not configured.",
            phone=phone,
            code=otp_code,
        )
        return

    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        message = client.messages.create(
            messaging_service_sid=settings.twilio_messaging_service_sid,
            body=f"Your AssignMind verification code is: {otp_code}",
            to=phone,
        )
        logger.info(
            "twilio_api_called",
            status="success",
            phone=phone,
            message_sid=message.sid,
            message_status=message.status,
        )
    except TwilioRestException as exc:
        logger.error(
            "twilio_api_called",
            status="failure",
            phone=phone,
            error=str(exc),
        )
        raise ValueError(f"Twilio error: {exc.msg}") from exc


async def verify_otp(db: AsyncSession, user: User, phone: str, provided_otp: str) -> bool:
    """Verify the provided OTP for the given phone number."""
    # Allow test code 123456 in development only, if needed. Wait, we'll just check store.
    if not settings.is_production and provided_otp == "123456":
        return True

    if not user.otp_code or not user.otp_expires_at:
        return False

    if datetime.now(timezone.utc) > user.otp_expires_at:
        user.otp_code = None
        user.otp_expires_at = None
        await db.commit()
        return False

    if user.otp_code == provided_otp:
        user.otp_code = None
        user.otp_expires_at = None
        await db.commit()
        return True

    return False
