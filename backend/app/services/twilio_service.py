"""
AssignMind — Twilio Verify Service

Handles sending and verifying OTP codes using Twilio Verify API.
Twilio Verify manages OTP generation, delivery, and expiry automatically —
no OTP storage in the application database is required.
"""

import structlog
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


def _get_twilio_client() -> Client:
    """Instantiate and return a Twilio REST client."""
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


async def send_otp(phone: str) -> None:
    """
    Trigger a Twilio Verify OTP delivery to the given phone number.

    Twilio Verify handles code generation, SMS delivery, and expiry.
    No OTP is stored in the application database.
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning(
            "twilio_credentials_missing",
            msg="Simulating OTP send. Twilio not configured.",
            phone=phone,
        )
        return

    if not settings.twilio_verify_service_sid:
        logger.warning(
            "twilio_verify_sid_missing",
            msg="TWILIO_VERIFY_SERVICE_SID not configured.",
            phone=phone,
        )
        return

    try:
        client = _get_twilio_client()
        verification = client.verify.v2.services(
            settings.twilio_verify_service_sid
        ).verifications.create(to=phone, channel="sms")
        logger.info(
            "twilio_verify_send",
            status=verification.status,
            phone=phone,
            sid=verification.sid,
        )
    except TwilioRestException as exc:
        logger.error(
            "twilio_verify_send_failed",
            phone=phone,
            error=str(exc),
        )
        raise ValueError(f"Twilio Verify error: {exc.msg}") from exc


async def verify_otp(phone: str, otp_code: str) -> bool:
    """
    Check the provided OTP code via Twilio Verify.

    Returns True if the code is approved, False otherwise.
    Twilio Verify handles expiry and attempt-limit enforcement automatically.
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning(
            "twilio_credentials_missing",
            msg="Twilio not configured — rejecting OTP in production guard.",
            phone=phone,
        )
        return False

    if not settings.twilio_verify_service_sid:
        logger.warning(
            "twilio_verify_sid_missing",
            msg="TWILIO_VERIFY_SERVICE_SID not configured.",
            phone=phone,
        )
        return False

    try:
        client = _get_twilio_client()
        result = client.verify.v2.services(
            settings.twilio_verify_service_sid
        ).verification_checks.create(to=phone, code=otp_code)
        approved = result.status == "approved"
        logger.info(
            "twilio_verify_check",
            status=result.status,
            approved=approved,
            phone=phone,
        )
        return approved
    except TwilioRestException as exc:
        logger.error(
            "twilio_verify_check_failed",
            phone=phone,
            error=str(exc),
        )
        raise ValueError(f"Twilio Verify check error: {exc.msg}") from exc
