# Checklist de calidad de requisitos: Experiencia de usuario y validación de datos

**Propósito**: Revisar que los requisitos de experiencia de usuario y de validación de datos estén completos, sean claros, consistentes y verificables antes de implementar. Este checklist evalúa lo que está escrito en la especificación y en el plan, no el funcionamiento del sistema.
**Creado**: 2026-10-26
**Funcionalidad**: [spec.md](../spec.md) · [plan.md](../plan.md) · [data-model.md](../data-model.md) · [contracts/api.md](../contracts/api.md)
**Profundidad**: Estándar | **Audiencia**: autor de la especificación, antes de `/speckit-tasks`

**Nota**: Este checklist fue generado por `/speckit-checklist` a partir del contexto de la funcionalidad.
**Propiedad de la revisión**: Es un artefacto de revisión de calidad de requisitos. Marca `[x]` solo cuando el revisor determine que el criterio de calidad se cumple. Marcar `[x]` no significa que la implementación esté terminada.

## Completitud de los requisitos de experiencia de usuario

- [ ] CHK001 - ¿Están definidos los requisitos de la vista de materias (listar, crear, editar, eliminar), o solo se describen las acciones de la vista de tareas? [Completitud, Gap, Spec §FR-001 a FR-005]
- [ ] CHK002 - ¿Están especificados los estados vacíos de cada vista: sin materias, sin tareas y sin resultados con filtros activos? [Completitud, Spec §FR-024, Casos límite]
- [ ] CHK003 - ¿Están definidos los estados de carga y de error mientras la interfaz espera la respuesta del servidor? [Completitud, Gap]
- [ ] CHK004 - ¿Se especifica qué ve el estudiante cuando el servidor no responde o la red falla al intentar guardar? [Excepción, Gap]
- [ ] CHK005 - ¿Están definidos los requisitos de navegación entre la vista de tareas y la vista de materias, incluido cómo se vuelve de un formulario sin perder datos? [Completitud, Gap]
- [ ] CHK006 - ¿Se especifica el comportamiento de la interfaz después de crear, editar o eliminar un elemento (lista actualizada, mensaje de confirmación, posición del foco)? [Completitud, Gap]

## Claridad de los requisitos de validación de datos

- [ ] CHK007 - ¿Los límites de longitud de "nombre de materia" (1 a 50), "título" (1 a 100) y "descripción" (máximo 500) se miden en caracteres, en bytes o en unidades de texto Unicode? [Claridad, Spec §FR-002, FR-007, FR-008]
- [ ] CHK008 - ¿Está definido si los espacios internos repetidos en el nombre o título se conservan, se colapsan o se rechazan, además de recortar los espacios de los extremos? [Ambigüedad, Spec §FR-002]
- [ ] CHK009 - ¿Está especificado qué significa "solo espacios" para la descripción opcional: se guarda como vacía, como nula o se rechaza? [Claridad, Gap, data-model.md]
- [ ] CHK010 - ¿Está definida la regla de unicidad del nombre de materia para tildes y diacríticos (por ejemplo, "Física" frente a "Fisica")? La especificación solo menciona mayúsculas. [Conflicto, Spec §FR-002, plan.md]
- [ ] CHK011 - ¿Está definido qué fechas se consideran válidas al crear o editar una tarea (año mínimo y máximo, fechas inexistentes como el 31 de febrero)? [Completitud, Gap, Spec §FR-009]
- [ ] CHK012 - ¿Está especificado el formato de hora aceptado (24 horas, rango válido, minutos obligatorios) y qué ocurre cuando la hora es inválida? [Claridad, Gap, Spec §FR-009]
- [ ] CHK013 - ¿Está definido si una fecha de entrega en el pasado requiere confirmación adicional o se acepta sin más? [Ambigüedad, Spec §Casos límite]
- [ ] CHK014 - ¿Se especifica qué mensaje ve el estudiante por cada regla de validación incumplida, y que el mensaje debe indicar el campo corregido? [Completitud, Spec §FR-027]
- [ ] CHK015 - ¿Están definidas las reglas de validación de los filtros cuando llega un valor de estado no reconocido? [Cobertura, contracts/api.md]

## Coherencia de los requisitos

- [ ] CHK016 - ¿Coinciden los límites de longitud de la especificación con los de `data-model.md` y `contracts/api.md`? [Consistencia, Spec §FR-002, FR-007, FR-008]
- [ ] CHK017 - ¿La definición de "dispositivo" es consistente entre la especificación (datos en el dispositivo del estudiante) y el plan (datos en la computadora que ejecuta el servidor)? [Conflicto, Spec §FR-025, plan.md, research.md 1]
- [ ] CHK018 - ¿Son consistentes las reglas de "vencida" y "urgente" entre la especificación (FR-016 a FR-018), el modelo de datos y el contrato de la API? [Consistencia, data-model.md, contracts/api.md]
- [ ] CHK019 - ¿Coinciden los requisitos de la historia 4 (editar y eliminar) con los de FR-005 y FR-010 en cuanto a qué se confirma antes de borrar? [Consistencia, Spec §historia 4]
- [ ] CHK020 - ¿Están alineados los requisitos de color con la paleta de ocho colores, de modo que no quede ambiguo qué colores son válidos? [Consistencia, Spec §FR-003, data-model.md]

## Claridad de la experiencia de usuario

