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
    list_per_page = 25
    show_full_result_count = False  # tabla grande: evita COUNT(*) costoso
    list_display = ("dispositivo", "timestamp", "velocidad", "ignicion", "odometro")
    list_filter = ("ignicion", "movimiento")
    search_fields = ("dispositivo__imei",)
    readonly_fields = ("recibido_at",)
    date_hierarchy = "timestamp"


from ..models import ReglaMantenimiento, EventoConduccion, Alerta


@admin.register(ReglaMantenimiento)
class ReglaMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "vehiculo", "cada_km", "km_proximo", "fecha_proxima", "activa")
    list_filter = ("tipo", "activa")
    search_fields = ("vehiculo__matricula", "vehiculo__nombre")
    autocomplete_fields = ("vehiculo",)


@admin.register(EventoConduccion)
class EventoConduccionAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("tipo", "vehiculo", "severidad", "velocidad", "timestamp", "reserva")
    list_filter = ("tipo",)
    search_fields = ("vehiculo__matricula",)
    date_hierarchy = "timestamp"


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ("tipo", "vehiculo", "mensaje", "leida", "created_at")
    list_filter = ("tipo", "leida")
    search_fields = ("vehiculo__matricula", "mensaje")
    actions = ["marcar_leidas"]

    @admin.action(description="Marcar como leídas")
    def marcar_leidas(self, request, queryset):
        n = queryset.update(leida=True)
        self.message_user(request, f"{n} alerta(s) marcada(s) como leídas.")