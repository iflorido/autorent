"""
config/celery.py — App de Celery para AutoRent.

Lee la configuración desde settings.py (claves con prefijo CELERY_) y
autodescubre las tareas definidas en cada app (archivos tasks.py).

El scheduler usa django_celery_beat (DatabaseScheduler), de modo que las
tareas periódicas se gestionan desde el admin sin tocar código.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("autorent")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")