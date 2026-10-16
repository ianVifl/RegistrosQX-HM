import asyncio
import logging
from datetime import datetime, timedelta

from fastapi.concurrency import run_in_threadpool

from app import crud
from app.config import ACTUALIZAR_CADA_MIN, TZ
from app.database import SessionLocal
from app.realtime import manager

log = logging.getLogger(__name__)


def segundos_hasta_siguiente_corte(ahora: datetime, cada_min: int) -> float:
    """Segundos hasta el próximo múltiplo de `cada_min` minutos desde medianoche (:00, :30...)."""
    minutos = ahora.hour * 60 + ahora.minute
    siguiente = (minutos // cada_min + 1) * cada_min
    destino = ahora.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=siguiente)
    return max((destino - ahora).total_seconds(), 1)


def _actualizar_estatus() -> int:
    ahora = datetime.now(TZ).replace(tzinfo=None)  # la BD guarda fechas sin zona
    with SessionLocal() as db:
        return crud.activarProgramadas(db, ahora) + crud.finalizarVencidas(db, ahora)


async def ciclo_estatus() -> None:
    """Programadas que ya empezaron -> EN PROGRESO; en progreso que ya terminaron -> FINALIZADA."""
    while True:
        try:
            if await run_in_threadpool(_actualizar_estatus):
                await manager.broadcast("cambio")
        except Exception:
            log.exception("No se pudo actualizar el estatus de las cirugías")
        espera = segundos_hasta_siguiente_corte(datetime.now(TZ), ACTUALIZAR_CADA_MIN) + 1
        await asyncio.sleep(espera)
