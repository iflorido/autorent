"""Autenticación para la API.

CSRFExemptSessionAuthentication permite seguir usando la sesión de Django
(cómodo para navegar la API logueado y para el admin) sin imponer la
comprobación CSRF en las peticiones POST de la API pública consumida por la
SPA. La protección real de la API se basa en JWT (para clientes autenticados),
rate limiting y CORS, no en CSRF de sesión.
"""
from rest_framework.authentication import SessionAuthentication


class CSRFExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # No forzar CSRF: la API no se autentica por cookie de sesión desde
        # la SPA, así que el token CSRF no aplica aquí.
        return