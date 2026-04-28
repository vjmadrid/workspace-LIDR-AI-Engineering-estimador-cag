from pydantic import BaseModel

class TokenCostResponseDTO(BaseModel):
    llm_model: str
    input_token_cost: float
    output_token_cost: float
    total_token_cost: float