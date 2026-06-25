"""Crea las categorías iniciales y conecta los vehículos existentes.

Preserva los slugs actuales (turismo, furgoneta, camper, industrial, moto) que
usa el frontend, y los límites de velocidad y requisitos de conductor que
estaban en el código, para no cambiar el comportamiento actual.
"""
from django.db import migrations


# (slug, nombre, limite_velocidad, edad_min, antiguedad_min, orden)
CATEGORIAS = [
    ("turismo", "Turismo", 120, 21, 2, 1),
    ("furgoneta", "Furgoneta", 100, 23, 2, 2),
    ("camper", "Camper", 100, 23, 2, 3),
    ("industrial", "Industrial", 90, 23, 2, 4),
    ("moto", "Moto", 120, 21, 2, 5),
]


def crear_categorias(apps, schema_editor):
    CategoriaVehiculo = apps.get_model("autorent", "CategoriaVehiculo")
    Vehiculo = apps.get_model("autorent", "Vehiculo")

    mapa = {}
    for slug, nombre, limite, edad, antig, orden in CATEGORIAS:
        cat, _ = CategoriaVehiculo.objects.get_or_create(
            slug=slug,
            defaults={
                "nombre": nombre,
                "limite_velocidad": limite,
                "edad_min_conductor": edad,
                "antiguedad_carnet_min": antig,
                "orden": orden,
            },
        )
        mapa[slug] = cat

    # Conectar cada vehículo existente a su categoría según el texto actual.
    for v in Vehiculo.objects.all():
        cat = mapa.get(v.categoria)
        if cat:
            v.categoria_obj = cat
            v.save(update_fields=["categoria_obj"])


def revertir(apps, schema_editor):
    CategoriaVehiculo = apps.get_model("autorent", "CategoriaVehiculo")
    CategoriaVehiculo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("autorent", "0013_categoriavehiculo_vehiculo_categoria_obj"),
    ]

    operations = [
        migrations.RunPython(crear_categorias, revertir),
    ]