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

## Despliegue en el servidor

En `/opt/cirugias`:

```bash
nano .env            # crear o editar las variables
chmod 600 .env       # solo el dueño puede leer el archivo (contiene la contraseña)
sudo docker compose build
sudo docker compose up -d
```

> Uvicorn debe correr con **un solo worker**: los avisos en tiempo real (WebSocket) viven en la memoria del proceso.
