#!/bin/sh
set -e

echo "==> Esperando a la base de datos en ${DB_HOST}:${DB_PORT} ..."
# Espera activa hasta que el puerto de Postgres responda (máx ~60s)
i=0
while ! python -c "import socket,sys; s=socket.socket(); s.settimeout(2); sys.exit(0) if s.connect_ex(('${DB_HOST}', int('${DB_PORT:-5432}')))==0 else sys.exit(1)" 2>/dev/null; do
    i=$((i+1))
    if [ "$i" -ge 30 ]; then
        echo "!! No se pudo conectar a la BD tras 60s. Revisa DB_HOST/DB_PORT y pg_hba.conf."
        break
    fi
    sleep 2
done

echo "==> Aplicando migraciones ..."
python manage.py migrate --noinput

echo "==> Asegurando superusuario (si hay variables) ..."
python manage.py ensure_superuser

echo "==> Recolectando estáticos ..."
python manage.py collectstatic --noinput

echo "==> Arrancando Gunicorn ..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8072 \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile -