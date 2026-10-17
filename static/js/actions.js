
import { estado, diaDash, lunes } from "./state.js";
import { API } from "./api.js";
import { $, esc, sumarDias, lunesDe } from "./utils.js";
import { leerFormulario } from "./components.js";
import { toast, confirmar } from "./ui.js";
import { cargar, render } from "./app.js";

const buscar = id => estado.datos.find(r => r.id === id);

async function ejecutar(operacion, mensajeOk, alTerminar) {
  try {
    await operacion();
    alTerminar?.();
    await cargar();
    toast(mensajeOk);
  } catch (e) {
    toast(e.message, true);
  }
}

async function cargarBusqueda() {
  try {
    estado.busqueda.resultado = await API.buscar(estado.busqueda.q, estado.busqueda.pagina);
  } catch (e) {
    toast(e.message, true);
  }
  render();
}

const acciones = {
  // Alta: sin cuadro de confirmación, solo aviso de éxito.
  async nuevo() {
    const { datos, error } = leerFormulario("n", false);
    if (error) return toast(error, true);
    await ejecutar(() => API.crear(datos), "Cirugía registrada", () => {
      estado.panel = false;
      estado.semana = lunesDe(datos.fechaCirugia.slice(0, 10)); // se muestra la semana del nuevo registro
      $("slide").innerHTML = "";                    // se recrea limpio en el siguiente render
    });
  },
  limpiar() { $("slide").innerHTML = ""; render(); },
  slide() { estado.panel = !estado.panel; $("slide").classList.toggle("open", estado.panel); },
  exp(b) { const id = Number(b.dataset.id); estado.abierto = estado.abierto === id ? null : id; render(); },

  async guardar(b) {
    const id = Number(b.dataset.id);
    const { datos, error } = leerFormulario("x", true);
    if (error) return toast(error, true);
    const nombre = esc(buscar(id)?.nombrePaciente ?? "este registro");
    if (!await confirmar({ titulo: "Guardar cambios", mensaje: `Se actualizará el registro de <b>${nombre}</b>.`, boton: "Guardar" })) return;
    await ejecutar(() => API.modificar(id, datos), "Cambios guardados", () => { estado.abierto = null; });
  },
  async eliminar(b) {
    const id = Number(b.dataset.id);
    const nombre = esc(buscar(id)?.nombrePaciente ?? "este registro");
    if (!await confirmar({ titulo: "Eliminar registro", mensaje: `Se eliminará el registro de <b>${nombre}</b>. Esta acción no se puede deshacer.`, boton: "Eliminar", peligro: true })) return;
    await ejecutar(() => API.eliminar(id), "Registro eliminado", () => { estado.abierto = null; });
  },

  dl(b) { const { f, id, desde, hasta } = b.dataset; API.descargar(f, { id, desde, hasta }); },
  historico() {
    API.descargarHistorico();
    toast("Generando el histórico completo; con muchos registros puede tardar un poco");
  },

  // Paginación: Dashboard por día; Registro y Administración por semana (lunes a domingo).
  pag(b) {
    const d = Number(b.dataset.d);
    if (estado.pagina === "dash") estado.diaDash = sumarDias(diaDash(), d);
    else estado.semana = sumarDias(lunes(), 7 * d);
    cargar({ animar: true });
  },
  // Búsqueda en el historial (Administración)
  buscar() {
    const q = $("bq").value.trim();
    if (q.length < 2) return toast("Escribe al menos 2 letras para buscar", true);
    estado.busqueda = { q, pagina: 1, resultado: null };
    render();
    cargarBusqueda();
  },
  bpag(b) { estado.busqueda.pagina += Number(b.dataset.d); cargarBusqueda(); },
  bclear() { estado.busqueda = null; render(); },

  "pag-hoy"() {
    if (estado.pagina === "dash") estado.diaDash = null;
    else estado.semana = null;
    cargar({ animar: true });
  },
};

export function iniciarAcciones() {
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-a]");
    acciones[b?.dataset.a]?.(b);
  });
  // Formularios con data-f: Enter y el botón de enviar hacen lo mismo
  document.addEventListener("submit", e => {
    const f = e.target.closest("[data-f]");
    if (!f) return;
    e.preventDefault();
    acciones[f.dataset.f]?.(f);
  });
}
