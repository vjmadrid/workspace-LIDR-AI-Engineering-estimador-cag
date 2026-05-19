from types import SimpleNamespace
from unittest.mock import patch

import fakeredis
import pytest

from app.services.cache import EstimationCache
from app.services.llmwrapper.llm_wrapper_services import LLMWrapper, _estimate_cost

SYSTEM_PROMPT = "sys"
USER_MESSAGE = "usr"
PRIMARY_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"


def _fake_completion(
    model: str,
    content: str = "the answer",
    input_tokens: int = 100,
    output_tokens: int = 50,
):
    """Build a SimpleNamespace shaped like a litellm.ModelResponse."""
    return SimpleNamespace(
        model=model,
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
                finish_reason="stop",
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        ),
    )


@pytest.fixture
def wrapper() -> LLMWrapper:
    cache = EstimationCache(fakeredis.FakeRedis(decode_responses=True), ttl=60)
    return LLMWrapper(
        openai_api_key="fake-openai",
        anthropic_api_key="fake-anthropic",
        primary_model=PRIMARY_MODEL,
        fallback_model=ANTHROPIC_MODEL,
        timeout=30,
        num_retries=2,
        cache=cache,
    )


def complete(wrapper: LLMWrapper, **overrides):
    call_args = {
        "system_prompt": SYSTEM_PROMPT,
        "user_message": USER_MESSAGE,
        "model_override": None,
        "max_tokens": 4000,
        "thinking_budget": None,
    }
    call_args.update(overrides)
    return wrapper.complete(**call_args)


def stream(wrapper: LLMWrapper, **overrides):
    call_args = {
        "system_prompt": SYSTEM_PROMPT,
        "user_message": USER_MESSAGE,
        "model_override": None,
        "max_tokens": 4000,
    }
    call_args.update(overrides)
    return list(wrapper.complete_stream(**call_args))


def streaming_chunk(content: str | None):
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=content))])


def test_estimate_cost_uses_pricing_table() -> None:
    cost = _estimate_cost(PRIMARY_MODEL, 1_000_000, 1_000_000)
    # 1M input * 0.15 + 1M output * 0.60 = 0.75 USD
    assert cost == pytest.approx(0.75)


def test_complete_returns_normalised_dict_and_caches(wrapper: LLMWrapper) -> None:
    fake = _fake_completion(model=PRIMARY_MODEL, content="hello world")

    with patch.object(wrapper.router, "completion", return_value=fake) as mocked:
        result = complete(wrapper)

    assert mocked.call_count == 1
    assert result["estimation"] == "hello world"
    assert result["model"] == PRIMARY_MODEL
    assert result["provider"] == "openai"
    assert result["finish_reason"] == "stop"
    assert result["usage"]["input_tokens"] == 100
    assert result["usage"]["output_tokens"] == 50
    assert result["cache_hit"] is False
    assert result["cost_usd"] > 0

    # Second call with the same inputs should hit the cache without invoking the router.
    with patch.object(wrapper.router, "completion") as mocked_again:
        cached = complete(wrapper)

    assert mocked_again.call_count == 0
    assert cached["cache_hit"] is True
    assert cached["estimation"] == "hello world"


def test_complete_with_model_override_bypasses_router(wrapper: LLMWrapper) -> None:
    fake = _fake_completion(model="gpt-4o", content="overridden")

    with (
        patch("app.services.llm_wrapper.litellm.completion", return_value=fake) as direct,
        patch.object(wrapper.router, "completion") as router_call,
    ):
        result = complete(wrapper, model_override="gpt-4o")

    assert direct.call_count == 1
    assert router_call.call_count == 0
    assert direct.call_args.kwargs["model"] == "gpt-4o"
    assert result["model"] == "gpt-4o"


def test_thinking_budget_passed_for_anthropic_fallback(wrapper: LLMWrapper) -> None:
    fake = _fake_completion(model=ANTHROPIC_MODEL, content="ok")

    with patch.object(wrapper.router, "completion", return_value=fake) as mocked:
        complete(wrapper, thinking_budget=2048)

    # primary is OpenAI (gpt-4o-mini), so thinking budget is *ignored* in kwargs.
    assert "thinking" not in mocked.call_args.kwargs


def test_thinking_budget_pads_max_tokens_when_anthropic_override(wrapper: LLMWrapper) -> None:
    fake = _fake_completion(model=ANTHROPIC_MODEL, content="ok")

    with patch("app.services.llm_wrapper.litellm.completion", return_value=fake) as direct:
        complete(wrapper, model_override=ANTHROPIC_MODEL, max_tokens=1000, thinking_budget=4096)

    kwargs = direct.call_args.kwargs
    assert kwargs["thinking"] == {"type": "enabled", "budget_tokens": 4096}
    assert kwargs["max_tokens"] == 4096 + 1024


def test_complete_stream_yields_chunks_and_caches(wrapper: LLMWrapper) -> None:
    chunks = [streaming_chunk("Hello "), streaming_chunk("world"), streaming_chunk(None)]

    with patch("app.services.llm_wrapper.litellm.completion", return_value=iter(chunks)):
        emitted = stream(wrapper)

    assert "".join(emitted) == "Hello world"

    # Now the same request hits the cache and replays the full text as one chunk.
    with patch("app.services.llm_wrapper.litellm.completion") as direct_call:
        replayed = stream(wrapper)

    assert direct_call.call_count == 0
    assert "".join(replayed) == "Hello world"
