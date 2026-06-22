"""
autorent/models/reserva.py — Bloque de clientes y reservas.

  - Cliente          : datos del cliente y de su carnet de conducir.
  - Reserva          : núcleo, con máquina de estados y desglose económico.
  - ReservaExtra     : extras contratados, con precio CONGELADO.
  - DocumentoReserva : DNI/carnet subidos por el cliente (zona protegida).
  - Pago             : pagos asociados a la reserva.
  - Factura          : factura emitida de la reserva.
  - Cancelacion      : registro de cancelación.
"""
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .vehiculo import Extra, Vehiculo


class Cliente(models.Model):
    # Vínculo opcional con User (para un futuro portal de cliente).
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="cliente", verbose_name="Usuario",
    )

    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    apellidos = models.CharField(max_length=160, blank=True, verbose_name="Apellidos")
    nif = models.CharField(max_length=20, verbose_name="NIF/DNI/Pasaporte")
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de nacimiento")

    # Dirección
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    poblacion = models.CharField(max_length=100, blank=True, verbose_name="Población")
    cp = models.CharField(max_length=10, blank=True, verbose_name="Código postal")
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    pais = models.CharField(max_length=60, default="España", verbose_name="País")

    # Carnet de conducir
    carnet_numero = models.CharField(max_length=40, blank=True, verbose_name="Nº carnet de conducir")
    carnet_caducidad = models.DateField(blank=True, null=True, verbose_name="Caducidad del carnet")

    notas = models.TextField(blank=True, verbose_name="Notas internas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre", "apellidos"]

    def __str__(self):
        return f"{self.nombre} {self.apellidos}".strip() + f" ({self.nif})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellidos}".strip()


def documento_upload_path(instance, filename):
    """Documentos en subcarpeta separada (se protegerá con el frontend).

    NO debe servirse con el alias público de Nginx de /media/vehiculos/.
    """
    return f"documentos/reserva_{instance.reserva_id}/{filename}"


class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        DOCUMENTACION = "documentacion", "Pendiente de documentación"
        CONFIRMADA = "confirmada", "Confirmada"
        ACTIVA = "activa", "Activa (en curso)"
        FINALIZADA = "finalizada", "Finalizada"
        CANCELADA = "cancelada", "Cancelada"

    class MetodoPago(models.TextChoices):
        TRANSFERENCIA = "transferencia", "Transferencia bancaria"
        TARJETA = "tarjeta", "Tarjeta (online)"
        EFECTIVO = "efectivo", "Efectivo / en oficina"

    localizador = models.CharField(
        max_length=12, unique=True, editable=False, verbose_name="Localizador",
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="reservas", verbose_name="Cliente",
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, related_name="reservas", verbose_name="Vehículo",
    )

    fecha_inicio = models.DateField(verbose_name="Fecha de recogida")
    fecha_fin = models.DateField(verbose_name="Fecha de devolución")

    estado = models.CharField(
        max_length=20, choices=Estado.choices,
        default=Estado.PENDIENTE, verbose_name="Estado",
    )
    metodo_pago = models.CharField(
        max_length=20, choices=MetodoPago.choices,
        default=MetodoPago.TRANSFERENCIA, verbose_name="Método de pago",
    )

    # Desglose económico (se congela al crear/confirmar).
    num_dias = models.PositiveSmallIntegerField(default=0, verbose_name="Nº de días")
    precio_dia_base = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name="Precio/día base",
    )
    subtotal_vehiculo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal vehículo",
    )
    subtotal_extras = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal extras",
    )
    fianza = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name="Fianza",
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Total (sin fianza)",
    )

    notas = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.localizador} — {self.cliente.nombre_completo} / {self.vehiculo.nombre}"

    def save(self, *args, **kwargs):
        if not self.localizador:
            self.localizador = self._generar_localizador()
        super().save(*args, **kwargs)

    @staticmethod
    def _generar_localizador():
        # Ej: AR-9F3K2A (corto, legible, único).
        code = uuid.uuid4().hex[:6].upper()
        loc = f"AR-{code}"
        while Reserva.objects.filter(localizador=loc).exists():
            code = uuid.uuid4().hex[:6].upper()
            loc = f"AR-{code}"
        return loc

    def recalcular_totales(self, guardar=True):
        """Recalcula el desglose económico a partir del vehículo y extras.

        Usa el motor de precios del vehículo (rango por días + temporada) y
        suma los extras ya congelados. No incluye la fianza en el total
        (la fianza es un depósito reembolsable, se gestiona aparte).
        """
        calculo = self.vehiculo.calcular_precio(self.fecha_inicio, self.fecha_fin)
        if calculo is None:
            return None

        self.num_dias = calculo["num_dias"]
        self.precio_dia_base = calculo["precio_dia_base"]
        self.subtotal_vehiculo = calculo["subtotal_vehiculo"]
        self.fianza = calculo["fianza"]

        extras_total = Decimal("0.00")
        for re in self.extras_contratados.all():
            extras_total += re.precio_total
        self.subtotal_extras = extras_total.quantize(Decimal("0.01"))

        self.total = (self.subtotal_vehiculo + self.subtotal_extras).quantize(Decimal("0.01"))

        if guardar:
            self.save(update_fields=[
                "num_dias", "precio_dia_base", "subtotal_vehiculo",
                "subtotal_extras", "fianza", "total",
            ])
        return self.total


