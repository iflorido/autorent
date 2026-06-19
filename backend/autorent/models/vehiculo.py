"""
autorent/models/vehiculo.py — Bloque de flota y precios.

Vehiculo es el núcleo. De él cuelgan:
  - FotoVehiculo    : galería (una marcada como principal)
  - RangoPrecio     : tramos de precio escalonado por nº de días
  - TemporadaPrecio : ajuste de precio por época del año
  - Extra           : complementos (seguros, GPS, silla...) — M2M con Vehiculo
  - BloqueoFecha    : fechas no disponibles que no provienen de una reserva
  - Mantenimiento   : ITV, revisiones, etc.
"""
from django.core.validators import MinValueValidator
from django.db import models


class Vehiculo(models.Model):
    class Categoria(models.TextChoices):
        TURISMO = "turismo", "Turismo"
        FURGONETA = "furgoneta", "Furgoneta"
        CAMPER = "camper", "Camper"
        INDUSTRIAL = "industrial", "Industrial"
        MOTO = "moto", "Moto"

    class Combustible(models.TextChoices):
        GASOLINA = "gasolina", "Gasolina"
        DIESEL = "diesel", "Diésel"
        ELECTRICO = "electrico", "Eléctrico"
        HIBRIDO = "hibrido", "Híbrido"

    class Cambio(models.TextChoices):
        MANUAL = "manual", "Manual"
        AUTOMATICO = "automatico", "Automático"

    # --- Identificación ---
    nombre = models.CharField(
        max_length=120, verbose_name="Nombre comercial",
        help_text="Ej: Volkswagen California 2022",
    )
    matricula = models.CharField(max_length=15, unique=True, verbose_name="Matrícula")
    marca = models.CharField(max_length=60, verbose_name="Marca")
    modelo = models.CharField(max_length=60, verbose_name="Modelo")
    anio = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año")
    categoria = models.CharField(
        max_length=20, choices=Categoria.choices,
        default=Categoria.FURGONETA, verbose_name="Categoría",
    )

    # --- Características (para la ficha del frontend) ---
    plazas = models.PositiveSmallIntegerField(default=5, verbose_name="Plazas")
    puertas = models.PositiveSmallIntegerField(default=4, verbose_name="Puertas")
    combustible = models.CharField(
        max_length=20, choices=Combustible.choices,
        default=Combustible.DIESEL, verbose_name="Combustible",
    )
    cambio = models.CharField(
        max_length=20, choices=Cambio.choices,
        default=Cambio.MANUAL, verbose_name="Cambio",
    )
    capacidad_carga = models.CharField(
        max_length=60, blank=True, verbose_name="Capacidad de carga",
        help_text="Texto libre, ej: '3,2 m³ / 1000 kg'",
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    # --- Operativa ---
    fianza = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        validators=[MinValueValidator(0)], verbose_name="Fianza/depósito (€)",
    )
    km_actuales = models.PositiveIntegerField(
        default=0, verbose_name="Kilómetros actuales",
    )
    activo = models.BooleanField(
        default=True, verbose_name="Activo",
        help_text="Si se desmarca, no aparece en la web ni admite reservas.",
    )

    extras = models.ManyToManyField(
        "autorent.Extra", blank=True, related_name="vehiculos",
        verbose_name="Extras disponibles",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.matricula})"

    @property
    def foto_principal(self):
        return self.fotos.filter(principal=True).first() or self.fotos.first()


class FotoVehiculo(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="fotos",
        verbose_name="Vehículo",
    )
    imagen = models.ImageField(upload_to="vehiculos/", verbose_name="Imagen")
    principal = models.BooleanField(default=False, verbose_name="Principal")
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")
    titulo = models.CharField(max_length=120, blank=True, verbose_name="Título")

    class Meta:
        verbose_name = "Foto de vehículo"
        verbose_name_plural = "Fotos de vehículos"
        ordering = ["orden", "id"]

    def __str__(self):
        return f"Foto de {self.vehiculo.nombre}"

    def save(self, *args, **kwargs):
        # Solo una principal por vehículo: al marcar esta, desmarca las demás.
        if self.principal:
            FotoVehiculo.objects.filter(
                vehiculo=self.vehiculo, principal=True
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


class RangoPrecio(models.Model):
    """Tramo de precio escalonado. Ej: 1-2 días=50€/día, 3-6=40€, 7-29=35€."""

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="rangos_precio",
        verbose_name="Vehículo",
    )
    dias_min = models.PositiveSmallIntegerField(verbose_name="Días mínimo")
    dias_max = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Días máximo",
        help_text="Vacío = sin límite superior.",
    )
    precio_dia = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)], verbose_name="Precio por día (€)",
    )

    class Meta:
        verbose_name = "Rango de precio"
        verbose_name_plural = "Rangos de precio"
        ordering = ["vehiculo", "dias_min"]

    def __str__(self):
        tope = self.dias_max or "∞"
        return f"{self.vehiculo.nombre}: {self.dias_min}-{tope} días → {self.precio_dia}€/día"


