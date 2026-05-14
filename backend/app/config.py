from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FOUNDRY_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    database_url: PostgresDsn
    jwt_secret: SecretStr
    jwt_access_token_ttl_seconds: int = 900
    jwt_refresh_token_ttl_seconds: int = 1_209_600

    cors_origins: list[AnyHttpUrl] = ["http://localhost:5173"]  # type: ignore[list-item]
    cookie_secure: bool = True
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: SecretStr, info: object) -> SecretStr:
        secret = v.get_secret_value()
        if len(secret) < 32:
            raise ValueError("jwt_secret must be at least 32 characters")
        return v

    def assert_production_safety(self) -> None:
        """Raise at startup if running non-dev with a placeholder secret."""
        if self.env != "development":
            secret = self.jwt_secret.get_secret_value()
            placeholder_fragments = ("change-me", "secret", "example", "placeholder")
            if any(f in secret.lower() for f in placeholder_fragments):
                raise RuntimeError(
                    f"FOUNDRY_JWT_SECRET looks like a placeholder in env={self.env!r}. "
                    "Set a real secret before deploying."
                )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
