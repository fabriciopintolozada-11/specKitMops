"""Pruebas de la API de tareas (historia 1, FR-006 a FR-009, FR-012, FR-014)."""

from datetime import datetime, timedelta

import pytest

from app.colores import PALETA

AZUL = PALETA[0]["codigo"]


def crear_materia(cliente, nombre="Cálculo II"):
    respuesta = cliente.post("/api/materias", json={"nombre": nombre, "color": AZUL})
    return respuesta.json()["id"]


def crear_tarea(cliente, materia_id, **campos):
    cuerpo = {"materia_id": materia_id, "titulo": "Práctica", "fecha": "2026-11-03", **campos}
    return cliente.post("/api/tareas", json=cuerpo)


def test_crear_tarea_con_hora(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea(cliente, materia_id, hora="18:00", descripcion="Ejercicios 1 al 10")

    assert respuesta.status_code == 201
    tarea = respuesta.json()
    assert tarea["titulo"] == "Práctica"
    assert tarea["descripcion"] == "Ejercicios 1 al 10"
    assert tarea["fecha_entrega"] == "2026-11-03T18:00"
    assert tarea["completada"] is False
    assert tarea["materia"]["nombre"] == "Cálculo II"
    assert tarea["materia"]["color"] == AZUL


def test_sin_hora_la_entrega_es_2359(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea(cliente, materia_id)

    assert respuesta.json()["fecha_entrega"] == "2026-11-03T23:59"


def test_descripcion_vacia_se_guarda_como_nula(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea(cliente, materia_id, descripcion="   ")

    assert respuesta.json()["descripcion"] is None


def test_titulo_de_101_caracteres_da_422(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea(cliente, materia_id, titulo="a" * 101)

    assert respuesta.status_code == 422
    assert respuesta.json()["errores"][0]["campo"] == "titulo"


def test_descripcion_de_501_caracteres_da_422(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea(cliente, materia_id, descripcion="a" * 501)

    assert respuesta.status_code == 422
    assert respuesta.json()["errores"][0]["campo"] == "descripcion"


def test_materia_inexistente_da_400(cliente):
    respuesta = crear_tarea(cliente, materia_id=999)

    assert respuesta.status_code == 400
    assert respuesta.json()["errores"][0]["campo"] == "materia_id"


def test_fecha_inexistente_da_422_en_espanol(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea(cliente, materia_id, fecha="2026-02-30")

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "fecha"
    assert error["mensaje"] == "Debe ser una fecha válida (AAAA-MM-DD)."


def test_listado_ordenado_por_fecha_con_desempate_por_creacion(cliente):
    materia_id = crear_materia(cliente)
    crear_tarea(cliente, materia_id, titulo="Entrega 9", fecha="2026-11-09")
    crear_tarea(cliente, materia_id, titulo="Entrega 2", fecha="2026-11-02")
    crear_tarea(cliente, materia_id, titulo="Entrega 5 primera", fecha="2026-11-05", hora="10:00")
    crear_tarea(cliente, materia_id, titulo="Entrega 5 segunda", fecha="2026-11-05", hora="10:00")

    titulos = [t["titulo"] for t in cliente.get("/api/tareas").json()]

    assert titulos == ["Entrega 2", "Entrega 5 primera", "Entrega 5 segunda", "Entrega 9"]


def test_editar_tarea_recalcula_marca_y_orden(cliente):
    materia_id = crear_materia(cliente)
    otra_materia = crear_materia(cliente, "Física")
    ahora = datetime.now()
    futura = (ahora + timedelta(days=5)).date().isoformat()
    ayer = (ahora - timedelta(days=1)).date().isoformat()
    manana = (ahora + timedelta(days=1)).date().isoformat()
    tarea = crear_tarea(cliente, materia_id, fecha=futura).json()
    otra_tarea = crear_tarea(cliente, materia_id, fecha=manana).json()
    cuerpo = {"materia_id": otra_materia, "titulo": " Corregida ", "fecha": ayer, "descripcion": " "}
    respuesta = cliente.put(f"/api/tareas/{tarea['id']}", json=cuerpo)
    assert respuesta.status_code == 200
    editada = respuesta.json()
    assert editada["titulo"] == "Corregida"
    assert editada["descripcion"] is None
    assert editada["materia"]["id"] == otra_materia
    assert editada["fecha_entrega"] == f"{ayer}T23:59"
    assert editada["marca"] == "vencida"
    assert editada["creada_en"] == tarea["creada_en"]
    assert [t["id"] for t in cliente.get("/api/tareas").json()] == [tarea["id"], otra_tarea["id"]]
    assert cliente.put(f"/api/tareas/{tarea['id']}", json={**cuerpo, "fecha": manana}).json()["marca"] == "urgente"
    assert cliente.put(f"/api/tareas/{tarea['id']}", json={**cuerpo, "fecha": futura}).json()["marca"] is None
    assert [t["id"] for t in cliente.get("/api/tareas").json()] == [otra_tarea["id"], tarea["id"]]
    cliente.patch(f"/api/tareas/{tarea['id']}/completada", json={"completada": True})
    completada = cliente.put(f"/api/tareas/{tarea['id']}", json=cuerpo).json()
    assert completada["completada"] is True
    assert completada["marca"] is None


@pytest.mark.parametrize("campos,codigo", [({"materia_id": 999}, 400), ({"titulo": " "}, 422), ({"titulo": "a" * 101}, 422), ({"descripcion": "a" * 501}, 422), ({"fecha": "2026-02-30"}, 422), ({"hora": "25:00"}, 422)])
def test_editar_tarea_invalida_conserva_original(cliente, campos, codigo):
    materia_id = crear_materia(cliente)
    tarea = crear_tarea(cliente, materia_id).json()
    respuesta = cliente.put(f"/api/tareas/{tarea['id']}", json={"materia_id": materia_id, "titulo": "Práctica", "fecha": "2026-11-03", **campos})
    assert respuesta.status_code == codigo
    assert "errores" in respuesta.json()
    assert cliente.get("/api/tareas").json() == [tarea]


def test_eliminar_tarea_y_recursos_inexistentes(cliente):
    materia_id = crear_materia(cliente)
    tarea_id = crear_tarea(cliente, materia_id).json()["id"]
    respuesta = cliente.delete(f"/api/tareas/{tarea_id}")
    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get("/api/tareas").json() == []
    assert cliente.get("/api/materias").json()[0]["total_tareas"] == 0
    assert cliente.delete(f"/api/tareas/{tarea_id}").status_code == 404
    respuesta = cliente.put(f"/api/tareas/{tarea_id}", json={"materia_id": materia_id, "titulo": "Práctica", "fecha": "2026-11-03"})
    assert respuesta.status_code == 404
    assert respuesta.json()["errores"][0]["mensaje"] == "La tarea indicada no existe."


def test_soporte_de_completado_y_filtros_para_la_interfaz(cliente):
    materia_id = crear_materia(cliente)
    otra_materia = crear_materia(cliente, "Física")
    ayer = (datetime.now() - timedelta(days=1)).date().isoformat()
    tarea_id = crear_tarea(cliente, materia_id, fecha=ayer).json()["id"]
    crear_tarea(cliente, otra_materia)
    ruta = f"/api/tareas/{tarea_id}/completada"
    assert cliente.patch(ruta, json={"completada": True}).json()["marca"] is None
    assert cliente.get("/api/tareas", params={"materia_id": materia_id, "estado": "pendientes"}).json() == []
    assert [t["id"] for t in cliente.get("/api/tareas", params={"materia_id": materia_id, "estado": "completadas"}).json()] == [tarea_id]
    assert cliente.patch(ruta, json={"completada": False}).json()["marca"] == "vencida"
    assert [t["id"] for t in cliente.get("/api/tareas", params={"materia_id": materia_id, "estado": "vencidas"}).json()] == [tarea_id]
    assert cliente.get("/api/tareas", params={"estado": "invalido"}).status_code == 422
    assert cliente.patch(ruta, json={"completada": "true"}).status_code == 422


@pytest.mark.parametrize("metodo,ruta,codigo,mensaje", [
    ("get", "/api/no-existe", 404, "No se encontró el recurso solicitado."),
    ("patch", "/api/materias", 405, "El método no está permitido para este recurso."),
])
def test_errores_http_en_espanol(cliente, metodo, ruta, codigo, mensaje):
    respuesta = getattr(cliente, metodo)(ruta)
    assert respuesta.status_code == codigo
    assert respuesta.json() == {"errores": [{"campo": None, "mensaje": mensaje}]}
