"""
AutoRent — API Teltonika (FastAPI).

Ingesta de telemetría GPS de alta frecuencia. FastAPI (asíncrono) recibe la
trama ya decodificada, valida el token, inserta la posición en PostgreSQL con
asyncpg, y encola una tarea Celery para que el worker de Django aplique la
lógica de detección (eventos, alertas, driver score, mantenimiento) reutilizando
el código ya existente, sin duplicarlo.

División de responsabilidades:
  - Django  : dueño del esquema (modelos y migraciones) y de la lógica.
  - FastAPI : inquilino que solo inserta posiciones y encola el procesamiento.

Va detrás del proxy de Plesk en /gps/, por eso root_path="/gps".
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import asyncpg
from celery import Celery
from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse

ROOT_PATH = os.getenv("API_ROOT_PATH", "/gps")
GPS_INGEST_TOKEN = os.getenv("GPS_INGEST_TOKEN", "")

# --- Conexión a PostgreSQL (mismas variables que el backend Django) ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", ""),
}

# --- Cliente Celery (mismo broker Redis que el worker de Django) ---
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("autorent_api", broker=CELERY_BROKER)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pool de conexiones asíncrono, reutilizado en cada petición.
    app.state.pool = await asyncpg.create_pool(min_size=1, max_size=10, **DB_CONFIG)
    yield
    await app.state.pool.close()


app = FastAPI(
    title="AutoRent Teltonika API",
    version="1.0.0",
    root_path=ROOT_PATH,
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "service": "AutoRent Teltonika API",
        "status": "ok",
        "version": "1.0.0",
    }


@app.get("/health")
async def health(request: Request):
    """Salud del servicio + comprobación de la BD."""
    try:
        async with request.app.state.pool.acquire() as con:
            await con.fetchval("SELECT 1")
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False
    return {"status": "healthy", "db": db_ok}


def _num(datos, clave, defecto=None):
    v = datos.get(clave)
    if v is None:
        return defecto
    try:
        return float(v)
    except (TypeError, ValueError):
        return defecto


def _int_or_none(datos, clave):
    v = datos.get(clave)
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


@app.post("/ingesta/")
async def ingesta(request: Request, x_ingest_token: str = Header(default="")):
    """Recibe una trama de telemetría decodificada, la inserta y encola su
    procesamiento.

    POST /gps/ingesta/  (cabecera X-Ingest-Token)
    """
    # 1) Validar token (igual que Django).
    if not GPS_INGEST_TOKEN or x_ingest_token != GPS_INGEST_TOKEN:
        return JSONResponse({"detail": "No autorizado."}, status_code=401)

    datos = await request.json()
    imei = str(datos.get("imei", "")).strip()
    if not imei:
        return JSONResponse({"detail": "Falta el IMEI."}, status_code=400)

    # 2) Timestamp del fix (ISO) o la hora del servidor.
    ts_raw = datos.get("timestamp")
    ts = None
    if ts_raw:
        try:
            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            ts = None
    if ts is None:
        ts = datetime.now(timezone.utc)

    # 3) Coordenadas obligatorias.
    try:
        lat = float(datos["lat"])
        lon = float(datos["lon"])
    except (KeyError, TypeError, ValueError):
        return JSONResponse({"detail": "Latitud/longitud no válidas."}, status_code=400)

    pool = request.app.state.pool
    async with pool.acquire() as con:
        # 4) Identificar el dispositivo por IMEI (activo).
        disp = await con.fetchrow(
            "SELECT id FROM autorent_dispositivo WHERE imei = $1 AND activo = true",
            imei,
        )
        if not disp:
            return JSONResponse({"detail": "Dispositivo no registrado."}, status_code=404)
        dispositivo_id = disp["id"]

        # 5) Insertar la posición y recuperar su id.
        posicion_id = await con.fetchval(
            """
            INSERT INTO autorent_posicion (
                dispositivo_id, timestamp, latitud, longitud, altitud, rumbo,
                satelites, velocidad, ignicion, movimiento, odometro,
                nivel_combustible, voltaje_bateria,
                aceleracion_x, aceleracion_y, aceleracion_z, evento_id, recibido_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                $14, $15, $16, $17, NOW()
            ) RETURNING id
            """,
            dispositivo_id, ts, lat, lon,
            _num(datos, "altitud"), _num(datos, "rumbo"),
            _int_or_none(datos, "satelites"),
            _num(datos, "velocidad", 0) or 0,
            bool(datos.get("ignicion", False)),
            bool(datos.get("movimiento", False)),
            _int_or_none(datos, "odometro"),
            _num(datos, "nivel_combustible"),
            _num(datos, "voltaje_bateria"),
            _num(datos, "acel_x"), _num(datos, "acel_y"), _num(datos, "acel_z"),
            _int_or_none(datos, "evento_id"),
        )

        # 6) Actualizar la última comunicación del dispositivo.
        await con.execute(
            "UPDATE autorent_dispositivo SET ultima_comunicacion = $1 WHERE id = $2",
            ts, dispositivo_id,
        )

    # 7) Encolar el procesamiento en el worker de Django (no bloquea la ingesta).
    try:
        celery_app.send_task("autorent.tasks.procesar_telemetria_id", args=[posicion_id])
    except Exception:  # noqa: BLE001
        # Si Redis falla, la posición ya está guardada; no perdemos el dato.
        pass

    return JSONResponse({"ok": True, "id": posicion_id}, status_code=201)