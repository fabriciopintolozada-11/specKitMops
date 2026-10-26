# Especificación de funcionalidad: Organizador de tareas académicas UPB

**Rama de la funcionalidad**: `001-organizador-tareas`

**Creada**: 2026-10-26

**Estado**: Borrador

**Entrada**: Descripción del usuario: "Quiero una aplicación para estudiantes de la UPB que les ayude
a organizar sus tareas académicas. El estudiante puede registrar sus materias (nombre y color).
Puede crear tareas asociadas a una materia, con título, descripción opcional y fecha de entrega.
Ve un listado de tareas ordenado por fecha de entrega, donde las tareas vencidas se destacan y las
próximas 48 horas aparecen como "urgentes". Puede marcar tareas como completadas y filtrarlas por
materia o por estado. En esta primera versión no hay inicio de sesión: es un solo usuario por
dispositivo. Todo el contenido de la especificación debe estar en español."

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Registrar materias y tareas, y verlas ordenadas (Prioridad: P1)

El estudiante registra las materias que cursa este semestre, cada una con un nombre y un color.
Luego crea tareas dentro de cada materia, indicando título, una descripción opcional y la fecha
de entrega. Al abrir la aplicación ve todas sus tareas en un solo listado, ordenadas de la entrega
más próxima a la más lejana, y cada tarea muestra el color y nombre de su materia.

**Por qué esta prioridad**: Es el núcleo de la aplicación. Sin materias y tareas registradas no
existe nada que organizar; con solo esta historia el estudiante ya tiene una agenda útil.

**Prueba independiente**: Se registra una materia, se crean tres tareas con fechas distintas en
desorden y se comprueba que el listado las muestra ordenadas por fecha de entrega, con el color
de la materia.

**Escenarios de aceptación**:

1. **Dado** que no hay materias registradas, **Cuando** el estudiante registra la materia
   "Cálculo II" con color azul, **Entonces** la materia aparece en su lista de materias con ese
   nombre y color.
2. **Dado** que existe la materia "Cálculo II", **Cuando** el estudiante crea una tarea con
   título "Práctica 3" y fecha de entrega válida, sin descripción, **Entonces** la tarea se guarda
   y aparece en el listado asociada a "Cálculo II".
3. **Dado** que existen tareas con entregas el 5, el 2 y el 9 del mes, **Cuando** el estudiante
   abre el listado, **Entonces** las ve en el orden 2, 5, 9.
4. **Dado** que el estudiante intenta crear una tarea sin título o sin fecha de entrega,
   **Cuando** intenta guardarla, **Entonces** la tarea no se guarda y se le indica qué dato falta.
5. **Dado** que el estudiante registró materias y tareas, **Cuando** cierra la aplicación y la
   vuelve a abrir en el mismo dispositivo, **Entonces** sus materias y tareas siguen ahí.

---

### Historia de usuario 2 - Ver tareas vencidas y urgentes destacadas (Prioridad: P2)

En el listado, las tareas pendientes cuya fecha de entrega ya pasó se destacan como "vencidas",
y las tareas pendientes que vencen dentro de las próximas 48 horas se marcan como "urgentes".
Así el estudiante identifica de un vistazo qué necesita atención inmediata.

**Por qué esta prioridad**: Es el principal valor sobre una lista simple: ayuda a no olvidar
entregas. Depende de que existan tareas (P1), pero se puede probar por separado.

**Prueba independiente**: Se crean tareas pendientes con entrega ayer, dentro de 24 horas y
dentro de 5 días, y se verifica que se muestran como vencida, urgente y sin marca,
respectivamente.

**Escenarios de aceptación**:

1. **Dado** una tarea pendiente cuya fecha y hora de entrega ya pasaron, **Cuando** el estudiante
   ve el listado, **Entonces** la tarea aparece destacada como "vencida".
2. **Dado** una tarea pendiente que vence dentro de las próximas 48 horas, **Cuando** el
   estudiante ve el listado, **Entonces** la tarea aparece marcada como "urgente".
