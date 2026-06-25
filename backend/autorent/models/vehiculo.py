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


class CategoriaVehiculo(models.Model):
    """Categoría de vehículo, gestionable desde el admin.

    Define el límite de velocidad por defecto y los requisitos de conductor
    (edad mínima y antigüedad de carnet) de los vehículos de esa categoría.
    El 'slug' es el código estable que usa el frontend para filtrar el catálogo.
    """
    slug = models.SlugField(
        max_length=40, unique=True, verbose_name="Código (slug)",
        help_text="Identificador estable para el filtro del catálogo (ej: turismo).",
    )
    nombre = models.CharField(max_length=60, verbose_name="Nombre")
    limite_velocidad = models.PositiveIntegerField(
        default=120, verbose_name="Límite de velocidad por defecto (km/h)",
        help_text="Se aplica a los vehículos de esta categoría que no tengan "
                  "un límite propio.",
    )
    edad_min_conductor = models.PositiveIntegerField(
        default=23, verbose_name="Edad mínima del conductor (años)",
    )
    antiguedad_carnet_min = models.PositiveIntegerField(
        default=2, verbose_name="Antigüedad mínima de carnet (años)",
    )
    orden = models.PositiveIntegerField(
        default=0, verbose_name="Orden",
        help_text="Para ordenar las categorías en listados y filtros.",
    )

    class Meta:
        verbose_name = "Categoría de vehículo"
        verbose_name_plural = "Categorías de vehículo"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


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
    slug = models.SlugField(
        max_length=140, unique=True, blank=True, verbose_name="Slug (URL)",
        help_text="Se genera automáticamente del nombre si se deja vacío.",
    )
    matricula = models.CharField(max_length=15, unique=True, verbose_name="Matrícula")
    marca = models.CharField(max_length=60, verbose_name="Marca")
    modelo = models.CharField(max_length=60, verbose_name="Modelo")
    anio = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año")
    # Categoría como texto (compatibilidad con frontend y filtros existentes).
    categoria = models.CharField(
        max_length=20, choices=Categoria.choices,
        default=Categoria.FURGONETA, verbose_name="Categoría",
    )
    # Categoría como modelo gestionable (fuente de límites y requisitos).
    categoria_obj = models.ForeignKey(
        CategoriaVehiculo, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="vehiculos", verbose_name="Categoría (gestionable)",
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
    limite_velocidad = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Límite de velocidad (km/h)",
        help_text="Para alertas de exceso. Si se deja vacío, se usa el límite "
                  "por defecto de su categoría.",
    )
    activo = models.BooleanField(
        default=True, verbose_name="Activo",
        help_text="Si se desmarca, no aparece en la web ni admite reservas.",
    )
    sede = models.ForeignKey(
        "core.Sede", on_delete=models.SET_NULL, blank=True, null=True,
        related_name="vehiculos", verbose_name="Sede base",
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

    def save(self, *args, **kwargs):
        # Autogenera un slug único a partir del nombre si está vacío.
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.nombre) or "vehiculo"
            slug = base
            n = 2
            while Vehiculo.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug

        # Mantener coherentes los dos campos de categoría:
        #  - si hay categoría gestionable, el texto refleja su slug.
        #  - si solo hay texto, intenta enlazar la categoría gestionable por slug.
        if self.categoria_obj:
            self.categoria = self.categoria_obj.slug
        elif self.categoria:
            try:
                from .vehiculo import CategoriaVehiculo
                self.categoria_obj = CategoriaVehiculo.objects.filter(
                    slug=self.categoria
                ).first()
            except Exception:  # noqa: BLE001
                pass

        super().save(*args, **kwargs)

    @property
    def foto_principal(self):
        return self.fotos.filter(principal=True).first() or self.fotos.first()

    # --- Motor de cálculo de precio ---

    def precio_dia_para(self, num_dias):
        """Devuelve el precio/día base según el rango escalonado que aplique.

        Busca el RangoPrecio cuyo intervalo [dias_min, dias_max] contiene
        num_dias. dias_max vacío = sin tope. Si no hay rango aplicable,
        devuelve None (el vehículo no es alquilable para esa duración).
        """
        for rango in self.rangos_precio.order_by("dias_min"):
            if num_dias < rango.dias_min:
                continue
            if rango.dias_max is not None and num_dias > rango.dias_max:
                continue
            return rango.precio_dia
        return None

    def temporada_para(self, fecha):
        """Devuelve la TemporadaPrecio activa en una fecha dada, o None."""
        return self.temporadas.filter(
            fecha_inicio__lte=fecha, fecha_fin__gte=fecha
        ).first()

    def calcular_precio(self, fecha_inicio, fecha_fin):
        """Calcula el precio del alquiler entre dos fechas (fin no incluido).

        1) Determina el nº de días.
        2) Toma el precio/día base del rango escalonado.
        3) Aplica el ajuste de temporada DÍA A DÍA (un día en temporada alta
           cuesta más que uno fuera de ella), sumando el total.

        Devuelve un dict con el desglose, o None si no es calculable.
        """
        from decimal import Decimal

        num_dias = (fecha_fin - fecha_inicio).days
        if num_dias <= 0:
            return None

        precio_base = self.precio_dia_para(num_dias)
        if precio_base is None:
            return None

        from datetime import timedelta

        total = Decimal("0.00")
        dia = fecha_inicio
        while dia < fecha_fin:
            precio_hoy = precio_base
            temporada = self.temporada_para(dia)
            if temporada:
                if temporada.tipo_ajuste == "multiplicador":
                    precio_hoy = (precio_base * temporada.valor).quantize(Decimal("0.01"))
                else:  # precio_fijo
                    precio_hoy = temporada.valor
            total += precio_hoy
            dia += timedelta(days=1)

        return {
            "num_dias": num_dias,
            "precio_dia_base": precio_base,
            "subtotal_vehiculo": total.quantize(Decimal("0.01")),
            "fianza": self.fianza,
        }

    def esta_disponible(self, fecha_inicio, fecha_fin):
        """True si el vehículo está libre en [fecha_inicio, fecha_fin).

        No disponible si hay solapamiento con:
          - un bloqueo manual de fechas, o
          - una reserva en estado que ocupa el vehículo (no cancelada
            ni finalizada).

        Dos rangos [a_ini, a_fin) y [b_ini, b_fin) se solapan si
        a_ini < b_fin y b_ini < a_fin.
        """
        if not self.activo:
            return False

        # Bloqueos manuales (sus fechas son inclusivas: fecha_fin incluida).
        bloqueos = self.bloqueos.filter(
            fecha_inicio__lt=fecha_fin, fecha_fin__gte=fecha_inicio,
        )
        if bloqueos.exists():
            return False

        # Reservas que ocupan el vehículo.
        estados_ocupan = ["pendiente", "documentacion", "confirmada", "activa"]
        reservas = self.reservas.filter(
            estado__in=estados_ocupan,
            fecha_inicio__lt=fecha_fin, fecha_fin__gt=fecha_inicio,
        )
        return not reservas.exists()

    # --- Requisitos legales del conductor ---

    def requisitos_conductor(self):
        """Edad mínima y antigüedad de carnet (años) según la categoría.

        Usa la categoría gestionable (categoria_obj) si está definida; si no,
        cae en los valores por defecto históricos (turismo 21, resto 23).
        """
        if self.categoria_obj:
            return {
                "edad_min": self.categoria_obj.edad_min_conductor,
                "antiguedad_min": self.categoria_obj.antiguedad_carnet_min,
            }
        if self.categoria == self.Categoria.TURISMO:
            return {"edad_min": 21, "antiguedad_min": 2}
        return {"edad_min": 23, "antiguedad_min": 2}

    # Límites por defecto históricos (fallback si no hay categoría gestionable).
    LIMITES_CATEGORIA = {
        Categoria.TURISMO: 120,
        Categoria.CAMPER: 100,
        Categoria.FURGONETA: 100,
        Categoria.INDUSTRIAL: 90,
        Categoria.MOTO: 120,
    }

    def limite_velocidad_efectivo(self, defecto_global=120):
        """Límite de velocidad aplicable a este vehículo.

        Prioridad: límite propio del vehículo -> límite de su categoría
        gestionable -> límite por defecto histórico de la categoría -> global.
        """
        if self.limite_velocidad:
            return self.limite_velocidad
        if self.categoria_obj:
            return self.categoria_obj.limite_velocidad
        return self.LIMITES_CATEGORIA.get(self.categoria, defecto_global)

    @staticmethod
    def _anios_entre(desde, hasta):
        """Años cumplidos entre dos fechas."""
        if not desde or not hasta:
            return 0
        anios = hasta.year - desde.year
        if (hasta.month, hasta.day) < (desde.month, desde.day):
            anios -= 1
        return anios

    def validar_conductor(self, fecha_nacimiento, carnet_caducidad, fecha_inicio,
                          carnet_expedicion=None):
        """Devuelve None si el conductor cumple, o un mensaje de error si no.

        Comprueba edad mínima a la fecha de inicio y que el carnet no esté
        caducado. La antigüedad del carnet se valida solo si se aporta la
        fecha de expedición (en el asistente actual no la pedimos).
        """
        req = self.requisitos_conductor()
        edad = self._anios_entre(fecha_nacimiento, fecha_inicio)
        if edad < req["edad_min"]:
            return (
                f"La edad mínima para este vehículo es de {req['edad_min']} años."
            )
        if carnet_caducidad and carnet_caducidad < fecha_inicio:
            return "El carnet de conducir caduca antes del inicio del alquiler."
        if carnet_expedicion is not None:
            antiguedad = self._anios_entre(carnet_expedicion, fecha_inicio)
            if antiguedad < req["antiguedad_min"]:
                return (
                    f"Se requieren al menos {req['antiguedad_min']} años de "
                    "antigüedad del carnet."
                )
        return None


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