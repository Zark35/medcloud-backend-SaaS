# MedCloud API

![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-6.0-092E20)
![DRF](https://img.shields.io/badge/DRF-3.14+-red)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-336791)
![Docker](https://img.shields.io/badge/docker-compose-ready-2496ED)
![OpenAPI](https://img.shields.io/badge/docs-Swagger%20%7C%20OpenAPI-85EA2D)

## Overview

**MedCloud** is a production-oriented **SaaS backend API** for healthcare workflows. It provides secure JWT authentication, patient lifecycle management, medical exam records with validated file uploads, and interactive OpenAPI documentation — all packaged for local development, containerized deployment, and cloud-ready hosting.

The service is designed as a **backend-first REST platform**: mobile clients, web dashboards, or third-party integrations consume a consistent JSON API while infrastructure handles TLS termination, static/media delivery, and process scaling at the edge.

---

## SaaS Model

MedCloud follows a classic **multi-tenant-ready API architecture**:

| Layer | Responsibility |
|-------|----------------|
| **API (Django REST Framework)** | Business rules, validation, authentication, OpenAPI schema |
| **Application server (Gunicorn)** | WSGI workers, concurrent request handling |
| **Reverse proxy (Nginx)** | Public entrypoint, upload limits, static/media offload |
| **Database (PostgreSQL)** | Persistent patients, exams, and user accounts |

Current scope focuses on **core clinical data domains** (patients + medical exams). The stack is prepared to extend toward organization-based tenancy, object storage for media, and managed cloud databases without changing the API contract.

---

## Architecture

### Production stack (Docker Compose)

```text
Client (Browser / Postman / Mobile App)
              │
              ▼  HTTP :WEB_PORT (default 8000)
        ┌───────────┐
        │   Nginx   │  reverse proxy + /static/ + /media/
        └─────┬─────┘
              │  proxy_pass → web:8000 (internal network)
              ▼
        ┌───────────┐
        │ Gunicorn  │  WSGI workers (gunicorn.conf.py)
        └─────┬─────┘
              ▼
        ┌───────────┐
        │  Django   │  REST API, JWT, ORM, file validation
        └─────┬─────┘
              ▼
        ┌───────────┐
        │PostgreSQL │  persistent storage
        └───────────┘
```

- **Nginx** — single public entrypoint; serves collected static files and uploaded exam media directly (lower latency than routing through Django).
- **Gunicorn** — production WSGI server with configurable workers, threads, and worker recycling.
- **Django** — API layer with JWT auth, serializers, and domain models (`Patient`, `MedicalExam`).
- **PostgreSQL** — primary datastore with health checks and persistent Docker volumes.

### Cloud deployment (Render / similar)

On platforms like **Render**, the provider load balancer replaces the Nginx container for HTTPS and routing. The same Docker image runs **Gunicorn → Django → managed PostgreSQL** via `DATABASE_URL`. See [DEPLOY_RENDER.md](./DEPLOY_RENDER.md) and `render.yaml`.

Deep dive: [PRODUCTION.md](./PRODUCTION.md) · Docker guide: [DOCKER.md](./DOCKER.md)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 6.x, Django REST Framework 3.14+ |
| **Database** | PostgreSQL 16 (Docker / production), SQLite (optional local dev) |
| **Authentication** | JWT via `djangorestframework-simplejwt` |
| **API documentation** | `drf-spectacular`, Swagger UI, OpenAPI 3 schema |
| **App server** | Gunicorn 22+ (`gunicorn.conf.py`) |
| **Reverse proxy** | Nginx 1.27 (Docker Compose) |
| **Static files** | WhiteNoise + Nginx in production |
| **CORS** | `django-cors-headers` |
| **Configuration** | `python-dotenv`, `dj-database-url` |
| **Infrastructure** | Docker, Docker Compose, Render Blueprint |

---

## Features

- JWT authentication (register, login, refresh)
- Full **Patient** CRUD with gender and medical history
- Full **Medical Exam** CRUD with `multipart/form-data` file upload
- File validation: PDF, JPG, JPEG, PNG, WEBP — max **10 MB**
- Absolute `exam_file_url` in API responses for client downloads
- Health check endpoint for Docker, Nginx, and cloud probes
- Interactive **Swagger UI** with multipart upload schemas
- Environment-driven settings (local SQLite, Docker Postgres, Render `DATABASE_URL`)
- Production security headers when `DEBUG=False`
- Proxy-aware configuration (`BEHIND_PROXY`, `X-Forwarded-*`)
- Automated migrations and `collectstatic` on container startup
- Django Admin for operational data management

---

## API Documentation (Swagger / OpenAPI)

Interactive documentation is generated with **drf-spectacular** and exposed at:

| Resource | URL (local Docker / default) |
|----------|------------------------------|
| **Swagger UI** | http://localhost:8000/api/docs/ |
| **OpenAPI schema** | http://localhost:8000/api/schema/ |

`MedicalExam` create/update operations document `multipart/form-data` payloads (patient, title, description, `exam_file`) so clients and QA can test uploads directly from Swagger.

### Authorize in Swagger

1. Register or create a user.
2. `POST /api/auth/login/` → copy the `access` token.
3. In Swagger UI, click **Authorize** and enter: `Bearer <access_token>`.

---

## Repository Structure

```text
.
├── api/                      # Domain app: models, serializers, views, URLs
│   ├── models.py             # Patient, MedicalExam
│   ├── serializers.py        # Validation, file rules, registration
│   ├── views.py              # ViewSets, health check, register
│   ├── urls.py               # Router + auth routes
│   └── migrations/
├── medcloud/                 # Django project settings & WSGI
│   ├── settings.py             # Env-based config (DB, JWT, CORS, security)
│   └── urls.py               # Admin, API include, Swagger routes
├── nginx/
│   └── nginx.conf              # Reverse proxy, static/media, body size limit
├── docker-compose.yml          # db + web (Gunicorn) + nginx
├── Dockerfile                  # Python 3.12 slim + Gunicorn entrypoint
├── docker-entrypoint.sh        # Wait DB, migrate, collectstatic, superuser bootstrap
├── gunicorn.conf.py            # Workers, threads, timeouts, max_requests
├── render.yaml                 # Render Blueprint (Postgres + Web Service)
├── requirements.txt
├── .env.example                # Local dev (SQLite or Postgres)
├── .env.docker.example         # Docker Compose production-like stack
├── PRODUCTION.md               # WSGI, Nginx, Gunicorn architecture guide
├── DOCKER.md                   # Quick start & troubleshooting
├── DEPLOY_RENDER.md            # Cloud deployment notes
└── README.md
```

---

## Environment Variables

Copy the appropriate template before running:

```bash
# Local development (SQLite by default)
cp .env.example .env

# Docker Compose (Nginx + Gunicorn + PostgreSQL)
cp .env.docker.example .env
```

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key (required in production) |
| `DJANGO_DEBUG` | `True` for local dev, `False` for Docker/cloud |
| `DJANGO_ALLOWED_HOSTS` | Space- or comma-separated hostnames |
| `DJANGO_ALLOW_ALL_ORIGINS` | CORS allow-all (disable in real production) |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins when allow-all is off |
| `USE_POSTGRESQL` | Enable Postgres engine (Docker / explicit local) |
| `POSTGRES_*` | Database name, user, password, host, port |
| `DATABASE_URL` | Full DB URL (injected by Render / PaaS) |
| `DATABASE_SSL_REQUIRE` | Require SSL for remote Postgres |
| `BEHIND_PROXY` | Trust `X-Forwarded-*` from Nginx or cloud LB |
| `USE_X_FORWARDED_HOST` | Correct host behind reverse proxy |
| `CSRF_TRUSTED_ORIGINS` | HTTPS origins for admin/forms in production |
| `WEB_PORT` | Host port mapped to Nginx (default `8000`) |
| `GUNICORN_WORKERS` | WSGI worker processes |
| `GUNICORN_TIMEOUT` | Worker timeout (uploads / slow queries) |
| `CREATE_SUPERUSER` | Bootstrap admin on startup (Render-friendly) |
| `DJANGO_SUPERUSER_*` | Username, email, password for bootstrap |

---

## Local Setup (without Docker)

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd medcloud-backend-SaaS
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit DJANGO_SECRET_KEY; set USE_POSTGRESQL=True if using local Postgres
```

### 4. Migrate and run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

| Service | URL |
|---------|-----|
| API root | http://127.0.0.1:8000/api/ |
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| OpenAPI schema | http://127.0.0.1:8000/api/schema/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| Health check | http://127.0.0.1:8000/api/health/ |

> With `DEBUG=True`, Django can serve `/media/` locally. In Docker production mode, **Nginx** serves media instead.

---

## Docker Deployment

### Quick start

```bash
cp .env.docker.example .env
docker compose up --build
```

| Endpoint | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/api/docs/ |
| Health check | http://localhost:8000/api/health/ |
| Admin | http://localhost:8000/admin/ |

Host port `8000` maps to **Nginx :80**. Gunicorn is **not** exposed outside the Docker network — only Nginx is public, matching real SaaS edge patterns.

### Useful commands

```bash
docker compose ps
docker compose logs -f web      # Gunicorn / Django
docker compose logs -f nginx    # Reverse proxy
docker compose exec web python manage.py createsuperuser
```

### Services & volumes

| Service | Role |
|---------|------|
| `nginx` | Reverse proxy, static/media, `client_max_body_size 10M` |
| `web` | Django + Gunicorn, migrations on startup |
| `db` | PostgreSQL 16 with healthcheck |

| Volume | Purpose |
|--------|---------|
| `postgres_data` | Database persistence |
| `media_data` | Uploaded exam files (shared with Nginx) |
| `static_data` | `collectstatic` output (shared with Nginx) |

---

## Nginx + Gunicorn in Practice

| Concern | Implementation |
|---------|----------------|
| **Why not `runserver`?** | Gunicorn provides multi-worker WSGI serving suitable for production traffic |
| **Why Nginx?** | TLS-ready edge, efficient static/media, upload size limits, proxy timeouts |
| **Request flow** | `/api/*` → Gunicorn → Django; `/static/`, `/media/` → Nginx disk |
| **Config files** | `nginx/nginx.conf`, `gunicorn.conf.py` |
| **Proxy headers** | `BEHIND_PROXY=True` so Django respects forwarded host/proto |

Example upload path for a medical exam:

1. Client sends `POST /api/medical-exams/` as `multipart/form-data`.
2. Nginx enforces max body size (10 MB, aligned with serializer validation).
3. Gunicorn worker runs DRF view → saves file under `media/medical_exams/`.
4. `GET` responses include `exam_file_url` pointing to `/media/...` served by Nginx.

---

## Main API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register/` | Register user (`username`, `email`, `password`) |
| `POST` | `/api/auth/login/` | Obtain JWT `access` + `refresh` |
| `POST` | `/api/auth/refresh/` | Refresh access token |

### Patients

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/patients/` | List patients |
| `POST` | `/api/patients/` | Create patient |
| `GET` | `/api/patients/{id}/` | Retrieve patient |
| `PUT` | `/api/patients/{id}/` | Update patient |
| `PATCH` | `/api/patients/{id}/` | Partial update |
| `DELETE` | `/api/patients/{id}/` | Delete patient |

### Medical exams

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/medical-exams/` | List exams (includes `patient_name`, `exam_file_url`) |
| `POST` | `/api/medical-exams/` | Create exam + file (`multipart/form-data`) |
| `GET` | `/api/medical-exams/{id}/` | Retrieve exam |
| `PUT` / `PATCH` | `/api/medical-exams/{id}/` | Update exam (optional new file) |
| `DELETE` | `/api/medical-exams/{id}/` | Delete exam |

### Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health/` | Liveness probe (`{"status": "ok", "service": "medcloud-api"}`) |

### Example: create patient

```http
POST /api/patients/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Ana García",
  "age": 34,
  "gender": "female",
  "medical_history": "Hypertension controlled with medication."
}
```

### Example: upload medical exam

```http
POST /api/medical-exams/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

patient: 1
title: Chest X-Ray
description: Annual checkup
exam_file: <binary PDF or image, max 10 MB>
```

---

## Authentication Flow

```text
Register → Login → Access protected routes → Refresh when expired
```

1. `POST /api/auth/register/` with credentials.
2. `POST /api/auth/login/` → receive `access` and `refresh` tokens.
3. Send `Authorization: Bearer <access_token>` on all protected endpoints.
4. When access expires, `POST /api/auth/refresh/` with the refresh token.

---

## Screenshots

Add captures under `docs/` for portfolio presentation:

| Screenshot | Suggested file |
|------------|----------------|
| Swagger UI — auth + patients | `docs/swagger-auth-patients.png` |
| Swagger UI — medical exam upload | `docs/swagger-exam-upload.png` |
| Docker Compose stack running | `docs/docker-compose-ps.png` |
| Sample API response (Postman) | `docs/postman-patient-exam.png` |

```markdown
![Swagger UI — MedCloud API](./docs/swagger-auth-patients.png)
![Medical exam multipart upload](./docs/swagger-exam-upload.png)
```

---

## Cloud Deployment Readiness

MedCloud supports two deployment profiles:

| Profile | Entry | App server | Database | Media |
|---------|-------|------------|----------|-------|
| **VPS / Docker Compose** | Nginx container | Gunicorn (`web`) | Postgres container | Shared volume + Nginx |
| **Render (Blueprint)** | Render HTTPS LB | Gunicorn in `Dockerfile` | Managed Postgres via `DATABASE_URL` | Ephemeral disk — migrate to S3 for production |

**Included artifacts:**

- `render.yaml` — Blueprint with health check `/api/health/`
- `DEPLOY_RENDER.md` — environment checklist and media/storage notes
- `docker-entrypoint.sh` — migrations, static collection, optional superuser bootstrap

**Recommended production checklist:**

- `DJANGO_DEBUG=False`
- Strong `DJANGO_SECRET_KEY`
- Restrict `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- Set `CSRF_TRUSTED_ORIGINS` for HTTPS admin
- Use object storage (S3, GCS) for medical files at scale
- Managed PostgreSQL with backups and SSL

**Target platforms:** Render · AWS (ECS/EC2 + ALB) · DigitalOcean App Platform · Railway · Fly.io

---

## Roadmap

- [ ] Multi-tenant organizations and role-based access control (RBAC)
- [ ] S3-compatible storage for medical files (`django-storages`)
- [ ] Automated test suite (pytest + API integration tests)
- [ ] CI/CD pipeline (GitHub Actions: lint, test, Docker build)
- [ ] Rate limiting and audit logging for compliance-sensitive workflows
- [ ] Appointment scheduling and clinician dashboards
- [ ] Email notifications and password recovery flows
- [ ] Kubernetes manifests for horizontal scaling

---

## Related Documentation

| Document | Content |
|----------|---------|
| [PRODUCTION.md](./PRODUCTION.md) | WSGI, Gunicorn, Nginx, reverse proxy concepts |
| [DOCKER.md](./DOCKER.md) | Docker quick start and troubleshooting |
| [DEPLOY_RENDER.md](./DEPLOY_RENDER.md) | Render deployment and environment variables |

---

## License

This project is released under the MIT License.

---

## Author

**Andrés Bohórquez**

- GitHub: [Zark35](https://github.com/Zark35)
- LinkedIn: [andrés-bohórquez](https://www.linkedin.com/in/andr%C3%A9s-boh%C3%B3rquez-5b2a55340)
- Public Swagger UI: https://medcloud-backend-saas.onrender.com/api/docs/
- Django UI: https://medcloud-backend-saas.onrender.com/admin/

*MedCloud — production-ready SaaS backend for healthcare data management.*
