from app.services.llm_service import estimate_from_transcript

if __name__ == "__main__":

    TRANSCRIPT = (
        "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. "
        "La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. "
        "Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas."
    )

    print("\n*************************")
    print("\n***** ESTIMATE DEMO *****")
    print("\n*************************")

    print("\nTranscripción de ejemplo:\n", TRANSCRIPT)

    # Estimate
    print("\nEnviando transcripción a LLM...\n")
    estimation = estimate_from_transcript(TRANSCRIPT)
    print("\n=== ESTIMACIÓN GENERADA ===\n")
    print(estimation)
