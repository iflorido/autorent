"""
autorent/api_views.py — Endpoints de lectura de la API pública.

  GET /api/sedes/                         -> sedes activas
  GET /api/vehiculos/                     -> listado (filtros: categoria, fechas)
  GET /api/vehiculos/<id>/                -> ficha completa
  GET /api/vehiculos/<id>/precio/         -> cálculo de precio para unas fechas

Los filtros por fecha (fecha_inicio, fecha_fin en formato YYYY-MM-DD) aplican
el motor de disponibilidad: solo devuelven vehículos libres en ese rango.
"""
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import Sede
from .models import Extra, Vehiculo
from .serializers import (
    ExtraSerializer,
    SedeSerializer,
    VehiculoDetailSerializer,
    VehiculoListSerializer,
)


def _parse_fecha(valor):
    """Convierte 'YYYY-MM-DD' a date, o None si no es válida."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class SedeListView(ListAPIView):
    serializer_class = SedeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Sede.objects.filter(activa=True)


class VehiculoListView(ListAPIView):
    """Listado de vehículos activos.

    Filtros por querystring:
      ?categoria=camper           -> filtra por categoría
      ?fecha_inicio=2026-07-22&fecha_fin=2026-07-25
                                  -> solo los disponibles en ese rango
      ?sede=<id>                  -> vehículos de una sede
    """
    serializer_class = VehiculoListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Vehiculo.objects.filter(activo=True).prefetch_related(
            "fotos", "rangos_precio",
        )

        categoria = self.request.query_params.get("categoria")
        if categoria and categoria != "todos":
            qs = qs.filter(categoria=categoria)

        sede = self.request.query_params.get("sede")
        if sede:
            qs = qs.filter(sede_id=sede)

        # Filtro de disponibilidad por fechas.
        fi = _parse_fecha(self.request.query_params.get("fecha_inicio"))
        ff = _parse_fecha(self.request.query_params.get("fecha_fin"))
        if fi and ff and ff > fi:
            disponibles = [v.id for v in qs if v.esta_disponible(fi, ff)]
            qs = qs.filter(id__in=disponibles)

        return qs


class VehiculoDetailView(RetrieveAPIView):
    serializer_class = VehiculoDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Vehiculo.objects.filter(activo=True).prefetch_related(
            "fotos", "rangos_precio", "temporadas", "extras", "sede",
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def vehiculo_precio(request, pk):
    """Calcula el precio del vehículo para un rango de fechas.

    GET /api/vehiculos/<pk>/precio/?fecha_inicio=...&fecha_fin=...
    Devuelve el desglose o un error si las fechas no son válidas o el
    vehículo no es alquilable para esa duración.
    """
    try:
        vehiculo = Vehiculo.objects.get(pk=pk, activo=True)
    except Vehiculo.DoesNotExist:
        return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    fi = _parse_fecha(request.query_params.get("fecha_inicio"))
    ff = _parse_fecha(request.query_params.get("fecha_fin"))
    if not fi or not ff:
        return Response(
            {"detail": "Indica fecha_inicio y fecha_fin (YYYY-MM-DD)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if ff <= fi:
        return Response(
            {"detail": "La fecha de fin debe ser posterior a la de inicio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    calculo = vehiculo.calcular_precio(fi, ff)
    if calculo is None:
        return Response(
            {"detail": "El vehículo no tiene tarifa para esa duración."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    disponible = vehiculo.esta_disponible(fi, ff)
    return Response({
        "vehiculo_id": vehiculo.id,
        "fecha_inicio": fi,
        "fecha_fin": ff,
        "disponible": disponible,
        "num_dias": calculo["num_dias"],
        "precio_dia_base": calculo["precio_dia_base"],
        "subtotal_vehiculo": calculo["subtotal_vehiculo"],
        "fianza": calculo["fianza"],
    })


class ExtraListView(ListAPIView):
    """Listado de extras activos (para la página pública de Extras)."""
    serializer_class = ExtraSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Extra.objects.filter(activo=True)


# ─────────────────────────────────────────────────────────────
# Creación de reserva (asistente multipaso) — endpoint de ESCRITURA
# ─────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def crear_reserva(request):
    """Crea una reserva desde el asistente.

    POST /api/reservas/
    Flujo:
      1. Valida el payload (incluido acepta_condiciones).
      2. Comprueba que el vehículo existe, está activo y disponible.
      3. Crea/reutiliza el cliente (por NIF).
      4. Crea la reserva en estado 'pendiente'.
      5. Añade los extras con su precio CONGELADO del catálogo.
      6. Recalcula los totales EN SERVIDOR (ignora cualquier precio del front).
      7. Devuelve el localizador y el desglose.

    Todo dentro de una transacción atómica: si algo falla, no queda nada a medias.
    """
    from django.db import transaction
    from .models import Cliente, Reserva, ReservaExtra
    from .serializers import CrearReservaSerializer, ReservaCreadaSerializer

    serializer = CrearReservaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    datos = serializer.validated_data

    # 2) Vehículo activo + disponible en esas fechas.
    try:
        vehiculo = Vehiculo.objects.get(pk=datos["vehiculo_id"], activo=True)
    except Vehiculo.DoesNotExist:
        return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    fi, ff = datos["fecha_inicio"], datos["fecha_fin"]
    if not vehiculo.esta_disponible(fi, ff):
        return Response(
            {"detail": "El vehículo ya no está disponible en esas fechas."},
            status=status.HTTP_409_CONFLICT,
        )

    # Verificar que el vehículo tiene tarifa para esa duración.
    calculo = vehiculo.calcular_precio(fi, ff)
    if calculo is None:
        return Response(
            {"detail": "El vehículo no tiene tarifa para esa duración."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sedes = {}
    for campo, key in [("sede_recogida_id", "sede_recogida"), ("sede_entrega_id", "sede_entrega")]:
        sid = datos.get(campo)
        if sid:
            try:
                sedes[key] = Sede.objects.get(pk=sid, activa=True)
            except Sede.DoesNotExist:
                sedes[key] = None

    cdatos = datos["cliente"]

    try:
        with transaction.atomic():
            # 3) Cliente: reutiliza si el NIF ya existe, actualizando sus datos.
            cliente, _ = Cliente.objects.get_or_create(
                nif=cdatos["nif"],
                defaults={
                    "nombre": cdatos["nombre"],
                    "apellidos": cdatos.get("apellidos", ""),
                    "email": cdatos["email"],
                    "telefono": cdatos["telefono"],
                },
            )
            # Actualiza los datos del cliente con lo recibido.
            for campo in [
                "nombre", "apellidos", "email", "telefono", "fecha_nacimiento",
                "direccion", "poblacion", "cp", "provincia", "pais",
                "carnet_numero", "carnet_caducidad",
            ]:
                if campo in cdatos and cdatos[campo] not in (None, ""):
                    setattr(cliente, campo, cdatos[campo])
            cliente.save()

            # 4) Reserva en estado pendiente.
            reserva = Reserva.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                fecha_inicio=fi,
                fecha_fin=ff,
                sede_recogida=sedes.get("sede_recogida"),
                sede_entrega=sedes.get("sede_entrega"),
                estado=Reserva.Estado.PENDIENTE,
                metodo_pago=datos["metodo_pago"],
            )

            # 5) Extras con precio congelado del catálogo (no del front).
            for item in datos["extras"]:
                try:
                    extra = Extra.objects.get(pk=item["extra_id"], activo=True)
                except Extra.DoesNotExist:
                    continue  # ignora extras inexistentes
                ReservaExtra.objects.create(
                    reserva=reserva,
                    extra=extra,
                    cantidad=item.get("cantidad", 1),
                    precio_congelado=extra.precio,
                    tipo_cobro_congelado=extra.tipo_cobro,
                )

            # 6) Recalcular totales EN SERVIDOR.
            reserva.recalcular_totales(guardar=True)

    except Exception:
        return Response(
            {"detail": "No se pudo crear la reserva. Inténtalo de nuevo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 7) Respuesta con el localizador y el desglose.
    salida = ReservaCreadaSerializer(reserva)
    return Response(salida.data, status=status.HTTP_201_CREATED)