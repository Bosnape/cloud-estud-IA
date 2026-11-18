# Hoja · publicar en ECR con OIDC

Esta hoja es la plantilla con errores. No la corrijas aquí: escribe la corrección en [`soluciones.md`](soluciones.md).

Hay tres problemas. Uno está en el workflow, otro en la política de confianza del rol y otro en los permisos sobre el registro. La cuenta `123456789012`, el rol y el repositorio de ECR son ficticios: no existen y no hay claves en este archivo.

Las actions están en la versión vigente al armar el material (18 de noviembre de 2026). El fallo no es la versión.

## Workflow

```yaml
name: Publicar en ECR

on:
  workflow_dispatch:

jobs:
  publicar:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v7.0.1

      - name: Credenciales de AWS
        uses: aws-actions/configure-aws-credentials@v6.3.0
        with:
          role-to-assume: arn:aws:iam::123456789012:role/estudia-github-ecr-ejemplo
          aws-region: us-east-1

      - name: Login en ECR
        id: ecr
        uses: aws-actions/amazon-ecr-login@v2.2.0

      - name: Build y push
        uses: docker/build-push-action@v7.4.0
        with:
          context: semana-02/sesion-4/taller/backend
          push: true
          provenance: false
          tags: ${{ steps.ecr.outputs.registry }}/estudia-backend:taller
```

## Política de confianza del rol

Permite a GitHub Actions asumir el rol. El proveedor OIDC de la cuenta de ejemplo sería `arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

## Permisos del rol sobre el registro

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ecr:*",
      "Resource": "*"
    }
  ]
}
```

## Qué entregar

Una tabla con el antes y el después de tu propia imagen (la de una etapa y la que hayas mejorado):

| | MiB | Segundos de build | Clave guardada |
|---|---:|---:|---|
| Antes | | | |
| Después | | | |

MiB y segundos salen de tu build. La clave guardada es el id de la imagen (`docker image inspect --format '{{.Id}}'`) o, si usas la caché de Actions, el `scope` que reutilizaste. Anota también qué pasos del segundo build dicen `CACHED`.

Si no tienes cuenta de AWS, usa el plan B del [README](README.md): GHCR con `GITHUB_TOKEN`, o dos builds locales con BuildKit. La tabla se llena igual.
