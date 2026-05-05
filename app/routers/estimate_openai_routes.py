import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.constants.estimate_constants import (
    ESTIMATE_ANTHROPIC_ENDPOINT,
    ESTIMATE_OPENAI_ENDPOINT,
    ESTIMATE_OPENAI_STREAM_ENDPOINT,
)
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.requests.estimate_requests import EstimateRequest
from app.response.estimate_responses import EstimateResponse, generate_estimate_response
from app.services.estimate_anthropic_services import EstimateAnthropicService
from app.services.estimate_openai_services import EstimateOpenAIService

# Logging Configuration
logger = logging.getLogger(__name__)

# Services Configuracion
estimateOpenAIService = EstimateOpenAIService()
estimateAnthropicService = EstimateAnthropicService()

router = APIRouter(prefix="/api/v1", tags=["estimations"])


@router.post(ESTIMATE_OPENAI_ENDPOINT, response_model=EstimateResponse)
async def estimate_openai_endpoint(request: EstimateRequest):
    logger.info("Estimate OpenAI endpoint called")

    try:
        response = estimateOpenAIService.estimate_from_transcript(request.transcription)
    except EstimateServiceException as e:
        logger.error("Error occurred while estimating: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing the estimation") from e

    logger.info("Estimation result: %s", response)

    # Build response
    return generate_estimate_response(response)


@router.post(ESTIMATE_OPENAI_STREAM_ENDPOINT)
async def estimate_openai_stream_endpoint(request: EstimateRequest):
    logger.info("Estimate OpenAI stream endpoint called")

    def stream_response():
        try:
            for event in estimateOpenAIService.stream_estimate_from_transcript(request.transcription):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except EstimateServiceException as e:
            logger.error("Error occurred while streaming estimation: %s", str(e))
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
