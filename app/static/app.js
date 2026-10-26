// Lógica del frontend: llamadas a /api y renderizado del listado.
// Todo el contenido del usuario se escribe con textContent para evitar inyección de HTML.

const elementos = {
  formMateria: document.getElementById("form-materia"),
  formTarea: document.getElementById("form-tarea"),
  colorMateria: document.getElementById("materia-color"),
  selectMateriaTarea: document.getElementById("tarea-materia"),
  listaMaterias: document.getElementById("lista-materias"),
  listaTareas: document.getElementById("lista-tareas"),
  erroresMateria: document.getElementById("errores-materia"),
  erroresTarea: document.getElementById("errores-tarea"),
  avisoSinMaterias: document.getElementById("aviso-sin-materias"),
  avisoSinTareas: document.getElementById("aviso-sin-tareas"),
};

const ETIQUETAS_MARCA = { vencida: "Vencida", urgente: "Urgente" };

async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(ruta, {
    headers: { "Content-Type": "application/json" },
    ...opciones,
  });
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json();
  if (!respuesta.ok) {
    const error = new Error("Error de validación");
    error.errores = datos.errores ?? [{ campo: null, mensaje: "Ocurrió un error inesperado." }];
    throw error;
  }
  return datos;
}

function mostrarErrores(lista, errores) {
  lista.replaceChildren(
    ...errores.map((error) => {
      const item = document.createElement("li");
      item.textContent = error.campo ? `${error.campo}: ${error.mensaje}` : error.mensaje;
      return item;
    })
  );
}

function limpiarErrores(lista) {
  lista.replaceChildren();
}

function formatearEntrega(fechaEntrega) {
  const [fecha, hora] = fechaEntrega.split("T");
  const [anio, mes, dia] = fecha.split("-");
  return `${dia}/${mes}/${anio} ${hora}`;
}

async function cargarColores() {
  const colores = await pedir("/api/colores");
  elementos.colorMateria.replaceChildren(
    ...colores.map((color) => new Option(color.nombre, color.codigo))
  );
}

async function cargarMaterias() {
  const materias = await pedir("/api/materias");

  elementos.listaMaterias.replaceChildren(
    ...materias.map((materia) => {
      const item = document.createElement("li");
      const muestra = document.createElement("span");
      muestra.className = "muestra-color";
      muestra.style.backgroundColor = materia.color;
      muestra.setAttribute("aria-hidden", "true");
      item.append(muestra, `${materia.nombre} (${materia.total_tareas} tareas)`);
      return item;
    })
  );

  elementos.selectMateriaTarea.replaceChildren(
    ...materias.map((materia) => new Option(materia.nombre, materia.id))
  );

  const sinMaterias = materias.length === 0;
  elementos.avisoSinMaterias.hidden = !sinMaterias;
  elementos.formTarea.hidden = sinMaterias;
}

async function cargarTareas() {
  const tareas = await pedir("/api/tareas");

  elementos.avisoSinTareas.hidden = tareas.length > 0;
  elementos.listaTareas.replaceChildren(
    ...tareas.map((tarea) => {
      const item = document.createElement("li");
      item.className = "tarea";

      const titulo = document.createElement("strong");
      titulo.textContent = tarea.titulo;

      const materia = document.createElement("span");
      materia.className = "materia";
      const muestra = document.createElement("span");
      muestra.className = "muestra-color";
      muestra.style.backgroundColor = tarea.materia.color;
      muestra.setAttribute("aria-hidden", "true");
      materia.append(muestra, tarea.materia.nombre);

      const entrega = document.createElement("time");
      entrega.dateTime = tarea.fecha_entrega;
      entrega.textContent = `Entrega: ${formatearEntrega(tarea.fecha_entrega)}`;

      item.append(titulo, materia, entrega);
      // La marca se muestra con texto además del color (FR-020).
      if (tarea.marca) {
        item.classList.add(`tarea-${tarea.marca}`);
        const marca = document.createElement("span");
        marca.className = `marca marca-${tarea.marca}`;
        marca.textContent = ETIQUETAS_MARCA[tarea.marca];
        titulo.append(" ", marca);
      }
      if (tarea.descripcion) {
        const descripcion = document.createElement("p");
        descripcion.textContent = tarea.descripcion;
        item.append(descripcion);
      }
      return item;
    })
  );
}

async function recargarTodo() {
  await Promise.all([cargarMaterias(), cargarTareas()]);
}

elementos.formMateria.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limpiarErrores(elementos.erroresMateria);
  const datos = new FormData(elementos.formMateria);
  try {
    await pedir("/api/materias", {
      method: "POST",
      body: JSON.stringify({ nombre: datos.get("nombre"), color: datos.get("color") }),
    });
    elementos.formMateria.reset();
    await recargarTodo();
  } catch (error) {
    mostrarErrores(elementos.erroresMateria, error.errores ?? [{ campo: null, mensaje: error.message }]);
  }
});

elementos.formTarea.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limpiarErrores(elementos.erroresTarea);
  const datos = new FormData(elementos.formTarea);

  const cuerpo = {
    materia_id: Number(datos.get("materia_id")),
    titulo: datos.get("titulo"),
    fecha: datos.get("fecha"),
  };
  const descripcion = datos.get("descripcion");
  if (descripcion) cuerpo.descripcion = descripcion;
  // Si no se indica hora, se omite para que el servidor use 23:59 (FR-009).
  const hora = datos.get("hora");
  if (hora) cuerpo.hora = hora;

  try {
    await pedir("/api/tareas", { method: "POST", body: JSON.stringify(cuerpo) });
    elementos.formTarea.reset();
    await recargarTodo();
  } catch (error) {
    mostrarErrores(elementos.erroresTarea, error.errores ?? [{ campo: null, mensaje: error.message }]);
  }
});

async function iniciar() {
  await cargarColores();
  await recargarTodo();
}

iniciar();
