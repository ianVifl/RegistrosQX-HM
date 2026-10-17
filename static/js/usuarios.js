// Gestión de usuarios y bitácora (solo ADMIN). El backend valida todo; aquí solo se presenta.
import { API, irAlLogin } from "./api.js";
import { estado, restaurar } from "./state.js";
import { toast, confirmar } from "./ui.js";
import { IC } from "./icons.js";
import { $, esc, hm, pad } from "./utils.js";
import { vacio } from "./components.js";

const ROLES = { ADMIN: "Administrador", CAPTURISTA: "Capturista", VISUALIZADOR: "Visualizador" };
const ACCIONES = {
  CREAR: "Creó", EDITAR: "Editó", CAMBIAR_ESTATUS: "Cambió estatus", ELIMINAR: "Eliminó",
  ACTIVAR: "Activó", DESACTIVAR: "Desactivó", RESTABLECER_PASSWORD: "Restableció contraseña",
};
const ENTIDADES = { CIRUGIA: "Cirugía", USUARIO: "Usuario" };

const vista = {
  tab: "usr",
  usuarios: [],
  abierto: null, // id del usuario expandido para editar
  bit: { desde: "", hasta: "", pagina: 1, resultado: null },
};

restaurar();
document.documentElement.dataset.theme = estado.tema;
const yo = await API.yo();
if (yo.rol !== "ADMIN") {
  location.replace("./");
} else {
  $("quien").textContent = yo.nombre;
  $("bSalir").innerHTML = IC.salir;
  $("bSalir").onclick = () => API.logout().finally(irAlLogin);
  document.querySelectorAll(".nav a[data-t]").forEach(a => a.addEventListener("click", e => {
    e.preventDefault();
    vista.tab = a.dataset.t;
    cargar();
  }));
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-a]");
    acciones[b?.dataset.a]?.(b);
  });
  document.addEventListener("submit", e => {
    const f = e.target.closest("[data-f]");
    if (!f) return;
    e.preventDefault();
    acciones[f.dataset.f]?.(f);
  });
  cargar();
}

async function cargar() {
  try {
    if (vista.tab === "usr") vista.usuarios = await API.usuarios();
    else vista.bit.resultado = await API.bitacora(vista.bit);
  } catch (e) {
    toast(e.message, true);
  }
  render();
}

function render() {
  document.querySelectorAll(".nav a[data-t]").forEach(a => a.toggleAttribute("aria-current", a.dataset.t === vista.tab));
  $("view").innerHTML = vista.tab === "usr" ? pantallaUsuarios() : pantallaBitacora();
}

/* ---------- Usuarios ---------- */
const opcionesRol = actual => Object.entries(ROLES)
  .map(([v, txt]) => `<option value="${v}" ${v === actual ? "selected" : ""}>${txt}</option>`).join("");
const campo = (id, etiqueta, control) => `<div class="f"><label for="${id}">${etiqueta}</label>${control}</div>`;

const formNuevo = () => `<section class="card panel"><h2>Nuevo usuario</h2><form data-f="crear" class="fg c1" autocomplete="off">
  ${campo("nu", "Usuario (para iniciar sesión)", `<input id="nu" autocapitalize="none" spellcheck="false" placeholder="andrea.villanueva">`)}
  ${campo("nn", "Nombre completo", `<input id="nn">`)}
  ${campo("nr", "Rol", `<select id="nr">${opcionesRol("CAPTURISTA")}</select>`)}
  ${campo("np", "Contraseña (mínimo 8 caracteres)", `<input id="np" type="password" autocomplete="new-password">`)}
  <div class="acts"><button class="btn pri">Crear usuario</button></div></form></section>`;

