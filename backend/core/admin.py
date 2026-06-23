"""
core/admin.py — Admin de SiteConfig y EmailConfig.

EmailConfig incluye un botón de prueba de envío en la propia ficha para
verificar la configuración SMTP sin salir del admin.
"""
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import EmailConfig, FrontendConfig, FRONTEND_DEFAULTS, Sede, SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nif", "email", "telefono")
    fieldsets = (
        ("Identidad", {"fields": ("nombre", "razon_social", "nif", "logo")}),
        ("Dirección", {"fields": ("direccion", "poblacion", "cp", "provincia")}),
        ("Contacto", {"fields": ("telefono", "email", "web")}),
        ("Datos bancarios (transferencias)", {
            "fields": ("banco_titular", "banco_iban", "banco_bic"),
            "description": "Se mostrarán al cliente que elija pago por transferencia.",
        }),
        ("Marca (colores del frontend)", {
            "fields": ("color_primary", "color_accent"),
            "description": "Se exponen vía API para rebrandizar el frontend.",
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class EmailConfigForm(forms.ModelForm):
    class Meta:
        model = EmailConfig
        fields = "__all__"
        widgets = {
            "email_host_password": forms.PasswordInput(render_value=True),
        }


@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    form = EmailConfigForm
    list_display = ("email_host", "email_port", "email_host_user", "email_use_tls", "boton_prueba")
    readonly_fields = ("bloque_prueba_correo",)
    fieldsets = (
        ("Servidor SMTP", {
            "fields": ("email_host", "email_port", "email_host_user", "email_host_password"),
        }),
        ("Seguridad", {"fields": ("email_use_tls", "email_use_ssl")}),
        ("Remitente", {"fields": ("email_from_default",)}),
        ("Fix DNS (opcional)", {
            "fields": ("email_dns_workaround",),
            "classes": ("collapse",),
        }),
        ("Prueba de envío", {
            "fields": ("bloque_prueba_correo",),
            "description": "Envía un correo de prueba para verificar la configuración.",
        }),
    )

    def has_add_permission(self, request):
        return not EmailConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def bloque_prueba_correo(self, obj):
        if not obj or not obj.pk:
            return "— Guarda la configuración primero para poder enviar una prueba."

        # Enlace (no form anidado: dentro del form del admin un <form>
        # interno se aplana y acabaría guardando en vez de enviar la prueba).
        url = reverse("admin:core_email_prueba", args=[obj.pk])
        return format_html(
            '<a href="{}" style="display:inline-block;padding:9px 20px;background:#0891b3;'
            'color:#fff;border-radius:6px;font-size:.85rem;font-weight:600;text-decoration:none;">'
            'Abrir página de prueba de envío</a>'
            '<p style="margin:8px 0 0;font-size:.78rem;color:#6b7280;">'
            'Guarda primero los cambios; luego abre la página de prueba e indica el email destino.</p>',
            url,
        )
    bloque_prueba_correo.short_description = "Enviar correo de prueba"

    def boton_prueba(self, obj):
        url = reverse("admin:core_email_prueba", args=[obj.pk])
        return format_html(
            '<a href="{}" style="background:#0891b3;color:#fff;padding:3px 10px;'
            'border-radius:4px;font-size:.75rem;font-weight:600;text-decoration:none;">Probar</a>',
            url,
        )
    boton_prueba.short_description = "Prueba"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:email_id>/prueba/",
                self.admin_site.admin_view(self.vista_prueba_correo),
                name="core_email_prueba",
            ),
        ]
        return custom + urls

    def vista_prueba_correo(self, request, email_id):
        obj = EmailConfig.objects.get(pk=email_id)
        url_cambio = reverse("admin:core_emailconfig_change", args=[email_id])

        # GET: mostrar una página propia con su formulario (no anidado en el admin).
        if request.method != "POST":
            from django.middleware.csrf import get_token
            from django.shortcuts import render

            ctx = {
                **self.admin_site.each_context(request),
                "title": "Prueba de envío SMTP",
                "obj": obj,
                "url_cambio": url_cambio,
                "csrf_token": get_token(request),
            }
            return render(request, "admin/core/email_prueba.html", ctx)

        email_destino = request.POST.get("email_destino", "").strip()
        try:
            validate_email(email_destino)
        except ValidationError:
            messages.error(request, f'Email no válido: "{email_destino}"')
            return HttpResponseRedirect(url_cambio)

        try:
            connection = get_connection(
                backend="core.backends.ConfiguredEmailBackend",
                fail_silently=False,
            )
            asunto = "Prueba de correo — AutoRent"
            texto = (
                "Correo de prueba enviado desde AutoRent.\n"
                f"Servidor: {obj.email_host}:{obj.email_port}\n"
                f"Usuario: {obj.email_host_user}\n"
                "Si recibes este mensaje, la configuración SMTP es correcta."
            )
            html = (
                '<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;">'
                '<div style="background:#1c3042;padding:24px;text-align:center;border-radius:12px 12px 0 0;">'
                '<h1 style="margin:0;color:#fff;font-size:20px;">AutoRent</h1></div>'
                '<div style="padding:28px;background:#fff;border:1px solid #e5e7eb;border-top:none;'
                'border-radius:0 0 12px 12px;">'
                '<h2 style="margin:0 0 12px;color:#111827;font-size:17px;">Prueba de correo correcta</h2>'
                '<p style="color:#4b5563;font-size:14px;line-height:1.6;">'
                "Tu configuración SMTP está funcionando correctamente.</p>"
                f'<p style="color:#6b7280;font-size:13px;">Servidor: {obj.email_host}:{obj.email_port}<br>'
                f"Usuario: {obj.email_host_user}</p></div></div>"
            )
            msg = EmailMultiAlternatives(
                subject=asunto, body=texto,
                from_email=obj.email_from_default, to=[email_destino],
                connection=connection,
            )
            msg.attach_alternative(html, "text/html")
            msg.send()
            messages.success(request, f"Correo de prueba enviado a {email_destino}.")
        except Exception as exc:
            messages.error(request, f"Error al enviar el correo: {exc}")

        return HttpResponseRedirect(url_cambio)


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "poblacion", "provincia", "telefono", "activa", "orden")
    list_filter = ("activa", "provincia")
    search_fields = ("nombre", "poblacion", "direccion")
    prepopulated_fields = {"slug": ("nombre",)}
    fieldsets = (
        ("Identificación", {"fields": ("nombre", "slug", "activa", "orden")}),
        ("Dirección", {"fields": ("direccion", "poblacion", "cp", "provincia", "pais")}),
        ("Geolocalización", {"fields": ("latitud", "longitud")}),
        ("Contacto", {"fields": ("telefono", "email", "horario")}),
    )


