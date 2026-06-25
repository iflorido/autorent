"""
autorent/models/telemetria.py — Telemetría GPS (Teltonika FMC130 / FMC003).

Modelo de datos para la flota conectada:
  - Dispositivo: el aparato Teltonika, identificado por su IMEI, asignado a un
    vehículo. El enlace dispositivo↔vehículo es por IMEI (lo que envía el
    aparato en el protocolo Codec 8), nunca por matrícula.
  - Posicion: cada registro de telemetría recibido (posición, velocidad,
    ignición, odómetro, combustible, acelerómetro, etc.).
"""
from django.db import models

from .vehiculo import Vehiculo


class Dispositivo(models.Model):
    """Aparato Teltonika instalado en un vehículo, identificado por IMEI."""

    class Modelo(models.TextChoices):
        FMC130 = "fmc130", "Teltonika FMC130"
        FMC003 = "fmc003", "Teltonika FMC003"
        OTRO = "otro", "Otro"

    imei = models.CharField(
        max_length=20, unique=True, db_index=True, verbose_name="IMEI",
        help_text="Identificador único del dispositivo (15 dígitos).",
    )
    modelo = models.CharField(
        max_length=10, choices=Modelo.choices, default=Modelo.FMC130,
        verbose_name="Modelo",
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="dispositivos", verbose_name="Vehículo asignado",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    # Última telemetría conocida (desnormalizada para consultas rápidas del mapa).
    ultima_comunicacion = models.DateTimeField(
        blank=True, null=True, verbose_name="Última comunicación",
    )
    sim_iccid = models.CharField(
        max_length=25, blank=True, verbose_name="ICCID de la SIM",
    )
    notas = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dispositivo GPS"
        verbose_name_plural = "Dispositivos GPS"
        ordering = ["imei"]

    def __str__(self):
        destino = self.vehiculo.matricula if self.vehiculo else "sin asignar"
        return f"{self.get_modelo_display()} {self.imei} → {destino}"


class Posicion(models.Model):
    """Un registro de telemetría recibido de un dispositivo.

    Pensado para alta frecuencia: se indexan dispositivo+timestamp para
    consultas de histórico y de última posición.
    """
    dispositivo = models.ForeignKey(
        Dispositivo, on_delete=models.CASCADE, related_name="posiciones",
        verbose_name="Dispositivo",
    )
    # Momento del fix GPS (lo marca el dispositivo, no el servidor).
    timestamp = models.DateTimeField(db_index=True, verbose_name="Fecha/hora")

    # Posición.
    latitud = models.FloatField(verbose_name="Latitud")
    longitud = models.FloatField(verbose_name="Longitud")
    altitud = models.FloatField(blank=True, null=True, verbose_name="Altitud (m)")
    rumbo = models.FloatField(blank=True, null=True, verbose_name="Rumbo (°)")
    satelites = models.IntegerField(blank=True, null=True, verbose_name="Satélites")

    # Movimiento y estado.
    velocidad = models.FloatField(default=0, verbose_name="Velocidad (km/h)")
    ignicion = models.BooleanField(default=False, verbose_name="Encendido (ignición)")
    movimiento = models.BooleanField(default=False, verbose_name="En movimiento")

    # Datos OEM (vía CAN, según modelo y vehículo).
    odometro = models.BigIntegerField(
        blank=True, null=True, verbose_name="Odómetro (km)",
        help_text="Kilometraje real leído del vehículo.",
    )
    nivel_combustible = models.FloatField(
        blank=True, null=True, verbose_name="Nivel de combustible (%)",
    )
    voltaje_bateria = models.FloatField(
        blank=True, null=True, verbose_name="Voltaje batería (V)",
    )

    # Acelerómetro (para driver score: frenazos, acelerones, curvas).
    aceleracion_x = models.FloatField(blank=True, null=True, verbose_name="Acel. X")
    aceleracion_y = models.FloatField(blank=True, null=True, verbose_name="Acel. Y")
    aceleracion_z = models.FloatField(blank=True, null=True, verbose_name="Acel. Z")

    # Evento Teltonika (AVL event IO id) que disparó el envío, si aplica.
    evento_id = models.IntegerField(blank=True, null=True, verbose_name="Evento (IO id)")

    recibido_at = models.DateTimeField(auto_now_add=True, verbose_name="Recibido")

    class Meta:
        verbose_name = "Posición"
        verbose_name_plural = "Posiciones"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["dispositivo", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.dispositivo.imei} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"