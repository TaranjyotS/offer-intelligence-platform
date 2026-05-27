from functools import lru_cache
from typing import List

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Offer Intelligence Platform"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: List[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    prediction_concurrency: int = 5

    # Demo JWT auth for portfolio usage. In production, replace the login provider
    # with OAuth/OIDC and validate provider-issued JWTs at this boundary.
    auth_mode: str = "demo_jwt"
    demo_username: str = "admin"
    demo_password: SecretStr = SecretStr("demo123")
    jwt_secret: SecretStr = SecretStr("change-this-local-development-secret")
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
