"""Punto de entrada de la aplicación: crea FastAPI, la base de datos y sirve el frontend."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from app.api import router as router_api
from app.db import conectar, crear_esquema
from app.esquemas import traducir_errores

CARPETA_STATIC = Path(__file__).parent / "static"
RUTA_BD_POR_DEFECTO = os.environ.get("ORGANIZADOR_BD", "datos/organizador.db")


def crear_app(ruta_bd: str | Path = RUTA_BD_POR_DEFECTO) -> FastAPI:
    """Crea la aplicación. Recibe la ruta de la base para poder usar una temporal en las pruebas."""

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        conexion = conectar(ruta_bd)
        crear_esquema(conexion)
        conexion.close()
        app.state.ruta_bd = ruta_bd
        yield

    app = FastAPI(title="Organizador de tareas académicas UPB", lifespan=ciclo_de_vida)

    @app.exception_handler(RequestValidationError)
    async def manejar_error_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=traducir_errores(exc.errors()))

    @app.exception_handler(HTTPException)
    async def manejar_error_http(request: Request, exc: HTTPException) -> JSONResponse:
        mensajes = {
            404: "No se encontró el recurso solicitado.",
            405: "El método no está permitido para este recurso.",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={"errores": [{
                "campo": None,
                "mensaje": mensajes.get(exc.status_code, "No se pudo completar la solicitud."),
            }]},
            headers=exc.headers,
        )

    app.include_router(router_api)
    app.mount("/static", StaticFiles(directory=CARPETA_STATIC), name="static")

    @app.get("/", include_in_schema=False)
    async def pagina_principal() -> FileResponse:
        return FileResponse(CARPETA_STATIC / "index.html")

    return app


app = crear_app()
