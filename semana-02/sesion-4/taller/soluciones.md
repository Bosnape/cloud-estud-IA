# Soluciones de la hoja OIDC

Corresponde a los tres errores de [`oidc-errores.md`](oidc-errores.md). Los ARN siguen siendo ficticios (`123456789012`). No hay claves que copiar a un entorno real.

## 1. Falta `permissions: id-token: write`

`configure-aws-credentials` pide el JWT de GitHub (`ACTIONS_ID_TOKEN_REQUEST_TOKEN`). Con un bloque `permissions` que solo deja `contents: read`, ese token no se emite y el paso falla con un 403 al pedir el OIDC token.

Hay que declararlo en el job. `contents: read` se queda, porque el checkout no necesita más.

```yaml
permissions:
  contents: read
  id-token: write
```

## 2. La política de confianza no ata `sub` al repositorio ni a la rama

La condición solo mira `aud`. Cualquier workflow de cualquier repositorio que use este proveedor OIDC podría intentar asumir el rol. `sub` es la afirmación que dice *qué* repo y *qué* ref pidió el token. Hay que igualarla.

Para publicar solo desde `main` de este repositorio:

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
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:RafaelCampoTech/Estud-IA_cloud:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

Cambia el nombre del repositorio y `main` por la rama que sí puede publicar. `StringLike` con `repo:ORG/REPO:*` deja pasar tags y otras ramas: es más amplio, y hay que decidirlo, no heredarlo por omisión.

## 3. `ecr:*` sobre `*`

Ese statement permite borrar repositorios, cambiar políticas y leer cualquier imagen de la cuenta. Para subir una imagen basta el token de autorización (ese sí va sobre `*`, porque la API no lo aplica a un repositorio) y las acciones de push sobre el ARN de un repositorio.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TokenDeAutorizacion",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Sid": "PushAUnRepositorio",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:CompleteLayerUpload",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": "arn:aws:ecr:us-east-1:123456789012:repository/estudia-backend"
    }
  ]
}
```

`GetAuthorizationToken` sobre `*` no es el error de la hoja. El error es el comodín en la acción y en el recurso a la vez.

## Workflow corregido

```yaml
name: Publicar en ECR

on:
  workflow_dispatch:

jobs:
  publicar:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      id-token: write
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
          context: semana-02/sesion-3/backend
          push: true
          provenance: false
          tags: ${{ steps.ecr.outputs.registry }}/estudia-backend:taller
```

Este workflow asume el rol ficticio. No va a funcionar contra AWS hasta que exista el proveedor OIDC, el rol y el repositorio ECR. No lo lances esperando un push real.
