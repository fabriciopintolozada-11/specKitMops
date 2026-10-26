# Tareas: Organizador de tareas académicas UPB

**Entrada**: Documentos de diseño en `specs/001-organizador-tareas/`

**Requisitos previos**: [plan.md](plan.md) (obligatorio), [spec.md](spec.md) (obligatorio),
[research.md](research.md), [data-model.md](data-model.md), [contracts/api.md](contracts/api.md),
[quickstart.md](quickstart.md)

**Pruebas**: Incluidas. El plan exige pytest y el principio de pruebas obligatorias del usuario
exige pruebas automatizadas antes de dar una funcionalidad por terminada. Cada historia escribe
primero sus pruebas y verifica que fallan antes de implementar.

**Organización**: Las tareas se agrupan por historia de usuario para que cada una pueda
implementarse y probarse de forma independiente.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes).
- **[Historia]**: US1 a US4, según las historias de [spec.md](spec.md).
- Las rutas son relativas a la raíz del repositorio `speckit-practica/`.

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: Inicializar el proyecto Python.

- [X] T001 Crear `pyproject.toml` con Python >=3.12 y dependencias `fastapi`, `uvicorn`; dependencias de desarrollo `pytest` y `httpx`
- [X] T002 [P] Crear `app/__init__.py` y `tests/__init__.py` vacíos, y la carpeta `app/static/`
- [X] T003 [P] Crear `.gitignore` en la raíz con las entradas `datos/`, `.venv/`, `__pycache__/` y `.pytest_cache/`
- [X] T004 [P] Agregar en `pyproject.toml` la sección `[tool.pytest.ini_options]` con `testpaths = ["tests"]`

---

## Fase 2: Fundamentos (bloquean todas las historias)

**Propósito**: Infraestructura mínima compartida: base de datos, validación en español y servidor.

**⚠️ CRÍTICO**: Ninguna historia puede empezar hasta terminar esta fase.

- [X] T005 [P] Implementar la paleta predefinida de 8 colores (nombre y código) en `app/colores.py`, con los valores exactos de [data-model.md](data-model.md)
- [X] T006 [P] Implementar `conectar(ruta)` con `PRAGMA foreign_keys = ON` y `crear_esquema(conexion)` con las tablas `materia`, `tarea` y el índice `idx_tarea_entrega` del DDL de [data-model.md](data-model.md) en `app/db.py`
- [X] T007 [P] Implementar la función que traduce los errores de validación de Pydantic a `{"errores": [{"campo", "mensaje"}]}` con mensajes en español en `app/esquemas.py`
- [X] T008 Crear la aplicación FastAPI en `app/main.py`: ejecutar `crear_esquema` al iniciar, montar `/static` desde `app/static/`, servir `index.html` en `/`, y registrar el manejador de `RequestValidationError` de T007 (depende de T006, T007)
- [X] T009 Crear el fixture `cliente` en `tests/conftest.py` con una base SQLite temporal en `tmp_path` y `fastapi.testclient.TestClient` (depende de T008)
- [X] T010 [P] Crear `app/static/index.html`, `app/static/estilos.css` y `app/static/app.js` como archivos base, con `<meta name="viewport">` y `lang="es"`

**Punto de control**: Fundamentos listos. Las historias pueden empezar.

---

## Fase 3: Historia de usuario 1 - Registrar materias y tareas, y verlas ordenadas (Prioridad: P1) 🎯 MVP

**Objetivo**: El estudiante registra materias (nombre y color), crea tareas y ve el listado ordenado por fecha de entrega.

**Prueba independiente**: Registrar una materia, crear tres tareas con fechas desordenadas y comprobar que el listado sale ordenado y con el color de la materia.

### Pruebas de la historia 1 ⚠️ (escribir primero y verificar que fallan)

- [X] T011 [P] [US1] Pruebas de materias en `tests/test_api_materias.py`: crear y listar; nombre duplicado sin distinguir mayúsculas (409); nombre vacío y de 51 caracteres (422); color fuera de la paleta (422); mensajes de error en español
- [X] T012 [P] [US1] Pruebas de tareas en `tests/test_api_tareas.py`: crear con y sin hora (por defecto 23:59); título de 101 caracteres (422); materia inexistente (400); descripción de 501 caracteres (422); fecha inválida (422); listado ordenado por `fecha_entrega` con desempate por `id`

### Implementación de la historia 1

