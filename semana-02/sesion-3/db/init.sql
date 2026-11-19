-- Se ejecuta solo cuando el volumen está vacío (el primer arranque).
-- docker compose down no lo borra; docker compose down -v sí.

CREATE TABLE IF NOT EXISTS items (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre TEXT NOT NULL,
    nota TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
