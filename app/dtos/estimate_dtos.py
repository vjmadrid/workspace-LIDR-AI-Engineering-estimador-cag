from asyncio.log import logger

from pydantic import BaseModel

from app.core.cost.utils import OpenAICostUtil


# =====================
# Responses (BaseModel)
# =====================


class EstimateResponseDTO(BaseModel):
    llm_provider: str
    llm_model: str
    response: str
    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int
    input_token_cost: float
    output_token_cost: float
    total_token_cost: float


# =====================
# Generator functions
# =====================


def generate_openai_estimate_response_dto(provider, model, response):
    logger.debug("Input tokens used: %s", response.usage.prompt_tokens)
    logger.debug("Output tokens used: %s", response.usage.completion_tokens)
    logger.debug("Total tokens used: %s", response.usage.total_tokens)

    token_costs = OpenAICostUtil.calculate_cost(
        model=model,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
    )

    return EstimateResponseDTO(
        llm_provider=provider,
        llm_model=model,
        response=response.choices[0].message.content.strip(),
        num_tokens_input=response.usage.prompt_tokens,
        num_tokens_response=response.usage.completion_tokens,
        num_tokens_total=response.usage.total_tokens,
        input_token_cost=token_costs.input_token_cost,
        output_token_cost=token_costs.output_token_cost,
        total_token_cost=token_costs.total_token_cost,
    )