function filaUsuario(u) {
  const abierta = vista.abierto === u.id;
  const soyYo = u.id === yo.id;
  const estadoTxt = u.activo ? `<span class="pill s-prog">Activo</span>` : `<span class="pill s-fin">Inactivo</span>`;
  const boton = soyYo ? `<span class="mut">(tu cuenta)</span>`
    : `<button class="btn sm ${u.activo ? "dng" : ""}" data-a="activo" data-id="${u.id}">${u.activo ? "Desactivar" : "Activar"}</button>`;
  return `<div class="lr usr ${abierta ? "ex-open" : ""} ${u.activo ? "" : "inactivo"}">
    <span><b>${esc(u.nombre)}</b></span><span class="mut">${esc(u.usuario)}</span><span>${ROLES[u.rol] ?? esc(u.rol)}</span>
    ${estadoTxt}<span style="display:flex;gap:6px;align-items:center">${boton}
    <button class="btn sm ic" data-a="exp" data-id="${u.id}" aria-expanded="${abierta}" aria-label="Editar ${esc(u.nombre)}">${IC.chev}</button></span></div>`
    + (abierta ? `<div class="ex"><div class="fg">
      ${campo("xn", "Nombre completo", `<input id="xn" value="${esc(u.nombre)}">`)}
      ${campo("xr", "Rol", `<select id="xr" ${soyYo ? "disabled" : ""}>${opcionesRol(u.rol)}</select>`)}
      </div><div class="acts"><button class="btn pri sm" data-a="guardar" data-id="${u.id}">Guardar cambios</button></div>
      <div class="fg" style="margin-top:14px">${campo("xp", "Nueva contraseña", `<input id="xp" type="password" autocomplete="new-password">`)}</div>
      <div class="acts"><button class="btn sm" data-a="password" data-id="${u.id}">Restablecer contraseña</button></div></div>` : "");
}

const pantallaUsuarios = () => `<div class="lay1">${formNuevo()}<section>
  <div class="head-row"><h2>Usuarios</h2><span class="mut">${vista.usuarios.filter(u => u.activo).length} activos de ${vista.usuarios.length}</span></div>
  <div class="lst"><div class="lh usr"><span>Nombre</span><span>Usuario</span><span>Rol</span><span>Estado</span><span></span></div>
  ${vista.usuarios.map(filaUsuario).join("")}</div></section></div>`;

