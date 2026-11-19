import socket
import sys

import comprobar_nombre


def test_sin_argumentos(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["comprobar_nombre.py"])
    assert comprobar_nombre.main() == 2
    assert "uso:" in capsys.readouterr().err


def test_resuelve(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["comprobar_nombre.py", "db", "5432"])
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.8", 5432))],
    )
    assert comprobar_nombre.main() == 0
    assert "10.0.0.8" in capsys.readouterr().out


def test_no_resuelve(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["comprobar_nombre.py", "db"])

    def falla(*args):
        raise socket.gaierror("no existe")

    monkeypatch.setattr(socket, "getaddrinfo", falla)
    assert comprobar_nombre.main() == 1
    assert "no resuelve" in capsys.readouterr().out