- [ ] CHK021 - ¿Está cuantificado qué significa "destacar" una tarea vencida, con criterios visuales concretos además del color? [Claridad, Spec §FR-016]
- [ ] CHK022 - ¿Está definido cómo se distingue "urgente" de "vencida" sin depender solo del color, con texto o ícono especificados? [Medibilidad, Spec §FR-020]
- [ ] CHK023 - ¿Se especifica si el mensaje "no hay tareas" de FR-024 debe diferenciar entre lista vacía y filtro sin resultados? [Claridad, Spec §FR-024]
- [ ] CHK024 - ¿Está definido el texto exacto (o criterios de redacción) de las confirmaciones de eliminación, incluido el número de tareas que se eliminarán? [Claridad, Spec §FR-005]
- [ ] CHK025 - ¿Están definidos los criterios de orden del listado cuando hay empate de fecha, y se explica al usuario de algún modo? [Claridad, Spec §FR-014]

## Requisitos de accesibilidad y uso en celular

- [ ] CHK026 - ¿Están especificados los requisitos de accesibilidad para todos los formularios: etiquetas asociadas, mensajes de error anunciables y orden de tabulación? [Completitud, Gap, Principio V]
- [ ] CHK027 - ¿Se definen los requisitos de navegación solo con teclado para crear, completar, filtrar y eliminar? [Cobertura, Gap]
- [ ] CHK028 - ¿Está cuantificado el "uso en celular" de FR-028 con un ancho mínimo, tamaño de toque y comportamiento de rotación? La especificación solo menciona 360 px en SC-006. [Claridad, Spec §FR-028, SC-006]
- [ ] CHK029 - ¿Están definidos los requisitos de contraste de texto y de las marcas de color de las materias? [Medibilidad, Gap, Spec §FR-003]
- [ ] CHK030 - ¿Está especificado cómo accede el celular a la aplicación (dirección, red y requisitos de conexión), dado que el plan lo define pero la especificación no? [Conflicto, Gap, plan.md, research.md 1]

## Cobertura de escenarios y casos límite

- [ ] CHK031 - ¿Se definen requisitos para escenarios de excepción como datos corruptos o una base de datos no disponible al iniciar? [Cobertura, Excepción, Gap]
- [ ] CHK032 - ¿Están definidos los requisitos para la eliminación de una materia cuya última tarea está siendo editada al mismo tiempo, o se considera fuera de alcance por ser un solo usuario? [Cobertura, Gap]
- [ ] CHK033 - ¿Está especificado si editar la fecha de una tarea completada la devuelve a pendiente, o si la marca de vencida se recalcula solo para tareas pendientes? [Cobertura, Spec §historia 4, FR-018]
- [ ] CHK034 - ¿Están definidos los requisitos de recuperación cuando el estudiante vuelve a la aplicación después de días sin usarla y hay tareas que cambiaron de marca? [Cobertura, Recuperación, Spec §FR-019]
- [ ] CHK035 - ¿Se identifican los límites de rendimiento o de cantidad de tareas por encima de los cuales la interfaz debe reaccionar de forma distinta (paginación, mensaje)? [Cobertura, Spec §SC-004]

## Criterios de aceptación y medibilidad

- [ ] CHK036 - ¿Pueden medirse objetivamente los criterios SC-001 y SC-002 (tiempos de registro y creación) con los requisitos actuales? [Medibilidad, Spec §SC-001, SC-002]
- [ ] CHK037 - ¿Está definido cómo se mide el criterio SC-007 ("90 % identifican sin ayuda las tareas vencidas y urgentes") y qué tamaño de muestra o prueba se usa? [Medibilidad, Ambigüedad, Spec §SC-007]
- [ ] CHK038 - ¿Tienen todos los requisitos funcionales de validación un criterio de aceptación explícito, no solo la regla? [Medibilidad, Spec §FR-027]

## Supuestos, dependencias y ambigüedades

- [ ] CHK039 - ¿Está validado el supuesto de que un mismo nombre de materia nunca debe repetirse, incluso si el estudiante escribe el nombre en otro idioma o con otra ortografía? [Supuesto, Spec §Supuestos]
- [ ] CHK040 - ¿Se documentan los requisitos de respaldo de datos, o el supuesto de que no hay copia de seguridad es un riesgo aceptado por el autor? [Supuesto, Gap, Spec §Supuestos]
- [ ] CHK041 - ¿Está definida la zona horaria de referencia para las marcas de vencimiento cuando la computadora y el celular están en zonas horarias distintas? [Ambigüedad, Gap, Spec §Supuestos]
- [ ] CHK042 - ¿Hay un esquema de identificadores de requisitos para trazar cada criterio de este checklist hasta una pantalla o un endpoint concreto? [Trazabilidad, Gap]

## Notas

- Marca `[x]` solo cuando el revisor confirme que el requisito está escrito con la calidad necesaria.
- Los elementos que requieren aclaración deben quedar sin marcar, y el hallazgo debe anotarse en la línea.
- Los ítems CHK017, CHK030 y CHK010 señalan conflictos o vacíos entre documentos y conviene resolverlos antes de `/speckit-tasks`.
- `/speckit-implement` lee el estado de este checklist pero no modifica las marcas.
- El checklist `checklists/requirements.md` tiene su propio ciclo de vida y no se modifica con este comando.
