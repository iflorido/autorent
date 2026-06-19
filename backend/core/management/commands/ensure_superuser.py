"""
Crea un superusuario a partir de variables de entorno, de forma idempotente.

Variables:
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_EMAIL
    DJANGO_SUPERUSER_PASSWORD

- Si faltan las variables, no hace nada (permite crear el admin a mano).
- Si el usuario ya existe, no lo toca y no falla (seguro ante reinicios).
- Pensado para despliegues replicables: cada cliente arranca con su admin.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea un superusuario desde variables de entorno si no existe."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "Sin DJANGO_SUPERUSER_USERNAME/PASSWORD: no se crea superusuario."
            )
            return

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                f"El superusuario '{username}' ya existe. No se hace nada."
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Superusuario '{username}' creado correctamente.")
        )