import logging

from anthropic import Anthropic

from app.config import LLMProvider, get_settings
from app.core.cost.dtos import TokenCostResponseDTO
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.estimate_prompt_builder import EstimatePromptBuilder

logger = logging.getLogger(__name__)

ANTHROPIC_MODEL_DEFAULT = "claude-3-5-haiku-latest"
ANTHROPIC_MAX_TOKENS_DEFAULT = 4096


class AnthropicCostUtil:
    # Anthropic (USD per 1M tokens)
    PRICING = {
        "claude-3-5-haiku-latest": {"input": 0.80, "output": 4.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "claude-sonnet-4-0": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-7-sonnet-latest": {"input": 3.00, "output": 15.00},
        "claude-3-7-sonnet-20250219": {"input": 3.00, "output": 15.00},
        "claude-opus-4-1": {"input": 15.00, "output": 75.00},
        "claude-opus-4-1-20250805": {"input": 15.00, "output": 75.00},
        "claude-opus-4-0": {"input": 15.00, "output": 75.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    }

    @staticmethod
    def calculate_cost(
        model: str = ANTHROPIC_MODEL_DEFAULT,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> TokenCostResponseDTO:
        if model not in AnthropicCostUtil.PRICING:
            raise ValueError(f"Model '{model}' not found in pricing table")

        pricing = AnthropicCostUtil.PRICING[model]
        input_token_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_token_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_token_cost = input_token_cost + output_token_cost

        return TokenCostResponseDTO(
            llm_model=model,
            input_token_cost=input_token_cost,
            output_token_cost=output_token_cost,
            total_token_cost=total_token_cost,
        )


class EstimateService:
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
        messages = self._prompt_builder.build_messages(transcript)
        system_prompt, anthropic_messages = self._to_anthropic_messages(messages)

        logger.info("Estimating transcript with Anthropic model=%s", model)

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
            raise EstimateServiceException("An error occurred while generating the estimation") from exc

        if response.usage is None:
            raise EstimateServiceException("The LLM response did not include token usage metadata")

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
