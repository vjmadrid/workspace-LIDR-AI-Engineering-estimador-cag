"""FastAPI dependency factories for shared singletons (cache and LLM wrapper)."""

from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.cache.cache_services import EstimationCache
from app.services.estimate_advance_services import EstimateAdvancedService
from app.services.llmwrapper.llm_wrapper_services import LLMWrapper
from app.services.llmwrapperadvanced.llm_wrapper_advanced_services import (
    LLMWrapper as AdvancedLLMWrapper,
)


@lru_cache
def get_cache() -> EstimationCache:
    settings = get_settings()
    return EstimationCache.from_url(settings.REDIS_URL, ttl=settings.CACHE_TTL)


@lru_cache
def get_llm_wrapper() -> LLMWrapper:
    settings = get_settings()
    return LLMWrapper(
        openai_api_key=settings.OPENAI_API_KEY,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        primary_model=settings.PRIMARY_MODEL,
        fallback_model=settings.FALLBACK_MODEL,
        timeout=settings.LLM_TIMEOUT,
        num_retries=settings.LLM_RETRIES,
        cache=get_cache(),
    )


@lru_cache
def get_advanced_llm_wrapper() -> AdvancedLLMWrapper:
    settings = get_settings()
    return AdvancedLLMWrapper(
        openai_api_key=settings.OPENAI_API_KEY,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        primary_model=settings.PRIMARY_MODEL,
        fallback_model=settings.FALLBACK_MODEL,
        timeout=settings.LLM_TIMEOUT,
        num_retries=settings.LLM_RETRIES,
        cache=get_cache(),
    )


@lru_cache
def get_estimation_service() -> EstimateAdvancedService:
    return EstimateAdvancedService(
        llm_wrapper=get_advanced_llm_wrapper(),
        exact_cache=get_cache(),
    )
