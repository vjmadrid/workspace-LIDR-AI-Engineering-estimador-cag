from app.services.openai.estimate_openai_services import EstimateOpenAIService

estimateOpenAIService = EstimateOpenAIService()

if __name__ == "__main__":
    MESSAGE = (
        "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. "
        "La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. "
        "Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas."
    )

    print("\n********************************")
    print("\n***** ESTIMATE DEMO OPENAI *****")
    print("\n********************************")

    print("\nTranscripción de ejemplo:\n", MESSAGE)

    # Estimate
    print("\nEnviando transcripción a LLM ...\n")

    estimation = estimateOpenAIService.estimate_from_transcript(
        transcript=MESSAGE, model="gpt-4o-mini"
    )

    print("\n=== ESTIMACIÓN GENERADA ===\n")
    print(estimation.response)
