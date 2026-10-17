// Única capa que habla con el backend. Si el front se sirve desde otro origen,
// define antes window.API_BASE = "http://servidor:8000" y agrégalo a CORS_ORIGINS.
const BASE = (window.API_BASE || "").replace(/\/$/, "");
export const LOGIN = "login.html";

/** Sin sesión válida (expiró o desactivaron la cuenta): de vuelta al login. */
export const irAlLogin = () => location.replace(LOGIN);

async function peticion(ruta, opciones = {}, { alLogin = true } = {}) {
  let r;
  try {
    r = await fetch(BASE + ruta, {
      headers: { "Content-Type": "application/json" },
      credentials: BASE ? "include" : "same-origin", // la cookie de sesión viaja sola
      ...opciones,
    });
  } catch {
    throw new Error("Sin conexión con el servidor");
  }
  if (r.status === 401 && alLogin) {
    irAlLogin();
    return new Promise(() => {}); // nunca se resuelve: nada sigue ejecutándose mientras se va al login
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
const consulta = params => new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();

/** Descarga por enlace: el navegador manda la cookie y respeta el nombre de archivo del servidor. */
function descargarRuta(ruta) {
  const a = document.createElement("a");
  a.href = BASE + ruta;
  a.click();
}

export const API = {
  // Sesión
  login: (usuario, password) => peticion("/auth/login", { method: "POST", body: cuerpo({ usuario, password }) }, { alLogin: false }),
  logout: () => peticion("/auth/logout", { method: "POST" }, { alLogin: false }),
  yo: ({ alLogin = true } = {}) => peticion("/auth/yo", {}, { alLogin }),

  // Cirugías
  listar: (desde, hasta) => peticion(`/cirugias?desde=${desde}&hasta=${hasta}`),
  buscar: (q, pagina = 1, tamano = 20) => peticion(`/cirugias/buscar?${consulta({ q, pagina, tamano })}`),
  crear: datos => peticion("/cirugias", { method: "POST", body: cuerpo(datos) }),
  modificar: (id, datos) => peticion(`/cirugias/${id}`, { method: "PUT", body: cuerpo(datos) }),
  eliminar: id => peticion(`/cirugias/${id}`, { method: "DELETE" }),

  /** Descarga individual (id) o de un rango de fechas (desde/hasta). */
  descargar(formato, { id, desde, hasta }) {
    descargarRuta(id
      ? `/cirugias/${id}/exportar?formato=${formato}`
      : `/reportes/exportar?${consulta({ desde, hasta, formato })}`);
  },

  // Usuarios (solo admin)
  usuarios: () => peticion("/usuarios"),
  crearUsuario: datos => peticion("/usuarios", { method: "POST", body: cuerpo(datos) }),
  editarUsuario: (id, datos) => peticion(`/usuarios/${id}`, { method: "PUT", body: cuerpo(datos) }),
  activarUsuario: (id, activo) => peticion(`/usuarios/${id}/activo`, { method: "PATCH", body: cuerpo({ activo }) }),
  restablecerPassword: (id, password) => peticion(`/usuarios/${id}/password`, { method: "PUT", body: cuerpo({ password }) }),

  // Bitácora (solo admin). Sin fechas = todo el historial.
  bitacora: ({ desde, hasta, pagina = 1, tamano = 50 } = {}) => peticion(`/bitacora?${consulta({ desde, hasta, pagina, tamano })}`),
  descargarBitacora: (formato, { desde, hasta } = {}) => descargarRuta(`/bitacora/exportar?${consulta({ formato, desde, hasta })}`),

  /** Avisa cuando el backend notifica un cambio. Si se cae la conexión, revisa la sesión y reintenta. */
  conectar(alCambiar) {
    const origen = BASE ? BASE.replace(/^http/, "ws") : `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}`;
    const abrir = () => {
      const ws = new WebSocket(`${origen}/ws`);
      ws.onopen = alCambiar;      // al (re)conectar, resincroniza
      ws.onmessage = alCambiar;
      // Un rechazo por sesión vencida no se distingue de una caída de red: /auth/yo lo aclara
      // (con 401 manda al login; sin red, se vuelve a intentar).
      ws.onclose = () => setTimeout(() => API.yo().then(abrir, abrir), 3000);
    };
    abrir();
  },
};
