#!/bin/bash

source .env

PORT=8500

PID=$(lsof -ti tcp:$PORT)

if [ -z "$PID" ]; then
    echo "No hay ningún proceso usando el puerto $PORT"
else
    echo "Matando proceso en el puerto $PORT con PID: $PID"
    kill -9 $PID
    echo "Puerto $PORT liberado"
fi