"""
autorent/telemetria_views.py — Ingesta y lectura de telemetría GPS.

- Ingesta: POST con datos ya decodificados (el simulador, o más adelante un
  receptor Codec 8, los envía aquí). Protegido con un token compartido.
- Lectura: estado actual de la flota e histórico de un vehículo, para el
  dashboard tipo NavControl.
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Dispositivo, Posicion


def _token_ingesta_ok(request):
    """Comprueba el token compartido de ingesta (cabecera X-Ingest-Token)."""
    esperado = getattr(settings, "GPS_INGEST_TOKEN", "")
    if not esperado:
        return False
    recibido = request.headers.get("X-Ingest-Token", "")
    return recibido and recibido == esperado


@api_view(["POST"])
@permission_classes([AllowAny])  # autenticación por token de ingesta
def ingesta_telemetria(request):
    """Recibe una trama de telemetría ya decodificada.

    POST /api/gps/ingesta/
    Cabecera: X-Ingest-Token: <token>
    Cuerpo (JSON): { imei, timestamp, lat, lon, velocidad, ignicion, ... }
    """
    if not _token_ingesta_ok(request):
        return Response({"detail": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED)

    datos = request.data
    imei = str(datos.get("imei", "")).strip()
    if not imei:
        return Response({"detail": "Falta el IMEI."}, status=status.HTTP_400_BAD_REQUEST)

    # Identificar el dispositivo por IMEI (no por matrícula).
    try:
        dispositivo = Dispositivo.objects.get(imei=imei, activo=True)
    except Dispositivo.DoesNotExist:
        return Response({"detail": "Dispositivo no registrado."},
                        status=status.HTTP_404_NOT_FOUND)

    # Timestamp del fix (ISO). Si no viene, usar la hora del servidor.
    ts_raw = datos.get("timestamp")
    if ts_raw:
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
            if timezone.is_naive(ts):
                ts = timezone.make_aware(ts)
        except (ValueError, AttributeError):
            ts = timezone.now()
    else:
        ts = timezone.now()

    try:
        lat = float(datos["lat"])
        lon = float(datos["lon"])
    except (KeyError, TypeError, ValueError):
        return Response({"detail": "Latitud/longitud no válidas."},
                        status=status.HTTP_400_BAD_REQUEST)

    def num(clave, defecto=None):
        v = datos.get(clave)
        try:
            return float(v) if v is not None else defecto
        except (TypeError, ValueError):
            return defecto

    pos = Posicion.objects.create(
        dispositivo=dispositivo,
        timestamp=ts,
        latitud=lat,
        longitud=lon,
        altitud=num("altitud"),
        rumbo=num("rumbo"),
        satelites=int(datos["satelites"]) if datos.get("satelites") is not None else None,
        velocidad=num("velocidad", 0) or 0,
        ignicion=bool(datos.get("ignicion", False)),
        movimiento=bool(datos.get("movimiento", False)),
        odometro=int(datos["odometro"]) if datos.get("odometro") is not None else None,
        nivel_combustible=num("nivel_combustible"),
        voltaje_bateria=num("voltaje_bateria"),
        aceleracion_x=num("acel_x"),
        aceleracion_y=num("acel_y"),
        aceleracion_z=num("acel_z"),
        evento_id=int(datos["evento_id"]) if datos.get("evento_id") is not None else None,
    )

    # Actualizar la última comunicación del dispositivo (para el mapa).
    dispositivo.ultima_comunicacion = ts
    dispositivo.save(update_fields=["ultima_comunicacion"])

    # Analizar para driver score, exceso de velocidad y mantenimiento.
    from .flota_logica import procesar_telemetria
    procesar_telemetria(pos)

    return Response({"ok": True, "id": pos.id}, status=status.HTTP_201_CREATED)


def _serializar_posicion(pos):
    return {
        "timestamp": pos.timestamp.isoformat(),
        "lat": pos.latitud,
        "lon": pos.longitud,
        "velocidad": pos.velocidad,
        "ignicion": pos.ignicion,
        "movimiento": pos.movimiento,
        "rumbo": pos.rumbo,
        "altitud": pos.altitud,
        "satelites": pos.satelites,
        "odometro": pos.odometro,
        "nivel_combustible": pos.nivel_combustible,
        "voltaje_bateria": pos.voltaje_bateria,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def flota_estado(request):
    """Última posición conocida de cada vehículo con dispositivo.

    GET /api/gps/flota/
    Para el mapa del dashboard: un punto por vehículo, con datos del vehículo.
    """
    salida = []
    dispositivos = (
        Dispositivo.objects.filter(activo=True, vehiculo__isnull=False)
        .select_related("vehiculo")
    )
    for disp in dispositivos:
        ultima = disp.posiciones.first()  # ordenado por -timestamp
        if not ultima:
            continue
        # Online si ha comunicado en los últimos 10 minutos.
        online = (timezone.now() - ultima.timestamp) < timedelta(minutes=10)
        v = disp.vehiculo
        salida.append({
            "vehiculo_id": disp.vehiculo_id,
            "vehiculo": v.nombre,
            "matricula": v.matricula,
            "categoria": v.get_categoria_display(),
            "limite_velocidad": v.limite_velocidad_efectivo(),
            "imei": disp.imei,
            "modelo_dispositivo": disp.get_modelo_display(),
            "online": online,
            "ultima_comunicacion": ultima.timestamp.isoformat(),
            "posicion": _serializar_posicion(ultima),
        })
    return Response({"vehiculos": salida})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vehiculo_historico(request, vehiculo_id):
    """Histórico de posiciones de un vehículo en un rango de tiempo.

    GET /api/gps/vehiculo/<id>/historico/?desde=ISO&hasta=ISO
    Para dibujar la ruta (polilínea) en el mapa.
    """
    disp = Dispositivo.objects.filter(vehiculo_id=vehiculo_id, activo=True).first()
    if not disp:
        return Response({"detail": "El vehículo no tiene dispositivo."},
                        status=status.HTTP_404_NOT_FOUND)

    qs = disp.posiciones.all()
    desde = request.query_params.get("desde")
    hasta = request.query_params.get("hasta")
    if desde:
        try:
            qs = qs.filter(timestamp__gte=datetime.fromisoformat(desde))
        except ValueError:
            pass
    if hasta:
        try:
            qs = qs.filter(timestamp__lte=datetime.fromisoformat(hasta))
        except ValueError:
            pass

    # Limitar para no devolver cantidades enormes (orden cronológico).
    qs = qs.order_by("timestamp")[:5000]
    return Response({
        "vehiculo_id": vehiculo_id,
        "puntos": [_serializar_posicion(p) for p in qs],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def alertas_activas(request):
    """Alertas no leídas, para el panel del dashboard.

    GET /api/gps/alertas/
    """
    from .models import Alerta
    qs = Alerta.objects.filter(leida=False).select_related("vehiculo")[:50]
    salida = [{
        "id": a.id,
        "tipo": a.tipo,
        "tipo_display": a.get_tipo_display(),
        "vehiculo": a.vehiculo.nombre,
        "matricula": a.vehiculo.matricula,
        "mensaje": a.mensaje,
        "fecha": a.created_at.isoformat(),
    } for a in qs]
    return Response({"alertas": salida, "total": len(salida)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def alerta_marcar_leida(request, alerta_id):
    """Marca una alerta como atendida. POST /api/gps/alertas/<id>/leer/"""
    from .models import Alerta
    try:
        a = Alerta.objects.get(pk=alerta_id)
    except Alerta.DoesNotExist:
        return Response({"detail": "No existe."}, status=status.HTTP_404_NOT_FOUND)
    a.leida = True
    a.save(update_fields=["leida"])
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def driver_score(request, vehiculo_id):
    """Driver score de un vehículo (acumulado 30 días y de la reserva activa).

    GET /api/gps/vehiculo/<id>/score/
    """
    from .models import Vehiculo, Reserva
    from .flota_logica import calcular_driver_score
    try:
        vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    except Vehiculo.DoesNotExist:
        return Response({"detail": "No existe."}, status=status.HTTP_404_NOT_FOUND)

    acumulado = calcular_driver_score(vehiculo, dias=30)

    # Score de la reserva activa (quién lo lleva ahora), si la hay.
    reserva = (
        Reserva.objects.filter(vehiculo=vehiculo, estado=Reserva.Estado.ACTIVA)
        .select_related("cliente").first()
    )
    por_reserva = None
    if reserva:
        sc = calcular_driver_score(vehiculo, reserva=reserva)
        por_reserva = {
            "localizador": reserva.localizador,
            "cliente": reserva.cliente.nombre_completo,
            **sc,
        }

    return Response({
        "vehiculo_id": vehiculo_id,
        "acumulado_30d": acumulado,
        "reserva_activa": por_reserva,
    })