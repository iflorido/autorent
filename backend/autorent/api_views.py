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