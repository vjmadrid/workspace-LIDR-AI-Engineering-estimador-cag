import pytest

from app.core.cost.utils import (
    LLMWrapperCostUtil,
    normalise_litellm_model_name,
    provider_from_litellm_model,
)

ONE_MILLION_TOKENS = 1_000_000
OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
PREFIXED_ANTHROPIC_MODEL = f"anthropic/{ANTHROPIC_MODEL}"
UNKNOWN_MODEL = "custom-model"


def calculate_cost_for_million_token_prompt(model: str):
    return LLMWrapperCostUtil.calculate_cost(
        model=model,
        input_tokens=ONE_MILLION_TOKENS,
        output_tokens=ONE_MILLION_TOKENS,
    )


def test_normalise_litellm_model_name_strips_provider_prefix():
    assert normalise_litellm_model_name(PREFIXED_ANTHROPIC_MODEL) == ANTHROPIC_MODEL


@pytest.mark.parametrize(
    ("model", "expected_provider"),
    [
        (OPENAI_MODEL, "openai"),
        ("openai/gpt-4o", "openai"),
        (ANTHROPIC_MODEL, "anthropic"),
        ("anthropic/claude-sonnet-4-5", "anthropic"),
        (UNKNOWN_MODEL, "unknown"),
    ],
)
def test_provider_from_litellm_model(model, expected_provider):
    assert provider_from_litellm_model(model) == expected_provider


def test_llmwrapper_cost_util_calculates_openai_total_cost():
    token_costs = calculate_cost_for_million_token_prompt(OPENAI_MODEL)

    assert token_costs.llm_model == OPENAI_MODEL
    assert token_costs.input_token_cost == pytest.approx(0.15)
    assert token_costs.output_token_cost == pytest.approx(0.60)
    assert token_costs.total_token_cost == pytest.approx(0.75)


def test_llmwrapper_cost_util_calculates_anthropic_total_cost_with_prefixed_model():
    token_costs = calculate_cost_for_million_token_prompt(PREFIXED_ANTHROPIC_MODEL)

    assert token_costs.llm_model == ANTHROPIC_MODEL
    assert token_costs.input_token_cost == pytest.approx(1.00)
    assert token_costs.output_token_cost == pytest.approx(5.00)
    assert token_costs.total_token_cost == pytest.approx(6.00)


def test_llmwrapper_cost_util_returns_zero_for_unknown_provider():
    token_costs = calculate_cost_for_million_token_prompt(UNKNOWN_MODEL)

    assert token_costs.llm_model == UNKNOWN_MODEL
    assert token_costs.total_token_cost == 0


def test_llmwrapper_cost_util_calculates_rounded_total_float():
    total_cost = LLMWrapperCostUtil.calculate_total_cost(
        model=OPENAI_MODEL,
        input_tokens=ONE_MILLION_TOKENS,
        output_tokens=ONE_MILLION_TOKENS,
    )

    assert total_cost == pytest.approx(0.75)
