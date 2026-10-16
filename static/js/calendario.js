// Selector de fecha y hora propio. Reemplaza al <input type="datetime-local">, cuyo calendario lo dibuja
// el navegador y no se puede estilizar. El valor vive en un <input hidden> con el mismo formato
// ("YYYY-MM-DDTHH:MM"), así que leerFormulario() y el backend no cambian.
import { $, pad, ymd } from "./utils.js";
import { IC } from "./icons.js";

const SEMANA = ["L", "M", "X", "J", "V", "S", "D"]; // la semana empieza en lunes
const capitalizar = t => t.charAt(0).toUpperCase() + t.slice(1);

const etiqueta = valor => {
  const f = new Date(valor);
  if (!valor || isNaN(f)) return "Elegir fecha y hora";
  const dia = f.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short", year: "numeric" });
  return `${dia}, ${pad(f.getHours())}:${pad(f.getMinutes())}`;
};

/** Campo para el formulario: botón visible + input oculto con el valor. `id` es el del input oculto. */
export const campoFecha = (id, valor) => `<div class="dt"><input type="hidden" id="${id}" value="${valor}">
  <button type="button" class="dt-btn" id="${id}b" data-para="${id}" aria-haspopup="dialog" aria-expanded="false">
  <span>${etiqueta(valor)}</span>${IC.cal}</button></div>`;

let panel = null;  // panel flotante abierto
let ancla = null;  // botón que lo abrió
let vista = null;  // mes que se está mostrando { anio, mes }

const valor = () => new Date($(ancla.dataset.para).value);

function fijar(fecha) {
  const v = `${ymd(fecha)}T${pad(fecha.getHours())}:${pad(fecha.getMinutes())}`;
  $(ancla.dataset.para).value = v;
  ancla.querySelector("span").textContent = etiqueta(v);
}

function pintar() {
  const elegido = valor();
  const desfase = (new Date(vista.anio, vista.mes, 1).getDay() + 6) % 7;
  const hoy = ymd(new Date()), sel = ymd(elegido);
  // 42 celdas fijas (6 semanas): el panel mide siempre lo mismo
  const dias = Array.from({ length: 42 }, (_, i) => {
    const d = new Date(vista.anio, vista.mes, 1 - desfase + i), s = ymd(d);
    const clases = ["dt-d", d.getMonth() !== vista.mes && "fuera", s === hoy && "hoy", s === sel && "sel"].filter(Boolean).join(" ");
    return `<button type="button" class="${clases}" data-dia="${s}" aria-pressed="${s === sel}">${d.getDate()}</button>`;
  }).join("");
  const horas = Array.from({ length: 24 }, (_, h) => `<option ${h === elegido.getHours() ? "selected" : ""}>${pad(h)}</option>`).join("");
  const minutos = [...new Set([...Array.from({ length: 12 }, (_, i) => i * 5), elegido.getMinutes()])].sort((a, b) => a - b)
    .map(m => `<option ${m === elegido.getMinutes() ? "selected" : ""}>${pad(m)}</option>`).join("");
  const titulo = capitalizar(new Date(vista.anio, vista.mes, 1).toLocaleDateString("es-MX", { month: "long", year: "numeric" }));
  panel.innerHTML = `<div class="dt-cab"><button type="button" class="btn sm ic" data-nav="-1" aria-label="Mes anterior">${IC.izq}</button>
    <b aria-live="polite">${titulo}</b><button type="button" class="btn sm ic" data-nav="1" aria-label="Mes siguiente">${IC.der}</button></div>
    <div class="dt-sem">${SEMANA.map(d => `<span>${d}</span>`).join("")}</div><div class="dt-grid">${dias}</div>
    <div class="dt-hora"><label>Hora <select data-h aria-label="Hora">${horas}</select></label><b>:</b>
    <label>Min <select data-m aria-label="Minutos">${minutos}</select></label></div>
    <div class="dt-pie"><button type="button" class="btn sm" data-hoy>Hoy</button><button type="button" class="btn pri sm" data-ok>Listo</button></div>`;
}

/** El panel siempre se abre hacia arriba del campo (hacia abajo se cortaba con el scroll). */
function posicionar() {
  const r = ancla.getBoundingClientRect();
  panel.style.maxHeight = `${innerHeight - 16}px`; // en pantallas muy bajas el panel hace scroll en vez de salirse
  const alto = panel.offsetHeight, ancho = panel.offsetWidth;
  panel.style.top = `${Math.max(8, r.top - alto - 6)}px`;
  panel.style.left = `${Math.min(Math.max(8, r.left), innerWidth - ancho - 8)}px`;
}

function abrir(boton) {
  const mismo = ancla === boton;
  cerrar();
  if (mismo) return;
  ancla = boton;
  const f = valor();
  vista = { anio: f.getFullYear(), mes: f.getMonth() };
  panel = document.createElement("div");
  panel.className = "dt-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Elegir fecha y hora");
  document.body.append(panel);
  pintar();
  posicionar();
  ancla.setAttribute("aria-expanded", "true");
}

export function cerrarCalendario() {
  panel?.remove();
  ancla?.setAttribute("aria-expanded", "false");
  panel = ancla = vista = null;
}
const cerrar = cerrarCalendario;

const moverMes = delta => { const d = new Date(vista.anio, vista.mes + delta, 1); vista = { anio: d.getFullYear(), mes: d.getMonth() }; };

export function iniciarCalendario() {
  document.addEventListener("click", e => {
    const boton = e.target.closest(".dt-btn");
    if (boton) return abrir(boton);
    if (!panel) return;
    if (!e.target.closest(".dt-panel")) return cerrar();
    const t = e.target.closest("button");
    if (!t) return;
    const f = valor();
    if (t.dataset.dia) {
      const [a, m, d] = t.dataset.dia.split("-").map(Number);
      f.setFullYear(a, m - 1, d);
      fijar(f);
      vista = { anio: a, mes: m - 1 };
    } else if (t.dataset.nav) moverMes(Number(t.dataset.nav));
    else if ("hoy" in t.dataset) {
      const n = new Date();
      f.setFullYear(n.getFullYear(), n.getMonth(), n.getDate());
      fijar(f);
      vista = { anio: n.getFullYear(), mes: n.getMonth() };
    } else if ("ok" in t.dataset) { const b = ancla; cerrar(); return b.focus(); }
    pintar();
  });
  document.addEventListener("change", e => {
    if (!panel || !e.target.closest(".dt-panel")) return;
    const f = valor();
    f.setHours(Number(panel.querySelector("[data-h]").value), Number(panel.querySelector("[data-m]").value));
    fijar(f);
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && panel) { const b = ancla; cerrar(); b.focus(); } });
  addEventListener("scroll", () => panel && posicionar(), true);
  addEventListener("resize", () => panel && cerrar());
}
