from fastapi.testclient import TestClient

from app.constants.estimate_constants import ESTIMATE_LLMLITE_ENDPOINT
from app.routers import estimate_llmlite_routes
from tests.units.app.requests.estimate_request_factory import EstimateRequestFactory
from tests.units.app.responses.estimate_response_factory import EstimateResponseDTOFactory
from tests.units.app.routers.route_test_helpers import (
    FakeEstimateService,
    assert_estimate_response_matches_dto,
    assert_service_error_response,
    assert_validation_error_for_field,
    post_estimation,
    service_exception,
    valid_estimate_payload,
)

ENDPOINT = f"/api/v1{ESTIMATE_LLMLITE_ENDPOINT}"


def test_valid_payload_returns_llmlite_estimate_response(client: TestClient, monkeypatch) -> None:
    dto = EstimateResponseDTOFactory.build(llm_provider="llmlite", llm_model="gpt-4o-mini")
    service = FakeEstimateService(response=dto)
    monkeypatch.setattr(estimate_llmlite_routes, "estimateLLMLiteService", service)

    response = post_estimation(client, ENDPOINT)

    assert_estimate_response_matches_dto(response, dto)
    assert service.transcriptions == [EstimateRequestFactory.DEFAULT_TRANSCRIPTION]


def test_missing_transcription_returns_422(client: TestClient) -> None:
    response = post_estimation(client, ENDPOINT, payload={})

    assert_validation_error_for_field(response, "transcription")


def test_blank_transcription_returns_422(client: TestClient) -> None:
    payload = valid_estimate_payload(transcription="   ")
    response = post_estimation(client, ENDPOINT, payload)

    assert_validation_error_for_field(response, "transcription")


def test_service_exception_returns_500(client: TestClient, monkeypatch) -> None:
    service = FakeEstimateService(exception=service_exception())
    monkeypatch.setattr(estimate_llmlite_routes, "estimateLLMLiteService", service)

    response = post_estimation(client, ENDPOINT)

    assert_service_error_response(response)
