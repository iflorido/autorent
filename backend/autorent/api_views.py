"""
autorent/api_views.py — Endpoints de lectura de la API pública.

  GET /api/sedes/                         -> sedes activas
  GET /api/vehiculos/                     -> listado (filtros: categoria, fechas)
  GET /api/vehiculos/<id>/                -> ficha completa
  GET /api/vehiculos/<id>/precio/         -> cálculo de precio para unas fechas

Los filtros por fecha (fecha_inicio, fecha_fin en formato YYYY-MM-DD) aplican
el motor de disponibilidad: solo devuelven vehículos libres en ese rango.
"""
from datetime import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import Sede
from .models import Extra, Vehiculo
from .serializers import (
    ExtraSerializer,
    SedeSerializer,
    VehiculoDetailSerializer,
    VehiculoListSerializer,
)


def _parse_fecha(valor):
    """Convierte 'YYYY-MM-DD' a date, o None si no es válida."""
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class SedeListView(ListAPIView):
    serializer_class = SedeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Sede.objects.filter(activa=True)


class VehiculoListView(ListAPIView):
    """Listado de vehículos activos.

    Filtros por querystring:
      ?categoria=camper           -> filtra por categoría
      ?fecha_inicio=2026-07-22&fecha_fin=2026-07-25
                                  -> solo los disponibles en ese rango
      ?sede=<id>                  -> vehículos de una sede
    """
    serializer_class = VehiculoListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Vehiculo.objects.filter(activo=True).prefetch_related(
            "fotos", "rangos_precio",
        )

        categoria = self.request.query_params.get("categoria")
        if categoria and categoria != "todos":
            qs = qs.filter(categoria=categoria)

        sede = self.request.query_params.get("sede")
        if sede:
            qs = qs.filter(sede_id=sede)

        # Filtro de disponibilidad por fechas.
        fi = _parse_fecha(self.request.query_params.get("fecha_inicio"))
        ff = _parse_fecha(self.request.query_params.get("fecha_fin"))
        if fi and ff and ff > fi:
            disponibles = [v.id for v in qs if v.esta_disponible(fi, ff)]
            qs = qs.filter(id__in=disponibles)

        return qs


