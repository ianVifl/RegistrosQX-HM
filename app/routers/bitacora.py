from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import bitacora, crud, exports, seguridad
from app.database import get_db
from app.models import Bitacora
from app.schemas import BitacoraOut, Pagina

router = APIRouter(prefix="/bitacora", tags=["bitácora"], dependencies=[Depends(seguridad.solo_admin)])


def _salida(b: Bitacora) -> BitacoraOut:
    return BitacoraOut(id=b.id, fecha=b.fecha, autor=bitacora.autor(b), accion=b.accion, entidad=b.entidad,
                       entidadId=b.entidadId, detalle=b.detalle, resumen=bitacora.resumen(b))


def _validar(desde: date | None, hasta: date | None) -> None:
    if desde and hasta and hasta < desde:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'hasta' no puede ser anterior a 'desde'")


def _periodo(desde: date | None, hasta: date | None) -> str:
    if desde and hasta:
        return f"del {desde:%d/%m/%Y} al {hasta:%d/%m/%Y}"
    if desde:
        return f"desde el {desde:%d/%m/%Y}"
    if hasta:
        return f"hasta el {hasta:%d/%m/%Y}"
    return "completa"


@router.get("", response_model=Pagina[BitacoraOut])
def consultar(
    desde: date | None = None,
    hasta: date | None = None,
    pagina: int = Query(1, ge=1),
    tamano: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    _validar(desde, hasta)
    resultado = crud.paginar(crud.consultarBitacora(db, desde, hasta), pagina, tamano)
    return {**resultado, "items": [_salida(b) for b in resultado["items"]]}


@router.get("/exportar")
def exportar(
    formato: Literal["pdf", "xlsx"],
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
) -> Response:
    """Sin fechas exporta todo el historial (sin límite de rango: puede tardar si hay muchos registros)."""
    _validar(desde, hasta)
    movimientos = crud.consultarBitacora(db, desde, hasta).all()
    nombre = "bitacora" + (f"_{desde.isoformat()}" if desde else "") + (f"_a_{hasta.isoformat()}" if hasta else "")
    return exports.respuesta_archivo(
        movimientos, formato, f"Bitácora {_periodo(desde, hasta)}", nombre,
        exports.COLUMNAS_BITACORA, exports.ANCHOS_BITACORA, hoja="Bitácora",
    )