- [X] T013 [US1] Implementar en `app/repositorio.py` `crear_materia` (recorta espacios, calcula `nombre_normalizado` con `casefold()`, convierte la violación de unicidad en un error de dominio) y `listar_materias` con `total_tareas` (depende de T006)
- [X] T014 [US1] Implementar en `app/repositorio.py` `crear_tarea` (guarda `descripcion` vacía como NULL) y `listar_tareas` con `ORDER BY fecha_entrega, id` (depende de T013)
- [X] T015 [US1] Implementar en `app/esquemas.py` los modelos `MateriaEntrada`, `Materia`, `TareaEntrada` (con `fecha` obligatoria, `hora` opcional por defecto `23:59`) y `Tarea`, con los límites exactos de [data-model.md](data-model.md) (depende de T007)
- [X] T016 [US1] Implementar en `app/api.py` los endpoints `GET /api/colores`, `GET/POST /api/materias`, `GET/POST /api/tareas`, con los códigos de respuesta de [contracts/api.md](contracts/api.md), y registrar el router en `app/main.py` (depende de T013, T014, T015)
- [X] T017 [P] [US1] Implementar en `app/static/index.html` los formularios de materia (nombre y selector de color) y de tarea (materia, título, descripción, fecha, hora), con `<label>` asociado a cada campo y atributos `maxlength`
- [X] T018 [US1] Implementar en `app/static/app.js` la carga de materias y tareas con `fetch`, el renderizado del listado con `textContent` (nunca `innerHTML` con datos del usuario), y la muestra de errores por campo; si no hay materias, mostrar el aviso de registrar una primera materia (depende de T016, T017)
- [X] T019 [P] [US1] Implementar en `app/static/estilos.css` el diseño base de una columna que pasa a dos columnas a partir de 768 px, sin desplazamiento horizontal a 360 px (SC-006)

**Punto de control**: La historia 1 es un MVP funcional y probado de forma independiente.

---

## Fase 4: Historia de usuario 2 - Ver tareas vencidas y urgentes destacadas (Prioridad: P2)

**Objetivo**: El listado marca como "vencida" o "urgente" las tareas pendientes según la hora actual.

**Prueba independiente**: Crear tareas con entrega ayer, dentro de 24 horas y dentro de 5 días, y comprobar sus marcas en el listado.

### Pruebas de la historia 2 ⚠️

- [X] T020 [P] [US2] Pruebas unitarias de `calcular_marca` en `tests/test_estado.py`: completada sin marca; vencida 1 minuto después de la entrega; urgente en la hora exacta de entrega y a exactamente 48 h (límite inclusivo); sin marca a 48 h y 1 minuto; sin marca si la entrega es posterior a 48 h
- [X] T021 [P] [US2] Pruebas de API en `tests/test_api_tareas.py`: el campo `marca` aparece en el listado con el valor esperado para cada caso; una tarea completada no lleva marca

### Implementación de la historia 2

- [X] T022 [US2] Implementar `calcular_marca(tarea, ahora)` como función pura en `app/estado.py`, con las cuatro reglas de [data-model.md](data-model.md) evaluadas en orden
- [X] T023 [US2] Integrar `calcular_marca` en `app/api.py` con la hora local del servidor como `ahora` en todas las respuestas que devuelven tareas (listado, creación y edición), y agregar el campo `marca` a `Tarea` en `app/esquemas.py` (depende de T022)
- [X] T024 [US2] Mostrar en `app/static/app.js` la etiqueta de texto "Vencida" o "Urgente" junto a cada tarea, además del color (FR-020)
- [X] T025 [US2] Agregar en `app/static/estilos.css` los estilos de las marcas de vencida y urgente, con contraste suficiente (depende de T024)

**Punto de control**: Las historias 1 y 2 funcionan juntas y las marcas son correctas en los límites de 0 y 48 horas.

---

## Fase 5: Historia de usuario 3 - Completar tareas y filtrar el listado (Prioridad: P3)

**Objetivo**: El estudiante marca o desmarca tareas como completadas y filtra por materia y por estado.

**Prueba independiente**: Con tareas de dos materias, aplicar el filtro de materia y el de "Pendientes" juntos y comprobar el resultado.

### Pruebas de la historia 3 ⚠️

- [X] T026 [P] [US3] Pruebas en `tests/test_api_tareas.py` de `PATCH /api/tareas/{id}/completada`: marcar, desmarcar, 404 y 422 cuando falta el campo o no es booleano
- [X] T027 [P] [US3] Pruebas en `tests/test_api_tareas.py` de filtros: por `materia_id`, por cada valor de `estado`, combinados, `estado` inválido (422), y lista vacía con mensaje cuando no hay resultados