3. **Dado** una tarea pendiente que vence en más de 48 horas, **Cuando** el estudiante ve el
   listado, **Entonces** no lleva marca de vencida ni de urgente.
4. **Dado** una tarea completada con fecha de entrega pasada o próxima, **Cuando** el estudiante
   ve el listado, **Entonces** no se marca como vencida ni como urgente.
5. **Dado** una tarea marcada como urgente, **Cuando** pasa su hora de entrega sin completarse,
   **Entonces** la siguiente vez que el estudiante ve el listado aparece como "vencida".

---

### Historia de usuario 3 - Completar tareas y filtrar el listado (Prioridad: P3)

El estudiante marca una tarea como completada cuando la entrega; si se equivocó, puede volver a
marcarla como pendiente. También puede filtrar el listado por materia, por estado, o por ambos a
la vez, para concentrarse en lo que le interesa.

**Por qué esta prioridad**: Mejora el uso diario cuando ya hay muchas tareas, pero la aplicación
es útil sin esta historia.

**Prueba independiente**: Con tareas de dos materias, algunas completadas, se aplica el filtro
"Cálculo II" + "Pendientes" y se comprueba que solo se ven las tareas pendientes de esa materia.

**Escenarios de aceptación**:

1. **Dado** una tarea pendiente, **Cuando** el estudiante la marca como completada, **Entonces**
   la tarea queda en estado "completada" y deja de mostrarse como vencida o urgente.
2. **Dado** una tarea completada, **Cuando** el estudiante la desmarca, **Entonces** vuelve a
   estado "pendiente" y recupera la marca de vencida o urgente que le corresponda.
3. **Dado** tareas de varias materias, **Cuando** el estudiante filtra por la materia
   "Física I", **Entonces** solo ve las tareas de esa materia, en orden de fecha de entrega.
4. **Dado** tareas en distintos estados, **Cuando** el estudiante filtra por estado
   "Completadas", **Entonces** solo ve las tareas completadas.
5. **Dado** un filtro activo que no tiene resultados, **Cuando** el estudiante ve el listado,
   **Entonces** se muestra un mensaje que indica que no hay tareas con ese filtro.
6. **Dado** un filtro activo, **Cuando** el estudiante lo quita, **Entonces** vuelve a ver todas
   las tareas.

---

### Historia de usuario 4 - Editar y eliminar materias y tareas (Prioridad: P4)

El estudiante corrige datos de una materia (nombre o color) o de una tarea (título, descripción,
fecha de entrega o materia), y elimina materias o tareas que ya no necesita.

**Por qué esta prioridad**: Evita que un error al registrar obligue a convivir con datos
incorrectos, pero no es imprescindible para el primer uso.

**Prueba independiente**: Se edita la fecha de una tarea y se comprueba que cambia su posición en
el listado; se elimina una tarea y se comprueba que desaparece.

**Escenarios de aceptación**:

1. **Dado** una tarea existente, **Cuando** el estudiante cambia su fecha de entrega, **Entonces**
   el listado la reubica según la nueva fecha y recalcula su marca de vencida o urgente.
2. **Dado** una materia existente, **Cuando** el estudiante cambia su color, **Entonces** todas
   sus tareas se muestran con el nuevo color.
3. **Dado** una tarea existente, **Cuando** el estudiante la elimina y confirma, **Entonces** la
   tarea desaparece del listado.
4. **Dado** una materia con tareas asociadas, **Cuando** el estudiante intenta eliminarla,
   **Entonces** se le avisa cuántas tareas se eliminarán junto con ella y solo se elimina si
   confirma.

---

### Casos límite

- ¿Qué pasa si el estudiante intenta crear una tarea sin tener ninguna materia registrada? Se le
  indica que primero debe registrar una materia y se le ofrece hacerlo.
- ¿Qué pasa si registra una materia con un nombre que ya existe (sin importar mayúsculas,
  minúsculas o espacios al inicio y al final)? No se guarda y se le indica que el nombre ya existe.
