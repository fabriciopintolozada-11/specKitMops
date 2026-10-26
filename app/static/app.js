// Insertar siempre los datos del usuario con textContent, nunca como HTML.
const porId = (id) => document.getElementById(id);
const formMateria = porId("form-materia");
const formTarea = porId("form-tarea");
const filtroMateria = porId("filtro-materia");
const filtroEstado = porId("filtro-estado");
const erroresListado = porId("errores-listado");
let materiaEnEdicion = null;
let tareaEnEdicion = null;
let solicitudTareas = 0;

const MENSAJE_SIN_CONEXION = "No se pudo conectar con el servidor. Revisa la conexión e inténtalo de nuevo.";
const MENSAJE_INESPERADO = "El servidor devolvió una respuesta inesperada. Inténtalo de nuevo.";

function errorDeApi(errores) {
  const error = new Error(MENSAJE_INESPERADO);
  error.errores = errores;
  return error;
}

async function pedir(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(ruta, {
      headers: { "Content-Type": "application/json" },
      ...opciones,
    });
  } catch {
    throw errorDeApi([{ campo: null, mensaje: MENSAJE_SIN_CONEXION }]);
  }
  if (respuesta.status === 204) return null;

  let datos = null;
  try {
    datos = await respuesta.json();
  } catch {
    // La respuesta no es JSON (por ejemplo, un error del servidor sin cuerpo).
  }
  if (!respuesta.ok) {
    throw errorDeApi(datos?.errores ?? [{ campo: null, mensaje: MENSAJE_INESPERADO }]);
  }
  if (datos === null) {
    throw errorDeApi([{ campo: null, mensaje: MENSAJE_INESPERADO }]);
  }
  return datos;
}

const etiquetas = {
  nombre: "Nombre", color: "Color", materia_id: "Materia", titulo: "Título",
  descripcion: "Descripción", fecha: "Fecha", hora: "Hora", estado: "Estado",
  completada: "Completada",
};

function limpiarErrores(lista) {
  lista.replaceChildren();
  lista.closest("form")?.querySelectorAll("[aria-invalid]").forEach((campo) => {
    campo.removeAttribute("aria-invalid");
    campo.removeAttribute("aria-describedby");
  });
}

function mostrarError(lista, error) {
  limpiarErrores(lista);
  // Los errores del navegador (red/JSON) también se presentan en español.
  const errores = error.errores ?? [{ campo: null, mensaje: "No se pudo completar la operación. Revisa la conexión e inténtalo de nuevo." }];
  const formulario = lista.closest("form");
  let primerCampo;
  errores.forEach((error) => {
    const item = document.createElement("li");
    item.textContent = error.campo ? `${etiquetas[error.campo] ?? "Campo"}: ${error.mensaje}` : error.mensaje;
    lista.append(item);
    const campo = error.campo ? formulario?.elements.namedItem(error.campo) : null;
    if (campo) {
      campo.setAttribute("aria-invalid", "true");
      campo.setAttribute("aria-describedby", lista.id);
      if (!primerCampo) primerCampo = campo;
    }
  });
  primerCampo?.focus();
}

function muestraColor(color) {
  const muestra = document.createElement("span");
  muestra.className = "muestra-color";
  muestra.style.backgroundColor = color;
  muestra.setAttribute("aria-hidden", "true");
  return muestra;
}

function botonAccion(texto, nombre, accion) {
  const boton = document.createElement("button");
  boton.type = "button";
  boton.textContent = texto;
  boton.setAttribute("aria-label", `${texto}: ${nombre}`);
  boton.addEventListener("click", async () => {
    limpiarErrores(erroresListado);
    boton.disabled = true;
    try { await accion(); }
    catch (error) { mostrarError(erroresListado, error); }
    finally { boton.disabled = false; }
  });
  return boton;
}

function acciones(...botones) {
  const contenedor = document.createElement("div");
  contenedor.className = "acciones";
  contenedor.append(...botones);
  return contenedor;
}

function cancelarEdicion(tipo, enfocar = true) {
  if (tipo === "materia") materiaEnEdicion = null;
  else tareaEnEdicion = null;
  porId(`form-${tipo}`).reset();
  porId(`guardar-${tipo}`).textContent = `Agregar ${tipo}`;
  porId(`cancelar-${tipo}`).hidden = true;
  limpiarErrores(porId(`errores-${tipo}`));
  if (enfocar && !porId(`form-${tipo}`).hidden) porId(tipo === "materia" ? "materia-nombre" : "tarea-titulo").focus();
}

