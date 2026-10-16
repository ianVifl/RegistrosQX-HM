// Única capa que habla con el backend. Si el front se sirve desde otro origen,
// define antes window.API_BASE = "http://servidor:8000" y agrégalo a CORS_ORIGINS.
const BASE = (window.API_BASE || "").replace(/\/$/, "");

async function peticion(ruta, opciones = {}) {
  let r;
  try {
    r = await fetch(BASE + ruta, { headers: { "Content-Type": "application/json" }, ...opciones });
  } catch {
    throw new Error("Sin conexión con el servidor");
  }
  if (r.status === 204) return null;
  const json = await r.json().catch(() => null);
  if (!r.ok) {
    const d = json?.detail;
    throw new Error(Array.isArray(d) ? d.map(e => `${e.loc.slice(-1)}: ${e.msg}`).join("; ") : d || `Error ${r.status}`);
  }
  return json;
}

const cuerpo = o => JSON.stringify(o);

export const API = {
  listar: (desde, hasta) => peticion(`/cirugias?desde=${desde}&hasta=${hasta}`),
  crear: datos => peticion("/cirugias", { method: "POST", body: cuerpo(datos) }),
  modificar: (id, datos) => peticion(`/cirugias/${id}`, { method: "PUT", body: cuerpo(datos) }),
  eliminar: id => peticion(`/cirugias/${id}`, { method: "DELETE" }),

  /** Descarga individual (id) o de un rango de fechas (desde/hasta). */
  descargar(formato, { id, desde, hasta }) {
    const ruta = id
      ? `/cirugias/${id}/exportar?formato=${formato}`
      : `/reportes/exportar?desde=${desde}&hasta=${hasta}&formato=${formato}`;
    const a = document.createElement("a");
    a.href = BASE + ruta;
    a.click();
  },

  /** Avisa cuando el backend notifica un cambio. Reintenta solo si se cae la conexión. */
  conectar(alCambiar) {
    const origen = BASE ? BASE.replace(/^http/, "ws") : `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}`;
    const abrir = () => {
      const ws = new WebSocket(`${origen}/ws`);
      ws.onopen = alCambiar;      // al (re)conectar, resincroniza
      ws.onmessage = alCambiar;
      ws.onclose = () => setTimeout(abrir, 3000);
    };
    abrir();
  },
};
