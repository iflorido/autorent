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


def _supl_txt(reserva):
    """Línea de suplemento fuera de horario para texto plano (vacía si 0)."""
    supl = getattr(reserva, "suplemento_fuera_horario", 0) or 0
    if float(supl) > 0:
        return f"Suplemento fuera de horario: {_fmt(supl)} €\n"
    return ""


def _html_supl(reserva):
    """Fila de suplemento fuera de horario para tabla HTML (vacía si 0)."""
    supl = getattr(reserva, "suplemento_fuera_horario", 0) or 0
    if float(supl) > 0:
        return (
            '<tr><td style="padding:6px 0;color:#4b5c78">Suplemento fuera de horario</td>'
            f'<td style="text-align:right">{_fmt(supl)} €</td></tr>'
        )
    return ""


def _fecha_hora(fecha, hora):
    """'12/06/2026 a las 16:00' si hay hora; '12/06/2026' si no.

    Acepta date y time (o None). Tolerante a formatos.
    """
    try:
        f = fecha.strftime("%d/%m/%Y")
    except (AttributeError, ValueError):
        f = str(fecha)
    if hora:
        try:
            return f"{f} a las {hora.strftime('%H:%M')}"
        except (AttributeError, ValueError):
            return f
    return f


def enviar_correos_reserva(reserva, token_subida=None):
    """Envía el correo de confirmación al cliente y el aviso a la empresa.

    Si se pasa token_subida, el correo del cliente incluye el enlace mágico
    para subir su documentación. Devuelve un dict {cliente: bool, empresa: bool}.
    Nunca lanza excepción hacia arriba.
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
        asunto_cli, texto_cli, html_cli = _email_cliente(reserva, site, token_subida)
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


def _enlace_subida(token_subida):
    """Construye la URL del enlace mágico de subida de documentos."""
    if not token_subida:
        return None
    from django.conf import settings
    return f"{settings.SITE_URL}/subir-documentos/{token_subida.token}"


def _email_cliente(reserva, site, token_subida=None):
    nombre_empresa = site.nombre or "AutoRent"
    asunto = f"Tu reserva {reserva.localizador} — {nombre_empresa}"
    enlace = _enlace_subida(token_subida)

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

    bloque_docs = ""
    if enlace:
        bloque_docs = (
            "\n\nDOCUMENTACIÓN NECESARIA\n"
            "Para poder formalizar tu contrato necesitamos el DNI/NIE y el carnet de "
            "conducir del conductor titular"
            + (" y de cada conductor adicional.\n" if reserva.conductores_adicionales.exists() else ".\n")
            + f"Súbela de forma segura desde este enlace (válido 7 días):\n{enlace}\n"
            "Es un enlace personal: no lo compartas. Podrás subir cada documento una vez."
        )

    extras = _bloque_extras(reserva)
    extras_txt = f"\nExtras:\n{extras}" if extras else ""

    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Hemos registrado tu reserva con el localizador {reserva.localizador}.\n\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Recogida: {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}\n"
        f"Devolución: {_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)} ({reserva.num_dias} días)\n"
        f"Subtotal vehículo: {_fmt(reserva.subtotal_vehiculo)} €"
        f"{extras_txt}\n"
        f"{_supl_txt(reserva)}"
        f"Total alquiler: {_fmt(reserva.total)} €\n"
        f"Fianza (depósito): {_fmt(reserva.fianza)} €\n"
        "\nIMPORTANTE — FIANZA: el depósito de garantía se retiene en el momento de la "
        "recogida mediante TARJETA DE CRÉDITO válida a nombre del conductor titular. "
        "No se admite débito ni efectivo para la fianza. Asegúrate de llevarla.\n"
        f"{datos_banco}"
        f"{bloque_docs}\n\n"
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
        <tr><td style="padding:6px 0;color:#4b5c78">Recogida</td>
            <td style="text-align:right">{_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}</td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Devolución</td>
            <td style="text-align:right">{_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)} ({reserva.num_dias} días)</td></tr>
        {_html_supl(reserva)}
        <tr><td style="padding:6px 0;color:#4b5c78">Total alquiler</td>
            <td style="text-align:right"><strong>{_fmt(reserva.total)} €</strong></td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Fianza (depósito)</td>
            <td style="text-align:right">{_fmt(reserva.fianza)} €</td></tr>
      </table>
      {_html_banco(reserva, site)}
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px;margin:16px 0">
        <p style="margin:0;font-size:14px"><strong>Fianza:</strong> el depósito de garantía
           ({_fmt(reserva.fianza)} €) se retiene en la recogida con <strong>tarjeta de crédito</strong>
           válida a nombre del conductor titular. No se admite débito ni efectivo para la fianza.</p>
      </div>
      {_html_subida(enlace, reserva)}
      <p style="color:#4b5c78;font-size:14px">Gracias por confiar en {escape(nombre_empresa)}.</p>
    </div>
    """
    return asunto, texto, html


