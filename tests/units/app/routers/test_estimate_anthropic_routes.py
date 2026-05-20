from fastapi.testclient import TestClient

from app.constants.estimate_constants import (
    ESTIMATE_ANTHROPIC_ENDPOINT,
    ESTIMATE_ANTHROPIC_STREAM_ENDPOINT,
)
from app.routers import estimate_anthropic_routes
from tests.units.app.requests.estimate_request_factory import EstimateRequestFactory
from tests.units.app.responses.estimate_response_factory import EstimateResponseDTOFactory
from tests.units.app.routers.route_test_helpers import (
    FakeEstimateService,
    assert_estimate_response_matches_dto,
    assert_service_error_response,
    assert_validation_error_for_field,
    parse_ndjson_response,
    post_estimation,
    service_exception,
    valid_estimate_payload,
)

ENDPOINT = f"/api/v1{ESTIMATE_ANTHROPIC_ENDPOINT}"
STREAM_ENDPOINT = f"/api/v1{ESTIMATE_ANTHROPIC_STREAM_ENDPOINT}"


def test_valid_payload_returns_anthropic_estimate_response(
    client: TestClient, monkeypatch
) -> None:
    dto = EstimateResponseDTOFactory.build(
        llm_provider="anthropic",
        llm_model="claude-haiku-4-5-20251001",
    )
    service = FakeEstimateService(response=dto)
    monkeypatch.setattr(estimate_anthropic_routes, "estimateAnthropicService", service)

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
    monkeypatch.setattr(estimate_anthropic_routes, "estimateAnthropicService", service)

    response = post_estimation(client, ENDPOINT)

    assert_service_error_response(response)


def test_stream_endpoint_returns_ndjson_events(client: TestClient, monkeypatch) -> None:
    events = [{"type": "delta", "content": "Hello"}, {"type": "metadata", "provider": "anthropic"}]
    service = FakeEstimateService(stream_events=events)
    monkeypatch.setattr(estimate_anthropic_routes, "estimateAnthropicService", service)

    response = post_estimation(client, STREAM_ENDPOINT)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert parse_ndjson_response(response) == events
    assert service.transcriptions == [EstimateRequestFactory.DEFAULT_TRANSCRIPTION]


def test_stream_endpoint_returns_error_event_on_service_exception(
    client: TestClient, monkeypatch
) -> None:
    service = FakeEstimateService(exception=service_exception())
    monkeypatch.setattr(estimate_anthropic_routes, "estimateAnthropicService", service)

    response = post_estimation(client, STREAM_ENDPOINT)

    assert response.status_code == 200
    assert parse_ndjson_response(response) == [
        {
            "type": "error",
            "message": "An error occurred while processing the estimation",
        }
    ]
