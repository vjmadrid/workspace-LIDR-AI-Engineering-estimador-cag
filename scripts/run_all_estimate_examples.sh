#!/bin/bash
# Script para probar todos los endpoints de estimación de la API local.
# Uso: ./scripts/run_all_estimate_examples.sh

BASE_URL="${BASE_URL:-http://127.0.0.1:8000/api/v1}"

TRANSCRIPTION="El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas."

CLASSIC_PAYLOAD=$(cat <<JSON
{
  "transcription": "$TRANSCRIPTION"
}
JSON
)

LLMWRAPPER_PAYLOAD=$(cat <<JSON
{
  "description": "$TRANSCRIPTION",
  "project_type": "mobile_app",
  "detail_level": "medium",
  "output_format": "phases_table"
}
JSON
)

run_json_endpoint() {
  local name="$1"
  local path="$2"
  local payload="$3"

  echo
  echo "==> $name"
  echo "POST $BASE_URL$path"

  curl -sS -X 'POST' \
    "$BASE_URL$path" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d "$payload"

  echo
}

run_stream_endpoint() {
  local name="$1"
  local path="$2"
  local payload="$3"
  local accept_header="$4"

  echo
  echo "==> $name"
  echo "POST $BASE_URL$path"

  curl -N -sS -X 'POST' \
    "$BASE_URL$path" \
    -H "accept: $accept_header" \
    -H 'Content-Type: application/json' \
    -d "$payload"

  echo
}

run_json_endpoint "Generic estimate" "/estimate" "$CLASSIC_PAYLOAD"
run_json_endpoint "OpenAI estimate" "/estimate/openai" "$CLASSIC_PAYLOAD"
run_stream_endpoint "OpenAI estimate stream" "/estimate/openai/stream" "$CLASSIC_PAYLOAD" "application/x-ndjson"
run_json_endpoint "Anthropic estimate" "/estimate/anthropic" "$CLASSIC_PAYLOAD"
run_json_endpoint "LiteLLM estimate" "/estimate/llmlite" "$CLASSIC_PAYLOAD"
run_json_endpoint "LLM wrapper estimate" "/estimate/llmwrapper" "$LLMWRAPPER_PAYLOAD"
run_stream_endpoint "LLM wrapper estimate stream" "/estimate/llmwrapper/stream" "$LLMWRAPPER_PAYLOAD" "text/event-stream"
