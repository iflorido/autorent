# Despliegue de AutoRent en Plesk

Guía de referencia para desplegar AutoRent en el VPS con Plesk. Un solo
dominio reparte por rutas hacia tres contenedores.

## Mapa de puertos

| Contenedor | Puerto interno | Puerto publicado | Ruta pública |
|---|---|---|---|
| `frontend` (Nginx) | 80 | 8074 | `/` |
| `backend` (Django) | 8072 | 8072 | `/api/`, `/admin/` |
| `api` (FastAPI) | 8073 | 8073 | `/gps/` |
| `redis` | 6379 | (interno) | — |

Los estáticos (`/static/`) y los archivos subidos (`/media/`) los sirve
el proxy directamente desde los volúmenes mapeados, sin pasar por Django.

## Variables de entorno (Plesk → contenedor backend)

Defínelas en la configuración del contenedor en Plesk. No subir el `.env`
real al repo; solo `.env.example` como referencia.

```
DJANGO_SECRET_KEY=<clave larga aleatoria>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=autorent.automaworks.es
DJANGO_CSRF_TRUSTED_ORIGINS=https://autorent.automaworks.es

DB_HOST=<IP del VPS>
DB_PORT=5432
DB_NAME=admin_autorent
DB_USER=admin_userautorent
DB_PASSWORD=<password>

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

## Volúmenes mapeados al VPS (para backups)

```
<ruta-en-VPS>/media   -> /app/media           (contenedor backend)
<ruta-en-VPS>/static  -> /app/staticfiles      (contenedor backend)
```

La base de datos NO usa volumen Docker: vive en el PostgreSQL del host
gestionado por Plesk. Sus copias van por las herramientas de Plesk o un
`pg_dump` programado en el host.

## Reglas de proxy en Plesk (Apache & nginx Settings)

En Plesk: dominio → Apache & nginx Settings → "Additional nginx directives".
Estas directivas reparten el dominio entre los contenedores. Ajusta el host:
si Plesk corre los contenedores en el mismo host, suele ser `127.0.0.1`.

```nginx
# --- Backend Django: API REST ---
location /api/ {
    proxy_pass http://127.0.0.1:8072;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# --- Backend Django: admin (Jazzmin) ---
location /admin/ {
    proxy_pass http://127.0.0.1:8072;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# --- API FastAPI Teltonika ---
location /gps/ {
    proxy_pass http://127.0.0.1:8073/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# --- Estáticos del admin Django (servidos desde el volumen) ---
location /static/ {
    alias <ruta-en-VPS>/static/;
    expires 30d;
    access_log off;
}

# --- Archivos subidos: fotos de vehículos, documentos ---
location /media/ {
    alias <ruta-en-VPS>/media/;
    expires 7d;
}

# --- Frontend (React): todo lo demás ---
location / {
    proxy_pass http://127.0.0.1:8074;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Notas:
- El orden importa: nginx evalúa los `location` por especificidad, así que
  las rutas concretas (`/api/`, `/admin/`, `/gps/`, `/static/`, `/media/`)
  ganan sobre la genérica `/`.
- La barra final en `proxy_pass http://127.0.0.1:8073/;` (FastAPI) hace que
  `/gps/health` llegue al contenedor como `/health`, que es lo que la app
  espera con `root_path=/gps`.
- El SSL lo gestiona Plesk (Let's Encrypt) sobre el dominio; los contenedores
  hablan HTTP por detrás. Por eso Django usa `SECURE_PROXY_SSL_HEADER`.

## Replicar para otro cliente

1. Nuevo dominio (p. ej. `rentacar.clienteX.com`) en Plesk.
2. Nueva BD PostgreSQL en el host.
3. Nuevo `.env` con ese dominio, esa BD y la marca del cliente.
4. Mismas imágenes de ghcr.io, mismas reglas de proxy (cambiando solo las
   rutas de los volúmenes y, si hace falta, los puertos publicados).
5. Los colores y datos de empresa se ajustan desde `core.SiteConfig` y las
   variables CSS del frontend, sin recompilar.
