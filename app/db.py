"""Conexión a SQLite y creación del esquema (ver data-model.md)."""

import sqlite3
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS materia (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre              TEXT NOT NULL,
    nombre_normalizado  TEXT NOT NULL UNIQUE,
    color               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tarea (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id     INTEGER NOT NULL REFERENCES materia(id) ON DELETE CASCADE,
    titulo         TEXT NOT NULL,
    descripcion    TEXT,
    fecha_entrega  TEXT NOT NULL,
    completada     INTEGER NOT NULL DEFAULT 0 CHECK (completada IN (0, 1)),
    creada_en      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tarea_entrega ON tarea (fecha_entrega, id);
"""


def conectar(ruta: str | Path) -> sqlite3.Connection:
    """Abre la base de datos y activa las claves foráneas (necesario para el borrado en cascada)."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta, check_same_thread=False)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_esquema(conexion: sqlite3.Connection) -> None:
    """Crea las tablas e índices si no existen. Es seguro llamarla en cada arranque."""
    conexion.executescript(ESQUEMA)
    conexion.commit()
