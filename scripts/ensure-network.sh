#!/bin/sh
#
# ensure-network.sh
# -----------------
# Asegura que la red Docker 'autorent_net' existe y que todos los
# contenedores de AutoRent que necesitan comunicarse entre sí están
# conectados a ella.
#
# Por qué existe: Plesk recrea los contenedores en cada despliegue
# (cambio de imagen o de variables) y al recrearlos los saca de las
# redes creadas manualmente. Este script los vuelve a meter.
#
# Uso:
#   - Manual tras un despliegue:  sh /ruta/ensure-network.sh
#   - Automático por cron cada 3 min (ver instrucciones abajo).
#
# Es idempotente: solo conecta lo que falta, no toca lo que ya está bien.

set -eu

NETWORK="autorent_net"

# Contenedores que deben estar en la red (los que hablan entre sí).
# frontend y api no la necesitan; añádelos aquí si en el futuro sí.
CONTAINERS="autorent-redis autorent-backend autorent-celery autorent-celery-beat"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 1. Crear la red si no existe.
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    log "La red $NETWORK no existe. Creándola..."
    docker network create "$NETWORK" >/dev/null
    log "Red $NETWORK creada."
fi

# 2. Conectar cada contenedor que falte.
for c in $CONTAINERS; do
    # ¿Existe el contenedor? (puede no estar creado aún)
    if ! docker inspect "$c" >/dev/null 2>&1; then
        log "AVISO: el contenedor $c no existe todavía. Se omite."
        continue
    fi

    # ¿Está ya en la red?
    if docker inspect "$c" \
        --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
        | grep -qw "$NETWORK"; then
        : # ya conectado, no hacer nada
    else
        log "Conectando $c a $NETWORK ..."
        docker network connect "$NETWORK" "$c"
        log "$c conectado."
    fi
done

log "Comprobación de red completada."