class VehiculoDetailView(RetrieveAPIView):
    serializer_class = VehiculoDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Vehiculo.objects.filter(activo=True).prefetch_related(
            "fotos", "rangos_precio", "temporadas", "extras", "sede",
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def vehiculo_precio(request, pk):
    """Calcula el precio del vehículo para un rango de fechas.

    GET /api/vehiculos/<pk>/precio/?fecha_inicio=...&fecha_fin=...
    Devuelve el desglose o un error si las fechas no son válidas o el
    vehículo no es alquilable para esa duración.
    """
    try:
        vehiculo = Vehiculo.objects.get(pk=pk, activo=True)
    except Vehiculo.DoesNotExist:
        return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    fi = _parse_fecha(request.query_params.get("fecha_inicio"))
    ff = _parse_fecha(request.query_params.get("fecha_fin"))
    if not fi or not ff:
        return Response(
            {"detail": "Indica fecha_inicio y fecha_fin (YYYY-MM-DD)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if ff <= fi:
        return Response(
            {"detail": "La fecha de fin debe ser posterior a la de inicio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    calculo = vehiculo.calcular_precio(fi, ff)
    if calculo is None:
        return Response(
            {"detail": "El vehículo no tiene tarifa para esa duración."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Suplemento fuera de horario (según horas y sedes, si se indican).
    suplemento, detalle_suplemento = _calcular_suplemento_horario(request, fi, ff)

    disponible = vehiculo.esta_disponible(fi, ff)
    total = calculo["subtotal_vehiculo"] + suplemento
    return Response({
        "vehiculo_id": vehiculo.id,
        "fecha_inicio": fi,
        "fecha_fin": ff,
        "disponible": disponible,
        "num_dias": calculo["num_dias"],
        "precio_dia_base": calculo["precio_dia_base"],
        "subtotal_vehiculo": calculo["subtotal_vehiculo"],
        "suplemento_fuera_horario": suplemento,
        "suplemento_detalle": detalle_suplemento,
        "fianza": calculo["fianza"],
    })


def _parse_hora(valor):
    """Convierte 'HH:MM' en time, o None."""
    if not valor:
        return None
    from datetime import datetime as _dt
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return _dt.strptime(valor, fmt).time()
        except (ValueError, TypeError):
            continue
    return None


def _calcular_suplemento_horario(request, fi, ff):
    """Calcula el suplemento fuera de horario a partir de los parámetros de la
    petición (horas y sedes de recogida/entrega). Devuelve (importe, detalle)."""
    from decimal import Decimal
    from core.models import Sede

    hora_rec = _parse_hora(request.query_params.get("hora_recogida"))
    hora_ent = _parse_hora(request.query_params.get("hora_entrega"))
    sede_rec_id = request.query_params.get("sede_recogida")
    sede_ent_id = request.query_params.get("sede_entrega")

    total = Decimal("0.00")
    detalle = {"recogida_fuera": False, "entrega_fuera": False}

    def suplemento_de(sede_id, fecha, hora, clave):
        nonlocal total
        if not (sede_id and hora):
            return
        try:
            sede = Sede.objects.get(pk=sede_id)
        except (Sede.DoesNotExist, ValueError, TypeError):
            return
        if not sede.hora_dentro_de_horario(fecha, hora):
            total += sede.suplemento_fuera_horario or Decimal("0.00")
            detalle[clave] = True

    suplemento_de(sede_rec_id, fi, hora_rec, "recogida_fuera")
    suplemento_de(sede_ent_id, ff, hora_ent, "entrega_fuera")
    return total.quantize(Decimal("0.01")), detalle


class ExtraListView(ListAPIView):
    """Listado de extras activos (para la página pública de Extras)."""
    serializer_class = ExtraSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Extra.objects.filter(activo=True)


# ─────────────────────────────────────────────────────────────
# Creación de reserva (asistente multipaso) — endpoint de ESCRITURA
# ─────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def crear_reserva(request):
    """Crea una reserva desde el asistente.

    POST /api/reservas/
    Flujo:
      1. Valida el payload (incluido acepta_condiciones).
      2. Comprueba que el vehículo existe, está activo y disponible.
      3. Crea/reutiliza el cliente (por NIF).
      4. Crea la reserva en estado 'pendiente'.
      5. Añade los extras con su precio CONGELADO del catálogo.
      6. Recalcula los totales EN SERVIDOR (ignora cualquier precio del front).
      7. Devuelve el localizador y el desglose.

    Todo dentro de una transacción atómica: si algo falla, no queda nada a medias.
    """
    from django.db import transaction
    from .models import Cliente, Reserva, ReservaExtra
    from .serializers import CrearReservaSerializer, ReservaCreadaSerializer

    serializer = CrearReservaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    datos = serializer.validated_data

    # 2) Vehículo activo + disponible en esas fechas.
    try:
        vehiculo = Vehiculo.objects.get(pk=datos["vehiculo_id"], activo=True)
    except Vehiculo.DoesNotExist:
        return Response({"detail": "Vehículo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    fi, ff = datos["fecha_inicio"], datos["fecha_fin"]
    if not vehiculo.esta_disponible(fi, ff):
        return Response(
            {"detail": "El vehículo ya no está disponible en esas fechas."},
            status=status.HTTP_409_CONFLICT,
        )

    # Verificar que el vehículo tiene tarifa para esa duración.
    calculo = vehiculo.calcular_precio(fi, ff)
    if calculo is None:
        return Response(
            {"detail": "El vehículo no tiene tarifa para esa duración."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sedes = {}
    for campo, key in [("sede_recogida_id", "sede_recogida"), ("sede_entrega_id", "sede_entrega")]:
        sid = datos.get(campo)
        if sid:
            try:
                sedes[key] = Sede.objects.get(pk=sid, activa=True)
            except Sede.DoesNotExist:
                sedes[key] = None

    cdatos = datos["cliente"]

    # Validar requisitos legales del conductor principal (edad / carnet).
    err_cond = vehiculo.validar_conductor(
        cdatos["fecha_nacimiento"], cdatos["carnet_caducidad"], fi,
    )
    if err_cond:
        return Response(
            {"detail": f"Conductor principal: {err_cond}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validar cada conductor adicional con los mismos requisitos.
    for i, cond in enumerate(datos.get("conductores_adicionales", []), start=1):
        err = vehiculo.validar_conductor(
            cond["fecha_nacimiento"], cond["carnet_caducidad"], fi,
        )
        if err:
            return Response(
                {"detail": f"Conductor adicional {i}: {err}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        with transaction.atomic():
            # 3) Cliente: reutiliza si el NIF ya existe, actualizando sus datos.
            cliente, _ = Cliente.objects.get_or_create(
                nif=cdatos["nif"],
                defaults={
                    "nombre": cdatos["nombre"],
                    "apellidos": cdatos.get("apellidos", ""),
                    "email": cdatos["email"],
                    "telefono": cdatos["telefono"],
                },
            )
            # Actualiza los datos del cliente con lo recibido.
            for campo in [
                "nombre", "apellidos", "email", "telefono", "fecha_nacimiento",
                "direccion", "poblacion", "cp", "provincia", "pais",
                "carnet_numero", "carnet_caducidad",
            ]:
                if campo in cdatos and cdatos[campo] not in (None, ""):
                    setattr(cliente, campo, cdatos[campo])
            cliente.save()

            # 4) Reserva en estado pendiente.
            reserva = Reserva.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                fecha_inicio=fi,
                fecha_fin=ff,
                sede_recogida=sedes.get("sede_recogida"),
                sede_entrega=sedes.get("sede_entrega"),
                estado=Reserva.Estado.PENDIENTE,
                metodo_pago=datos["metodo_pago"],
            )

            # 5) Extras con precio congelado del catálogo (no del front).
            for item in datos["extras"]:
                try:
                    extra = Extra.objects.get(pk=item["extra_id"], activo=True)
                except Extra.DoesNotExist:
                    continue  # ignora extras inexistentes
                ReservaExtra.objects.create(
                    reserva=reserva,
                    extra=extra,
                    cantidad=item.get("cantidad", 1),
                    precio_congelado=extra.precio,
                    tipo_cobro_congelado=extra.tipo_cobro,
                )

            # 6) Recalcular totales EN SERVIDOR.
            reserva.recalcular_totales(guardar=True)

            # 7) Conductores adicionales con sus datos legales.
            from .models import ConductorAdicional
            for cond in datos.get("conductores_adicionales", []):
                ConductorAdicional.objects.create(
                    reserva=reserva,
                    nombre=cond["nombre"],
                    apellidos=cond.get("apellidos", ""),
                    nif=cond["nif"],
                    fecha_nacimiento=cond["fecha_nacimiento"],
                    carnet_numero=cond["carnet_numero"],
                    carnet_caducidad=cond["carnet_caducidad"],
                )

    except Exception:
        return Response(
            {"detail": "No se pudo crear la reserva. Inténtalo de nuevo."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 7) Respuesta con el localizador y el desglose.
    # Generar el token de subida de documentos (enlace mágico, 7 días).
    from .models import TokenSubida
    token_subida = TokenSubida.generar(reserva, dias_validez=7)

    # Enviar correos (al cliente y a la empresa). Fuera de la transacción:
    # si el envío falla, la reserva ya está creada y no se revierte.
    from .notificaciones import enviar_correos_reserva
    enviar_correos_reserva(reserva, token_subida=token_subida)

    salida = ReservaCreadaSerializer(reserva)
    datos = dict(salida.data)
    # Incluir el token de subida para que el asistente enlace al formulario
    # de documentos (mismo flujo que el enlace del correo).
    datos["token_subida"] = token_subida.token
    return Response(datos, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────────
# Subida de documentos de una reserva (DNI, carnet) — datos sensibles
# ─────────────────────────────────────────────────────────────

# Tipos MIME y extensiones permitidos para documentos.
DOC_EXTENSIONES = {".jpg", ".jpeg", ".png", ".pdf", ".webp", ".heic"}
DOC_MIME = {
    "image/jpeg", "image/png", "image/webp", "image/heic", "application/pdf",
}
DOC_MAX_BYTES = 10 * 1024 * 1024  # 10 MB por archivo
DOC_TIPOS_VALIDOS = {"dni_anverso", "dni_reverso", "carnet", "otro"}


@api_view(["POST"])
@permission_classes([AllowAny])
def subir_documento(request, localizador):
    """Sube un documento (DNI/carnet) asociado a una reserva.

    POST /api/reservas/<localizador>/documentos/
    Campos (multipart/form-data): tipo, archivo.

    Seguridad:
      - Valida que la reserva existe (por localizador).
      - Valida tipo de documento, extensión, MIME y tamaño.
      - Guarda en carpeta protegida (no servida públicamente por Nginx).
    """
    import os
    from .models import Reserva, DocumentoReserva

    try:
        reserva = Reserva.objects.get(localizador=localizador)
    except Reserva.DoesNotExist:
        return Response({"detail": "Reserva no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    tipo = request.data.get("tipo", "otro")
    if tipo not in DOC_TIPOS_VALIDOS:
        return Response({"detail": "Tipo de documento no válido."}, status=status.HTTP_400_BAD_REQUEST)

    archivo = request.FILES.get("archivo")
    if not archivo:
        return Response({"detail": "No se ha enviado ningún archivo."}, status=status.HTTP_400_BAD_REQUEST)

    # Validación de tamaño.
    if archivo.size > DOC_MAX_BYTES:
        return Response(
            {"detail": "El archivo supera el tamaño máximo de 10 MB."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validación de extensión.
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in DOC_EXTENSIONES:
        return Response(
            {"detail": "Formato no permitido. Usa JPG, PNG, WEBP o PDF."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validación de tipo MIME declarado.
    content_type = getattr(archivo, "content_type", "") or ""
    if content_type and content_type not in DOC_MIME:
        return Response(
            {"detail": "Tipo de archivo no permitido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    doc = DocumentoReserva.objects.create(
        reserva=reserva, tipo=tipo, archivo=archivo,
        estado=DocumentoReserva.Estado.PENDIENTE,
    )

    return Response(
        {"id": doc.id, "tipo": doc.tipo, "estado": doc.estado, "subido": True},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([AllowAny])  # control de acceso real: ver dentro
def servir_documento(request, doc_id):
    """Sirve un documento protegido SOLO a personal autenticado (staff).

    GET /api/documentos/<doc_id>/

    Los documentos (DNI, carnet) NO se sirven por Nginx público: se acceden
    únicamente a través de esta vista, que exige usuario staff autenticado.
    """
    from django.http import FileResponse, Http404
    from .models import DocumentoReserva

    # Solo personal autenticado del panel puede ver documentos sensibles.
    if not (request.user and request.user.is_authenticated and request.user.is_staff):
        return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

    try:
        doc = DocumentoReserva.objects.get(pk=doc_id)
    except DocumentoReserva.DoesNotExist:
        raise Http404

    if not doc.archivo:
        raise Http404

    return FileResponse(doc.archivo.open("rb"), as_attachment=False)


# ─────────────────────────────────────────────────────────────
# Subida de documentos vía ENLACE MÁGICO (token, sin login)
# ─────────────────────────────────────────────────────────────

def _token_valido_o_respuesta(token):
    """Devuelve (token_obj, None) si es válido, o (None, Response) si no."""
    from .models import TokenSubida
    try:
        t = TokenSubida.objects.select_related("reserva").get(token=token)
    except TokenSubida.DoesNotExist:
        return None, Response({"detail": "Enlace no válido."}, status=status.HTTP_404_NOT_FOUND)
    if t.usado_at is not None:
        return None, Response(
            {"detail": "Este enlace ya se ha utilizado.", "estado": "usado"},
            status=status.HTTP_410_GONE,
        )
    if t.ha_expirado:
        return None, Response(
            {"detail": "Este enlace ha caducado.", "estado": "expirado"},
            status=status.HTTP_410_GONE,
        )
    return t, None


@api_view(["GET"])
@permission_classes([AllowAny])
def info_subida(request, token):
    """Datos necesarios para el formulario de subida (sin login).

    GET /api/subida/<token>/
    Devuelve el titular y los conductores adicionales, para que el frontend
    muestre qué documentos pedir de cada uno.
    """
    t, err = _token_valido_o_respuesta(token)
    if err:
        return err
    reserva = t.reserva

    conductores = [
        {"id": co.id, "nombre_completo": co.nombre_completo}
        for co in reserva.conductores_adicionales.all()
    ]
    # Documentos ya subidos (para indicar el progreso).
    subidos = [
        {"tipo": d.tipo, "conductor_id": d.conductor_id}
        for d in reserva.documentos.all()
    ]
    return Response({
        "localizador": reserva.localizador,
        "titular": reserva.cliente.nombre_completo,
        "vehiculo": reserva.vehiculo.nombre,
        "conductores_adicionales": conductores,
        "documentos_subidos": subidos,
        "expira_at": t.expira_at,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def subir_documento_token(request, token):
    """Sube un documento usando el token (sin login).

    POST /api/subida/<token>/
    Campos: tipo, archivo, conductor_id (opcional; vacío = titular).
    """
    import os
    from .models import DocumentoReserva, ConductorAdicional

    t, err = _token_valido_o_respuesta(token)
    if err:
        return err
    reserva = t.reserva

    tipo = request.data.get("tipo", "otro")
    if tipo not in DOC_TIPOS_VALIDOS:
        return Response({"detail": "Tipo de documento no válido."}, status=status.HTTP_400_BAD_REQUEST)

    archivo = request.FILES.get("archivo")
    if not archivo:
        return Response({"detail": "No se ha enviado ningún archivo."}, status=status.HTTP_400_BAD_REQUEST)
    if archivo.size > DOC_MAX_BYTES:
        return Response({"detail": "El archivo supera el tamaño máximo de 10 MB."},
                        status=status.HTTP_400_BAD_REQUEST)
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in DOC_EXTENSIONES:
        return Response({"detail": "Formato no permitido. Usa JPG, PNG, WEBP o PDF."},
                        status=status.HTTP_400_BAD_REQUEST)
    content_type = getattr(archivo, "content_type", "") or ""
    if content_type and content_type not in DOC_MIME:
        return Response({"detail": "Tipo de archivo no permitido."}, status=status.HTTP_400_BAD_REQUEST)

    # Conductor adicional (opcional). Debe pertenecer a la misma reserva.
    conductor = None
    conductor_id = request.data.get("conductor_id")
    if conductor_id:
        try:
            conductor = ConductorAdicional.objects.get(pk=conductor_id, reserva=reserva)
        except ConductorAdicional.DoesNotExist:
            return Response({"detail": "Conductor no válido."}, status=status.HTTP_400_BAD_REQUEST)

    # Reemplaza un documento previo del mismo tipo y conductor (re-subida).
    DocumentoReserva.objects.filter(
        reserva=reserva, conductor=conductor, tipo=tipo,
    ).delete()

    doc = DocumentoReserva.objects.create(
        reserva=reserva, conductor=conductor, tipo=tipo, archivo=archivo,
        estado=DocumentoReserva.Estado.PENDIENTE,
    )
    return Response(
        {"id": doc.id, "tipo": doc.tipo, "conductor_id": conductor.id if conductor else None,
         "subido": True},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def finalizar_subida(request, token):
    """Marca el token como usado al terminar la subida (un solo uso).

    POST /api/subida/<token>/finalizar/
    Al finalizar, avisa a la empresa (documentación recibida) y al cliente
    (confirmación de recepción).
    """
    t, err = _token_valido_o_respuesta(token)
    if err:
        return err
    reserva = t.reserva
    t.marcar_usado()

    # Al subir documentación nueva, reiniciar el estado notificado para que el
    # ciclo de revisión pueda volver a avisar (aprobada/rechazada) tras revisar.
    if reserva.doc_estado_notificado:
        reserva.doc_estado_notificado = ""
        reserva.save(update_fields=["doc_estado_notificado"])

    # Avisos por correo (tolerantes a fallos: no rompen la respuesta).
    from .notificaciones import (
        enviar_correo_documentos_subidos_admin,
        enviar_correo_documentos_recibidos_cliente,
    )
    enviar_correo_documentos_subidos_admin(reserva)
    enviar_correo_documentos_recibidos_cliente(reserva)

    return Response({"finalizado": True})


@api_view(["GET"])
@permission_classes([AllowAny])  # control real dentro: solo staff
def servir_contrato(request, reserva_id):
    """Sirve el PDF del contrato SOLO a personal autenticado (staff).

    GET /api/contratos/<reserva_id>/
    """
    from django.http import FileResponse, Http404
    from .models import ContratoReserva

    if not (request.user and request.user.is_authenticated and request.user.is_staff):
        return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

    try:
        contrato = ContratoReserva.objects.get(reserva_id=reserva_id)
    except ContratoReserva.DoesNotExist:
        raise Http404
    if not contrato.archivo:
        raise Http404

    return FileResponse(contrato.archivo.open("rb"), as_attachment=False,
                        filename=f"contrato_{contrato.reserva.localizador}.pdf")


@api_view(["GET"])
@permission_classes([AllowAny])
def categorias_vehiculo(request):
    """Lista las categorías de vehículo que tienen al menos un vehículo activo.

    GET /api/categorias/
    Para los filtros dinámicos del catálogo en el frontend.
    """
    from .models import CategoriaVehiculo
    cats = (
        CategoriaVehiculo.objects.filter(vehiculos__activo=True)
        .distinct()
        .order_by("orden", "nombre")
    )
    return Response([
        {"slug": c.slug, "nombre": c.nombre}
        for c in cats
    ])