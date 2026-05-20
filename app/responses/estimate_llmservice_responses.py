from typing import Literal

from pydantic import BaseModel, Field

PreprocessingMode = Literal["none", "inline_cleaning", "two_phase"]
ExampleFormat = Literal["markdown", "json", "narrative"]

class TokenUsage(BaseModel):
    """Token consumption details from the LLM call(s)."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    preprocessing_input_tokens: int = 0
    preprocessing_output_tokens: int = 0


class StructureCheck(BaseModel):
    """Level-1 structural evaluation of the generated estimation."""

    has_title: bool
    has_breakdown_table: bool
    has_totals_section: bool
    has_team_section: bool
    has_duration_section: bool
    declared_total_hours: int | None
    sum_row_hours: int | None
    hours_match: bool | None
    declared_total_cost: float | None
    sum_row_cost: float | None
    cost_match: bool | None
    finish_reason_ok: bool
    score: float
    issues: list[str]


class EstimationLLMServiceResponse(BaseModel):
    """Response containing the generated estimation and metadata."""

    estimation: str = Field(..., description="Generated software estimation in markdown")
    model: str = Field(..., description="LLM model used")
    provider: str = Field(..., description="LLM provider used")
    usage: TokenUsage
    finish_reason: str = Field(..., description="Stop reason reported by the provider")
    preprocessing: PreprocessingMode = "none"
    extracted_requirements: str | None = Field(
        default=None,
        description="Phase-1 output when preprocessing='two_phase'; null otherwise",
    )
    latency_ms: int = Field(..., description="Server-side total latency in milliseconds")
    validation: StructureCheck | None = None

    # --- Session 3 — wrapper metadata (additive, defaults preserve Session 2 tests) ---
    cache_hit: bool = Field(default=False, description="True when the response came from Redis")
    cost_usd: float = Field(default=0.0, description="Estimated USD cost based on token usage")


