"""
AssignMind — JWT Authentication Utilities

Validates Supabase-issued JWTs server-side using SUPABASE_JWT_SECRET.
Every endpoint MUST validate authentication (Constitution §V).
"""

from datetime import datetime, timezone
from uuid import UUID

import jwt
from pydantic import BaseModel

from app.config import get_settings


class TokenPayload(BaseModel):
    """Decoded JWT token claims."""

    sub: str          # Supabase user ID (UUID string)
    exp: int          # Expiration timestamp (Unix epoch)
    aud: str = ""     # Audience
    role: str = ""    # Supabase role (e.g., "authenticated")


class AuthError(Exception):
    """Raised when JWT verification fails."""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def decode_jwt(token: str) -> TokenPayload:
    """
    Decode and validate a Supabase JWT.

    Verifies:
      - Signature using SUPABASE_JWT_SECRET (for HS256) or JWKS (for ES256/RS256)
      - Expiration (exp claim)
      - Presence of sub claim

    Returns TokenPayload on success.
    Raises AuthError on any failure.
    """
    settings = get_settings()

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        if alg == "HS256":
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"require": ["sub", "exp"]},
            )
        else:
            jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/jwks"
            jwks_client = jwt.PyJWKClient(
                jwks_url,
                headers={"apikey": settings.supabase_service_role_key}
            )
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                options={"require": ["sub", "exp"]},
            )

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except Exception as exc:
        raise AuthError(f"Invalid token: {exc}")

    return TokenPayload(**payload)


def extract_bearer_token(authorization: str | None) -> str:
    """
    Extract the JWT from an Authorization header value.

    Expects format: "Bearer <token>"
    Raises AuthError if header is missing or malformed.
    """
    if not authorization:
        raise AuthError("Missing Authorization header")

    parts = authorization.split(" ", maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Invalid Authorization header format")

    return parts[1]


def get_supabase_user_id(token: str) -> UUID:
    """
    Decode JWT and return the Supabase user UUID.

    Convenience wrapper combining decode + UUID parsing.
    Raises AuthError if token is invalid.
    """
    payload = decode_jwt(token)

    try:
        return UUID(payload.sub)
    except ValueError:
        raise AuthError("Invalid user ID in token")


def is_token_expired(payload: TokenPayload) -> bool:
    """Check if a token payload has expired."""
    now = datetime.now(timezone.utc)
    exp = datetime.fromtimestamp(payload.exp, tz=timezone.utc)
    return now >= exp
