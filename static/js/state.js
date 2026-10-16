import { hoy, lunesDe } from "./utils.js";

const CLAVE = "hm.preferencias";

/** Estado compartido de la app. `null` en diaDash/semana significa "el actual". */
export const estado = {
  pagina: "dash",
  tema: "blanco",
  modos: { reg: 1, dash: 1, adm: 1 },
  datos: [],
  abierto: null,   // id del registro expandido para editar
  panel: false,    // panel lateral de alta (Registro, Mode 3)
  diaDash: null,   // día mostrado en Dashboard
  semana: null,    // lunes de la semana mostrada en Registro y Administración
};

export const diaDash = () => estado.diaDash ?? hoy();
export const lunes = () => estado.semana ?? lunesDe(hoy());

export function restaurar() {
  try {
    const g = JSON.parse(localStorage.getItem(CLAVE) || "{}");
    if (g.tema) estado.tema = g.tema;
    if (g.modos) Object.assign(estado.modos, g.modos);
  } catch { /* localStorage no disponible: se usan los valores por defecto */ }
}

export function persistir() {
  try { localStorage.setItem(CLAVE, JSON.stringify({ tema: estado.tema, modos: estado.modos })); } catch { /* ignorar */ }
}
