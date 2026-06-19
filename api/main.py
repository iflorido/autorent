"""
AutoRent — API Teltonika (FastAPI).

De momento es un esqueleto: expone endpoints de salud para que la ruta
/gps/ responda en producción. La ingesta real del protocolo Teltonika
(Codec 8 / 8E) y el almacenamiento GPS se añadirán en la fase GPS.

Va detrás del proxy de Plesk en la ruta /gps/, por eso usamos
root_path="/gps" para que la documentación y las URLs se generen bien.
"""
import os

from fastapi import FastAPI

ROOT_PATH = os.getenv("API_ROOT_PATH", "/gps")

app = FastAPI(
    title="AutoRent Teltonika API",
    version="0.1.0",
    root_path=ROOT_PATH,
)


@app.get("/")
def root():
    return {
        "service": "AutoRent Teltonika API",
        "status": "ok",
        "version": "0.1.0",
        "note": "Ingesta GPS pendiente (fase Teltonika).",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}