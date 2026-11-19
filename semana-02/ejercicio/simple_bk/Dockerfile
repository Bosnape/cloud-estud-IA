# Imagen de simple_bk. uvicorn escucha en 0.0.0.0 y en $PORT.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

# --only-binary evita setup.py de paquetes. uv publica wheel.
RUN pip install --no-cache-dir --only-binary=:all: uv==0.13.9

COPY pyproject.toml uv.lock README.md ./
# --frozen usa uv.lock. --no-build no ejecuta scripts de sdists.
RUN uv sync --frozen --no-dev --no-install-project --no-build

COPY main.py codes.py config.py ./

RUN useradd --system --create-home --uid 10001 --shell /usr/sbin/nologin app \
    && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["sh", "-c", "exec /app/.venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
