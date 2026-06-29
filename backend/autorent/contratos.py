"""
autorent/contratos.py — Generación del contrato de alquiler en PDF.

Usa reportlab (ya en requirements, sin dependencias del sistema). Incluye los
datos de la reserva, cliente, conductores adicionales, vehículo y las
condiciones generales completas. Devuelve los bytes del PDF y su hash SHA-256.
"""
import hashlib
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

# Color corporativo (teal de AutoRent).
ACCENT = colors.HexColor("#0891b2")
GRIS = colors.HexColor("#4b5c78")

# Cláusulas de las Condiciones Generales de Contratación.
CONDICIONES = [
    ("1. Objeto del contrato",
     "El presente contrato regula el alquiler del vehículo identificado, sin conductor, "
     "entre el arrendador y el arrendatario, por el periodo y condiciones aquí descritos."),
    ("2. Conductores autorizados",
     "Solo podrán conducir el vehículo el conductor titular y los conductores adicionales "
     "registrados en este contrato, que deben cumplir la edad mínima y antigüedad de carnet "
     "exigidas según la categoría del vehículo. Ceder el volante a un conductor no registrado "
     "anula todas las coberturas del seguro."),
    ("3. Documentación",
     "El arrendatario y cada conductor adicional deben presentar en la recogida el DNI/NIE o "
     "pasaporte y el carnet de conducir en vigor, que deben coincidir con la documentación "
     "aportada durante la reserva."),
    ("4. Fianza",
     "En el momento de la recogida se retiene una fianza mediante tarjeta de crédito válida a "
     "nombre del conductor titular. No se admite tarjeta de débito ni efectivo para la fianza. "
     "La fianza se libera tras la devolución del vehículo, una vez verificado su estado."),
    ("5. Uso del vehículo",
     "El vehículo se destinará exclusivamente a un uso particular y conforme a la legislación "
     "vigente. Queda prohibido subarrendarlo, usarlo para competiciones, transporte de "
     "mercancías ilegales o conducirlo bajo los efectos de alcohol o sustancias."),
    ("6. Combustible",
     "El vehículo se entrega con el depósito lleno y debe devolverse lleno. En caso contrario, "
     "se cobrará el combustible faltante más un cargo por el servicio de repostaje."),
    ("7. Kilometraje",
     "El kilometraje incluido es el indicado en la tarifa contratada. Los kilómetros que "
     "excedan ese límite se facturarán según la tarifa por kilómetro vigente."),
    ("8. Seguro y franquicia",
     "El vehículo dispone del seguro contratado en la reserva. En caso de siniestro, el "
     "arrendatario responde de la franquicia correspondiente, salvo en las coberturas que la "
     "reduzcan o eliminen según la modalidad elegida."),
    ("9. Averías y asistencia",
     "Ante cualquier avería o incidencia, el arrendatario debe contactar con el servicio de "
     "asistencia. No se autorizan reparaciones por cuenta propia sin consentimiento previo."),
    ("10. Devolución",
     "El vehículo se devolverá en la fecha, hora y lugar acordados, en el mismo estado en que "
     "se entregó. Los retrasos no autorizados podrán facturarse como días adicionales."),
    ("11. Cancelación",
     "Las condiciones de cancelación son las vigentes en el momento de la reserva según la "
     "modalidad contratada. El importe reembolsable dependerá de la antelación de la cancelación."),
    ("12. Protección de datos",
     "Los datos personales y la documentación aportada se tratan conforme a la normativa de "
     "protección de datos, con la finalidad de gestionar el alquiler, y se conservan durante "
     "los plazos legalmente exigidos."),
]


