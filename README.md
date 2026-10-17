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

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La app queda en http://localhost:8000 y la documentación de la API en http://localhost:8000/docs.

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
```

> MySQL/MariaDB no permiten deshacer cambios de esquema (DDL) dentro de una transacción: si una migración falla a la mitad, queda aplicada a medias. **Respalda la BD antes de migrar** (`mysqldump`).

> Uvicorn debe correr con **un solo worker**: los avisos en tiempo real (WebSocket) viven en la memoria del proceso.
