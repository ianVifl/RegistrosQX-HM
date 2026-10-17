import { estado, restaurar, paginasPermitidas, esAdmin } from "./state.js";
import { API, irAlLogin } from "./api.js";
import { IC } from "./icons.js";
import { $, hm, pad, nombreDia, hoy } from "./utils.js";
import { cargar, render, refrescar, transicion, TEMAS } from "./app.js";
import { iniciarAcciones } from "./actions.js";
import { iniciarCalendario } from "./calendario.js";

const raiz = document.documentElement;
// --- Frecuencias de actualización (se pueden cambiar aquí) ---
const REFRESCO_MIN = 30; // corte alineado al reloj: el dashboard se resincroniza en cada :00 y :30
const SONDEO_SEG = 60;   // red de seguridad: cada cuántos segundos el dashboard pide los datos al servidor

restaurar();
raiz.dataset.theme = estado.tema;

/* Sesión: sin sesión válida, API.yo() redirige al login y aquí se detiene el módulo */
estado.usuario = await API.yo();
const permitidas = paginasPermitidas();
if (!permitidas.includes(estado.pagina)) estado.pagina = permitidas[0];
document.querySelectorAll(".nav a[data-p]").forEach(a => { a.hidden = !permitidas.includes(a.dataset.p); });
$("lUsuarios").hidden = !esAdmin();
$("quien").textContent = estado.usuario.nombre;
$("quien").title = `Sesión: ${estado.usuario.usuario} (${estado.usuario.rol.toLowerCase()})`;
$("bSalir").innerHTML = IC.salir;
$("bSalir").onclick = () => API.logout().finally(irAlLogin);

iniciarAcciones();
iniciarCalendario();

/* Navegación y botones cíclicos de tema y vista */
document.querySelectorAll(".nav a[data-p]").forEach(a => a.addEventListener("click", e => {
  e.preventDefault();
  estado.pagina = a.dataset.p;
  estado.abierto = null;
  cargar({ animar: true });
}));
$("bTema").onclick = () => {
  const i = TEMAS.findIndex(t => t[0] === estado.tema);
  estado.tema = TEMAS[(i + 1) % TEMAS.length][0];
  transicion(render);
};
$("bModo").onclick = () => { estado.modos[estado.pagina] = (estado.modos[estado.pagina] % 3) + 1; transicion(render); };

/* Reloj (con segundos y fecha en pantalla completa) */
function tick() {
  const d = new Date();
  $("clock").textContent = hm(d) + (raiz.classList.contains("fs") ? `:${pad(d.getSeconds())}` : "");
  $("fecha").innerHTML = `<b style="color:var(--ink)">${nombreDia(hoy()).split(" ")[0]}</b><br>${d.toLocaleDateString("es-MX", { day: "numeric", month: "long", year: "numeric" })}`;
}
setInterval(tick, 1000);

/* Pantalla completa: solo reloj, logo y el botón; el Dashboard vuelve a "hoy" */
const fs = $("fs");
fs.innerHTML = IC.expand;
fs.onclick = () => estado.pagina === "dash" && (document.fullscreenElement ? document.exitFullscreen() : raiz.requestFullscreen()).catch(() => {});
document.addEventListener("fullscreenchange", () => {
  const activo = !!document.fullscreenElement;
  raiz.classList.toggle("fs", activo);
  fs.innerHTML = activo ? IC.shrink : IC.expand;
  fs.setAttribute("aria-label", activo ? "Salir de pantalla completa" : "Pantalla completa");
  fs.title = fs.getAttribute("aria-label");
  if (activo) estado.diaDash = null;
  tick();
  render();
});

/* Actualización: avisos del servidor, corte cada media hora y repintado local cada minuto */
API.conectar(refrescar);
function programarCorte() {
  const ahora = new Date();
  const segundosDelDia = ahora.getHours() * 3600 + ahora.getMinutes() * 60 + ahora.getSeconds();
  const siguiente = (Math.floor(segundosDelDia / (REFRESCO_MIN * 60)) + 1) * REFRESCO_MIN * 60;
  setTimeout(() => { refrescar(); programarCorte(); }, (siguiente - segundosDelDia) * 1000 + 5000); // +5 s: deja que el backend actualice primero
}
programarCorte();
setInterval(() => { if (estado.pagina === "dash") refrescar(); }, SONDEO_SEG * 1000); // también repinta las barras de avance

tick();
cargar();
