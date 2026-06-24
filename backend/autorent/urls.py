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
    path("contratos/<int:reserva_id>/", api_views.servir_contrato, name="servir-contrato"),
    path("subida/<str:token>/", api_views.info_subida, name="info-subida"),
    path("subida/<str:token>/documento/", api_views.subir_documento_token, name="subir-documento-token"),
    path("subida/<str:token>/finalizar/", api_views.finalizar_subida, name="finalizar-subida"),
    path("vehiculos/", api_views.VehiculoListView.as_view(), name="vehiculo-list"),
    path("vehiculos/<slug:slug>/", api_views.VehiculoDetailView.as_view(), name="vehiculo-detail"),
    path("vehiculos/<int:pk>/precio/", api_views.vehiculo_precio, name="vehiculo-precio"),
]