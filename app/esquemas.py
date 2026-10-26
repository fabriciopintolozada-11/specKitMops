"""Modelos de entrada y salida de la API, y traducción de errores de validación al español."""

from datetime import date, time
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.colores import CODIGOS_VALIDOS

FORMATO_ENTREGA = "%Y-%m-%dT%H:%M"
HORA_POR_DEFECTO = time(23, 59)

# Mensajes en español por tipo de error de Pydantic (FR-027).
MENSAJES_POR_TIPO: dict[str, str] = {
    "missing": "Este campo es obligatorio.",
    "string_too_short": "Este campo no puede estar vacío.",
    "string_too_long": "Este campo supera la longitud máxima permitida.",
    "int_parsing": "Debe ser un número entero.",
    "bool_parsing": "Debe ser verdadero o falso.",
    "bool_type": "Debe ser verdadero o falso.",
    "date_parsing": "Debe ser una fecha válida (AAAA-MM-DD).",
    "date_from_datetime_parsing": "Debe ser una fecha válida (AAAA-MM-DD).",
    "date_type": "Debe ser una fecha válida (AAAA-MM-DD).",
    "time_parsing": "Debe ser una hora válida (HH:MM).",
    "time_type": "Debe ser una hora válida (HH:MM).",
    "json_invalid": "El cuerpo de la petición no es JSON válido.",
    "literal_error": "El valor no es una opción permitida.",
}
MENSAJE_GENERICO = "El valor no es válido."


def traducir_errores(errores: list[dict[str, Any]]) -> dict[str, list[dict[str, str | None]]]:
    """Convierte los errores de Pydantic al formato {"errores": [{"campo", "mensaje"}]}."""
    traducidos = []
    for error in errores:
        loc = error.get("loc", ())
        campo = str(loc[-1]) if loc and loc[-1] != "body" else None
        traducidos.append(
            {
                "campo": campo,
                "mensaje": MENSAJES_POR_TIPO.get(error.get("type", ""), MENSAJE_GENERICO),
            }
        )
    return {"errores": traducidos}


# Color válido: solo los códigos de la paleta predefinida (FR-003).
Color = Literal[tuple(sorted(CODIGOS_VALIDOS))]
Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Titulo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class MateriaEntrada(BaseModel):
    nombre: Nombre
    color: Color


class Materia(BaseModel):
    id: int
    nombre: str
    color: str
    total_tareas: int


class TareaEntrada(BaseModel):
    materia_id: int
    titulo: Titulo
    descripcion: Annotated[str | None, Field(max_length=500)] = None
    fecha: date
    hora: time = HORA_POR_DEFECTO

    @field_validator("descripcion")
    @classmethod
    def vaciar_descripcion_en_blanco(cls, valor: str | None) -> str | None:
        if valor is None or not valor.strip():
            return None
        return valor.strip()


class MateriaResumen(BaseModel):
    id: int
    nombre: str
    color: str


class Tarea(BaseModel):
    id: int
    materia: MateriaResumen
    titulo: str
    descripcion: str | None
    fecha_entrega: str
    completada: bool
    creada_en: str
