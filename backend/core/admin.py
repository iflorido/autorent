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

from .models import EmailConfig, SiteConfig


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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self._current_request = request
        return super().change_view(request, object_id, form_url, extra_context)

    def bloque_prueba_correo(self, obj):
        if not obj or not obj.pk:
            return "— Guarda la configuración primero para poder enviar una prueba."

        from django.middleware.csrf import get_token

        request = getattr(self, "_current_request", None)
        csrf_token = get_token(request) if request else ""
        url = reverse("admin:core_email_prueba", args=[obj.pk])

        return format_html(
            '<div style="background:#f0f9ff;border:1px solid #bae6fd;'
            'border-left:4px solid #0891b3;border-radius:8px;padding:16px 20px;max-width:560px;">'
            '<form method="post" action="{}" style="display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;">'
            '<input type="hidden" name="csrfmiddlewaretoken" value="{}">'
            '<div style="flex:1;min-width:220px;">'
            '<label style="display:block;font-size:.72rem;font-weight:700;color:#374151;'
            'margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em;">Email destino</label>'
            '<input type="email" name="email_destino" placeholder="tu@email.com" required '
            'style="width:100%;padding:8px 12px;border:1px solid #cbd5e1;border-radius:6px;'
            'font-size:.85rem;box-sizing:border-box;"></div>'
            '<button type="submit" style="padding:8px 18px;background:#0891b3;color:#fff;border:none;'
            'border-radius:6px;font-size:.85rem;font-weight:600;cursor:pointer;white-space:nowrap;">'
            'Enviar prueba</button></form></div>',
            url, csrf_token,
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

        if request.method != "POST":
            return HttpResponseRedirect(url_cambio)

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