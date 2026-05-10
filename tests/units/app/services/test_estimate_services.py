from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config import LLMProvider
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.estimate_services import EstimateService


def build_service(
    provider: LLMProvider,
    openai_service=None,
    anthropic_service=None,
    llmlite_service=None,
):
    return EstimateService(
        settings=SimpleNamespace(LLM_PROVIDER=provider),
        openai_service=openai_service or Mock(),
        anthropic_service=anthropic_service or Mock(),
        llmlite_service=llmlite_service or Mock(),
    )


def test_estimate_from_transcript_delegates_to_openai_service():
    openai_service = Mock()
    openai_service.estimate_from_transcript.return_value = "openai-response"
    anthropic_service = Mock()
    service = build_service(
        LLMProvider.OPENAI,
        openai_service=openai_service,
        anthropic_service=anthropic_service,
    )

    response = service.estimate_from_transcript("transcript")

    assert response == "openai-response"
    openai_service.estimate_from_transcript.assert_called_once_with("transcript")
    anthropic_service.estimate_from_transcript.assert_not_called()


def test_estimate_from_transcript_delegates_to_anthropic_service():
    openai_service = Mock()
    anthropic_service = Mock()
    anthropic_service.estimate_from_transcript.return_value = "anthropic-response"
    service = build_service(
        LLMProvider.ANTHROPIC,
        openai_service=openai_service,
        anthropic_service=anthropic_service,
    )

    response = service.estimate_from_transcript("transcript")

    assert response == "anthropic-response"
    anthropic_service.estimate_from_transcript.assert_called_once_with("transcript")
    openai_service.estimate_from_transcript.assert_not_called()


def test_estimate_from_transcript_delegates_to_llmlite_service():
    openai_service = Mock()
    anthropic_service = Mock()
    llmlite_service = Mock()
    llmlite_service.estimate_from_transcript.return_value = "llmlite-response"
    service = build_service(
        LLMProvider.LLMLITE,
        openai_service=openai_service,
        anthropic_service=anthropic_service,
        llmlite_service=llmlite_service,
    )

    response = service.estimate_from_transcript("transcript")

    assert response == "llmlite-response"
    llmlite_service.estimate_from_transcript.assert_called_once_with("transcript")
    openai_service.estimate_from_transcript.assert_not_called()
    anthropic_service.estimate_from_transcript.assert_not_called()


def test_estimate_from_transcript_preserves_service_exceptions():
    openai_service = Mock()
    openai_service.estimate_from_transcript.side_effect = EstimateServiceException(
        "service failed"
    )
    service = build_service(LLMProvider.OPENAI, openai_service=openai_service)

    with pytest.raises(EstimateServiceException, match="service failed"):
        service.estimate_from_transcript("transcript")


def test_estimate_from_transcript_wraps_unexpected_exceptions():
    openai_service = Mock()
    openai_service.estimate_from_transcript.side_effect = RuntimeError("boom")
    service = build_service(LLMProvider.OPENAI, openai_service=openai_service)

    with pytest.raises(EstimateServiceException, match="LLM call failed: boom"):
        service.estimate_from_transcript("transcript")
