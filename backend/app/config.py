"""
AssignMind Backend — Application Configuration

Loads all environment variables via Pydantic Settings.
All secrets are server-side only (Constitution §II).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──
    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # ── Database ──
    database_url: str
    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    # ── AI (Constitution §IV — service layer only) ──
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 4096
    anthropic_timeout_seconds: int = 60

    # ── Email ──
    resend_api_key: str
    email_from: str = "noreply@assignmind.com"
    email_from_name: str = "AssignMind"

    # ── Payments ──
    lemon_squeezy_api_key: str
    lemon_squeezy_webhook_secret: str
    lemon_squeezy_store_id: str
    lemon_squeezy_starter_variant_id: str = ""
    lemon_squeezy_standard_variant_id: str = ""
    lemon_squeezy_pro_variant_id: str = ""

    # ── Rate Limiting ──
    rate_limit_redis_url: str = ""

    # ── Logging ──
    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins — no wildcard in production."""
        origins = [self.frontend_url]
        if not self.is_production:
            origins.append("http://localhost:3000")
        return origins


def get_settings() -> Settings:
    """Create and return application settings instance."""
    return Settings()  # type: ignore[call-arg]
