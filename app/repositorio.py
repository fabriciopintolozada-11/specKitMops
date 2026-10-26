"""Consultas SQL a SQLite para materias y tareas (ver data-model.md)."""

import sqlite3

SELECT_MATERIAS = """
    SELECT m.id, m.nombre, m.color, COUNT(t.id) AS total_tareas
    FROM materia m
    LEFT JOIN tarea t ON t.materia_id = m.id
"""

SELECT_TAREAS = """
    SELECT t.id, t.titulo, t.descripcion, t.fecha_entrega, t.completada, t.creada_en,
           m.id AS materia_id, m.nombre AS materia_nombre, m.color AS materia_color
    FROM tarea t
    JOIN materia m ON m.id = t.materia_id
"""


class NombreDuplicado(Exception):
    """Ya existe una materia con el mismo nombre, sin distinguir mayúsculas."""


class MateriaNoExiste(Exception):
    """La materia indicada no existe."""


def crear_materia(conexion: sqlite3.Connection, nombre: str, color: str) -> int:
    try:
        cursor = conexion.execute(
            "INSERT INTO materia (nombre, nombre_normalizado, color) VALUES (?, ?, ?)",
            (nombre, nombre.casefold(), color),
        )
    except sqlite3.IntegrityError as error:
        raise NombreDuplicado(nombre) from error
    conexion.commit()
    return cursor.lastrowid


def obtener_materia(conexion: sqlite3.Connection, materia_id: int) -> sqlite3.Row | None:
    return conexion.execute(
        SELECT_MATERIAS + " WHERE m.id = ? GROUP BY m.id", (materia_id,)
    ).fetchone()


def listar_materias(conexion: sqlite3.Connection) -> list[sqlite3.Row]:
    return conexion.execute(
        SELECT_MATERIAS + " GROUP BY m.id ORDER BY m.nombre_normalizado"
    ).fetchall()


def crear_tarea(
    conexion: sqlite3.Connection,
    materia_id: int,
    titulo: str,
    descripcion: str | None,
    fecha_entrega: str,
    creada_en: str,
) -> int:
    if conexion.execute("SELECT 1 FROM materia WHERE id = ?", (materia_id,)).fetchone() is None:
        raise MateriaNoExiste(materia_id)
    cursor = conexion.execute(
        """
        INSERT INTO tarea (materia_id, titulo, descripcion, fecha_entrega, completada, creada_en)
        VALUES (?, ?, ?, ?, 0, ?)
        """,
        (materia_id, titulo, descripcion, fecha_entrega, creada_en),
    )
    conexion.commit()
    return cursor.lastrowid


def obtener_tarea(conexion: sqlite3.Connection, tarea_id: int) -> sqlite3.Row | None:
    return conexion.execute(SELECT_TAREAS + " WHERE t.id = ?", (tarea_id,)).fetchone()


def listar_tareas(
    conexion: sqlite3.Connection,
    materia_id: int | None = None,
    completada: bool | None = None,
) -> list[sqlite3.Row]:
    """Lista tareas ordenadas por entrega; los filtros en None no se aplican."""
    condiciones = []
    parametros: list[int] = []
    if materia_id is not None:
        condiciones.append("t.materia_id = ?")
        parametros.append(materia_id)
    if completada is not None:
        condiciones.append("t.completada = ?")
        parametros.append(int(completada))
    where = " WHERE " + " AND ".join(condiciones) if condiciones else ""
    return conexion.execute(
        SELECT_TAREAS + where + " ORDER BY t.fecha_entrega, t.id", parametros
    ).fetchall()


def actualizar_completada(conexion: sqlite3.Connection, tarea_id: int, completada: bool) -> bool:
    """Marca o desmarca la tarea. Devuelve False si la tarea no existe."""
    cursor = conexion.execute(
        "UPDATE tarea SET completada = ? WHERE id = ?", (int(completada), tarea_id)
    )
    conexion.commit()
    return cursor.rowcount > 0


def actualizar_materia(conexion: sqlite3.Connection, materia_id: int, nombre: str, color: str) -> bool:
    nombre = nombre.strip()
    try:
        cursor = conexion.execute(
            "UPDATE materia SET nombre = ?, nombre_normalizado = ?, color = ? WHERE id = ?",
            (nombre, nombre.casefold(), color, materia_id),
        )
    except sqlite3.IntegrityError as error:
        conexion.rollback()
        raise NombreDuplicado(nombre) from error
    conexion.commit()
    return cursor.rowcount > 0


def eliminar_materia(conexion: sqlite3.Connection, materia_id: int) -> bool:
    """La clave foránea elimina las tareas de la materia en la misma transacción."""
    cursor = conexion.execute("DELETE FROM materia WHERE id = ?", (materia_id,))
    conexion.commit()
    return cursor.rowcount > 0


def actualizar_tarea(
    conexion: sqlite3.Connection,
    tarea_id: int,
    materia_id: int,
    titulo: str,
    descripcion: str | None,
    fecha_entrega: str,
) -> bool:
    if obtener_tarea(conexion, tarea_id) is None:
        return False
    if obtener_materia(conexion, materia_id) is None:
        raise MateriaNoExiste(materia_id)
    cursor = conexion.execute(
        "UPDATE tarea SET materia_id = ?, titulo = ?, descripcion = ?, fecha_entrega = ? WHERE id = ?",
        (materia_id, titulo.strip(), (descripcion or "").strip() or None, fecha_entrega, tarea_id),
    )
    conexion.commit()
    return cursor.rowcount > 0


def eliminar_tarea(conexion: sqlite3.Connection, tarea_id: int) -> bool:
    cursor = conexion.execute("DELETE FROM tarea WHERE id = ?", (tarea_id,))
    conexion.commit()
    return cursor.rowcount > 0
