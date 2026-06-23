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


@api_view(["GET"])
@permission_classes([AllowAny])
def frontend_config(request):
    """Tokens de color y fuentes para que el frontend aplique el tema.

    GET /api/frontend-config/
    """
    from .models import FrontendConfig
    cfg = FrontendConfig.load()
    return Response({
        "tokens": cfg.as_tokens(),
        "fuentes_google": cfg.fuentes_google,
        "font_display": cfg.font_display,
        "font_body": cfg.font_body,
    })