class RestablecerWidget(forms.TextInput):
    """Input de texto con un botón 'Restablecer' que pone el valor por defecto."""

    def __init__(self, default_value="", *args, **kwargs):
        self.default_value = default_value
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        # Muestra una pastilla con el valor por defecto y un botón restablecer.
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
            '{}'
            '<button type="button" class="ar-reset" data-default="{}" '
            'style="padding:4px 10px;border:1px solid #cbd5e1;border-radius:6px;'
            'background:#f8fafc;font-size:.75rem;cursor:pointer;white-space:nowrap;">'
            '↺ Restablecer</button>'
            '<code style="font-size:.7rem;color:#94a3b8;">{}</code>'
            '</div>',
            input_html, self.default_value, self.default_value,
        )


class FrontendConfigForm(forms.ModelForm):
    class Meta:
        model = FrontendConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asignar a cada campo de color su widget con su valor por defecto.
        for campo, default in FRONTEND_DEFAULTS.items():
            if campo in self.fields and campo not in ("font_display", "font_body"):
                self.fields[campo].widget = RestablecerWidget(default_value=default)


@admin.register(FrontendConfig)
class FrontendConfigAdmin(admin.ModelAdmin):
    form = FrontendConfigForm

    fieldsets = (
        ("Fondo y superficies", {
            "fields": ("bg", "bg_2", "surface", "surface_2", "surface_3"),
        }),
        ("Bordes", {"fields": ("border", "border_2")}),
        ("Texto", {"fields": ("text", "text_2")}),
        ("Acento", {"fields": ("accent", "accent_dim", "accent_glow")}),
        ("Sombra", {"fields": ("shadow",)}),
        ("Tipografía", {"fields": ("font_display", "font_body")}),
    )

    def has_add_permission(self, request):
        return not FrontendConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = FrontendConfig.load()
        from django.urls import reverse
        url = reverse("admin:core_frontendconfig_change", args=[obj.pk])
        return HttpResponseRedirect(url)

    class Media:
        js = ("core/js/frontend_reset.js",)