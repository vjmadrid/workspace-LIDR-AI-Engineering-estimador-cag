import pytest
from pydantic import ValidationError

from app.responses.estimate_responses import EstimateResponse, generate_estimate_response
from tests.units.app.responses.estimate_response_factory import (
    EstimateResponseFactory,
)

@pytest.mark.parametrize(
    "overrides",
    [
        {"provider": None},
        {"llm_model": None},
        {"estimation": None},
    ],
)
def test_estimate_response_rejects_invalid_required_fields(overrides):
    with pytest.raises(ValidationError):
        EstimateResponseFactory.build(**overrides)


def test_estimate_response_rejects_extra_fields():
    with pytest.raises(ValidationError):
        EstimateResponseFactory.build(unexpected="extra")


def test_estimate_response_rejects_extra_metadata_fields():
    payload = EstimateResponseFactory.build_payload()
    payload["metadata"]["token_metadata"]["unexpected"] = "extra"

    with pytest.raises(ValidationError):
        EstimateResponse(**payload)
