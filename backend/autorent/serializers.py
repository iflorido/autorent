"""
autorent/serializers.py — Serializers de lectura para la API pública.

Pensados para el frontend React:
  - SedeSerializer            : sedes de recogida/entrega.
  - ExtraSerializer           : extras contratables.
  - FotoVehiculoSerializer    : fotos de la galería.
  - RangoPrecioSerializer     : tramos de precio.
  - VehiculoListSerializer    : tarjeta resumida (listado/carrusel).
  - VehiculoDetailSerializer  : ficha completa.
"""
from rest_framework import serializers

from core.models import Sede
from .models import Extra, FotoVehiculo, RangoPrecio, TemporadaPrecio, Vehiculo


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = [
            "id", "nombre", "slug", "direccion", "poblacion", "cp",
            "provincia", "pais", "latitud", "longitud", "telefono",
            "email", "horario",
        ]


class ExtraSerializer(serializers.ModelSerializer):
    tipo_cobro_display = serializers.CharField(source="get_tipo_cobro_display", read_only=True)

    class Meta:
        model = Extra
        fields = ["id", "nombre", "descripcion", "precio", "tipo_cobro", "tipo_cobro_display"]


class FotoVehiculoSerializer(serializers.ModelSerializer):
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = FotoVehiculo
        fields = ["id", "imagen", "principal", "orden", "titulo"]

    def get_imagen(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get("request")
        url = obj.imagen.url
        return request.build_absolute_uri(url) if request else url


class RangoPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangoPrecio
        fields = ["dias_min", "dias_max", "precio_dia"]


class VehiculoListSerializer(serializers.ModelSerializer):
    """Tarjeta resumida para listados y carrusel."""
    categoria_display = serializers.CharField(source="get_categoria_display", read_only=True)
    foto_principal = serializers.SerializerMethodField()
    precio_desde = serializers.SerializerMethodField()

    class Meta:
        model = Vehiculo
        fields = [
            "id", "nombre", "marca", "modelo", "categoria", "categoria_display",
            "plazas", "puertas", "combustible", "cambio", "capacidad_carga",
            "foto_principal", "precio_desde",
        ]

    def get_foto_principal(self, obj):
        foto = obj.foto_principal
        if not foto or not foto.imagen:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(foto.imagen.url) if request else foto.imagen.url

    def get_precio_desde(self, obj):
        """Precio/día más bajo de sus rangos (el 'desde X €')."""
        rangos = obj.rangos_precio.all()
        if not rangos:
            return None
        return min(r.precio_dia for r in rangos)


class VehiculoDetailSerializer(serializers.ModelSerializer):
    """Ficha completa del vehículo."""
    categoria_display = serializers.CharField(source="get_categoria_display", read_only=True)
    combustible_display = serializers.CharField(source="get_combustible_display", read_only=True)
    cambio_display = serializers.CharField(source="get_cambio_display", read_only=True)
    fotos = FotoVehiculoSerializer(many=True, read_only=True)
    rangos_precio = RangoPrecioSerializer(many=True, read_only=True)
    extras = ExtraSerializer(many=True, read_only=True)
    precio_desde = serializers.SerializerMethodField()
    sede = SedeSerializer(read_only=True)

    class Meta:
        model = Vehiculo
        fields = [
            "id", "nombre", "marca", "modelo", "anio", "categoria",
            "categoria_display", "plazas", "puertas", "combustible",
            "combustible_display", "cambio", "cambio_display",
            "capacidad_carga", "descripcion", "fianza",
            "fotos", "rangos_precio", "extras", "precio_desde", "sede",
        ]

    def get_precio_desde(self, obj):
        rangos = obj.rangos_precio.all()
        if not rangos:
            return None
        return min(r.precio_dia for r in rangos)