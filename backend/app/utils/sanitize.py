"""
AssignMind — Input Sanitization Utilities

All user inputs MUST be sanitized before processing (Constitution §III).
Three sanitization layers:
  1. XSS — strip dangerous HTML via bleach
  2. SQL injection — enforced by ORM-only access (no raw SQL)
  3. Prompt injection — wrap untrusted text in delimiters for Claude
"""

import re

import bleach


# ── Allowed HTML (none for most inputs; minimal for rich text if needed) ──

ALLOWED_TAGS: list[str] = []
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {}


def sanitize_html(text: str) -> str:
    """
    Strip ALL HTML tags from user input.

    Used for: workspace titles, task titles, chat messages,
    profile fields, and any other user-supplied text.
    """
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def sanitize_and_trim(text: str, max_length: int = 5000) -> str:
    """
    Sanitize HTML, collapse whitespace, and enforce length limit.

    Returns cleaned text truncated to max_length characters.
    """
    cleaned = sanitize_html(text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:max_length]


def wrap_for_ai(text: str, tag: str = "assignment_document") -> str:
    """
    Wrap untrusted user content in XML-like delimiters for AI prompts.

    Prevents prompt injection by instructing Claude to treat
    content within delimiters as untrusted data, not instructions.
    """
    sanitized = sanitize_html(text)
    return f"<{tag}>\n{sanitized}\n</{tag}>"


def is_empty_or_whitespace(text: str | None) -> bool:
    """Check if text is None, empty, or whitespace-only."""
    if text is None:
        return True
    return len(text.strip()) == 0


def validate_text_length(
    text: str, field_name: str, min_len: int = 1, max_len: int = 5000
) -> str:
    """
    Validate text length bounds after sanitization.

    Raises ValueError with a descriptive message if out of bounds.
    Returns the sanitized text if valid.
    """
    cleaned = sanitize_and_trim(text, max_length=max_len)
    if len(cleaned) < min_len:
        raise ValueError(
            f"{field_name} must be at least {min_len} character(s)"
        )
    return cleaned
