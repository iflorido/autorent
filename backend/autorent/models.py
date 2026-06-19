from django.db import models

"""
Paquete de modelos de autorent.

Los modelos se organizan por dominio en módulos separados y se reexportan
aquí para que Django los descubra como `autorent.<Modelo>`.
"""
from .vehiculo import (
    BloqueoFecha,
    Extra,
    FotoVehiculo,
    Mantenimiento,
    RangoPrecio,
    TemporadaPrecio,
    Vehiculo,
)

__all__ = [
    "Vehiculo",
    "FotoVehiculo",
    "RangoPrecio",
    "TemporadaPrecio",
    "Extra",
    "BloqueoFecha",
    "Mantenimiento",
]
