"""URLs de la API pública de autorent."""
from django.urls import path

from . import api_views

app_name = "autorent"

urlpatterns = [
    path("sedes/", api_views.SedeListView.as_view(), name="sede-list"),
    path("vehiculos/", api_views.VehiculoListView.as_view(), name="vehiculo-list"),
    path("vehiculos/<int:pk>/", api_views.VehiculoDetailView.as_view(), name="vehiculo-detail"),
    path("vehiculos/<int:pk>/precio/", api_views.vehiculo_precio, name="vehiculo-precio"),
]