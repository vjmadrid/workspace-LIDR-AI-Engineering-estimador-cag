from pydantic import BaseModel, Field

class EstimationResponse(BaseModel):
    estimation: str = Field(..., description="Estimación generada por el modelo")