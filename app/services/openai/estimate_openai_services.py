import logging
from collections.abc import Iterator
from typing import Any

from openai import OpenAI

from app.config import LLMProvider, get_settings
from app.constants.estimate_constants import OPENAI_MODEL_DEFAULT
from app.core.cost.utils import OpenAICostUtil
from app.core.token.utils import OpenAITokenUtil
from app.dtos.estimate_dtos import EstimateResponseDTO, generate_openai_estimate_response_dto
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.prompts.builders.estimate_openai_prompt_builder import EstimateOpenAIPromptBuilder

logger = logging.getLogger(__name__)


class EstimateOpenAIService:
    def __init__(
        self,
        client: OpenAI | None = None,
        prompt_builder: EstimateOpenAIPromptBuilder | None = None,
        settings=None,
    ):
        self._client = client
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or EstimateOpenAIPromptBuilder()

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self._settings.OPENAI_API_KEY)
        return self._client

    def estimate_from_transcript(
        self,
        transcript: str,
        model: str = OPENAI_MODEL_DEFAULT,
    ) -> EstimateResponseDTO:
        logger.info("Estimating transcript with OpenAI model=%s", model)

        # Prepare prompts
        messages = self._prompt_builder.build_messages(transcript)

        # Count tokens before making the API call to have an estimate of the input tokens
        input_tokens = OpenAITokenUtil.count_tokens(messages, model)
        logger.debug("Estimated prompt tokens: %s", input_tokens)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as exc:
            logger.exception("Error while generating estimation with OpenAI")
            raise EstimateServiceException("An error occurred while generating the estimation") from exc

        if response.usage is None:
            raise EstimateServiceException("The LLM response did not include token usage metadata")

        response_content = response.choices[0].message.content
        if not response_content:
            raise EstimateServiceException("The LLM response content is empty")

        estimate_response_dto = generate_openai_estimate_response_dto(LLMProvider.OPENAI, model, response)

        logger.debug("Input tokens used: %s", response.usage.prompt_tokens)
        logger.debug("Output tokens used: %s", response.usage.completion_tokens)
        logger.debug("Total tokens used: %s", response.usage.total_tokens)

        return estimate_response_dto

    def stream_estimate_from_transcript(
        self,
        transcript: str,
        model: str = OPENAI_MODEL_DEFAULT,
    ) -> Iterator[dict[str, Any]]:
        logger.info("Streaming transcript estimation with OpenAI model=%s", model)

        messages = self._prompt_builder.build_messages(transcript)

        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                stream=True,
                stream_options={"include_usage": True},
            )
        except Exception as exc:
            logger.exception("Error while starting streaming estimation with OpenAI")
            raise EstimateServiceException("An error occurred while generating the estimation") from exc

        usage = None
        response_parts: list[str] = []

        try:
            for chunk in stream:
                if chunk.usage is not None:
                    usage = chunk.usage

                for choice in chunk.choices:
                    content = choice.delta.content
                    if content:
                        response_parts.append(content)
                        yield {"type": "delta", "content": content}
        except Exception as exc:
            logger.exception("Error while streaming estimation with OpenAI")
            raise EstimateServiceException("An error occurred while generating the estimation") from exc

        response_content = "".join(response_parts).strip()
        if not response_content:
            raise EstimateServiceException("The LLM response content is empty")

        if usage is None:
            raise EstimateServiceException("The LLM response did not include token usage metadata")

        token_costs = OpenAICostUtil.calculate_cost(
            model=model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
        )

        yield {
            "type": "metadata",
            "provider": LLMProvider.OPENAI.value,
            "llm_model": model,
            "num_tokens_input": usage.prompt_tokens,
            "num_tokens_response": usage.completion_tokens,
            "num_tokens_total": usage.total_tokens,
            "input_token_cost": token_costs.input_token_cost,
            "output_token_cost": token_costs.output_token_cost,
            "total_token_cost": token_costs.total_token_cost,
        }
