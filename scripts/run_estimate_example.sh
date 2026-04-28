#!/bin/bash
# Script para probar el endpoint de estimación de la API local
# Uso: ./run_estimate_example.sh

API_URL="http://127.0.0.1:8000/api/v1/estimate"

curl -X 'POST' \
  "$API_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "transcription": "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas."
}'
