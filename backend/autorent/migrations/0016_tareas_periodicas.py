"""Configura las tareas periódicas en Celery Beat automáticamente.

Crea los horarios y las tareas periódicas para:
  - Limpieza diaria de posiciones GPS antiguas (> 30 días).
  - Recordatorios de recogida (cada hora revisa reservas a 48h y 24h).

Así aparecen ya listas en el admin (django_celery_beat) tras desplegar, sin
configurarlas a mano. Son idempotentes: si ya existen, no se duplican.
"""
import json

from django.db import migrations


def crear_tareas_periodicas(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    # --- Limpieza GPS: todos los días a las 03:30 ---
    crontab_limpieza, _ = CrontabSchedule.objects.get_or_create(
        minute="30", hour="3", day_of_week="*",
        day_of_month="*", month_of_year="*",
    )
    PeriodicTask.objects.get_or_create(
        name="Limpieza de posiciones GPS antiguas",
        defaults={
            "crontab": crontab_limpieza,
            "task": "autorent.tasks.limpiar_posiciones_antiguas",
            "kwargs": json.dumps({"dias": 30}),
            "enabled": True,
            "description": "Borra posiciones GPS con más de 30 días para acotar la BD.",
        },
    )

    # --- Recordatorios de recogida: todos los días a las 09:00 ---
    crontab_recordatorios, _ = CrontabSchedule.objects.get_or_create(
        minute="0", hour="9", day_of_week="*",
        day_of_month="*", month_of_year="*",
    )
    PeriodicTask.objects.get_or_create(
        name="Recordatorios de recogida (48h y 24h)",
        defaults={
            "crontab": crontab_recordatorios,
            "task": "autorent.tasks.enviar_recordatorios_recogida",
            "enabled": True,
            "description": "Avisa a los clientes 48h y 24h antes de su recogida (cada día a las 9:00).",
        },
    )


def revertir(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(
        name__in=[
            "Limpieza de posiciones GPS antiguas",
            "Recordatorios de recogida (48h y 24h)",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("autorent", "0015_reserva_recordatorio_24h_enviado_and_more"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_tareas_periodicas, revertir),
    ]