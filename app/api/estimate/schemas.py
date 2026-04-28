from pydantic import BaseModel

class EstimateResponse(BaseModel):
    response: str
    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int