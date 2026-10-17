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