class TemporadaPrecio(models.Model):
    """Ajuste de precio por época del año (temporada alta/baja)."""

    class TipoAjuste(models.TextChoices):
        MULTIPLICADOR = "multiplicador", "Multiplicador (ej: 1.30 = +30%)"
        PRECIO_FIJO = "precio_fijo", "Precio fijo por día (€)"

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="temporadas",
        verbose_name="Vehículo",
    )
    nombre = models.CharField(
        max_length=80, verbose_name="Nombre", help_text="Ej: Temporada alta verano",
    )
    fecha_inicio = models.DateField(verbose_name="Desde")
    fecha_fin = models.DateField(verbose_name="Hasta")
    tipo_ajuste = models.CharField(
        max_length=20, choices=TipoAjuste.choices,
        default=TipoAjuste.MULTIPLICADOR, verbose_name="Tipo de ajuste",
    )
    valor = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Valor",
        help_text="Si es multiplicador: 1.30. Si es precio fijo: el €/día.",
    )

    class Meta:
        verbose_name = "Temporada de precio"
        verbose_name_plural = "Temporadas de precio"
        ordering = ["vehiculo", "fecha_inicio"]

    def __str__(self):
        return f"{self.vehiculo.nombre}: {self.nombre} ({self.fecha_inicio} a {self.fecha_fin})"


class Extra(models.Model):
    """Complemento contratable: seguro, GPS, silla infantil, etc."""

    class TipoCobro(models.TextChoices):
        POR_DIA = "por_dia", "Por día"
        UNICO = "unico", "Pago único"

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    precio = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)], verbose_name="Precio (€)",
    )
    tipo_cobro = models.CharField(
        max_length=10, choices=TipoCobro.choices,
        default=TipoCobro.POR_DIA, verbose_name="Tipo de cobro",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Extra"
        verbose_name_plural = "Extras"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.precio}€ {self.get_tipo_cobro_display().lower()})"


class BloqueoFecha(models.Model):
    """Fechas no disponibles que NO vienen de una reserva (taller, uso interno...)."""

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="bloqueos",
        verbose_name="Vehículo",
    )
    fecha_inicio = models.DateField(verbose_name="Desde")
    fecha_fin = models.DateField(verbose_name="Hasta")
    motivo = models.CharField(max_length=255, blank=True, verbose_name="Motivo")

    class Meta:
        verbose_name = "Bloqueo de fechas"
        verbose_name_plural = "Bloqueos de fechas"
        ordering = ["vehiculo", "fecha_inicio"]

    def __str__(self):
        return f"{self.vehiculo.nombre}: {self.fecha_inicio} a {self.fecha_fin}"


class Mantenimiento(models.Model):
    """Registro de mantenimiento: ITV, revisiones, neumáticos, etc."""

    class Tipo(models.TextChoices):
        ITV = "itv", "ITV"
        REVISION = "revision", "Revisión"
        NEUMATICOS = "neumaticos", "Neumáticos"
        SEGURO = "seguro", "Seguro"
        REPARACION = "reparacion", "Reparación"
        OTRO = "otro", "Otro"

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="mantenimientos",
        verbose_name="Vehículo",
    )
    tipo = models.CharField(
        max_length=20, choices=Tipo.choices, default=Tipo.REVISION,
        verbose_name="Tipo",
    )
    fecha = models.DateField(verbose_name="Fecha")
    fecha_proximo = models.DateField(
        blank=True, null=True, verbose_name="Próximo vencimiento",
        help_text="Para alertas (ej: próxima ITV).",
    )
    km = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Km en el momento",
    )
    coste = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name="Coste (€)",
    )
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.vehiculo.nombre} — {self.get_tipo_display()} ({self.fecha})"