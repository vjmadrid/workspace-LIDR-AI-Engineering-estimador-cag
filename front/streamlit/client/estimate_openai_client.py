import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from pydantic import ValidationError

from app.constants.estimate_constants import ESTIMATE_OPENAI_ENDPOINT, ESTIMATE_OPENAI_STREAM_ENDPOINT
from app.response.estimate_responses import EstimateResponse

API_V1_PREFIX = "api/v1"


class EstimateBackendError(Exception):
    """Raised when the estimation backend cannot return a valid response."""


class EstimateStreamEvent(TypedDict, total=False):
    type: Literal["delta", "metadata", "error"]
    content: str
    message: str
    provider: str
    llm_model: str
    num_tokens_input: int
    num_tokens_response: int
    num_tokens_total: int


@dataclass(frozen=True)
class EstimateOpenAIBackendClient:
    base_url: str
    timeout_seconds: float

    def estimate_from_transcript(self, transcription: str) -> EstimateResponse:
        request = Request(
            url=self._estimate_url,
            data=json.dumps({"transcription": transcription}).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read()
        except HTTPError as exc:
            raise EstimateBackendError(_format_http_error(exc)) from exc
        except TimeoutError as exc:
            raise EstimateBackendError("El backend tardó demasiado en responder. Inténtalo de nuevo.") from exc
        except URLError as exc:
            raise EstimateBackendError("No se pudo conectar con el backend de estimaciones.") from exc

        try:
            payload = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise EstimateBackendError("El backend devolvió una respuesta que no se puede interpretar.") from exc

        try:
            return EstimateResponse.model_validate(payload)
        except ValidationError as exc:
            raise EstimateBackendError("El backend devolvió una estimación con un formato inesperado.") from exc

    def stream_estimate_from_transcript(self, transcription: str) -> Iterator[EstimateStreamEvent]:
        request = Request(
            url=self._estimate_stream_url,
            data=json.dumps({"transcription": transcription}).encode("utf-8"),
            headers={
                "Accept": "application/x-ndjson",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue

                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise EstimateBackendError("El backend devolvió un fragmento de streaming que no se puede interpretar.") from exc

                    if payload.get("type") == "error":
                        raise EstimateBackendError(payload.get("message", "El backend no pudo generar la estimación."))

                    yield payload
        except HTTPError as exc:
            raise EstimateBackendError(_format_http_error(exc)) from exc
        except TimeoutError as exc:
            raise EstimateBackendError("El backend tardó demasiado en responder. Inténtalo de nuevo.") from exc
        except URLError as exc:
            raise EstimateBackendError("No se pudo conectar con el backend de estimaciones.") from exc

    @property
    def _estimate_url(self) -> str:
        endpoint_path = f"{API_V1_PREFIX}/{ESTIMATE_OPENAI_ENDPOINT.lstrip('/')}"
        return urljoin(f"{self.base_url.rstrip('/')}/", endpoint_path)

    @property
    def _estimate_stream_url(self) -> str:
        endpoint_path = f"{API_V1_PREFIX}/{ESTIMATE_OPENAI_STREAM_ENDPOINT.lstrip('/')}"
        return urljoin(f"{self.base_url.rstrip('/')}/", endpoint_path)


def _format_http_error(error: HTTPError) -> str:
    if error.code == 422:
        return "La transcripción no es válida. Revisa que el texto no esté vacío."
    if error.code >= 500:
        return "El backend no pudo generar la estimación. Revisa que el servicio esté levantado y configurado."
    return f"El backend respondió con un error HTTP {error.code}."
