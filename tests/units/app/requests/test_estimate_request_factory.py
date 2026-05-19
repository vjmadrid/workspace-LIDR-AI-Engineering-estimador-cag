from app.requests.estimate_llmwrapper_requests import (
    DetailLevel,
    EstimateLLMWrapperRequest,
    OutputFormat,
    ProjectType,
)
from app.requests.estimate_requests import EstimateRequest
from tests.units.app.requests.estimate_request_factory import (
    EstimateLLMWrapperRequestFactory,
    EstimateRequestFactory,
)


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


def test_estimate_llmwrapper_request_is_created_from_factory_defaults():
    request = EstimateLLMWrapperRequestFactory.build()

    assert isinstance(request, EstimateLLMWrapperRequest)
    assert request.description == EstimateLLMWrapperRequestFactory.DEFAULT_DESCRIPTION
    assert request.project_type == ProjectType.WEB_SAAS
    assert request.detail_level == DetailLevel.MEDIUM
    assert request.output_format == OutputFormat.PHASES_TABLE


def test_estimate_llmwrapper_request_normalizes_description_whitespace():
    description = "  Estimar una aplicacion interna para gestionar inventario y pedidos.  "

    request = EstimateLLMWrapperRequestFactory.build(description=description)

    assert request.description == description.strip()
