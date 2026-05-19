from app.prompts.builders.estimate_openai_prompt_builder import EstimateOpenAIPromptBuilder


def test_estimate_prompt_builder_is_created_with_custom_values():
    examples = [
        {
            "meeting_summary": "Crear login con email y password.",
            "estimation": "Backend: 6 horas",
        }
    ]

    builder = EstimateOpenAIPromptBuilder(
        system_prompt="Eres un estimador tecnico.",
        examples=examples,
    )

    assert builder.system_prompt == "Eres un estimador tecnico."
    assert builder.examples == examples


def test_build_messages_starts_with_system_prompt():
    builder = EstimateOpenAIPromptBuilder(
        system_prompt="System prompt de prueba.",
        examples=[],
    )

    messages = builder.build_messages("Crear una API de estimaciones.")

    assert messages[0] == {
        "role": "system",
        "content": "System prompt de prueba.",
    }


def test_build_messages_adds_final_transcript_message():
    builder = EstimateOpenAIPromptBuilder(
        system_prompt="System prompt de prueba.",
        examples=[],
    )

    messages = builder.build_messages("Crear una API de estimaciones.")

    assert messages[-1] == {
        "role": "user",
        "content": "Resumen de reunión: Crear una API de estimaciones.",
    }


def test_build_messages_includes_examples_between_system_and_transcript():
    examples = [
        {
            "meeting_summary": "Crear autenticacion.",
            "estimation": "Backend: 8 horas",
        },
        {
            "meeting_summary": "Crear dashboard.",
            "estimation": "Frontend: 13 horas",
        },
    ]
    builder = EstimateOpenAIPromptBuilder(
        system_prompt="System prompt de prueba.",
        examples=examples,
    )

    messages = builder.build_messages("Crear exportacion CSV.")

    assert messages == [
        {
            "role": "system",
            "content": "System prompt de prueba.",
        },
        {
            "role": "user",
            "content": ("Ejemplo de entrada\nResumen de reunión: Crear autenticacion.\n\nEjemplo de salida\nBackend: 8 horas"),
        },
        {
            "role": "user",
            "content": ("Ejemplo de entrada\nResumen de reunión: Crear dashboard.\n\nEjemplo de salida\nFrontend: 13 horas"),
        },
        {
            "role": "user",
            "content": "Resumen de reunión: Crear exportacion CSV.",
        },
    ]


def test_build_messages_without_examples_returns_system_and_transcript_messages():
    builder = EstimateOpenAIPromptBuilder(
        system_prompt="System prompt de prueba.",
        examples=[],
    )

    messages = builder.build_messages("Crear un endpoint de healthcheck.")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1] == {
        "role": "user",
        "content": "Resumen de reunión: Crear un endpoint de healthcheck.",
    }


def test_build_messages_preserves_transcript_content():
    builder = EstimateOpenAIPromptBuilder(
        system_prompt="System prompt de prueba.",
        examples=[],
    )

    messages = builder.build_messages("  Texto con espacios  ")

    assert messages[-1]["content"] == "Resumen de reunión:   Texto con espacios  "
