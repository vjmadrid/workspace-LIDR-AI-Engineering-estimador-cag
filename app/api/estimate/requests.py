from pydantic import BaseModel, Field

class EstimateRequest(BaseModel):
    transcription: str = Field(..., description="Texto de la transcripción de la reunión")
