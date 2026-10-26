"""Marcas derivadas de las tareas, calculadas con la hora local recibida."""

from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any, Literal


def calcular_marca(tarea: Mapping[str, Any], ahora: datetime) -> Literal["vencida", "urgente"] | None:
    if tarea["completada"]:
        return None
    entrega = datetime.fromisoformat(tarea["fecha_entrega"])
    if entrega < ahora:
        return "vencida"
    if entrega <= ahora + timedelta(hours=48):
        return "urgente"
    return None


def es_vencida(tarea: Mapping[str, Any], ahora: datetime) -> bool:
    return calcular_marca(tarea, ahora) == "vencida"
