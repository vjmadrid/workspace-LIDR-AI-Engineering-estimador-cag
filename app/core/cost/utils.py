from app.core.cost.dtos import TokenCostResponseDTO
from app.core.openai.constants import DEFAULT_OPENAI_MODEL


class OpenAICostUtil:
    # OpenAI (USD per 1M tokens)
    PRICING = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o-mini-2024-07-18": {"input": 0.15, "output": 0.60},
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
