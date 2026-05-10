import logging
from collections.abc import Callable
from typing import Any

from app.config import LLMProvider, get_settings
from app.constants.estimate_constants import LLMLITE_MODEL_DEFAULT
from app.core.cost.dtos import TokenCostResponseDTO
from app.core.cost.utils import OpenAICostUtil
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.prompts.builders.estimate_openai_prompt_builder import EstimateOpenAIPromptBuilder

logger = logging.getLogger(__name__)


class EstimateLLMLiteService:
    def __init__(
        self,
        completion: Callable[..., Any] | None = None,
        prompt_builder: EstimateOpenAIPromptBuilder | None = None,
        settings=None,
    ):
        self._completion = completion
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or EstimateOpenAIPromptBuilder()

    @property
    def completion(self) -> Callable[..., Any]:
        if self._completion is None:
            from litellm import completion

            self._completion = completion
        return self._completion

    def estimate_from_transcript(
        self,
        transcript: str,
        model: str | None = None,
    ) -> EstimateResponseDTO:
        model = model or getattr(self._settings, "LLMLITE_MODEL", LLMLITE_MODEL_DEFAULT)
        logger.info("Estimating transcript with LiteLLM model=%s", model)

        messages = self._prompt_builder.build_messages(transcript)

        try:
            response = self.completion(
                model=model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as exc:
            logger.exception("Error while generating estimation with LiteLLM")
            raise EstimateServiceException("An error occurred while generating the estimation") from exc

        usage = self._get_usage(response)
        if usage is None:
            raise EstimateServiceException("The LLM response did not include token usage metadata")

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

        logger.debug("Input tokens used: %s", prompt_tokens)
        logger.debug("Output tokens used: %s", completion_tokens)
        logger.debug("Total tokens used: %s", total_tokens)

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
        if isinstance(source, dict):
            return source.get(key, default)
        return getattr(source, key, default)

    @staticmethod
    def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> TokenCostResponseDTO:
        try:
            return OpenAICostUtil.calculate_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        except ValueError:
            return TokenCostResponseDTO(
                llm_model=model,
                input_token_cost=0,
                output_token_cost=0,
                total_token_cost=0,
            )
