"""
autorent/admin/vehiculo.py — Admin del bloque Vehículo.

La ficha del vehículo integra (inlines) sus fotos, rangos de precio,
temporadas, bloqueos y mantenimientos, para gestionarlo todo en un sitio.
"""
from django.contrib import admin
from django.utils.html import format_html

from ..models import (
    BloqueoFecha,
    Extra,
    FotoVehiculo,
    Mantenimiento,
    RangoPrecio,
    TemporadaPrecio,
    Vehiculo,
)


class FotoVehiculoInline(admin.TabularInline):
    model = FotoVehiculo
    extra = 5  # 5 filas vacías para subir varias fotos de una vez
    fields = ("imagen", "miniatura", "principal", "orden", "titulo")
    readonly_fields = ("miniatura",)

    def miniatura(self, obj):
        if obj and obj.imagen:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:4px;">', obj.imagen.url
            )
        return "—"
    miniatura.short_description = "Vista previa"


class RangoPrecioInline(admin.TabularInline):
    model = RangoPrecio
    extra = 1


class TemporadaPrecioInline(admin.TabularInline):
    model = TemporadaPrecio
    extra = 0


class BloqueoFechaInline(admin.TabularInline):
    model = BloqueoFecha
    extra = 0


class MantenimientoInline(admin.TabularInline):
    model = Mantenimiento
    extra = 0
    fields = ("tipo", "fecha", "fecha_proximo", "km", "coste")


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "matricula", "categoria", "sede", "plazas", "km_actuales", "activo")
    list_filter = ("categoria", "activo", "sede", "combustible", "cambio")
    search_fields = ("nombre", "matricula", "marca", "modelo")
    prepopulated_fields = {"slug": ("nombre",)}
    filter_horizontal = ("extras",)
    inlines = [
        FotoVehiculoInline,
        RangoPrecioInline,
        TemporadaPrecioInline,
        BloqueoFechaInline,
        MantenimientoInline,
    ]
    fieldsets = (
        ("Identificación", {
            "fields": ("nombre", "slug", "matricula", "marca", "modelo", "anio", "categoria"),
        }),
        ("Características", {
            "fields": ("plazas", "puertas", "combustible", "cambio",
                       "capacidad_carga", "descripcion"),
        }),
        ("Operativa", {
            "fields": ("sede", "fianza", "km_actuales", "activo", "extras"),
        }),
    )


@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "tipo_cobro", "activo")
    list_filter = ("tipo_cobro", "activo")
    search_fields = ("nombre",)


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo", "fecha", "fecha_proximo", "km", "coste")
    list_filter = ("tipo", "fecha")
    search_fields = ("vehiculo__nombre", "vehiculo__matricula")
    date_hierarchy = "fecha"