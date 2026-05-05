import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from pydantic import ValidationError

from app.constants.estimate_constants import ESTIMATE_ENDPOINT
from app.response.estimate_responses import EstimateResponse

API_V1_PREFIX = "api/v1"


class EstimateBackendError(Exception):
    """Raised when the estimation backend cannot return a valid response."""


@dataclass(frozen=True)
class EstimateBackendClient:
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

    @property
    def _estimate_url(self) -> str:
        endpoint_path = f"{API_V1_PREFIX}/{ESTIMATE_ENDPOINT.lstrip('/')}"
        return urljoin(f"{self.base_url.rstrip('/')}/", endpoint_path)


def _format_http_error(error: HTTPError) -> str:
    if error.code == 422:
        return "La transcripción no es válida. Revisa que el texto no esté vacío."
    if error.code >= 500:
        return "El backend no pudo generar la estimación. Revisa que el servicio esté levantado y configurado."
    return f"El backend respondió con un error HTTP {error.code}."
