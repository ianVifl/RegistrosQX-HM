// Utilidades puras: fechas, formato y constantes de dominio. Sin dependencias del DOM (salvo $).

export const $ = id => document.getElementById(id);
export const pad = n => String(n).padStart(2, "0");

// Todo texto que viene de la BD se escapa antes de entrar a un innerHTML.
const HTML = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const esc = s => String(s ?? "").replace(/[&<>"']/g, c => HTML[c]);

/* ---------- Fechas (YYYY-MM-DD en hora local) ---------- */
export const ymd = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
export const hoy = () => ymd(new Date());
const aFecha = s => new Date(`${s}T00:00:00`);
export const sumarDias = (s, n) => { const d = aFecha(s); d.setDate(d.getDate() + n); return ymd(d); };
/** Lunes de la semana de `s`. La semana va de lunes a domingo. */
export const lunesDe = s => { const d = aFecha(s); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); return ymd(d); };

const capitalizar = t => t.charAt(0).toUpperCase() + t.slice(1);
export const nombreDia = s =>
  capitalizar(aFecha(s).toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" }));
export const rangoSemana = lunes => {
  const fmt = (s, anio) => aFecha(s).toLocaleDateString("es-MX", { day: "numeric", month: "short", ...(anio && { year: "numeric" }) });
  return `${fmt(lunes)} al ${fmt(sumarDias(lunes, 6), true)}`;
};
export const hm = d => `${pad(d.getHours())}:${pad(d.getMinutes())}`;

/* ---------- Cirugías ---------- */
export const inicio = r => new Date(r.fechaCirugia);
export const fin = r => new Date(inicio(r).getTime() + r.duracionEstimada * 60000);
export const porHora = (a, b) => inicio(a) - inicio(b);
export const diaDe = r => r.fechaCirugia.slice(0, 10);
export const avance = r => {
  const p = Math.round(((Date.now() - inicio(r)) / (r.duracionEstimada * 60000)) * 100);
  return Math.max(3, Math.min(100, p));
};

/** Agrupa por día (YYYY-MM-DD) con las cirugías de cada día ordenadas por hora: [[dia, [cirugías]], ...]. */
export function agruparPorDia(lista) {
  const grupos = new Map();
  for (const r of [...lista].sort(porHora)) {
    const d = diaDe(r);
    if (!grupos.has(d)) grupos.set(d, []);
    grupos.get(d).push(r);
  }
  return [...grupos];
}

export const ESTATUS = {
  PROGRAMADA: { cls: "esp", txt: "En espera" },
  "EN PROGRESO": { cls: "prog", txt: "En progreso" },
  FINALIZADA: { cls: "fin", txt: "Finalizada" },
};
export const infoEstatus = r => ESTATUS[r.estatus] ?? ESTATUS.PROGRAMADA;

export const SEXO = { FEMENINO: "Femenino", MASCULINO: "Masculino" };
export const EDAD_MAX = 120;

/* ---------- Duración: la BD guarda minutos, el usuario ve horas ---------- */
export const OPCIONES_DURACION = Array.from({ length: 24 }, (_, i) => (i + 1) * 30); // 30 min a 12 h
export const etiquetaDuracion = m => {
  const h = Math.floor(m / 60);
  if (m === 30) return "Media hora";
  const horas = `${h} ${h === 1 ? "hora" : "horas"}`;
  return m % 60 === 30 ? `${horas} y media` : horas;
};
export const durCorta = m => [m >= 60 && `${Math.floor(m / 60)} h`, m % 60 && `${m % 60} min`].filter(Boolean).join(" ");
/** Ajusta a la opción de media hora más cercana hacia arriba (por si hay filas viejas de 75 min). */
export const ajustarDuracion = m => Math.min(720, Math.max(30, Math.ceil((m || 60) / 30) * 30));
