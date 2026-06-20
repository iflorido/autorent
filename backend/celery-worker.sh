#!/bin/sh
set -e
echo "==> Esperando a Redis en ${CELERY_BROKER_URL} ..."
echo "==> Arrancando Celery worker ..."
exec celery -A config worker -l info --concurrency=${CELERY_CONCURRENCY:-2}