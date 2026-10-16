// Piezas de UI reutilizadas por las vistas.
import { IC } from "./icons.js";
import { campoFecha } from "./calendario.js";
import { $, esc, avance, infoEstatus, ESTATUS, OPCIONES_DURACION, etiquetaDuracion, ajustarDuracion } from "./utils.js";

export const pill = r => {
  const i = infoEstatus(r);
  return `<span class="pill s-${i.cls}">${i.txt}</span>`;
};
export const asegurada = r => !!r.aseguradora && r.aseguradora.trim().toLowerCase() !== "no";
export const seg = r => asegurada(r)
  ? `<span class="seg seg-si">${esc(r.aseguradora)}</span>`
  : `<span class="seg seg-no">Sin aseguradora</span>`;
export const barra = r => r.estatus === "EN PROGRESO"
  ? `<div class="bar" role="progressbar" aria-valuenow="${avance(r)}" aria-valuemin="0" aria-valuemax="100"><i style="width:${avance(r)}%"></i></div>`
  : "";
export const kpi = (n, t) => `<div class="card kpi"><b>${n}</b><span>${t}</span></div>`;
export const vacio = msg => `<div class="empty">${msg}</div>`;

export const leyenda = () => `<div class="legend">
  <span><b style="background:var(--green)"></b>En progreso</span><span><b style="background:var(--blue)"></b>En espera</span>
  <span><b style="background:var(--gray)"></b>Finalizada</span><span><b style="background:var(--violet)"></b>Con aseguradora</span>
  <span><b style="background:var(--amber)"></b>Sin aseguradora (No)</span></div>`;

export const pager = etiqueta => `<div class="pager" role="group" aria-label="Paginación">
  <button class="btn sm ic" data-a="pag" data-d="-1" aria-label="Anterior">${IC.izq}</button>
  <span class="pager-t" aria-live="polite">${etiqueta}</span>
  <button class="btn sm ic" data-a="pag" data-d="1" aria-label="Siguiente">${IC.der}</button>
  <button class="btn sm" data-a="pag-hoy">Hoy</button></div>`;

/** Botones PDF/XLSX. `datos` son los data-* que leerá la acción "dl" (id, o desde/hasta). */
export const botonesDescarga = (datos, prefijo = "", etiquetaAria = "") => ["pdf", "xlsx"].map(f =>
  `<button class="btn sm" data-a="dl" data-f="${f}" ${Object.entries(datos).map(([k, v]) => `data-${k}="${v}"`).join(" ")}
   aria-label="Descargar ${f.toUpperCase()} ${esc(etiquetaAria)}">${IC.dl}${prefijo}${f.toUpperCase()}</button>`).join("");

/* ---------- Formulario de cirugía (alta y edición) ---------- */
const QUIROFANOS = ["Quirófano 1", "Quirófano 2", "Quirófano 3"];
const CIRUJANOS = ["Dr. Roberto Gómez", "Dra. Sofía Martínez", "Dr. Alejandro Ruiz", "Dra. Elena Navarro"]; // luego: catálogo del backend
const OBLIGATORIOS = [
  ["nombrePaciente", "el nombre del paciente"], ["codigoPaciente", "el código del paciente"],
  ["procedimiento", "el procedimiento"], ["cirujano", "el cirujano"], ["fechaCirugia", "la fecha y hora"],
];

const opciones = (lista, actual) => lista.map(x => `<option ${x === actual ? "selected" : ""}>${x}</option>`).join("");

function fechaPorDefecto() {
  const d = new Date();
  d.setMinutes(0, 0, 0);
  d.setHours(d.getHours() + 1);
  const p = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:00`;
}

/** `edicion` agrega el campo Estatus; en el alta no existe (siempre nace "En espera"). */
export function formulario(p, r = {}, { edicion = false, columna = false } = {}) {
  const minutos = ajustarDuracion(r.duracionEstimada);
  const duraciones = OPCIONES_DURACION
    .map(m => `<option value="${m}" ${m === minutos ? "selected" : ""}>${etiquetaDuracion(m)}</option>`).join("");
  const campo = (id, etiqueta, control, para = `${p}${id}`) => `<div class="f"><label for="${para}">${etiqueta}</label>${control}</div>`;
  return `<div class="fg ${columna ? "c1" : ""}">
    ${campo("n", "Nombre del paciente", `<input id="${p}n" value="${esc(r.nombrePaciente)}" autocomplete="off">`)}
    ${campo("c", "Código del paciente", `<input id="${p}c" value="${esc(r.codigoPaciente)}" autocomplete="off">`)}
    ${campo("p", "Procedimiento", `<input id="${p}p" value="${esc(r.procedimiento)}">`)}
    ${campo("ci", "Cirujano", `<input id="${p}ci" list="lista-cirujanos" value="${esc(r.cirujano)}">`)}
    ${campo("q", "Quirófano", `<select id="${p}q">${opciones(QUIROFANOS, r.quirofano)}</select>`)}
    ${campo("f", "Fecha y hora", campoFecha(`${p}f`, (r.fechaCirugia || fechaPorDefecto()).slice(0, 16)), `${p}fb`)}
    ${campo("d", "Duración estimada", `<select id="${p}d">${duraciones}</select>`)}
    ${edicion ? campo("e", "Estatus", `<select id="${p}e">${Object.entries(ESTATUS).map(([v, i]) =>
      `<option value="${v}" ${v === r.estatus ? "selected" : ""}>${i.txt}</option>`).join("")}</select>`) : ""}
    ${campo("a", "Aseguradora (No si no tiene)", `<input id="${p}a" value="${esc(r.aseguradora ?? "No")}">`)}
  </div><datalist id="lista-cirujanos">${CIRUJANOS.map(c => `<option value="${c}">`).join("")}</datalist>`;
}

/** Lee el formulario `p`. Devuelve { datos, error }; `error` es un mensaje en español o null. */
export function leerFormulario(p, edicion) {
  const v = id => $(p + id).value.trim();
  const datos = {
    nombrePaciente: v("n"), codigoPaciente: v("c"), procedimiento: v("p"), cirujano: v("ci"),
    quirofano: v("q"), fechaCirugia: v("f"), duracionEstimada: Number(v("d")), aseguradora: v("a") || "No",
  };
  if (edicion) datos.estatus = v("e");
  const falta = OBLIGATORIOS.find(([k]) => !datos[k]);
  return { datos, error: falta ? `Falta ${falta[1]}` : null };
}
