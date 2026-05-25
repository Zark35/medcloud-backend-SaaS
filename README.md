# MedCloud - Backend API

MedCloud es una API profesional construida con Django y Django REST Framework para gestionar pacientes y exámenes médicos.

## Estructura principal

- `medcloud/settings.py`: configuración del proyecto, JWT, CORS y base de datos.
- `medcloud/urls.py`: rutas principales que importan las rutas de `api`.
- `api/models.py`: modelos `Patient` y `MedicalExam`.
- `api/serializers.py`: validación y representación de datos para los modelos.
- `api/views.py`: viewsets y endpoint de registro.
- `api/urls.py`: endpoints organizados con router profesional.

## Dependencias

Instalar:

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Variables de entorno

Copiar `.env.example` a `.env` y ajustar las variables. Los valores por defecto permiten desarrollo local con SQLite.

## Comandos

```bash
cd "c:\Users\Andres\Desktop\Proyecto de SaaS"
.venv\Scripts\python.exe manage.py makemigrations api
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py runserver
```

## Endpoints principales

- `POST /api/auth/register/` - registro de usuario
- `POST /api/auth/login/` - obtiene `access` y `refresh` JWT
- `POST /api/auth/refresh/` - renueva el token
- `GET /api/patients/` - lista pacientes
- `POST /api/patients/` - crea paciente
- `GET /api/medical-exams/` - lista exámenes
- `POST /api/medical-exams/` - crea examen con upload de archivo

## Pruebas con Postman

1. Registrar usuario: `POST /api/auth/register/` con JSON `{ "username": "demo", "email": "demo@example.com", "password": "strongpass123" }`
2. Login: `POST /api/auth/login/` con JSON `{ "username": "demo", "password": "strongpass123" }`
3. Añadir cabecera `Authorization: Bearer <access_token>` para las rutas protegidas.
4. Crear paciente: `POST /api/patients/`.
5. Crear examen: `POST /api/medical-exams/` con `form-data` y campo `exam_file`.
