"""
seed_vehiculos — Crea 10 vehículos VW de ejemplo con sus precios y extras.

Idempotente por matrícula. Ejecutar DESPUÉS de seed_extras.
No carga imágenes (se suben manualmente desde el admin).

    python manage.py seed_vehiculos
"""
from datetime import date

from django.core.management.base import BaseCommand

from autorent.models import Extra, RangoPrecio, TemporadaPrecio, Vehiculo

# Rangos de precio por categoría: (dias_min, dias_max, precio_dia).
# El último tramo deja dias_max=None (sin límite superior).
PRECIOS = {
    "turismo":    [(1, 2, 75), (3, 6, 65), (7, 29, 55), (30, None, 48)],
    "furgoneta":  [(1, 2, 70), (3, 6, 60), (7, 29, 50), (30, None, 42)],
    "camper":     [(1, 2, 110), (3, 6, 95), (7, 29, 80), (30, None, 70)],
    "industrial": [(1, 2, 90), (3, 6, 78), (7, 29, 65), (30, None, 55)],
}

# Extras por categoría (nombres deben existir; los crea seed_extras).
EXTRAS_COMUNES = [
    "Seguro básico", "Seguro todo riesgo", "Conductor adicional",
    "GPS / Navegador", "Kilometraje ilimitado",
]
EXTRAS_POR_CATEGORIA = {
    "turismo":    EXTRAS_COMUNES + ["Silla infantil", "Wifi portátil"],
    "furgoneta":  EXTRAS_COMUNES + ["Portabicicletas", "Limpieza final"],
    "camper":     EXTRAS_COMUNES + ["Kit camping", "Wifi portátil", "Portabicicletas", "Silla infantil"],
    "industrial": EXTRAS_COMUNES + ["Limpieza final"],
}

# Los 10 vehículos. anio, plazas, puertas, combustible, cambio, carga, fianza.
VEHICULOS = [
    # 2 Multivan (turismo)
    {"nombre": "Volkswagen Multivan 2023", "matricula": "1001 MTV", "modelo": "Multivan",
     "categoria": "turismo", "anio": 2023, "plazas": 7, "puertas": 5, "combustible": "diesel",
     "cambio": "automatico", "capacidad_carga": "Maletero 469 L", "fianza": 800,
     "km_actuales": 28000, "descripcion": "Monovolumen amplio de 7 plazas, ideal para familias y grupos."},
    {"nombre": "Volkswagen Multivan 2022", "matricula": "1002 MTV", "modelo": "Multivan",
     "categoria": "turismo", "anio": 2022, "plazas": 7, "puertas": 5, "combustible": "hibrido",
     "cambio": "automatico", "capacidad_carga": "Maletero 469 L", "fianza": 800,
     "km_actuales": 41000, "descripcion": "Versión híbrida enchufable, confortable y eficiente."},

    # 2 Transporter (furgoneta)
    {"nombre": "Volkswagen Transporter 2023", "matricula": "2001 TRP", "modelo": "Transporter",
     "categoria": "furgoneta", "anio": 2023, "plazas": 3, "puertas": 4, "combustible": "diesel",
     "cambio": "manual", "capacidad_carga": "6,7 m³ / 1200 kg", "fianza": 600,
     "km_actuales": 35000, "descripcion": "Furgoneta de carga versátil para mudanzas y transporte."},
    {"nombre": "Volkswagen Transporter 2021", "matricula": "2002 TRP", "modelo": "Transporter",
     "categoria": "furgoneta", "anio": 2021, "plazas": 3, "puertas": 4, "combustible": "diesel",
     "cambio": "manual", "capacidad_carga": "6,7 m³ / 1200 kg", "fianza": 600,
     "km_actuales": 68000, "descripcion": "Fiable y espaciosa, perfecta para profesionales."},

    # 2 California (camper)
    {"nombre": "Volkswagen California Ocean 2023", "matricula": "3001 CAL", "modelo": "California",
     "categoria": "camper", "anio": 2023, "plazas": 4, "puertas": 5, "combustible": "diesel",
     "cambio": "automatico", "capacidad_carga": "Camper equipada", "fianza": 1200,
     "km_actuales": 22000, "descripcion": "Camper icónica con techo elevable, cocina y 4 plazas para dormir."},
    {"nombre": "Volkswagen California Beach 2022", "matricula": "3002 CAL", "modelo": "California",
     "categoria": "camper", "anio": 2022, "plazas": 4, "puertas": 5, "combustible": "diesel",
     "cambio": "automatico", "capacidad_carga": "Camper equipada", "fianza": 1200,
     "km_actuales": 39000, "descripcion": "Versión Beach, flexible para escapadas y aventuras."},

    # 2 Crafter L5H4 (industrial, grande)
    {"nombre": "Volkswagen Crafter L5H4 2023", "matricula": "4001 CRF", "modelo": "Crafter L5H4",
     "categoria": "industrial", "anio": 2023, "plazas": 3, "puertas": 4, "combustible": "diesel",
     "cambio": "manual", "capacidad_carga": "18,4 m³ / 1400 kg", "fianza": 900,
     "km_actuales": 45000, "descripcion": "Furgón industrial de gran volumen, batalla larga y techo alto."},
    {"nombre": "Volkswagen Crafter L5H4 2022", "matricula": "4002 CRF", "modelo": "Crafter L5H4",
     "categoria": "industrial", "anio": 2022, "plazas": 3, "puertas": 4, "combustible": "diesel",
     "cambio": "manual", "capacidad_carga": "18,4 m³ / 1400 kg", "fianza": 900,
     "km_actuales": 72000, "descripcion": "Máxima capacidad de carga para transporte profesional."},

    # 2 Crafter L3H3 (industrial, medio)
    {"nombre": "Volkswagen Crafter L3H3 2023", "matricula": "5001 CRF", "modelo": "Crafter L3H3",
     "categoria": "industrial", "anio": 2023, "plazas": 3, "puertas": 4, "combustible": "diesel",
     "cambio": "manual", "capacidad_carga": "11,3 m³ / 1300 kg", "fianza": 800,
     "km_actuales": 31000, "descripcion": "Furgón industrial de volumen medio, equilibrado y maniobrable."},
    {"nombre": "Volkswagen Crafter L3H3 2021", "matricula": "5002 CRF", "modelo": "Crafter L3H3",
     "categoria": "industrial", "anio": 2021, "plazas": 3, "puertas": 4, "combustible": "diesel",
     "cambio": "manual", "capacidad_carga": "11,3 m³ / 1300 kg", "fianza": 800,
     "km_actuales": 85000, "descripcion": "Práctico para reparto urbano y transporte de mercancía."},
]


