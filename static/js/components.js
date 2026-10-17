// Piezas de UI reutilizadas por las vistas.
import { IC } from "./icons.js";
import { campoFecha } from "./calendario.js";
import { $, esc, avance, infoEstatus, ESTATUS, SEXO, EDAD_MAX, OPCIONES_DURACION, etiquetaDuracion, ajustarDuracion } from "./utils.js";

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
/** "45 años · Femenino": la línea secundaria debajo del nombre del paciente. */
export const datosPaciente = r => `${r.edad} año${r.edad === 1 ? "" : "s"} · ${SEXO[r.sexo] ?? esc(r.sexo)}`;
/** Diagnóstico y servicios especiales; solo los que tengan texto. */
export const notasClinicas = r => [["Diagnóstico", r.diagnostico], ["Servicios especiales", r.serviciosEspeciales]]
  .filter(([, texto]) => texto)
  .map(([etiqueta, texto]) => `<div class="nota"><div class="lbl">${etiqueta}</div><div>${esc(texto)}</div></div>`).join("");
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
  ["nombrePaciente", "el nombre del paciente"], ["edad", "la edad"], ["sexo", "el sexo"],
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
  const campo = (id, etiqueta, control, para = `${p}${id}`, clase = "") => `<div class="f ${clase}"><label for="${para}">${etiqueta}</label>${control}</div>`;
  const sexos = `<option value="">Seleccionar</option>` + Object.entries(SEXO)
    .map(([v, txt]) => `<option value="${v}" ${v === r.sexo ? "selected" : ""}>${txt}</option>`).join("");
  return `<div class="fg ${columna ? "c1" : ""}">
    ${campo("n", "Nombre del paciente", `<input id="${p}n" value="${esc(r.nombrePaciente)}" autocomplete="off">`)}
    ${campo("ed", "Edad", `<input id="${p}ed" type="number" min="0" max="${EDAD_MAX}" step="1" inputmode="numeric" value="${r.edad ?? ""}">`)}
    ${campo("sx", "Sexo", `<select id="${p}sx">${sexos}</select>`)}
    ${campo("p", "Procedimiento", `<input id="${p}p" value="${esc(r.procedimiento)}">`)}
    ${campo("ci", "Cirujano", `<input id="${p}ci" list="lista-cirujanos" value="${esc(r.cirujano)}">`)}
    ${campo("q", "Quirófano", `<select id="${p}q">${opciones(QUIROFANOS, r.quirofano)}</select>`)}
    ${campo("f", "Fecha y hora", campoFecha(`${p}f`, (r.fechaCirugia || fechaPorDefecto()).slice(0, 16)), `${p}fb`)}
    ${campo("d", "Duración estimada", `<select id="${p}d">${duraciones}</select>`)}
    ${edicion ? campo("e", "Estatus", `<select id="${p}e">${Object.entries(ESTATUS).map(([v, i]) =>
      `<option value="${v}" ${v === r.estatus ? "selected" : ""}>${i.txt}</option>`).join("")}</select>`) : ""}
    ${campo("a", "Aseguradora (No si no tiene)", `<input id="${p}a" value="${esc(r.aseguradora ?? "No")}">`)}
    ${campo("dx", "Diagnóstico", `<textarea id="${p}dx" rows="3">${esc(r.diagnostico)}</textarea>`, undefined, "ancho")}
    ${campo("se", "Servicios especiales", `<textarea id="${p}se" rows="3">${esc(r.serviciosEspeciales)}</textarea>`, undefined, "ancho")}
  </div><datalist id="lista-cirujanos">${CIRUJANOS.map(c => `<option value="${c}">`).join("")}</datalist>`;
}

/** Lee el formulario `p`. Devuelve { datos, error }; `error` es un mensaje en español o null. */
export function leerFormulario(p, edicion) {
  const v = id => $(p + id).value.trim();
  const edad = v("ed");
  const datos = {
    nombrePaciente: v("n"), edad: edad === "" ? null : Number(edad), sexo: v("sx"),
    procedimiento: v("p"), cirujano: v("ci"), quirofano: v("q"), fechaCirugia: v("f"),
    duracionEstimada: Number(v("d")), aseguradora: v("a") || "No",
    diagnostico: v("dx") || null, serviciosEspeciales: v("se") || null,
  };
  if (edicion) datos.estatus = v("e");
  const falta = OBLIGATORIOS.find(([k]) => datos[k] == null || datos[k] === ""); // edad 0 es válida
  if (falta) return { datos, error: `Falta ${falta[1]}` };
  if (!Number.isInteger(datos.edad) || datos.edad < 0 || datos.edad > EDAD_MAX) {
    return { datos, error: `La edad debe ser un número entero entre 0 y ${EDAD_MAX}` };
  }
  return { datos, error: null };
}
