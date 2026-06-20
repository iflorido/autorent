FROM redis:7-alpine

# Imagen de Redis con configuración propia + contraseña por variable.
# Necesaria porque Plesk no permite sobrescribir el comando de inicio.
COPY redis.conf /usr/local/etc/redis/redis.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 6379

ENTRYPOINT ["/entrypoint.sh"]
