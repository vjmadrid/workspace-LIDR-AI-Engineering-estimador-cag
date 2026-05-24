import pytest

from app.guardrails.input import InputGuardrailViolation
from app.responses.estimate_llmwrapper_advanced_responses import (
    LOW_CONFIDENCE_THRESHOLD,
    OUT_OF_SCOPE_PREFIX,
    EstimationResult,
)
from app.services.estimate_advance_services import EstimateAdvancedService
from tests.units.app.requests.estimate_request_factory import (
    EstimateLLMWrapperAdvancedRequestFactory,
)
from tests.units.app.responses.estimate_response_factory import EstimationResultFactory


class FakeExactCache:
    def __init__(self, hit: dict | None = None) -> None:
        self.hit = hit
        self.get_keys: list[str] = []
        self.set_calls: list[tuple[str, dict]] = []

    def get(self, key: str):
        self.get_keys.append(key)
        return self.hit

    def set(self, key: str, response: dict) -> None:
        self.set_calls.append((key, response))


class FakeSemanticCache:
    def __init__(self, hit: EstimationResult | None = None) -> None:
        self.hit = hit
        self.lookup_calls = []
        self.store_calls = []

    def lookup(self, request, prompt_version: str):
        self.lookup_calls.append((request, prompt_version))
        return self.hit

    def store(self, request, result: EstimationResult, prompt_version: str) -> None:
        self.store_calls.append((request, result, prompt_version))


class FakeAdvancedLLMWrapper:
    def __init__(
        self,
        *,
        result: EstimationResult | None = None,
        exception: Exception | None = None,
        primary_model: str = "gpt-4o-mini",
    ) -> None:
        self.result = result or EstimationResultFactory.build()
        self.exception = exception
        self.primary_model = primary_model
        self.calls: list[dict] = []

    def complete_structured(self, **kwargs):
        self.calls.append(kwargs)
        if self.exception:
            raise self.exception
        return self.result, {
            "model": self.primary_model,
            "provider": "openai",
            "latency_ms": 1,
        }


def build_service(
    *,
    wrapper: FakeAdvancedLLMWrapper | None = None,
    exact_cache: FakeExactCache | None = None,
    semantic_cache: FakeSemanticCache | None = None,
    prompt_version: str = "v1",
) -> EstimateAdvancedService:
    return EstimateAdvancedService(
        llm_wrapper=wrapper or FakeAdvancedLLMWrapper(),
        exact_cache=exact_cache or FakeExactCache(),
        semantic_cache=semantic_cache,
        prompt_version=prompt_version,
    )


def test_estimate_returns_exact_cache_hit_without_calling_llm_or_semantic_cache():
    cached_result = EstimationResultFactory.build()
    exact_cache = FakeExactCache(hit={"result": cached_result.model_dump(mode="json")})
    semantic_cache = FakeSemanticCache()
    wrapper = FakeAdvancedLLMWrapper()
    service = build_service(
        wrapper=wrapper,
        exact_cache=exact_cache,
        semantic_cache=semantic_cache,
        prompt_version="v2",
    )

    response = service.estimate(EstimateLLMWrapperAdvancedRequestFactory.build())

    assert response.result == cached_result
    assert response.prompt_version == "v2"
    assert response.cached is True
    assert len(exact_cache.get_keys) == 1
    assert exact_cache.set_calls == []
    assert semantic_cache.lookup_calls == []
    assert wrapper.calls == []


def test_estimate_returns_semantic_cache_hit_without_calling_llm():
    semantic_result = EstimationResultFactory.build(summary="Semantic cache result is valid and ready.")
    exact_cache = FakeExactCache()
    semantic_cache = FakeSemanticCache(hit=semantic_result)
    wrapper = FakeAdvancedLLMWrapper()
    service = build_service(
        wrapper=wrapper,
        exact_cache=exact_cache,
        semantic_cache=semantic_cache,
    )
    request = EstimateLLMWrapperAdvancedRequestFactory.build()

    response = service.estimate(request)

    assert response.result == semantic_result
    assert response.cached is True
    assert len(exact_cache.get_keys) == 1
    assert exact_cache.set_calls == []
    assert semantic_cache.lookup_calls == [(request, "v1")]
    assert semantic_cache.store_calls == []
    assert wrapper.calls == []


def test_estimate_generates_result_and_stores_exact_and_semantic_cache_on_miss():
    generated_result = EstimationResultFactory.build(summary="Generated result from the structured wrapper.")
    exact_cache = FakeExactCache()
    semantic_cache = FakeSemanticCache()
    wrapper = FakeAdvancedLLMWrapper(result=generated_result)
    service = build_service(
        wrapper=wrapper,
        exact_cache=exact_cache,
        semantic_cache=semantic_cache,
    )
    request = EstimateLLMWrapperAdvancedRequestFactory.build()

    response = service.estimate(request)

    assert response.result == generated_result
    assert response.cached is False
    assert response.prompt_version == "v1"
    assert len(wrapper.calls) == 1
    call = wrapper.calls[0]
    assert call["response_model"] is EstimationResult
    assert request.description in call["user_message"]
    assert request.description not in call["system_prompt"]
    assert len(exact_cache.set_calls) == 1
    stored_key, stored_payload = exact_cache.set_calls[0]
    assert stored_key == exact_cache.get_keys[0]
    assert stored_payload == {
        "result": generated_result.model_dump(mode="json"),
        "prompt_version": "v1",
    }
    assert semantic_cache.store_calls == [(request, generated_result, "v1")]


def test_estimate_runs_input_guardrails_before_cache_lookup_or_llm_call():
    request = EstimateLLMWrapperAdvancedRequestFactory.build(
        description=(
            "We need to estimate a SaaS platform with users, roles, dashboards, "
            "and contact email ana@example.com."
        )
    )
    exact_cache = FakeExactCache()
    wrapper = FakeAdvancedLLMWrapper()
    service = build_service(wrapper=wrapper, exact_cache=exact_cache)

    with pytest.raises(InputGuardrailViolation) as exc_info:
        service.estimate(request)

    assert exc_info.value.reason == "pii"
    assert exact_cache.get_keys == []
    assert exact_cache.set_calls == []
    assert wrapper.calls == []


def test_estimate_propagates_structured_llm_errors():
    exact_cache = FakeExactCache()
    wrapper = FakeAdvancedLLMWrapper(exception=RuntimeError("provider down"))
    service = build_service(wrapper=wrapper, exact_cache=exact_cache)

    with pytest.raises(RuntimeError, match="provider down"):
        service.estimate(EstimateLLMWrapperAdvancedRequestFactory.build())

    assert len(wrapper.calls) == 1
    assert exact_cache.set_calls == []


def test_estimate_applies_output_guardrail_before_caching_result():
    low_confidence_result = EstimationResult.model_construct(
        summary="The requirements are too vague to estimate confidently.",
        confidence_pct=LOW_CONFIDENCE_THRESHOLD - 1,
        phases=[],
        total_duration_weeks=1,
        total_cost_eur=1,
    )
    exact_cache = FakeExactCache()
    wrapper = FakeAdvancedLLMWrapper(result=low_confidence_result)
    service = build_service(wrapper=wrapper, exact_cache=exact_cache)

    response = service.estimate(EstimateLLMWrapperAdvancedRequestFactory.build())

    assert response.result.summary.startswith(OUT_OF_SCOPE_PREFIX)
    assert response.result.total_cost_eur == 0
    assert response.result.phases[0].name == "Not estimated"
    assert exact_cache.set_calls[0][1]["result"] == response.result.model_dump(mode="json")
