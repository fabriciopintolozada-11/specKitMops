# Modelo de datos: Organizador de tareas académicas UPB

Fuente: entidades clave y requisitos de [spec.md](spec.md); decisiones técnicas en
[research.md](research.md).

## Entidad: Materia

| Campo | Tipo (SQLite) | Reglas | Origen |
|---|---|---|---|
| `id` | INTEGER, clave primaria autoincremental | Generado por el sistema. | — |
| `nombre` | TEXT, NOT NULL | Se recortan espacios al inicio y al final; de 1 a 50 caracteres. | FR-002 |
| `nombre_normalizado` | TEXT, NOT NULL, UNIQUE | `nombre` recortado y pasado a minúsculas con `casefold()`. Garantiza que no haya dos materias con el mismo nombre sin importar mayúsculas. No se expone en la API. | FR-002, research 7 |
| `color` | TEXT, NOT NULL | Código hexadecimal que debe pertenecer a la paleta predefinida (ver abajo). | FR-003 |

**Relaciones**: una Materia tiene cero o más Tareas. Al eliminar una Materia se eliminan sus
Tareas (`ON DELETE CASCADE`), después de que el estudiante confirme en la interfaz (FR-005).

**Dato derivado en la API**: `total_tareas` (cantidad de tareas asociadas), para que la
interfaz pueda avisar cuántas tareas se eliminarán.

### Paleta predefinida de colores (FR-003)

| Nombre | Código |
|---|---|
| Azul | `#1E66F5` |
| Rojo | `#D20F39` |
| Verde | `#40A02B` |
| Naranja | `#FE640B` |
| Morado | `#8839EF` |
| Rosa | `#EA76CB` |
| Turquesa | `#179299` |
| Gris | `#6C6F85` |

## Entidad: Tarea

| Campo | Tipo (SQLite) | Reglas | Origen |
|---|---|---|---|
| `id` | INTEGER, clave primaria autoincremental | Generado por el sistema. También desempata el orden entre tareas con la misma fecha de entrega (orden de creación). | FR-014 |
| `materia_id` | INTEGER, NOT NULL, clave foránea a `materia.id` con `ON DELETE CASCADE` | Debe existir una materia con ese id. | FR-006 |
| `titulo` | TEXT, NOT NULL | Se recortan espacios; de 1 a 100 caracteres. | FR-007 |
| `descripcion` | TEXT, NULL | Opcional; se recortan espacios; máximo 500 caracteres. Una cadena vacía se guarda como NULL. | FR-008 |
| `fecha_entrega` | TEXT, NOT NULL | Formato `YYYY-MM-DDTHH:MM` en hora local. Se arma con `fecha` (obligatoria) y `hora` (opcional, por defecto `23:59`). Se permiten fechas pasadas. | FR-009 |
| `completada` | INTEGER, NOT NULL, DEFAULT 0 | 0 = pendiente, 1 = completada. Toda tarea nueva empieza en 0. | FR-012, FR-013 |
| `creada_en` | TEXT, NOT NULL | Momento de creación, `YYYY-MM-DDTHH:MM:SS` en hora local. | Entidades clave |

**Índice**: `(fecha_entrega, id)` para el listado ordenado.

### Dato derivado: marca

No se guarda; se calcula en cada consulta con `calcular_marca(tarea, ahora)`:

| Condición (evaluada en este orden) | Marca |
|---|---|
| `completada = 1` | ninguna (`null`) |
| `fecha_entrega < ahora` | `"vencida"` |
| `fecha_entrega <= ahora + 48 horas` | `"urgente"` |
| en otro caso | ninguna (`null`) |

Fuente: FR-016, FR-017, FR-018, FR-019.

### Transiciones de estado

```text
          crear
            │
            ▼
       ┌──────────┐   marcar completada   ┌─────────────┐
       │ pendiente│ ────────────────────► │ completada  │
       │          │ ◄──────────────────── │             │
       └──────────┘   desmarcar           └─────────────┘
```

Mientras está pendiente, la marca pasa de ninguna → "urgente" → "vencida" a medida que avanza
el tiempo. Una tarea completada nunca tiene marca. Al editar la fecha de entrega, la marca se
recalcula (historia 4, escenario 1).

## Esquema SQL de referencia

```sql
CREATE TABLE IF NOT EXISTS materia (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre              TEXT NOT NULL,
    nombre_normalizado  TEXT NOT NULL UNIQUE,
    color               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tarea (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id     INTEGER NOT NULL REFERENCES materia(id) ON DELETE CASCADE,
    titulo         TEXT NOT NULL,
    descripcion    TEXT,
    fecha_entrega  TEXT NOT NULL,
    completada     INTEGER NOT NULL DEFAULT 0 CHECK (completada IN (0, 1)),
    creada_en      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tarea_entrega ON tarea (fecha_entrega, id);
```

Cada conexión debe ejecutar `PRAGMA foreign_keys = ON;` para que la cascada funcione.
