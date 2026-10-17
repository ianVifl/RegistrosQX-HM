from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app import crud, exports, seguridad
from app.database import get_db
from app.validaciones import validar_rango

router = APIRouter(prefix="/reportes", tags=["reportes"], dependencies=[Depends(seguridad.editor)])


@router.get("/exportar")
def exportar_rango(
    formato: Literal["pdf", "xlsx"],
    desde: date,
    hasta: date,
    db: Session = Depends(get_db),
) -> Response:
    """Un día (desde == hasta), una semana o cualquier rango de hasta 31 días."""
    validar_rango(desde, hasta)
    cirugias = crud.obtenerCirugiasPorRango(db, desde, hasta)
    nombre = f"cirugias_{desde.isoformat()}" + ("" if desde == hasta else f"_a_{hasta.isoformat()}")
    return exports.respuesta_archivo(cirugias, formato, exports.titulo_rango(desde, hasta), nombre)
