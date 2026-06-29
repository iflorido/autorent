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
    ContratoReserva,
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
    fields = ("tipo", "conductor", "ver_seguro", "estado", "notas_revision", "subido_at")
    readonly_fields = ("subido_at", "ver_seguro")

    def has_add_permission(self, request, obj=None):
        # Los documentos los sube el cliente (enlace/asistente), no el admin.
        return False

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


class ContratoReservaInline(admin.StackedInline):
    model = ContratoReserva
    extra = 0
    can_delete = False
    fields = ("descargar", "generado_at", "enviado_at", "hash_sha256")
    readonly_fields = ("descargar", "generado_at", "enviado_at", "hash_sha256")

    def has_add_permission(self, request, obj=None):
        return False  # se crea automáticamente al confirmar

    def descargar(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if not obj.pk or not obj.archivo:
            return "Aún no generado"
        url = reverse("autorent:servir-contrato", args=[obj.reserva_id])
        return format_html('<a href="{}" target="_blank">Descargar contrato 🔒</a>', url)
    descargar.short_description = "Contrato"


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
        "subtotal_extras", "suplemento_fuera_horario", "total",
        "created_at", "updated_at",
    )
    inlines = [ReservaExtraInline, ConductorAdicionalInline, DocumentoReservaInline, PagoInline, ContratoReservaInline]
    fieldsets = (
        ("Reserva", {
            "fields": ("localizador", "cliente", "vehiculo",
                       "fecha_inicio", "fecha_fin", "estado", "metodo_pago"),
        }),
        ("Recogida y entrega", {
            "fields": ("hora_recogida", "sede_recogida", "hora_entrega", "sede_entrega"),
            "description": "Si una hora cae fuera del horario de su sede, al guardar "
                           "se recalcula el suplemento fuera de horario.",
        }),
        ("Desglose económico (calculado)", {
            "fields": ("num_dias", "precio_dia_base", "subtotal_vehiculo",
                       "subtotal_extras", "suplemento_fuera_horario", "fianza", "total"),
            "description": "Se recalcula automáticamente al guardar.",
        }),
        ("Notas y fechas", {
            "fields": ("notas", "created_at", "updated_at"),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Detectar si la reserva pasa a "confirmada" en este guardado.
        paso_a_confirmada = False
        if change and "estado" in form.changed_data:
            from ..models import Reserva
            if obj.estado == Reserva.Estado.CONFIRMADA:
                paso_a_confirmada = True

        super().save_model(request, obj, form, change)
        obj.recalcular_totales()

        # Al confirmar, generar el contrato en segundo plano (Celery).
        if paso_a_confirmada:
            from ..tasks import generar_contrato_reserva
            generar_contrato_reserva.delay(obj.pk)
            self.message_user(
                request,
                "Reserva confirmada. El contrato se está generando; "
                "actualiza en unos segundos para verlo en la sección Contrato.",
            )

    def save_related(self, request, form, formsets, change):
        # Tras guardar los inlines (extras y documentos), recalcular el total.
        super().save_related(request, form, formsets, change)
        reserva = form.instance
        reserva.recalcular_totales()
        # Revisar el estado de la documentación y avisar al cliente si cambió.
        self._notificar_estado_documentacion(request, reserva)

    def _notificar_estado_documentacion(self, request, reserva):
        """Envía el correo adecuado al cliente según el estado de los documentos.

        Solo envía si el estado cambió respecto al último notificado, para no
        repetir correos al guardar la ficha varias veces.
          - todos aprobados  -> correo de aprobación.
          - alguno rechazado -> correo de rechazo con motivos + nuevo enlace.
          - pendiente / sin documentos -> no se avisa.
        """
        from ..models import TokenSubida
        from ..notificaciones import (
            enviar_correo_documentos_aprobados,
            enviar_correo_documentos_rechazados,
            _motivos_rechazo,
        )

        estado = reserva.estado_documentacion()  # sin_documentos|pendiente|rechazada|aprobada
        if estado in ("sin_documentos", "pendiente"):
            return  # nada que notificar todavía

        # Evitar reenvíos: solo si cambia respecto a lo ya notificado.
        if reserva.doc_estado_notificado == estado:
            return

        if estado == "aprobada":
            if enviar_correo_documentos_aprobados(reserva):
                self.message_user(request, "Cliente avisado: documentación aprobada.")
        elif estado == "rechazada":
            # Nuevo enlace para volver a subir toda la documentación.
            token = TokenSubida.generar(reserva, dias_validez=7)
            motivo = _motivos_rechazo(reserva)
            if enviar_correo_documentos_rechazados(reserva, token, motivo=motivo):
                self.message_user(
                    request,
                    "Cliente avisado: documentación rechazada, se envió un nuevo enlace.",
                )

        # Registrar el estado notificado para no repetir el correo.
        reserva.doc_estado_notificado = estado
        reserva.save(update_fields=["doc_estado_notificado"])

    actions = ["regenerar_contrato", "enviar_contrato"]

    @admin.action(description="Regenerar contrato PDF")
    def regenerar_contrato(self, request, queryset):
        from ..tasks import generar_contrato_reserva
        for reserva in queryset:
            generar_contrato_reserva.delay(reserva.pk)
        self.message_user(
            request,
            f"Generando contrato de {queryset.count()} reserva(s). "
            "Actualiza en unos segundos.",
        )

    @admin.action(description="Enviar contrato al cliente por correo")
    def enviar_contrato(self, request, queryset):
        from django.utils import timezone
        from ..notificaciones import enviar_contrato_cliente
        enviados = 0
        sin_contrato = 0
        for reserva in queryset:
            contrato = getattr(reserva, "contrato", None)
            if not contrato or not contrato.archivo:
                sin_contrato += 1
                continue
            if enviar_contrato_cliente(reserva):
                contrato.enviado_at = timezone.now()
                contrato.save(update_fields=["enviado_at"])
                enviados += 1
        msg = f"Contrato enviado a {enviados} cliente(s)."
        if sin_contrato:
            msg += f" {sin_contrato} sin contrato generado (genéralo primero)."
        self.message_user(request, msg)


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