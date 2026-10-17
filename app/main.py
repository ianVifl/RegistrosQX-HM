import asyncio
import logging
import mimetypes
from contextlib import asynccontextmanager, suppress
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import realtime
from app.config import CORS_ORIGINS, STATIC_DIR
from app.routers import auth, bitacora, cirugias, reportes, usuarios
from app.scheduler import ciclo_estatus

log = logging.getLogger(__name__)

# En Windows el registro del sistema puede mapear .js a text/plain, y los navegadores
# rechazan los módulos ES con ese tipo MIME.
mimetypes.add_type("text/javascript", ".js")


class EstaticosRevalidados(StaticFiles):
    """Archivos del frontend con Cache-Control: no-cache.

    No desactiva la caché: obliga al navegador a preguntar si el archivo cambió (ETag) antes de usar
    su copia. Si no cambió responde 304 sin reenviarlo; si cambió (nuevo despliegue) baja el nuevo.
    Sin esta cabecera el navegador puede seguir usando JS viejo durante horas.
    """

    async def get_response(self, path, scope):
        respuesta = await super().get_response(path, scope)
        respuesta.headers["Cache-Control"] = "no-cache"
        return respuesta


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # El esquema lo administra Alembic (alembic upgrade head), no la app al arrancar.
    tarea = asyncio.create_task(ciclo_estatus())
    yield
    tarea.cancel()
    with suppress(asyncio.CancelledError):
        await tarea


app = FastAPI(
    title="Cirugias API",
    description="API para gestionar registros de cirugías",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cirugias.router)
app.include_router(reportes.router)
app.include_router(usuarios.router)
app.include_router(bitacora.router)
app.include_router(realtime.router)

# Siempre al final: el mount en "/" captura todo lo que no coincidió antes.
if STATIC_DIR.is_dir():
    app.mount("/", EstaticosRevalidados(directory=STATIC_DIR, html=True), name="front")
else:
    log.warning("No existe la carpeta del frontend (%s): solo se sirve la API", STATIC_DIR)
