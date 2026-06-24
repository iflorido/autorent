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
from .models import (
    Cliente, Extra, FotoVehiculo, RangoPrecio, Reserva,
    ReservaExtra, TemporadaPrecio, Vehiculo,
)


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
            "id", "slug", "nombre", "marca", "modelo", "categoria", "categoria_display",
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
            "id", "slug", "nombre", "marca", "modelo", "anio", "categoria",
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


# ─────────────────────────────────────────────────────────────
# Serializers de ESCRITURA (creación de reserva desde el asistente)
# ─────────────────────────────────────────────────────────────

class FechaOpcionalField(serializers.DateField):
    """DateField que trata la cadena vacía como null (el front envía '')."""
    def to_internal_value(self, value):
        if value in ("", None):
            return None
        return super().to_internal_value(value)


class ClienteEntradaSerializer(serializers.Serializer):
    """Datos del cliente que llegan del asistente de reserva.

    Para formalizar el contrato de alquiler todos los datos son obligatorios.
    """
    nombre = serializers.CharField(max_length=120)
    apellidos = serializers.CharField(max_length=160)
    nif = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=20)
    fecha_nacimiento = serializers.DateField()
    direccion = serializers.CharField(max_length=255)
    poblacion = serializers.CharField(max_length=100)
    cp = serializers.CharField(max_length=10)
    provincia = serializers.CharField(max_length=100)
    pais = serializers.CharField(max_length=60, required=False, allow_blank=True, default="España")
    carnet_numero = serializers.CharField(max_length=40)
    carnet_caducidad = serializers.DateField()


class ConductorAdicionalSerializer(serializers.Serializer):
    """Conductor adicional con sus datos legales (todos obligatorios)."""
    nombre = serializers.CharField(max_length=120)
    apellidos = serializers.CharField(max_length=160)
    nif = serializers.CharField(max_length=20)
    fecha_nacimiento = serializers.DateField()
    carnet_numero = serializers.CharField(max_length=40)
    carnet_caducidad = serializers.DateField()


class ExtraEntradaSerializer(serializers.Serializer):
    """Un extra seleccionado: id + cantidad."""
    extra_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1, default=1)


class CrearReservaSerializer(serializers.Serializer):
    """Payload completo del asistente para crear una reserva.

    El precio NO se acepta del cliente: se recalcula en el servidor a partir
    del vehículo, las fechas y los extras (con su precio congelado del catálogo).
    """
    vehiculo_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    sede_recogida_id = serializers.IntegerField(required=False, allow_null=True)
    sede_entrega_id = serializers.IntegerField(required=False, allow_null=True)
    metodo_pago = serializers.ChoiceField(
        choices=["transferencia", "tarjeta", "efectivo"], default="transferencia",
    )
    cliente = ClienteEntradaSerializer()
    extras = ExtraEntradaSerializer(many=True, required=False, default=list)
    conductores_adicionales = ConductorAdicionalSerializer(many=True, required=False, default=list)
    acepta_condiciones = serializers.BooleanField()

    def validate_acepta_condiciones(self, value):
        if not value:
            raise serializers.ValidationError(
                "Debes aceptar las Condiciones Generales de Contratación."
            )
        return value

    def validate(self, data):
        if data["fecha_fin"] <= data["fecha_inicio"]:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de devolución debe ser posterior a la de recogida."}
            )
        return data


class ReservaCreadaSerializer(serializers.ModelSerializer):
    """Respuesta tras crear la reserva (resumen para el frontend)."""
    vehiculo_nombre = serializers.CharField(source="vehiculo.nombre", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Reserva
        fields = [
            "localizador", "estado", "estado_display", "vehiculo_nombre",
            "fecha_inicio", "fecha_fin", "num_dias", "precio_dia_base",
            "subtotal_vehiculo", "subtotal_extras", "fianza", "total",
            "metodo_pago",
        ]