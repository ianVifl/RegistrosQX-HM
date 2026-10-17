import { estado, lunes } from "../state.js";
import { esc, hm, inicio, agruparPorDia, nombreDia, rangoSemana, sumarDias, ESTATUS } from "../utils.js";
import { pill, seg, asegurada, kpi, vacio, leyenda, pager, botonesDescarga, datosPaciente } from "../components.js";

const SIN_DATOS = vacio("No hay cirugías en esta semana.");
const semana = () => ({ desde: lunes(), hasta: sumarDias(lunes(), 6) });

/* ---------- Estadísticas de la semana (se calculan con la lista ya cargada) ---------- */
const conteo = campo => estado.datos.reduce((m, r) => ({ ...m, [r[campo]]: (m[r[campo]] || 0) + 1 }), {});
const promedio = () => Math.round(estado.datos.reduce((s, r) => s + r.duracionEstimada, 0) / (estado.datos.length || 1));
const kpis = () => `<div class="kpis">${kpi(estado.datos.length, "cirugías en la semana")}${kpi(`${promedio()} min`, "duración promedio")}
  ${kpi(`${Math.round(estado.datos.filter(asegurada).length / (estado.datos.length || 1) * 100)}%`, "con aseguradora")}
  ${kpi(estado.datos.filter(r => r.estatus === "FINALIZADA").length, "finalizadas")}</div>`;
const barras = (mapa, color, nombre = k => k) => `<div class="bars">${Object.entries(mapa).map(([k, v]) =>
  `<div><span>${esc(nombre(k))}</span><span class="bar"><i style="width:${v / estado.datos.length * 100}%;background:${color}"></i></span><b>${v}</b></div>`).join("")}</div>`;
const graficas = () => `<div class="card panel"><h2>Por estatus</h2>${barras(conteo("estatus"), "var(--brand)", k => ESTATUS[k]?.txt ?? k)}</div>
  <div class="card panel"><h2>Por quirófano</h2>${barras(conteo("quirofano"), "var(--accent)")}</div>`;

/* ---------- Listado agrupado por día ---------- */
const conteoTxt = n => `${n} cirugía${n > 1 ? "s" : ""}`;
const filaTabla = r => `<div class="lr adm"><span class="t">${hm(inicio(r))}</span>
  <span><b>${esc(r.nombrePaciente)}</b><br><span class="mut">${datosPaciente(r)}</span></span><span>${esc(r.procedimiento)}</span>
  <span class="t-q">${esc(r.quirofano)}</span>${pill(r)}${seg(r)}
  <span style="display:flex;gap:6px">${botonesDescarga({ id: r.id }, "", r.nombrePaciente)}</span></div>`;

const tabla = () => !estado.datos.length ? SIN_DATOS : `<div class="lst">
  <div class="lh adm"><span>Hora</span><span>Paciente</span><span>Procedimiento</span><span>Sala</span><span>Estatus</span><span>Aseguradora</span><span>Descargar</span></div>
  ${agruparPorDia(estado.datos).map(([d, filas]) => `<div class="dia-h"><b>${nombreDia(d)}</b><span class="mut">${conteoTxt(filas.length)}</span>
    <span class="dia-dl">${botonesDescarga({ desde: d, hasta: d }, "", nombreDia(d))}</span></div>${filas.map(filaTabla).join("")}`).join("")}</div>`;

const tarjetas = () => !estado.datos.length ? SIN_DATOS : agruparPorDia(estado.datos).map(([d, filas]) => `<section class="dia-grupo">
  <div class="head-row"><h3>${nombreDia(d)} <span class="mut">(${conteoTxt(filas.length)})</span></h3><span class="dia-dl">${botonesDescarga({ desde: d, hasta: d }, "", nombreDia(d))}</span></div>
  <div class="cards3">${filas.map(r => `<article class="card cm c-${r.estatus === "EN PROGRESO" ? "prog" : r.estatus === "FINALIZADA" ? "fin" : "esp"}">
    <div class="r"><b>${hm(inicio(r))} ${esc(r.quirofano)}</b>${pill(r)}</div>
    <div><b>${esc(r.procedimiento)}</b><div class="mut">${esc(r.nombrePaciente)} (${datosPaciente(r)})</div></div>
    <div class="r">${seg(r)}<span style="display:flex;gap:6px">${botonesDescarga({ id: r.id }, "", r.nombrePaciente)}</span></div></article>`).join("")}</div></section>`).join("");

const encabezado = () => `<div class="head-row">${pager(`Semana del ${rangoSemana(lunes())}`)}
  <div class="acciones-semana">${botonesDescarga(semana(), "Semana ")}</div></div>`;

export const admin = {
  barra: leyenda,
  modos: {
    1: () => `${encabezado()}${kpis()}${tabla()}`,
    2: () => `<div class="side"><aside class="stk"><div class="card panel">${pager(`Semana del ${rangoSemana(lunes())}`)}
      <div class="acts" style="flex-direction:column">${botonesDescarga(semana(), "Semana ")}</div></div>${graficas()}</aside><section>${kpis()}${tabla()}</section></div>`,
    3: () => `${encabezado()}${kpis()}<div class="two" style="margin-bottom:8px">${graficas()}</div>${tarjetas()}`,
  },
};
