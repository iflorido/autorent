"""
Paquete de configuración del admin de autorent.

Se importan los módulos por dominio para que Django ejecute los
decoradores @admin.register de cada uno al cargar la app.
"""
from . import vehiculo  # noqa: F401
from . import reserva  # noqa: F401
from . import telemetria  # noqa: F401