### Implementación de la historia 3

- [X] T028 [US3] Implementar `actualizar_completada` en `app/repositorio.py` (depende de T014)
- [X] T029 [US3] Implementar el endpoint `PATCH /api/tareas/{id}/completada` con el modelo `CompletadaEntrada` en `app/esquemas.py` y `app/api.py` (depende de T028)
- [X] T030 [US3] Implementar en `app/estado.py` la función `es_vencida(tarea, ahora)` y en `app/api.py` los parámetros `materia_id` y `estado` de `GET /api/tareas`, con filtro de "vencidas" aplicado después de calcular la marca (depende de T022, T023)
- [ ] T031 [US3] Implementar en `app/static/app.js` la casilla para completar tareas, los selectores de materia y de estado, y el mensaje de "no hay tareas con este filtro" (FR-024) (depende de T029, T030)
- [ ] T032 [P] [US3] Agregar en `app/static/estilos.css` el estilo de tareas completadas (texto tachado o atenuado, sin marca de vencida ni urgente)

**Punto de control**: Las historias 1 a 3 funcionan de forma independiente y combinada.

---

## Fase 6: Historia de usuario 4 - Editar y eliminar materias y tareas (Prioridad: P4)

**Objetivo**: El estudiante corrige y elimina materias y tareas, con confirmación y aviso del número de tareas afectadas.

**Prueba independiente**: Editar la fecha de una tarea y comprobar su nueva posición y marca; eliminar una materia con tareas y comprobar el aviso y la eliminación en cascada.

### Pruebas de la historia 4 ⚠️

- [ ] T033 [P] [US4] Pruebas en `tests/test_api_materias.py` de `PUT /api/materias/{id}` (validaciones y 409 al repetir nombre) y `DELETE /api/materias/{id}` (204, eliminación en cascada de sus tareas y 404)
- [ ] T034 [P] [US4] Pruebas en `tests/test_api_tareas.py` de `PUT /api/tareas/{id}` (la marca se recalcula con la nueva fecha; 400 si la materia no existe) y `DELETE /api/tareas/{id}` (204 y 404)

### Implementación de la historia 4

- [ ] T035 [US4] Implementar en `app/repositorio.py` `actualizar_materia`, `eliminar_materia`, `actualizar_tarea` y `eliminar_tarea`, reutilizando las reglas de validación de T013 y T014
- [ ] T036 [US4] Implementar en `app/api.py` los endpoints `PUT` y `DELETE` de materias y tareas con los códigos de [contracts/api.md](contracts/api.md) (depende de T035)
- [ ] T037 [US4] Implementar en `app/static/app.js` los botones de editar y eliminar; la eliminación de una materia muestra cuántas tareas se borrarán (`total_tareas`) y solo llama al API si el estudiante confirma (FR-005) (depende de T036)

**Punto de control**: Las cuatro historias funcionan de forma independiente y combinada.

---

## Fase 7: Pulido y temas transversales

**Propósito**: Verificación final y calidad transversal.

- [ ] T038 Ejecutar `uv run pytest` y corregir cualquier fallo hasta que la suite completa pase
- [ ] T039 [P] Revisar en `app/static/index.html` y `app/static/app.js` que todos los formularios tengan etiquetas, que el orden de tabulación sea lógico y que el foco sea visible (Principio V, CHK026 y CHK027)
- [ ] T040 [P] Revisar que todos los mensajes de error visibles y devueltos por la API estén en español, incluido el mensaje de error de validación de T007 (FR-027)
- [ ] T041 Ejecutar a mano los 12 escenarios de [quickstart.md](quickstart.md) y anotar el resultado de cada uno en esta tarea
- [X] T042 [P] Actualizar [quickstart.md](quickstart.md) si algún comando del arranque o de las pruebas cambió durante la implementación

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Fase 1 (Preparación)**: sin dependencias; puede empezar de inmediato.
- **Fase 2 (Fundamentos)**: depende de la fase 1; bloquea todas las historias.
- **Fases 3 a 6 (historias)**: dependen de la fase 2. Se pueden hacer en paralelo, pero el orden
  recomendado es P1 → P2 → P3 → P4 porque P2 usa `estado.py` y P3 depende de P2.
- **Fase 7 (Pulido)**: depende de todas las historias que se quieran entregar.

### Dependencias entre historias

