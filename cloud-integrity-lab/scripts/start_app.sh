#!/bin/bash
# start_app.sh - Inicia el servidor Django del Cloud Integrity Lab.
set -e

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "[start_app] WARNING: no .env found. Copia .env.example a .env y configura las variables."
fi

python3 manage.py migrate --noinput
python3 manage.py seed_data || true
exec python3 manage.py runserver 0.0.0.0:8080
