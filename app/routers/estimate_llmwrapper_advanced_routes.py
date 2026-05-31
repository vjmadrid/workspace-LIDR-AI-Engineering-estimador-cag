"""POST /api/v1/estimate — typed input, validated structured output.

Error handling mapping:

- ``InputGuardrailViolation`` → HTTP 400 with ``{reason, message}`` so the cliente
  can render a clear actionable message (the regex caught a prompt injection,
  PII, or moderation flagged the content).
- Anything else from the pipeline → HTTP 502 (the LLM upstream failed,
  including ``InstructorRetryException`` when the model couldn't satisfy
  validators within ``max_retries``).
"""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.constants.estimate_constants import ESTIMATE_LLMWRAPPER_ADVANCED_ENDPOINT
from app.dependencies import get_estimation_service
from app.guardrails.input import InputGuardrailViolation
from app.requests.estimate_llmwrapper_advanced_requests import EstimateLLMWrapperAdvancedRequest
from app.responses.estimate_llmwrapper_advanced_responses import EstimationLLMWrapperAdvancedResponse
from app.services.estimate_advance_services import EstimateAdvancedService

# Logging Configuration
log = structlog.get_logger()


# Router Configuration
router = APIRouter(prefix="/api/v1", tags=["estimations"])


@router.post(ESTIMATE_LLMWRAPPER_ADVANCED_ENDPOINT, response_model=EstimationLLMWrapperAdvancedResponse)
def estimate_llmwrapper_advanced_endpoint(
    request: EstimateLLMWrapperAdvancedRequest,
    service: Annotated[EstimateAdvancedService, Depends(get_estimation_service)],
) -> EstimationLLMWrapperAdvancedResponse:
    """Run the full estimation pipeline and return the structured response."""
    log.info(
        "estimation_advanced_request_received",
        project_type=request.project_type.value,
        detail_level=request.detail_level.value,
        output_format=request.output_format.value,
        description_chars=len(request.description),
    )

    try:
        return service.estimate(request)
    except InputGuardrailViolation as exc:
        log.info(
            "estimation_blocked_by_input_guardrail",
            reason=exc.reason,
            message=exc.message,
        )
        raise HTTPException(
            status_code=400, detail={"reason": exc.reason, "message": exc.message}
        ) from exc
    except Exception as exc:
        error_message = str(exc)
        log.error(
            "estimation_endpoint_error",
            error=error_message[:400],
            error_type=type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Upstream LLM call failed",
                "error_type": type(exc).__name__,
                "error": error_message,
            },
        ) from exc