function editarMateria(materia) {
  limpiarErrores(porId("errores-materia"));
  materiaEnEdicion = materia.id;
  porId("materia-nombre").value = materia.nombre;
  porId("materia-color").value = materia.color;
  porId("guardar-materia").textContent = "Guardar materia";
  porId("cancelar-materia").hidden = false;
  porId("materia-nombre").focus();
}

function editarTarea(tarea) {
  limpiarErrores(porId("errores-tarea"));
  tareaEnEdicion = tarea.id;
  porId("tarea-materia").value = tarea.materia.id;
  porId("tarea-titulo").value = tarea.titulo;
  porId("tarea-descripcion").value = tarea.descripcion ?? "";
  const [fecha, hora] = tarea.fecha_entrega.split("T");
  porId("tarea-fecha").value = fecha;
  porId("tarea-hora").value = hora;
  porId("guardar-tarea").textContent = "Guardar tarea";
  porId("cancelar-tarea").hidden = false;
  porId("tarea-titulo").focus();
}

async function eliminarMateria(materia) {
  // Actualizar el conteo antes de confirmar, incluso si otra pestaña creó tareas.
  const actual = (await pedir("/api/materias")).find((item) => item.id === materia.id);
  if (!actual) { await recargarTodo(); return; }
  if (!window.confirm(`¿Eliminar la materia «${actual.nombre}»? Se eliminarán también ${actual.total_tareas} tareas. Esta acción no se puede deshacer.`)) return;
  await pedir(`/api/materias/${materia.id}`, { method: "DELETE" });
  if (materiaEnEdicion === materia.id) cancelarEdicion("materia", false);
  if (tareaEnEdicion !== null && Number(porId("tarea-materia").value) === materia.id) cancelarEdicion("tarea", false);
  await recargarTodo();
  porId("materia-nombre").focus();
}

async function eliminarTarea(tarea) {
  if (!window.confirm(`¿Eliminar la tarea «${tarea.titulo}»? Esta acción no se puede deshacer.`)) return;
  await pedir(`/api/tareas/${tarea.id}`, { method: "DELETE" });
  if (tareaEnEdicion === tarea.id) cancelarEdicion("tarea", false);
  await recargarTodo();
  filtroEstado.focus();
}

function actualizarOpciones(selector, materias, incluirTodas = false) {
  const seleccionado = selector.value;
  selector.replaceChildren(
    ...(incluirTodas ? [new Option("Todas las materias", "")] : []),
    ...materias.map((materia) => new Option(materia.nombre, materia.id))
  );
  if ([...selector.options].some((opcion) => opcion.value === seleccionado)) selector.value = seleccionado;
}

async function cargarMaterias() {
  const materias = await pedir("/api/materias");
  porId("lista-materias").replaceChildren(...materias.map((materia) => {
    const item = document.createElement("li");
    item.append(muestraColor(materia.color), `${materia.nombre} (${materia.total_tareas} tareas)`);
    item.append(acciones(
      botonAccion("Editar", materia.nombre, () => editarMateria(materia)),
      botonAccion("Eliminar", materia.nombre, () => eliminarMateria(materia))
    ));
    return item;
  }));
  actualizarOpciones(porId("tarea-materia"), materias);
  actualizarOpciones(filtroMateria, materias, true);
  porId("aviso-sin-materias").hidden = materias.length > 0;
  formTarea.hidden = materias.length === 0;
}

