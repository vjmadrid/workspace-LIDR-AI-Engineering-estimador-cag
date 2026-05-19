import unittest

from app.app_factory import create_app
from app.constants.estimate_constants import (
    ESTIMATE_ANTHROPIC_ENDPOINT,
    ESTIMATE_ENDPOINT,
    ESTIMATE_LLMLITE_ENDPOINT,
    ESTIMATE_LLMWRAPPER_ENDPOINT,
    ESTIMATE_OPENAI_ENDPOINT,
)

CLASSIC_ESTIMATE_ENDPOINTS = [
    ESTIMATE_ENDPOINT,
    ESTIMATE_OPENAI_ENDPOINT,
    ESTIMATE_ANTHROPIC_ENDPOINT,
    ESTIMATE_LLMLITE_ENDPOINT,
]


class RouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = create_app().openapi()

    def test_classic_estimate_routes_use_shared_request_and_response_contracts(self) -> None:
        for endpoint in CLASSIC_ESTIMATE_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                operation = self.schema["paths"][f"/api/v1{endpoint}"]["post"]

                self.assertEqual(
                    "#/components/schemas/EstimateRequest",
                    operation["requestBody"]["content"]["application/json"]["schema"]["$ref"],
                )
                self.assertEqual(
                    "#/components/schemas/EstimateResponse",
                    operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
                )

    def test_llmwrapper_route_uses_llmwrapper_request_and_response_contracts(self) -> None:
        operation = self.schema["paths"][f"/api/v1{ESTIMATE_LLMWRAPPER_ENDPOINT}"]["post"]

        self.assertEqual(
            "#/components/schemas/EstimateLLMWrapperRequest",
            operation["requestBody"]["content"]["application/json"]["schema"]["$ref"],
        )
        self.assertEqual(
            "#/components/schemas/EstimationLLMWrapperResponse",
            operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
        )
