import logging

import pytest
from pydantic import ValidationError

from app.config import (
    AppEnvironment,
    DevelopmentConfig,
    LLMProvider,
    LOG_LEVEL_MAP,
    ProductionConfig,
    Settings,
    TestingConfig as AppTestingConfig,
    get_settings,
)


@pytest.fixture(autouse=True)
def clear_settings_cache_and_external_debug_env(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def build_settings_payload(**overrides) -> dict:
    payload = {
        "SERVICE_HOST": "127.0.0.1",
        "SERVICE_PORT": "8000",
        "APP_NAME": "Estimador CAG",
        "APP_ENV": "development",
        "LOG_LEVEL": "info",
        "LLM_PROVIDER": "openai",
        "OPENAI_MODEL": "gpt-4o-mini",
        "ANTHROPIC_MODEL": "claude-haiku",
        "LLMLITE_MODEL": "gpt-4o-mini",
        "PRIMARY_MODEL": "gpt-4o-mini",
        "FALLBACK_MODEL": "claude-haiku-4-5-20251001",
        "LLM_TIMEOUT": "30",
        "LLM_RETRIES": "2",
        "REDIS_URL": "redis://localhost:6379",
        "CACHE_TTL": "86400",
        "OPENAI_API_KEY": "test-openai-api-key",
        "ANTHROPIC_API_KEY": "",
        "ESTIMATE_BACKEND_BASE_URL": "http://localhost:8000",
        "ESTIMATE_BACKEND_TIMEOUT_SECONDS": "10.5",
    }
    payload.update(overrides)
    return payload


def build_settings(**overrides) -> Settings:
    return Settings(_env_file=None, **build_settings_payload(**overrides))


def test_settings_loads_valid_minimum_configuration_with_expected_types():
    settings = build_settings()

    assert settings.SERVICE_HOST == "127.0.0.1"
    assert settings.SERVICE_PORT == 8000
    assert settings.APP_NAME == "Estimador CAG"
    assert settings.APP_ENV == AppEnvironment.DEVELOPMENT
    assert settings.LLM_PROVIDER == LLMProvider.OPENAI
    assert settings.LLMLITE_MODEL == "gpt-4o-mini"
    assert settings.PRIMARY_MODEL == "gpt-4o-mini"
    assert settings.FALLBACK_MODEL == "claude-haiku-4-5-20251001"
    assert settings.LLM_TIMEOUT == 30
    assert settings.LLM_RETRIES == 2
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.CACHE_TTL == 86400
    assert settings.ESTIMATE_BACKEND_TIMEOUT_SECONDS == 10.5


def test_settings_requires_openai_api_key_when_provider_is_openai():
    with pytest.raises(ValidationError, match="OPENAI_API_KEY is required"):
        build_settings(LLM_PROVIDER="openai", OPENAI_API_KEY="")


def test_settings_requires_anthropic_api_key_when_provider_is_anthropic():
    with pytest.raises(ValidationError, match="ANTHROPIC_API_KEY is required"):
        build_settings(
            LLM_PROVIDER="anthropic",
            OPENAI_API_KEY="",
            ANTHROPIC_API_KEY="",
        )


def test_settings_accepts_api_key_for_selected_provider():
    openai_settings = build_settings(LLM_PROVIDER="openai", OPENAI_API_KEY="openai-key")
    anthropic_settings = build_settings(
        LLM_PROVIDER="anthropic",
        OPENAI_API_KEY="",
        ANTHROPIC_API_KEY="anthropic-key",
    )

    assert openai_settings.OPENAI_API_KEY == "openai-key"
    assert anthropic_settings.ANTHROPIC_API_KEY == "anthropic-key"


def test_settings_accepts_llmlite_provider_without_provider_specific_api_key():
    settings = build_settings(
        LLM_PROVIDER="llmlite",
        OPENAI_API_KEY="",
        ANTHROPIC_API_KEY="",
        LLMLITE_MODEL="anthropic/claude-haiku-4-5-20251001",
    )

    assert settings.LLM_PROVIDER == LLMProvider.LLMLITE
    assert settings.LLMLITE_MODEL == "anthropic/claude-haiku-4-5-20251001"


@pytest.mark.parametrize(
    ("app_env", "expected"),
    [
        ("production", True),
        ("development", False),
        ("test", False),
        ("staging", False),
    ],
)
def test_settings_is_production_depends_on_app_environment(app_env, expected):
    settings = build_settings(APP_ENV=app_env)

    assert settings.is_production is expected


def test_app_environment_enum_values_are_stable():
    assert AppEnvironment.DEVELOPMENT.value == "development"
    assert AppEnvironment.TEST.value == "test"
    assert AppEnvironment.STAGING.value == "staging"
    assert AppEnvironment.PRODUCTION.value == "production"


def test_llm_provider_enum_values_are_stable():
    assert LLMProvider.OPENAI.value == "openai"
    assert LLMProvider.ANTHROPIC.value == "anthropic"
    assert LLMProvider.LLMLITE.value == "llmlite"


def test_log_level_map_values_are_stable():
    assert LOG_LEVEL_MAP["debug"] == logging.DEBUG
    assert LOG_LEVEL_MAP["info"] == logging.INFO
    assert LOG_LEVEL_MAP["warn"] == logging.WARNING
    assert LOG_LEVEL_MAP["error"] == logging.ERROR


@pytest.mark.parametrize(
    "overrides",
    [
        {"APP_ENV": "local"},
        {"LLM_PROVIDER": "ollama"},
    ],
)
def test_settings_rejects_invalid_enum_values(overrides):
    with pytest.raises(ValidationError):
        build_settings(**overrides)


def test_get_settings_returns_cached_instance(monkeypatch):
    get_settings.cache_clear()
    for key, value in build_settings_payload().items():
        monkeypatch.setenv(key, value)

    first_settings = get_settings()
    second_settings = get_settings()

    assert first_settings is second_settings

    get_settings.cache_clear()


def test_development_config_defaults():
    settings = DevelopmentConfig(
        _env_file=None,
        **build_settings_payload(LOG_LEVEL="debug"),
    )

    assert settings.DEBUG is True
    assert settings.LOG_LEVEL == "debug"


def test_testing_config_defaults():
    settings = AppTestingConfig(_env_file=None, **build_settings_payload(APP_ENV="test"))

    assert settings.DEBUG is False
    assert settings.is_production is False


def test_production_config_defaults():
    settings = ProductionConfig(
        _env_file=None,
        **build_settings_payload(APP_ENV="production"),
    )

    assert settings.DEBUG is False
    assert settings.is_production is True


def test_settings_base_dir_points_to_project_root():
    settings = build_settings()

    assert settings.BASE_DIR.name == "workspace-LIDR-AI-Engineering-estimador-cag"
    assert (settings.BASE_DIR / "app" / "config.py").exists()