def _estilos():
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        "TituloDoc", parent=estilos["Title"], fontSize=18, textColor=ACCENT, spaceAfter=2,
    ))
    estilos.add(ParagraphStyle(
        "Seccion", parent=estilos["Heading2"], fontSize=11, textColor=ACCENT,
        spaceBefore=10, spaceAfter=4,
    ))
    estilos.add(ParagraphStyle(
        "ClausulaTit", parent=estilos["Heading3"], fontSize=9.5, spaceBefore=6, spaceAfter=1,
    ))
    estilos.add(ParagraphStyle(
        "Cuerpo", parent=estilos["Normal"], fontSize=9, leading=13, alignment=TA_JUSTIFY,
    ))
    estilos.add(ParagraphStyle(
        "Pequeno", parent=estilos["Normal"], fontSize=8, textColor=GRIS,
    ))
    return estilos


def _fmt_fecha(f):
    if not f:
        return "—"
    return f.strftime("%d/%m/%Y") if hasattr(f, "strftime") else str(f)


def _fmt_fecha_hora(fecha, hora):
    """'12/06/2026 a las 16:00' si hay hora; '12/06/2026' si no."""
    base = _fmt_fecha(fecha)
    if hora and hasattr(hora, "strftime"):
        return f"{base} a las {hora.strftime('%H:%M')}"
    return base


def _detalle_fuera_horario(reserva):
    """Devuelve las líneas (etiqueta, importe) del suplemento fuera de horario,
    separando recogida y entrega. Vacío si no hay suplemento.

    Recalcula por tramo a partir de las horas y sedes, para mostrar a cuál
    corresponde cada cargo en el contrato.
    """
    from decimal import Decimal
    lineas = []
    # Recogida.
    if reserva.hora_recogida and reserva.sede_recogida_id:
        sede = reserva.sede_recogida
        if not sede.hora_dentro_de_horario(reserva.fecha_inicio, reserva.hora_recogida):
            imp = sede.suplemento_fuera_horario or Decimal("0.00")
            if imp > 0:
                lineas.append((
                    f"Recogida fuera de horario ({reserva.hora_recogida.strftime('%H:%M')})",
                    imp,
                ))
    # Entrega.
    if reserva.hora_entrega and reserva.sede_entrega_id:
        sede = reserva.sede_entrega
        if not sede.hora_dentro_de_horario(reserva.fecha_fin, reserva.hora_entrega):
            imp = sede.suplemento_fuera_horario or Decimal("0.00")
            if imp > 0:
                lineas.append((
                    f"Entrega fuera de horario ({reserva.hora_entrega.strftime('%H:%M')})",
                    imp,
                ))
    return lineas


