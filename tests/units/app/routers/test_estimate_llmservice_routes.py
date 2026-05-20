from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.constants.estimate_constants import (
    ESTIMATE_LLMSERVICE_ENDPOINT,
    ESTIMATE_LLMSERVICE_STREAM_ENDPOINT,
)
from app.dependencies import get_llm_wrapper
from app.main import app
from app.routers import estimate_llmservice_routes
from app.services.llmservice.estimate_llm_services import LLMServiceError

ENDPOINT = f"/api/v1{ESTIMATE_LLMSERVICE_ENDPOINT}"
STREAM_ENDPOINT = f"/api/v1{ESTIMATE_LLMSERVICE_STREAM_ENDPOINT}"


def build_llmservice_result(**overrides: Any) -> dict[str, Any]:
    result = {
        "estimation": "## Project title\n\nGenerated estimation",
        "model": "gpt-4o-mini",
        "provider": "openai",
        "finish_reason": "stop",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30,
            "preprocessing_input_tokens": 0,
            "preprocessing_output_tokens": 0,
        },
        "preprocessing": "none",
        "extracted_requirements": None,
        "latency_ms": 1,
        "cache_hit": False,
        "cost_usd": 0.001,
    }
    result.update(overrides)
    return result


class FakeStreamingWrapper:
    def __init__(self, chunks: list[str] | None = None, exception: Exception | None = None) -> None:
        self.chunks = chunks or ["hello ", "world"]
        self.exception = exception
        self.calls: list[dict[str, Any]] = []

    def complete_stream(self, **kwargs: Any):
        self.calls.append(kwargs)
        if self.exception:
            raise self.exception
        yield from self.chunks


@pytest.fixture
def fake_streaming_wrapper() -> FakeStreamingWrapper:
    wrapper = FakeStreamingWrapper()
    app.dependency_overrides[get_llm_wrapper] = lambda: wrapper
    yield wrapper
    app.dependency_overrides.pop(get_llm_wrapper, None)


VALID_PAYLOAD = {
    "transcription": (
        "El cliente solicita una aplicación para gestionar reservas de salas, "
        "notificaciones y autenticación corporativa con integración de calendario."
    ),
}


def post_estimation(client: TestClient, payload: dict | None = None):
    return client.post(ENDPOINT, json=payload or VALID_PAYLOAD)


def post_stream(client: TestClient, payload: dict | None = None):
    return client.post(STREAM_ENDPOINT, json=payload or VALID_PAYLOAD)


def test_create_estimation_returns_llmservice_response(client: TestClient) -> None:
    generate_estimation = Mock(return_value=build_llmservice_result())

    with patch.object(estimate_llmservice_routes, "generate_estimation", generate_estimation):
        response = post_estimation(client)

    assert response.status_code == 200
    body = response.json()
    assert body["estimation"] == "## Project title\n\nGenerated estimation"
    assert body["model"] == "gpt-4o-mini"
    assert body["provider"] == "openai"
    assert body["usage"]["input_tokens"] == 10
    assert body["cache_hit"] is False
    assert body["cost_usd"] == 0.001
    assert body["validation"] is not None

    generate_estimation.assert_called_once()
    transcription, opts = generate_estimation.call_args.args
    assert transcription == VALID_PAYLOAD["transcription"]
    assert opts.preprocessing == "none"
    assert opts.example_format == "markdown"
    assert opts.num_examples == 3
    assert opts.use_examples is True


def test_create_estimation_can_skip_structural_evaluation(client: TestClient) -> None:
    payload = {**VALID_PAYLOAD, "evaluate": False}
    generate_estimation = Mock(return_value=build_llmservice_result())

    with patch.object(estimate_llmservice_routes, "generate_estimation", generate_estimation):
        response = post_estimation(client, payload)

    assert response.status_code == 200
    assert response.json()["validation"] is None


def test_create_estimation_returns_500_for_llmservice_error(client: TestClient) -> None:
    with patch.object(
        estimate_llmservice_routes,
        "generate_estimation",
        side_effect=LLMServiceError("LLM call failed"),
    ):
        response = post_estimation(client)

    assert response.status_code == 500
    assert response.json() == {"detail": "LLM call failed"}


def test_create_estimation_validates_short_transcription(client: TestClient) -> None:
    response = post_estimation(client, {"transcription": "too short"})

    assert response.status_code == 422
    assert any(error["loc"][-1] == "transcription" for error in response.json()["detail"])


def test_stream_estimation_returns_sse_tokens(
    client: TestClient,
    fake_streaming_wrapper: FakeStreamingWrapper,
) -> None:
    response = post_stream(client)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: token\r\ndata: hello \r\n" in response.text
    assert "event: token\r\ndata: world\r\n" in response.text
    assert "event: done\r\ndata: [DONE]\r\n" in response.text

    assert len(fake_streaming_wrapper.calls) == 1
    call = fake_streaming_wrapper.calls[0]
    assert VALID_PAYLOAD["transcription"] == call["user_message"]
    assert call["model_override"] is None
    assert call["max_tokens"] == 4000
