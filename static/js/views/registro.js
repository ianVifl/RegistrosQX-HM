import { estado, lunes } from "../state.js";
import { IC } from "../icons.js";
import { esc, hm, inicio, agruparPorDia, nombreDia, rangoSemana } from "../utils.js";
import { pill, seg, vacio, formulario, pager } from "../components.js";

const paginador = () => pager(`Semana del ${rangoSemana(lunes())}`);
const cabecera = () => `<div class="head-row"><h2>Registros de la semana</h2>${paginador()}</div>`;

const formularioNuevo = columna => `${formulario("n", {}, { columna })}
  <div class="acts"><button class="btn pri" data-a="nuevo">Registrar cirugía</button><button class="btn" data-a="limpiar">Limpiar</button></div>`;

/** Contenido del panel lateral (solo Mode 3). */
export const panelNuevo = () => `<div class="head-row"><h2>Nueva cirugía</h2><button class="btn sm" data-a="slide">Cerrar</button></div>${formularioNuevo(true)}`;

const fila = r => {
  const abierta = estado.abierto === r.id;
  return `<div class="lr ${abierta ? "ex-open" : ""}"><span class="t">${hm(inicio(r))}</span>
    <span><b>${esc(r.nombrePaciente)}</b><br><span class="mut">${esc(r.codigoPaciente)}</span></span>
    <span>${esc(r.procedimiento)}</span><span class="t-q">${esc(r.quirofano)}</span>${pill(r)}${seg(r)}
    <button class="btn sm ic" data-a="exp" data-id="${r.id}" aria-expanded="${abierta}" aria-label="Expandir para editar">${IC.chev}</button></div>`
    + (abierta ? `<div class="ex">${formulario("x", r, { edicion: true })}
      <div class="acts"><button class="btn pri sm" data-a="guardar" data-id="${r.id}">Guardar cambios</button>
      <button class="btn sm" data-a="exp" data-id="${r.id}">Cancelar</button>
      <button class="btn sm dng" data-a="eliminar" data-id="${r.id}">Eliminar</button></div></div>` : "");
};

/** Registros de la semana agrupados por día, cada día con sus cirugías por hora. */
const lista = () => {
  if (!estado.datos.length) return vacio("No hay cirugías registradas esta semana.");
  return `<div class="lst"><div class="lh"><span>Hora</span><span>Paciente</span><span>Procedimiento</span><span>Sala</span><span>Estatus</span><span>Aseguradora</span><span></span></div>
    ${agruparPorDia(estado.datos).map(([dia, filas]) => `<div class="dia-h"><b>${nombreDia(dia)}</b>
      <span class="mut">${filas.length} cirugía${filas.length > 1 ? "s" : ""}</span></div>${filas.map(fila).join("")}`).join("")}</div>`;
};

export const registro = {
  barra: () => "",
  modos: {
    1: () => `<div class="lay1"><section class="card panel"><h2>Nueva cirugía</h2>${formularioNuevo(true)}</section><section>${cabecera()}${lista()}</section></div>`,
    2: () => `<section class="card panel" style="margin-bottom:20px"><h2>Nueva cirugía</h2>${formularioNuevo(false)}</section>${cabecera()}${lista()}`,
    3: () => `<div class="head-row"><h2>Registros de la semana</h2>${paginador()}<button class="btn pri" data-a="slide">${IC.plus}Nueva cirugía</button></div>${lista()}`,
  },
};
