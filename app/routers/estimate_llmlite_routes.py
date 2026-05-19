import logging

from fastapi import APIRouter, HTTPException

from app.constants.estimate_constants import ESTIMATE_LLMLITE_ENDPOINT
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.requests.estimate_requests import EstimateRequest
from app.responses.estimate_responses import EstimateResponse, generate_estimate_response
from app.services.llmlite.estimate_llmlite_services import EstimateLLMLiteService

# Logging Configuration
logger = logging.getLogger(__name__)

# Services Configuracion
estimateLLMLiteService = EstimateLLMLiteService()

router = APIRouter(prefix="/api/v1", tags=["estimations"])


@router.post(ESTIMATE_LLMLITE_ENDPOINT, response_model=EstimateResponse)
async def estimate_llmlite_endpoint(request: EstimateRequest):
    logger.info("Estimate LLM Lite endpoint called")

    try:
        response = estimateLLMLiteService.estimate_from_transcript(request.transcription)
    except EstimateServiceException as e:
        logger.error("Error occurred while estimating: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing the estimation") from e

    logger.info("Estimation result: %s", response)

    # Build response
    return generate_estimate_response(response)
