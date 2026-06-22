"""
seed_extras — Crea los extras base de AutoRent.

Idempotente: usa get_or_create por nombre, así re-ejecutarlo no duplica.
Ejecutar antes que seed_vehiculos (los vehículos asocian estos extras).

    python manage.py seed_extras
"""
from django.core.management.base import BaseCommand

from autorent.models import Extra

EXTRAS = [
    {"nombre": "Seguro básico", "descripcion": "Cobertura a terceros con franquicia.", "precio": 8, "tipo_cobro": "por_dia"},
    {"nombre": "Seguro todo riesgo", "descripcion": "Cobertura completa sin franquicia.", "precio": 15, "tipo_cobro": "por_dia"},
    {"nombre": "Conductor adicional", "descripcion": "Añade un segundo conductor autorizado.", "precio": 5, "tipo_cobro": "por_dia"},
    {"nombre": "GPS / Navegador", "descripcion": "Navegador GPS portátil.", "precio": 4, "tipo_cobro": "por_dia"},
    {"nombre": "Silla infantil", "descripcion": "Silla homologada para niños.", "precio": 4, "tipo_cobro": "por_dia"},
    {"nombre": "Kilometraje ilimitado", "descripcion": "Sin límite de kilómetros.", "precio": 12, "tipo_cobro": "por_dia"},
    {"nombre": "Wifi portátil", "descripcion": "Router 4G con datos.", "precio": 6, "tipo_cobro": "por_dia"},
    {"nombre": "Kit camping", "descripcion": "Mesa, sillas y menaje (solo camper).", "precio": 25, "tipo_cobro": "unico"},
    {"nombre": "Portabicicletas", "descripcion": "Soporte trasero para bicicletas.", "precio": 18, "tipo_cobro": "unico"},
    {"nombre": "Limpieza final", "descripcion": "Servicio de limpieza a la devolución.", "precio": 30, "tipo_cobro": "unico"},
]


class Command(BaseCommand):
    help = "Crea los extras base (idempotente)."

    def handle(self, *args, **options):
        creados = 0
        for data in EXTRAS:
            obj, created = Extra.objects.get_or_create(
                nombre=data["nombre"],
                defaults={
                    "descripcion": data["descripcion"],
                    "precio": data["precio"],
                    "tipo_cobro": data["tipo_cobro"],
                    "activo": True,
                },
            )
            if created:
                creados += 1
                self.stdout.write(f"  + {obj.nombre}")
            else:
                self.stdout.write(f"  = {obj.nombre} (ya existía)")
        self.stdout.write(self.style.SUCCESS(f"Extras: {creados} creados, {len(EXTRAS) - creados} ya existían."))