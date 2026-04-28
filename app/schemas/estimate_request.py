from pydantic import BaseModel, Field

class EstimationRequest(BaseModel):
    transcription: str = Field(..., description="Texto de la transcripción de la reunión")
