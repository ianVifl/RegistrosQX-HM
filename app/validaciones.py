from datetime import date

from fastapi import HTTPException, status

from app.config import MAX_DIAS_RANGO


def validar_rango(desde: date, hasta: date) -> None:
    if hasta < desde:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'hasta' no puede ser anterior a 'desde'")
    if (hasta - desde).days >= MAX_DIAS_RANGO:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"El rango máximo es de {MAX_DIAS_RANGO} días")
