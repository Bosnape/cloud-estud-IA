"""La misma API en las tres variantes. El health importa psycopg2 para
obligar a que la librería compilada esté en la imagen final."""

import psycopg2
from fastapi import FastAPI

app = FastAPI(title="Estud-IA · sesión 4")

MENSAJE = "API de la sesión 4, revisión 2"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mensaje": MENSAJE,
        "psycopg2": psycopg2.__version__,
    }
