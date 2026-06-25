"""Admin de telemetría GPS: dispositivos y posiciones."""
from django.contrib import admin

from ..models import Dispositivo, Posicion


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ("imei", "modelo", "vehiculo", "activo", "ultima_comunicacion")
    list_filter = ("modelo", "activo")
    search_fields = ("imei", "vehiculo__matricula", "vehiculo__nombre", "sim_iccid")
    autocomplete_fields = ("vehiculo",)
    readonly_fields = ("ultima_comunicacion", "created_at")


@admin.register(Posicion)
class PosicionAdmin(admin.ModelAdmin):
    list_display = ("dispositivo", "timestamp", "velocidad", "ignicion", "odometro")
    list_filter = ("ignicion", "movimiento")
    search_fields = ("dispositivo__imei",)
    readonly_fields = ("recibido_at",)
    date_hierarchy = "timestamp"