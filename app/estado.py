"""Reglas de negocio puras: marcas de vencida y urgente (ver data-model.md, FR-016 a FR-019).

Reciben la hora actual como parámetro para poder probar los límites exactos.
"""

from datetime import datetime, timedelta
from typing import Literal, Protocol

from app.esquemas import FORMATO_ENTREGA

Marca = Literal["vencida", "urgente"]
VENTANA_URGENTE = timedelta(hours=48)


class TareaConEntrega(Protocol):
    fecha_entrega: str
    completada: bool


def calcular_marca(tarea: TareaConEntrega, ahora: datetime) -> Marca | None:
    """Aplica las cuatro reglas en orden: completada, vencida, urgente (48 h inclusivo), ninguna."""
    if tarea.completada:
        return None
    entrega = datetime.strptime(tarea.fecha_entrega, FORMATO_ENTREGA)
    if entrega < ahora:
        return "vencida"
    if entrega <= ahora + VENTANA_URGENTE:
        return "urgente"
    return None


def es_vencida(tarea: TareaConEntrega, ahora: datetime) -> bool:
    return calcular_marca(tarea, ahora) == "vencida"
