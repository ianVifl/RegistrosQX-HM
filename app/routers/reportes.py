from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app import config, crud, exports, seguridad
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


@router.get("/historico")
def exportar_historico(db: Session = Depends(get_db)) -> Response:
    """Todas las cirugías registradas, de la más antigua a la más reciente, en XLSX (sin límite de fechas)."""
    hoy = config.ahora().date()
    return exports.respuesta_archivo(
        crud.obtenerTodasLasCirugias(db), "xlsx",
        f"Histórico completo de cirugías al {hoy:%d/%m/%Y}", f"cirugias_historico_completo_{hoy.isoformat()}",
    )
