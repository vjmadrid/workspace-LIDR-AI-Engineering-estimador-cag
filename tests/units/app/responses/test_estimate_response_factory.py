import pytest
from pydantic import ValidationError

from app.responses.estimate_responses import EstimateResponse, generate_estimate_response
from tests.units.app.responses.estimate_response_factory import (
    EstimateResponseDTOFactory,
    EstimateResponseFactory,
)


def test_estimate_response_is_created_from_factory_defaults():
    response = EstimateResponseFactory.build()

    assert isinstance(response, EstimateResponse)
    assert response.provider == EstimateResponseFactory.DEFAULT_PROVIDER
    assert response.llm_model == EstimateResponseFactory.DEFAULT_LLM_MODEL
    assert response.estimation == EstimateResponseFactory.DEFAULT_ESTIMATION
    assert response.metadata is not None
    assert response.metadata.token_metadata is not None
    assert response.metadata.cost_metadata is not None
    assert response.metadata.token_metadata.num_tokens_input == EstimateResponseFactory.DEFAULT_NUM_TOKENS_INPUT
    assert response.metadata.cost_metadata.total_token_cost == EstimateResponseFactory.DEFAULT_TOTAL_TOKEN_COST


def test_estimate_response_is_created_with_custom_values():
    response = EstimateResponseFactory.build(
        provider="anthropic",
        llm_model="claude-sonnet-4",
        estimation="La funcionalidad se estima en 13 horas.",
    )

    assert response.provider == "anthropic"
    assert response.llm_model == "claude-sonnet-4"
    assert response.estimation == "La funcionalidad se estima en 13 horas."


def test_estimate_response_can_be_created_without_metadata():
    response = EstimateResponseFactory.build(metadata=None)

    assert response.metadata is None


def test_generate_estimate_response_maps_dto_to_response():
    dto = EstimateResponseDTOFactory.build()

    response = generate_estimate_response(dto)

    assert response.provider == dto.llm_provider
    assert response.llm_model == dto.llm_model
    assert response.estimation == dto.response
    assert response.metadata is not None
    assert response.metadata.token_metadata is not None
    assert response.metadata.cost_metadata is not None
    assert response.metadata.token_metadata.num_tokens_input == dto.num_tokens_input
    assert response.metadata.token_metadata.num_tokens_response == dto.num_tokens_response
    assert response.metadata.token_metadata.num_tokens_total == dto.num_tokens_total
    assert response.metadata.cost_metadata.input_token_cost == dto.input_token_cost
    assert response.metadata.cost_metadata.output_token_cost == dto.output_token_cost
    assert response.metadata.cost_metadata.total_token_cost == dto.total_token_cost
