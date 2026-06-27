"""
autorent/tasks.py — Tareas Celery de autorent.

Celery las autodescubre gracias a app.autodiscover_tasks() en config/celery.py.
La generación del contrato corre en el worker (no bloquea la petición web) y
guarda el PDF en la carpeta protegida de documentos.
"""
import logging

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def generar_contrato_reserva(reserva_id):
    """Genera (o regenera) el PDF del contrato de una reserva.

    Crea el ContratoReserva si no existe, genera el PDF, lo guarda con su hash
    y registra la fecha de generación. Devuelve el localizador o None.
    """
    from .models import Reserva, ContratoReserva
    from .contratos import generar_pdf_contrato

    try:
        reserva = Reserva.objects.get(pk=reserva_id)
    except Reserva.DoesNotExist:
        logger.error("generar_contrato_reserva: reserva %s no existe", reserva_id)
        return None

    pdf_bytes, digest = generar_pdf_contrato(reserva)

    contrato, _ = ContratoReserva.objects.get_or_create(reserva=reserva)
    # Borra el PDF anterior (regeneración) para no acumular ficheros.
    if contrato.archivo:
        contrato.archivo.delete(save=False)

    nombre = f"contrato_{reserva.localizador}.pdf"
    contrato.archivo.save(nombre, ContentFile(pdf_bytes), save=False)
    contrato.hash_sha256 = digest
    contrato.generado_at = timezone.now()
    contrato.save()

    logger.info("Contrato generado para %s (hash %s)", reserva.localizador, digest[:12])
    return reserva.localizador


@shared_task
def procesar_telemetria_id(posicion_id):
    """Procesa una posición ya insertada (por FastAPI) aplicando la lógica de
    detección de eventos, alertas, driver score y mantenimiento.

    FastAPI inserta la posición y encola esta tarea; el worker la ejecuta con
    la misma lógica que usa la ingesta de Django (sin duplicar nada).
    """
    from .models import Posicion
    from .flota_logica import procesar_telemetria
    try:
        posicion = Posicion.objects.select_related("dispositivo__vehiculo").get(pk=posicion_id)
    except Posicion.DoesNotExist:
        logger.warning("procesar_telemetria_id: posición %s no existe", posicion_id)
        return None
    procesar_telemetria(posicion)
    return posicion_id


@shared_task
def limpiar_posiciones_antiguas(dias=30):
    """Borra las posiciones GPS con más de 'dias' días, para acotar la BD.

    Se ejecuta una vez al día (configurado en Celery Beat).
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Posicion

    limite = timezone.now() - timedelta(days=dias)
    borradas, _ = Posicion.objects.filter(timestamp__lt=limite).delete()
    logger.info("Limpieza GPS: %s posiciones eliminadas (> %s días).", borradas, dias)
    return borradas


@shared_task
def enviar_recordatorios_recogida():
    """Envía recordatorios a clientes con recogida próxima (48h y 24h antes).

    Se ejecuta periódicamente (p.ej. cada hora). Marca cada recordatorio como
    enviado para no duplicarlo. Como la recogida es por fecha (sin hora), se
    interpreta a 2 días y 1 día de antelación respectivamente.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Reserva
    from .notificaciones import enviar_recordatorio_recogida

    hoy = timezone.now().date()
    enviados = 0

    # Estados en los que tiene sentido recordar (no canceladas ni finalizadas).
    activas = Reserva.objects.filter(
        estado__in=[Reserva.Estado.CONFIRMADA, Reserva.Estado.DOCUMENTACION,
                    Reserva.Estado.PENDIENTE],
    )

    # 48h antes ~ recogida dentro de 2 días.
    for r in activas.filter(fecha_inicio=hoy + timedelta(days=2),
                            recordatorio_48h_enviado=False):
        if enviar_recordatorio_recogida(r, 48):
            r.recordatorio_48h_enviado = True
            r.save(update_fields=["recordatorio_48h_enviado"])
            enviados += 1

    # 24h antes ~ recogida dentro de 1 día.
    for r in activas.filter(fecha_inicio=hoy + timedelta(days=1),
                            recordatorio_24h_enviado=False):
        if enviar_recordatorio_recogida(r, 24):
            r.recordatorio_24h_enviado = True
            r.save(update_fields=["recordatorio_24h_enviado"])
            enviados += 1

    logger.info("Recordatorios de recogida enviados: %s", enviados)
    return enviados