def _html_subida(enlace, reserva):
    if not enlace:
        return ""
    extra = (" y de cada conductor adicional" if reserva.conductores_adicionales.exists() else "")
    return f"""
    <div style="background:#ecfeff;border:1px solid #a5f3fc;border-radius:10px;padding:16px;margin:16px 0">
      <p style="margin:0 0 8px;font-weight:600">Sube tu documentación</p>
      <p style="margin:0 0 12px;font-size:14px;color:#155e75">
        Necesitamos el DNI/NIE y el carnet de conducir del titular{extra}.
        El enlace es personal y caduca en 7 días.</p>
      <a href="{enlace}" style="display:inline-block;background:#0891b2;color:#fff;
         text-decoration:none;padding:10px 20px;border-radius:8px;font-weight:600">
        Subir documentación</a>
    </div>
    """


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
        f"Recogida: {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}\n"
        f"Devolución: {_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)} ({reserva.num_dias} días)\n"
        f"{_supl_txt(reserva)}"
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
        <tr><td style="padding:5px 0;color:#4b5c78">Recogida</td><td style="text-align:right">{_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}</td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Devolución</td><td style="text-align:right">{_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)}</td></tr>
        {_html_supl(reserva)}
        <tr><td style="padding:5px 0;color:#4b5c78">Total</td><td style="text-align:right"><strong>{_fmt(reserva.total)} €</strong></td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Pago</td><td style="text-align:right">{reserva.get_metodo_pago_display()}</td></tr>
      </table>
      <p style="font-size:13px;color:#4b5c78">Conductores adicionales: {conductores.count()}</p>
    </div>
    """
    return asunto, texto, html


def enviar_correo_documentos_rechazados(reserva, token_subida, motivo=""):
    """Avisa al cliente de que su documentación fue rechazada y da un enlace nuevo.

    Se llama desde el admin cuando el personal rechaza documentos. Tolerante a
    fallos: registra el error pero no lanza excepción.
    """
    from core.models import EmailConfig
    site = _site_config()
    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)
    nombre_empresa = site.nombre or "AutoRent"
    enlace = _enlace_subida(token_subida)

    asunto = f"Documentación de tu reserva {reserva.localizador}: revisión necesaria"
    motivo_txt = f"\nMotivo: {motivo}\n" if motivo else ""

    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Hemos revisado la documentación de tu reserva {reserva.localizador} y "
        f"necesitamos que vuelvas a subir alguno de los documentos.\n"
        f"{motivo_txt}\n"
        f"Sube de nuevo tu documentación desde este enlace (válido 7 días):\n{enlace}\n\n"
        f"Disculpa las molestias. Gracias por tu colaboración.\n"
        f"{nombre_empresa}"
    )
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#b45309">Revisión de documentación</h2>
      <p>Hola {escape(reserva.cliente.nombre)},</p>
      <p>Hemos revisado la documentación de tu reserva
         <strong>{reserva.localizador}</strong> y necesitamos que vuelvas a subir
         alguno de los documentos.</p>
      {f'<p style="background:#fef3c7;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;font-size:14px"><strong>Motivo:</strong> {escape(motivo)}</p>' if motivo else ''}
      <div style="background:#ecfeff;border:1px solid #a5f3fc;border-radius:10px;padding:16px;margin:16px 0">
        <a href="{enlace}" style="display:inline-block;background:#0891b2;color:#fff;
           text-decoration:none;padding:10px 20px;border-radius:8px;font-weight:600">
          Volver a subir documentación</a>
        <p style="margin:10px 0 0;font-size:13px;color:#155e75">El enlace caduca en 7 días.</p>
      </div>
      <p style="color:#4b5c78;font-size:14px">Disculpa las molestias. {escape(nombre_empresa)}.</p>
    </div>
    """
    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
        msg = EmailMultiAlternatives(
            asunto, texto, from_email=remitente,
            to=[reserva.cliente.email], connection=connection,
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo enviando correo de rechazo de %s: %s", reserva.localizador, exc)
        return False


def _lista_documentos_texto(reserva):
    """Devuelve una lista legible de los documentos subidos, por persona."""
    lineas = []
    # Documentos del titular (sin conductor).
    titular = reserva.documentos.filter(conductor__isnull=True)
    if titular.exists():
        lineas.append(f"Titular ({reserva.cliente.nombre_completo}):")
        for d in titular:
            lineas.append(f"  - {d.get_tipo_display()}")
    # Documentos de cada conductor adicional.
    for co in reserva.conductores_adicionales.all():
        docs = reserva.documentos.filter(conductor=co)
        if docs.exists():
            lineas.append(f"Conductor adicional ({co.nombre_completo}):")
            for d in docs:
                lineas.append(f"  - {d.get_tipo_display()}")
    return "\n".join(lineas) if lineas else "  (sin documentos)"


def enviar_correo_documentos_subidos_admin(reserva):
    """Avisa a la empresa de que el cliente ha subido su documentación."""
    from core.models import EmailConfig
    site = _site_config()
    email_empresa = (site.email or "").strip()
    if not email_empresa:
        logger.warning("SiteConfig.email vacío: no se avisa de docs subidos de %s",
                       reserva.localizador)
        return False

    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)
    docs = _lista_documentos_texto(reserva)
    n_docs = reserva.documentos.count()

    asunto = f"Documentación recibida — reserva {reserva.localizador}"
    texto = (
        f"El cliente de la reserva {reserva.localizador} ha subido su documentación.\n\n"
        f"Cliente: {reserva.cliente.nombre_completo} ({reserva.cliente.nif})\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Recogida: {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}\n"
        f"Devolución: {_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)}\n\n"
        f"Documentos subidos ({n_docs}):\n{docs}\n\n"
        f"Revísala en el panel de administración. Si algo no es válido, usa la acción "
        f"'Rechazar documentación' para pedir al cliente que la vuelva a subir."
    )
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">Documentación recibida</h2>
      <p>El cliente de la reserva <strong>{reserva.localizador}</strong> ha subido su documentación.</p>
      <table style="width:100%;border-collapse:collapse;margin:12px 0">
        <tr><td style="padding:5px 0;color:#4b5c78">Cliente</td>
            <td style="text-align:right">{escape(reserva.cliente.nombre_completo)} ({escape(reserva.cliente.nif)})</td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Vehículo</td>
            <td style="text-align:right">{escape(reserva.vehiculo.nombre)}</td></tr>
        <tr><td style="padding:5px 0;color:#4b5c78">Documentos</td>
            <td style="text-align:right"><strong>{n_docs}</strong></td></tr>
      </table>
      <pre style="background:#f1f5f9;border-radius:8px;padding:12px;font-size:13px;white-space:pre-wrap">{escape(docs)}</pre>
      <p style="font-size:13px;color:#4b5c78">Revísala en el panel de administración.</p>
    </div>
    """
    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
        msg = EmailMultiAlternatives(asunto, texto, from_email=remitente,
                                     to=[email_empresa], connection=connection)
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo avisando a la empresa de docs subidos de %s: %s",
                     reserva.localizador, exc)
        return False


def enviar_correo_documentos_recibidos_cliente(reserva):
    """Confirma al cliente que su documentación se recibió y explica los pasos."""
    from core.models import EmailConfig
    site = _site_config()
    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)
    nombre_empresa = site.nombre or "AutoRent"

    asunto = f"Documentación recibida — reserva {reserva.localizador}"
    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Hemos recibido correctamente la documentación de tu reserva {reserva.localizador}.\n\n"
        f"Uno de nuestros gestores la revisará. Si queda aprobada, te enviaremos un "
        f"correo de confirmación. Si hubiera cualquier problema con algún documento, "
        f"te avisaremos con un nuevo enlace para volver a subirlo.\n\n"
        f"IMPORTANTE: deberás presentar esta misma documentación (en original) al recoger "
        f"el vehículo. Los documentos deben coincidir con los que acabas de subir.\n\n"
        f"Gracias por tu colaboración.\n{nombre_empresa}"
    )
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">¡Documentación recibida!</h2>
      <p>Hola {escape(reserva.cliente.nombre)},</p>
      <p>Hemos recibido correctamente la documentación de tu reserva
         <strong>{reserva.localizador}</strong>.</p>
      <p>Uno de nuestros gestores la revisará. Si queda aprobada, te enviaremos un correo
         de confirmación. Si hubiera algún problema, te avisaremos con un nuevo enlace.</p>
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px;margin:16px 0">
        <p style="margin:0;font-size:14px"><strong>Importante:</strong> deberás presentar esta
           misma documentación (en original) al recoger el vehículo. Los documentos deben
           coincidir con los que acabas de subir.</p>
      </div>
      <p style="color:#4b5c78;font-size:14px">Gracias por tu colaboración. {escape(nombre_empresa)}.</p>
    </div>
    """
    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
        msg = EmailMultiAlternatives(asunto, texto, from_email=remitente,
                                     to=[reserva.cliente.email], connection=connection)
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo confirmando recepción de docs al cliente de %s: %s",
                     reserva.localizador, exc)
        return False


