"""
Django settings for medcloud project.
Configuración por variables de entorno (desarrollo local, Docker, Render).
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# --- Seguridad básica ---
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

_allowed_hosts_raw = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1')
ALLOWED_HOSTS = [
    host.strip()
    for host in _allowed_hosts_raw.replace(',', ' ').split()
    if host.strip()
]

# --- Aplicaciones ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medcloud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'medcloud.wsgi.application'

# --- Base de datos ---
# Render inyecta DATABASE_URL; Docker/local usan POSTGRES_* o SQLite
DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRESQL = os.getenv('USE_POSTGRESQL', 'False') == 'True'

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.getenv('DB_CONN_MAX_AGE', '600')),
            ssl_require=os.getenv('DATABASE_SSL_REQUIRE', 'False') == 'True',
        )
    }
elif USE_POSTGRESQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'medcloud'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos y media ---
# Nginx sirve /static/ y /media/ en producción; collectstatic rellena STATIC_ROOT
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- DRF / JWT / OpenAPI ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

CORS_ALLOW_ALL_ORIGINS = os.getenv('DJANGO_ALLOW_ALL_ORIGINS', 'True') == 'True'
CORS_ALLOW_CREDENTIALS = True

if not CORS_ALLOW_ALL_ORIGINS:
    _cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in _cors_origins.replace(',', ' ').split()
        if origin.strip()
    ]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SPECTACULAR_SETTINGS = {
    'TITLE': 'MedCloud API',
    'DESCRIPTION': 'API para gestión de pacientes y exámenes médicos.',
    'VERSION': '1.0.0',
    'COMPONENT_SPLIT_REQUEST': True,
}

# --- Producción (detrás de Nginx / Render load balancer) ---
USE_X_FORWARDED_HOST = os.getenv('USE_X_FORWARDED_HOST', 'False') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

_csrf_origins_raw = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _csrf_origins_raw.replace(',', ' ').split()
    if origin.strip()
]

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
    SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0

# Activar headers de proxy cuando Nginx o Render terminan TLS
if os.getenv('BEHIND_PROXY', 'False') == 'True':
    USE_X_FORWARDED_HOST = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
}
