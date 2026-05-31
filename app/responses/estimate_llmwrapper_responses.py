# Sesion 04
from pydantic import BaseModel, Field

# =====================
# Responses (BaseModel)
# =====================

class EstimationLLMWrapperResponse(BaseModel):
    """Estimation rendered as free text, plus the prompt version that produced it."""

    text: str = Field(description="Estimation rendered by the LLM as free text.")
    prompt_version: str = Field(description="Identifier of the prompt template used.")
