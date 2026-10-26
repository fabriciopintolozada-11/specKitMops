"""Endpoints JSON de /api: colores, materias y tareas (ver contracts/api.md)."""

import sqlite3
from collections.abc import Iterator
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

from app import repositorio
from app.colores import PALETA
from app.db import conectar
from app.esquemas import (
    FORMATO_ENTREGA,
    CompletadaEntrada,
    EstadoFiltro,
    Materia,
    MateriaEntrada,
    MateriaResumen,
    Tarea,
    TareaEntrada,
)
from app.estado import calcular_marca, es_vencida

router = APIRouter(prefix="/api")


def obtener_conexion(request: Request) -> Iterator[sqlite3.Connection]:
    conexion = conectar(request.app.state.ruta_bd)
    try:
        yield conexion
    finally:
        conexion.close()


Conexion = Annotated[sqlite3.Connection, Depends(obtener_conexion)]


def error(codigo: int, campo: str | None, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=codigo, content={"errores": [{"campo": campo, "mensaje": mensaje}]})


def fila_a_tarea(fila: sqlite3.Row, ahora: datetime) -> Tarea:
    tarea = Tarea(
        id=fila["id"],
        materia=MateriaResumen(
            id=fila["materia_id"], nombre=fila["materia_nombre"], color=fila["materia_color"]
        ),
        titulo=fila["titulo"],
        descripcion=fila["descripcion"],
        fecha_entrega=fila["fecha_entrega"],
        completada=bool(fila["completada"]),
        creada_en=fila["creada_en"],
    )
    tarea.marca = calcular_marca(tarea, ahora)
    return tarea


@router.get("/colores")
def listar_colores() -> list[dict[str, str]]:
    return PALETA


@router.get("/materias", response_model=list[Materia])
def listar_materias(conexion: Conexion) -> list[dict]:
    return [dict(fila) for fila in repositorio.listar_materias(conexion)]


@router.post("/materias", status_code=201, response_model=Materia)
def crear_materia(entrada: MateriaEntrada, conexion: Conexion) -> dict | JSONResponse:
    try:
        materia_id = repositorio.crear_materia(conexion, entrada.nombre, entrada.color)
    except repositorio.NombreDuplicado:
        return error(409, "nombre", "Ya existe una materia con ese nombre.")
    return dict(repositorio.obtener_materia(conexion, materia_id))


@router.get("/tareas", response_model=list[Tarea])
def listar_tareas(
    conexion: Conexion, materia_id: int | None = None, estado: EstadoFiltro = "todas"
) -> list[Tarea]:
    # "vencidas" depende de la hora actual, así que se filtra después de calcular la marca.
    completada = {"pendientes": False, "completadas": True, "vencidas": False}.get(estado)
    ahora = datetime.now()
    tareas = [
        fila_a_tarea(fila, ahora)
        for fila in repositorio.listar_tareas(conexion, materia_id, completada)
    ]
    if estado == "vencidas":
        tareas = [tarea for tarea in tareas if es_vencida(tarea, ahora)]
    return tareas


@router.post("/tareas", status_code=201, response_model=Tarea)
def crear_tarea(entrada: TareaEntrada, conexion: Conexion) -> Tarea | JSONResponse:
    fecha_entrega = datetime.combine(entrada.fecha, entrada.hora).strftime(FORMATO_ENTREGA)
    creada_en = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        tarea_id = repositorio.crear_tarea(
            conexion,
            entrada.materia_id,
            entrada.titulo,
            entrada.descripcion,
            fecha_entrega,
            creada_en,
        )
    except repositorio.MateriaNoExiste:
        return error(400, "materia_id", "La materia indicada no existe.")
    return fila_a_tarea(repositorio.obtener_tarea(conexion, tarea_id), datetime.now())


@router.patch("/tareas/{tarea_id}/completada", response_model=Tarea)
def actualizar_completada(
    tarea_id: int, entrada: CompletadaEntrada, conexion: Conexion
) -> Tarea | JSONResponse:
    if not repositorio.actualizar_completada(conexion, tarea_id, entrada.completada):
        return error(404, None, "La tarea no existe.")
    return fila_a_tarea(repositorio.obtener_tarea(conexion, tarea_id), datetime.now())


@router.put("/materias/{materia_id}", response_model=Materia)
def actualizar_materia(materia_id: int, entrada: MateriaEntrada, conexion: Conexion) -> dict | JSONResponse:
    try:
        existe = repositorio.actualizar_materia(conexion, materia_id, entrada.nombre, entrada.color)
    except repositorio.NombreDuplicado:
        return error(409, "nombre", "Ya existe una materia con ese nombre.")
    if not existe:
        return error(404, None, "La materia indicada no existe.")
    return dict(repositorio.obtener_materia(conexion, materia_id))


@router.delete("/materias/{materia_id}", status_code=204)
def eliminar_materia(materia_id: int, conexion: Conexion) -> Response:
    if not repositorio.eliminar_materia(conexion, materia_id):
        return error(404, None, "La materia indicada no existe.")
    return Response(status_code=204)


@router.put("/tareas/{tarea_id}", response_model=Tarea)
def actualizar_tarea(tarea_id: int, entrada: TareaEntrada, conexion: Conexion) -> Tarea | JSONResponse:
    fecha_entrega = datetime.combine(entrada.fecha, entrada.hora).strftime(FORMATO_ENTREGA)
    try:
        existe = repositorio.actualizar_tarea(
            conexion, tarea_id, entrada.materia_id, entrada.titulo, entrada.descripcion, fecha_entrega
        )
    except repositorio.MateriaNoExiste:
        return error(400, "materia_id", "La materia indicada no existe.")
    if not existe:
        return error(404, None, "La tarea indicada no existe.")
    return fila_a_tarea(repositorio.obtener_tarea(conexion, tarea_id), datetime.now())


@router.delete("/tareas/{tarea_id}", status_code=204)
def eliminar_tarea(tarea_id: int, conexion: Conexion) -> Response:
    if not repositorio.eliminar_tarea(conexion, tarea_id):
        return error(404, None, "La tarea indicada no existe.")
    return Response(status_code=204)
