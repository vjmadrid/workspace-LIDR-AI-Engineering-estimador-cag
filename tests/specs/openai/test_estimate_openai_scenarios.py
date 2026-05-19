import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.app_factory import create_app
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.requests.estimate_requests import EstimateRequest
from app.responses.estimate_responses import generate_estimate_response
from app.prompts.builders.estimate_openai_prompt_builder import EstimateOpenAIPromptBuilder

ROOT_DIR = Path(__file__).resolve().parents[3]
SPECS_DIR = ROOT_DIR / "specs"


def load_json(relative_path: str) -> dict:
    return json.loads((SPECS_DIR / relative_path).read_text(encoding="utf-8"))


class EstimateOpenAIScenarioTests(unittest.TestCase):
    def test_success_scenario_is_stable(self) -> None:
        scenario = load_json("scenarios/openai/estimate_openai_success.json")
        expected = scenario["expected_response"]

        dto = EstimateResponseDTO(
            llm_provider=expected["provider"],
            llm_model=expected["llm_model"],
            response=expected["estimation"],
            num_tokens_input=expected["metadata"]["token_metadata"]["num_tokens_input"],
            num_tokens_response=expected["metadata"]["token_metadata"]["num_tokens_response"],
            num_tokens_total=expected["metadata"]["token_metadata"]["num_tokens_total"],
            input_token_cost=expected["metadata"]["cost_metadata"]["input_token_cost"],
            output_token_cost=expected["metadata"]["cost_metadata"]["output_token_cost"],
            total_token_cost=expected["metadata"]["cost_metadata"]["total_token_cost"],
        )

        response = generate_estimate_response(dto)

        self.assertEqual(expected["provider"], response.provider)
        self.assertEqual(expected["llm_model"], response.llm_model)
        self.assertEqual(expected["estimation"], response.estimation)

    def test_prompt_builder_uses_examples_as_specified(self) -> None:
        builder = EstimateOpenAIPromptBuilder()
        messages = builder.build_messages("ejemplo")

        self.assertEqual("system", messages[0]["role"])
        self.assertEqual("Resumen de reunión: ejemplo", messages[-1]["content"])
        self.assertEqual(len(messages), len(builder.examples) + 2)

    def test_whitespace_transcription_is_rejected_by_contract(self) -> None:
        with self.assertRaises(ValueError):
            EstimateRequest(transcription="   ")

    def test_endpoint_rejects_blank_transcription(self) -> None:
        client = TestClient(create_app())

        response = client.post("/api/v1/estimate/openai", json={"transcription": "   "})

        self.assertEqual(422, response.status_code)
        self.assertTrue(response.json()["detail"])
