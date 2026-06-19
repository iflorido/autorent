"""
URL configuration — AutoRent.

Rutas tras el proxy de Plesk:
  /api/    -> API REST (DRF)
  /admin/  -> Django admin (Jazzmin)
  /static/ y /media/ los sirve el proxy vía volúmenes en producción;
  en desarrollo (DEBUG) los sirve Django.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    # path("api/", include("autorent.urls")),  # se añadirá en la fase de negocio
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)