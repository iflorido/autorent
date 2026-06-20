#!/bin/sh
set -e
echo "==> Arrancando Celery beat (scheduler) ..."
exec celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler