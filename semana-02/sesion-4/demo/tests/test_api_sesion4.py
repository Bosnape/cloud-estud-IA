import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

_ruta = Path(__file__).resolve().parents[1] / "app" / "main.py"
_spec = importlib.util.spec_from_file_location("api_sesion4", _ruta)
main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(main)


def test_health():
    respuesta = TestClient(main.app).get("/health")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["status"] == "ok"
    assert cuerpo["mensaje"] == main.MENSAJE
    assert isinstance(cuerpo["psycopg2"], str)
