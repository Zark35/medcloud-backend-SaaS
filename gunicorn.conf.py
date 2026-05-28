"""
Configuración de Gunicorn para MedCloud.

Gunicorn es el servidor WSGI de producción: recibe peticiones HTTP y las pasa
a la aplicación Django (medcloud.wsgi:application) usando varios workers.
"""
import multiprocessing
import os

# Render inyecta PORT; en Docker Compose usamos 8000 en el servicio web
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

_default_workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
workers = int(os.getenv('GUNICORN_WORKERS', str(_default_workers)))

threads = int(os.getenv('GUNICORN_THREADS', '2'))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '5'))

accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Reciclar workers tras N peticiones (mitiga fugas de memoria en procesos largos)
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '50'))

wsgi_app = 'medcloud.wsgi:application'
