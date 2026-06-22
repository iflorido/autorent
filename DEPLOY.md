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

## Redis y Celery (contenedores separados en Plesk)

Tres contenedores adicionales:

- **redis**: imagen `redis:7-alpine`. Comando de inicio con contraseña:
  ```
  redis-server --requirepass TU_PASSWORD_REDIS
  ```
- **celery**: imagen del backend (`ghcr.io/iflorido/autorent-backend:latest`),
  comando de inicio `/app/celery-worker.sh`. Mismas variables que el backend.
- **celery-beat**: misma imagen del backend, comando `/app/celery-beat.sh`.

### Variables Redis/Celery (en backend, celery y celery-beat)

Como los contenedores en Plesk no comparten red, se conecta por IP del VPS.
La contraseña va en la propia URL (usuario vacío -> `redis://:PASSWORD@...`):

```
REDIS_URL=redis://:TU_PASSWORD_REDIS@217.154.183.21:6379/0
CELERY_BROKER_URL=redis://:TU_PASSWORD_REDIS@217.154.183.21:6379/0
CELERY_RESULT_BACKEND=redis://:TU_PASSWORD_REDIS@217.154.183.21:6379/1
```

### Seguridad de Redis

- **Contraseña (requirepass)**: imprescindible. Cierra Redis aunque el puerto
  6379 quede accesible. Generar con:
  `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Firewall**: Docker puentea iptables/UFW al publicar puertos, así que una
  regla de firewall de Plesk sobre el 6379 puede no surtir efecto. La forma
  efectiva de no exponer Redis es publicarlo solo en local
  (`127.0.0.1:6379:6379`) y que los contenedores usen el gateway Docker
  (`172.17.0.1`) en las variables. Con la contraseña puesta, esta capa es
  opcional pero recomendable.

## Red Docker para comunicación entre contenedores (autorent_net)

En la red bridge por defecto de Docker los contenedores NO se resuelven por
nombre, solo por IP (y las IPs cambian al reiniciar). Por eso se usa una red
personalizada `autorent_net`, donde Docker sí da resolución DNS por nombre:
así Redis es siempre alcanzable como `autorent-redis`.

### Variables Redis (usando el nombre de contenedor)

En backend, celery y celery-beat:

```
REDIS_URL=redis://:PASSWORD@autorent-redis:6379/0
CELERY_BROKER_URL=redis://:PASSWORD@autorent-redis:6379/0
CELERY_RESULT_BACKEND=redis://:PASSWORD@autorent-redis:6379/1
```

### Problema: Plesk saca los contenedores de la red al recrearlos

Cada despliegue (cambio de imagen o variables) recrea el contenedor y lo
desconecta de `autorent_net` (Plesk no gestiona esa red). Solución: el script
`scripts/ensure-network.sh` reconecta lo que falte. Es idempotente.

### Instalación del script en el VPS

```sh
# Copiar el script al VPS (ej. a /opt/autorent/)
mkdir -p /opt/autorent
cp scripts/ensure-network.sh /opt/autorent/
chmod +x /opt/autorent/ensure-network.sh

# Ejecutarlo manualmente tras cada despliegue:
/opt/autorent/ensure-network.sh
```

### Cron cada 3 minutos (red de seguridad automática)

```sh
crontab -e
```

Añadir la línea:

```
*/3 * * * * /opt/autorent/ensure-network.sh >> /var/log/autorent-network.log 2>&1
```

Así, aunque un despliegue saque un contenedor de la red, en menos de 3
minutos el cron lo reconecta solo. El log queda en /var/log/autorent-network.log.