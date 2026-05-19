import pytest
from pydantic import ValidationError

from tests.units.app.requests.estimate_request_factory import (
    EstimateLLMWrapperRequestFactory,
)


@pytest.mark.parametrize("description", ["", "   "])
def test_estimate_llmwrapper_request_rejects_empty_description(description):
    with pytest.raises(ValidationError):
        EstimateLLMWrapperRequestFactory.build(description=description)


def test_estimate_llmwrapper_request_rejects_short_description():
    with pytest.raises(ValidationError):
        EstimateLLMWrapperRequestFactory.build(description="Too short")


def test_estimate_llmwrapper_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        EstimateLLMWrapperRequestFactory.build(unexpected="extra")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("project_type", "unknown_project_type"),
        ("detail_level", "unknown_detail_level"),
        ("output_format", "unknown_output_format"),
    ],
)
def test_estimate_llmwrapper_request_rejects_unknown_enum_values(field, value):
    with pytest.raises(ValidationError):
        EstimateLLMWrapperRequestFactory.build(**{field: value})
