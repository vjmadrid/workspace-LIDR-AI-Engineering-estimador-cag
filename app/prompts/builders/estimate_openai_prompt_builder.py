from app.context.estimate_prompts import DEFAULT_SYSTEM_PROMPT_1
from app.context.examples import ESTIMATION_EXAMPLES


class EstimateOpenAIPromptBuilder:
    """
    Builds the message payload used by the estimation workflow.

    Keeping this logic isolated makes it easier to version the prompt as a
    spec, test it independently, and swap examples without touching the LLM
    execution path.
    """

    def __init__(
        self,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT_1,
        examples: list[dict] = ESTIMATION_EXAMPLES,
    ):
        self.system_prompt = system_prompt
        self.examples = examples

    def build_messages(self, transcript: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
        ]

        for example in self.examples:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Ejemplo de entrada\n"
                        f"Resumen de reunión: {example['meeting_summary']}\n\n"
                        "Ejemplo de salida\n"
                        f"{example['estimation']}"
                    ),
                }
            )

        messages.append(
            {"role": "user", "content": f"Resumen de reunión: {transcript}"}
        )
        return messages
