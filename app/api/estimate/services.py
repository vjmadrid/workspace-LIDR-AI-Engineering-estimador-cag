from openai import OpenAI
from app.config import get_settings


from app.api.estimate.prompts import SYSTEM_PROMPT

from app.context.utils import build_context_examples
from app.context.examples import ESTIMATION_EXAMPLES

from app.api.estimate.constants import OPENAI_MODEL_DEFAULT
from app.api.estimate.schemas import EstimateResponse
from app.core.token.utils import OpenAITokenUtil


settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class EstimateService:

    def estimate_from_transcript(self, transcript: str, model: str = OPENAI_MODEL_DEFAULT) -> str:

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *[
                {"role": "user", "content": f"Ejemplo de entrada\nResumen de reunión: {ex['meeting_summary']}\n\nEjemplo de salida\n{ex['estimation']}"}
                for ex in ESTIMATION_EXAMPLES
            ],
            {"role": "user", "content": f"Resumen de reunión: {transcript}"},
        ]

        print(f"\n[INFO] transcript: {transcript}...")
        print(f"\n[INFO] model: {model}")

        input_tokens = OpenAITokenUtil.count_tokens(messages, model)
        print(f"[INFO] Tokens de entrada (prompt): {input_tokens}")

        #try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        #    max_tokens=2048,
            temperature=0.2,
        )
        #except openai.error.RateLimitError:
        #    raise HTTPException(status_code=429, detail="Rate limit exceeded")
        #except openai.error.InvalidRequestError as e:
        #    raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
        #except Exception as e:
        #    raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


        response_value = response.choices[0].message.content.strip()

        print(f"[INFO] Tokens prompt usados: {response.usage.prompt_tokens}")
        print(f"[INFO] Tokens completados (respuesta): {response.usage.completion_tokens}")
        print(f"[INFO] Tokens totales: {response.usage.total_tokens}")

        return EstimateResponse(
            response=response.choices[0].message.content.strip(),
            num_tokens_input=response.usage.prompt_tokens,
            num_tokens_response=response.usage.completion_tokens,
            num_tokens_total=response.usage.total_tokens
        )

        return response_value