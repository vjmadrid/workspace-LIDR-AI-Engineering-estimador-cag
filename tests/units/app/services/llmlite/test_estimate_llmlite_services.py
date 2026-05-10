from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config import LLMProvider
from app.constants.estimate_constants import LLMLITE_MODEL_DEFAULT
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.llmlite.estimate_llmlite_services import EstimateLLMLiteService


def build_llmlite_response(
    content: str | None = " Estimacion generada con LiteLLM. ",
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
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        ),
    )


def build_service(completion=None, prompt_builder=None, settings=None):
    return EstimateLLMLiteService(
        completion=completion or Mock(return_value=build_llmlite_response()),
        prompt_builder=prompt_builder or Mock(),
        settings=settings
        or SimpleNamespace(
            LLMLITE_MODEL=LLMLITE_MODEL_DEFAULT,
        ),
    )


def test_estimate_from_transcript_returns_estimate_response_dto():
    messages = [{"role": "user", "content": "Resumen de reunión: crear dashboard"}]
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = messages
    completion = Mock(return_value=build_llmlite_response())
    service = build_service(completion=completion, prompt_builder=prompt_builder)

    response = service.estimate_from_transcript("crear dashboard")

    assert isinstance(response, EstimateResponseDTO)
    assert response.llm_provider == LLMProvider.LLMLITE
    assert response.llm_model == LLMLITE_MODEL_DEFAULT
    assert response.response == "Estimacion generada con LiteLLM."
    assert response.num_tokens_input == 100
    assert response.num_tokens_response == 50
    assert response.num_tokens_total == 150
    assert response.total_token_cost > 0


def test_estimate_from_transcript_builds_messages_and_calls_litellm_completion():
    messages = [{"role": "user", "content": "Resumen de reunión: crear login"}]
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = messages
    completion = Mock(return_value=build_llmlite_response())
    service = build_service(completion=completion, prompt_builder=prompt_builder)

    service.estimate_from_transcript("crear login", model="gpt-4o-mini")

    prompt_builder.build_messages.assert_called_once_with("crear login")
    completion.assert_called_once_with(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )


def test_estimate_from_transcript_uses_model_from_settings_by_default():
    completion = Mock(return_value=build_llmlite_response())
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    service = build_service(
        completion=completion,
        prompt_builder=prompt_builder,
        settings=SimpleNamespace(LLMLITE_MODEL="custom/model"),
    )

    response = service.estimate_from_transcript("texto")

    assert response.llm_model == "custom/model"
    assert response.total_token_cost == 0
    completion.assert_called_once_with(
        model="custom/model",
        messages=[{"role": "user", "content": "texto"}],
        temperature=0.2,
    )


def test_estimate_from_transcript_wraps_completion_errors():
    completion = Mock(side_effect=RuntimeError("litellm unavailable"))
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    service = build_service(completion=completion, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="An error occurred while generating the estimation",
    ):
        service.estimate_from_transcript("texto")


def test_estimate_from_transcript_raises_when_usage_is_missing():
    completion = Mock(return_value=build_llmlite_response())
    completion.return_value.usage = None
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    service = build_service(completion=completion, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="The LLM response did not include token usage metadata",
    ):
        service.estimate_from_transcript("texto")


@pytest.mark.parametrize("content", ["", None])
def test_estimate_from_transcript_raises_when_response_content_is_empty(content):
    completion = Mock(return_value=build_llmlite_response(content=content))
    prompt_builder = Mock()
    prompt_builder.build_messages.return_value = [{"role": "user", "content": "texto"}]
    service = build_service(completion=completion, prompt_builder=prompt_builder)

    with pytest.raises(
        EstimateServiceException,
        match="The LLM response content is empty",
    ):
        service.estimate_from_transcript("texto")
