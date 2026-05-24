from app.guardrails.output import enforce_scope_response
from app.responses.estimate_llmwrapper_advanced_responses import (
    LOW_CONFIDENCE_THRESHOLD,
    OUT_OF_SCOPE_PREFIX,
    EstimationResult,
)
from tests.units.app.responses.estimate_response_factory import EstimationResultFactory


def test_enforce_scope_response_returns_high_confidence_result_unchanged():
    result = EstimationResultFactory.build(confidence_pct=LOW_CONFIDENCE_THRESHOLD)

    filtered = enforce_scope_response(result)

    assert filtered is result


def test_enforce_scope_response_returns_already_marked_result_unchanged():
    result = EstimationResultFactory.build(
        summary=f"{OUT_OF_SCOPE_PREFIX} not enough information to estimate confidently.",
        confidence_pct=LOW_CONFIDENCE_THRESHOLD - 1,
    )

    filtered = enforce_scope_response(result)

    assert filtered is result


def test_enforce_scope_response_rewrites_low_confidence_result():
    result = EstimationResult.model_construct(
        summary="The description is too vague to estimate with confidence.",
        confidence_pct=LOW_CONFIDENCE_THRESHOLD - 1,
        phases=[],
        total_duration_weeks=1,
        total_cost_eur=1,
    )

    filtered = enforce_scope_response(result)

    assert filtered is not result
    assert filtered.summary.startswith(OUT_OF_SCOPE_PREFIX)
    assert filtered.confidence_pct == LOW_CONFIDENCE_THRESHOLD - 1
    assert filtered.total_duration_weeks == 1
    assert filtered.total_cost_eur == 0
    assert len(filtered.phases) == 1
    assert filtered.phases[0].name == "Not estimated"
