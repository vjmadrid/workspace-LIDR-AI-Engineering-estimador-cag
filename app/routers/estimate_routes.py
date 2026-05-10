import json
import logging

from fastapi import APIRouter, HTTPException

from app.constants.estimate_constants import (
    ESTIMATE_ENDPOINT
)
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.requests.estimate_requests import EstimateRequest
from app.responses.estimate_responses import EstimateResponse, generate_estimate_response
from app.services.estimate_services import EstimateService

# Logging Configuration
logger = logging.getLogger(__name__)

# Services Configuracion
estimateService = EstimateService()

router = APIRouter(prefix="/api/v1", tags=["estimations"])

@router.post(ESTIMATE_ENDPOINT, response_model=EstimateResponse)
async def estimate_endpoint(request: EstimateRequest):
    logger.info("Estimate endpoint called")

    try:
        response = estimateService.estimate_from_transcript(request.transcription)
    except EstimateServiceException as e:
        logger.error("Error occurred while estimating: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing the estimation") from e

    logger.info("Estimation result: %s", response)

    # Build response
    return generate_estimate_response(response)

