import pytest
from pydantic import ValidationError

from tests.units.app.requests.estimate_request_factory import EstimateRequestFactory


@pytest.mark.parametrize("transcription", ["", "   "])
def test_estimate_request_rejects_empty_transcription(transcription):
    with pytest.raises(ValidationError):
        EstimateRequestFactory.build(transcription=transcription)


def test_estimate_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        EstimateRequestFactory.build(unexpected="extra")