def enviar_correo_documentos_aprobados(reserva):
    """Avisa al cliente de que su documentación ha sido aprobada."""
    from core.models import EmailConfig
    site = _site_config()
    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)
    nombre_empresa = site.nombre or "AutoRent"

    asunto = f"Documentación aprobada — reserva {reserva.localizador}"
    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Tu documentación para la reserva {reserva.localizador} ha sido revisada y "
        f"APROBADA. ¡Todo correcto!\n\n"
        f"Recuerda que deberás presentar esta misma documentación en original al recoger "
        f"el vehículo, junto con una tarjeta de crédito válida a nombre del conductor "
        f"titular para la fianza.\n\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Recogida: {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}\n"
        f"Devolución: {_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)}\n\n"
        f"Gracias por confiar en {nombre_empresa}."
    )
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">Documentación aprobada</h2>
      <p>Hola {escape(reserva.cliente.nombre)},</p>
      <p>Tu documentación para la reserva <strong>{reserva.localizador}</strong> ha sido
         revisada y <strong style="color:#059669">aprobada</strong>. ¡Todo correcto!</p>
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px;margin:16px 0">
        <p style="margin:0;font-size:14px">Recuerda presentar esta misma documentación en
           original al recoger el vehículo, junto con una <strong>tarjeta de crédito</strong>
           válida a nombre del titular para la fianza.</p>
      </div>
      <p style="color:#4b5c78;font-size:14px">Gracias por confiar en {escape(nombre_empresa)}.</p>
    </div>
    """
    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
        msg = EmailMultiAlternatives(asunto, texto, from_email=remitente,
                                     to=[reserva.cliente.email], connection=connection)
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo enviando aprobación de %s: %s", reserva.localizador, exc)
        return False


def _motivos_rechazo(reserva):
    """Recopila las notas de revisión de los documentos rechazados."""
    motivos = []
    for d in reserva.documentos.filter(estado="rechazado"):
        quien = d.conductor.nombre_completo if d.conductor_id else reserva.cliente.nombre_completo
        nota = (d.notas_revision or "").strip()
        etiqueta = f"{d.get_tipo_display()} ({quien})"
        motivos.append(f"{etiqueta}: {nota}" if nota else etiqueta)
    return "; ".join(motivos)


def enviar_contrato_cliente(reserva):
    """Envía el contrato PDF al cliente como adjunto."""
    from core.models import EmailConfig
    contrato = getattr(reserva, "contrato", None)
    if not contrato or not contrato.archivo:
        logger.warning("No hay contrato que enviar para %s", reserva.localizador)
        return False

    site = _site_config()
    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)
    nombre_empresa = site.nombre or "AutoRent"

    asunto = f"Tu contrato de alquiler — reserva {reserva.localizador}"
    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Adjuntamos el contrato de alquiler de tu reserva {reserva.localizador}.\n\n"
        f"Revísalo y consérvalo. Deberás presentar tu documentación original y una "
        f"tarjeta de crédito válida para la fianza al recoger el vehículo.\n\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Recogida: {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}\n"
        f"Devolución: {_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)}\n\n"
        f"Gracias por confiar en {nombre_empresa}."
    )
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">Tu contrato de alquiler</h2>
      <p>Hola {escape(reserva.cliente.nombre)},</p>
      <p>Adjuntamos el contrato de alquiler de tu reserva
         <strong>{reserva.localizador}</strong>. Revísalo y consérvalo.</p>
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px;margin:16px 0">
        <p style="margin:0;font-size:14px">Recuerda presentar tu documentación original y una
           <strong>tarjeta de crédito</strong> válida para la fianza al recoger el vehículo.</p>
      </div>
      <p style="color:#4b5c78;font-size:14px">Gracias por confiar en {escape(nombre_empresa)}.</p>
    </div>
    """
    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
        msg = EmailMultiAlternatives(asunto, texto, from_email=remitente,
                                     to=[reserva.cliente.email], connection=connection)
        msg.attach_alternative(html, "text/html")
        # Adjuntar el PDF.
        contrato.archivo.open("rb")
        msg.attach(f"contrato_{reserva.localizador}.pdf",
                   contrato.archivo.read(), "application/pdf")
        contrato.archivo.close()
        msg.send()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo enviando contrato de %s: %s", reserva.localizador, exc)
        return False


