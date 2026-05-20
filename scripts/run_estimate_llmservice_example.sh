#!/bin/bash
# Script para probar el endpoint LLM Service de estimación de la API local.
# Uso: ./scripts/run_estimate_llmservice_example.sh

API_URL="${API_URL:-http://127.0.0.1:8000/api/v1/estimate/llmservice}"

curl -X 'POST' \
  "$API_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "transcription": "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas.",
  "preprocessing": "none",
  "example_format": "markdown",
  "num_examples": 3,
  "use_examples": true,
  "max_tokens": 4000,
  "evaluate": true
}'
