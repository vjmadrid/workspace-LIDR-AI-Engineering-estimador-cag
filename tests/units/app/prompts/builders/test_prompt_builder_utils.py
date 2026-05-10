from unittest.mock import Mock

from app.prompts.builders import utils as prompt_builder_utils
from app.prompts.builders.utils import PromptBuilderUtil


def test_build_system_prompt_returns_expected_base_instructions(monkeypatch):
    monkeypatch.setattr(
        prompt_builder_utils.ContextExamplesUtil,
        "format_examples_for_prompt",
        Mock(return_value="FORMATTED EXAMPLES"),
    )

    prompt = PromptBuilderUtil.build_system_prompt()

    assert "You are a senior software consultant with 15+ years of experience" in prompt
    assert "Your output MUST follow this exact format:" in prompt
    assert "- Project title as an H2 heading" in prompt
    assert "- A task breakdown table with columns: Task, Hours, Cost (EUR)" in prompt
    assert "- Total hours" in prompt
    assert "- Total cost in EUR" in prompt
    assert "- Recommended team composition" in prompt
    assert "- Estimated duration in weeks" in prompt
    assert "62.50 EUR/hour" in prompt
    assert "50 EUR/hour" in prompt


def test_build_system_prompt_appends_formatted_examples(monkeypatch):
    monkeypatch.setattr(
        prompt_builder_utils.ContextExamplesUtil,
        "format_examples_for_prompt",
        Mock(return_value="FORMATTED EXAMPLES"),
    )

    prompt = PromptBuilderUtil.build_system_prompt()

    assert prompt.endswith("FORMATTED EXAMPLES")


def test_build_system_prompt_formats_estimation_examples(monkeypatch):
    format_examples_for_prompt = Mock(return_value="FORMATTED EXAMPLES")
    monkeypatch.setattr(
        prompt_builder_utils.ContextExamplesUtil,
        "format_examples_for_prompt",
        format_examples_for_prompt,
    )

    PromptBuilderUtil.build_system_prompt()

    format_examples_for_prompt.assert_called_once_with(
        prompt_builder_utils.ESTIMATION_EXAMPLES
    )


def test_build_system_prompt_returns_non_empty_string(monkeypatch):
    monkeypatch.setattr(
        prompt_builder_utils.ContextExamplesUtil,
        "format_examples_for_prompt",
        Mock(return_value="FORMATTED EXAMPLES"),
    )

    prompt = PromptBuilderUtil.build_system_prompt()

    assert isinstance(prompt, str)
    assert prompt
