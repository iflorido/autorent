#!/bin/sh
set -e

# Inyecta la contraseña desde la variable de entorno REDIS_PASSWORD.
# Si no se define, Redis arranca SIN contraseña (no recomendado en prod).
if [ -n "$REDIS_PASSWORD" ]; then
    echo "==> Redis con contraseña (requirepass) desde variable de entorno."
    exec redis-server /usr/local/etc/redis/redis.conf --requirepass "$REDIS_PASSWORD"
else
    echo "!! AVISO: REDIS_PASSWORD no definida. Redis arranca SIN contraseña."
    exec redis-server /usr/local/etc/redis/redis.conf
fi