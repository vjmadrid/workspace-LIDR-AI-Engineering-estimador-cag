#!/bin/bash
# Script para probar el endpoint LLM Service streaming de estimación de la API local.
# Uso: ./scripts/run_estimate_llmservice_stream_example.sh

API_URL="${API_URL:-http://127.0.0.1:8000/api/v1/estimate/llmservice/stream}"

curl -N -X 'POST' \
  "$API_URL" \
  -H 'accept: text/event-stream' \
  -H 'Content-Type: application/json' \
  -d '{
  "transcription": "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas.",
  "max_tokens": 4000
}'
