# AutoRent

Plataforma integral de alquiler de vehículos (turismos, furgonetas y campers) con seguimiento GPS de flota en tiempo real, gestión de reservas, verificación documental, generación automática de contratos y panel de administración.

AutoRent está construida como un sistema de **microservicios** sobre un único dominio, con despliegue continuo mediante Docker y GitHub Actions.

---

## Tabla de contenidos

- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Módulos funcionales](#módulos-funcionales)
- [Puesta en marcha (desarrollo local)](#puesta-en-marcha-desarrollo-local)
- [Variables de entorno](#variables-de-entorno)
- [Tareas programadas](#tareas-programadas)
- [Telemetría GPS](#telemetría-gps)
- [Despliegue](#despliegue)

---

## Arquitectura

El sistema se compone de seis servicios independientes, cada uno en su propio contenedor, coordinados tras un proxy inverso que enruta cada petición según su ruta:

| Servicio | Rol | Puerto |
|----------|-----|--------|
| `backend` | API REST (Django + DRF) y panel de administración. Dueño del esquema de datos. | 8072 |
| `api` | Ingesta GPS de alta frecuencia (FastAPI + asyncpg). | 8073 |
| `frontend` | Aplicación web SPA (React + Vite). | 8074 |
| `celery` | Worker de tareas en segundo plano (contratos, telemetría, correos). | — |
| `celery-beat` | Planificador de tareas periódicas. | — |
| `redis` | Broker de mensajes y caché. | 6379 |

La base de datos **PostgreSQL** es compartida: Django es el propietario del esquema (define modelos y migraciones) y FastAPI actúa como inquilino que solo inserta posiciones GPS y delega su procesamiento.

### Flujo de la ingesta GPS

```
Dispositivo Teltonika
        │  (trama decodificada + token)
        ▼
   FastAPI /gps/ingesta/  ──►  inserta posición (asyncpg)
        │
        ▼
   Redis (cola Celery)
        │
        ▼
   Worker Django  ──►  detecta eventos, driver score, alertas, mantenimiento
```

FastAPI responde de inmediato tras guardar la posición y encola el procesamiento en segundo plano, de modo que la ingesta nunca se bloquea aunque lleguen muchas tramas por minuto.

---

## Stack tecnológico

**Backend**
- Python 3.12, Django 5.1, Django REST Framework
- FastAPI (microservicio GPS), asyncpg
- Celery + Celery Beat
- Gunicorn / Uvicorn

**Frontend**
- React 18, TypeScript, Vite
- Tailwind CSS, React Router, Axios

**Datos e infraestructura**
- PostgreSQL, Redis
- Docker, GitHub Actions (CI/CD)
- Nginx / Plesk como proxy inverso

**Telemetría y documentos**
- Dispositivos Teltonika (protocolo Codec 8)
- Leaflet + OpenStreetMap / CARTO para los mapas
- ReportLab para la generación de contratos en PDF

---

## Estructura del repositorio

```
autorent/
├── backend/              # Django: API REST, admin, modelos, tareas Celery
│   ├── autorent/         # App principal (reservas, flota, telemetría)
│   │   ├── models/       # flota, reserva, telemetria, vehiculo
│   │   ├── migrations/
│   │   ├── tasks.py      # tareas Celery
│   │   ├── contratos.py  # generación de PDF
│   │   └── notificaciones.py
│   ├── core/             # Configuración del sitio, sedes, tema
│   ├── config/           # settings, celery, urls
│   ├── simulador_gps*.py # simuladores de telemetría (uso local)
│   └── requirements.txt
├── api/                  # FastAPI: ingesta de telemetría GPS
│   └── main.py
├── frontend/             # React + Vite
│   └── src/
│       ├── pages/        # Home, Modelos, Vehiculo, Reserva, Stack, etc.
│       ├── components/
│       ├── lib/          # cliente API y utilidades
│       └── types/
├── redis/
├── scripts/
├── docker-compose.yml
└── DEPLOY.md             # guía detallada de despliegue en Plesk
```

---

## Módulos funcionales

**Motor de reservas.** Asistente multipaso con conductores adicionales, validación de requisitos por categoría de vehículo, extras con precio congelado, y recálculo del precio siempre en el servidor dentro de una transacción atómica.

**Horarios de sede y suplementos.** Cada sede define franjas horarias configurables por día (horario partido, días cerrados) y un suplemento por recogida o entrega fuera de horario. El cliente elige hora de recogida y entrega; si caen fuera del horario de su sede, el suplemento se aplica automáticamente (calculado en servidor).

**Verificación documental.** Subida de documentación mediante enlace mágico sin registro, almacenamiento fuera del alcance público, y flujo de revisión con aprobación o rechazo y aviso automático al cliente.

**Contratos automáticos.** Generación del contrato en PDF al confirmar la reserva, con todas las condiciones, desglose económico (incluido el suplemento fuera de horario) y huella de integridad SHA-256.

**Seguimiento GPS de flota.** Dispositivos Teltonika enlazados por IMEI que reportan posición, velocidad, odómetro y combustible, con un dashboard de mapa en tiempo real integrado en el panel de gestión.

**Driver score y alertas.** Detección de frenazos, acelerones, curvas bruscas y excesos de velocidad (según el límite de cada categoría) mediante acelerómetro, con puntuación de conducción por vehículo y por reserva, y alertas en tiempo real.

**Mantenimiento predictivo.** Reglas por kilometraje real (odómetro) y por fecha (ITV) que generan avisos automáticos al alcanzar el umbral.

**Notificaciones por correo.** Confirmación de reserva, documentos, envío de contrato y recordatorios de recogida (48 h y 24 h antes), con backend SMTP configurable.

---

## Puesta en marcha (desarrollo local)

Requisitos: Docker y Docker Compose. Para trabajar fuera de contenedores: Python 3.12, Node 20 y PostgreSQL.

### Con Docker Compose

```bash
# Crea un archivo .env en la raíz con las variables de la sección siguiente

# Levanta todos los servicios
docker compose up --build
```

Servicios disponibles: frontend en `http://localhost:8074`, API REST y admin en `http://localhost:8072`, ingesta GPS en `http://localhost:8073`.

### Backend sin Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend sin Docker

```bash
cd frontend
npm install
npm run dev
```

> **Nota sobre la build:** el `target` de TypeScript es ES2020. Evita sintaxis más reciente (por ejemplo el operador `??=`) en el código que vaya a compilarse, o la build de CI fallará.

---

## Variables de entorno

El backend y el servicio FastAPI comparten la configuración de base de datos. Las variables principales:

| Variable | Servicio | Descripción |
|----------|----------|-------------|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | backend, api | Conexión a PostgreSQL |
| `CELERY_BROKER_URL` | backend, api, celery | URL de Redis (p. ej. `redis://autorent-redis:6379/0`) |
| `GPS_INGEST_TOKEN` | backend, api | Token que valida la ingesta de telemetría |
| `DJANGO_SECRET_KEY` | backend | Clave secreta de Django |
| `DJANGO_DEBUG` | backend | `True`/`False` |
| `ALLOWED_HOSTS` | backend | Dominios permitidos |

La configuración completa de despliegue, volúmenes y reglas de proxy está documentada en [`DEPLOY.md`](./DEPLOY.md).

---

## Tareas programadas

Gestionadas por Celery Beat y configurables desde el admin (`django_celery_beat`):

- **Limpieza de posiciones GPS:** borra a diario (3:30) las posiciones con más de 30 días, para acotar el tamaño de la base de datos.
- **Recordatorios de recogida:** cada día a las 9:00 avisa a los clientes con recogida prevista en 48 h y en 24 h.

Las zonas horarias están fijadas a `Europe/Madrid`, por lo que las horas configuradas son hora española.

---

## Telemetría GPS

La ingesta se realiza en `POST /gps/ingesta/` (servicio FastAPI), validada con la cabecera `X-Ingest-Token`. El endpoint de Django se mantiene como respaldo.

Para pruebas en local existen dos simuladores que envían tramas sintéticas:

```bash
cd backend
# Simulador básico
python simulador_gps.py --url <URL>/gps/ingesta/ --token <TOKEN> --imeis <IMEI1>,<IMEI2> --intervalo 5

# Simulador v2 con perfiles de conducción (provoca eventos)
python simulador_gps_v2.py --url <URL>/gps/ingesta/ --token <TOKEN> --imeis <IMEI> --perfiles agresivo,tranquilo
```

---

## Despliegue

El despliegue es continuo: cada push construye las imágenes de los contenedores mediante GitHub Actions, las publica en el registro de contenedores, y el servidor (Plesk) recoge la nueva versión y recarga los servicios. Las migraciones de base de datos se aplican automáticamente al arrancar (gestionadas por `entrypoint.sh` según el rol del contenedor).

Consulta [`DEPLOY.md`](./DEPLOY.md) para la guía detallada: mapa de puertos, variables de entorno en Plesk, volúmenes para backups y reglas de proxy.

---

## Licencia y autoría

Proyecto desarrollado por **Ignacio Florido** ([iflorido.es](https://iflorido.es)) bajo la marca **AutomaWorks**.