def enviar_recordatorio_recogida(reserva, horas):
    """Recordatorio al cliente de su próxima recogida (48h o 24h antes)."""
    from core.models import EmailConfig
    site = _site_config()
    cfg_email = EmailConfig.load()
    remitente = _remitente(cfg_email)
    nombre_empresa = site.nombre or "AutoRent"

    asunto = f"Tu recogida es pronto — reserva {reserva.localizador}"
    texto = (
        f"Hola {reserva.cliente.nombre},\n\n"
        f"Te recordamos que tu recogida está prevista para el {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)} "
        f"(en aproximadamente {horas} horas).\n\n"
        f"Vehículo: {reserva.vehiculo.nombre}\n"
        f"Recogida: {_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}\n"
        f"Devolución: {_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)}\n\n"
        f"Recuerda traer tu documentación original y una tarjeta de crédito válida a "
        f"nombre del conductor titular para la fianza.\n\n"
        f"¡Te esperamos! {nombre_empresa}."
    )
    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:560px;margin:0 auto;color:#0f172a">
      <h2 style="color:#0891b2">Tu recogida es pronto</h2>
      <p>Hola {escape(reserva.cliente.nombre)},</p>
      <p>Te recordamos que tu recogida está prevista para
         <strong>{_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}</strong> (en aproximadamente {horas} horas).</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px">
        <tr><td style="padding:6px 0;color:#4b5c78">Vehículo</td>
            <td style="text-align:right"><strong>{escape(reserva.vehiculo.nombre)}</strong></td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Recogida</td>
            <td style="text-align:right">{_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)}</td></tr>
        <tr><td style="padding:6px 0;color:#4b5c78">Devolución</td>
            <td style="text-align:right">{_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)}</td></tr>
      </table>
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px;margin:16px 0">
        <p style="margin:0;font-size:14px">Recuerda traer tu documentación original y una
           <strong>tarjeta de crédito</strong> válida a nombre del titular para la fianza.</p>
      </div>
      <p style="color:#4b5c78;font-size:14px">¡Te esperamos! {escape(nombre_empresa)}.</p>
    </div>
    """
    try:
        connection = get_connection(
            backend="core.backends.ConfiguredEmailBackend", fail_silently=False,
        )
        msg = EmailMultiAlternatives(asunto, texto, from_email=remitente,
                                     to=[reserva.cliente.email], connection=connection)
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallo enviando recordatorio de %s: %s", reserva.localizador, exc)
        return False