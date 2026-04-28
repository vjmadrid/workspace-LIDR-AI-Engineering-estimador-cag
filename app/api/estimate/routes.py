import logging
from fastapi import APIRouter, HTTPException

from app.api.estimate.constants import ESTIMATE_ENDPOINT
from app.api.estimate.requests import EstimateRequest
from app.api.estimate.responses import EstimateResponse, EstimateMetadata
from app.api.estimate.services import EstimateService

# Logging Configuration
logger = logging.getLogger(__name__)

# Services Configuracion
estimateService = EstimateService()


router = APIRouter(prefix="/api/v1", tags=["estimations"])

@router.post(ESTIMATE_ENDPOINT, response_model=EstimateResponse)
async def estimate_endpoint(payload: EstimateRequest) :
    logger.info("Estimate endpoint called")

    if not payload.transcription.strip():
        raise HTTPException(status_code=400, detail="The 'transcription' field must not be empty")

    estimation = estimateService.estimate_from_transcript(payload.transcription)
    logger.info("Estimation result: %s", estimation)

    # Build response

    metadata = EstimateMetadata(
        llm_model=estimation.llm_model,
        num_tokens_input=estimation.num_tokens_input,
        num_tokens_response=estimation.num_tokens_response,
        num_tokens_total=estimation.num_tokens_total
    )

    return EstimateResponse(
        estimation=estimation.response,
        metadata=metadata
    )