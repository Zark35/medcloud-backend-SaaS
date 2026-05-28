# MedCloud — imagen de aplicación Django + Gunicorn (WSGI)
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# libpq para psycopg2; gosu para bajar privilegios tras ajustar volúmenes
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gosu \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

COPY . .

RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

# El entrypoint corre como root solo para chown de volúmenes; Gunicorn como appuser
USER root

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "medcloud.wsgi:application"]
