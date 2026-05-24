import structlog

from app.config import LLMProvider, get_settings
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.anthropic.estimate_anthropic_services import EstimateAnthropicService
from app.services.llmlite.estimate_llmlite_services import EstimateLLMLiteService
from app.services.openai.estimate_openai_services import EstimateOpenAIService

# Logging Configuration
log = structlog.get_logger()


class EstimateService:
    def __init__(
        self,
        settings=None,
        openai_service: EstimateOpenAIService | None = None,
        anthropic_service: EstimateAnthropicService | None = None,
        llmlite_service: EstimateLLMLiteService | None = None,
    ):
        self._settings = settings or get_settings()
        self._openai_service = openai_service or EstimateOpenAIService(settings=self._settings)
        self._anthropic_service = anthropic_service or EstimateAnthropicService(settings=self._settings)
        self._llmlite_service = llmlite_service or EstimateLLMLiteService(settings=self._settings)

    def estimate_from_transcript(self, transcript: str) -> EstimateResponseDTO:
        provider = self._settings.LLM_PROVIDER
        log.info("generating_estimation", provider=provider.value)

        try:
            if provider == LLMProvider.OPENAI:
                return self._openai_service.estimate_from_transcript(transcript)
            if provider == LLMProvider.ANTHROPIC:
                return self._anthropic_service.estimate_from_transcript(transcript)
            if provider == LLMProvider.LLMLITE:
                return self._llmlite_service.estimate_from_transcript(transcript)

            raise EstimateServiceException(f"Unsupported LLM provider: {provider}")
        except EstimateServiceException:
            raise
        except Exception as exc:
            log.error("llm_call_failed", provider=provider.value, error=str(exc))
            raise EstimateServiceException(f"LLM call failed: {exc}") from exc
