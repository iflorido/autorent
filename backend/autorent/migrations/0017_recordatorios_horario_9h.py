"""Actualiza los recordatorios de recogida a un horario fijo de las 09:00.

Si la tarea se creó antes con un intervalo (cada hora), aquí se cambia a un
Crontab diario a las 9:00 (hora Europe/Madrid). Idempotente y seguro tanto si
el sistema ya tenía la tarea como si no.
"""
from django.db import migrations


def recordatorios_a_las_9(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    crontab_9, _ = CrontabSchedule.objects.get_or_create(
        minute="0", hour="9", day_of_week="*",
        day_of_month="*", month_of_year="*",
    )
    try:
        tarea = PeriodicTask.objects.get(name="Recordatorios de recogida (48h y 24h)")
        tarea.interval = None        # quitar el intervalo anterior si lo tenía
        tarea.crontab = crontab_9    # pasar a horario fijo de las 9:00
        tarea.save()
    except PeriodicTask.DoesNotExist:
        # Si no existía, la crea ya con el crontab correcto.
        PeriodicTask.objects.create(
            name="Recordatorios de recogida (48h y 24h)",
            crontab=crontab_9,
            task="autorent.tasks.enviar_recordatorios_recogida",
            enabled=True,
            description="Avisa a los clientes 48h y 24h antes de su recogida (cada día a las 9:00).",
        )


def revertir(apps, schema_editor):
    # No revertimos el horario (no es destructivo); se deja como está.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("autorent", "0016_tareas_periodicas"),
    ]

    operations = [
        migrations.RunPython(recordatorios_a_las_9, revertir),
    ]