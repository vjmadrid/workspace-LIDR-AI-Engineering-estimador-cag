from __future__ import annotations

import json
from typing import Iterator

import structlog

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse


from app.constants.estimate_constants import ESTIMATE_LLMWRAPPER_ENDPOINT, ESTIMATE_LLMWRAPPER_STREAM_ENDPOINT
from app.dependencies import get_llm_wrapper
from app.prompts.estimation.loader import render_estimation_prompt
from app.services.llmwrapper.llm_wrapper_services import LLMWrapper
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.requests.estimate_llmwrapper_requests import EstimateLLMWrapperRequest
from app.responses.estimate_llmwrapper_responses import EstimationLLMWrapperResponse
from app.services.llmlite.estimate_llmlite_services import EstimateLLMLiteService

# Logging Configuration
log = structlog.get_logger()

# Services Configuracion
estimateLLMLiteService = EstimateLLMLiteService()

# Router Configuration
router = APIRouter(prefix="/api/v1", tags=["estimations"])

# Prompt Configuration
PROMPT_VERSION = "v1"

@router.post(ESTIMATE_LLMWRAPPER_ENDPOINT, response_model=EstimationLLMWrapperResponse)
async def estimate_llmwrapper_endpoint(
    request: EstimateLLMWrapperRequest,
    wrapper: LLMWrapper = Depends(get_llm_wrapper),
) -> EstimationLLMWrapperResponse:
    log.info("Estimate LLM Wrapper endpoint called")

    # Prepare prompts (system and user) for the LLM based on the request and the prompt version
    """Render the versioned prompt pair and ask the LLM for an estimation."""
    system_prompt, user_message = render_estimation_prompt(request, version=PROMPT_VERSION)

    # Show Estimate LLM Wrapper request details
    log.info("- Show Estimate LLM Wrapper request details")
    log.info(
        "estimate_llmwrapper_request_received",
        prompt_version=PROMPT_VERSION,
        project_type=request.project_type.value,
        detail_level=request.detail_level.value,
        output_format=request.output_format.value,
        description_chars=len(request.description),
    )

    # Execute call to the LLM Wrapper and handle potential exceptions
    try:
        response = wrapper.complete(
            system_prompt=system_prompt,
            user_message=user_message,
        )
    except Exception as exc:
        log.error("estimation_endpoint_error", error=str(exc), error_type=type(exc).__name__)
        raise HTTPException(status_code=502, detail="Upstream LLM call failed") from exc

    log.info("Estimation result: %s", response)

    return EstimationLLMWrapperResponse(text=response["estimation"], prompt_version=PROMPT_VERSION)


def _sse(event: str, payload: dict) -> str:
    """Format a Server-Sent Event frame."""
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

@router.post(ESTIMATE_LLMWRAPPER_STREAM_ENDPOINT)
def stream_estimation(
    request: EstimateLLMWrapperRequest,
    wrapper: LLMWrapper = Depends(get_llm_wrapper),
) -> StreamingResponse:
    """Stream the estimation as Server-Sent Events.

    Event types emitted (in order):
        - ``status``    : lifecycle markers (``preparing``, ``calling_llm``)
        - ``token``     : incremental text chunks from the LLM
        - ``complete``  : final marker with prompt_version
        - ``error``     : a single error frame if the LLM call fails mid-stream

    The whole stream stays on a single connection; the client closes it after
    receiving ``complete`` or ``error``.
    """

    # Prepare prompts (system and user) for the LLM based on the request and the prompt version
    system_prompt, user_message = render_estimation_prompt(request, version=PROMPT_VERSION)

    # Show Estimate LLM Wrapper request details
    log.info(
        "estimation_stream_request_received",
        prompt_version=PROMPT_VERSION,
        project_type=request.project_type.value,
        detail_level=request.detail_level.value,
        output_format=request.output_format.value,
        description_chars=len(request.description),
    )

    def event_stream() -> Iterator[str]:
        yield _sse("status", {"phase": "preparing", "prompt_version": PROMPT_VERSION})
        yield _sse("status", {"phase": "calling_llm"})

        try:
            for chunk in wrapper.complete_stream(
                system_prompt=system_prompt,
                user_message=user_message,
            ):
                if chunk:
                    yield _sse("token", {"chunk": chunk})
        except Exception as exc:
            log.error(
                "estimation_stream_error",
                error=str(exc),
                error_type=type(exc).__name__,
            )
            yield _sse("error", {"message": "Upstream LLM call failed"})
            return

        yield _sse("complete", {"prompt_version": PROMPT_VERSION})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable buffering in proxies like nginx
        },
    )