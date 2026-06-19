FROM nginx:1.27-alpine

# De momento servimos un index estático de andamiaje.
# En la fase frontend esto pasará a un multi-stage:
#   1) node build (vite build)
#   2) copiar /dist a /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
