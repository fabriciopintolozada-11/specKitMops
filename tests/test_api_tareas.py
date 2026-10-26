"""Pruebas de la API de tareas (historia 1, FR-006 a FR-009, FR-012, FR-014)."""

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
