# Plan de implementación: Organizador de tareas académicas UPB

**Rama**: `001-organizador-tareas` | **Fecha**: 2026-10-26 | **Especificación**: [spec.md](spec.md)

**Entrada**: Especificación de la funcionalidad en `specs/001-organizador-tareas/spec.md`

## Resumen

Aplicación web de un solo usuario para que un estudiante de la UPB registre sus materias y
tareas, vea las tareas ordenadas por fecha de entrega con marcas de "vencida" y "urgente"
(próximas 48 horas), las marque como completadas y las filtre por materia y estado.

Enfoque técnico: un único proyecto Python 3.12 con FastAPI que expone una API JSON y sirve
también el frontend estático (HTML, CSS y JavaScript sin frameworks). Los datos se guardan en un
archivo SQLite usando el módulo `sqlite3` de la biblioteca estándar, sin ORM. Las marcas
"vencida" y "urgente" se calculan en una función pura que recibe la hora actual como parámetro,
para poder probar los límites exactos con pytest.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (backend); HTML5, CSS3 y JavaScript ES2020 sin frameworks
(frontend).

**Dependencias principales**: FastAPI, Uvicorn (servidor). Pydantic viene incluido con FastAPI.
Para pruebas: pytest y httpx (requerido por el `TestClient` de FastAPI).

**Almacenamiento**: SQLite en un archivo local (`datos/organizador.db`), accedido con el módulo
`sqlite3` de la biblioteca estándar.

**Pruebas**: pytest; pruebas unitarias de las reglas de negocio y pruebas de la API con
`fastapi.testclient.TestClient` sobre una base SQLite temporal.

**Plataforma objetivo**: El servidor corre en la computadora del estudiante (Windows, macOS o
Linux). Se usa desde un navegador moderno en esa computadora o desde un celular conectado a la
misma red Wi-Fi (ver [research.md](research.md), decisión 1).

**Tipo de proyecto**: Aplicación web de un solo proyecto (backend y frontend en el mismo
repositorio y proceso).

**Metas de rendimiento**: Con 200 tareas, listado y filtros responden en menos de 1 segundo
(SC-004).

**Restricciones**: Sin inicio de sesión; un solo usuario. Sin Docker ni microservicios. Interfaz
usable a 360 px de ancho sin desplazamiento horizontal (SC-006). Todos los mensajes al usuario en
español.

**Escala/Alcance**: Un usuario, decenas de materias y cientos de tareas; una sola página web con
dos vistas (tareas y materias).

## Chequeo de la constitución

*PUERTA: debe pasar antes de la fase 0 y volver a revisarse después del diseño de la fase 1.*

> **Advertencia**: `.specify/memory/constitution.md` sigue siendo la plantilla sin rellenar
> (`/speckit-constitution` no llegó a completarse). Como puertas provisionales se usan los cinco
> principios que el usuario propuso para la constitución. Hay que repetir este chequeo cuando la
> constitución quede ratificada.

| Principio (provisional) | Cómo lo cumple el plan | Estado |
|---|---|---|
| I. Simplicidad primero (YAGNI) | Un proyecto, un proceso, sin ORM, sin framework de frontend, sin capa de servicios separada ni migraciones: el esquema se crea al iniciar. | ✅ Pasa |
| II. Pruebas obligatorias | Cada requisito funcional tiene pruebas pytest: unitarias para el cálculo de marcas y validaciones, y de API para cada endpoint. Ninguna tarea se da por terminada sin sus pruebas. | ✅ Pasa |
| III. Código legible | Módulos pequeños con una responsabilidad cada uno (`estado.py`, `repositorio.py`, `esquemas.py`, `api.py`). Nombres de dominio en español, iguales a los de la especificación. | ✅ Pasa |
| IV. Validación de entradas | Toda entrada pasa por esquemas Pydantic con límites de longitud, recorte de espacios, color dentro de la paleta y fechas válidas; los errores se devuelven en español por campo. El frontend valida también, pero el backend es la fuente de verdad. | ✅ Pasa |
| V. Accesible y responsivo | CSS de una sola columna que crece a dos columnas en pantallas anchas; marcas con texto además de color (FR-020); formularios con `<label>` asociados y navegación por teclado. | ✅ Pasa |

