"""Pruebas de la API de tareas (historias 1 a 3: FR-006 a FR-019, FR-021 a FR-024)."""

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import pytest

from app.colores import PALETA
from app.main import crear_app

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


# Historia 2: marcas de vencida y urgente (FR-016 a FR-019).


def crear_tarea_en(cliente, materia_id, entrega, **campos):
    return crear_tarea(
        cliente,
        materia_id,
        fecha=entrega.strftime("%Y-%m-%d"),
        hora=entrega.strftime("%H:%M"),
        **campos,
    )


def marcas_por_titulo(cliente, **parametros):
    return {t["titulo"]: t["marca"] for t in cliente.get("/api/tareas", params=parametros).json()}


def test_listado_incluye_la_marca_de_cada_tarea(cliente):
    materia_id = crear_materia(cliente)
    ahora = datetime.now()
    crear_tarea_en(cliente, materia_id, ahora - timedelta(days=1), titulo="Ayer")
    crear_tarea_en(cliente, materia_id, ahora + timedelta(hours=24), titulo="Mañana")
    crear_tarea_en(cliente, materia_id, ahora + timedelta(days=5), titulo="En 5 días")

    assert marcas_por_titulo(cliente) == {"Ayer": "vencida", "Mañana": "urgente", "En 5 días": None}


def test_crear_tarea_devuelve_su_marca(cliente):
    materia_id = crear_materia(cliente)

    respuesta = crear_tarea_en(cliente, materia_id, datetime.now() - timedelta(days=1))

    assert respuesta.json()["marca"] == "vencida"


def test_tarea_completada_no_lleva_marca(cliente):
    materia_id = crear_materia(cliente)
    tarea_id = crear_tarea_en(cliente, materia_id, datetime.now() - timedelta(days=1)).json()["id"]

    cliente.patch(f"/api/tareas/{tarea_id}/completada", json={"completada": True})

    assert cliente.get("/api/tareas").json()[0]["marca"] is None


# Historia 3: completar tareas (FR-013).


def test_marcar_tarea_como_completada(cliente):
    tarea_id = crear_tarea(cliente, crear_materia(cliente)).json()["id"]

    respuesta = cliente.patch(f"/api/tareas/{tarea_id}/completada", json={"completada": True})

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True
    assert cliente.get("/api/tareas").json()[0]["completada"] is True


def test_desmarcar_tarea_recupera_su_marca(cliente):
    materia_id = crear_materia(cliente)
    tarea_id = crear_tarea_en(cliente, materia_id, datetime.now() - timedelta(days=1)).json()["id"]
    cliente.patch(f"/api/tareas/{tarea_id}/completada", json={"completada": True})

    respuesta = cliente.patch(f"/api/tareas/{tarea_id}/completada", json={"completada": False})

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is False
    assert respuesta.json()["marca"] == "vencida"


def test_completar_tarea_inexistente_da_404(cliente):
    respuesta = cliente.patch("/api/tareas/999/completada", json={"completada": True})

    assert respuesta.status_code == 404
    assert respuesta.json()["errores"][0]["mensaje"] == "La tarea no existe."


def test_completar_sin_el_campo_da_422(cliente):
    tarea_id = crear_tarea(cliente, crear_materia(cliente)).json()["id"]

    respuesta = cliente.patch(f"/api/tareas/{tarea_id}/completada", json={})

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "completada"
    assert error["mensaje"] == "Este campo es obligatorio."


def test_completar_con_valor_no_booleano_da_422(cliente):
    tarea_id = crear_tarea(cliente, crear_materia(cliente)).json()["id"]

    respuesta = cliente.patch(f"/api/tareas/{tarea_id}/completada", json={"completada": "sí"})

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "completada"
    assert error["mensaje"] == "Debe ser verdadero o falso."


# Historia 3: filtros por materia y estado (FR-021 a FR-024).


def preparar_tareas_para_filtros(cliente):
    """Dos materias; en cada una, una tarea vencida, una pendiente futura y una completada."""
    ahora = datetime.now()
    ids = {}
    for nombre in ("Cálculo II", "Física I"):
        materia_id = crear_materia(cliente, nombre)
        ids[nombre] = materia_id
        crear_tarea_en(cliente, materia_id, ahora - timedelta(days=1), titulo=f"{nombre} vencida")
        crear_tarea_en(cliente, materia_id, ahora + timedelta(days=5), titulo=f"{nombre} pendiente")
        completada = crear_tarea_en(
            cliente, materia_id, ahora - timedelta(days=2), titulo=f"{nombre} completada"
        ).json()["id"]
        cliente.patch(f"/api/tareas/{completada}/completada", json={"completada": True})
    return ids


def titulos(cliente, **parametros):
    return {t["titulo"] for t in cliente.get("/api/tareas", params=parametros).json()}


def test_filtrar_por_materia(cliente):
    ids = preparar_tareas_para_filtros(cliente)

    assert titulos(cliente, materia_id=ids["Física I"]) == {
        "Física I vencida",
        "Física I pendiente",
        "Física I completada",
    }


def test_filtrar_por_estado_todas(cliente):
    preparar_tareas_para_filtros(cliente)

    assert len(titulos(cliente, estado="todas")) == 6


def test_filtrar_por_estado_pendientes(cliente):
    preparar_tareas_para_filtros(cliente)

    assert titulos(cliente, estado="pendientes") == {
        "Cálculo II vencida",
        "Cálculo II pendiente",
        "Física I vencida",
        "Física I pendiente",
    }


def test_filtrar_por_estado_completadas(cliente):
    preparar_tareas_para_filtros(cliente)

    assert titulos(cliente, estado="completadas") == {"Cálculo II completada", "Física I completada"}


def test_filtrar_por_estado_vencidas_excluye_completadas(cliente):
    preparar_tareas_para_filtros(cliente)

    assert titulos(cliente, estado="vencidas") == {"Cálculo II vencida", "Física I vencida"}


def test_filtros_combinados(cliente):
    ids = preparar_tareas_para_filtros(cliente)

    assert titulos(cliente, materia_id=ids["Cálculo II"], estado="pendientes") == {
        "Cálculo II vencida",
        "Cálculo II pendiente",
    }


def test_filtro_combinado_mantiene_el_orden_por_fecha(cliente):
    ids = preparar_tareas_para_filtros(cliente)

    respuesta = cliente.get("/api/tareas", params={"materia_id": ids["Física I"]})

    assert [t["titulo"] for t in respuesta.json()] == [
        "Física I completada",
        "Física I vencida",
        "Física I pendiente",
    ]


def test_estado_invalido_da_422(cliente):
    respuesta = cliente.get("/api/tareas", params={"estado": "urgentes"})

    assert respuesta.status_code == 422
    error = respuesta.json()["errores"][0]
    assert error["campo"] == "estado"
    assert error["mensaje"] == "El valor no es una opción permitida."


def test_filtro_sin_resultados_devuelve_lista_vacia(cliente):
    preparar_tareas_para_filtros(cliente)

    respuesta = cliente.get("/api/tareas", params={"materia_id": 999})

    assert respuesta.status_code == 200
    assert respuesta.json() == []


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
