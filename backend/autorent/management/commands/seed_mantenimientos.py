"""
seed_mantenimientos — Crea registros de mantenimiento para cada vehículo.

Para cada vehículo genera: ITV, seguro, cambio de aceite y revisión general,
con fechas pasadas y su próximo vencimiento (para probar alertas).

Idempotente: solo crea mantenimientos si el vehículo aún no tiene ninguno.
Ejecutar DESPUÉS de seed_vehiculos.

    python manage.py seed_mantenimientos
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from autorent.models import Mantenimiento, Vehiculo


class Command(BaseCommand):
    help = "Crea mantenimientos de ejemplo para cada vehículo (idempotente)."

    def handle(self, *args, **options):
        vehiculos = Vehiculo.objects.all()
        if not vehiculos:
            self.stdout.write(self.style.WARNING(
                "No hay vehículos. Ejecuta primero: python manage.py seed_vehiculos"
            ))
            return

        hoy = date.today()
        creados = 0

        for v in vehiculos:
            if v.mantenimientos.exists():
                self.stdout.write(f"  = {v.nombre} (ya tiene mantenimientos, se omite)")
                continue

            km = v.km_actuales or 0
            registros = [
                # ITV: hecha hace ~6 meses, próxima en ~1,5 años.
                {"tipo": "itv", "fecha": hoy - timedelta(days=180),
                 "fecha_proximo": hoy + timedelta(days=545), "km": max(km - 5000, 0),
                 "coste": 45, "notas": "ITV favorable."},
                # Seguro: renovado hace ~3 meses, vence en ~9 meses.
                {"tipo": "seguro", "fecha": hoy - timedelta(days=90),
                 "fecha_proximo": hoy + timedelta(days=275), "km": None,
                 "coste": 650, "notas": "Póliza anual todo riesgo."},
                # Cambio de aceite: hace ~2 meses.
                {"tipo": "revision", "fecha": hoy - timedelta(days=60),
                 "fecha_proximo": hoy + timedelta(days=305), "km": max(km - 2000, 0),
                 "coste": 120, "notas": "Cambio de aceite y filtros."},
                # Revisión general: hace ~4 meses.
                {"tipo": "revision", "fecha": hoy - timedelta(days=120),
                 "fecha_proximo": hoy + timedelta(days=245), "km": max(km - 4000, 0),
                 "coste": 220, "notas": "Revisión general (frenos, neumáticos, niveles)."},
            ]

            for r in registros:
                Mantenimiento.objects.create(vehiculo=v, **r)
                creados += 1

            self.stdout.write(f"  + {v.nombre}: 4 mantenimientos")

        self.stdout.write(self.style.SUCCESS(f"Mantenimientos creados: {creados}."))