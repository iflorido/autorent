"""URLs de la API pública de autorent."""
from django.urls import path

from . import api_views

app_name = "autorent"

urlpatterns = [
    path("sedes/", api_views.SedeListView.as_view(), name="sede-list"),
    path("extras/", api_views.ExtraListView.as_view(), name="extra-list"),
    path("reservas/", api_views.crear_reserva, name="crear-reserva"),
    path("reservas/<str:localizador>/documentos/", api_views.subir_documento, name="subir-documento"),
    path("documentos/<int:doc_id>/", api_views.servir_documento, name="servir-documento"),
    path("vehiculos/", api_views.VehiculoListView.as_view(), name="vehiculo-list"),
    path("vehiculos/<slug:slug>/", api_views.VehiculoDetailView.as_view(), name="vehiculo-detail"),
    path("vehiculos/<int:pk>/precio/", api_views.vehiculo_precio, name="vehiculo-precio"),
]