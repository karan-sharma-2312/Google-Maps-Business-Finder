"""Application configuration management.

This module centralizes all environment-driven settings for the platform.
It uses pydantic-settings for validation, defaults, and `.env` integration.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    """Core application runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    name: str = Field(default="Business Intelligence AI Agent", validation_alias="APP_NAME")
    environment: AppEnvironment = Field(default=AppEnvironment.DEVELOPMENT, validation_alias="APP_ENV")
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    host: str = Field(default="127.0.0.1", validation_alias="APP_HOST")
    port: int = Field(default=8000, validation_alias="APP_PORT")


class SecuritySettings(BaseSettings):
    """Authentication and API security settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"), validation_alias="SECRET_KEY")
    api_key: SecretStr | None = Field(default=None, validation_alias="API_KEY")
    access_token_expire_minutes: int = Field(default=60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    rate_limit_per_minute: int = Field(default=120, validation_alias="RATE_LIMIT_PER_MINUTE")
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], validation_alias="ALLOWED_ORIGINS")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> list[str]:
        """Convert CSV origins from env to a clean list."""
        if isinstance(value, list):
            return [item.strip() for item in value if item and str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["http://localhost:3000"]


class LoggingSettings(BaseSettings):
    """Structured logging configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="json", validation_alias="LOG_FORMAT")
    file: Path = Field(default=Path("logs/app.log"), validation_alias="LOG_FILE")


class DatabaseSettings(BaseSettings):
    """Database connection settings for local and production adapters."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/business_intelligence.db",
        validation_alias="DATABASE_URL",
    )
    postgres_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/business_intelligence",
        validation_alias="POSTGRES_URL",
    )
    sql_echo: bool = Field(default=False, validation_alias="SQL_ECHO")


class QueueSettings(BaseSettings):
    """Message queue and cache settings for async task execution."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672//", validation_alias="RABBITMQ_URL")
    celery_broker_url: str = Field(default="amqp://guest:guest@localhost:5672//", validation_alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", validation_alias="CELERY_RESULT_BACKEND")


class ScraperSettings(BaseSettings):
    """Network and Playwright controls for scraping workloads."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    http_timeout_seconds: int = Field(default=30, validation_alias="HTTP_TIMEOUT_SECONDS")
    http_max_retries: int = Field(default=3, validation_alias="HTTP_MAX_RETRIES")
    http_retry_backoff_seconds: int = Field(default=1, validation_alias="HTTP_RETRY_BACKOFF_SECONDS")
    playwright_headless: bool = Field(default=True, validation_alias="PLAYWRIGHT_HEADLESS")
    playwright_navigation_timeout_ms: int = Field(default=45000, validation_alias="PLAYWRIGHT_NAVIGATION_TIMEOUT_MS")
    playwright_max_concurrency: int = Field(default=5, validation_alias="PLAYWRIGHT_MAX_CONCURRENCY")
    google_maps_base_url: str = Field(default="https://www.google.com/maps", validation_alias="GOOGLE_MAPS_BASE_URL")
    google_maps_default_max_results: int = Field(default=20, validation_alias="GOOGLE_MAPS_DEFAULT_MAX_RESULTS")


class AISettings(BaseSettings):
    """AI provider credentials and model defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", validation_alias="OPENAI_MODEL")
    gemini_api_key: SecretStr | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")

    @field_validator("openai_api_key", "gemini_api_key", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        """Normalize blank API key values to None for safer runtime checks."""
        if isinstance(value, str) and not value.strip():
            return None
        return value


class FeatureSettings(BaseSettings):
    """Feature flags to gradually enable platform capabilities."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    enable_ai_analysis: bool = Field(default=True, validation_alias="ENABLE_AI_ANALYSIS")
    enable_seo_analysis: bool = Field(default=True, validation_alias="ENABLE_SEO_ANALYSIS")
    enable_notifications: bool = Field(default=False, validation_alias="ENABLE_NOTIFICATIONS")
    enable_scheduler: bool = Field(default=False, validation_alias="ENABLE_SCHEDULER")


class PathSettings(BaseSettings):
    """Filesystem paths used by runtime components."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    export_dir: Path = Field(default=Path("exports"), validation_alias="EXPORT_DIR")
    data_dir: Path = Field(default=Path("data"), validation_alias="DATA_DIR")
    log_dir: Path = Field(default=Path("logs"), validation_alias="LOG_DIR")


class Settings(BaseModel):
    """Application settings aggregate used for dependency injection."""

    app: AppSettings
    security: SecuritySettings
    logging: LoggingSettings
    database: DatabaseSettings
    queue: QueueSettings
    scraper: ScraperSettings
    ai: AISettings
    features: FeatureSettings
    paths: PathSettings

    @classmethod
    def load(cls) -> Settings:
        """Load all settings sections from environment and `.env` file."""
        return cls(
            app=AppSettings(),
            security=SecuritySettings(),
            logging=LoggingSettings(),
            database=DatabaseSettings(),
            queue=QueueSettings(),
            scraper=ScraperSettings(),
            ai=AISettings(),
            features=FeatureSettings(),
            paths=PathSettings(),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance for the process lifecycle.

    Caching ensures config is parsed once and shared across FastAPI dependencies,
    CLI commands, and background workers.
    """

    return Settings.load()
