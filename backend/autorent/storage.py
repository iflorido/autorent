"""
autorent/storage.py — Almacenamiento de documentos sensibles.

Los documentos (DNI, carnet) se guardan en DOCUMENTS_ROOT, una carpeta
SEPARADA de MEDIA_ROOT que Nginx no sirve. El único acceso es a través de
la vista protegida de Django (solo staff). Al no tener `base_url`, estos
ficheros no tienen URL pública.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class DocumentosStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs["location"] = settings.DOCUMENTS_ROOT
        # Sin base_url: estos archivos no se exponen por URL directa.
        kwargs["base_url"] = None
        super().__init__(*args, **kwargs)


# Instancia reutilizable.
documentos_storage = DocumentosStorage()