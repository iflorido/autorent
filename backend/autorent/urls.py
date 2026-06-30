"""URLs de la API pública de autorent."""
from django.urls import path

from . import api_views
from . import telemetria_views

app_name = "autorent"

urlpatterns = [
    path("sedes/", api_views.SedeListView.as_view(), name="sede-list"),
    path("extras/", api_views.ExtraListView.as_view(), name="extra-list"),
    path("reservas/", api_views.crear_reserva, name="crear-reserva"),
    path("reservas/<str:localizador>/documentos/", api_views.subir_documento, name="subir-documento"),
    path("documentos/<int:doc_id>/", api_views.servir_documento, name="servir-documento"),
    path("contratos/<int:reserva_id>/", api_views.servir_contrato, name="servir-contrato"),
    # Telemetría GPS
    path("gps/ingesta/", telemetria_views.ingesta_telemetria, name="gps-ingesta"),
    path("gps/flota/", telemetria_views.flota_estado, name="gps-flota"),
    path("gps/vehiculo/<int:vehiculo_id>/historico/", telemetria_views.vehiculo_historico, name="gps-historico"),
    path("gps/vehiculo/<int:vehiculo_id>/score/", telemetria_views.driver_score, name="gps-score"),
    path("gps/alertas/", telemetria_views.alertas_activas, name="gps-alertas"),
    path("gps/alertas/<int:alerta_id>/leer/", telemetria_views.alerta_marcar_leida, name="gps-alerta-leer"),
    path("subida/<str:token>/", api_views.info_subida, name="info-subida"),
    path("subida/<str:token>/documento/", api_views.subir_documento_token, name="subir-documento-token"),
    path("subida/<str:token>/finalizar/", api_views.finalizar_subida, name="finalizar-subida"),
    path("categorias/", api_views.categorias_vehiculo, name="categoria-list"),
    path("contacto/", api_views.contacto, name="contacto"),
    path("vehiculos/", api_views.VehiculoListView.as_view(), name="vehiculo-list"),
    path("vehiculos/<slug:slug>/", api_views.VehiculoDetailView.as_view(), name="vehiculo-detail"),
    path("vehiculos/<int:pk>/precio/", api_views.vehiculo_precio, name="vehiculo-precio"),
]