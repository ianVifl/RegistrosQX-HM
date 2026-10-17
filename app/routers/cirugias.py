from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, exports, models, seguridad
from app.config import TZ
from app.database import get_db
from app.realtime import manager
from app.schemas import CirugiaCreate, CirugiaOut, CirugiaUpdate, EstatusUpdate, Pagina
from app.validaciones import validar_rango

router = APIRouter(prefix="/cirugias", tags=["cirugias"])


def _no_encontrada() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "No se encontró la cirugía")


def _validar_traslape(db: Session, datos: CirugiaCreate, excluir_id: int | None = None) -> None:
    if getattr(datos, "estatus", None) == "FINALIZADA":
        return
    choque = crud.buscarTraslape(db, datos.quirofano, datos.fechaCirugia, datos.duracionEstimada, excluir_id)
    if choque:
        fin = choque.fechaCirugia + timedelta(minutes=choque.duracionEstimada)
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"{datos.quirofano} ya tiene una cirugía de {choque.fechaCirugia:%H:%M} a {fin:%H:%M} "
            f"({choque.nombrePaciente})",
        )


@router.post("", response_model=CirugiaOut, status_code=status.HTTP_201_CREATED)
def crear_cirugia(
    datos: CirugiaCreate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(seguridad.editor),
) -> models.Cirugia:
    _validar_traslape(db, datos)
    cirugia = crud.crearRegistroCirugia(db, **datos.model_dump(), autor=usuario)
    background.add_task(manager.broadcast, "cambio")
    return cirugia


@router.get("", response_model=list[CirugiaOut], dependencies=[Depends(seguridad.cualquier_rol)])
def listar_cirugias(
    fecha: date | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
) -> list[models.Cirugia]:
    """Un día (`fecha`, por defecto hoy) o un rango (`desde` + `hasta`, ambos incluidos)."""
    if desde or hasta:
        if not (desde and hasta):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Indica 'desde' y 'hasta'")
        validar_rango(desde, hasta)
        return crud.obtenerCirugiasPorRango(db, desde, hasta)
    return crud.obtenerCirugiasPorFecha(db, fecha or datetime.now(TZ).date())


@router.get("/buscar", response_model=Pagina[CirugiaOut], dependencies=[Depends(seguridad.editor)])
def buscar_cirugias(
    q: str = Query(min_length=2, max_length=100, description="Nombre del paciente o del cirujano"),
    pagina: int = Query(1, ge=1),
    tamano: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """Busca en todo el historial, de la cirugía más reciente a la más antigua."""
    return crud.buscarCirugias(db, q.strip(), pagina, tamano)


@router.get("/{cirugia_id}", response_model=CirugiaOut, dependencies=[Depends(seguridad.cualquier_rol)])
def obtener_cirugia(cirugia_id: int, db: Session = Depends(get_db)) -> models.Cirugia:
    cirugia = crud.obtenerRegistroCirugiaPorId(db, cirugia_id)
    if cirugia is None:
        raise _no_encontrada()
    return cirugia


@router.put("/{cirugia_id}", response_model=CirugiaOut)
def modificar_cirugia(
    cirugia_id: int,
    datos: CirugiaUpdate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(seguridad.editor),
) -> models.Cirugia:
    _validar_traslape(db, datos, excluir_id=cirugia_id)
    cirugia = crud.modificarRegistroCirugia(db, cirugia_id, **datos.model_dump(), autor=usuario)
    if cirugia is None:
        raise _no_encontrada()
    background.add_task(manager.broadcast, "cambio")
    return cirugia


@router.patch("/{cirugia_id}/estatus", response_model=CirugiaOut)
def cambiar_estatus(
    cirugia_id: int,
    datos: EstatusUpdate,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(seguridad.editor),
) -> models.Cirugia:
    cirugia = crud.cambiarEstatusCirugia(db, cirugia_id, datos.estatus, autor=usuario)
    if cirugia is None:
        raise _no_encontrada()
    background.add_task(manager.broadcast, "cambio")
    return cirugia


@router.delete("/{cirugia_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def eliminar_cirugia(
    cirugia_id: int,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(seguridad.solo_admin),
) -> Response:
    if crud.eliminarRegistroCirugia(db, cirugia_id, autor=usuario) is None:
        raise _no_encontrada()
    background.add_task(manager.broadcast, "cambio")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{cirugia_id}/exportar", dependencies=[Depends(seguridad.editor)])
def exportar_cirugia(
    cirugia_id: int,
    formato: Literal["pdf", "xlsx"],
    db: Session = Depends(get_db),
) -> Response:
    cirugia = crud.obtenerRegistroCirugiaPorId(db, cirugia_id)
    if cirugia is None:
        raise _no_encontrada()
    return exports.respuesta_archivo(
        [cirugia], formato, f"Cirugía de {cirugia.nombrePaciente}", f"cirugia_{cirugia.id}"
    )
