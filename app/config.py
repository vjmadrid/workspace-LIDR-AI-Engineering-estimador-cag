import logging
import pathlib
from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class LLMProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    # General Settings
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8000
    APP_NAME: str = "estimador-cag-default"
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT
    LOG_LEVEL: str = logging.INFO
    ESTIMATE_BACKEND_BASE_URL: str = "http://127.0.0.1:8000"
    ESTIMATE_BACKEND_TIMEOUT_SECONDS: float = 120.0

    # LLM Settings
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI
    LLM_MODEL_OPENAI: str = "gpt-4o-mini"

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

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
