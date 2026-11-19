import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

_ruta = Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("api_sesion3", _ruta)
main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(main)


CREADO = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


class Resultado:
    def __init__(self, fila=None, filas=None):
        self._fila = fila
        self._filas = filas or []

    def fetchone(self):
        return self._fila

    def fetchall(self):
        return self._filas


class Conexion:
    def __init__(self, fila=None, filas=None, error=False):
        self.fila = fila
        self.filas = filas
        self.error = error
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        if self.error:
            raise psycopg.OperationalError("no hay base")
        return Resultado(self.fila, self.filas)

    def commit(self):
        self.committed = True


@pytest.fixture
def cliente(monkeypatch):
    for clave, valor in {
        "POSTGRES_HOST": "db",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "inventario",
        "POSTGRES_USER": "estudia",
        "POSTGRES_PASSWORD": "clave-ficticia-de-ejemplo",
    }.items():
        monkeypatch.setenv(clave, valor)
    with TestClient(main.app) as cliente_http:
        yield cliente_http


def test_conectar_usa_el_entorno(monkeypatch):
    capturado = {}

    def falso_connect(**kwargs):
        capturado.update(kwargs)
        return Conexion()

    monkeypatch.setattr(main.psycopg, "connect", falso_connect)
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_DB", "inventario")
    monkeypatch.setenv("POSTGRES_USER", "estudia")
    monkeypatch.setenv("POSTGRES_PASSWORD", "clave-ficticia-de-ejemplo")
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    main.conectar()
    assert capturado["host"] == "db"
    assert capturado["port"] == "5432"


def test_health_ok(monkeypatch, cliente):
    monkeypatch.setattr(main, "conectar", lambda: Conexion())
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_health_sin_base(monkeypatch, cliente):
    monkeypatch.setattr(main, "conectar", lambda: Conexion(error=True))
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 503
    assert respuesta.json()["status"] == "error"


def test_lista_y_crea(monkeypatch, cliente):
    conexion = Conexion(
        fila=(1, "cable", "nota", CREADO),
        filas=[(1, "cable", "nota", CREADO)],
    )
    monkeypatch.setattr(main, "conectar", lambda: conexion)
    creado = cliente.post("/items", json={"nombre": "cable", "nota": "nota"})
    assert creado.status_code == 201
    assert creado.json()["nombre"] == "cable"
    assert conexion.committed
    lista = cliente.get("/items")
    assert lista.status_code == 200
    assert lista.json()[0]["id"] == 1


def test_lista_vacia_sin_nota(monkeypatch, cliente):
    monkeypatch.setattr(
        main,
        "conectar",
        lambda: Conexion(filas=[(2, "conector", None, CREADO)]),
    )
    cuerpo = cliente.get("/items").json()
    assert cuerpo[0]["nota"] is None


def test_errores_de_base(monkeypatch, cliente):
    monkeypatch.setattr(main, "conectar", lambda: Conexion(error=True))
    assert cliente.get("/items").status_code == 503
    assert cliente.post("/items", json={"nombre": "cable"}).status_code == 503
