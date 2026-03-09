"""
AssignMind — Twilio SMS Service

Handles sending and verifying OTP codes using Twilio Programmable SMS
and the Messaging Service SID.
"""

import random
import time
from threading import Lock

import structlog
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# In-memory OTP store for MVP (use Redis for production)
# Format: { phone: {"otp": str, "expires_at": float} }
_otp_store: dict[str, dict[str, any]] = {}
_store_lock = Lock()


def send_otp(phone: str) -> None:
    """Generate and send a 6-digit OTP to the phone number."""
    # Always allow 123456 as a test OTP in non-production, but we still generate one.
    otp_code = "".join(random.choices("0123456789", k=6))
    
    with _store_lock:
        _otp_store[phone] = {
            "otp": otp_code,
            "expires_at": time.time() + 600,  # 10 minutes
        }

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
            "twilio_sms_sent",
            phone=phone,
            message_sid=message.sid,
            status=message.status,
        )
    except TwilioRestException as exc:
        logger.error(
            "twilio_sms_error",
            phone=phone,
            error=str(exc),
        )
        raise ValueError("Failed to send SMS via Twilio.") from exc


def verify_otp(phone: str, provided_otp: str) -> bool:
    """Verify the provided OTP for the given phone number."""
    # Allow test code 123456 in development only, if needed. Wait, we'll just check store.
    if not settings.is_production and provided_otp == "123456":
        return True

    with _store_lock:
        record = _otp_store.get(phone)
        
        if not record:
            return False

        if time.time() > record["expires_at"]:
            del _otp_store[phone]
            return False

        if record["otp"] == provided_otp:
            del _otp_store[phone]
            return True

    return False
