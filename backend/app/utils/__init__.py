"""
AssignMind — Utility Functions

Pure utility modules for sanitization, auth, rate limiting, and datetime.
"""

from app.utils.sanitize import (
    sanitize_html,
    sanitize_and_trim,
    wrap_for_ai,
    is_empty_or_whitespace,
    validate_text_length,
)
from app.utils.auth import (
    AuthError,
    TokenPayload,
    decode_jwt,
    extract_bearer_token,
    get_supabase_user_id,
)
from app.utils.rate_limit import (
    RateLimitExceeded,
    RateLimiter,
    rate_limiter,
)
from app.utils.datetime_utils import (
    utcnow,
    to_user_timezone,
    format_datetime,
    hours_until,
    is_past,
    add_hours,
    is_valid_timezone,
)

__all__ = [
    # Sanitization
    "sanitize_html",
    "sanitize_and_trim",
    "wrap_for_ai",
    "is_empty_or_whitespace",
    "validate_text_length",
    # Auth
    "AuthError",
    "TokenPayload",
    "decode_jwt",
    "extract_bearer_token",
    "get_supabase_user_id",
    # Rate limiting
    "RateLimitExceeded",
    "RateLimiter",
    "rate_limiter",
    # Datetime
    "utcnow",
    "to_user_timezone",
    "format_datetime",
    "hours_until",
    "is_past",
    "add_hours",
    "is_valid_timezone",
]
