"""
AssignMind — Date/Time Utilities

All internal timestamps are UTC. Timezone conversion happens
only at the presentation layer (emails, API responses).
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def to_user_timezone(
    dt: datetime, user_timezone: str = "UTC"
) -> datetime:
    """
    Convert a UTC datetime to the user's local timezone.

    Args:
        dt: UTC datetime (must be timezone-aware).
        user_timezone: IANA timezone string (e.g., 'Asia/Riyadh').

    Returns:
        Datetime converted to the user's timezone.
        Falls back to UTC if timezone is invalid.
    """
    try:
        tz = ZoneInfo(user_timezone)
    except (ZoneInfoNotFoundError, KeyError):
        tz = ZoneInfo("UTC")

    return dt.astimezone(tz)


def format_datetime(
    dt: datetime, user_timezone: str = "UTC"
) -> str:
    """
    Format a UTC datetime for display in the user's timezone.

    Returns a human-readable string like "Mar 7, 2026, 2:30 PM".
    """
    local_dt = to_user_timezone(dt, user_timezone)
    return local_dt.strftime("%b %-d, %Y, %-I:%M %p")


def format_datetime_windows(
    dt: datetime, user_timezone: str = "UTC"
) -> str:
    """
    Format a UTC datetime (Windows-compatible, no %-d).

    Returns a string like "Mar 07, 2026, 02:30 PM".
    """
    local_dt = to_user_timezone(dt, user_timezone)
    return local_dt.strftime("%b %d, %Y, %I:%M %p")


def hours_until(target: datetime) -> float:
    """Return hours remaining until the target datetime."""
    now = utcnow()
    delta = target - now
    return delta.total_seconds() / 3600


def is_past(dt: datetime) -> bool:
    """Check if a datetime is in the past."""
    return dt < utcnow()


def add_hours(dt: datetime, hours: float) -> datetime:
    """Add a number of hours to a datetime."""
    return dt + timedelta(hours=hours)


def is_valid_timezone(tz_string: str) -> bool:
    """Check if a timezone string is a valid IANA timezone."""
    try:
        ZoneInfo(tz_string)
        return True
    except (ZoneInfoNotFoundError, KeyError):
        return False
