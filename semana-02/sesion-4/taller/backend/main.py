import logging
import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from psycopg import Error as PsycopgError

logger = logging.getLogger("uvicorn.error")


def conectar() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "La API usará la base en %s:%s.",
        os.environ.get("POSTGRES_HOST", "(sin definir)"),
        os.environ.get("POSTGRES_PORT", "5432"),
    )
    yield


app = FastAPI(title="Inventario Estud-IA", lifespan=lifespan)


class ItemNuevo(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    nota: str | None = Field(default=None, max_length=500)


class Item(BaseModel):
    id: int
    nombre: str
    nota: str | None
    creado_en: str


def fila_a_item(fila: tuple) -> Item:
    return Item(id=fila[0], nombre=fila[1], nota=fila[2], creado_en=fila[3].isoformat())


@app.get("/health")
def health():
    try:
        with conectar() as conn:
            conn.execute("SELECT 1")
    except PsycopgError:
        return JSONResponse(status_code=503, content={"status": "error"})
    return {"status": "ok"}


@app.get("/items", response_model=list[Item])
def listar_items():
    try:
        with conectar() as conn:
            filas = conn.execute(
                "SELECT id, nombre, nota, creado_en FROM items ORDER BY id"
            ).fetchall()
    except PsycopgError as exc:
        raise HTTPException(status_code=503, detail="La base no está disponible") from exc
    return [fila_a_item(fila) for fila in filas]


@app.post("/items", response_model=Item, status_code=201)
def crear_item(item: ItemNuevo):
    try:
        with conectar() as conn:
            fila = conn.execute(
                """
                INSERT INTO items (nombre, nota)
                VALUES (%s, %s)
                RETURNING id, nombre, nota, creado_en
                """,
                (item.nombre, item.nota),
            ).fetchone()
            conn.commit()
    except PsycopgError as exc:
        raise HTTPException(status_code=503, detail="La base no está disponible") from exc
    return fila_a_item(fila)
