"""
autorent/notificaciones.py — Envío de correos relacionados con reservas.

Reutiliza el backend SMTP configurable (core.backends.ConfiguredEmailBackend)
y los datos de la empresa (core.SiteConfig). Los envíos son tolerantes a
fallos: si el SMTP falla, la reserva NO se revierte (ya está creada); se
registra el error y se continúa.
"""
import logging

from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.html import escape

logger = logging.getLogger(__name__)


def _site_config():
    from core.models import SiteConfig
    return SiteConfig.load()


def _remitente(cfg_email):
    """Email remitente: el configurado en EmailConfig, o un fallback."""
    return getattr(cfg_email, "email_from_default", None) or "noreply@localhost"


def _fmt(valor):
    try:
        return f"{float(valor):.2f}"
    except (TypeError, ValueError):
        return str(valor)


def enviar_correos_reserva(reserva):
    """Envía el correo de confirmación al cliente y el aviso a la empresa.

    Devuelve un dict {cliente: bool, empresa: bool} indicando qué envíos
    tuvieron éxito. Nunca lanza excepción hacia arriba.
    """
    from core.models import EmailConfig
    resultado = {"cliente": False, "empresa": False}

    site = _site_config()
    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)

    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("No se pudo abrir conexión SMTP para la reserva %s: %s",
                     reserva.localizador, exc)
        return resultado

    # 1) Correo al cliente.
    try:
        asunto_cli, texto_cli, html_cli = _email_cliente(reserva, site)
        msg = EmailMultiAlternatives(
            asunto_cli, texto_cli, from_email=remitente,
            to=[reserva.cliente.email], connection=connection,
        )
        msg.attach_alternative(html_cli, "text/html")
        msg.send()
        resultado["cliente"] = True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo enviando correo al cliente de %s: %s",
                     reserva.localizador, exc)

    # 2) Correo a la empresa (al email de contacto de SiteConfig).
    email_empresa = (site.email or "").strip()
    if email_empresa:
        try:
            asunto_emp, texto_emp, html_emp = _email_empresa(reserva, site)
            msg = EmailMultiAlternatives(
                asunto_emp, texto_emp, from_email=remitente,
                to=[email_empresa], connection=connection,
            )
            msg.attach_alternative(html_emp, "text/html")
            msg.send()
            resultado["empresa"] = True
        except Exception as exc:  # noqa: BLE001
            logger.error("Fallo enviando correo a la empresa de %s: %s",
                         reserva.localizador, exc)
    else:
        logger.warning("SiteConfig.email vacío: no se avisa a la empresa de %s",
                       reserva.localizador)

    return resultado


def _bloque_extras(reserva):
    lineas = []
    for re in reserva.extras_contratados.all():
        lineas.append(f"  - {re.extra.nombre} x{re.cantidad}: {_fmt(re.precio_total)} €")
    return "\n".join(lineas)


