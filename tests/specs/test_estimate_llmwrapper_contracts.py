import unittest

from pydantic import ValidationError

from app.requests.estimate_llmwrapper_requests import EstimateLLMWrapperRequest
from app.responses.estimate_llmwrapper_responses import EstimationLLMWrapperResponse
from tests.specs.helpers import load_json, resolve_ref


class EstimateLLMWrapperContractTests(unittest.TestCase):
    def test_request_contract_matches_spec(self) -> None:
        spec = load_json("contracts/estimate_llmwrapper_request.schema.json")
        schema = EstimateLLMWrapperRequest.model_json_schema()

        self.assertEqual(spec["required"], schema["required"])
        self.assertEqual(spec["additionalProperties"], schema["additionalProperties"])
        self.assertEqual(
            spec["properties"]["description"]["minLength"],
            schema["properties"]["description"]["minLength"],
        )
        self.assertEqual(
            spec["properties"]["description"]["maxLength"],
            schema["properties"]["description"]["maxLength"],
        )

    def test_request_enum_contracts_match_spec(self) -> None:
        spec = load_json("contracts/estimate_llmwrapper_request.schema.json")
        schema = EstimateLLMWrapperRequest.model_json_schema()

        for field_name in ("project_type", "detail_level", "output_format"):
            enum_schema = resolve_ref(schema, schema["properties"][field_name]["$ref"])
            self.assertEqual(spec["properties"][field_name]["enum"], enum_schema["enum"])

    def test_response_contract_matches_spec(self) -> None:
        spec = load_json("contracts/estimate_llmwrapper_response.schema.json")
        schema = EstimationLLMWrapperResponse.model_json_schema()

        self.assertEqual(spec["required"], schema["required"])
        self.assertEqual(spec["additionalProperties"], schema["additionalProperties"])
        self.assertEqual(
            set(spec["properties"].keys()),
            set(schema["properties"].keys()),
        )

    def test_response_model_serializes_with_expected_keys(self) -> None:
        response = EstimationLLMWrapperResponse(text="Example estimation", prompt_version="v1")

        self.assertEqual({"text", "prompt_version"}, set(response.model_dump().keys()))

    def test_request_rejects_blank_description_by_contract(self) -> None:
        with self.assertRaises(ValidationError):
            EstimateLLMWrapperRequest(
                description="   ",
                project_type="web_saas",
                detail_level="medium",
                output_format="phases_table",
            )

    def test_request_rejects_unknown_enum_by_contract(self) -> None:
        with self.assertRaises(ValidationError):
            EstimateLLMWrapperRequest(
                description="A sufficiently long project description for estimation.",
                project_type="unknown",
                detail_level="medium",
                output_format="phases_table",
            )
