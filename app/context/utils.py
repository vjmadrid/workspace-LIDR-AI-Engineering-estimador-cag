from app.context.basic_examples import BASIC_ESTIMATION_EXAMPLES
from app.context.canonical_examples import CANONICAL_EXAMPLES
from app.context.dtos import CanonicalExample

class ContextExamplesUtil:

    @staticmethod
    def build_context_examples():
        """
        Construye el bloque de ejemplos para el prompt, usando los ejemplos definidos en ESTIMATION_EXAMPLES.
        """

        context = []

        for ex in BASIC_ESTIMATION_EXAMPLES:
            context.append(
                f"### Ejemplo de entrada\nResumen de reunión: {ex['meeting_summary']}\n\n### Ejemplo de salida\n{ex['estimation']}\n"
            )

        return "\n".join(context)

class BasicExamplesUtil:

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

class CanonicalExamplesUtil:

    @staticmethod
    def select_examples(n: int) -> list[CanonicalExample]:
        """Return the first n canonical examples, capped at the available pool."""
        return CANONICAL_EXAMPLES[: max(0, min(n, len(CANONICAL_EXAMPLES)))]

    def format_examples_for_prompt(
        examples: list[CanonicalExample],
        fmt: ExampleFormat = "markdown",
    ) -> str:
        """Render a list of canonical examples in the requested format for prompt injection."""
        if not examples:
            return ""
        if fmt == "markdown":
            return _format_markdown(examples)
        if fmt == "json":
            return _format_json(examples)
        if fmt == "narrative":
            return _format_narrative(examples)
        raise ValueError(f"Unknown example format: {fmt}")


def _format_markdown(examples: list[CanonicalExample]) -> str:
    parts: list[str] = []
    for i, ex in enumerate(examples, start=1):
        parts.append(
            f"--- EXAMPLE {i} ---\n"
            f"Meeting Summary:\n{ex.meeting_summary}\n\n"
            f"Estimation:\n{ex.estimation_markdown}\n"
        )
    return "\n".join(parts)


def _format_json(examples: list[CanonicalExample]) -> str:
    payload = [
        {
            "meeting_summary": ex.meeting_summary,
            "title": ex.title,
            "breakdown": [
                {"task": task, "hours": hours, "cost_eur": cost}
                for task, hours, cost in ex.breakdown
            ],
            "totals": {"hours": ex.total_hours, "cost_eur": ex.total_cost},
            "team": ex.team,
            "duration_weeks": ex.duration_weeks,
        }
        for ex in examples
    ]
    return "Reference examples (JSON):\n" + json.dumps(payload, indent=2, ensure_ascii=False)


def _format_narrative(examples: list[CanonicalExample]) -> str:
    parts: list[str] = []
    for i, ex in enumerate(examples, start=1):
        items = "; ".join(f"{task} ({hours}h)" for task, hours, _ in ex.breakdown)
        parts.append(
            f"In a previous engagement (#{i}), the client requested: {ex.meeting_summary} "
            f"We proposed '{ex.title}', estimating {ex.total_hours} hours at "
            f"{ex.total_cost:,} EUR over {ex.duration_weeks} weeks with team "
            f"{', '.join(ex.team)}. Major work items included: {items}."
        )
    return "\n\n".join(parts)