- ¿Qué pasa si el nombre de la materia o el título de la tarea solo contiene espacios? Se trata
  como vacío y no se guarda.
- ¿Qué pasa si se registra una tarea con fecha de entrega en el pasado? Se permite (por ejemplo,
  para registrar una entrega atrasada) y la tarea aparece como vencida si está pendiente.
- ¿Qué pasa si la fecha de entrega se indica sin hora? Se toma como hora de entrega las 23:59 de
  ese día.
- ¿Qué pasa con una tarea que vence exactamente dentro de 48 horas? Se considera urgente (el
  límite de 48 horas es inclusivo).
- ¿Qué pasa si dos tareas tienen la misma fecha y hora de entrega? Se muestran en el orden en que
  fueron creadas.
- ¿Qué pasa si el listado está vacío (no hay tareas)? Se muestra un mensaje que invita a crear la
  primera tarea.
- ¿Qué pasa si el texto ingresado supera la longitud máxima permitida? No se guarda y se indica el
  máximo permitido.
- ¿Qué pasa si el estudiante usa la aplicación en otro dispositivo? No ve los datos del primero,
  porque los datos se guardan solo en el dispositivo donde se registraron.

## Requisitos *(obligatorio)*

### Requisitos funcionales

**Materias**

- **FR-001**: El sistema DEBE permitir registrar una materia con nombre y color.
- **FR-002**: El nombre de la materia DEBE ser obligatorio, tener entre 1 y 50 caracteres (sin
  contar espacios al inicio y al final) y ser único sin distinguir mayúsculas de minúsculas.
- **FR-003**: El color de la materia DEBE elegirse de una paleta predefinida de al menos
  8 colores distinguibles entre sí.
- **FR-004**: El sistema DEBE permitir editar el nombre y el color de una materia, aplicando las
  mismas validaciones que al registrarla.
- **FR-005**: El sistema DEBE permitir eliminar una materia; si tiene tareas asociadas, DEBE
  informar cuántas se eliminarán y pedir confirmación antes de eliminar la materia y sus tareas.

**Tareas**

- **FR-006**: El sistema DEBE permitir crear una tarea asociada a exactamente una materia
  existente, con título, descripción opcional y fecha de entrega.
- **FR-007**: El título de la tarea DEBE ser obligatorio y tener entre 1 y 100 caracteres (sin
  contar espacios al inicio y al final).
- **FR-008**: La descripción de la tarea DEBE ser opcional y tener como máximo 500 caracteres.
- **FR-009**: La fecha de entrega DEBE ser obligatoria y válida; la hora es opcional y, si no se
  indica, se toma como las 23:59 de ese día.
- **FR-010**: El sistema DEBE permitir editar todos los datos de una tarea, incluida su materia,
  aplicando las mismas validaciones que al crearla.
- **FR-011**: El sistema DEBE permitir eliminar una tarea, previa confirmación.
- **FR-012**: Toda tarea nueva DEBE crearse en estado "pendiente".
- **FR-013**: El sistema DEBE permitir marcar una tarea pendiente como completada y una tarea
  completada como pendiente.

**Listado y marcas**

- **FR-014**: El sistema DEBE mostrar un listado de tareas ordenado por fecha y hora de entrega,
  de la más próxima a la más lejana; ante empate, por orden de creación.
- **FR-015**: Cada tarea del listado DEBE mostrar su título, el nombre y color de su materia, su
  fecha de entrega y su estado.
- **FR-016**: El sistema DEBE destacar como "vencida" toda tarea pendiente cuya fecha y hora de
  entrega sean anteriores al momento actual.
- **FR-017**: El sistema DEBE marcar como "urgente" toda tarea pendiente cuya entrega esté entre el
  momento actual y las 48 horas siguientes, ambos límites incluidos.
- **FR-018**: Las tareas completadas NO DEBEN mostrarse como vencidas ni como urgentes.
- **FR-019**: Las marcas de vencida y urgente DEBEN calcularse respecto a la fecha y hora actuales
  del dispositivo cada vez que se muestra el listado.
