import pytest
from pydantic import ValidationError

from app.responses.estimate_llmwrapper_advanced_responses import (
    LOW_CONFIDENCE_THRESHOLD,
    OUT_OF_SCOPE_PREFIX,
    EstimationLLMWrapperAdvancedResponse,
    EstimationResult,
    Phase,
)
from tests.units.app.responses.estimate_response_factory import (
    EstimateLLMWrapperAdvancedResponseFactory,
    EstimationResultFactory,
    PhaseFactory,
)

INVALID_PHASE_OVERRIDES = [
    {"name": ""},
    {"duration_weeks": 0},
    {"duration_weeks": 53},
    {"cost_eur": -1},
    {"cost_eur": 1_000_001},
    {"summary": "short"},
]

INVALID_RESULT_OVERRIDES = [
    {"summary": "short"},
    {"confidence_pct": -1},
    {"confidence_pct": 101},
    {"phases": []},
    {"phases": [PhaseFactory.build_payload()] * 9},
    {"total_duration_weeks": 0},
    {"total_duration_weeks": 105},
    {"total_cost_eur": -1},
    {"total_cost_eur": 2_000_001},
]


def assert_phase_is_invalid(**overrides) -> None:
    with pytest.raises(ValidationError):
        PhaseFactory.build(**overrides)


def assert_result_is_invalid(**overrides) -> None:
    with pytest.raises(ValidationError):
        EstimationResultFactory.build(**overrides)


def assert_response_is_invalid(**overrides) -> None:
    with pytest.raises(ValidationError):
        EstimateLLMWrapperAdvancedResponseFactory.build(**overrides)


def test_phase_is_created_from_factory_defaults():
    phase = PhaseFactory.build()

    assert isinstance(phase, Phase)
    assert phase.name == PhaseFactory.DEFAULT_NAME
    assert phase.duration_weeks == PhaseFactory.DEFAULT_DURATION_WEEKS
    assert phase.cost_eur == PhaseFactory.DEFAULT_COST_EUR
    assert phase.summary == PhaseFactory.DEFAULT_SUMMARY


@pytest.mark.parametrize("overrides", INVALID_PHASE_OVERRIDES)
def test_phase_rejects_invalid_fields(overrides):
    assert_phase_is_invalid(**overrides)


def test_phase_rejects_extra_fields():
    assert_phase_is_invalid(unexpected="extra")


def test_estimation_result_is_created_from_factory_defaults():
    result = EstimationResultFactory.build()

    assert isinstance(result, EstimationResult)
    assert result.summary == EstimationResultFactory.DEFAULT_SUMMARY
    assert result.confidence_pct == EstimationResultFactory.DEFAULT_CONFIDENCE_PCT
    assert result.total_duration_weeks == EstimationResultFactory.DEFAULT_TOTAL_DURATION_WEEKS
    assert result.total_cost_eur == EstimationResultFactory.DEFAULT_TOTAL_COST_EUR
    assert len(result.phases) == 1


@pytest.mark.parametrize("overrides", INVALID_RESULT_OVERRIDES)
def test_estimation_result_rejects_invalid_fields(overrides):
    assert_result_is_invalid(**overrides)


def test_estimation_result_rejects_extra_fields():
    assert_result_is_invalid(unexpected="extra")


def test_estimation_result_rejects_total_cost_that_does_not_match_phase_sum():
    assert_result_is_invalid(total_cost_eur=PhaseFactory.DEFAULT_COST_EUR + 1)


def test_estimation_result_rejects_low_confidence_without_out_of_scope_prefix():
    assert_result_is_invalid(confidence_pct=LOW_CONFIDENCE_THRESHOLD - 1)


def test_estimation_result_accepts_low_confidence_with_out_of_scope_prefix():
    result = EstimationResultFactory.build(
        summary=f"{OUT_OF_SCOPE_PREFIX} not enough information to estimate confidently.",
        confidence_pct=LOW_CONFIDENCE_THRESHOLD - 1,
    )

    assert result.summary.startswith(OUT_OF_SCOPE_PREFIX)
    assert result.confidence_pct == LOW_CONFIDENCE_THRESHOLD - 1


def test_estimate_llmwrapper_advanced_response_is_created_from_factory_defaults():
    response = EstimateLLMWrapperAdvancedResponseFactory.build()

    assert isinstance(response, EstimationLLMWrapperAdvancedResponse)
    assert isinstance(response.result, EstimationResult)
    assert response.prompt_version == EstimateLLMWrapperAdvancedResponseFactory.DEFAULT_PROMPT_VERSION
    assert response.cached is EstimateLLMWrapperAdvancedResponseFactory.DEFAULT_CACHED


def test_estimate_llmwrapper_advanced_response_defaults_cached_to_false():
    payload = EstimateLLMWrapperAdvancedResponseFactory.build_payload()
    payload.pop("cached")

    response = EstimationLLMWrapperAdvancedResponse(**payload)

    assert response.cached is False


def test_estimate_llmwrapper_advanced_response_rejects_invalid_required_fields():
    assert_response_is_invalid(result=None)
    assert_response_is_invalid(prompt_version=None)


def test_estimate_llmwrapper_advanced_response_rejects_extra_fields():
    assert_response_is_invalid(unexpected="extra")
