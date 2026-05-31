# Sesion 04
import structlog
from collections.abc import Callable
from typing import Any

from app.config import LLMProvider, get_settings
from app.constants.estimate_constants import LLMLITE_MODEL_DEFAULT
from app.core.cost.dtos import TokenCostResponseDTO
from app.core.cost.utils import LLMWrapperCostUtil
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.prompts.builders.estimate_prompt_builder import EstimatePromptBuilder

# Logging Configuration
log = structlog.get_logger()

class EstimateLLMLiteService:
    def __init__(
        self,
        completion: Callable[..., Any] | None = None,
        prompt_builder: EstimatePromptBuilder | None = None,
        settings=None,
    ):
        self._completion = completion
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or EstimatePromptBuilder()

    @property
    def completion(self) -> Callable[..., Any]:
        if self._completion is None:
            # Import LiteLLM lazily so tests can inject a fake completion function without loading the provider client.
            from litellm import completion

            self._completion = completion
        return self._completion

    def estimate_from_transcript(
        self,
        transcript: str,
        model: str | None = None,
    ) -> EstimateResponseDTO:
        model = model or getattr(self._settings, "LLMLITE_MODEL", LLMLITE_MODEL_DEFAULT)
        log.info("Estimating transcript with LiteLLM model=%s", model)

        messages = self._prompt_builder.build_messages(transcript)

        try:
            response = self.completion(
                model=model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as exc:
            log.exception("Error while generating estimation with LiteLLM")
            raise EstimateServiceException("An error occurred while generating the estimation") from exc

        usage = self._get_usage(response)
        if usage is None:
            # Some LiteLLM providers may omit usage metadata; keep the estimation and report zero token/cost data.
            log.warning("LiteLLM response did not include token usage metadata for model=%s", model)

        response_content = self._get_response_content(response)
        if not response_content:
            raise EstimateServiceException("The LLM response content is empty")

        prompt_tokens = self._get_value(usage, "prompt_tokens", 0)
        completion_tokens = self._get_value(usage, "completion_tokens", 0)
        total_tokens = self._get_value(
            usage,
            "total_tokens",
            prompt_tokens + completion_tokens,
        )

        log.debug("Input tokens used: %s", prompt_tokens)
        log.debug("Output tokens used: %s", completion_tokens)
        log.debug("Total tokens used: %s", total_tokens)

        token_costs = self._calculate_cost(
            model=model,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
        )

        return EstimateResponseDTO(
            llm_provider=LLMProvider.LLMLITE,
            llm_model=model,
            response=response_content.strip(),
            num_tokens_input=prompt_tokens,
            num_tokens_response=completion_tokens,
            num_tokens_total=total_tokens,
            input_token_cost=token_costs.input_token_cost,
            output_token_cost=token_costs.output_token_cost,
            total_token_cost=token_costs.total_token_cost,
        )

    @staticmethod
    def _get_usage(response):
        return EstimateLLMLiteService._get_value(response, "usage")

    @staticmethod
    def _get_response_content(response) -> str | None:
        choices = EstimateLLMLiteService._get_value(response, "choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        message = EstimateLLMLiteService._get_value(first_choice, "message")
        if message is None:
            return None

        return EstimateLLMLiteService._get_value(message, "content")

    @staticmethod
    def _get_value(source, key: str, default=None):
        # LiteLLM responses and tests may use either dicts or attribute-based objects.
        if isinstance(source, dict):
            return source.get(key, default)
        return getattr(source, key, default)

    @staticmethod
    def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> TokenCostResponseDTO:
        # Use the provider-aware cost utility because LiteLLM can route to OpenAI, Anthropic, or custom models.
        return LLMWrapperCostUtil.calculate_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
