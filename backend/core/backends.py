"""
core/backends.py

Backend de correo que lee la configuración SMTP desde la base de datos
(EmailConfig) en lugar de settings.py. Así cada cliente edita su servidor
de correo desde el admin sin tocar código ni variables de entorno.

Para activarlo, en settings.py:
    EMAIL_BACKEND = "core.backends.ConfiguredEmailBackend"
"""
import ssl

from django.core.mail.backends.smtp import EmailBackend
from django.utils.functional import cached_property

from .models import EmailConfig


class ConfiguredEmailBackend(EmailBackend):
    """Backend SMTP que toma host/puerto/credenciales de EmailConfig (BD)."""

    def __init__(self, fail_silently=False, **kwargs):
        try:
            config = EmailConfig.load()
            kwargs["host"] = config.email_host
            kwargs["port"] = config.email_port
            kwargs["username"] = config.email_host_user
            kwargs["password"] = config.email_host_password
            kwargs["use_tls"] = config.email_use_tls
            kwargs["use_ssl"] = config.email_use_ssl
            kwargs["timeout"] = 15
            # Parámetro nativo de Django para el saludo HELO/EHLO:
            # útil cuando el envío falla por resolución DNS inversa.
            if config.email_dns_workaround:
                kwargs["local_hostname"] = config.email_dns_workaround
        except Exception as exc:
            # Durante migraciones la tabla puede no existir todavía;
            # en ese caso seguimos con los kwargs/ajustes por defecto.
            print(f"Aviso: no se pudo cargar EmailConfig: {exc}")

        super().__init__(fail_silently=fail_silently, **kwargs)

    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
            return context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context