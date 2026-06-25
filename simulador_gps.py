#!/usr/bin/env python3
"""
simulador_gps.py — Simula dispositivos Teltonika enviando telemetría.

Sin hardware real, este script emula uno o varios dispositivos que se mueven y
envían sus datos (ya decodificados) al endpoint de ingesta por HTTP. Sirve para
desarrollar y probar el dashboard de flota.

Uso:
    python simulador_gps.py \
        --url https://autorent.automaworks.es/api/gps/ingesta/ \
        --token <GPS_INGEST_TOKEN> \
        --imeis 356307042441013,356307042441020 \
        --intervalo 5

Cada IMEI debe existir como Dispositivo activo en la BD, asignado a un vehículo.
"""
import argparse
import json
import math
import random
import sys
import time
from datetime import datetime, timezone
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError


class VehiculoSimulado:
    """Un vehículo que se mueve por un recorrido con estado realista."""

    def __init__(self, imei, lat0, lon0):
        self.imei = imei
        self.lat = lat0
        self.lon = lon0
        self.rumbo = random.uniform(0, 360)       # grados
        self.velocidad = 0.0                       # km/h
        self.ignicion = False
        self.odometro = random.randint(20_000, 180_000)  # km
        self.combustible = random.uniform(40, 95)  # %
        self.parado_desde = time.time()
        self.en_ruta = False

    def _quizas_cambiar_estado(self):
        """Alterna entre parado y en ruta de forma aleatoria."""
        if self.en_ruta:
            # Pequeña probabilidad de parar.
            if random.random() < 0.05:
                self.en_ruta = False
                self.ignicion = False
                self.velocidad = 0.0
        else:
            # Probabilidad de arrancar.
            if random.random() < 0.2:
                self.en_ruta = True
                self.ignicion = True

    def paso(self, segundos):
        """Avanza la simulación un intervalo y devuelve la trama de telemetría."""
        self._quizas_cambiar_estado()

        if self.en_ruta:
            # Velocidad objetivo variable (zona urbana/carretera).
            objetivo = random.uniform(20, 110)
            # Suavizar el cambio de velocidad.
            self.velocidad += (objetivo - self.velocidad) * 0.3
            self.velocidad = max(0.0, min(120.0, self.velocidad))
            # Variar ligeramente el rumbo (curvas).
            self.rumbo = (self.rumbo + random.uniform(-15, 15)) % 360

            # Desplazamiento según velocidad y rumbo.
            dist_km = self.velocidad * (segundos / 3600.0)
            self.odometro += dist_km
            rad = math.radians(self.rumbo)
            # Aproximación: 1 grado lat ≈ 111 km; lon escala con cos(lat).
            self.lat += (dist_km / 111.0) * math.cos(rad)
            self.lon += (dist_km / (111.0 * math.cos(math.radians(self.lat)))) * math.sin(rad)
            # Consumo de combustible.
            self.combustible = max(5.0, self.combustible - dist_km * 0.05)
        else:
            self.velocidad = 0.0

        # Acelerómetro: ruido + picos ocasionales (frenazo/acelerón).
        acel_x = random.gauss(0, 0.05)
        if self.en_ruta and random.random() < 0.05:
            acel_x = random.choice([-1, 1]) * random.uniform(0.4, 0.9)  # evento brusco

        return {
            "imei": self.imei,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6),
            "altitud": round(random.uniform(0, 200), 1),
            "rumbo": round(self.rumbo, 1),
            "satelites": random.randint(7, 12),
            "velocidad": round(self.velocidad, 1),
            "ignicion": self.ignicion,
            "movimiento": self.velocidad > 1,
            "odometro": int(self.odometro),
            "nivel_combustible": round(self.combustible, 1),
            "voltaje_bateria": round(random.uniform(12.2, 14.4), 1),
            "acel_x": round(acel_x, 3),
            "acel_y": round(random.gauss(0, 0.05), 3),
            "acel_z": round(random.gauss(1.0, 0.03), 3),
        }


def enviar(url, token, trama):
    cuerpo = json.dumps(trama).encode("utf-8")
    req = urlrequest.Request(url, data=cuerpo, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Ingest-Token", token)
    try:
        with urlrequest.urlopen(req, timeout=10) as resp:
            return resp.status
    except HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode(errors='ignore')[:120]}"
    except URLError as e:
        return f"ERROR: {e.reason}"


# Puntos de partida (zona de Cádiz/San Fernando como ejemplo).
PUNTOS_BASE = [
    (36.4626, -6.1900),
    (36.4750, -6.2000),
    (36.5297, -6.2920),
    (36.6850, -6.1300),
]


def main():
    p = argparse.ArgumentParser(description="Simulador de dispositivos Teltonika.")
    p.add_argument("--url", required=True, help="Endpoint de ingesta")
    p.add_argument("--token", required=True, help="GPS_INGEST_TOKEN")
    p.add_argument("--imeis", required=True, help="IMEIs separados por coma")
    p.add_argument("--intervalo", type=float, default=5.0, help="Segundos entre envíos")
    args = p.parse_args()

    imeis = [x.strip() for x in args.imeis.split(",") if x.strip()]
    vehiculos = [
        VehiculoSimulado(imei, *PUNTOS_BASE[i % len(PUNTOS_BASE)])
        for i, imei in enumerate(imeis)
    ]
    print(f"Simulando {len(vehiculos)} dispositivo(s). Ctrl+C para parar.")
    print(f"Enviando a {args.url} cada {args.intervalo}s\n")

    try:
        while True:
            for veh in vehiculos:
                trama = veh.paso(args.intervalo)
                estado = enviar(args.url, args.token, trama)
                marca = "🟢" if veh.en_ruta else "⚪"
                print(f"{marca} {veh.imei} | {trama['lat']:.4f},{trama['lon']:.4f} "
                      f"| {trama['velocidad']:5.1f} km/h | od {trama['odometro']} km "
                      f"| -> {estado}")
            print("-" * 60)
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nSimulador detenido.")
        sys.exit(0)


if __name__ == "__main__":
    main()