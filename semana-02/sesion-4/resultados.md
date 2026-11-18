# Resultados de la matriz · sesión 4

Números sacados del job `Tabla en el summary`, no estimados. Runner `ubuntu-24.04`. El tiempo es el de la etapa `docker/build-push-action`. El tamaño es `docker image inspect --format '{{.Size}}'`, en MiB (1024²).

El cambio entre las dos corridas es una sola cadena en `demo/app/main.py`. El Dockerfile y `requirements.txt` no se tocaron.

## Fría

[Corrida 44406451515](https://github.com/RafaelCampoTech/Estud-IA_cloud/actions/runs/44406451515), evento `push`, commit `28972c1`.

| Variante | Dockerfile | Caché | Segundos | MiB | Bytes |
|---|---|---|---:|---:|---:|
| A | `Dockerfile.a` | sin caché (`--no-cache`) | 33.38 | 422.8 | 443301010 |
| B | `Dockerfile.b` | sin caché (`--no-cache`) | 25.80 | 135.0 | 141541941 |
| C | `Dockerfile.b` | `type=gha`, `scope=estudia-sesion4-variante-c`, `mode=max` | 63.33 | 135.0 | 141563330 |

## Tibia

[Corrida 44406836560](https://github.com/RafaelCampoTech/Estud-IA_cloud/actions/runs/44406836560), evento `push`, commit `5ea13a2`.

| Variante | Dockerfile | Caché | Segundos | MiB | Bytes |
|---|---|---|---:|---:|---:|
| A | `Dockerfile.a` | sin caché (`--no-cache`) | 44.86 | 422.7 | 443276224 |
| B | `Dockerfile.b` | sin caché (`--no-cache`) | 21.40 | 135.0 | 141563343 |
| C | `Dockerfile.b` | `type=gha`, `scope=estudia-sesion4-variante-c`, `mode=max` | 12.59 | 135.0 | 141563343 |

En la tibia, el log de C marca `CACHED` la instalación de `psycopg2` (la capa que compila). C es la más rápida de esa corrida. B y C pesan menos que A en las dos.

El mismo push también dispara `pull_request`, así que hubo una corrida gemela de cada commit. La fría gemela es la [44406460859](https://github.com/RafaelCampoTech/Estud-IA_cloud/actions/runs/44406460859) y la tibia gemela es la [44406848825](https://github.com/RafaelCampoTech/Estud-IA_cloud/actions/runs/44406848825). Las tablas de arriba son las del evento `push`, que es la secuencia fría y luego tibia.
