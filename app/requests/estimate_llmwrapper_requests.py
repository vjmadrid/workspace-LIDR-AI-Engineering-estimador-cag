from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ProjectType(str, Enum):
    MOBILE_APP = "mobile_app"
    WEB_SAAS = "web_saas"
    INTERNAL_TOOL = "internal_tool"
    DATA_PIPELINE = "data_pipeline"


class DetailLevel(str, Enum):
    SUMMARY = "summary"
    MEDIUM = "medium"
    DETAILED = "detailed"


class OutputFormat(str, Enum):
    PHASES_TABLE = "phases_table"
    LINE_ITEMS = "line_items"
    NARRATIVE = "narrative"


class EstimateLLMWrapperRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(
        min_length=20,
        max_length=80000,
        description="Free-text description or transcription of the project to estimate.",
    )

    project_type: ProjectType = Field(description="Coarse-grained project category.")
    detail_level: DetailLevel = Field(description="How deep the estimation should go.")
    output_format: OutputFormat = Field(description="Shape of the rendered estimation.")


    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("The 'description' field must not be empty")
        return normalized_value
