// Orquesta el render y la carga de datos. Las vistas son funciones puras del estado.
import { estado, persistir, diaDash, lunes } from "./state.js";
import { API } from "./api.js";
import { IC } from "./icons.js";
import { $, sumarDias } from "./utils.js";
import { toast } from "./ui.js";
import { cerrarCalendario } from "./calendario.js";
import { dashboard } from "./views/dashboard.js";
import { registro, panelNuevo } from "./views/registro.js";
import { admin } from "./views/admin.js";

const VISTAS = { reg: registro, dash: dashboard, adm: admin };
export const TEMAS = [["dark", "Dark theme"], ["blanco", "Blanco"], ["menta", "Menta"]];

/** Rango que necesita la página actual: un día (Dashboard) o la semana lun-dom (Registro y Administración). */
export function rangoActual() {
  if (estado.pagina === "dash") return [diaDash(), diaDash()];
  return [lunes(), sumarDias(lunes(), 6)];
}

/** Cambio de pantalla con transición suave (View Transitions API); sin soporte, un fundido por CSS. */
export function transicion(cambio) {
  if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return cambio();
  if (document.startViewTransition) return document.startViewTransition(cambio);
  cambio();
  const v = $("view");
  v.classList.remove("entra");
  void v.offsetWidth; // fuerza el reflujo para reiniciar la animación
  v.classList.add("entra");
}

/** Carga los datos de la página actual. `animar` es para navegación del usuario; los refrescos automáticos no animan. */
export async function cargar({ animar = false } = {}) {
  try {
    estado.datos = await API.listar(...rangoActual());
  } catch (e) {
    toast(e.message, true);
  }
  if (animar) transicion(render); else render();
}

/** Hay un formulario a medias en Registro: no se recarga sola la pantalla para no borrarlo. */
const editando = () => estado.abierto !== null || ["nn", "nc", "np"].some(id => $(id)?.value);
export function refrescar() {
  if (estado.pagina === "reg" && editando()) return;
  cargar();
}

const etiquetar = (el, html, texto) => { el.innerHTML = html; el.title = texto; el.setAttribute("aria-label", texto); };

export function render() {
  cerrarCalendario(); // el panel flotante quedaría huérfano si el formulario se vuelve a pintar
  persistir();
  const { pagina, modos, tema } = estado;
  const modo = modos[pagina];
  document.documentElement.dataset.theme = tema;
  document.querySelectorAll(".nav a").forEach(a => a.toggleAttribute("aria-current", a.dataset.p === pagina));
  etiquetar($("bTema"), IC.tema, `Tema: ${TEMAS.find(t => t[0] === tema)[1]} (clic para cambiar)`);
  etiquetar($("bModo"), `${IC.vista}<span class="bd">${modo}</span>`, `Vista: Mode ${modo} (clic para cambiar)`);
  // Pantalla completa: solo en el Dashboard. Si se sale de ahí con la pantalla completa activa, se cierra.
  $("fs").hidden = pagina !== "dash";
  if (pagina !== "dash" && document.fullscreenElement) document.exitFullscreen().catch(() => {});
  $("view").innerHTML = VISTAS[pagina].barra() + VISTAS[pagina].modos[modo]();

  // Panel lateral de alta: solo en Registro/Mode 3. No se reescribe si ya existe, para no borrar lo tecleado.
  const slide = $("slide");
  const activo = pagina === "reg" && modo === 3;
  if (!activo) slide.innerHTML = "";
  else if (!slide.firstChild) slide.innerHTML = panelNuevo();
  slide.classList.toggle("open", activo && estado.panel);
}
