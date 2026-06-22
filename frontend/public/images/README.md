# Imágenes de diseño del frontend

Imágenes fijas de la web (hero, fondos, ilustraciones). Van aquí y se
referencian desde la raíz, p. ej. `/images/hero.jpg`.

Vite copia todo `public/` a la raíz del build, así que estas imágenes
viajan DENTRO de la imagen Docker del frontend.

NO confundir con `/media/` (fotos de vehículos que sube el admin, servidas
por Nginx desde data/media en el VPS).

Imágenes esperadas:
  - hero.jpg   -> fondo del hero de la Home (recomendado ~1920x1080)
