from __future__ import annotations

from fastapi.testclient import TestClient

from app.constants.estimate_constants import ESTIMATE_LLMWRAPPER_ADVANCED_ENDPOINT
from app.dependencies import get_estimation_service
from app.guardrails.input import InputGuardrailViolation
from app.main import app
from tests.units.app.requests.estimate_request_factory import (
    EstimateLLMWrapperAdvancedRequestFactory,
)
from tests.units.app.responses.estimate_response_factory import (
    EstimateLLMWrapperAdvancedResponseFactory,
)

ENDPOINT = f"/api/v1{ESTIMATE_LLMWRAPPER_ADVANCED_ENDPOINT}"


class FakeAdvancedEstimateService:
    def __init__(self, *, response=None, exception: Exception | None = None) -> None:
        self.response = response or EstimateLLMWrapperAdvancedResponseFactory.build()
        self.exception = exception
        self.requests = []

    def estimate(self, request):
        self.requests.append(request)
        if self.exception:
            raise self.exception
        return self.response


def override_estimation_service(service: FakeAdvancedEstimateService):
    app.dependency_overrides[get_estimation_service] = lambda: service
    return service


def clear_estimation_service_override() -> None:
    app.dependency_overrides.pop(get_estimation_service, None)


def valid_advanced_payload(**overrides) -> dict:
    return EstimateLLMWrapperAdvancedRequestFactory.build_payload(**overrides)


def post_estimation(client: TestClient, payload: dict | None = None):
    return client.post(ENDPOINT, json=payload or valid_advanced_payload())


def assert_validation_error_for_field(response, field: str) -> None:
    assert response.status_code == 422
    assert any(error["loc"][-1] == field for error in response.json()["detail"])


def test_valid_payload_returns_advanced_estimation_response(client: TestClient) -> None:
    service = override_estimation_service(FakeAdvancedEstimateService())
    try:
        response = post_estimation(client)
    finally:
        clear_estimation_service_override()

    assert response.status_code == 200
    assert response.json() == service.response.model_dump(mode="json")
    assert len(service.requests) == 1
    assert service.requests[0].description == EstimateLLMWrapperAdvancedRequestFactory.DEFAULT_DESCRIPTION


def test_missing_project_type_returns_422(client: TestClient) -> None:
    service = override_estimation_service(FakeAdvancedEstimateService())
    payload = {key: value for key, value in valid_advanced_payload().items() if key != "project_type"}
    try:
        response = post_estimation(client, payload)
    finally:
        clear_estimation_service_override()

    assert_validation_error_for_field(response, "project_type")
    assert service.requests == []


def test_invalid_enum_value_returns_422(client: TestClient) -> None:
    service = override_estimation_service(FakeAdvancedEstimateService())
    try:
        response = post_estimation(client, valid_advanced_payload(output_format="not_a_real_format"))
    finally:
        clear_estimation_service_override()

    assert_validation_error_for_field(response, "output_format")
    assert service.requests == []


def test_input_guardrail_violation_returns_400(client: TestClient) -> None:
    override_estimation_service(
        FakeAdvancedEstimateService(
            exception=InputGuardrailViolation(
                "Email address detected in description.",
                reason="pii",
            )
        )
    )
    try:
        response = post_estimation(client)
    finally:
        clear_estimation_service_override()

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "reason": "pii",
            "message": "Email address detected in description.",
        }
    }


def test_unexpected_service_exception_returns_502(client: TestClient) -> None:
    override_estimation_service(FakeAdvancedEstimateService(exception=RuntimeError("provider down")))
    try:
        response = post_estimation(client)
    finally:
        clear_estimation_service_override()

    assert response.status_code == 502
    assert response.json() == {"detail": "Upstream LLM call failed"}
