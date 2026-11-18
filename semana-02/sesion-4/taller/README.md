# Taller · imagen de una etapa, y quién puede publicarla

La plantilla es el backend de la sesión 3, el de una sola etapa: [`semana-02/sesion-3/backend`](../../sesion-3/backend). No hay una segunda copia del código: el taller construye esa misma carpeta. El workflow inicial, que solo corre si lo lanzas a mano, está en [`.github/workflows/sesion-4-taller.yml`](../../../.github/workflows/sesion-4-taller.yml): construye esa imagen y anota segundos y MiB en el summary.

La hoja [`oidc-errores.md`](oidc-errores.md) trae un workflow y dos políticas (confianza del rol y permisos del registro) con tres errores. Las correcciones están en [`soluciones.md`](soluciones.md). Conviene intentar la hoja antes de abrirlas.

## Qué entregas

| | MiB | Segundos de build | Clave guardada |
|---|---:|---:|---|
| Antes | | | |
| Después | | | |

El antes es esta plantilla. El después es tu mejora (otra etapa, caché, o las dos). La clave guardada es el id de la imagen o el `scope` de la caché que sí se reutilizó. Copia del log las líneas que digan `CACHED`.

## Plan B sin AWS: GHCR y `GITHUB_TOKEN`

No hace falta un rol de IAM. El token del propio workflow publica en GitHub Container Registry si el job pide `packages: write`.

El archivo listo, con un candado para no publicarlo sin querer, es [`.github/workflows/sesion-4-taller-ghcr.yml`](../../../.github/workflows/sesion-4-taller-ghcr.yml). La parte que importa:

```yaml
permissions:
  contents: read
  packages: write

steps:
  - uses: docker/login-action@v4.8.0
    with:
      registry: ghcr.io
      username: ${{ github.actor }}
      password: ${{ secrets.GITHUB_TOKEN }}
```

El nombre de la imagen tiene que ir en minúsculas (`ghcr.io/<owner>/<repo>/estudia-taller`). El workflow lo pasa a minúsculas antes de etiquetar. Lanzarlo de verdad sube una imagen al registro del repositorio: por eso pide escribir `publicar` en el input.

## Plan B sin Actions: dos builds locales con BuildKit

Desde `semana-02/sesion-3/backend`:

```bash
DOCKER_BUILDKIT=1 docker build --progress=plain --no-cache -t estudia-taller:antes .
# anota segundos, MiB y el id
docker image inspect --format '{{.Size}} {{.Id}}' estudia-taller:antes

# cambia solo una línea de main.py
DOCKER_BUILDKIT=1 docker build --progress=plain -t estudia-taller:despues .
docker image inspect --format '{{.Size}} {{.Id}}' estudia-taller:despues
```

El segundo build no lleva `--no-cache`. En el log, los pasos que no se repiten dicen `CACHED`: esa es la clave que se guardó. El id de la imagen cambia, porque cambió el código; el id de las capas de `pip install` no.

BuildKit es el builder por defecto en Docker actual. `DOCKER_BUILDKIT=1` deja explícito el contrato aunque alguien tenga el builder clásico.
