from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config import LLMProvider
from app.constants.estimate_constants import ANTHROPIC_MAX_TOKENS_DEFAULT, ANTHROPIC_MODEL_DEFAULT
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.anthropic.estimate_anthropic_services import EstimateAnthropicService


class FakeAnthropicStream:
    def __init__(self, chunks: list[str], final_message) -> None:
        self.text_stream = iter(chunks)
        self._final_message = final_message

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def get_final_message(self):
        return self._final_message


def build_final_message(input_tokens: int = 100, output_tokens: int = 50):
    return SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    )


def build_service(client=None, prompt_builder=None) -> EstimateAnthropicService:
    return EstimateAnthropicService(
        client=client or Mock(),
        prompt_builder=prompt_builder or Mock(),
        settings=SimpleNamespace(ANTHROPIC_API_KEY="test-anthropic-api-key"),
    )


def test_stream_estimate_from_transcript_yields_delta_and_metadata_events() -> None:
    messages = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "Resumen de reunión: crear dashboard"},
    ]
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = messages
    client = Mock()
    client.messages.stream.return_value = FakeAnthropicStream(
        chunks=["Hello ", "world"],
        final_message=build_final_message(input_tokens=120, output_tokens=80),
    )
    service = build_service(client=client, prompt_builder=prompt_builder)

    events = list(service.stream_estimate_from_transcript("crear dashboard"))

    assert events == [
        {"type": "delta", "content": "Hello "},
        {"type": "delta", "content": "world"},
        {
            "type": "metadata",
            "provider": LLMProvider.ANTHROPIC.value,
            "llm_model": ANTHROPIC_MODEL_DEFAULT,
            "num_tokens_input": 120,
            "num_tokens_response": 80,
            "num_tokens_total": 200,
            "input_token_cost": pytest.approx(0.00012),
            "output_token_cost": pytest.approx(0.0004),
            "total_token_cost": pytest.approx(0.00052),
        },
    ]
    prompt_builder.build_messages.assert_called_once_with("crear dashboard")
    client.messages.stream.assert_called_once_with(
        model=ANTHROPIC_MODEL_DEFAULT,
        max_tokens=ANTHROPIC_MAX_TOKENS_DEFAULT,
        system="System prompt",
        messages=[{"role": "user", "content": "Resumen de reunión: crear dashboard"}],
        temperature=0.2,
    )


def test_stream_estimate_from_transcript_uses_custom_model_and_max_tokens() -> None:
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.messages.stream.return_value = FakeAnthropicStream(
        chunks=["ok"],
        final_message=build_final_message(),
    )
    service = build_service(client=client, prompt_builder=prompt_builder)

    list(
        service.stream_estimate_from_transcript(
            "texto",
            model="claude-sonnet-4-0",
            max_tokens=1024,
        )
    )

    client.messages.stream.assert_called_once_with(
        model="claude-sonnet-4-0",
        max_tokens=1024,
        system=None,
        messages=[{"role": "user", "content": "texto"}],
        temperature=0.2,
    )


def test_stream_estimate_from_transcript_wraps_start_errors() -> None:
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.messages.stream.side_effect = RuntimeError("anthropic unavailable")
    service = build_service(client=client, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="An error occurred while generating the estimation",
    ):
        list(service.stream_estimate_from_transcript("texto"))


def test_stream_estimate_from_transcript_raises_when_content_is_empty() -> None:
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.messages.stream.return_value = FakeAnthropicStream(
        chunks=["", ""],
        final_message=build_final_message(),
    )
    service = build_service(client=client, prompt_builder=prompt_builder)

    with pytest.raises(EstimateServiceException, match="The LLM response content is empty"):
        list(service.stream_estimate_from_transcript("texto"))


def test_stream_estimate_from_transcript_raises_when_usage_is_missing() -> None:
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.messages.stream.return_value = FakeAnthropicStream(
        chunks=["ok"],
        final_message=SimpleNamespace(usage=None),
    )
    service = build_service(client=client, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="The LLM response did not include token usage metadata",
    ):
        list(service.stream_estimate_from_transcript("texto"))
