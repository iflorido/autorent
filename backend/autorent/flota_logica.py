"""
autorent/flota_logica.py — Detección de eventos y alertas a partir de telemetría.

Se invoca al ingestar cada posición. Detecta:
  - Conducción brusca (frenazo, acelerón, curva) por acelerómetro.
  - Exceso de velocidad.
  - Mantenimiento vencido por odómetro (km) o por fecha (ITV).
Genera EventoConduccion y Alerta según corresponda.

Umbrales configurables vía settings (con valores por defecto razonables).
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Umbrales por defecto (g del acelerómetro; km/h para velocidad).
UMBRAL_FRENAZO = getattr(settings, "GPS_UMBRAL_FRENAZO_G", 0.45)
UMBRAL_ACELERON = getattr(settings, "GPS_UMBRAL_ACELERON_G", 0.45)
UMBRAL_CURVA = getattr(settings, "GPS_UMBRAL_CURVA_G", 0.40)
LIMITE_VELOCIDAD = getattr(settings, "GPS_LIMITE_VELOCIDAD_KMH", 120)


def _reserva_activa(vehiculo, momento):
    """Reserva en curso del vehículo en ese instante (estado activa), si existe."""
    from .models import Reserva
    return (
        Reserva.objects.filter(
            vehiculo=vehiculo,
            estado=Reserva.Estado.ACTIVA,
            fecha_inicio__lte=momento.date(),
            fecha_fin__gte=momento.date(),
        )
        .first()
    )


def procesar_telemetria(posicion):
    """Analiza una Posicion recién guardada y genera eventos/alertas.

    Se llama desde la ingesta tras crear la posición. Tolerante a fallos: si
    algo va mal, se registra y no rompe la ingesta.
    """
    try:
        dispositivo = posicion.dispositivo
        vehiculo = dispositivo.vehiculo
        if not vehiculo:
            return
        reserva = _reserva_activa(vehiculo, posicion.timestamp)

        _detectar_conduccion(posicion, vehiculo, reserva)
        _detectar_velocidad(posicion, vehiculo, reserva)
        if posicion.odometro is not None:
            _comprobar_mantenimiento_km(vehiculo, posicion.odometro)
        _comprobar_mantenimiento_fecha(vehiculo)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error procesando telemetría %s: %s", posicion.id, exc)


def _crear_evento(vehiculo, reserva, tipo, severidad, posicion, velocidad=None):
    from .models import EventoConduccion
    EventoConduccion.objects.create(
        vehiculo=vehiculo, reserva=reserva, tipo=tipo, severidad=round(severidad, 3),
        velocidad=velocidad, latitud=posicion.latitud, longitud=posicion.longitud,
        timestamp=posicion.timestamp,
    )


def _detectar_conduccion(posicion, vehiculo, reserva):
    """Frenazo/acelerón (eje longitudinal X) y curva (eje lateral Y)."""
    from .models import EventoConduccion, Alerta

    ax = posicion.aceleracion_x
    ay = posicion.aceleracion_y

    if ax is not None:
        if ax <= -UMBRAL_FRENAZO:
            _crear_evento(vehiculo, reserva, EventoConduccion.Tipo.FRENAZO, abs(ax), posicion)
            _alerta_conduccion(vehiculo, "Frenazo brusco detectado", Alerta)
        elif ax >= UMBRAL_ACELERON:
            _crear_evento(vehiculo, reserva, EventoConduccion.Tipo.ACELERON, abs(ax), posicion)
            _alerta_conduccion(vehiculo, "Aceleración brusca detectada", Alerta)

    if ay is not None and abs(ay) >= UMBRAL_CURVA:
        _crear_evento(vehiculo, reserva, EventoConduccion.Tipo.CURVA, abs(ay), posicion)
        _alerta_conduccion(vehiculo, "Curva tomada bruscamente", Alerta)


def _detectar_velocidad(posicion, vehiculo, reserva):
    from .models import EventoConduccion, Alerta
    if posicion.velocidad and posicion.velocidad > LIMITE_VELOCIDAD:
        exceso = posicion.velocidad - LIMITE_VELOCIDAD
        _crear_evento(vehiculo, reserva, EventoConduccion.Tipo.VELOCIDAD, exceso,
                      posicion, velocidad=posicion.velocidad)
        # Alerta de velocidad (no deduplicada: cada exceso importa).
        Alerta.objects.create(
            vehiculo=vehiculo, tipo=Alerta.Tipo.VELOCIDAD,
            mensaje=f"Exceso de velocidad: {posicion.velocidad:.0f} km/h "
                    f"(límite {LIMITE_VELOCIDAD}).",
        )


def _alerta_conduccion(vehiculo, mensaje, Alerta):
    """Crea alerta de conducción, evitando spam (1 cada 5 min por vehículo)."""
    hace_5 = timezone.now() - timedelta(minutes=5)
    reciente = Alerta.objects.filter(
        vehiculo=vehiculo, tipo=Alerta.Tipo.CONDUCCION, created_at__gte=hace_5,
    ).exists()
    if not reciente:
        Alerta.objects.create(
            vehiculo=vehiculo, tipo=Alerta.Tipo.CONDUCCION, mensaje=mensaje,
        )


def _comprobar_mantenimiento_km(vehiculo, odometro):
    """Si el odómetro alcanza el umbral de una regla por km, genera alerta."""
    from .models import ReglaMantenimiento, Alerta
    reglas = ReglaMantenimiento.objects.filter(
        vehiculo=vehiculo, activa=True, km_proximo__isnull=False,
    )
    for regla in reglas:
        if odometro >= regla.km_proximo:
            clave = f"mant-km-{regla.id}-{regla.km_proximo}"
            # Evitar duplicar la misma alerta hasta que se actualice el umbral.
            if not Alerta.objects.filter(clave_dedupe=clave).exists():
                Alerta.objects.create(
                    vehiculo=vehiculo, tipo=Alerta.Tipo.MANTENIMIENTO,
                    mensaje=f"{regla.get_tipo_display()}: alcanzados "
                            f"{odometro:,} km (programado a {regla.km_proximo:,} km).".replace(",", "."),
                    clave_dedupe=clave,
                )


def _comprobar_mantenimiento_fecha(vehiculo):
    """Si una regla por fecha (ITV) está próxima a vencer, genera alerta."""
    from .models import ReglaMantenimiento, Alerta
    hoy = timezone.now().date()
    reglas = ReglaMantenimiento.objects.filter(
        vehiculo=vehiculo, activa=True, fecha_proxima__isnull=False,
    )
    for regla in reglas:
        dias_restantes = (regla.fecha_proxima - hoy).days
        if dias_restantes <= regla.dias_aviso:
            clave = f"mant-fecha-{regla.id}-{regla.fecha_proxima}"
            if not Alerta.objects.filter(clave_dedupe=clave).exists():
                if dias_restantes < 0:
                    txt = f"{regla.get_tipo_display()} VENCIDA el {regla.fecha_proxima}."
                else:
                    txt = (f"{regla.get_tipo_display()} próxima: {regla.fecha_proxima} "
                           f"({dias_restantes} días).")
                Alerta.objects.create(
                    vehiculo=vehiculo, tipo=Alerta.Tipo.MANTENIMIENTO,
                    mensaje=txt, clave_dedupe=clave,
                )


def calcular_driver_score(vehiculo, dias=30, reserva=None):
    """Calcula la puntuación de conducción (0-100) de un vehículo.

    Parte de 100 y resta según los eventos. Si se pasa 'reserva', puntúa solo
    los eventos de esa reserva (quién lo lleva ahora).
    """
    from .models import EventoConduccion
    qs = vehiculo.eventos_conduccion.all()
    if reserva is not None:
        qs = qs.filter(reserva=reserva)
    else:
        desde = timezone.now() - timedelta(days=dias)
        qs = qs.filter(timestamp__gte=desde)

    # Penalización por tipo de evento.
    pesos = {
        EventoConduccion.Tipo.FRENAZO: 3,
        EventoConduccion.Tipo.ACELERON: 2,
        EventoConduccion.Tipo.CURVA: 2,
        EventoConduccion.Tipo.VELOCIDAD: 4,
    }
    penalizacion = 0
    conteo = {}
    for ev in qs:
        penalizacion += pesos.get(ev.tipo, 1)
        conteo[ev.tipo] = conteo.get(ev.tipo, 0) + 1

    score = max(0, 100 - penalizacion)
    return {
        "score": score,
        "eventos_total": qs.count(),
        "desglose": conteo,
    }