from app.context.examples import ESTIMATION_EXAMPLES

class ContextExamplesUtil:

    @staticmethod
    def build_context_examples():
        """
        Construye el bloque de ejemplos para el prompt, usando los ejemplos definidos en ESTIMATION_EXAMPLES.
        """

        context = []

        for ex in ESTIMATION_EXAMPLES:
            context.append(
                f"### Ejemplo de entrada\nResumen de reunión: {ex['meeting_summary']}\n\n### Ejemplo de salida\n{ex['estimation']}\n"
            )

        return "\n".join(context)

    @staticmethod
    def format_examples_for_prompt(examples: list[dict]) -> str:
        """Format estimation examples into a string suitable for injection into a system prompt."""
        parts: list[str] = []
        for i, example in enumerate(examples, start=1):
            parts.append(
                f"--- EXAMPLE {i} ---\n"
                f"Meeting Summary:\n{example['meeting_summary']}\n\n"
                f"Estimation:\n{example['estimation']}\n"
            )
        return "\n".join(parts)