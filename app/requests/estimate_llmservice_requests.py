from typing import Literal

from pydantic import BaseModel, Field

PreprocessingMode = Literal["none", "inline_cleaning", "two_phase"]
ExampleFormat = Literal["markdown", "json", "narrative"]


class EstimationLLMServiceRequest(BaseModel):
    """Incoming request containing a meeting transcription to estimate."""

    transcription: str = Field(..., min_length=50, description="Meeting transcription text")

    preprocessing: PreprocessingMode = Field(
        default="none",
        description="Input preprocessing strategy: none | inline_cleaning | two_phase",
    )
    example_format: ExampleFormat = Field(
        default="markdown",
        description="Format used to render the CAG examples in the system prompt",
    )
    num_examples: int = Field(
        default=3,
        ge=0,
        le=5,
        description="Number of canonical examples to inject (0..N where N=len(CANONICAL_EXAMPLES))",
    )
    use_examples: bool = Field(
        default=True,
        description="Toggle the CAG examples block on/off (overrides num_examples when False)",
    )
    model: str | None = Field(
        default=None,
        description="Override the default LLM_MODEL for this request",
    )
    max_tokens: int = Field(
        default=4000,
        gt=0,
        le=16000,
        description="Maximum output tokens for the estimation call",
    )
    thinking_budget: int | None = Field(
        default=None,
        ge=0,
        le=16000,
        description="Extended thinking budget (Anthropic only). Ignored for OpenAI.",
    )
    evaluate: bool = Field(
        default=True,
        description="Run the structural evaluation on the generated estimation",
    )

class StreamEstimationLLMServiceRequest(BaseModel):
    """Streaming endpoint request — only the transcription, knobs are not exposed."""

    transcription: str = Field(..., min_length=50, description="Meeting transcription text")
    model: str | None = Field(default=None, description="Override the default model")
    max_tokens: int = Field(default=4000, gt=0, le=16000)