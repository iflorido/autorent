#!/usr/bin/env python3
"""
simulador_gps_v2.py — Simula dispositivos Teltonika con perfiles de conducción.

Versión 2: además de mover los vehículos, asigna a cada uno un PERFIL de
conducción (tranquilo / normal / agresivo) que genera frenazos, acelerones,
curvas bruscas y excesos de velocidad con distinta frecuencia. Sirve para
probar el Driver Score y las alertas en tiempo real.

Uso:
    python simulador_gps_v2.py \
        --url https://autorent.automaworks.es/api/gps/ingesta/ \
        --token <GPS_INGEST_TOKEN> \
        --imeis 356307042441013,356307042441020 \
        --intervalo 5

Opciones extra:
    --perfiles agresivo,tranquilo   Fuerza el perfil de cada IMEI (en orden).
                                    Si no se indica, se asigna uno aleatorio.
    --vel-max 160                   Velocidad máxima que puede alcanzar (para
                                    provocar excesos). Por defecto 160.

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


# Parámetros por perfil:
#   p_evento: probabilidad por paso de provocar un evento brusco (acelerómetro).
#   p_exceso: probabilidad por paso de pegar un acelerón hacia exceso de velocidad.
#   vel_objetivo: rango de velocidad de crucero que busca el vehículo.
PERFILES = {
    "tranquilo": {"p_evento": 0.02, "p_exceso": 0.01, "vel_objetivo": (20, 85)},
    "normal":    {"p_evento": 0.08, "p_exceso": 0.05, "vel_objetivo": (30, 110)},
    "agresivo":  {"p_evento": 0.28, "p_exceso": 0.30, "vel_objetivo": (60, 150)},
}


class VehiculoSimulado:
    """Vehículo con un perfil de conducción que condiciona sus eventos."""

    def __init__(self, imei, lat0, lon0, perfil, vel_max):
        self.imei = imei
        self.lat = lat0
        self.lon = lon0
        self.perfil = perfil
        self.cfg = PERFILES[perfil]
        self.vel_max = vel_max
        self.rumbo = random.uniform(0, 360)
        self.velocidad = 0.0
        self.ignicion = False
        self.odometro = random.randint(20_000, 180_000)
        self.combustible = random.uniform(40, 95)
        self.en_ruta = False
        self.ultimo_evento = ""

    def _quizas_cambiar_estado(self):
        if self.en_ruta:
            if random.random() < 0.04:
                self.en_ruta = False
                self.ignicion = False
                self.velocidad = 0.0
        else:
            if random.random() < 0.25:
                self.en_ruta = True
                self.ignicion = True

    def paso(self, segundos):
        self._quizas_cambiar_estado()
        self.ultimo_evento = ""

        # Valores base del acelerómetro (ruido suave).
        acel_x = random.gauss(0, 0.05)
        acel_y = random.gauss(0, 0.05)
        acel_z = random.gauss(1.0, 0.03)

        if self.en_ruta:
            vmin, vmax = self.cfg["vel_objetivo"]
            objetivo = random.uniform(vmin, vmax)

            # Exceso de velocidad provocado según el perfil.
            if random.random() < self.cfg["p_exceso"]:
                objetivo = random.uniform(self.vel_max * 0.85, self.vel_max)
                self.ultimo_evento = "EXCESO"

            self.velocidad += (objetivo - self.velocidad) * 0.35
            self.velocidad = max(0.0, min(self.vel_max, self.velocidad))
            self.rumbo = (self.rumbo + random.uniform(-15, 15)) % 360

            # Evento brusco del acelerómetro según el perfil.
            if random.random() < self.cfg["p_evento"]:
                tipo = random.choice(["frenazo", "aceleron", "curva"])
                magnitud = random.uniform(0.5, 1.2)  # supera el umbral (~0.45)
                if tipo == "frenazo":
                    acel_x = -magnitud
                    # Un frenazo brusco baja la velocidad de golpe.
                    self.velocidad = max(0.0, self.velocidad - random.uniform(20, 50))
                elif tipo == "aceleron":
                    acel_x = magnitud
                else:  # curva
                    acel_y = random.choice([-1, 1]) * magnitud
                self.ultimo_evento = tipo.upper() if not self.ultimo_evento else self.ultimo_evento + "+" + tipo.upper()

            # Desplazamiento.
            dist_km = self.velocidad * (segundos / 3600.0)
            self.odometro += dist_km
            rad = math.radians(self.rumbo)
            self.lat += (dist_km / 111.0) * math.cos(rad)
            self.lon += (dist_km / (111.0 * math.cos(math.radians(self.lat)))) * math.sin(rad)
            self.combustible = max(5.0, self.combustible - dist_km * 0.05)
        else:
            self.velocidad = 0.0

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
            "acel_y": round(acel_y, 3),
            "acel_z": round(acel_z, 3),
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


PUNTOS_BASE = [
    (36.4626, -6.1900),
    (36.4750, -6.2000),
    (36.5297, -6.2920),
    (36.6850, -6.1300),
]


def main():
    p = argparse.ArgumentParser(description="Simulador Teltonika v2 (con perfiles).")
    p.add_argument("--url", required=True, help="Endpoint de ingesta")
    p.add_argument("--token", required=True, help="GPS_INGEST_TOKEN")
    p.add_argument("--imeis", required=True, help="IMEIs separados por coma")
    p.add_argument("--intervalo", type=float, default=5.0, help="Segundos entre envíos")
    p.add_argument("--perfiles", default="",
                   help="Perfil por IMEI (tranquilo|normal|agresivo), separado por coma. "
                        "Si falta, se asigna aleatorio.")
    p.add_argument("--vel-max", type=float, default=160.0,
                   help="Velocidad máxima alcanzable (para provocar excesos).")
    args = p.parse_args()

    imeis = [x.strip() for x in args.imeis.split(",") if x.strip()]
    perfiles_arg = [x.strip() for x in args.perfiles.split(",") if x.strip()]

    vehiculos = []
    for i, imei in enumerate(imeis):
        if i < len(perfiles_arg) and perfiles_arg[i] in PERFILES:
            perfil = perfiles_arg[i]
        else:
            perfil = random.choice(list(PERFILES.keys()))
        veh = VehiculoSimulado(imei, *PUNTOS_BASE[i % len(PUNTOS_BASE)], perfil, args.vel_max)
        vehiculos.append(veh)
        print(f"  {imei} -> perfil: {perfil.upper()}")

    print(f"\nSimulando {len(vehiculos)} dispositivo(s). Ctrl+C para parar.")
    print(f"Enviando a {args.url} cada {args.intervalo}s\n")

    try:
        while True:
            for veh in vehiculos:
                trama = veh.paso(args.intervalo)
                estado = enviar(args.url, args.token, trama)
                marca = "🔴" if veh.perfil == "agresivo" else ("🟡" if veh.perfil == "normal" else "🟢")
                evento = f" ⚡{veh.ultimo_evento}" if veh.ultimo_evento else ""
                print(f"{marca} {veh.imei} | {trama['velocidad']:5.1f} km/h "
                      f"| od {trama['odometro']} km | -> {estado}{evento}")
            print("-" * 64)
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nSimulador detenido.")
        sys.exit(0)


if __name__ == "__main__":
    main()