**Revisión posterior al diseño (fase 1)**: el modelo de datos, los contratos y la estructura no
introducen componentes nuevos. Las cinco puertas siguen pasando. No hay violaciones que
justificar.

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/001-organizador-tareas/
├── plan.md              # Este archivo (salida de /speckit-plan)
├── research.md          # Salida de la fase 0
├── data-model.md        # Salida de la fase 1
├── quickstart.md        # Salida de la fase 1
├── contracts/
│   └── api.md           # Salida de la fase 1: contrato de la API JSON
├── checklists/
│   └── requirements.md  # Checklist de calidad de la especificación
└── tasks.md             # Salida de la fase 2 (/speckit-tasks; no la crea /speckit-plan)
```

### Código fuente (raíz del repositorio)

```text
pyproject.toml           # Dependencias y configuración de pytest
app/
├── __init__.py
├── main.py              # Crea la app FastAPI, monta /api y los archivos estáticos
├── api.py               # Endpoints de materias y tareas; traduce errores a respuestas
├── esquemas.py          # Modelos Pydantic de entrada y salida, con sus validaciones
├── estado.py            # Funciones puras: calcular marca (vencida/urgente) y filtrar
├── repositorio.py       # Consultas SQL a SQLite (crear, leer, actualizar, eliminar)
├── db.py                # Conexión a SQLite y creación del esquema
├── colores.py           # Paleta predefinida de colores de materia
└── static/
    ├── index.html       # Única página: vista de tareas y vista de materias
    ├── estilos.css      # Estilos responsivos
    └── app.js           # Lógica del frontend: llamadas a la API y renderizado

tests/
├── conftest.py          # Cliente de prueba con base SQLite temporal
├── test_estado.py       # Pruebas unitarias del cálculo de marcas y límites de 48 h
├── test_api_materias.py # Pruebas de la API de materias
└── test_api_tareas.py   # Pruebas de la API de tareas, orden y filtros

datos/                   # Se crea al iniciar; contiene organizador.db (ignorado por git)
```

**Decisión de estructura**: un solo proyecto con el paquete `app/` y la carpeta `tests/` en la
raíz de `speckit-practica`. El frontend vive en `app/static/` porque lo sirve el mismo FastAPI;
no tiene proceso de compilación. No se separan capas de "modelos", "servicios" y "controladores"
porque el dominio tiene solo dos entidades; `estado.py` concentra la única lógica de negocio no
trivial para que sea fácil de probar.

## Seguimiento de complejidad

No aplica: el chequeo de la constitución no tiene violaciones.

## Pendientes heredados de la especificación

- La sesión de `/speckit-clarify` se interrumpió sin respuestas. Este plan mantiene lo que dice la
  especificación: al eliminar una materia se eliminan sus tareas tras avisar y confirmar (FR-005);
  límites de 50/100/500 caracteres (FR-002, FR-007, FR-008); "urgente" con límite de 48 horas
  inclusivo (FR-017). Si esas decisiones cambian, hay que actualizar
  [data-model.md](data-model.md) y [contracts/api.md](contracts/api.md).
- Interpretación de "dispositivo" ajustada a la arquitectura elegida (ver
  [research.md](research.md), decisión 1).

## Asignación de tareas pendientes

Reparto de las 33 tareas pendientes de [tasks.md](tasks.md) en tres grupos de 11, en orden de ID.
Cada grupo es responsable de implementar y marcar como `[X]` sus tareas.

| Responsable | Tareas | Cantidad | Historias y temas |
|---|---|---|---|
| Julio | T020 a T030 | 11 | US2 (marcas vencida y urgente), inicio de US3 (completar y filtrar en el backend) |
| Sergio | T031 a T041 | 11 | US3 (interfaz de completar y filtros), US4 (editar y eliminar), pruebas y revisión de pulido |
| Yo | T042 a T052 | 11 | Actualización de quickstart y tareas de convergencia (T043 a T052) |

### Dependencias entre grupos

- **Sergio, T031**: depende de T029 y T030, que son de Julio. Conviene que Sergio empiece con T032
  (estilos) o con T033 y T034 (pruebas), que no dependen de Julio, mientras Julio termina.
- **Sergio, T037**: depende de T036 (de Sergio), no hay bloqueo externo.
- **Sergio, T038 a T041**: deben ejecutarse al final, cuando las historias 1 a 4 estén completas.
- **Yo, T042**: va al final, porque actualiza `quickstart.md` según lo que quedó implementado.
- **Yo, T043 a T052**: son correcciones de convergencia. Varias tocan archivos que también editan
  los otros grupos (ver abajo), así que conviene hacerlas después de que Julio y Sergio terminen
  sus tareas.

### Archivos compartidos (riesgo de conflictos)

- `app/static/app.js`: Julio (T024), Sergio (T031 y T037), yo (T046 y T050).
- `tests/test_api_tareas.py`: Julio (T021, T026, T027), Sergio (T034), yo (T045, T047, T048, T049).
- `app/main.py`: yo (T043, T052).

Recomendación: hacer `git pull` antes de empezar cada tarea y confirmar cambios en commits chicos,
para que los conflictos en esos tres archivos se resuelvan rápido.
