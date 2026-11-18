"""Arma la tabla del job summary a partir de los JSON de la matriz."""

import json
import os
import sys
from pathlib import Path


def main() -> int:
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else "mediciones")
    filas = []
    if raiz.exists():
        for path in sorted(raiz.rglob("*.json")):
            filas.append(json.loads(path.read_text(encoding="utf-8")))
    filas.sort(key=lambda fila: fila["variante"])

    lineas = [
        "## Comparación de imágenes · sesión 4",
        "",
        "Runner `ubuntu-24.04`. La misma base `python:3.13.18-slim-bookworm` por digest en las tres variantes. "
        "El tiempo es el de la etapa `docker/build-push-action` (incluye el arranque de la action, medido igual en A, B y C). "
        "El tamaño es `docker image inspect --format '{{.Size}}'`, en MiB (1024²).",
        "",
    ]
    if not filas:
        lineas.append("No hubo mediciones. Revisa los jobs de la matriz.")
    else:
        lineas.extend(
            [
                "| Variante | Dockerfile | Caché | Segundos | MiB | Bytes |",
                "|---|---|---|---:|---:|---:|",
            ]
        )
        for fila in filas:
            lineas.append(
                "| {variante} | `{dockerfile}` | {cache} | {segundos:.2f} | {mib:.1f} | {bytes} |".format(
                    **fila
                )
            )
        lineas.extend(
            [
                "",
                "Lectura esperada del demo: B y C pesan menos que A, porque el compilador no se queda en la imagen final. "
                "En una segunda corrida, con la caché de C ya guardada y un cambio solo en el código de la aplicación, C debería ser la más rápida. "
                "Los números de arriba son los de esta corrida.",
            ]
        )

    texto = "\n".join(lineas) + "\n"
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as resumen:
            resumen.write(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
