"""Fixtures compartidas: cliente HTTP sobre una base SQLite temporal."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import crear_app


@pytest.fixture
def cliente(tmp_path) -> Iterator[TestClient]:
    """Cliente de prueba con una base de datos nueva para cada prueba."""
    aplicacion = crear_app(tmp_path / "prueba.db")
    with TestClient(aplicacion) as cliente_http:
        yield cliente_http
