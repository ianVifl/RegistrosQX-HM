# Registro de Cirugías — Hospital Morelos

Sistema para programar y monitorear cirugías en quirófano: registro, dashboard en tiempo real y reportes PDF/XLSX.

**Stack:** FastAPI + SQLAlchemy (MariaDB/MySQL) · frontend en HTML/JS sin build · Docker.

## Configuración

Copia la plantilla y completa los valores:

```bash
cp .env.example .env
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Sí (`DB_PORT` por defecto 3306) | Conexión a la base de datos |
| `APP_TZ` | No | Zona horaria de las fechas (por defecto `America/Mexico_City`) |
| `CORS_ORIGINS` | No | Orígenes permitidos, separados por coma |
| `ACTUALIZAR_CADA_MIN` | No | Cada cuántos minutos se actualiza el estatus de las cirugías (por defecto 30) |
| `SECRET_KEY` | Sí | Firma las sesiones; mínimo 32 bytes. Genera una con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Si cambia, todas las sesiones se cierran |
| `COOKIE_SECURE` | No | `true` solo si la app se sirve por HTTPS (por defecto `false`) |

## Usuarios y roles

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

Detalle y notas en [PERMISOS.md](PERMISOS.md). Descripción general, historias de usuario y flujo típico en [PROYECTO.md](PROYECTO.md).

No hay un administrador por defecto. El primero se crea desde la terminal:

```bash
python -m app.crear_admin                                  # local
sudo docker compose run --rm api python -m app.crear_admin # servidor
```

> La app corre por HTTP en la red local: las contraseñas viajan sin cifrar. Se recomienda servirla por HTTPS y poner `COOKIE_SECURE=true`.

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La app queda en http://localhost:8000 y la documentación de la API en http://localhost:8000/docs.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Usan una BD aparte, `registros_cirugias_test` (o la que indique `TEST_DB_NAME`), en el mismo servidor del `.env`: se crea sola y se le aplican las migraciones. Por seguridad solo corren contra un host local y una BD cuyo nombre termine en `_test`.

## Migraciones (Alembic)

El esquema de la BD lo administra Alembic; la app **no** crea tablas al arrancar.

```bash
alembic upgrade head                             # aplica las migraciones pendientes
alembic current                                  # versión en la que está la BD
alembic revision --autogenerate -m "descripción" # genera una migración a partir de los cambios en app/models.py
alembic check                                    # falla si models.py y la BD no coinciden
```

Revisa siempre el archivo generado en `alembic/versions/` antes de aplicarlo: autogenerate no detecta todo (por ejemplo, renombrar una columna lo interpreta como borrar y crear).

**BD que ya existía antes de Alembic:** no se ejecuta la migración base, solo se marca (`alembic stamp 8392ed4674d8`) y después `alembic upgrade head`.

## Despliegue en el servidor

En `/opt/cirugias`:

```bash
nano .env            # crear o editar las variables
chmod 600 .env       # solo el dueño puede leer el archivo (contiene la contraseña)
sudo docker compose build
sudo docker compose run --rm api alembic upgrade head   # migraciones antes de levantar la app
sudo docker compose up -d
sudo docker compose run --rm api python -m app.crear_admin   # solo la primera vez
```

> MySQL/MariaDB no permiten deshacer cambios de esquema (DDL) dentro de una transacción: si una migración falla a la mitad, queda aplicada a medias. **Respalda la BD antes de migrar** (`mysqldump`).

> Uvicorn debe correr con **un solo worker**: los avisos en tiempo real (WebSocket) viven en la memoria del proceso.
