import logging
import pathlib
from enum import StrEnum
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        extra="ignore",
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

    # Semantic cache Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    SEMANTIC_CACHE_THRESHOLD: float = 0.85
    SEMANTIC_CACHE_TTL: int = 86400

    # When True, the semantic cache LOGS potential hits but does NOT serve them.
    # Used to gather metrics before flipping the cache on in production.
    SEMANTIC_CACHE_LOG_ONLY: bool = False

    # Streamlit Settings
    ESTIMATE_BACKEND_BASE_URL: str
    ESTIMATE_BACKEND_TIMEOUT_SECONDS: float

    @model_validator(mode="after")
    def validate_api_key_for_provider(self) -> "Settings":
        """Ensure the selected direct provider has its API key configured."""
        if self.LLM_PROVIDER == LLMProvider.OPENAI and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        if self.LLM_PROVIDER == LLMProvider.ANTHROPIC and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'anthropic'")
        return self

    @model_validator(mode="after")
    def validate_at_least_one_api_key(self) -> "Settings":
        """LiteLLM may try either provider via fallback, so we require at least one key."""
        if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
            raise ValueError(
                "At least one of OPENAI_API_KEY or ANTHROPIC_API_KEY must be set"
            )
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
