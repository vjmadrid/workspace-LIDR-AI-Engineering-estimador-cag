import json
import structlog

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.constants.estimate_constants import (
    ESTIMATE_ANTHROPIC_ENDPOINT,
    ESTIMATE_ANTHROPIC_STREAM_ENDPOINT,
)
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.requests.estimate_requests import EstimateRequest
from app.responses.estimate_responses import EstimateResponse, generate_estimate_response
from app.services.anthropic.estimate_anthropic_services import EstimateAnthropicService

# Logging Configuration
log = structlog.get_logger()

# Services Configuracion
estimateAnthropicService = EstimateAnthropicService()

# Router Configuration
router = APIRouter(prefix="/api/v1", tags=["estimations"])


@router.post(ESTIMATE_ANTHROPIC_ENDPOINT, response_model=EstimateResponse)
async def estimate_anthropic_endpoint(request: EstimateRequest):
    log.info("Estimate Anthropic endpoint called")

    try:
        response = estimateAnthropicService.estimate_from_transcript(request.transcription)
    except EstimateServiceException as e:
        log.error("Error occurred while estimating: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing the estimation") from e

    log.info("Estimation result: %s", response)

    # Build response
    return generate_estimate_response(response)


@router.post(ESTIMATE_ANTHROPIC_STREAM_ENDPOINT)
async def estimate_anthropic_stream_endpoint(request: EstimateRequest):
    log.info("Estimate Anthropic stream endpoint called")

    def stream_response():
        try:
            for event in estimateAnthropicService.stream_estimate_from_transcript(request.transcription):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except EstimateServiceException as e:
            log.error("Error occurred while streaming estimation: %s", str(e))
            yield (
                json.dumps(
                    {
                        "type": "error",
                        "message": "An error occurred while processing the estimation",
                    }
                )
                + "\n"
            )

    return StreamingResponse(
        stream_response(),
        media_type="application/x-ndjson",
    )
