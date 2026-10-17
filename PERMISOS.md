# Permisos por rol

| Permiso | Admin | Capturista | Visualizador |
|---|:-:|:-:|:-:|
| Ver Dashboard | ✅ | ✅ | ✅ |
| Ver Registro y Administración | ✅ | ✅ | ❌ |
| Crear y editar cirugías | ✅ | ✅ | ❌ |
| Cambiar estatus | ✅ | ✅ | ❌ |
| **Eliminar cirugías** | ✅ | ❌ | ❌ |
| Buscar en el historial | ✅ | ✅ | ❌ |
| Descargar PDF/XLSX (individual, día, semana) | ✅ | ✅ | ❌ |
| Descargar histórico completo (XLSX) | ✅ | ✅ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ |
| Ver y descargar la bitácora | ✅ | ❌ | ❌ |
| **Duración de la sesión** | 12 h | 24 h | 30 días |

## Notas

- **Ocultar no es bloquear:** que un botón no aparezca es solo comodidad. La protección real está en el servidor: una acción no permitida responde **403** (sin permiso) o **401** (sin sesión). Lo verifican `tests/test_auth.py` y `tests/test_usuarios.py`.
- **Cambios inmediatos:** si un admin cambia el rol de alguien o lo desactiva, aplica en su siguiente acción, aunque tenga una sesión abierta.
- **Ningún admin puede quitarse a sí mismo** el rol ni desactivar su propia cuenta: el sistema nunca se queda sin administrador.
- **Bitácora:** todo movimiento queda registrado con el rol y el nombre de quien lo hizo en ese momento (por ejemplo `capturista:Andrea_Villanueva`); los cambios automáticos de estatus aparecen como `sistema`.
- Los permisos están definidos en `app/seguridad.py` (backend) y `static/js/state.js` (qué páginas se muestran).

## Funcionalidades agregadas

| Funcionalidad | Qué hace | Quién la usa |
|---|---|---|
| **Inicio de sesión** | Cada persona entra con su usuario y contraseña. Sin sesión no se ve nada. | Todos |
| **Roles** | Admin, Capturista y Visualizador, cada uno con lo que le corresponde (tabla de arriba). | Todos |
| **Gestión de usuarios** | Crear cuentas, cambiar nombre o rol, desactivar/activar y restablecer contraseñas. Página **Usuarios**. | Admin |
| **Bitácora** | Registro de todo lo que se crea, edita, cambia de estatus o elimina, con quién y cuándo. Se puede filtrar por fechas y descargar en PDF o XLSX (todo el historial o un periodo). Pestaña **Bitácora** en Usuarios. | Admin |
| **Búsqueda en el historial** | Busca cirugías de cualquier fecha por nombre del paciente o del cirujano, sin importar mayúsculas ni acentos. Resultados por páginas. En **Administración**. | Admin, Capturista |
| **Histórico completo** | Botón **Histórico completo (XLSX)** que descarga todas las cirugías registradas. En **Administración**. | Admin, Capturista |
| **Datos clínicos** | Cada cirugía lleva edad y sexo (obligatorios), y diagnóstico y servicios especiales (opcionales). Se quitó el código de paciente. Aparecen en el formulario, el dashboard y los reportes. | Todos |
| **Versiones nuevas sin borrar caché** | Al publicar una nueva versión, las pantallas (incluida la TV) la cargan al recargar la página, sin tener que borrar la caché del navegador. | Todos |
