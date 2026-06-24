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