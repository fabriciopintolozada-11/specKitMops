# Guía rápida de validación: Organizador de tareas académicas UPB

Guía para ejecutar la aplicación y comprobar de punta a punta que cumple la
[especificación](spec.md). Los detalles de datos y endpoints están en
[data-model.md](data-model.md) y [contracts/api.md](contracts/api.md).

## Requisitos previos

- `uv` instalado (`uv --version`). `uv` descarga Python 3.12 si no está disponible.
- Alternativa sin `uv`: Python 3.12 con `venv` y `pip`.
- Para probar desde el celular: celular y computadora en la misma red Wi-Fi.

## Preparar el entorno

Desde la raíz del repositorio (`speckit-practica`):

```powershell
uv sync
```

Alternativa con `pip`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
```

## Ejecutar las pruebas automatizadas

```powershell
uv run pytest
```

**Resultado esperado**: todas las pruebas pasan. Deben incluir, como mínimo:

- `tests/test_estado.py`: tarea completada sin marca; vencida un minuto después de la entrega;
  urgente justo en la hora de entrega y justo a las 48 h; sin marca a las 48 h y 1 minuto.
- `tests/test_api_materias.py`: crear, nombre duplicado sin distinguir mayúsculas, incluido
  "FÍSICA" frente a "física" (409), límite de 50 caracteres (422), color fuera de la paleta (422), eliminar en
  cascada.
- `tests/test_api_tareas.py`: crear con y sin hora, límites de 100 y 500 caracteres, orden por
  fecha con desempate por creación, filtros combinados, marcar y desmarcar completada.

## Ejecutar la aplicación

```powershell
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- En la computadora: abrir `http://localhost:8000`.
- En el celular: abrir `http://<IP-de-la-computadora>:8000`. La IP se obtiene con `ipconfig`
  (dato "Dirección IPv4"). Si no carga, permitir Python en el Firewall de Windows para redes
  privadas.

## Escenarios de validación manual

| # | Pasos | Resultado esperado | Requisitos |
|---|---|---|---|
| 1 | Sin materias, intentar crear una tarea. | Se indica que primero hay que registrar una materia. | Casos límite |
| 2 | Registrar "Cálculo II" en azul y luego "cálculo ii". | La primera se guarda; la segunda se rechaza por nombre repetido. | FR-001 a FR-003 |
| 3 | Crear tres tareas con entregas en 5 días, mañana y ayer. | El listado muestra: ayer (vencida), mañana (urgente), 5 días (sin marca). | FR-014 a FR-017 |
| 4 | Crear una tarea con título de solo espacios. | No se guarda; se indica que el título es obligatorio. | FR-007, FR-027 |
| 5 | Marcar como completada la tarea vencida. | Pierde la marca "vencida". Al desmarcarla, la recupera. | FR-013, FR-018 |
| 6 | Filtrar por "Cálculo II" + "Pendientes". | Solo se ven las tareas pendientes de esa materia, en orden de fecha. | FR-021 a FR-023 |
| 7 | Filtrar por una combinación sin resultados. | Aparece un mensaje de que no hay tareas con ese filtro. | FR-024 |
| 8 | Cambiar la fecha de la tarea de 5 días a mañana. | Se reubica en el listado y aparece como urgente. | FR-010, historia 4 |
| 9 | Eliminar "Cálculo II". | Se avisa cuántas tareas se eliminarán; al confirmar desaparecen materia y tareas. | FR-005 |
| 10 | Cerrar el servidor, volver a iniciarlo y recargar. | Los datos siguen ahí. | FR-025, SC-005 |
| 11 | Repetir los pasos 2, 3 y 6 desde el celular (360 px de ancho). | Todo funciona sin desplazamiento horizontal. | FR-028, SC-006 |
| 12 | Recorrer la página solo con el teclado (Tab, Enter, Espacio). | Se puede crear, completar y filtrar tareas sin mouse. | Principio V |
