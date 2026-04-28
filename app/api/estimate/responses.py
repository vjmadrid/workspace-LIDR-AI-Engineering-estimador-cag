from pydantic import BaseModel, Field

from app.api.estimate.dtos import EstimateResponseDTO

# =====================
# Responses (BaseModel)
# =====================
class EstimateTokenMetadataResponse(BaseModel):
    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int
class EstimateCostMetadataResponse(BaseModel):
    input_token_cost: float
    output_token_cost: float
    total_token_cost: float
class EstimateMetadataResponse(BaseModel):
    token_metadata: EstimateTokenMetadataResponse | None = None
    cost_metadata: EstimateCostMetadataResponse | None = None
class EstimateResponse(BaseModel):
    provider: str
    llm_model: str
    estimation: str = Field(..., description="Estimación generada por el modelo")
    metadata: EstimateMetadataResponse | None = None

# =====================
# Generator functions
# =====================

def generate_estimate_response(estimate: EstimateResponseDTO):

    token_metadata=EstimateTokenMetadataResponse(
        num_tokens_input=estimate.num_tokens_input,
        num_tokens_response=estimate.num_tokens_response,
        num_tokens_total=estimate.num_tokens_total
    )

    cost_metadata = EstimateCostMetadataResponse(
        input_token_cost=estimate.input_token_cost,
        output_token_cost=estimate.output_token_cost,
        total_token_cost=estimate.total_token_cost
    )

    metadata = EstimateMetadataResponse(
        token_metadata=token_metadata,
        cost_metadata=cost_metadata
    )

    return EstimateResponse(
        provider=estimate.llm_provider,
        llm_model=estimate.llm_model,
        estimation=estimate.response,
        metadata=metadata
    )
