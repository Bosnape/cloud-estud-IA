# Sesión 4 · La misma API, tres formas de construirla

A, B y C comparten código, `requirements.txt` y la imagen base `python:3.13.18-slim-bookworm` fijada por digest. El runner de las tres es `ubuntu-24.04`.

`psycopg2` se instala con `--no-binary=psycopg2`. No hay wheel: hay que compilar con gcc. Eso es lo que hace visible el multi-stage.

| Variante | Dockerfile | Caché |
|---|---|---|
| A | `Dockerfile.a` | ninguna (`--no-cache`). gcc y `libpq-dev` se quedan en la imagen final |
| B | `Dockerfile.b` | ninguna (`--no-cache`). La etapa final solo tiene el runtime y `libpq5` |
| C | el mismo `Dockerfile.b` | `type=gha`, `scope=estudia-sesion4-variante-c`, `mode=max` |

`variante-c.Dockerfile` no se construye. Está en el árbol para que se vea que C no tiene otra receta. No lleva sufijo `.c`: Sonar lo analizaría como código C y el job del repositorio falla.

`mode=max` guarda también las capas intermedias. Sin eso, la etapa que compila no vuelve a usarse y la segunda corrida de C no se nota.

El workflow es [`.github/workflows/sesion-4-comparar-imagenes.yml`](../../../.github/workflows/sesion-4-comparar-imagenes.yml). Corre con *workflow dispatch* y en cada push a la rama del PR que toque esta carpeta. La matriz mide segundos y tamaño, y el job `resumen` escribe la tabla en el summary del job.

Acciones fijadas al revisarlas el 18 de noviembre de 2026:

- `actions/checkout@v7.0.1`
- `docker/setup-buildx-action@v4.4.1`
- `docker/build-push-action@v7.4.0`
- `actions/upload-artifact@v7.0.2`
- `actions/download-artifact@v8.0.2`

La atestación de procedencia va apagada (`provenance: false`) para poder cargar la imagen en el daemon y leer `.Size`. No cambia las capas de la aplicación.

Para repetir la corrida tibia: cambia solo un archivo bajo `app/` (una cadena alcanza) y vuelve a lanzar el workflow. No toques el Dockerfile ni las dependencias: si no, la caché de C no tiene nada que reutilizar.

Los números de las corridas de este repositorio, cuando existen, están en [`../resultados.md`](../resultados.md). Si el archivo no está, la corrida todavía no se archivó: el summary del job es la fuente.
