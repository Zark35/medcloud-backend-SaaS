# MedCloud — Docker (Nginx + Gunicorn + PostgreSQL)

## Inicio rápido

```bash
cp .env.docker.example .env
docker compose up --build
```

- **API / Swagger:** http://localhost:8000/api/docs/
- **Health:** http://localhost:8000/api/health/

El puerto **8000 del host** apunta a **Nginx (80)** dentro del stack. Gunicorn no está expuesto fuera de la red Docker.

## Arquitectura

```
localhost:WEB_PORT
       │
       ▼
┌─────────────┐     proxy      ┌─────────────┐
│   nginx     │ ─────────────► │ web:Gunicorn│
│  :80        │                │  :8000      │
│ /static     │                └──────┬──────┘
│ /media      │                       │
└─────────────┘                       ▼
                              ┌─────────────┐
                              │     db      │
                              │  Postgres   │
                              └─────────────┘
```

Guía completa: [PRODUCTION.md](./PRODUCTION.md)

## Servicios

| Servicio | Imagen / build | Rol |
|----------|----------------|-----|
| `nginx` | nginx:1.27-alpine | Reverse proxy, static, media |
| `web` | Dockerfile | Django + Gunicorn |
| `db` | postgres:16-alpine | Base de datos |

## Volúmenes

| Volume | Uso |
|--------|-----|
| `postgres_data` | Datos PostgreSQL |
| `media_data` | PDF/imágenes de exámenes |
| `static_data` | `collectstatic` (admin, Swagger assets) |

## Verificación

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f nginx
docker compose exec web python manage.py createsuperuser
```

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `502 Bad Gateway` | Gunicorn aún no listo | Esperar healthcheck de `web`; ver `docker compose logs web` |
| `DisallowedHost` | Host no en `ALLOWED_HOSTS` | Añadir dominio o `nginx` en `.env` |
| Media 404 con `DEBUG=False` | Nginx no ve el archivo | Comprobar volume `media_data` y ruta `/media/` |
| `exec /docker-entrypoint.sh: no such file` | CRLF en Windows | Rebuild; `.gitattributes` fuerza LF en `*.sh` |

## Render

Despliegue cloud: [DEPLOY_RENDER.md](./DEPLOY_RENDER.md) y `render.yaml`.
