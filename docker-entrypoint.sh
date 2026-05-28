#!/bin/sh
set -e

# Volúmenes Docker suelen montarse como root; Django/Gunicorn corren como appuser
mkdir -p /app/media /app/staticfiles
chown -R appuser:appuser /app/media /app/staticfiles

if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL configurada (p. ej. Render); omitiendo espera TCP local a Postgres."
else
  echo "Esperando a que PostgreSQL esté disponible en ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."

gosu appuser python - <<'PY'
import os
import socket
import sys
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
timeout = 60
deadline = time.time() + timeout

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"PostgreSQL accesible en {host}:{port}")
            sys.exit(0)
    except OSError:
        time.sleep(1)

print(f"Timeout: no se pudo conectar a PostgreSQL en {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
fi

echo "Aplicando migraciones..."
gosu appuser python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
gosu appuser python manage.py collectstatic --noinput

echo "Iniciando aplicación..."
exec gosu appuser "$@"
