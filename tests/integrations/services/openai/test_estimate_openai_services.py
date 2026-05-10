from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config import LLMProvider
from app.constants.estimate_constants import OPENAI_MODEL_DEFAULT
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.openai import estimate_openai_services as service_module
from app.services.openai.estimate_openai_services import EstimateOpenAIService


def build_openai_response(
    content: str | None = " Estimacion generada por OpenAI. ",
    usage=None,
):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ],
        usage=usage
        if usage is not None
        else SimpleNamespace(
            prompt_tokens=120,
            completion_tokens=80,
            total_tokens=200,
        ),
    )


def build_service(client=None, prompt_builder=None) -> EstimateOpenAIService:
    return EstimateOpenAIService(
        client=client or Mock(),
        prompt_builder=prompt_builder or Mock(),
        settings=SimpleNamespace(OPENAI_API_KEY="test-openai-api-key"),
    )


def test_estimate_from_transcript_returns_estimate_response_dto(monkeypatch):
    messages = [{"role": "user", "content": "Resumen de reunión: crear login"}]
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = messages
    client = Mock()
    client.chat.completions.create.return_value = build_openai_response()
    token_costs = SimpleNamespace(
        input_token_cost=0.000018,
        output_token_cost=0.000048,
        total_token_cost=0.000066,
    )
    count_tokens = Mock(return_value=120)
    calculate_cost = Mock(return_value=token_costs)
    monkeypatch.setattr(service_module.OpenAITokenUtil, "count_tokens", count_tokens)
    monkeypatch.setattr(service_module.OpenAICostUtil, "calculate_cost", calculate_cost)
    service = build_service(client=client, prompt_builder=prompt_builder)

    response = service.estimate_from_transcript("crear login")

    assert isinstance(response, EstimateResponseDTO)
    assert response.llm_provider == LLMProvider.OPENAI
    assert response.llm_model == OPENAI_MODEL_DEFAULT
    assert response.response == "Estimacion generada por OpenAI."
    assert response.num_tokens_input == 120
    assert response.num_tokens_response == 80
    assert response.num_tokens_total == 200
    assert response.input_token_cost == token_costs.input_token_cost
    assert response.output_token_cost == token_costs.output_token_cost
    assert response.total_token_cost == token_costs.total_token_cost


def test_estimate_from_transcript_builds_messages_and_calls_openai(monkeypatch):
    messages = [{"role": "user", "content": "Resumen de reunión: crear dashboard"}]
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = messages
    client = Mock()
    client.chat.completions.create.return_value = build_openai_response()
    count_tokens = Mock(return_value=120)
    calculate_cost = Mock(
        return_value=SimpleNamespace(
            input_token_cost=0.000018,
            output_token_cost=0.000048,
            total_token_cost=0.000066,
        )
    )
    monkeypatch.setattr(service_module.OpenAITokenUtil, "count_tokens", count_tokens)
    monkeypatch.setattr(service_module.OpenAICostUtil, "calculate_cost", calculate_cost)
    service = build_service(client=client, prompt_builder=prompt_builder)

    service.estimate_from_transcript("crear dashboard", model="gpt-4o-mini")

    prompt_builder.build_messages.assert_called_once_with("crear dashboard")
    count_tokens.assert_called_once_with(messages, "gpt-4o-mini")
    client.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )
    calculate_cost.assert_called_once_with(
        model="gpt-4o-mini",
        input_tokens=120,
        output_tokens=80,
    )


def test_estimate_from_transcript_wraps_openai_client_errors(monkeypatch):
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.chat.completions.create.side_effect = RuntimeError("openai unavailable")
    monkeypatch.setattr(service_module.OpenAITokenUtil, "count_tokens", Mock(return_value=1))
    service = build_service(client=client, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="An error occurred while generating the estimation",
    ):
        service.estimate_from_transcript("texto")


def test_estimate_from_transcript_raises_when_usage_is_missing(monkeypatch):
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.chat.completions.create.return_value = build_openai_response(usage=None)
    client.chat.completions.create.return_value.usage = None
    monkeypatch.setattr(service_module.OpenAITokenUtil, "count_tokens", Mock(return_value=1))
    service = build_service(client=client, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="The LLM response did not include token usage metadata",
    ):
        service.estimate_from_transcript("texto")


@pytest.mark.parametrize("content", ["", None])
def test_estimate_from_transcript_raises_when_response_content_is_empty(
    monkeypatch,
    content,
):
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    client = Mock()
    client.chat.completions.create.return_value = build_openai_response(content=content)
    monkeypatch.setattr(service_module.OpenAITokenUtil, "count_tokens", Mock(return_value=1))
    service = build_service(client=client, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="The LLM response content is empty",
    ):
        service.estimate_from_transcript("texto")
