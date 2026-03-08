"""
AssignMind — Rate Limiting Utilities

In-memory rate limiter for MVP. Uses a sliding window counter
per (key, action) pair. Redis-ready interface for production.

Usage:
    limiter = RateLimiter()
    limiter.check("user-123", "assignment_upload", max_calls=5, window_seconds=3600)
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RateLimitEntry:
    """Tracks timestamps of calls within the sliding window."""

    timestamps: list[float] = field(default_factory=list)


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(
        self, action: str, max_calls: int, window_seconds: int
    ):
        self.action = action
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.message = (
            f"Rate limit exceeded for '{action}': "
            f"max {max_calls} calls per {window_seconds}s"
        )
        super().__init__(self.message)


class RateLimiter:
    """
    In-memory sliding window rate limiter.

    Thread-safe via Lock. Suitable for single-process MVP.
    For multi-process production, swap to Redis backend.
    """

    def __init__(self) -> None:
        self._entries: dict[str, RateLimitEntry] = defaultdict(
            RateLimitEntry
        )
        self._lock = Lock()

    def _build_key(self, identifier: str, action: str) -> str:
        """Build a composite key from identifier and action."""
        return f"{action}:{identifier}"

    def check(
        self,
        identifier: str,
        action: str,
        max_calls: int,
        window_seconds: int,
    ) -> None:
        """
        Check rate limit and record this call.

        Args:
            identifier: User ID, IP, or phone number.
            action: Name of the action being limited.
            max_calls: Maximum allowed calls in window.
            window_seconds: Sliding window duration in seconds.

        Raises:
            RateLimitExceeded: If limit is exceeded.
        """
        key = self._build_key(identifier, action)
        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            entry = self._entries[key]
            # Prune expired timestamps
            entry.timestamps = [
                t for t in entry.timestamps if t > cutoff
            ]

            if len(entry.timestamps) >= max_calls:
                raise RateLimitExceeded(
                    action, max_calls, window_seconds
                )

            entry.timestamps.append(now)

    def reset(self, identifier: str, action: str) -> None:
        """Clear rate limit history for a specific key."""
        key = self._build_key(identifier, action)
        with self._lock:
            self._entries.pop(key, None)

    def remaining(
        self,
        identifier: str,
        action: str,
        max_calls: int,
        window_seconds: int,
    ) -> int:
        """Return the number of remaining calls in the window."""
        key = self._build_key(identifier, action)
        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return max_calls
            active = [t for t in entry.timestamps if t > cutoff]
            return max(0, max_calls - len(active))


# ── Singleton for app-wide use ──

rate_limiter = RateLimiter()
