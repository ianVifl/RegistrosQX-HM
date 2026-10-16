from fastapi import APIRouter, WebSocket, WebSocketDisconnect


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


@router.websocket("/ws")
async def ws_cambios(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # solo mantiene viva la conexión
    except WebSocketDisconnect:
        manager.disconnect(ws)