/* ---------- Bitácora ---------- */
const fechaHora = iso => {
  const d = new Date(iso);
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${hm(d)}`;
};

const filaBitacora = m => `<div class="lr bit"><span class="mut">${fechaHora(m.fecha)}</span>
  <span><b>${esc(m.autor)}</b></span><span>${ACCIONES[m.accion] ?? esc(m.accion)}</span>
  <span>${ENTIDADES[m.entidad] ?? esc(m.entidad)}${m.entidadId ? ` #${m.entidadId}` : ""}</span>
  <span class="nota">${esc(m.resumen)}</span></div>`;

function pantallaBitacora() {
  const { desde, hasta, resultado: r } = vista.bit;
  const filtros = `<form class="card panel filtros" data-f="filtrar">
    ${campo("bd", "Desde", `<input id="bd" type="date" value="${desde}">`)}
    ${campo("bh", "Hasta", `<input id="bh" type="date" value="${hasta}">`)}
    <div class="acts"><button class="btn pri">Filtrar</button>${desde || hasta ? `<button type="button" class="btn" data-a="sinfiltro">Quitar filtro</button>` : ""}</div>
    <div class="acts descarga"><span class="mut">${desde || hasta ? "Descargar el periodo filtrado:" : "Descargar todo el historial:"}</span>
      ${["pdf", "xlsx"].map(f => `<button type="button" class="btn sm" data-a="dlbit" data-fmt="${f}">${IC.dl}${f.toUpperCase()}</button>`).join("")}</div>
  </form>`;
  if (!r) return filtros + vacio("Cargando…");
  if (!r.total) return filtros + vacio("No hay movimientos en este periodo.");
  const paginador = `<div class="pager" role="group" aria-label="Páginas de la bitácora">
    <button class="btn sm ic" data-a="bitpag" data-d="-1" aria-label="Página anterior" ${r.pagina <= 1 ? "disabled" : ""}>${IC.izq}</button>
    <span class="pager-t" aria-live="polite">Página ${r.pagina} de ${r.paginas}</span>
    <button class="btn sm ic" data-a="bitpag" data-d="1" aria-label="Página siguiente" ${r.pagina >= r.paginas ? "disabled" : ""}>${IC.der}</button></div>`;
  return `${filtros}<div class="head-row"><h2>${r.total} movimiento${r.total === 1 ? "" : "s"}</h2>${paginador}</div>
    <div class="lst"><div class="lh bit"><span>Fecha</span><span>Usuario</span><span>Acción</span><span>Registro</span><span>Detalle</span></div>
    ${r.items.map(filaBitacora).join("")}</div>`;
}

/* ---------- Acciones ---------- */
const buscarUsuario = id => vista.usuarios.find(u => u.id === id);

async function ejecutar(operacion, mensajeOk) {
  try {
    await operacion();
    toast(mensajeOk);
    await cargar();
    return true;
  } catch (e) {
    toast(e.message, true);
    return false;
  }
}

const acciones = {
  async crear() {
    const datos = { usuario: $("nu").value.trim(), nombre: $("nn").value.trim(), rol: $("nr").value, password: $("np").value };
    if (!datos.usuario || !datos.nombre) return toast("Escribe el usuario y el nombre", true);
    if (datos.password.length < 8) return toast("La contraseña debe tener al menos 8 caracteres", true);
    await ejecutar(() => API.crearUsuario(datos), `Usuario ${datos.usuario} creado`);
  },
  exp(b) { const id = Number(b.dataset.id); vista.abierto = vista.abierto === id ? null : id; render(); },
  async guardar(b) {
    const id = Number(b.dataset.id);
    const datos = { nombre: $("xn").value.trim(), rol: $("xr").value };
    if (!datos.nombre) return toast("El nombre no puede quedar vacío", true);
    if (await ejecutar(() => API.editarUsuario(id, datos), "Cambios guardados")) { vista.abierto = null; render(); }
  },
  async password(b) {
    const id = Number(b.dataset.id), password = $("xp").value;
    if (password.length < 8) return toast("La contraseña debe tener al menos 8 caracteres", true);
    const nombre = esc(buscarUsuario(id)?.nombre);
    if (!await confirmar({ titulo: "Restablecer contraseña", mensaje: `<b>${nombre}</b> tendrá que usar la nueva contraseña desde su próximo inicio de sesión.`, boton: "Restablecer" })) return;
    if (await ejecutar(() => API.restablecerPassword(id, password), "Contraseña restablecida")) { vista.abierto = null; render(); }
  },
  async activo(b) {
    const u = buscarUsuario(Number(b.dataset.id));
    if (u.activo && !await confirmar({
      titulo: "Desactivar usuario", boton: "Desactivar", peligro: true,
      mensaje: `<b>${esc(u.nombre)}</b> ya no podrá entrar y su sesión abierta se cerrará. Su historial en la bitácora se conserva.`,
    })) return;
    await ejecutar(() => API.activarUsuario(u.id, !u.activo), u.activo ? "Usuario desactivado" : "Usuario activado");
  },

  filtrar() {
    const desde = $("bd").value, hasta = $("bh").value;
    if (desde && hasta && hasta < desde) return toast("'Hasta' no puede ser anterior a 'Desde'", true);
    Object.assign(vista.bit, { desde, hasta, pagina: 1, resultado: null });
    render();
    cargar();
  },
  sinfiltro() { Object.assign(vista.bit, { desde: "", hasta: "", pagina: 1, resultado: null }); render(); cargar(); },
  bitpag(b) { vista.bit.pagina += Number(b.dataset.d); cargar(); },
  dlbit(b) {
    API.descargarBitacora(b.dataset.fmt, vista.bit);
    toast("Generando el archivo; con mucho historial puede tardar un poco");
  },
};
