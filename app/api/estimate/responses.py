from pydantic import BaseModel, Field

class EstimateMetadata(BaseModel):
    llm_model: str
    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int

class EstimateResponse(BaseModel):
    estimation: str = Field(..., description="Estimación generada por el modelo")
    metadata: EstimateMetadata | None = None