# Contrato de la API JSON

Base: `/api`. Todas las peticiones y respuestas usan JSON en UTF-8. Los campos y reglas de
validación se describen en [data-model.md](../data-model.md).

## Formato de error común

Toda respuesta de error tiene esta forma, con mensajes en español:

```json
{
  "errores": [
    { "campo": "titulo", "mensaje": "El título es obligatorio." }
  ]
}
```

`campo` es `null` cuando el error no corresponde a un campo concreto.

| Código | Cuándo |
|---|---|
| 400 | Datos con formato correcto pero inválidos por una regla de negocio (por ejemplo, `materia_id` que no existe al crear una tarea). |
| 404 | El recurso de la ruta (`{id}`) no existe. |
| 409 | Ya existe una materia con ese nombre. |
| 422 | Faltan datos, sobran caracteres, color fuera de la paleta o fecha/hora inválida. |

## Colores

### `GET /api/colores`

Devuelve la paleta predefinida.

**200**:

```json
[ { "nombre": "Azul", "codigo": "#1E66F5" }, { "nombre": "Rojo", "codigo": "#D20F39" } ]
```

## Materias

### Objeto `Materia`

```json
{ "id": 1, "nombre": "Cálculo II", "color": "#1E66F5", "total_tareas": 3 }
```

### `GET /api/materias`

Lista todas las materias ordenadas por nombre (sin distinguir mayúsculas). **200**: `Materia[]`.

### `POST /api/materias`

**Cuerpo**: `{ "nombre": "Cálculo II", "color": "#1E66F5" }`

- **201**: `Materia` creada (`total_tareas` = 0).
- **409**: nombre duplicado. **422**: nombre vacío o de más de 50 caracteres; color fuera de la paleta.

### `PUT /api/materias/{id}`

**Cuerpo**: igual que `POST`. Reemplaza nombre y color.

- **200**: `Materia` actualizada. **404**, **409**, **422** como arriba.

### `DELETE /api/materias/{id}`

Elimina la materia y todas sus tareas. La confirmación con el número de tareas
(`total_tareas`) la pide la interfaz antes de llamar a este endpoint.

- **204**: eliminada (sin cuerpo). **404**: no existe.

## Tareas

### Objeto `Tarea`

```json
{
  "id": 7,
  "materia": { "id": 1, "nombre": "Cálculo II", "color": "#1E66F5" },
  "titulo": "Práctica 3",
  "descripcion": null,
  "fecha_entrega": "2026-11-03T23:59",
  "completada": false,
  "creada_en": "2026-10-26T14:05:12",
  "marca": "urgente"
}
```

`marca` es `"vencida"`, `"urgente"` o `null`, calculada con la hora actual del servidor en cada
respuesta (ver [data-model.md](../data-model.md#dato-derivado-marca)).

### `GET /api/tareas`

Lista tareas ordenadas por `fecha_entrega` ascendente y, ante empate, por `id`.

**Parámetros de consulta** (opcionales y combinables):

| Parámetro | Valores | Por defecto |
|---|---|---|
| `materia_id` | id de una materia existente | todas las materias |
| `estado` | `todas`, `pendientes`, `completadas`, `vencidas` | `todas` |

- **200**: `Tarea[]` (lista vacía si no hay resultados; la interfaz muestra el mensaje de FR-024).
- **422**: `estado` con un valor no permitido. Un `materia_id` inexistente devuelve lista vacía.

### `POST /api/tareas`

**Cuerpo**:

```json
{
  "materia_id": 1,
  "titulo": "Práctica 3",
  "descripcion": "Ejercicios 1 al 10",
  "fecha": "2026-11-03",
  "hora": "18:00"
}
```

`descripcion` y `hora` son opcionales; sin `hora` se usa `23:59`. La tarea se crea pendiente.

- **201**: `Tarea` creada.
- **400**: `materia_id` no existe. **422**: título vacío o de más de 100 caracteres; descripción
  de más de 500; fecha u hora faltante o inválida.

### `PUT /api/tareas/{id}`

**Cuerpo**: igual que `POST`. Reemplaza todos los datos editables (no cambia `completada`).

- **200**: `Tarea` actualizada con la marca recalculada. **400**, **404**, **422** como arriba.

### `PATCH /api/tareas/{id}/completada`

**Cuerpo**: `{ "completada": true }` o `{ "completada": false }`.

- **200**: `Tarea` actualizada. **404**: no existe. **422**: falta `completada` o no es booleano.

### `DELETE /api/tareas/{id}`

La confirmación la pide la interfaz antes de llamar a este endpoint.

- **204**: eliminada. **404**: no existe.

## Interfaz web

`GET /` devuelve `index.html`; los archivos estáticos se sirven desde `/static/`. La interfaz
consume exclusivamente los endpoints anteriores.
