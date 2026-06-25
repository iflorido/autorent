"""
autorent/admin_dashboard.py — Dashboard de flota GPS dentro del admin.

Una vista a medida, protegida con la autenticación del admin (solo staff),
que renderiza el mapa Leaflet. Los datos los obtiene de los endpoints
/api/gps/flota/ y /api/gps/vehiculo/<id>/historico/, autenticados por la
sesión del admin.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def dashboard_flota(request):
    """Página del dashboard de flota (mapa + lista de vehículos)."""
    contexto = {
        "title": "Dashboard de flota",
        "site_header": "AutoRent",
    }
    return render(request, "autorent/dashboard_flota.html", contexto)