from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise Order Management Platform"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./eomp.db"
    secret_key: SecretStr = SecretStr("local-development-only-change-me")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    worker_poll_seconds: int = Field(default=5, ge=1, le=300)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def secure_production_secret(self) -> "Settings":
        if self.app_env.lower() == "production":
            value = self.secret_key.get_secret_value()
            if value == "local-development-only-change-me" or len(value) < 32:
                raise ValueError("Production requires a SECRET_KEY of at least 32 characters")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
