FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias de sistema:
#  - libpq-dev + gcc      -> compilar/usar psycopg2
#  - libjpeg/zlib         -> Pillow (fotos de vehículos)
#  - fonts/liberation     -> reportlab (PDFs de facturas)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# entrypoint: migra, recolecta estáticos y lanza Gunicorn
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8072

ENTRYPOINT ["/entrypoint.sh"]