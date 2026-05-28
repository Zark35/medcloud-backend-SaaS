# MedCloud — Arquitectura de producción (Nginx + Gunicorn)

Guía educativa de la pila que usa MedCloud en Docker y cómo se relaciona con despliegues SaaS reales.

## Arquitectura objetivo

```
Cliente (navegador / Postman / app móvil)
        │
        ▼  HTTP :8000 (host) → :80 (contenedor nginx)
┌───────────────┐
│    Nginx      │  ← reverse proxy + archivos estáticos/media
└───────┬───────┘
        │  proxy_pass → web:8000 (red Docker)
        ▼
┌───────────────┐
│   Gunicorn    │  ← servidor WSGI (varios workers)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    Django     │  ← lógica API, ORM, JWT
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  PostgreSQL   │  ← servicio db:5432
└───────────────┘
```

## 1. ¿Qué es WSGI?

**WSGI** (Web Server Gateway Interface) es el estándar en Python para conectar un **servidor web** con una **aplicación web** (Django, Flask, etc.).

- Django expone `medcloud.wsgi:application`.
- El servidor WSGI (Gunicorn) llama a esa aplicación por cada petición HTTP.
- `runserver` también implementa WSGI, pero solo para desarrollo: un proceso, sin optimización ni seguridad para internet.

## 2. ¿Qué es Gunicorn?

**Gunicorn** (Green Unicorn) es un servidor WSGI de producción:

| Aspecto | runserver | Gunicorn |
|---------|-----------|----------|
| Procesos | 1 | Varios **workers** |
| Concurrencia | Baja | Workers + threads |
| Uso en internet | No recomendado | Estándar en SaaS |
| Reinicio / logs | Básico | Configurable (`gunicorn.conf.py`) |

En MedCloud, el contenedor `web` ejecuta:

```bash
gunicorn -c gunicorn.conf.py medcloud.wsgi:application
```

Los workers son procesos separados; si uno falla, los demás siguen atendiendo peticiones.

## 3. ¿Qué hace Nginx?

**Nginx** es un servidor web y **reverse proxy** muy eficiente:

1. **Puerta de entrada única** en el puerto 80 (publicado como `WEB_PORT` en el host).
2. **Sirve `/static/` y `/media/`** leyendo disco directamente (sin cargar Django).
3. **Reenvía** el resto (`/api/`, `/admin/`, Swagger) a Gunicorn con cabeceras `X-Forwarded-*` para que Django conozca el host y HTTPS reales.

## 4. ¿Qué es un reverse proxy?

El cliente **no habla con Gunicorn directamente**. Habla con Nginx, y Nginx **invierte** la dirección de la conexión hacia el backend interno (`web:8000`).

Ventajas en SaaS real:

- **TLS/HTTPS** en el borde (Nginx o load balancer cloud).
- **Límite de tamaño** de subida (`client_max_body_size 10M`).
- **Timeouts** y protección ante peticiones lentas.
- **Ocultar** puertos internos (Gunicorn no está expuesto al host).

## 5. Flujo de una petición

Ejemplo: `GET http://localhost:8000/api/patients/` con JWT.

1. El host redirige `8000` → contenedor `nginx:80`.
2. Nginx: la ruta no es `/static/` ni `/media/` → `proxy_pass` a `http://web:8000`.
3. Gunicorn asigna un worker → ejecuta Django → middleware → vista DRF.
4. Django consulta PostgreSQL en `db:5432`.
5. Respuesta JSON vuelve por la misma cadena.

Ejemplo: `GET /media/medical_exams/archivo.pdf`

1. Nginx resuelve el archivo en el volume compartido `/var/www/media/`.
2. Django **no** interviene → menos CPU y latencia.

## 6. Puertos y Docker

| Componente | Puerto interno | Publicado al host |
|------------|----------------|-------------------|
| nginx | 80 | `WEB_PORT` (default 8000) |
| web (Gunicorn) | 8000 | **No** (solo `expose`) |
| db (Postgres) | 5432 | opcional `POSTGRES_PUBLISH_PORT` |

Dentro de la red `medcloud-network`, Docker DNS resuelve:

- `web` → IP del contenedor Gunicorn
- `db` → IP de PostgreSQL
- `nginx` → IP de Nginx (otros contenedores podrían llamarlo, no es el caso habitual)

## 7. Static files y media

| Tipo | Ruta URL | Origen | Quién sirve en prod |
|------|----------|--------|---------------------|
| Static | `/static/` | `collectstatic` → `STATIC_ROOT` | Nginx |
| Media | `/media/` | uploads `FileField` | Nginx |

Volúmenes compartidos:

- `static_data` → `/app/staticfiles` (web) y `/var/www/static` (nginx)
- `media_data` → `/app/media` (web) y `/var/www/media` (nginx)

Con `DEBUG=False`, Django **no** sirve media por URLconf; Nginx es obligatorio para `exam_file_url`.

## 8. Cómo se usa en SaaS reales

| Entorno | Capa frontal | App server | BD |
|---------|--------------|------------|-----|
| **Docker Compose / VPS** | Nginx | Gunicorn | Postgres en contenedor o RDS |
| **Render / Heroku / Fly** | Load balancer del proveedor | Gunicorn | Postgres gestionado |
| **AWS (típico)** | ALB + Nginx o solo ALB | Gunicorn en ECS/EC2 | RDS |

MedCloud prepara ambos caminos: Compose con Nginx, Render con `render.yaml` y `DATABASE_URL`.

## 9. Probar la pila

```bash
cp .env.docker.example .env
docker compose up --build
```

| Prueba | URL / comando |
|--------|----------------|
| Health | http://localhost:8000/api/health/ |
| Swagger | http://localhost:8000/api/docs/ |
| Admin estáticos | http://localhost:8000/admin/ |
| Logs Gunicorn | `docker compose logs -f web` |
| Logs Nginx | `docker compose logs -f nginx` |
| Solo Gunicorn (red interna) | `docker compose exec web python -c "..."` |

## 10. Variables clave

Ver `.env.docker.example`. En producción real:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY` larga y secreta
- `DJANGO_ALLOWED_HOSTS` con tu dominio
- `CORS_ALLOWED_ORIGINS` en lugar de `DJANGO_ALLOW_ALL_ORIGINS=True`
- `BEHIND_PROXY=True` detrás de Nginx o Render

Más detalle de Render: [DEPLOY_RENDER.md](./DEPLOY_RENDER.md).
