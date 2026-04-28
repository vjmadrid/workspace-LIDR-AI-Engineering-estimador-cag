from fastapi import APIRouter, HTTPException

from app.schemas.estimate_request import EstimationRequest
from app.schemas.estimate_response import EstimationResponse

from app.services.llm_service import estimate_from_transcript

router = APIRouter(prefix="/api/v1", tags=["estimations"])

@router.post("/estimate", response_model=EstimationResponse)
def estimate_endpoint(payload: EstimationRequest):
    if not payload.transcription.strip():
        raise HTTPException(status_code=400, detail="El campo 'transcription' no puede estar vacío.")
    estimation = estimate_from_transcript(payload.transcription)
    return EstimationResponse(estimation=estimation)
