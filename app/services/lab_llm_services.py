from openai import OpenAI

from app.config import get_settings
from app.context.basic_examples import BASIC_ESTIMATION_EXAMPLES

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Eres un estimador de software experto. "
    "Generas estimaciones detalladas y realistas a partir de ejemplos previos y la transcripción de una nueva reunión. "
    "Sigue el formato y el nivel de detalle de los ejemplos proporcionados."
)


def estimate_from_transcript(transcript: str, model: str = "gpt-4o-mini") -> str:
    """
    Envía la transcripción y el contexto a OpenAI y devuelve la estimación generada.
    """
    # The `prompt` variable in the `estimate_from_transcript` function is a string that serves as the
    # input prompt for the OpenAI API. It includes the system prompt, context examples, and the new
    # meeting transcript to generate an estimation. The `prompt` is structured in a specific format
    # required by the OpenAI API to provide relevant information for generating accurate estimations.
    # prompt = f"""{SYSTEM_PROMPT}\n\n# Ejemplos de referencia\n{build_context_examples()}\n\n# Nueva reunión\nResumen de reunión: {transcript}\n\n### Estimación generada\n"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *[
                {
                    "role": "user",
                    "content": f"Ejemplo de entrada\nResumen de reunión: {ex['meeting_summary']}\n\nEjemplo de salida\n{ex['estimation']}",
                }
                for ex in BASIC_ESTIMATION_EXAMPLES
            ],
            {"role": "user", "content": f"Resumen de reunión: {transcript}"},
        ],
        max_tokens=2048,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
