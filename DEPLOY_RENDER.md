# Despliegue en Render

## Dos modos de despliegue

| Modo | Dónde | Arquitectura |
|------|--------|--------------|
| **Docker Compose (local / VPS)** | `docker compose up` | Cliente → **Nginx** → Gunicorn → Django → Postgres |
| **Render Web Service** | `render.yaml` | Cliente → **Render LB (HTTPS)** → Gunicorn → Django → Postgres gestionado |

En Render no suele hacer falta un contenedor Nginx aparte: el **load balancer de Render** termina TLS y reenvía HTTP a tu contenedor en `PORT`. Gunicorn sigue siendo el servidor WSGI de Django.

## Pasos en Render

1. Conecta el repositorio en [Render Dashboard](https://dashboard.render.com).
2. Usa **Blueprint** con `render.yaml` o crea un **Web Service** con runtime Docker.
3. Configura manualmente (si no usas blueprint):
   - `DATABASE_URL` → desde la base Postgres de Render
   - `DJANGO_SECRET_KEY` → generada o en Secret
   - `DJANGO_ALLOWED_HOSTS` → `tu-servicio.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` → `https://tu-servicio.onrender.com`
   - `CORS_ALLOWED_ORIGINS` → URL de tu frontend
   - `DJANGO_DEBUG=False`
   - `BEHIND_PROXY=True`
4. **Health check path:** `/api/health/`
5. **Docker Command:** dejar el CMD del Dockerfile (`gunicorn ...`)

## Media en Render

El disco de Render es **efímero**. Para exámenes médicos en producción usa **S3** (o similar) con `django-storages` en una fase posterior. El volume `media_data` de Compose es válido en VPS, no en Render free.

## Static files en Render

`collectstatic` corre en el entrypoint. Los estáticos del admin/Swagger se sirven desde el contenedor; para tráfico alto considera WhiteNoise o CDN.

## Probar localmente la misma imagen que Render

```bash
cp .env.docker.example .env
docker compose up --build
# API vía Nginx: http://localhost:8000/api/docs/
```
