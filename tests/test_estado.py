"""Pruebas unitarias del cálculo de marcas (historia 2, FR-016 a FR-019)."""

from datetime import datetime, timedelta
from types import SimpleNamespace

from app.estado import calcular_marca, es_vencida

AHORA = datetime(2026, 10, 26, 12, 0)


def tarea(entrega: datetime, completada: bool = False) -> SimpleNamespace:
    return SimpleNamespace(fecha_entrega=entrega.strftime("%Y-%m-%dT%H:%M"), completada=completada)


def test_completada_no_lleva_marca_aunque_este_vencida():
    assert calcular_marca(tarea(AHORA - timedelta(days=3), completada=True), AHORA) is None


def test_completada_no_lleva_marca_aunque_sea_urgente():
    assert calcular_marca(tarea(AHORA + timedelta(hours=2), completada=True), AHORA) is None


def test_vencida_un_minuto_despues_de_la_entrega():
    assert calcular_marca(tarea(AHORA - timedelta(minutes=1)), AHORA) == "vencida"


def test_urgente_en_la_hora_exacta_de_entrega():
    assert calcular_marca(tarea(AHORA), AHORA) == "urgente"


def test_urgente_a_exactamente_48_horas():
    assert calcular_marca(tarea(AHORA + timedelta(hours=48)), AHORA) == "urgente"


def test_sin_marca_a_48_horas_y_1_minuto():
    assert calcular_marca(tarea(AHORA + timedelta(hours=48, minutes=1)), AHORA) is None


def test_sin_marca_si_la_entrega_es_en_5_dias():
    assert calcular_marca(tarea(AHORA + timedelta(days=5)), AHORA) is None


def test_es_vencida_solo_para_pendientes_con_entrega_pasada():
    assert es_vencida(tarea(AHORA - timedelta(minutes=1)), AHORA)
    assert not es_vencida(tarea(AHORA - timedelta(minutes=1), completada=True), AHORA)
    assert not es_vencida(tarea(AHORA), AHORA)
