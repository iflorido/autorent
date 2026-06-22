"""
core/tasks.py — Tareas Celery de core.

De momento solo una tarea de comprobación (ping). Celery la autodescubre
gracias a app.autodiscover_tasks() en config/celery.py.

Para probar el circuito completo, desde el shell de Django:
    from core.tasks import ping
    ping.delay()
y revisar el log del worker: debe aparecer "pong".
"""
from celery import shared_task
from django.utils import timezone


@shared_task
def ping():
    """Tarea trivial para verificar que el worker ejecuta."""
    mensaje = f"pong @ {timezone.now().isoformat()}"
    print(mensaje)
    return mensaje