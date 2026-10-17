# Registro de Cirugías — Hospital Morelos

## ¿Qué es?

Un sistema web para **programar las cirugías de los quirófanos y ver en tiempo real cuáles están en curso y cuáles siguen**. Se usa desde el navegador de cualquier computadora de la red del hospital y en una pantalla (TV) para la sala.

## ¿Qué se puede hacer?

| Pantalla | Para qué sirve |
|---|---|
| **Registro** | Dar de alta una cirugía (paciente, edad, sexo, procedimiento, cirujano, quirófano, fecha, duración, aseguradora, diagnóstico y servicios especiales) y editar las de la semana. |
| **Dashboard** | Ver las cirugías del día: cuáles están **en progreso** (con barra de avance) y cuáles **en espera**. Tiene modo pantalla completa para la TV. |
| **Administración** | Resumen de la semana (totales, duración promedio, por quirófano), buscar cirugías de cualquier fecha y descargar reportes en PDF o Excel. |
| **Usuarios** (solo admin) | Crear y administrar las cuentas, y consultar o descargar la **bitácora** de movimientos. |

**Cosas que el sistema hace solo:**
- Una cirugía pasa a **En progreso** cuando llega su hora y a **Finalizada** cuando termina su duración estimada.
- No deja programar dos cirugías **en el mismo quirófano a la misma hora**.
- Todas las pantallas se **actualizan solas** cuando alguien hace un cambio.
- Cada movimiento queda guardado en la **bitácora** con quién lo hizo y cuándo.

**Quién puede hacer qué:** ver [PERMISOS.md](PERMISOS.md).

## Historias de usuario

- **Como capturista**, quiero registrar una cirugía con los datos del paciente, para que quede programada en su quirófano.
- **Como capturista**, quiero que el sistema me avise si el quirófano ya está ocupado a esa hora, para no empalmar cirugías.
- **Como capturista**, quiero corregir los datos de una cirugía ya registrada, para mantener la información al día.
- **Como personal de quirófano**, quiero ver en la TV qué cirugías están en curso y cuáles siguen, para organizarme sin preguntar.
- **Como administrador**, quiero buscar las cirugías de un paciente o de un cirujano en todo el historial, para consultar sus antecedentes.
- **Como administrador**, quiero descargar reportes del día, la semana o el histórico completo, para entregarlos o archivarlos.
- **Como administrador**, quiero crear cuentas y asignar roles, para que cada persona solo haga lo que le corresponde.
- **Como administrador**, quiero ver quién registró, cambió o eliminó cada cirugía, para tener control y respaldo de la información.

## Flujo típico de un día

1. **Inicio:** la TV de la sala ya está con sesión de **Visualizador** y muestra el **Dashboard** del día.
2. **Registro:** la capturista entra con su usuario y, en **Registro**, da de alta las cirugías programadas. Si un quirófano está ocupado a esa hora, el sistema se lo indica.
3. **Durante el día:** cuando llega la hora de cada cirugía, cambia sola a **En progreso** y en la TV aparece su barra de avance; al terminar su tiempo pasa a **Finalizada** y sale del dashboard.
4. **Cambios:** si se mueve una cirugía o se corrige un dato, se edita en **Registro** y todas las pantallas se actualizan al momento.
5. **Cierre:** en **Administración** se revisa el resumen de la semana y se descargan los reportes necesarios (PDF o Excel).
6. **Control:** el administrador puede consultar en la **Bitácora** todo lo que se hizo y quién lo hizo.
