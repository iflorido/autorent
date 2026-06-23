# Migración del campo slug de Vehiculo (en pasos seguros para datos existentes).
from django.db import migrations, models
from django.utils.text import slugify


def poblar_slugs(apps, schema_editor):
    Vehiculo = apps.get_model("autorent", "Vehiculo")
    usados = set()
    for v in Vehiculo.objects.all():
        base = slugify(v.nombre) or "vehiculo"
        slug = base
        n = 2
        while slug in usados or Vehiculo.objects.filter(slug=slug).exclude(pk=v.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        v.slug = slug
        usados.add(slug)
        v.save(update_fields=["slug"])


def revertir(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("autorent", "0003_reserva_sede_entrega_reserva_sede_recogida_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehiculo",
            name="slug",
            field=models.SlugField(
                blank=True, 
                default="", 
                max_length=140,
                db_index=False,  # <--- ESTO EVITA QUE EL PASO 1 CREE EL ÍNDICE 'LIKE'
                verbose_name="Slug (URL)",
                help_text="Se genera automáticamente del nombre si se deja vacío.",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(poblar_slugs, revertir),
        migrations.AlterField(
            model_name="vehiculo",
            name="slug",
            field=models.SlugField(
                blank=True, unique=True, max_length=140,
                verbose_name="Slug (URL)",
                help_text="Se genera automáticamente del nombre si se deja vacío.",
            ),
        ),
    ]