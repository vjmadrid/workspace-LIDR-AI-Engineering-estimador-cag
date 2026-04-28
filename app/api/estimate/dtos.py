from pydantic import BaseModel

class EstimateResponseDTO(BaseModel):
    response: str
    llm_model: str
    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int
    input_token_cost: float
    output_token_cost: float
    total_token_cost: float
