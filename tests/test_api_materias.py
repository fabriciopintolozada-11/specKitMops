"""Pruebas de la API de materias (historia 1, FR-001 a FR-003)."""

import pytest

from app.colores import PALETA

AZUL = PALETA[0]["codigo"]
ROJO = PALETA[1]["codigo"]


def test_crear_y_listar_materia(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "Cálculo II", "color": AZUL})

    assert respuesta.status_code == 201
    materia = respuesta.json()
    assert materia["nombre"] == "Cálculo II"
    assert materia["color"] == AZUL
    assert materia["total_tareas"] == 0

    listado = cliente.get("/api/materias").json()
    assert [m["nombre"] for m in listado] == ["Cálculo II"]


def test_recorta_espacios_del_nombre(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "  Física I  ", "color": AZUL})

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Física I"


def test_nombre_duplicado_sin_distinguir_mayusculas_da_409(cliente):
    cliente.post("/api/materias", json={"nombre": "Cálculo II", "color": AZUL})

    respuesta = cliente.post("/api/materias", json={"nombre": "cálculo ii", "color": ROJO})

    assert respuesta.status_code == 409
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "nombre"
    assert error["mensaje"] == "Ya existe una materia con ese nombre."


def test_nombre_vacio_da_422_en_espanol(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "   ", "color": AZUL})

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "nombre"
    assert error["mensaje"] == "Este campo no puede estar vacío."


def test_nombre_de_51_caracteres_da_422(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "a" * 51, "color": AZUL})

    assert respuesta.status_code == 422
    assert respuesta.json()["errores"][0]["campo"] == "nombre"


def test_nombre_de_50_caracteres_es_valido(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "a" * 50, "color": AZUL})

    assert respuesta.status_code == 201


def test_color_fuera_de_la_paleta_da_422(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "Química", "color": "#000000"})

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "color"
    assert error["mensaje"] == "El valor no es una opción permitida."


def test_campo_obligatorio_faltante_da_422_en_espanol(cliente):
    respuesta = cliente.post("/api/materias", json={"nombre": "Química"})

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "color"
    assert error["mensaje"] == "Este campo es obligatorio."


def test_nombre_duplicado_con_tildes_y_mayusculas_da_409(cliente):
    cliente.post("/api/materias", json={"nombre": "Física", "color": AZUL})

    respuesta = cliente.post("/api/materias", json={"nombre": "FÍSICA", "color": ROJO})

    assert respuesta.status_code == 409


def test_editar_materia_actualiza_nombre_color_y_sus_tareas(cliente):
    materia_id = cliente.post("/api/materias", json={"nombre": "Cálculo", "color": AZUL}).json()["id"]
    cliente.post("/api/tareas", json={"materia_id": materia_id, "titulo": "Práctica", "fecha": "2026-11-03"})
    respuesta = cliente.put(f"/api/materias/{materia_id}", json={"nombre": "  Álgebra  ", "color": ROJO})
    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": materia_id, "nombre": "Álgebra", "color": ROJO, "total_tareas": 1}
    assert cliente.get("/api/tareas").json()[0]["materia"] == {"id": materia_id, "nombre": "Álgebra", "color": ROJO}
    assert cliente.put(f"/api/materias/{materia_id}", json={"nombre": "álgebra", "color": AZUL}).status_code == 200
    duplicado = cliente.post("/api/materias", json={"nombre": "ÁLGEBRA", "color": AZUL})
    assert duplicado.status_code == 409


@pytest.mark.parametrize("campos,campo", [({"nombre": " "}, "nombre"), ({"nombre": "a" * 51}, "nombre"), ({"color": "#000000"}, "color")])
def test_editar_materia_valida_sin_modificar_datos(cliente, campos, campo):
    original = cliente.post("/api/materias", json={"nombre": "Cálculo", "color": AZUL}).json()
    respuesta = cliente.put(f"/api/materias/{original['id']}", json={"nombre": "Cálculo", "color": AZUL, **campos})
    assert respuesta.status_code == 422
    assert respuesta.json()["errores"][0]["campo"] == campo
    assert cliente.get("/api/materias").json() == [original]


def test_editar_materia_rechaza_nombre_duplicado(cliente):
    cliente.post("/api/materias", json={"nombre": "Cálculo", "color": AZUL})
    materia_id = cliente.post("/api/materias", json={"nombre": "Física", "color": ROJO}).json()["id"]
    respuesta = cliente.put(f"/api/materias/{materia_id}", json={"nombre": " CÁLCULO ", "color": AZUL})
    assert respuesta.status_code == 409
    assert respuesta.json()["errores"][0]["mensaje"] == "Ya existe una materia con ese nombre."
    assert len(cliente.get("/api/materias").json()) == 2


def test_eliminar_materia_borra_solo_sus_tareas(cliente):
    ids = [cliente.post("/api/materias", json={"nombre": nombre, "color": AZUL}).json()["id"] for nombre in ("Cálculo", "Física")]
    for materia_id in ids:
        cliente.post("/api/tareas", json={"materia_id": materia_id, "titulo": "Práctica", "fecha": "2026-11-03"})
    respuesta = cliente.delete(f"/api/materias/{ids[0]}")
    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert [m["id"] for m in cliente.get("/api/materias").json()] == [ids[1]]
    assert [t["materia"]["id"] for t in cliente.get("/api/tareas").json()] == [ids[1]]
    assert cliente.delete(f"/api/materias/{ids[0]}").status_code == 404


def test_editar_materia_inexistente_da_404(cliente):
    respuesta = cliente.put("/api/materias/999", json={"nombre": "Cálculo", "color": AZUL})
    assert respuesta.status_code == 404
    assert respuesta.json()["errores"][0]["mensaje"] == "La materia indicada no existe."
