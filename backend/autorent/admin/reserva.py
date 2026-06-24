"""
autorent/admin/reserva.py — Admin del bloque Cliente + Reserva.

La ficha de Reserva integra sus extras, documentos y pagos como inlines,
y recalcula automáticamente el desglose económico al guardar.
"""
from django.contrib import admin

from ..models import (
    Cancelacion,
    Cliente,
    ConductorAdicional,
    DocumentoReserva,
    Factura,
    Pago,
    Reserva,
    ReservaExtra,
    TokenSubida,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "nif", "email", "telefono", "carnet_caducidad")
    search_fields = ("nombre", "apellidos", "nif", "email", "telefono")
    fieldsets = (
        ("Datos personales", {
            "fields": ("usuario", "nombre", "apellidos", "nif", "fecha_nacimiento"),
        }),
        ("Contacto", {"fields": ("email", "telefono")}),
        ("Dirección", {"fields": ("direccion", "poblacion", "cp", "provincia", "pais")}),
        ("Carnet de conducir", {"fields": ("carnet_numero", "carnet_caducidad")}),
        ("Interno", {"fields": ("notas",)}),
    )


class ReservaExtraInline(admin.TabularInline):
    model = ReservaExtra
    extra = 0
    fields = ("extra", "cantidad", "precio_congelado", "tipo_cobro_congelado")


class ConductorAdicionalInline(admin.TabularInline):
    model = ConductorAdicional
    extra = 0
    fields = ("nombre", "apellidos", "nif", "fecha_nacimiento", "carnet_numero", "carnet_caducidad")


class DocumentoReservaInline(admin.TabularInline):
    model = DocumentoReserva
    extra = 0
    fields = ("tipo", "conductor", "archivo", "ver_seguro", "estado", "notas_revision", "subido_at")
    readonly_fields = ("subido_at", "ver_seguro")

    def ver_seguro(self, obj):
        """Enlace a la vista protegida (no a la URL pública de media)."""
        from django.urls import reverse
        from django.utils.html import format_html
        if not obj.pk or not obj.archivo:
            return "—"
        url = reverse("autorent:servir-documento", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Ver documento 🔒</a>', url)
    ver_seguro.short_description = "Ver (seguro)"


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    fields = ("metodo", "importe", "estado", "referencia", "fecha")
    readonly_fields = ("fecha",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "localizador", "cliente", "vehiculo", "fecha_inicio",
        "fecha_fin", "estado", "total",
    )
    list_filter = ("estado", "metodo_pago", "fecha_inicio")
    search_fields = (
        "localizador", "cliente__nombre", "cliente__apellidos",
        "cliente__nif", "vehiculo__nombre", "vehiculo__matricula",
    )
    date_hierarchy = "fecha_inicio"
    readonly_fields = (
        "localizador", "num_dias", "precio_dia_base", "subtotal_vehiculo",
        "subtotal_extras", "total", "created_at", "updated_at",
    )
    inlines = [ReservaExtraInline, ConductorAdicionalInline, DocumentoReservaInline, PagoInline]
    fieldsets = (
        ("Reserva", {
            "fields": ("localizador", "cliente", "vehiculo",
                       "fecha_inicio", "fecha_fin", "estado", "metodo_pago"),
        }),
        ("Desglose económico (calculado)", {
            "fields": ("num_dias", "precio_dia_base", "subtotal_vehiculo",
                       "subtotal_extras", "fianza", "total"),
            "description": "Se recalcula automáticamente al guardar.",
        }),
        ("Notas y fechas", {
            "fields": ("notas", "created_at", "updated_at"),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Guardar primero para tener pk, luego recalcular con extras incluidos.
        super().save_model(request, obj, form, change)
        obj.recalcular_totales()

    def save_related(self, request, form, formsets, change):
        # Tras guardar los inlines (extras), recalcular de nuevo el total.
        super().save_related(request, form, formsets, change)
        form.instance.recalcular_totales()

    actions = ["rechazar_documentacion"]

    @admin.action(description="Rechazar documentación y reenviar enlace al cliente")
    def rechazar_documentacion(self, request, queryset):
        """Marca los documentos como rechazados, genera un token nuevo y avisa."""
        from ..models import DocumentoReserva, TokenSubida
        from ..notificaciones import enviar_correo_documentos_rechazados
        enviadas = 0
        for reserva in queryset:
            reserva.documentos.update(estado=DocumentoReserva.Estado.RECHAZADO)
            token = TokenSubida.generar(reserva, dias_validez=7)
            if enviar_correo_documentos_rechazados(reserva, token):
                enviadas += 1
        self.message_user(
            request,
            f"Documentación rechazada en {queryset.count()} reserva(s). "
            f"Correo de nuevo enlace enviado: {enviadas}.",
        )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("reserva", "metodo", "importe", "estado", "fecha")
    list_filter = ("estado", "metodo")
    search_fields = ("reserva__localizador", "referencia")


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero", "reserva", "fecha_emision", "total")
    search_fields = ("numero", "reserva__localizador")
    date_hierarchy = "fecha_emision"


@admin.register(Cancelacion)
class CancelacionAdmin(admin.ModelAdmin):
    list_display = ("reserva", "fecha", "importe_reembolsado")
    search_fields = ("reserva__localizador",)