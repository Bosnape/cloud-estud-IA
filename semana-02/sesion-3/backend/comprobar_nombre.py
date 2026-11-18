"""Resuelve un nombre DNS desde dentro del contenedor.

No usa ping ni curl: la imagen del backend no los trae.

    python comprobar_nombre.py db
    python comprobar_nombre.py frontend 80
"""

import socket
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("uso: python comprobar_nombre.py NOMBRE [PUERTO]", file=sys.stderr)
        return 2
    nombre = sys.argv[1]
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else None
    try:
        infos = socket.getaddrinfo(nombre, puerto)
    except socket.gaierror as exc:
        print(f"{nombre} no resuelve: {exc}")
        return 1
    direcciones = sorted({item[4][0] for item in infos})
    print(f"{nombre} resuelve a {', '.join(direcciones)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