- **US1 (P1)**: sin dependencias de otras historias. Es el MVP.
- **US2 (P2)**: usa las tareas de US1; la lógica de marcas es independiente.
- **US3 (P3)**: usa las marcas de US2 para el filtro "vencidas".
- **US4 (P4)**: reutiliza las validaciones de US1 y el cálculo de US2.

### Dentro de cada historia

- Las pruebas se escriben y se ven fallar antes de implementar.
- Repositorio → esquemas → endpoints → interfaz.

### Oportunidades de paralelismo

- T002, T003 y T004 pueden hacerse a la vez.
- T005, T006, T007 y T010 pueden hacerse a la vez en la fase 2.
- Dentro de cada historia, las dos suites de pruebas marcadas con [P] pueden escribirse en paralelo.
- T017 y T019 (HTML y CSS) pueden hacerse en paralelo con T013 a T016 (backend).

---

## Ejemplo de ejecución en paralelo: Historia 1

```text
# Pruebas de la historia 1 juntas:
Tarea: "Pruebas de materias en tests/test_api_materias.py"
Tarea: "Pruebas de tareas en tests/test_api_tareas.py"

# Interfaz base mientras se implementa el backend:
Tarea: "Formularios en app/static/index.html"
Tarea: "Diseño base en app/static/estilos.css"
```

---

## Estrategia de implementación

### MVP primero (solo historia 1)

1. Completar la fase 1 (Preparación).
2. Completar la fase 2 (Fundamentos).
3. Completar la fase 3 (US1).
4. **Detenerse y validar**: ejecutar los escenarios 1 a 4 y 11 de [quickstart.md](quickstart.md).

### Entrega incremental

1. Preparación + Fundamentos → base lista.
2. US1 → validar → primera entrega (MVP).
3. US2 → validar las marcas en los límites de 0 y 48 horas.
4. US3 → validar filtros y completado.
5. US4 → validar edición y eliminación con confirmación.
6. Pulido → validación completa con quickstart.

---

## Notas

- Las decisiones abiertas de `/speckit-clarify` (eliminación en cascada, límites de longitud,
  definición de "urgente") se implementan con los valores de la especificación. Si el estudiante
  cambia alguna, ajustar las tareas T015, T022 y T037 antes de implementarlas.
- Cada historia debe completarse y validarse antes de pasar a la siguiente prioridad.
- Confirmar que cada prueba falla antes de implementar su funcionalidad.
- Hacer commit después de cada tarea o grupo lógico de tareas.

---

## Phase 8: Convergence

- [X] T043 Anclar la ruta por defecto de la base de datos a la raíz del proyecto en `app/main.py` (en vez de depender del directorio de trabajo) per FR-025 (partial)
- [X] T044 Agregar en `tests/test_api_materias.py` la prueba de unicidad con combinación de tildes y mayúsculas ("FÍSICA" frente a "física" devuelve 409) per FR-002 (partial)
- [X] T045 Agregar en `tests/test_api_tareas.py` la prueba de que una tarea con fecha de entrega en el pasado se acepta y se guarda per Casos límite (fecha pasada) (missing)
- [X] T046 Mostrar en `app/static/app.js` una etiqueta en español por campo en los mensajes de error (por ejemplo "Título", "Materia") en vez del nombre técnico del campo per FR-027 (partial)
- [X] T047 Agregar en `tests/test_api_tareas.py` una prueba automatizada que cierre la aplicación, la vuelva a abrir sobre la misma base y compruebe que las materias y tareas siguen ahí per SC-005 (missing)
- [X] T048 Agregar en `tests/test_api_tareas.py` la aserción de que una tarea nueva se crea con `completada = false` per FR-012 (partial)
- [X] T049 Agregar en `tests/test_api_tareas.py` una prueba de que el listado incluye título, nombre y color de la materia, fecha de entrega y estado por cada tarea per FR-015 (partial)
- [X] T050 Manejar en `app/static/app.js` las respuestas que no son JSON y las fallas de red en `pedir()`, mostrando un mensaje en español per FR-027 (partial)
- [X] T051 Hacer que el aviso "Primero registra una materia" en `app/static/index.html` lleve al formulario de materias (enlace o enfoque del campo nombre) per Casos límite (materia no registrada) (partial)
- [X] T052 Justificar en `specs/001-organizador-tareas/plan.md` o eliminar la variable de entorno `ORGANIZADOR_BD` de `app/main.py` per plan: estructura y configuración (unrequested)
