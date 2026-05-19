import json

from fastapi.testclient import TestClient

from app.exceptions.estimate_exceptions import EstimateServiceException
from tests.units.app.requests.estimate_request_factory import EstimateRequestFactory
from tests.units.app.responses.estimate_response_factory import EstimateResponseDTOFactory

VALID_TRANSCRIPTION = EstimateRequestFactory.DEFAULT_TRANSCRIPTION


class FakeEstimateService:
    def __init__(
        self,
        *,
        response=None,
        exception: Exception | None = None,
        stream_events: list[dict] | None = None,
    ) -> None:
        self.response = response or EstimateResponseDTOFactory.build()
        self.exception = exception
        self.stream_events = stream_events or []
        self.transcriptions: list[str] = []

    def estimate_from_transcript(self, transcription: str):
        self.transcriptions.append(transcription)
        if self.exception:
            raise self.exception
        return self.response

    def stream_estimate_from_transcript(self, transcription: str):
        self.transcriptions.append(transcription)
        if self.exception:
            raise self.exception
        yield from self.stream_events


def valid_estimate_payload(**overrides) -> dict:
    return EstimateRequestFactory.build_payload(**overrides)


def post_estimation(client: TestClient, endpoint: str, payload: dict | None = None):
    return client.post(endpoint, json=valid_estimate_payload() if payload is None else payload)


def assert_validation_error_for_field(response, field: str) -> None:
    assert response.status_code == 422
    assert any(error["loc"][-1] == field for error in response.json()["detail"])


def assert_estimate_response_matches_dto(response, dto) -> None:
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == dto.llm_provider
    assert body["llm_model"] == dto.llm_model
    assert body["estimation"] == dto.response
    assert body["metadata"]["token_metadata"]["num_tokens_input"] == dto.num_tokens_input
    assert body["metadata"]["cost_metadata"]["total_token_cost"] == dto.total_token_cost


def assert_service_error_response(response) -> None:
    assert response.status_code == 500
    assert response.json() == {"detail": "An error occurred while processing the estimation"}


def service_exception() -> EstimateServiceException:
    return EstimateServiceException("service failed")


def parse_ndjson_response(response) -> list[dict]:
    return [json.loads(line) for line in response.text.splitlines()]
