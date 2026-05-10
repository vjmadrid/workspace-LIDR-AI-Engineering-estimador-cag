from pydantic import BaseModel, ConfigDict, Field

from app.dtos.estimate_dtos import EstimateResponseDTO


# =====================
# Responses (BaseModel)
# =====================

class EstimateTokenMetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int


class EstimateCostMetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_token_cost: float
    output_token_cost: float
    total_token_cost: float


class EstimateMetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token_metadata: EstimateTokenMetadataResponse | None = None
    cost_metadata: EstimateCostMetadataResponse | None = None


class EstimateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(..., description="LLM provider used")
    llm_model: str = Field(..., description="LLM model used")
    estimation: str = Field(..., description="Estimación generada por el modelo")
    metadata: EstimateMetadataResponse | None = None


# =====================
# Generator functions
# =====================

def generate_estimate_response(estimate: EstimateResponseDTO):

    token_metadata = EstimateTokenMetadataResponse(
        num_tokens_input=estimate.num_tokens_input,
        num_tokens_response=estimate.num_tokens_response,
        num_tokens_total=estimate.num_tokens_total,
    )

    cost_metadata = EstimateCostMetadataResponse(
        input_token_cost=estimate.input_token_cost,
        output_token_cost=estimate.output_token_cost,
        total_token_cost=estimate.total_token_cost,
    )

    metadata = EstimateMetadataResponse(
        token_metadata=token_metadata, cost_metadata=cost_metadata
    )

    return EstimateResponse(
        provider=estimate.llm_provider,
        llm_model=estimate.llm_model,
        estimation=estimate.response,
        metadata=metadata,
    )
