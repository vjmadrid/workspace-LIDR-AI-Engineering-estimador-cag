from app.dtos.estimate_dtos import EstimateResponseDTO
from app.responses.estimate_llmwrapper_advanced_responses import (
    EstimationLLMWrapperAdvancedResponse,
    EstimationResult,
    Phase,
)
from app.responses.estimate_llmwrapper_responses import EstimationLLMWrapperResponse
from app.responses.estimate_responses import EstimateResponse


class EstimateResponseFactory:
    DEFAULT_PROVIDER = "openai"
    DEFAULT_LLM_MODEL = "gpt-4o-mini"
    DEFAULT_ESTIMATION = "La funcionalidad se estima en 8 horas."
    DEFAULT_NUM_TOKENS_INPUT = 120
    DEFAULT_NUM_TOKENS_RESPONSE = 80
    DEFAULT_NUM_TOKENS_TOTAL = 200
    DEFAULT_INPUT_TOKEN_COST = 0.000018
    DEFAULT_OUTPUT_TOKEN_COST = 0.000048
    DEFAULT_TOTAL_TOKEN_COST = 0.000066

    @classmethod
    def build(cls, **overrides) -> EstimateResponse:
        return EstimateResponse(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "provider": cls.DEFAULT_PROVIDER,
            "llm_model": cls.DEFAULT_LLM_MODEL,
            "estimation": cls.DEFAULT_ESTIMATION,
            "metadata": {
                "token_metadata": {
                    "num_tokens_input": cls.DEFAULT_NUM_TOKENS_INPUT,
                    "num_tokens_response": cls.DEFAULT_NUM_TOKENS_RESPONSE,
                    "num_tokens_total": cls.DEFAULT_NUM_TOKENS_TOTAL,
                },
                "cost_metadata": {
                    "input_token_cost": cls.DEFAULT_INPUT_TOKEN_COST,
                    "output_token_cost": cls.DEFAULT_OUTPUT_TOKEN_COST,
                    "total_token_cost": cls.DEFAULT_TOTAL_TOKEN_COST,
                },
            },
        }
        payload.update(overrides)
        return payload


class EstimateResponseDTOFactory:
    @classmethod
    def build(cls, **overrides) -> EstimateResponseDTO:
        return EstimateResponseDTO(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "llm_provider": EstimateResponseFactory.DEFAULT_PROVIDER,
            "llm_model": EstimateResponseFactory.DEFAULT_LLM_MODEL,
            "response": EstimateResponseFactory.DEFAULT_ESTIMATION,
            "num_tokens_input": EstimateResponseFactory.DEFAULT_NUM_TOKENS_INPUT,
            "num_tokens_response": EstimateResponseFactory.DEFAULT_NUM_TOKENS_RESPONSE,
            "num_tokens_total": EstimateResponseFactory.DEFAULT_NUM_TOKENS_TOTAL,
            "input_token_cost": EstimateResponseFactory.DEFAULT_INPUT_TOKEN_COST,
            "output_token_cost": EstimateResponseFactory.DEFAULT_OUTPUT_TOKEN_COST,
            "total_token_cost": EstimateResponseFactory.DEFAULT_TOTAL_TOKEN_COST,
        }
        payload.update(overrides)
        return payload


class EstimateLLMWrapperResponseFactory:
    DEFAULT_TEXT = "La funcionalidad se estima en 8 horas."
    DEFAULT_PROMPT_VERSION = "v1"

    @classmethod
    def build(cls, **overrides) -> EstimationLLMWrapperResponse:
        return EstimationLLMWrapperResponse(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "text": cls.DEFAULT_TEXT,
            "prompt_version": cls.DEFAULT_PROMPT_VERSION,
        }
        payload.update(overrides)
        return payload


class PhaseFactory:
    DEFAULT_NAME = "Discovery"
    DEFAULT_DURATION_WEEKS = 2
    DEFAULT_COST_EUR = 4000
    DEFAULT_SUMMARY = "Product discovery, scope refinement, and technical planning."

    @classmethod
    def build(cls, **overrides) -> Phase:
        return Phase(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "name": cls.DEFAULT_NAME,
            "duration_weeks": cls.DEFAULT_DURATION_WEEKS,
            "cost_eur": cls.DEFAULT_COST_EUR,
            "summary": cls.DEFAULT_SUMMARY,
        }
        payload.update(overrides)
        return payload


class EstimationResultFactory:
    DEFAULT_SUMMARY = "The project can be delivered in phases with a moderate implementation risk."
    DEFAULT_CONFIDENCE_PCT = 80
    DEFAULT_TOTAL_DURATION_WEEKS = 2
    DEFAULT_TOTAL_COST_EUR = PhaseFactory.DEFAULT_COST_EUR

    @classmethod
    def build(cls, **overrides) -> EstimationResult:
        return EstimationResult(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "summary": cls.DEFAULT_SUMMARY,
            "confidence_pct": cls.DEFAULT_CONFIDENCE_PCT,
            "phases": [PhaseFactory.build_payload()],
            "total_duration_weeks": cls.DEFAULT_TOTAL_DURATION_WEEKS,
            "total_cost_eur": cls.DEFAULT_TOTAL_COST_EUR,
        }
        payload.update(overrides)
        return payload


class EstimateLLMWrapperAdvancedResponseFactory:
    DEFAULT_PROMPT_VERSION = "v1"
    DEFAULT_CACHED = False

    @classmethod
    def build(cls, **overrides) -> EstimationLLMWrapperAdvancedResponse:
        return EstimationLLMWrapperAdvancedResponse(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "result": EstimationResultFactory.build_payload(),
            "prompt_version": cls.DEFAULT_PROMPT_VERSION,
            "cached": cls.DEFAULT_CACHED,
        }
        payload.update(overrides)
        return payload
