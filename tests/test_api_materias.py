"""Pruebas de la API de materias (historia 1, FR-001 a FR-003)."""

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
