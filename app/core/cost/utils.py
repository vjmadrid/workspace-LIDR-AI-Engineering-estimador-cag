from app.core.openai.constants import DEFAULT_OPENAI_MODEL, DEFAULT_ANTHROPIC_MODEL
from app.core.cost.dtos import TokenCostResponseDTO


class OpenAICostUtil:
    # OpenAI (USD per 1M tokens)
    PRICING = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o-mini-2024-07-18": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
        "gpt-5.4": {"input": 2.50, "output": 15.00},
        "gpt-5.4-nano": {"input": 0.20, "output": 1.25},
        "gpt-5-mini": {"input": 0.25, "output": 2.00},
        "gpt-5-nano": {"input": 0.05, "output": 0.40},
    }

    @staticmethod
    def calculate_cost(model=DEFAULT_OPENAI_MODEL, input_tokens=0, output_tokens=0):
        if model not in OpenAICostUtil.PRICING:
            raise ValueError(f"Model '{model}' not found in pricing table")

        # Get pricing for the specified model
        pricing = OpenAICostUtil.PRICING[model]

        # Calculate cost based on token counts and pricing
        input_token_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_token_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_token_cost = input_token_cost + output_token_cost

        # Build response DTO
        response_dto = TokenCostResponseDTO(
            llm_model=model,
            input_token_cost=input_token_cost,
            output_token_cost=output_token_cost,
            total_token_cost=total_token_cost,
        )

        return response_dto


class AnthropicCostUtil:
    # Anthropic (USD per 1M tokens)
    PRICING = {
        "claude-3-5-haiku-latest": {"input": 0.80, "output": 4.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "claude-sonnet-4-0": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
        "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
        "claude-sonnet-4-6-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-7-sonnet-latest": {"input": 3.00, "output": 15.00},
        "claude-3-7-sonnet-20250219": {"input": 3.00, "output": 15.00},
        "claude-opus-4-1": {"input": 15.00, "output": 75.00},
        "claude-opus-4-1-20250805": {"input": 15.00, "output": 75.00},
        "claude-opus-4-0": {"input": 15.00, "output": 75.00},
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    }

    @staticmethod
    def calculate_cost(model=DEFAULT_ANTHROPIC_MODEL, input_tokens=0, output_tokens=0):
        if model not in AnthropicCostUtil.PRICING:
            raise ValueError(f"Model '{model}' not found in pricing table")

        # Get pricing for the specified model
        pricing = AnthropicCostUtil.PRICING[model]

        # Calculate cost based on token counts and pricing
        input_token_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_token_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_token_cost = input_token_cost + output_token_cost

        # Build response DTO
        response_dto = TokenCostResponseDTO(
            llm_model=model,
            input_token_cost=input_token_cost,
            output_token_cost=output_token_cost,
            total_token_cost=total_token_cost,
        )

        return response_dto


def normalise_litellm_model_name(model: str) -> str:
    """Strip provider prefixes like ``anthropic/`` that LiteLLM may emit."""
    return model.split("/", 1)[1] if "/" in model else model


def provider_from_litellm_model(model: str) -> str:
    name = normalise_litellm_model_name(model).lower()
    if name.startswith("claude"):
        return "anthropic"
    if name.startswith("gpt") or name.startswith("o1") or name.startswith("o3"):
        return "openai"
    return "unknown"


class LLMWrapperCostUtil:
    """Cost utility for LiteLLM wrapper responses across supported providers."""

    @staticmethod
    def calculate_cost(model: str, input_tokens=0, output_tokens=0):
        normalised_model = normalise_litellm_model_name(model)
        provider = provider_from_litellm_model(normalised_model)

        if provider == "openai":
            return OpenAICostUtil.calculate_cost(
                model=normalised_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        if provider == "anthropic":
            return AnthropicCostUtil.calculate_cost(
                model=normalised_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        return TokenCostResponseDTO(
            llm_model=normalised_model,
            input_token_cost=0,
            output_token_cost=0,
            total_token_cost=0,
        )

    @staticmethod
    def calculate_total_cost(model: str, input_tokens=0, output_tokens=0) -> float:
        token_costs = LLMWrapperCostUtil.calculate_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        return round(token_costs.total_token_cost, 6)
