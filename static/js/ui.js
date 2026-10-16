import { $, esc } from "./utils.js";

/* ---------- Avisos (toasts) ---------- */
const MAX_AVISOS = 4;
const DURACION_MS = { ok: 3500, error: 7000 }; // los errores se quedan más tiempo
const TITULOS = { ok: "¡Listo!", error: "No se pudo completar" };
const ICONOS = {
  ok: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle class="c" cx="12" cy="12" r="10"/><path class="m" d="m7.5 12.5 3 3 6-6.5"/></svg>',
  error: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle class="c" cx="12" cy="12" r="10"/><path class="m" d="M12 7.5v5.5M12 16.5v.01"/></svg>',
};
const CERRAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';

/** Muestra un aviso arriba al centro. `error = true` lo pinta en rojo y lo deja más tiempo. */
export function toast(mensaje, error = false) {
  const tipo = error ? "error" : "ok";
  const contenedor = $("toasts");
  while (contenedor.children.length >= MAX_AVISOS) contenedor.firstElementChild.remove();

  const el = document.createElement("div");
  el.className = `toast ${tipo}`;
  el.setAttribute("role", error ? "alert" : "status");
  el.innerHTML = `<span class="t-ic">${ICONOS[tipo]}</span>
    <div class="t-tx"><b>${TITULOS[tipo]}</b><span>${esc(mensaje)}</span></div>
    <button class="t-x" aria-label="Cerrar aviso">${CERRAR}</button>
    <i class="t-bar" style="animation-duration:${DURACION_MS[tipo]}ms"></i>`;

  const cerrar = () => {
    if (el.classList.contains("saliendo")) return;
    el.classList.add("saliendo");
    el.addEventListener("animationend", e => { if (e.target === el) el.remove(); });
    setTimeout(() => el.remove(), 400); // respaldo si el usuario desactivó las animaciones
  };
  el.querySelector(".t-x").onclick = cerrar;
  // La barra de progreso es el temporizador: al terminar cierra el aviso, y se pausa con el cursor encima.
  el.querySelector(".t-bar").addEventListener("animationend", cerrar);
  contenedor.append(el);
}

/* ---------- Confirmación modal ---------- */
const ICONOS_DLG = {
  editar: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
  peligro: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/></svg>',
};

/** Cuadro de confirmación. Resuelve true si el usuario confirma. `mensaje` admite HTML ya escapado. */
export function confirmar({ titulo, mensaje, boton = "Confirmar", peligro = false }) {
  const d = $("confirmar");
  d.innerHTML = `<form method="dialog" class="dlg ${peligro ? "peligro" : ""}">
    <span class="dlg-ic">${ICONOS_DLG[peligro ? "peligro" : "editar"]}</span>
    <h2>${esc(titulo)}</h2><p>${mensaje}</p>
    <div class="acts"><button class="btn" value="no">Cancelar</button>
    <button class="btn ${peligro ? "fill-dng" : "pri"}" value="si" autofocus>${esc(boton)}</button></div></form>`;
  return new Promise(resolver => {
    d.onclose = () => resolver(d.returnValue === "si"); // Esc cierra con returnValue vacío
    d.showModal();
  });
}