def generar_pdf_contrato(reserva):
    """Genera el PDF del contrato. Devuelve (bytes_pdf, hash_sha256)."""
    from core.models import SiteConfig
    site = SiteConfig.load()
    estilos = _estilos()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"Contrato {reserva.localizador}",
    )
    el = []

    # Cabecera.
    empresa = site.nombre or "AutoRent"
    el.append(Paragraph("Contrato de alquiler de vehículo", estilos["TituloDoc"]))
    el.append(Paragraph(
        f"{empresa}"
        + (f" · NIF {site.nif}" if getattr(site, "nif", "") else ""),
        estilos["Pequeno"],
    ))
    el.append(Spacer(1, 4))
    el.append(Paragraph(
        f"Localizador <b>{reserva.localizador}</b> · Emitido el "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos["Pequeno"],
    ))
    el.append(Spacer(1, 8))
    el.append(HRFlowable(width="100%", color=ACCENT, thickness=1.2))

    # Datos del arrendador y arrendatario.
    c = reserva.cliente
    el.append(Paragraph("Partes", estilos["Seccion"]))
    razon = getattr(site, "razon_social", "") or empresa
    dir_emp = getattr(site, "direccion", "") or ""
    datos_partes = [
        ["Arrendador", "Arrendatario (conductor titular)"],
        [
            f"{razon}\n{dir_emp}\n" + (f"NIF: {site.nif}" if getattr(site, "nif", "") else ""),
            f"{c.nombre_completo}\nNIF: {c.nif}\n{c.email} · {c.telefono}\n"
            f"{c.direccion}, {c.poblacion} {c.cp} ({c.provincia})\n"
            f"Carnet: {c.carnet_numero} · caduca {_fmt_fecha(c.carnet_caducidad)}",
        ],
    ]
    t = Table(datos_partes, colWidths=[85 * mm, 85 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, GRIS),
    ]))
    el.append(t)

    # Conductores adicionales.
    conductores = list(reserva.conductores_adicionales.all())
    if conductores:
        el.append(Paragraph("Conductores adicionales autorizados", estilos["Seccion"]))
        filas = [["Nombre", "NIF", "Nacimiento", "Carnet", "Caduca"]]
        for co in conductores:
            filas.append([
                co.nombre_completo, co.nif, _fmt_fecha(co.fecha_nacimiento),
                co.carnet_numero, _fmt_fecha(co.carnet_caducidad),
            ])
        tc = Table(filas, colWidths=[50 * mm, 28 * mm, 28 * mm, 34 * mm, 30 * mm])
        tc.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ecfeff")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        el.append(tc)

    # Vehículo y periodo.
    v = reserva.vehiculo
    el.append(Paragraph("Vehículo y periodo", estilos["Seccion"]))
    filas_v = [
        ["Vehículo", v.nombre],
        ["Matrícula", getattr(v, "matricula", "") or "—"],
        ["Categoría", v.get_categoria_display()],
        ["Recogida", _fmt_fecha_hora(reserva.fecha_inicio, reserva.hora_recogida)],
        ["Devolución", f"{_fmt_fecha_hora(reserva.fecha_fin, reserva.hora_entrega)} ({reserva.num_dias} días)"],
    ]
    tv = Table(filas_v, colWidths=[40 * mm, 130 * mm])
    tv.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), GRIS),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    el.append(tv)

    # Desglose económico.
    el.append(Paragraph("Desglose económico", estilos["Seccion"]))
    filas_e = [["Concepto", "Importe"]]
    filas_e.append([f"Alquiler ({reserva.num_dias} días)", f"{reserva.subtotal_vehiculo:.2f} €"])
    for re in reserva.extras_contratados.all():
        filas_e.append([f"Extra: {re.extra.nombre} x{re.cantidad}", f"{re.precio_total:.2f} €"])

    # Suplemento fuera de horario, desglosado por tramo (recogida / entrega).
    for etiqueta, importe in _detalle_fuera_horario(reserva):
        filas_e.append([etiqueta, f"{importe:.2f} €"])

    filas_e.append(["TOTAL ALQUILER", f"{reserva.total:.2f} €"])
    filas_e.append(["Fianza (depósito, tarjeta de crédito)", f"{reserva.fianza:.2f} €"])
    te = Table(filas_e, colWidths=[130 * mm, 40 * mm])
    te.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, -2), (-1, -2), "Helvetica-Bold"),
        ("LINEABOVE", (0, -2), (-1, -2), 0.5, GRIS),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, -1), (-1, -1), GRIS),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    el.append(te)

    # Condiciones generales.
    el.append(Spacer(1, 6))
    el.append(Paragraph("Condiciones Generales de Contratación", estilos["Seccion"]))
    for titulo, texto in CONDICIONES:
        el.append(Paragraph(titulo, estilos["ClausulaTit"]))
        el.append(Paragraph(texto, estilos["Cuerpo"]))

    # Aceptación.
    el.append(Spacer(1, 10))
    el.append(HRFlowable(width="100%", color=GRIS, thickness=0.4))
    el.append(Spacer(1, 6))
    el.append(Paragraph(
        "El arrendatario declara haber leído y aceptado las presentes condiciones, "
        "aceptación registrada electrónicamente durante el proceso de reserva.",
        estilos["Pequeno"],
    ))
    el.append(Spacer(1, 16))
    firma = Table(
        [["_____________________________", "_____________________________"],
         ["Por el arrendador", "El arrendatario"]],
        colWidths=[85 * mm, 85 * mm],
    )
    firma.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, 1), GRIS),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
    ]))
    el.append(firma)

    doc.build(el)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    return pdf_bytes, digest