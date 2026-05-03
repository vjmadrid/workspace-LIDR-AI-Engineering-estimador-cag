from pydantic import BaseModel, ConfigDict, Field, field_validator


class EstimateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcription: str = Field(
        ...,
        min_length=1,
        description="Texto de la transcripción de la reunión",
    )

    @field_validator("transcription")
    @classmethod
    def normalize_transcription(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("The 'transcription' field must not be empty")
        return normalized_value
