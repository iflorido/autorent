"""
core/models.py — Configuración de AutoRent.

Dos modelos singleton (siempre pk=1) editables desde el admin:
  - SiteConfig:  datos de empresa, contacto, banco para transferencias,
                 y colores de marca para rebrandizar el frontend.
  - EmailConfig: servidor SMTP, leído dinámicamente por el backend de correo.

El patrón singleton (forzar pk=1 en save + load()) permite que cada
despliegue de cliente tenga UNA configuración, editable sin tocar código.
"""
from django.db import models


class SingletonModel(models.Model):
    """Base abstracta: fuerza que solo exista una fila (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteConfig(SingletonModel):
    """Datos de la empresa y de marca. Uno por despliegue/cliente."""

    # --- Identidad de la empresa ---
    nombre = models.CharField(
        max_length=200, default="AutoRent", verbose_name="Nombre comercial"
    )
    razon_social = models.CharField(
        max_length=200, blank=True, verbose_name="Razón social"
    )
    nif = models.CharField(max_length=20, blank=True, verbose_name="NIF/CIF")

    # --- Dirección ---
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    poblacion = models.CharField(max_length=100, blank=True, verbose_name="Población")
    cp = models.CharField(max_length=10, blank=True, verbose_name="Código postal")
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Provincia")

    # --- Contacto ---
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email de contacto")
    web = models.URLField(blank=True, verbose_name="Sitio web")

    # --- Datos bancarios (para reservas pagadas por transferencia) ---
    banco_titular = models.CharField(
        max_length=200, blank=True, verbose_name="Titular de la cuenta"
    )
    banco_iban = models.CharField(max_length=34, blank=True, verbose_name="IBAN")
    banco_bic = models.CharField(max_length=11, blank=True, verbose_name="BIC/SWIFT")

    # --- Marca (colores del frontend, expuestos vía API para rebrandizar) ---
    logo = models.ImageField(
        upload_to="branding/", blank=True, null=True, verbose_name="Logo"
    )
    color_primary = models.CharField(
        max_length=7, default="#1c3042", verbose_name="Color primario",
        help_text="Hex, ej: #1c3042",
    )
    color_accent = models.CharField(
        max_length=7, default="#0891b3", verbose_name="Color de acento",
        help_text="Hex, ej: #0891b3",
    )

    class Meta:
        verbose_name = "Configuración de empresa"
        verbose_name_plural = "Configuración de empresa"

    def __str__(self):
        return f"Configuración: {self.nombre}"


class EmailConfig(SingletonModel):
    """Servidor SMTP. Lo lee dinámicamente core.backends.ConfiguredEmailBackend."""

    email_host = models.CharField(
        max_length=100, default="smtp.ejemplo.com", verbose_name="Servidor SMTP"
    )
    email_port = models.IntegerField(default=587, verbose_name="Puerto")
    email_host_user = models.CharField(
        max_length=100, blank=True, verbose_name="Usuario"
    )
    email_host_password = models.CharField(
        max_length=200, blank=True, verbose_name="Contraseña"
    )
    email_use_tls = models.BooleanField(default=True, verbose_name="Usar TLS")
    email_use_ssl = models.BooleanField(default=False, verbose_name="Usar SSL")
    email_from_default = models.CharField(
        max_length=200,
        default="AutoRent <reservas@autorent.automaworks.es>",
        verbose_name="Remitente por defecto (FROM)",
    )
    email_dns_workaround = models.CharField(
        max_length=100, blank=True, verbose_name="Fix DNS (opcional)",
        help_text="Si el envío falla por DNS, pon aquí tu dominio (ej: automaworks.es).",
    )

    class Meta:
        verbose_name = "Configuración SMTP"
        verbose_name_plural = "Configuración SMTP"

    def __str__(self):
        return f"SMTP: {self.email_host}:{self.email_port}"