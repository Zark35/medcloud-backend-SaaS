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

if [ "${CREATE_SUPERUSER:-False}" = "True" ]; then
  if [ -z "${DJANGO_SUPERUSER_USERNAME:-}" ] || [ -z "${DJANGO_SUPERUSER_EMAIL:-}" ] || [ -z "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "CREATE_SUPERUSER=True pero faltan DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD; se omite creación."
  else
    echo "Verificando superusuario por defecto..."
    gosu appuser python - <<'PY'
import os
from django.contrib.auth import get_user_model

username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]

User = get_user_model()
user = User.objects.filter(username=username).first()

if user:
    updated = False
    if not user.is_staff:
        user.is_staff = True
        updated = True
    if not user.is_superuser:
        user.is_superuser = True
        updated = True
    if email and user.email != email:
        user.email = email
        updated = True
    if updated:
        user.save(update_fields=["is_staff", "is_superuser", "email"])
        print(f"Superusuario '{username}' ya existía; se actualizaron flags/email.")
    else:
        print(f"Superusuario '{username}' ya existe; sin cambios.")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superusuario '{username}' creado.")
PY
  fi
fi

echo "Iniciando aplicación..."
exec gosu appuser "$@"