function renderizarTarea(tarea) {
  const item = document.createElement("li");
  item.className = tarea.completada ? "tarea completada" : "tarea";
  const titulo = document.createElement("strong");
  titulo.textContent = tarea.titulo;
  const materia = document.createElement("span");
  materia.className = "materia";
  materia.append(muestraColor(tarea.materia.color), tarea.materia.nombre);
  const entrega = document.createElement("time");
  entrega.dateTime = tarea.fecha_entrega;
  const [fecha, hora] = tarea.fecha_entrega.split("T");
  const [anio, mes, dia] = fecha.split("-");
  entrega.textContent = `Entrega: ${dia}/${mes}/${anio} ${hora}`;
  item.append(titulo, materia, entrega);
  if (tarea.descripcion) {
    const descripcion = document.createElement("p");
    descripcion.textContent = tarea.descripcion;
    item.append(descripcion);
  }
  if (!tarea.completada && ["vencida", "urgente"].includes(tarea.marca)) {
    const marca = document.createElement("span");
    marca.className = `marca ${tarea.marca}`;
    marca.textContent = tarea.marca === "vencida" ? "Vencida" : "Urgente";
    item.append(marca);
  }
  const casilla = document.createElement("input");
  casilla.type = "checkbox";
  casilla.id = `completada-${tarea.id}`;
  casilla.checked = tarea.completada;
  casilla.setAttribute("aria-label", `Completada: ${tarea.titulo}`);
  const etiqueta = document.createElement("label");
  etiqueta.className = "completar";
  etiqueta.htmlFor = casilla.id;
  etiqueta.append(casilla, tarea.completada ? "Completada" : "Marcar como completada");
  casilla.addEventListener("change", async () => {
    limpiarErrores(erroresListado);
    casilla.disabled = true;
    try {
      await pedir(`/api/tareas/${tarea.id}/completada`, {
        method: "PATCH", body: JSON.stringify({ completada: casilla.checked }),
      });
      await cargarTareas();
      // El filtro puede ocultar la tarea: conservar el foco en un control estable.
      (porId(casilla.id) ?? filtroEstado).focus();
    } catch (error) {
      casilla.checked = tarea.completada;
      mostrarError(erroresListado, error);
    } finally { casilla.disabled = false; }
  });
  item.append(etiqueta, acciones(
    botonAccion("Editar", tarea.titulo, () => editarTarea(tarea)),
    botonAccion("Eliminar", tarea.titulo, () => eliminarTarea(tarea))
  ));
  return item;
}

async function cargarTareas() {
  const solicitud = ++solicitudTareas;
  const parametros = new URLSearchParams({ estado: filtroEstado.value });
  if (filtroMateria.value) parametros.set("materia_id", filtroMateria.value);
  const tareas = await pedir(`/api/tareas?${parametros}`);
  if (solicitud !== solicitudTareas) return;
  const filtrado = filtroMateria.value !== "" || filtroEstado.value !== "todas";
  porId("aviso-sin-tareas").hidden = tareas.length > 0;
  porId("aviso-sin-tareas").textContent = filtrado
    ? "No hay tareas con este filtro."
    : "Todavía no tienes tareas. Agrega la primera con el formulario de arriba.";
  porId("lista-tareas").replaceChildren(...tareas.map(renderizarTarea));
}

async function recargarTodo() {
  // Actualizar primero los selectores por si desapareció la materia filtrada.
  await cargarMaterias();
  await cargarTareas();
}

formMateria.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limpiarErrores(porId("errores-materia"));
  const datos = new FormData(formMateria);
  const boton = porId("guardar-materia");
  boton.disabled = true;
  try {
    await pedir(materiaEnEdicion === null ? "/api/materias" : `/api/materias/${materiaEnEdicion}`, {
      method: materiaEnEdicion === null ? "POST" : "PUT",
      body: JSON.stringify({ nombre: datos.get("nombre"), color: datos.get("color") }),
    });
    cancelarEdicion("materia");
    await recargarTodo();
  } catch (error) { mostrarError(porId("errores-materia"), error); }
  finally { boton.disabled = false; }
});

formTarea.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limpiarErrores(porId("errores-tarea"));
  const datos = new FormData(formTarea);
  const cuerpo = {
    materia_id: Number(datos.get("materia_id")), titulo: datos.get("titulo"),
    fecha: datos.get("fecha"), descripcion: datos.get("descripcion"),
  };
  if (datos.get("hora")) cuerpo.hora = datos.get("hora");
  const boton = porId("guardar-tarea");
  boton.disabled = true;
  try {
    await pedir(tareaEnEdicion === null ? "/api/tareas" : `/api/tareas/${tareaEnEdicion}`, {
      method: tareaEnEdicion === null ? "POST" : "PUT", body: JSON.stringify(cuerpo),
    });
    cancelarEdicion("tarea");
    await recargarTodo();
  } catch (error) { mostrarError(porId("errores-tarea"), error); }
  finally { boton.disabled = false; }
});

for (const tipo of ["materia", "tarea"]) {
  porId(`cancelar-${tipo}`).addEventListener("click", () => cancelarEdicion(tipo));
}
for (const selector of [filtroMateria, filtroEstado]) {
  selector.addEventListener("change", async () => {
    limpiarErrores(erroresListado);
    try { await cargarTareas(); }
    catch (error) { mostrarError(erroresListado, error); }
  });
}

async function iniciar() {
  try {
    const colores = await pedir("/api/colores");
    porId("materia-color").replaceChildren(...colores.map((color) => new Option(color.nombre, color.codigo)));
    await recargarTodo();
  } catch (error) { mostrarError(erroresListado, error); }
}

iniciar();
