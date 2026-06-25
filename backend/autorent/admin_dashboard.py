"""
autorent/admin_dashboard.py — Dashboard de flota GPS dentro del admin.

Una vista a medida, protegida con la autenticación del admin (solo staff),
que renderiza el mapa Leaflet. Usa admin.site.each_context() para que el
template herede el layout completo de Jazzmin (menú lateral incluido).
"""
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def dashboard_flota(request):
    """Página del dashboard de flota (mapa + paneles de vehículos)."""
    # each_context inyecta el contexto del admin (menú lateral, apps, usuario...)
    # para que Jazzmin pinte la barra de navegación como en cualquier página admin.
    contexto = admin.site.each_context(request)
    contexto.update({
        "title": "Dashboard de flota",
    })
    return render(request, "autorent/dashboard_flota.html", contexto)