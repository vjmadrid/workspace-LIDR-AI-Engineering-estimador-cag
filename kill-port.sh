#!/bin/bash
set -euo pipefail

PORT="${1:-}"

if [[ -z "$PORT" ]]; then
    echo "Usage: $0 <port>"
    exit 1
fi

if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: port must be a number"
    exit 1
fi

PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN || true)"

if [[ -z "$PIDS" ]]; then
    echo "No process found listening on port $PORT"
    exit 0
fi

echo "Killing process(es) listening on port $PORT: $PIDS"
kill $PIDS