- **FR-020**: Las marcas de vencida y urgente DEBEN distinguirse con texto o ícono además del
  color, para que no dependan solo de la percepción del color.

**Filtros**

- **FR-021**: El sistema DEBE permitir filtrar el listado por una materia.
- **FR-022**: El sistema DEBE permitir filtrar el listado por estado: "Todas", "Pendientes",
  "Completadas" o "Vencidas".
- **FR-023**: Los filtros por materia y por estado DEBEN poder combinarse, y el listado filtrado
  DEBE conservar el orden por fecha de entrega.
- **FR-024**: El sistema DEBE mostrar un mensaje cuando el listado (con o sin filtros) no tiene
  tareas que mostrar.

**Datos, validación y uso**

- **FR-025**: El sistema DEBE guardar materias y tareas en el dispositivo del estudiante, de modo
  que se conserven al cerrar y volver a abrir la aplicación.
- **FR-026**: El sistema NO DEBE requerir inicio de sesión ni registro de cuenta.
- **FR-027**: El sistema DEBE validar todos los datos ingresados antes de guardarlos y, si alguno
  no es válido, no guardar nada y mostrar un mensaje que indique qué campo corregir y por qué.
- **FR-028**: La interfaz DEBE poder usarse completa tanto en un celular como en una computadora.

### Entidades clave

- **Materia**: Asignatura que cursa el estudiante. Atributos: nombre (único) y color. Una materia
  tiene cero o más tareas.
- **Tarea**: Trabajo académico que el estudiante debe entregar. Atributos: título, descripción
  (opcional), fecha y hora de entrega, estado (pendiente o completada) y momento de creación.
  Pertenece a exactamente una materia. Las condiciones "vencida" y "urgente" no se guardan: se
  derivan del estado, la fecha de entrega y el momento actual.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: Un estudiante que usa la aplicación por primera vez registra una materia y crea su
  primera tarea en menos de 2 minutos.
- **SC-002**: Un estudiante crea una tarea adicional en menos de 30 segundos.
- **SC-003**: El 100 % de las tareas pendientes vencidas y urgentes se muestran con su marca
  correcta en los casos de prueba definidos, incluidos los límites de 0 y 48 horas.
- **SC-004**: Con 200 tareas registradas, el listado y los filtros muestran el resultado en menos
  de 1 segundo desde la acción del estudiante.
- **SC-005**: El 100 % de las materias y tareas registradas se conservan tras cerrar y volver a
  abrir la aplicación en el mismo dispositivo.
- **SC-006**: Todas las acciones de las historias de usuario 1 a 4 pueden completarse en una
  pantalla de celular de 360 px de ancho y en una de computadora, sin desplazamiento horizontal.
- **SC-007**: El 90 % de los estudiantes que prueban la aplicación identifican sin ayuda qué
  tareas están vencidas y cuáles son urgentes.

## Supuestos

- Los usuarios son estudiantes de la UPB que usan la aplicación de forma individual en su propio
  dispositivo; en esta versión no hay cuentas, sincronización ni uso compartido entre dispositivos.
- Los datos se guardan únicamente en el dispositivo; si el estudiante borra los datos de la
  aplicación, pierde sus materias y tareas. No hay copia de seguridad en esta
  versión.
- La fecha y hora actuales se toman del dispositivo del estudiante y se usa su zona horaria local.
- Fuera de alcance en esta versión: notificaciones o recordatorios, tareas recurrentes,
  calificaciones, archivos adjuntos, calendario mensual, integración con sistemas de la UPB y
  exportación de datos.
- La interfaz está en español.
- Se incluyen editar y eliminar materias y tareas (historia 4), aunque la descripción original no
  los menciona, porque sin ellos un error al registrar no tendría corrección.
- El filtro "Vencidas" se incluye como estado porque las tareas vencidas son una condición que el
  estudiante necesita revisar por separado; "Urgentes" no se incluye como filtro porque, por
  el orden por fecha, ya aparecen al inicio del listado, justo después de las vencidas.