def _email_cliente(reserva, site):
    nombre_empresa = site.nombre or "AutoRent"
    asunto = f"Tu reserva {reserva.localizador} — {nombre_empresa}"

    datos_banco = ""
    if reserva.metodo_pago == "transferencia" and (site.banco_iban or "").strip():
        datos_banco = (
            "\n\nPara confirmar tu reserva, realiza una transferencia con estos datos:\n"
            f"  Titular: {site.banco_titular}\n"
            f"  IBAN: {site.banco_iban}\n"
            + (f"  BIC/SWIFT: {site.banco_bic}\n" if (site.banco_bic or '').strip() else "")
            + f"  Concepto: {reserva.localizador}\n"
            f"  Importe: {_fmt(reserva.total)} €\n"
            "\nTu vehículo queda pre-reservado durante 24 horas. En cuanto recibamos el "
            "justificante, confirmaremos la reserva en firme."
        )

    extras = _bloque_extras(reserva)
    extras_txt = f"\nExtras:\n{extras}" if extras else ""

    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Hemos registrado tu reserva con el localizador {reserva.localizador}.\n\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Recogida: {reserva.fecha_inicio}\n"
        f"Devolución: {reserva.fecha_fin} ({reserva.num_dias} días)\n"
        f"Subtotal vehículo: {_fmt(reserva.subtotal_vehiculo)} €"
        f"{extras_txt}\n"
        f"Total alquiler: {_fmt(reserva.total)} €\n"
        f"Fianza (depósito): {_fmt(reserva.fianza)} €\n"
        f"{datos_banco}\n\n"
        f"Gracias por confiar en {nombre_empresa}."
    )

    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">Reserva registrada</h2>
      <p>Hola {escape(reserva.cliente.nombre)},</p>
      <p>Hemos registrado tu reserva con el localizador
         <strong style="font-size:1.1em">{reserva.localizador}</strong>.</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0">
        <tr><td style="padding:6px 0;color:#4b5c78">Vehículo</td>
            <td style="text-align:right"><strong>{escape(reserva.vehiculo.nombre)}</strong></td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Fechas</td>
            <td style="text-align:right">{reserva.fecha_inicio} → {reserva.fecha_fin} ({reserva.num_dias} días)</td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Total alquiler</td>
            <td style="text-align:right"><strong>{_fmt(reserva.total)} €</strong></td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Fianza (depósito)</td>
            <td style="text-align:right">{_fmt(reserva.fianza)} €</td></tr>
      </table>
      {_html_banco(reserva, site)}
      <p style="color:#4b5c78;font-size:14px">Gracias por confiar en {escape(nombre_empresa)}.</p>
    </div>
    """
    return asunto, texto, html


def _html_banco(reserva, site):
    if reserva.metodo_pago != "transferencia" or not (site.banco_iban or "").strip():
        return ""
    return f"""
    <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:16px;margin:16px 0">
      <p style="margin:0 0 8px;font-weight:600">Datos para la transferencia</p>
      <p style="margin:2px 0;font-size:14px">Titular: {escape(site.banco_titular or '')}</p>
      <p style="margin:2px 0;font-size:14px">IBAN: <strong>{escape(site.banco_iban)}</strong></p>
      <p style="margin:2px 0;font-size:14px">Concepto: <strong>{reserva.localizador}</strong></p>
      <p style="margin:2px 0;font-size:14px">Importe: <strong>{_fmt(reserva.total)} €</strong></p>
      <p style="margin:8px 0 0;font-size:13px;color:#4b5c78">
        Tu vehículo queda pre-reservado 24 horas. Al recibir el justificante confirmaremos la reserva.</p>
    </div>
    """


def _email_empresa(reserva, site):
    nombre_empresa = site.nombre or "AutoRent"
    c = reserva.cliente
    asunto = f"Nueva reserva {reserva.localizador} — {c.nombre_completo}"

    conductores = reserva.conductores_adicionales.all()
    cond_txt = ""
    if conductores:
        cond_txt = "\n\nConductores adicionales:\n" + "\n".join(
            f"  - {co.nombre_completo} ({co.nif}), carnet {co.carnet_numero} cad. {co.carnet_caducidad}"
            for co in conductores
        )

    texto = (
        f"Nueva reserva registrada: {reserva.localizador}\n\n"
        f"Estado: {reserva.get_estado_display()}\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Fechas: {reserva.fecha_inicio} → {reserva.fecha_fin} ({reserva.num_dias} días)\n"
        f"Total: {_fmt(reserva.total)} € | Fianza: {_fmt(reserva.fianza)} €\n"
        f"Método de pago: {reserva.get_metodo_pago_display()}\n\n"
        f"Cliente:\n"
        f"  {c.nombre_completo} ({c.nif})\n"
        f"  {c.email} | {c.telefono}\n"
        f"  Carnet {c.carnet_numero}, caduca {c.carnet_caducidad}\n"
        f"  {c.direccion}, {c.poblacion} {c.cp} ({c.provincia})"
        f"{cond_txt}\n\n"
        f"Revísala en el panel de administración."
    )

    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">Nueva reserva: {reserva.localizador}</h2>
      <p><strong>{escape(c.nombre_completo)}</strong> ({escape(c.nif)})<br>
         {escape(c.email)} · {escape(c.telefono)}</p>
      <table style="width:100%;border-collapse:collapse;margin:12px 0">
        <tr><td style="padding:5px 0;color:#4b5c78">Vehículo</td><td style="text-align:right">{escape(reserva.vehiculo.nombre)}</td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Fechas</td><td style="text-align:right">{reserva.fecha_inicio} → {reserva.fecha_fin}</td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Total</td><td style="text-align:right"><strong>{_fmt(reserva.total)} €</strong></td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Pago</td><td style="text-align:right">{reserva.get_metodo_pago_display()}</td></tr>
      </table>
      <p style="font-size:13px;color:#4b5c78">Conductores adicionales: {conductores.count()}</p>
    </div>
    """
    return asunto, texto, html