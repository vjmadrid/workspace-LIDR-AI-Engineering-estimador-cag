from types import SimpleNamespace

from app.config import LLMProvider
from app.constants.estimate_constants import ANTHROPIC_MODEL_DEFAULT, LLMLITE_MODEL_DEFAULT, OPENAI_MODEL_DEFAULT
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.services.anthropic.estimate_anthropic_services import EstimateAnthropicService
from app.services.estimate_services import EstimateService
from app.services.llmlite.estimate_llmlite_services import EstimateLLMLiteService
from app.services.openai.estimate_openai_services import EstimateOpenAIService


class FakePromptBuilder:
    def build_messages(self, transcript: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": "System prompt for integration test."},
            {"role": "user", "content": f"Resumen de reunión: {transcript}"},
        ]


class FakeOpenAIClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create_completion))
        self.calls = []

    def _create_completion(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=" Estimacion generada desde OpenAI fake. "))],
            usage=SimpleNamespace(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
            ),
        )


class FakeAnthropicClient:
    def __init__(self):
        self.messages = SimpleNamespace(create=self._create_message)
        self.calls = []

    def _create_message(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[
                SimpleNamespace(
                    type="text",
                    text="Estimacion generada desde Anthropic fake.",
                )
            ],
            usage=SimpleNamespace(
                input_tokens=80,
                output_tokens=40,
            ),
        )


class FakeLLMLiteCompletion:
    def __init__(self):
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=" Estimacion generada desde LiteLLM fake. "))],
            usage=SimpleNamespace(
                prompt_tokens=90,
                completion_tokens=45,
                total_tokens=135,
            ),
        )


def build_settings(provider: LLMProvider):
    return SimpleNamespace(
        LLM_PROVIDER=provider,
        OPENAI_API_KEY="test-openai-api-key",
        ANTHROPIC_API_KEY="test-anthropic-api-key",
        LLMLITE_MODEL=LLMLITE_MODEL_DEFAULT,
    )


def build_estimate_service(
    provider: LLMProvider,
    openai_client,
    anthropic_client,
    llmlite_completion,
):
    settings = build_settings(provider)
    prompt_builder = FakePromptBuilder()

    return EstimateService(
        settings=settings,
        openai_service=EstimateOpenAIService(
            client=openai_client,
            prompt_builder=prompt_builder,
            settings=settings,
        ),
        anthropic_service=EstimateAnthropicService(
            client=anthropic_client,
            prompt_builder=prompt_builder,
            settings=settings,
        ),
        llmlite_service=EstimateLLMLiteService(
            completion=llmlite_completion,
            prompt_builder=prompt_builder,
            settings=settings,
        ),
    )


def test_estimate_service_uses_openai_provider_end_to_end():
    openai_client = FakeOpenAIClient()
    anthropic_client = FakeAnthropicClient()
    llmlite_completion = FakeLLMLiteCompletion()
    service = build_estimate_service(
        LLMProvider.OPENAI,
        openai_client=openai_client,
        anthropic_client=anthropic_client,
        llmlite_completion=llmlite_completion,
    )

    response = service.estimate_from_transcript("Crear un panel de estimaciones.")

    assert isinstance(response, EstimateResponseDTO)
    assert response.llm_provider == LLMProvider.OPENAI
    assert response.llm_model == OPENAI_MODEL_DEFAULT
    assert response.response == "Estimacion generada desde OpenAI fake."
    assert response.num_tokens_input == 100
    assert response.num_tokens_response == 50
    assert response.num_tokens_total == 150
    assert response.total_token_cost > 0
    assert len(openai_client.calls) == 1
    assert len(anthropic_client.calls) == 0
    assert len(llmlite_completion.calls) == 0
    assert openai_client.calls[0]["model"] == OPENAI_MODEL_DEFAULT
    assert openai_client.calls[0]["temperature"] == 0.2
    assert openai_client.calls[0]["messages"] == [
        {"role": "system", "content": "System prompt for integration test."},
        {
            "role": "user",
            "content": "Resumen de reunión: Crear un panel de estimaciones.",
        },
    ]


def test_estimate_service_uses_anthropic_provider_end_to_end():
    openai_client = FakeOpenAIClient()
    anthropic_client = FakeAnthropicClient()
    llmlite_completion = FakeLLMLiteCompletion()
    service = build_estimate_service(
        LLMProvider.ANTHROPIC,
        openai_client=openai_client,
        anthropic_client=anthropic_client,
        llmlite_completion=llmlite_completion,
    )

    response = service.estimate_from_transcript("Crear un panel de estimaciones.")

    assert isinstance(response, EstimateResponseDTO)
    assert response.llm_provider == LLMProvider.ANTHROPIC
    assert response.llm_model == ANTHROPIC_MODEL_DEFAULT
    assert response.response == "Estimacion generada desde Anthropic fake."
    assert response.num_tokens_input == 80
    assert response.num_tokens_response == 40
    assert response.num_tokens_total == 120
    assert response.total_token_cost > 0
    assert len(openai_client.calls) == 0
    assert len(anthropic_client.calls) == 1
    assert len(llmlite_completion.calls) == 0
    assert anthropic_client.calls[0]["model"] == ANTHROPIC_MODEL_DEFAULT
    assert anthropic_client.calls[0]["temperature"] == 0.2
    assert anthropic_client.calls[0]["system"] == "System prompt for integration test."
    assert anthropic_client.calls[0]["messages"] == [
        {
            "role": "user",
            "content": "Resumen de reunión: Crear un panel de estimaciones.",
        },
    ]


def test_estimate_service_uses_llmlite_provider_end_to_end():
    openai_client = FakeOpenAIClient()
    anthropic_client = FakeAnthropicClient()
    llmlite_completion = FakeLLMLiteCompletion()
    service = build_estimate_service(
        LLMProvider.LLMLITE,
        openai_client=openai_client,
        anthropic_client=anthropic_client,
        llmlite_completion=llmlite_completion,
    )

    response = service.estimate_from_transcript("Crear un panel de estimaciones.")

    assert isinstance(response, EstimateResponseDTO)
    assert response.llm_provider == LLMProvider.LLMLITE
    assert response.llm_model == LLMLITE_MODEL_DEFAULT
    assert response.response == "Estimacion generada desde LiteLLM fake."
    assert response.num_tokens_input == 90
    assert response.num_tokens_response == 45
    assert response.num_tokens_total == 135
    assert response.total_token_cost > 0
    assert len(openai_client.calls) == 0
    assert len(anthropic_client.calls) == 0
    assert len(llmlite_completion.calls) == 1
    assert llmlite_completion.calls[0]["model"] == LLMLITE_MODEL_DEFAULT
    assert llmlite_completion.calls[0]["temperature"] == 0.2
    assert llmlite_completion.calls[0]["messages"] == [
        {"role": "system", "content": "System prompt for integration test."},
        {
            "role": "user",
            "content": "Resumen de reunión: Crear un panel de estimaciones.",
        },
    ]
