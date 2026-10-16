import { estado, diaDash } from "../state.js";
import { esc, hm, inicio, fin, durCorta, nombreDia, porHora, infoEstatus } from "../utils.js";
import { pill, seg, barra, kpi, leyenda, pager, vacio } from "../components.js";

const MAX = 6;
const VISIBLES = ["PROGRAMADA", "EN PROGRESO"]; // las finalizadas no se muestran aquí
const SIN_CIRUGIAS = vacio("No hay cirugías en espera ni en progreso para este día.");

/** Pendientes del día en orden ascendente de hora; solo se pintan las primeras MAX. */
function pendientes() {
  const todas = estado.datos.filter(r => VISIBLES.includes(r.estatus)).sort(porHora);
  const enProgreso = todas.filter(r => r.estatus === "EN PROGRESO").length;
  return { lista: todas.slice(0, MAX), extra: Math.max(0, todas.length - MAX), total: todas.length, enProgreso };
}
const masIndicador = n => n ? `<div class="more" aria-live="polite">+${n} cirugía${n > 1 ? "s" : ""} más</div>` : "";

const tarjeta = r => `<article class="card cA c-${infoEstatus(r).cls}">
  <div class="top"><span class="t-q">${esc(r.quirofano)}</span>${pill(r)}</div>
  <div class="time">${hm(inicio(r))} <small>a ${hm(fin(r))} (${durCorta(r.duracionEstimada)})</small></div>${barra(r)}
  <div><div class="lbl">Procedimiento</div><div class="big">${esc(r.procedimiento)}</div></div>
  <div><div class="lbl">Paciente</div><b>${esc(r.nombrePaciente)}</b><div class="mut">${esc(r.codigoPaciente)}</div></div>
  <div class="foot"><div><div class="lbl">Cirujano</div><b>${esc(r.cirujano)}</b></div>${seg(r)}</div></article>`;

const fila = r => `<article class="card rB c-${infoEstatus(r).cls}">
  <div class="big">${hm(inicio(r))}<div class="lbl" style="font-weight:500">${durCorta(r.duracionEstimada)}</div></div>
  <div><b>${esc(r.nombrePaciente)}</b><div class="mut">${esc(r.codigoPaciente)}</div></div>
  <div style="font-weight:600">${esc(r.procedimiento)}${barra(r) && `<div style="margin-top:8px">${barra(r)}</div>`}</div>
  <div>${esc(r.cirujano)}</div><div class="t-q">${esc(r.quirofano)}</div>${seg(r)}${pill(r)}</article>`;

const enCurso = r => `<article class="card cC c-prog">
  <div class="head"><span class="t-q big">${esc(r.quirofano)}</span>${seg(r)}</div>
  <div><div class="lbl">Procedimiento</div><div class="big">${esc(r.procedimiento)}</div></div>
  <div class="two"><div><div class="lbl">Paciente</div><b>${esc(r.nombrePaciente)}</b><div class="mut">${esc(r.codigoPaciente)}</div></div>
  <div><div class="lbl">Cirujano</div><b>${esc(r.cirujano)}</b></div></div>
  <div>${barra(r)}<div class="pm"><span>Inicio ${hm(inicio(r))}</span><span>Salida estimada ${hm(fin(r))}</span></div></div></article>`;

const siguiente = r => `<div class="nx"><span class="h">${hm(inicio(r))}</span>
  <div><b>${esc(r.procedimiento)}</b><div class="mut">${esc(r.quirofano)}, ${esc(r.cirujano)}</div>
  <div class="mut">${esc(r.nombrePaciente)} (${esc(r.codigoPaciente)})</div></div>${seg(r)}</div>`;

export const dashboard = {
  barra: () => `<div class="toolbar">${leyenda()}${pager(nombreDia(diaDash()))}</div>`,
  modos: {
    1() {
      const { lista, extra } = pendientes();
      if (!lista.length) return SIN_CIRUGIAS;
      return `<div class="gA" style="--rows:${Math.ceil(lista.length / 3)}">${lista.map(tarjeta).join("")}</div>${masIndicador(extra)}`;
    },
    2() {
      const { lista, extra } = pendientes();
      if (!lista.length) return SIN_CIRUGIAS;
      return `<div class="rowsB"><div class="hB"><span>Hora</span><span>Paciente</span><span>Procedimiento</span><span>Cirujano</span><span>Sala</span><span>Aseguradora</span><span>Estatus</span></div>
        ${lista.map(fila).join("")}</div>${masIndicador(extra)}`;
    },
    3() {
      const { lista, extra, total, enProgreso } = pendientes();
      if (!lista.length) return SIN_CIRUGIAS;
      const ahora = lista.filter(r => r.estatus === "EN PROGRESO");
      const despues = lista.filter(r => r.estatus !== "EN PROGRESO");
      return `<div class="kpis" style="grid-template-columns:repeat(3,1fr)">${kpi(total, "cirugías pendientes")}${kpi(enProgreso, "en progreso")}${kpi(total - enProgreso, "en espera")}</div>
        <div class="splitC"><section><h2 class="colh"><span class="pill s-prog">En quirófano ahora</span></h2>
          <div class="stk">${ahora.length ? ahora.map(enCurso).join("") : vacio("Ninguna cirugía en curso.")}</div></section>
        <section><h2 class="colh"><span class="pill s-esp">Siguientes</span></h2>
          <div class="card" style="padding:6px 8px">${despues.map(siguiente).join("") || vacio("Sin cirugías siguientes.")}</div>${masIndicador(extra)}</section></div>`;
    },
  },
};
