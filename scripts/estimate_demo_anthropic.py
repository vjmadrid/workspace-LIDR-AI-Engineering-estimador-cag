from app.services.estimate_anthropic_services import EstimateAnthropicService

estimateAnthropicService = EstimateAnthropicService()

if __name__ == "__main__":
    MESSAGE = (
        "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. "
        "La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. "
        "Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas."
    )

    print("\n***********************************")
    print("\n***** ESTIMATE DEMO ANTHROPIC *****")
    print("\n***********************************")

    print("\nTranscripción de ejemplo:\n", MESSAGE)

    # Estimate
    print("\nEnviando transcripción a LLM ...\n")

    estimation = estimateAnthropicService.estimate_from_transcript(
        transcript=MESSAGE, model="claude-haiku-4-5-20251001"
    )

    print("\n=== ESTIMACIÓN GENERADA ===\n")
    print(estimation.response)
