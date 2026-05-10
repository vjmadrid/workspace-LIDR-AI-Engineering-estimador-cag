from app.requests.estimate_requests import EstimateRequest


class EstimateRequestFactory:
    DEFAULT_TRANSCRIPTION = (
        "Reunion para estimar una funcionalidad de autenticacion con email y password."
    )

    @classmethod
    def build(cls, **overrides) -> EstimateRequest:
        return EstimateRequest(**cls.build_payload(**overrides))

    @classmethod
    def build_payload(cls, **overrides) -> dict:
        payload = {
            "transcription": cls.DEFAULT_TRANSCRIPTION,
        }
        payload.update(overrides)
        return payload
