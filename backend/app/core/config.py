from functools import lru_cache
import secrets
import warnings
from typing import List

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Offer Intelligence Platform"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: List[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    prediction_concurrency: int = 5

    # Auth boundary:
    # - Local/dev can auto-generate a temporary JWT secret.
    # - Production requires a stable JWT_SECRET so tokens survive restarts.
    # - OAuth/OIDC can replace demo login while keeping the same API boundary.
    auth_mode: str = "demo_jwt"
    demo_username: str = "admin"
    demo_password: SecretStr = SecretStr("demo123")
    jwt_secret: SecretStr | None = None
    jwt_issuer: str = "offer-intelligence-platform"
    jwt_audience: str = "offer-intelligence-dashboard"
    jwt_access_token_minutes: int = 60
    oauth_issuer_url: str | None = None
    oauth_audience: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def configure_jwt_secret(self):
        current_secret = self.jwt_secret.get_secret_value().strip() if self.jwt_secret else ""
        unsafe_defaults = {
            "",
            "change-this-local-development-secret",
            "replace-with-a-long-random-secret-in-production",
        }

        if current_secret not in unsafe_defaults:
            return self

        if self.environment.lower() in {"production", "prod"}:
            raise ValueError(
                "JWT_SECRET is required in production. "
                "Use Render Blueprint generateValue, Render dashboard secrets, "
                "or scripts/generate_jwt_secret.py to create one."
            )

        self.jwt_secret = SecretStr(secrets.token_urlsafe(64))
        warnings.warn(
            "JWT_SECRET was not provided. Generated a temporary development-only secret. "
            "Set JWT_SECRET for deployed environments so tokens remain valid across restarts.",
            RuntimeWarning,
            stacklevel=2,
        )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
