from unittest.mock import Mock, patch

import pytest

from app.services.llmservice import estimate_llm_services
from app.services.llmservice.estimate_llm_services import (
    DEFAULT_MAX_TOKENS,
    EXTRACTION_MAX_TOKENS,
    EXTRACTION_SYSTEM_PROMPT,
    INLINE_CLEANING_BLOCK,
    LLMServiceError,
    GenerationOptions,
    build_system_prompt,
    extract_requirements,
    generate_estimation,
)


def build_llm_result(
    estimation: str = "Generated estimation",
    *,
    input_tokens: int = 100,
    output_tokens: int = 50,
    cost_usd: float = 0.25,
    cache_hit: bool | None = None,
):
    result = {
        "estimation": estimation,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
        "cost_usd": cost_usd,
    }
    if cache_hit is not None:
        result["cache_hit"] = cache_hit
    return result


def test_build_system_prompt_includes_core_sections_without_examples():
    system_prompt = build_system_prompt(use_examples=False)

    assert "You are a senior software consultant" in system_prompt
    assert "62.50 EUR/hour" in system_prompt
    assert "Generate an estimation for the project described above." in system_prompt
    assert "reference estimations from previous projects" not in system_prompt
    assert INLINE_CLEANING_BLOCK not in system_prompt


def test_build_system_prompt_can_include_inline_cleaning_instructions():
    system_prompt = build_system_prompt(use_examples=False, inline_cleaning=True)

    assert INLINE_CLEANING_BLOCK in system_prompt


def test_build_system_prompt_adds_formatted_examples_when_enabled():
    example = Mock()

    with (
        patch.object(estimate_llm_services, "select_examples", return_value=[example]) as select_examples,
        patch.object(
            estimate_llm_services,
            "format_examples_for_prompt",
            return_value="FORMATTED EXAMPLES",
        ) as format_examples,
    ):
        system_prompt = build_system_prompt(
            example_format="json",
            num_examples=2,
            use_examples=True,
        )

    select_examples.assert_called_once_with(2)
    format_examples.assert_called_once_with([example], "json")
    assert "reference estimations from previous projects" in system_prompt
    assert "FORMATTED EXAMPLES" in system_prompt


def test_extract_requirements_uses_extraction_prompt_and_returns_usage():
    opts = GenerationOptions(model="gpt-4o-mini")
    invoke_llm = Mock(
        return_value=build_llm_result(
            estimation="- Requirement A",
            input_tokens=40,
            output_tokens=12,
            cost_usd=0.001,
        )
    )

    with patch.object(estimate_llm_services, "_invoke_llm", invoke_llm):
        requirements, usage, cost = extract_requirements("raw transcript", opts)

    assert requirements == "- Requirement A"
    assert usage == {"input": 40, "output": 12}
    assert cost == 0.001
    invoke_llm.assert_called_once_with(
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
        user_message="raw transcript",
        model_override="gpt-4o-mini",
        max_tokens=EXTRACTION_MAX_TOKENS,
        thinking_budget=None,
    )


def test_generate_estimation_invokes_llm_and_enriches_response_metadata():
    invoke_llm = Mock(
        return_value=build_llm_result(
            estimation="Final estimation",
            input_tokens=120,
            output_tokens=80,
            cost_usd=0.1234567,
        )
    )
    opts = GenerationOptions(
        preprocessing="none",
        use_examples=False,
        model="gpt-4o-mini",
        max_tokens=900,
        thinking_budget=256,
    )

    with patch.object(estimate_llm_services, "_invoke_llm", invoke_llm):
        result = generate_estimation("meeting transcript", opts)

    assert result["estimation"] == "Final estimation"
    assert result["preprocessing"] == "none"
    assert result["extracted_requirements"] is None
    assert result["usage"]["preprocessing_input_tokens"] == 0
    assert result["usage"]["preprocessing_output_tokens"] == 0
    assert result["cache_hit"] is False
    assert result["cost_usd"] == 0.123457
    assert isinstance(result["latency_ms"], int)
    invoke_llm.assert_called_once()
    assert invoke_llm.call_args.kwargs["user_message"] == "meeting transcript"
    assert invoke_llm.call_args.kwargs["model_override"] == "gpt-4o-mini"
    assert invoke_llm.call_args.kwargs["max_tokens"] == 900
    assert invoke_llm.call_args.kwargs["thinking_budget"] == 256


def test_generate_estimation_preserves_cache_hit_returned_by_wrapper():
    invoke_llm = Mock(return_value=build_llm_result(cache_hit=True))

    with patch.object(estimate_llm_services, "_invoke_llm", invoke_llm):
        result = generate_estimation("meeting transcript", GenerationOptions(use_examples=False))

    assert result["cache_hit"] is True


def test_generate_estimation_uses_inline_cleaning_prompt_when_requested():
    invoke_llm = Mock(return_value=build_llm_result())
    opts = GenerationOptions(preprocessing="inline_cleaning", use_examples=False)

    with patch.object(estimate_llm_services, "_invoke_llm", invoke_llm):
        generate_estimation("meeting transcript", opts)

    assert INLINE_CLEANING_BLOCK in invoke_llm.call_args.kwargs["system_prompt"]


def test_generate_estimation_two_phase_uses_extracted_requirements_for_final_call():
    extraction_result = build_llm_result(
        estimation="- Clean requirement",
        input_tokens=30,
        output_tokens=10,
        cost_usd=0.001,
    )
    final_result = build_llm_result(
        estimation="Final estimation",
        input_tokens=200,
        output_tokens=100,
        cost_usd=0.01,
    )
    invoke_llm = Mock(side_effect=[extraction_result, final_result])
    opts = GenerationOptions(preprocessing="two_phase", use_examples=False)

    with patch.object(estimate_llm_services, "_invoke_llm", invoke_llm):
        result = generate_estimation("messy transcript", opts)

    assert result["preprocessing"] == "two_phase"
    assert result["extracted_requirements"] == "- Clean requirement"
    assert result["usage"]["preprocessing_input_tokens"] == 30
    assert result["usage"]["preprocessing_output_tokens"] == 10
    assert result["cost_usd"] == 0.011

    extraction_call, final_call = invoke_llm.call_args_list
    assert extraction_call.kwargs["system_prompt"] == EXTRACTION_SYSTEM_PROMPT
    assert extraction_call.kwargs["max_tokens"] == EXTRACTION_MAX_TOKENS
    assert final_call.kwargs["user_message"] == "- Clean requirement"
    assert final_call.kwargs["max_tokens"] == DEFAULT_MAX_TOKENS


def test_generate_estimation_wraps_llm_errors():
    with patch.object(estimate_llm_services, "_invoke_llm", side_effect=RuntimeError("provider down")):
        with pytest.raises(LLMServiceError, match="LLM call failed: provider down"):
            generate_estimation("meeting transcript", GenerationOptions(use_examples=False))
