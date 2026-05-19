import unittest

from app.requests.estimate_requests import EstimateRequest
from app.responses.estimate_responses import EstimateResponse
from tests.specs.helpers import load_json


class EstimateSharedContractTests(unittest.TestCase):
    def test_request_contract_matches_spec(self) -> None:
        spec = load_json("contracts/estimate_request.schema.json")
        schema = EstimateRequest.model_json_schema()

        self.assertEqual(spec["required"], schema["required"])
        self.assertEqual(
            spec["properties"]["transcription"]["type"],
            schema["properties"]["transcription"]["type"],
        )
        self.assertEqual(
            spec["properties"]["transcription"]["minLength"],
            schema["properties"]["transcription"]["minLength"],
        )
        self.assertEqual(spec["additionalProperties"], schema["additionalProperties"])

    def test_response_contract_matches_top_level_spec(self) -> None:
        spec = load_json("contracts/estimate_response.schema.json")
        schema = EstimateResponse.model_json_schema()

        self.assertEqual(spec["required"], schema["required"])
        self.assertEqual(spec["additionalProperties"], schema["additionalProperties"])
        for field_name in ("provider", "llm_model", "estimation", "metadata"):
            self.assertIn(field_name, schema["properties"])

    def test_response_model_serializes_with_expected_keys(self) -> None:
        response = EstimateResponse(
            provider="openai",
            llm_model="gpt-4o-mini",
            estimation="Example estimation",
            metadata=None,
        )

        self.assertEqual(
            {"provider", "llm_model", "estimation", "metadata"},
            set(response.model_dump().keys()),
        )
