"""
autorent/models/flota.py — Driver score, mantenimiento por odómetro y alertas.

Capas de valor sobre la telemetría:
  - ReglaMantenimiento: umbrales por km o por fecha (aceite cada X km, ITV...).
  - EventoConduccion: cada evento brusco detectado (frenazo, acelerón, curva,
    exceso de velocidad), asociado al vehículo y a la reserva activa si la hay.
  - Alerta: avisos unificados para el dashboard (mantenimiento, velocidad,
    conducción).
"""
from django.db import models

from .vehiculo import Vehiculo
from .reserva import Reserva


class ReglaMantenimiento(models.Model):
    """Regla recurrente de mantenimiento de un vehículo (o plantilla global).

    Por km: salta cuando el odómetro alcanza (ultimo_km_aviso + cada_km).
    Por fecha: salta cuando se acerca fecha_proxima.
    """
    class Tipo(models.TextChoices):
        ACEITE = "aceite", "Cambio de aceite"
        NEUMATICOS = "neumaticos", "Neumáticos"
        ITV = "itv", "ITV"
        REVISION = "revision", "Revisión general"
        OTRO = "otro", "Otro"

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="reglas_mantenimiento",
        verbose_name="Vehículo",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, verbose_name="Tipo")
    # Mantenimiento por kilometraje.
    cada_km = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Cada (km)",
        help_text="Intervalo en km (ej: aceite cada 15000). Vacío si es por fecha.",
    )
    km_proximo = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Próximo aviso (km)",
        help_text="Odómetro al que saltará el aviso.",
    )
    # Mantenimiento por fecha (ITV, seguro).
    fecha_proxima = models.DateField(
        blank=True, null=True, verbose_name="Próxima fecha",
    )
    dias_aviso = models.PositiveIntegerField(
        default=15, verbose_name="Avisar con (días) de antelación",
    )
    activa = models.BooleanField(default=True, verbose_name="Activa")
    notas = models.CharField(max_length=255, blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Regla de mantenimiento"
        verbose_name_plural = "Reglas de mantenimiento"
        ordering = ["vehiculo", "tipo"]

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.vehiculo.matricula}"


class EventoConduccion(models.Model):
    """Un evento de conducción brusca o exceso de velocidad detectado."""
    class Tipo(models.TextChoices):
        FRENAZO = "frenazo", "Frenazo brusco"
        ACELERON = "aceleron", "Aceleración brusca"
        CURVA = "curva", "Curva brusca"
        VELOCIDAD = "velocidad", "Exceso de velocidad"

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="eventos_conduccion",
        verbose_name="Vehículo",
    )
    reserva = models.ForeignKey(
        Reserva, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="eventos_conduccion", verbose_name="Reserva activa",
    )
    tipo = models.CharField(max_length=12, choices=Tipo.choices, verbose_name="Tipo")
    severidad = models.FloatField(
        default=1.0, verbose_name="Severidad",
        help_text="Magnitud del evento (g del acelerómetro o km/h de exceso).",
    )
    velocidad = models.FloatField(blank=True, null=True, verbose_name="Velocidad (km/h)")
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(db_index=True, verbose_name="Momento")

    class Meta:
        verbose_name = "Evento de conducción"
        verbose_name_plural = "Eventos de conducción"
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["vehiculo", "-timestamp"])]

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.vehiculo.matricula}"


class Alerta(models.Model):
    """Alerta unificada para el dashboard (mantenimiento / velocidad / conducción)."""
    class Tipo(models.TextChoices):
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        VELOCIDAD = "velocidad", "Exceso de velocidad"
        CONDUCCION = "conduccion", "Conducción brusca"

    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, related_name="alertas",
        verbose_name="Vehículo",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, verbose_name="Tipo")
    mensaje = models.CharField(max_length=255, verbose_name="Mensaje")
    leida = models.BooleanField(default=False, verbose_name="Leída/atendida")
    # Clave para evitar duplicar la misma alerta de mantenimiento.
    clave_dedupe = models.CharField(
        max_length=120, blank=True, db_index=True, editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.vehiculo.matricula}"