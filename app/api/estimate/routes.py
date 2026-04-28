import logging
from fastapi import APIRouter, HTTPException

from app.api.estimate.constants import ESTIMATE_ENDPOINT
from app.api.estimate.requests import EstimateRequest
from app.api.estimate.responses import EstimateResponse, generate_estimate_response
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

    response = estimateService.estimate_from_transcript(payload.transcription)
    logger.info("Estimation result: %s", response)

    # Build response
    return generate_estimate_response(response)
