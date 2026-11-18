# syntax=docker/dockerfile:1
# Variante B, y también la C. La etapa "build" compila; la etapa final
# solo copia el resultado y la librería de runtime (libpq5), sin gcc.
# C no tiene otro Dockerfile: el workflow construye este archivo con
# caché type=gha y un scope propio.

FROM python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72 AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /src

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install --no-binary=psycopg2 -r requirements.txt

FROM python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /install /usr/local

WORKDIR /app
COPY app/main.py .

RUN useradd --system --create-home --uid 10001 --shell /usr/sbin/nologin app
USER app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
