from app.requests.estimate_llmwrapper_advanced_requests import (
    EstimateLLMWrapperAdvancedRequest,
)
from app.requests.estimate_llmwrapper_requests import (
    DetailLevel,
    EstimateLLMWrapperRequest,
    OutputFormat,
    ProjectType,
)
from app.requests.estimate_requests import EstimateRequest


class EstimateRequestFactory:
    DEFAULT_TRANSCRIPTION = "Reunion para estimar una funcionalidad de autenticacion con email y password."

    @classmethod
    def build(cls, **overrides) -> EstimateRequest:
        return EstimateRequest(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "transcription": cls.DEFAULT_TRANSCRIPTION,
        }
        payload.update(overrides)
        return payload


class EstimateLLMWrapperRequestFactory:
    DEFAULT_DESCRIPTION = (
        "Reunion para estimar una aplicacion web SaaS con autenticacion, usuarios, "
        "roles, permisos y panel de administracion."
    )

    @classmethod
    def build(cls, **overrides) -> EstimateLLMWrapperRequest:
        return EstimateLLMWrapperRequest(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "description": cls.DEFAULT_DESCRIPTION,
            "project_type": ProjectType.WEB_SAAS,
            "detail_level": DetailLevel.MEDIUM,
            "output_format": OutputFormat.PHASES_TABLE,
        }
        payload.update(overrides)
        return payload


class EstimateLLMWrapperAdvancedRequestFactory:
    DEFAULT_DESCRIPTION = EstimateLLMWrapperRequestFactory.DEFAULT_DESCRIPTION

    @classmethod
    def build(cls, **overrides) -> EstimateLLMWrapperAdvancedRequest:
        return EstimateLLMWrapperAdvancedRequest(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = EstimateLLMWrapperRequestFactory.build_payload()
        payload.update(overrides)
        return payload
