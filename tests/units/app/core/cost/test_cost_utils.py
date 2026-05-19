import pytest

from app.core.cost.utils import (
    LLMWrapperCostUtil,
    normalise_litellm_model_name,
    provider_from_litellm_model,
)


def test_normalise_litellm_model_name_strips_provider_prefix():
    assert normalise_litellm_model_name("anthropic/claude-haiku-4-5-20251001") == (
        "claude-haiku-4-5-20251001"
    )


@pytest.mark.parametrize(
    ("model", "expected_provider"),
    [
        ("gpt-4o-mini", "openai"),
        ("openai/gpt-4o", "openai"),
        ("claude-haiku-4-5-20251001", "anthropic"),
        ("anthropic/claude-sonnet-4-5", "anthropic"),
        ("custom-model", "unknown"),
    ],
)
def test_provider_from_litellm_model(model, expected_provider):
    assert provider_from_litellm_model(model) == expected_provider


def test_llmwrapper_cost_util_calculates_openai_total_cost():
    token_costs = LLMWrapperCostUtil.calculate_cost(
        model="gpt-4o-mini",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert token_costs.llm_model == "gpt-4o-mini"
    assert token_costs.input_token_cost == pytest.approx(0.15)
    assert token_costs.output_token_cost == pytest.approx(0.60)
    assert token_costs.total_token_cost == pytest.approx(0.75)


def test_llmwrapper_cost_util_calculates_anthropic_total_cost_with_prefixed_model():
    token_costs = LLMWrapperCostUtil.calculate_cost(
        model="anthropic/claude-haiku-4-5-20251001",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert token_costs.llm_model == "claude-haiku-4-5-20251001"
    assert token_costs.input_token_cost == pytest.approx(1.00)
    assert token_costs.output_token_cost == pytest.approx(5.00)
    assert token_costs.total_token_cost == pytest.approx(6.00)


def test_llmwrapper_cost_util_returns_zero_for_unknown_provider():
    token_costs = LLMWrapperCostUtil.calculate_cost(
        model="custom-model",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert token_costs.llm_model == "custom-model"
    assert token_costs.total_token_cost == 0


def test_llmwrapper_cost_util_calculates_rounded_total_float():
    total_cost = LLMWrapperCostUtil.calculate_total_cost(
        model="gpt-4o-mini",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    assert total_cost == pytest.approx(0.75)
