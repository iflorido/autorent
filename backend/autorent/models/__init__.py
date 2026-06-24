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
from .reserva import (
    Cancelacion,
    Cliente,
    ConductorAdicional,
    DocumentoReserva,
    Factura,
    Pago,
    Reserva,
    ReservaExtra,
    TokenSubida,
)

__all__ = [
    # vehiculo
    "Vehiculo",
    "FotoVehiculo",
    "RangoPrecio",
    "TemporadaPrecio",
    "Extra",
    "BloqueoFecha",
    "Mantenimiento",
    # reserva
    "Cliente",
    "Reserva",
    "ReservaExtra",
    "ConductorAdicional",
    "TokenSubida",
    "DocumentoReserva",
    "Pago",
    "Factura",
    "Cancelacion",
]