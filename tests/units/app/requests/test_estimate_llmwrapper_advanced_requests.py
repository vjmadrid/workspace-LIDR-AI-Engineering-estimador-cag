import pytest
from pydantic import ValidationError

from app.requests.estimate_llmwrapper_advanced_requests import EstimateLLMWrapperAdvancedRequest
from tests.units.app.requests.estimate_request_factory import (
    EstimateLLMWrapperAdvancedRequestFactory,
)

EMPTY_DESCRIPTIONS = ["", "   "]
INVALID_ENUM_VALUES = [
    ("project_type", "unknown_project_type"),
    ("detail_level", "unknown_detail_level"),
    ("output_format", "unknown_output_format"),
]


def assert_request_is_invalid(**overrides) -> None:
    with pytest.raises(ValidationError):
        EstimateLLMWrapperAdvancedRequestFactory.build(**overrides)


@pytest.mark.parametrize("description", EMPTY_DESCRIPTIONS)
def test_estimate_llmwrapper_advanced_request_rejects_empty_description(description):
    assert_request_is_invalid(description=description)


def test_estimate_llmwrapper_advanced_request_rejects_short_description():
    assert_request_is_invalid(description="Too short")


def test_estimate_llmwrapper_advanced_request_rejects_extra_fields():
    assert_request_is_invalid(unexpected="extra")


@pytest.mark.parametrize(("field", "value"), INVALID_ENUM_VALUES)
def test_estimate_llmwrapper_advanced_request_rejects_unknown_enum_values(field, value):
    assert_request_is_invalid(**{field: value})


def test_estimate_llmwrapper_advanced_request_normalizes_description_whitespace():
    request = EstimateLLMWrapperAdvancedRequestFactory.build(
        description=f"  {EstimateLLMWrapperAdvancedRequestFactory.DEFAULT_DESCRIPTION}  "
    )

    assert isinstance(request, EstimateLLMWrapperAdvancedRequest)
    assert request.description == EstimateLLMWrapperAdvancedRequestFactory.DEFAULT_DESCRIPTION
