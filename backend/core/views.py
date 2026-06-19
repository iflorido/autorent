from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    """Endpoint de salud y bienvenida de la API de AutoRent."""
    return Response(
        {
            "service": "AutoRent API",
            "status": "ok",
            "version": "0.1.0",
            "endpoints": {
                "admin": "/admin/",
                "api": "/api/",
            },
        }
    )