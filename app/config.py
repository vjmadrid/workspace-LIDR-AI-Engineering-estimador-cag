import logging
import pathlib
from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LLMLITE = "llmlite"


LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    # General Settings
    SERVICE_HOST: str
    SERVICE_PORT: int
    APP_NAME: str
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT
    LOG_LEVEL: str = logging.INFO

    # LLM Settings
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI

    # OpenAI Settings
    OPENAI_MODEL: str
    OPENAI_API_KEY: str = ""

    # Anthropic Settings
    ANTHROPIC_MODEL: str
    ANTHROPIC_API_KEY: str = ""

    # LiteLLM Settings
    LLMLITE_MODEL: str = "gpt-4o-mini"

    # LiteLLM Advanced Settings
    PRIMARY_MODEL: str = "gpt-4o-mini"
    FALLBACK_MODEL: str = "claude-haiku-4-5-20251001"

    LLM_TIMEOUT: int = 30
    LLM_RETRIES: int = 2

    # Caching Settings (Redis or similar)
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 86400

    # Streamlit Settings
    ESTIMATE_BACKEND_BASE_URL: str
    ESTIMATE_BACKEND_TIMEOUT_SECONDS: float

    @model_validator(mode="after")
    def validate_api_key_for_provider(self) -> "Settings":
        """Ensure the API key for the selected LLM provider is present."""
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        if self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'anthropic'")
        return self

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == AppEnvironment.PRODUCTION


class DevelopmentConfig(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = logging.DEBUG


class TestingConfig(Settings):
    DEBUG: bool = False


class ProductionConfig(Settings):
    DEBUG: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
