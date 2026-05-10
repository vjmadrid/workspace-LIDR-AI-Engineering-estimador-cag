import pytest
from pydantic import ValidationError

from app.requests.estimate_requests import EstimateRequest
from tests.units.app.requests.estimate_request_factory import EstimateRequestFactory


def test_estimate_request_is_created_from_factory_defaults():
    request = EstimateRequestFactory.build()

    assert isinstance(request, EstimateRequest)
    assert request.transcription == EstimateRequestFactory.DEFAULT_TRANSCRIPTION


def test_estimate_request_is_created_with_custom_transcription():
    transcription = "Crear un dashboard para revisar estimaciones historicas."

    request = EstimateRequestFactory.build(transcription=transcription)

    assert request.transcription == transcription


def test_estimate_request_normalizes_transcription_whitespace():
    request = EstimateRequestFactory.build(transcription="  Estimar nuevo flujo de pago.  ")

    assert request.transcription == "Estimar nuevo flujo de pago."
