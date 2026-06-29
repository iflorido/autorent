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


class Sede(models.Model):
    """Localización física donde se recogen/entregan los vehículos.

    Multi-sede: de momento habrá una, pero el modelo permite varias para
    que en el futuro se pueda recoger en una sede y entregar en otra.
    """
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    slug = models.SlugField(max_length=140, unique=True, verbose_name="Slug")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    # Dirección
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    poblacion = models.CharField(max_length=100, blank=True, verbose_name="Población")
    cp = models.CharField(max_length=10, blank=True, verbose_name="Código postal")
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    pais = models.CharField(max_length=60, default="España", verbose_name="País")

    # Geolocalización (para mapa en el frontend)
    latitud = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Latitud",
    )
    longitud = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Longitud",
    )

    # Contacto y horario
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    horario = models.TextField(blank=True, verbose_name="Horario", help_text="Texto libre.")

    # Suplemento por recogida/entrega fuera del horario comercial de esta sede.
    suplemento_fuera_horario = models.DecimalField(
        max_digits=7, decimal_places=2, default=0,
        verbose_name="Suplemento fuera de horario (€)",
        help_text="Se aplica automáticamente si la hora elegida cae fuera de las "
                  "franjas horarias de la sede. 0 = no se permite/cobra.",
    )

    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre

    def hora_dentro_de_horario(self, fecha, hora):
        """¿La 'hora' de un día concreto cae dentro de alguna franja de la sede?

        Si la sede no tiene franjas definidas para ese día de la semana, se
        considera FUERA de horario (no abre ese día). Devuelve True/False.
        """
        dia = fecha.weekday()  # 0 = lunes ... 6 = domingo
        franjas = self.franjas.filter(dia_semana=dia)
        for f in franjas:
            if f.hora_apertura <= hora <= f.hora_cierre:
                return True
        return False


class FranjaHorariaSede(models.Model):
    """Una franja de horario comercial de una sede, por día de la semana.

    Permite horario partido (varias franjas el mismo día) y días distintos.
    Un día sin franjas se considera cerrado.
    """
    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    sede = models.ForeignKey(
        Sede, on_delete=models.CASCADE, related_name="franjas", verbose_name="Sede",
    )
    dia_semana = models.IntegerField(choices=DiaSemana.choices, verbose_name="Día")
    hora_apertura = models.TimeField(verbose_name="Apertura")
    hora_cierre = models.TimeField(verbose_name="Cierre")

    class Meta:
        verbose_name = "Franja horaria"
        verbose_name_plural = "Franjas horarias"
        ordering = ["sede", "dia_semana", "hora_apertura"]

    def __str__(self):
        return (f"{self.sede.nombre} · {self.get_dia_semana_display()} "
                f"{self.hora_apertura:%H:%M}-{self.hora_cierre:%H:%M}")


# Valores por defecto del tema (la paleta "general" de iflorido.es, versión light).
# Se usan como default de cada campo y para el botón "restablecer".
FRONTEND_DEFAULTS = {
    "bg": "#f5f7fb",
    "bg_2": "#ffffff",
    "surface": "rgba(15, 23, 42, 0.028)",
    "surface_2": "rgba(15, 23, 42, 0.048)",
    "surface_3": "rgba(15, 23, 42, 0.07)",
    "border": "rgba(15, 23, 42, 0.07)",
    "border_2": "rgba(15, 23, 42, 0.12)",
    "text": "#0f172a",
    "text_2": "#4b5c78",
    "accent": "#0891b2",
    "accent_dim": "rgba(8, 145, 178, 0.08)",
    "accent_glow": "rgba(8, 145, 178, 0.05)",
    "shadow": "0 20px 50px rgba(15, 23, 42, 0.07)",
    "font_display": "Cabin",
    "font_body": "DM Sans",
}

# Fuentes disponibles (Google Fonts fáciles de cargar).
FUENTES_CHOICES = [
    ("Cabin", "Cabin"),
    ("DM Sans", "DM Sans"),
    ("Oxygen", "Oxygen"),
    ("Inter", "Inter"),
    ("Poppins", "Poppins"),
    ("Montserrat", "Montserrat"),
    ("Work Sans", "Work Sans"),
    ("Nunito", "Nunito"),
    ("Rubik", "Rubik"),
    ("Manrope", "Manrope"),
]


class FrontendConfig(SingletonModel):
    """Tokens de color y tipografía del frontend, editables desde el admin.

    Permite rebrandizar el frontend (colores + fuentes) por cliente sin tocar
    código. El frontend los lee de un endpoint y los aplica como variables CSS.
    """
    bg = models.CharField("--bg", max_length=40, default=FRONTEND_DEFAULTS["bg"])
    bg_2 = models.CharField("--bg-2", max_length=40, default=FRONTEND_DEFAULTS["bg_2"])
    surface = models.CharField("--surface", max_length=40, default=FRONTEND_DEFAULTS["surface"])
    surface_2 = models.CharField("--surface-2", max_length=40, default=FRONTEND_DEFAULTS["surface_2"])
    surface_3 = models.CharField("--surface-3", max_length=40, default=FRONTEND_DEFAULTS["surface_3"])
    border = models.CharField("--border", max_length=40, default=FRONTEND_DEFAULTS["border"])
    border_2 = models.CharField("--border-2", max_length=40, default=FRONTEND_DEFAULTS["border_2"])
    text = models.CharField("--text", max_length=40, default=FRONTEND_DEFAULTS["text"])
    text_2 = models.CharField("--text-2", max_length=40, default=FRONTEND_DEFAULTS["text_2"])
    accent = models.CharField("--accent", max_length=40, default=FRONTEND_DEFAULTS["accent"])
    accent_dim = models.CharField("--accent-dim", max_length=40, default=FRONTEND_DEFAULTS["accent_dim"])
    accent_glow = models.CharField("--accent-glow", max_length=40, default=FRONTEND_DEFAULTS["accent_glow"])
    shadow = models.CharField("--shadow", max_length=80, default=FRONTEND_DEFAULTS["shadow"])

    font_display = models.CharField(
        "Fuente de títulos (--font-display)", max_length=40,
        choices=FUENTES_CHOICES, default=FRONTEND_DEFAULTS["font_display"],
    )
    font_body = models.CharField(
        "Fuente de texto (--font-body)", max_length=40,
        choices=FUENTES_CHOICES, default=FRONTEND_DEFAULTS["font_body"],
    )

    class Meta:
        verbose_name = "Frontend (colores y fuentes)"
        verbose_name_plural = "Frontend (colores y fuentes)"

    def __str__(self):
        return "Configuración del frontend"

    def as_tokens(self):
        """Devuelve los tokens en el formato que consume el frontend."""
        return {
            "--bg": self.bg,
            "--bg-2": self.bg_2,
            "--surface": self.surface,
            "--surface-2": self.surface_2,
            "--surface-3": self.surface_3,
            "--border": self.border,
            "--border-2": self.border_2,
            "--text": self.text,
            "--text-2": self.text_2,
            "--accent": self.accent,
            "--accent-dim": self.accent_dim,
            "--accent-glow": self.accent_glow,
            "--shadow": self.shadow,
            "--font-display": f'"{self.font_display}", sans-serif',
            "--font-body": f'"{self.font_body}", system-ui, sans-serif',
        }

    @property
    def fuentes_google(self):
        """Lista de familias (sin repetir) para cargar de Google Fonts."""
        return list({self.font_display, self.font_body})