class ReservaExtra(models.Model):
    """Extra contratado en una reserva, con precio CONGELADO al contratarlo."""

    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name="extras_contratados",
        verbose_name="Reserva",
    )
    extra = models.ForeignKey(
        Extra, on_delete=models.PROTECT, related_name="contrataciones", verbose_name="Extra",
    )
    cantidad = models.PositiveSmallIntegerField(default=1, verbose_name="Cantidad")
    # Se copian del Extra al contratar; si el Extra cambia luego, esto no.
    precio_congelado = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Precio congelado",
    )
    tipo_cobro_congelado = models.CharField(max_length=10, verbose_name="Tipo de cobro")

    class Meta:
        verbose_name = "Extra contratado"
        verbose_name_plural = "Extras contratados"

    def __str__(self):
        return f"{self.extra.nombre} x{self.cantidad} ({self.reserva.localizador})"

    @property
    def precio_total(self):
        """Precio total del extra en la reserva (según tipo de cobro)."""
        if self.tipo_cobro_congelado == "por_dia":
            return self.precio_congelado * self.cantidad * (self.reserva.num_dias or 1)
        return self.precio_congelado * self.cantidad


class DocumentoReserva(models.Model):
    class Tipo(models.TextChoices):
        DNI_ANVERSO = "dni_anverso", "DNI (anverso)"
        DNI_REVERSO = "dni_reverso", "DNI (reverso)"
        CARNET = "carnet", "Carnet de conducir"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de revisión"
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"

    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name="documentos", verbose_name="Reserva",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, verbose_name="Tipo")
    archivo = models.FileField(upload_to=documento_upload_path, verbose_name="Archivo")
    estado = models.CharField(
        max_length=12, choices=Estado.choices,
        default=Estado.PENDIENTE, verbose_name="Estado",
    )
    notas_revision = models.CharField(max_length=255, blank=True, verbose_name="Notas de revisión")
    subido_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento de reserva"
        verbose_name_plural = "Documentos de reserva"
        ordering = ["reserva", "tipo"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.reserva.localizador} ({self.get_estado_display()})"


class Pago(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        COMPLETADO = "completado", "Completado"
        FALLIDO = "fallido", "Fallido"
        REEMBOLSADO = "reembolsado", "Reembolsado"

    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name="pagos", verbose_name="Reserva",
    )
    metodo = models.CharField(
        max_length=20, choices=Reserva.MetodoPago.choices, verbose_name="Método",
    )
    importe = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)], verbose_name="Importe",
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices,
        default=Estado.PENDIENTE, verbose_name="Estado",
    )
    referencia = models.CharField(
        max_length=120, blank=True, verbose_name="Referencia",
        help_text="ID de transacción de pasarela o concepto de transferencia.",
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.importe}€ — {self.reserva.localizador} ({self.get_estado_display()})"


class Factura(models.Model):
    reserva = models.OneToOneField(
        Reserva, on_delete=models.PROTECT, related_name="factura", verbose_name="Reserva",
    )
    numero = models.CharField(max_length=30, unique=True, verbose_name="Número de factura")
    fecha_emision = models.DateField(auto_now_add=True, verbose_name="Fecha de emisión")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total facturado")
    pdf = models.FileField(upload_to="facturas/", blank=True, null=True, verbose_name="PDF")

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-fecha_emision"]

    def __str__(self):
        return f"Factura {self.numero} ({self.reserva.localizador})"


class Cancelacion(models.Model):
    reserva = models.OneToOneField(
        Reserva, on_delete=models.CASCADE, related_name="cancelacion", verbose_name="Reserva",
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de cancelación")
    motivo = models.TextField(blank=True, verbose_name="Motivo")
    importe_reembolsado = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Importe reembolsado",
    )

    class Meta:
        verbose_name = "Cancelación"
        verbose_name_plural = "Cancelaciones"

    def __str__(self):
        return f"Cancelación de {self.reserva.localizador}"