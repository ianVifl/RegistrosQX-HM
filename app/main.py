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
from app.database import Base, engine
from app.routers import cirugias, reportes
from app.scheduler import ciclo_estatus

log = logging.getLogger(__name__)

# En Windows el registro del sistema puede mapear .js a text/plain, y los navegadores
# rechazan los módulos ES con ese tipo MIME.
mimetypes.add_type("text/javascript", ".js")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
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

app.include_router(cirugias.router)
app.include_router(reportes.router)
app.include_router(realtime.router)

# Siempre al final: el mount en "/" captura todo lo que no coincidió antes.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="front")
else:
    log.warning("No existe la carpeta del frontend (%s): solo se sirve la API", STATIC_DIR)
