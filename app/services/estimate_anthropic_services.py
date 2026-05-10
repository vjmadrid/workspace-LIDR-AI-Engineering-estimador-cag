import logging

from anthropic import Anthropic

from app.config import LLMProvider, get_settings
from app.constants.estimate_constants import ANTHROPIC_MODEL_DEFAULT, ANTHROPIC_MAX_TOKENS_DEFAULT
from app.core.cost.utils import AnthropicCostUtil
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.prompts.builders.estimate_prompt_builder import EstimatePromptBuilder

logger = logging.getLogger(__name__)

class EstimateAnthropicService:
    def __init__(
        self,
        client: Anthropic | None = None,
        prompt_builder: EstimatePromptBuilder | None = None,
        settings=None,
    ):
        self._client = client
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or EstimatePromptBuilder()

    @property
    def client(self) -> Anthropic:
        if self._client is None:
            self._client = Anthropic(api_key=self._settings.ANTHROPIC_API_KEY)
        return self._client

    def estimate_from_transcript(
        self,
        transcript: str,
        model: str = ANTHROPIC_MODEL_DEFAULT,
        max_tokens: int = ANTHROPIC_MAX_TOKENS_DEFAULT,
    ) -> EstimateResponseDTO:
        logger.info("Estimating transcript with Anthropic model=%s", model)

        # Prepare prompts
        messages = self._prompt_builder.build_messages(transcript)
        system_prompt, anthropic_messages = self._to_anthropic_messages(messages)


        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=anthropic_messages,
                temperature=0.2,
            )
        except Exception as exc:
            logger.exception("Error while generating estimation with Anthropic")
            raise EstimateServiceException(
                "An error occurred while generating the estimation"
            ) from exc

        if response.usage is None:
            raise EstimateServiceException(
                "The LLM response did not include token usage metadata"
            )

        response_content = self._extract_text_response(response.content)
        if not response_content:
            raise EstimateServiceException("The LLM response content is empty")

        logger.debug("Input tokens used: %s", response.usage.input_tokens)
        logger.debug("Output tokens used: %s", response.usage.output_tokens)
        logger.debug(
            "Total tokens used: %s",
            response.usage.input_tokens + response.usage.output_tokens,
        )

        token_costs = AnthropicCostUtil.calculate_cost(
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        return EstimateResponseDTO(
            llm_provider=LLMProvider.ANTHROPIC,
            llm_model=model,
            response=response_content,
            num_tokens_input=response.usage.input_tokens,
            num_tokens_response=response.usage.output_tokens,
            num_tokens_total=response.usage.input_tokens + response.usage.output_tokens,
            input_token_cost=token_costs.input_token_cost,
            output_token_cost=token_costs.output_token_cost,
            total_token_cost=token_costs.total_token_cost,
        )

    @staticmethod
    def _to_anthropic_messages(
        messages: list[dict[str, str]],
    ) -> tuple[str | None, list[dict[str, str]]]:
        system_prompt: str | None = None
        anthropic_messages: list[dict[str, str]] = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                system_prompt = content
                continue

            if role not in {"user", "assistant"}:
                raise EstimateServiceException(f"Unsupported message role for Anthropic: {role}")

            anthropic_messages.append({"role": role, "content": content})

        if not anthropic_messages:
            raise EstimateServiceException("Anthropic messages cannot be empty")

        return system_prompt, anthropic_messages

    @staticmethod
    def _extract_text_response(content_blocks) -> str:
        texts: list[str] = []

        for block in content_blocks:
            if getattr(block, "type", None) == "text":
                text = getattr(block, "text", "")
                if text:
                    texts.append(text)

        return "\n".join(texts).strip()