class Command(BaseCommand):
    help = "Crea 10 vehículos VW de ejemplo con precios, temporada y extras (idempotente)."

    def handle(self, *args, **options):
        # Cachear extras por nombre para asociarlos.
        extras_db = {e.nombre: e for e in Extra.objects.all()}
        if not extras_db:
            self.stdout.write(self.style.WARNING(
                "No hay extras. Ejecuta primero: python manage.py seed_extras"
            ))

        creados = 0
        for data in VEHICULOS:
            matricula = data["matricula"]
            categoria = data["categoria"]

            vehiculo, created = Vehiculo.objects.get_or_create(
                matricula=matricula,
                defaults={
                    "nombre": data["nombre"],
                    "marca": "Volkswagen",
                    "modelo": data["modelo"],
                    "anio": data["anio"],
                    "categoria": categoria,
                    "plazas": data["plazas"],
                    "puertas": data["puertas"],
                    "combustible": data["combustible"],
                    "cambio": data["cambio"],
                    "capacidad_carga": data["capacidad_carga"],
                    "descripcion": data["descripcion"],
                    "fianza": data["fianza"],
                    "km_actuales": data["km_actuales"],
                    "activo": True,
                },
            )

            if not created:
                self.stdout.write(f"  = {vehiculo.nombre} (ya existía, se omite)")
                continue

            creados += 1
            self.stdout.write(f"  + {vehiculo.nombre}")

            # Rangos de precio escalonados.
            for dias_min, dias_max, precio in PRECIOS[categoria]:
                RangoPrecio.objects.create(
                    vehiculo=vehiculo, dias_min=dias_min,
                    dias_max=dias_max, precio_dia=precio,
                )

            # Temporada alta de verano (+30%).
            TemporadaPrecio.objects.create(
                vehiculo=vehiculo, nombre="Temporada alta verano",
                fecha_inicio=date(date.today().year, 7, 1),
                fecha_fin=date(date.today().year, 8, 31),
                tipo_ajuste="multiplicador", valor="1.30",
            )

            # Asociar extras de su categoría.
            for nombre_extra in EXTRAS_POR_CATEGORIA.get(categoria, []):
                extra = extras_db.get(nombre_extra)
                if extra:
                    vehiculo.extras.add(extra)

        self.stdout.write(self.style.SUCCESS(
            f"Vehículos: {creados} creados, {len(VEHICULOS) - creados} ya existían."
        ))