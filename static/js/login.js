import { API } from "./api.js";
import { estado, restaurar } from "./state.js";
import { toast } from "./ui.js";
import { $ } from "./utils.js";

restaurar();
document.documentElement.dataset.theme = estado.tema;

const entrar = () => location.replace("./");

// Si la sesión sigue vigente (p. ej. la TV del dashboard se recargó), no hace falta volver a entrar
API.yo({ alLogin: false }).then(entrar, () => {});

$("fLogin").addEventListener("submit", async e => {
  e.preventDefault();
  const usuario = $("lu").value.trim(), password = $("lp").value;
  if (!usuario || !password) return toast("Escribe tu usuario y contraseña", true);
  const boton = $("lEntrar");
  boton.disabled = true;
  try {
    await API.login(usuario, password);
    entrar();
  } catch (err) {
    toast(err.message, true);
    $("lp").value = "";
    $("lp").focus();
  } finally {
    boton.disabled = false;
  }
});
