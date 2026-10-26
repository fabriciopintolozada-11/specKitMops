# Investigación (fase 0): Organizador de tareas académicas UPB

Este documento resuelve las incógnitas del contexto técnico del [plan](plan.md). No quedan
puntos marcados como "NEEDS CLARIFICATION".

## 1. Dónde viven los datos y cómo se usa desde el celular

- **Decisión**: El servidor FastAPI y el archivo SQLite viven en la computadora del estudiante.
  El "dispositivo" de la especificación (FR-025) es esa computadora. Desde el celular se usa la
  aplicación abriendo en el navegador la dirección de la computadora dentro de la misma red
  Wi-Fi (por ejemplo, `http://192.168.1.20:8000`). Computadora y celular ven los mismos datos.
- **Justificación**: Es la forma más simple de cumplir a la vez el stack pedido (FastAPI +
  SQLite, servidor único) y el requisito de uso en celular (FR-028), sin cuentas ni
  sincronización. Al haber un solo usuario, no hace falta autenticación.
- **Alternativas consideradas**:
  - Guardar los datos en el navegador (almacenamiento local) y usar FastAPI solo para servir
    archivos: contradice el pedido de usar SQLite y deja el backend sin función.
  - Desplegar el servidor en internet: exige autenticación para no exponer los datos, lo que
    queda fuera del alcance de esta versión.
- **Impacto en la especificación**: el supuesto "los datos se guardan únicamente en el
  dispositivo" se cumple para la computadora que ejecuta el servidor. El celular es un cliente
  más; si la computadora está apagada, el celular no tiene acceso. Esto debería reflejarse en
  la sección "Supuestos" de [spec.md](spec.md).

## 2. Acceso a SQLite

- **Decisión**: Módulo `sqlite3` de la biblioteca estándar, con SQL escrito a mano en
  `repositorio.py`. Las claves foráneas se activan con `PRAGMA foreign_keys = ON` en cada
  conexión, y la eliminación en cascada de tareas se delega a `ON DELETE CASCADE`.
- **Justificación**: Dos tablas y consultas simples; un ORM agregaría una dependencia y una capa
  de abstracción sin beneficio (principio de simplicidad).
- **Alternativas consideradas**: SQLAlchemy y SQLModel. Descartadas por complejidad innecesaria.

## 3. Creación del esquema

- **Decisión**: `db.py` ejecuta `CREATE TABLE IF NOT EXISTS ...` al iniciar la aplicación. No hay
  herramienta de migraciones.
- **Justificación**: Primera versión sin datos previos que migrar.
- **Alternativas consideradas**: Alembic. Se puede incorporar cuando el esquema cambie con datos
  reales ya guardados.

## 4. Cálculo de "vencida" y "urgente"

- **Decisión**: La marca se calcula en el servidor, en la función pura
  `calcular_marca(tarea, ahora)` de `estado.py`, cada vez que se piden las tareas. `ahora` es la
  hora local de la computadora que ejecuta el servidor. Reglas:
  - completada → sin marca;
  - `fecha_entrega < ahora` → `"vencida"`;
  - `ahora <= fecha_entrega <= ahora + 48 h` → `"urgente"`;
  - en otro caso → sin marca.
- **Justificación**: Una sola fuente de verdad para las reglas (FR-016 a FR-019), comprobable
  con pytest inyectando `ahora`, incluidos los límites de 0 y 48 horas (SC-003). Como el servidor
  corre en la computadora del estudiante, su hora local coincide con la del estudiante.
- **Alternativas consideradas**: Calcular la marca en JavaScript, con la hora del navegador.
  Descartada porque duplica la lógica y deja las reglas sin cubrir con pytest.

## 5. Representación de fechas

- **Decisión**: La fecha de entrega se guarda como texto ISO 8601 en hora local sin zona horaria,
  con precisión de minutos (`"2026-11-03T23:59"`). La API recibe `fecha` (`YYYY-MM-DD`,
  obligatoria) y `hora` (`HH:MM`, opcional; por defecto `23:59`) y responde con
  `fecha_entrega` combinada.
- **Justificación**: El texto ISO se ordena correctamente con `ORDER BY` en SQLite y es fácil de
  leer al depurar. Todo ocurre en una sola zona horaria (la de la computadora).
- **Alternativas consideradas**: Guardar en UTC con zona horaria. Agrega conversiones sin
  beneficio con un único usuario en una sola máquina.

## 6. Validación y mensajes de error en español

- **Decisión**: Esquemas Pydantic con `str_strip_whitespace`, `min_length` y `max_length`, y
  validadores para color y fecha. Un manejador de `RequestValidationError` convierte los errores a
  `{"errores": [{"campo": ..., "mensaje": ...}]}` con mensajes en español. El frontend aplica los
  mismos límites con atributos HTML (`required`, `maxlength`) para dar respuesta inmediata, pero
  el servidor siempre revalida.
- **Justificación**: Cumple FR-027 y el principio de validación de entradas; los mensajes por
  defecto de FastAPI están en inglés.
- **Alternativas consideradas**: Validar a mano en cada endpoint. Más código y más fácil de
  olvidar un caso.

## 7. Unicidad del nombre de materia

- **Decisión**: Columna `nombre` con restricción `UNIQUE COLLATE NOCASE`. Antes de insertar se
  recortan espacios. Si SQLite rechaza por duplicado, la API responde 409 con mensaje en español.
- **Justificación**: La base de datos garantiza la regla aunque haya dos peticiones seguidas.
- **Limitación conocida**: `NOCASE` de SQLite solo ignora mayúsculas en letras ASCII, así que
  "Física" y "FÍSICA" no se detectan como iguales. Para evitarlo se guarda también
  `nombre_normalizado` (en minúsculas con `str.casefold()` de Python) con restricción `UNIQUE`, y
  la unicidad se valida sobre esa columna.

## 8. Orden y filtrado

- **Decisión**: El orden y los filtros por materia y por estado "pendientes" y "completadas" se
  resuelven en SQL (`ORDER BY fecha_entrega, id`). El filtro "vencidas" depende de `ahora` y se
  aplica en Python después de calcular la marca.
- **Justificación**: Con unos cientos de tareas, filtrar en memoria es inmediato (SC-004) y evita
  duplicar la regla de vencimiento en SQL.

## 9. Gestión del entorno y ejecución

- **Decisión**: `pyproject.toml` con dependencias declaradas; el entorno se crea con `uv`
  (`uv sync`) y la app se ejecuta con `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`.
  Las pruebas se ejecutan con `uv run pytest`.
- **Justificación**: `uv` ya está instalado en la máquina y puede instalar Python 3.12 si falta.
  `--host 0.0.0.0` es necesario para entrar desde el celular.
- **Alternativas consideradas**: `pip` + `venv`. Funciona igual; se documenta como alternativa en
  el [quickstart](quickstart.md).

## 10. Frontend sin frameworks

- **Decisión**: Una sola página (`index.html`) con dos secciones (tareas y materias) que se
  alternan con botones; `app.js` usa `fetch` contra `/api` y construye el listado con
  `document.createElement` y `textContent` (nunca `innerHTML` con datos del usuario, para evitar
  inyección de HTML). Diseño con CSS Grid/Flexbox y una media query a partir de 768 px.
- **Justificación**: Cumple el pedido de no usar frameworks y mantiene un solo archivo de lógica.
