import logging
from fastapi import APIRouter, HTTPException

from app.schemas.estimate_request import EstimationRequest
from app.schemas.estimate_response import EstimationResponse

from app.api.estimate.services import estimate_from_transcript

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["estimations"])

@router.post("/estimate", response_model=EstimationResponse)
def estimate_endpoint(payload: EstimationRequest):
    logger.info("Estimate endpoint called")
    if not payload.transcription.strip():
        raise HTTPException(status_code=400, detail="El campo 'transcription' no puede estar vacío.")
    estimation = estimate_from_transcript(payload.transcription)
    logger.info("Estimation result: %s", estimation)
    return EstimationResponse(estimation=estimation)
