from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.concurrency import run_in_threadpool

from app import seguridad
from app.database import SessionLocal


class ConnectionManager:
    """Mantiene los WebSockets abiertos (dashboards) y les avisa de cambios.

    Vive en la memoria del proceso: ejecuta uvicorn con UN solo worker.
    """

    def __init__(self) -> None:
        self.activas: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.activas.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.activas.discard(ws)

    async def broadcast(self, mensaje: str) -> None:
        for ws in list(self.activas):
            try:
                await ws.send_text(mensaje)
            except Exception:
                self.disconnect(ws)


manager = ConnectionManager()
router = APIRouter()


def _sesion_valida(token: str | None) -> bool:
    with SessionLocal() as db:
        return seguridad.usuario_de_token(db, token) is not None


@router.websocket("/ws")
async def ws_cambios(ws: WebSocket) -> None:
    # El navegador manda la cookie de sesión en el handshake (no permite headers como Authorization).
    if not await run_in_threadpool(_sesion_valida, ws.cookies.get(seguridad.COOKIE)):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # solo mantiene viva la conexión
    except WebSocketDisconnect:
        manager.disconnect(ws)
