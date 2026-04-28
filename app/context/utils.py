from app.context.examples import ESTIMATION_EXAMPLES

def build_context_examples():
    """
    Construye el bloque de ejemplos para el prompt, usando los ejemplos definidos en ESTIMATION_EXAMPLES.
    """

    context = []

    for ex in ESTIMATION_EXAMPLES:
        context.append(f"### Ejemplo de entrada\nResumen de reunión: {ex['meeting_summary']}\n\n### Ejemplo de salida\n{ex['estimation']}\n")

    return "\n".join(context)