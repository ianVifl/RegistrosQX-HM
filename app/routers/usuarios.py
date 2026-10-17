from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import crud, seguridad
from app.database import get_db
from app.models import Usuario
from app.schemas import ActivoUpdate, PasswordUpdate, Rol, UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _obtener(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No se encontró el usuario")
    return usuario


def _no_a_si_mismo(objetivo: Usuario, admin: Usuario, mensaje: str) -> None:
    """Un admin no puede quitarse el rol ni desactivarse: el sistema nunca se queda sin administrador."""
    if objetivo.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, mensaje)


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(seguridad.solo_admin)) -> list[Usuario]:
    return crud.listarUsuarios(db)


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear(datos: UsuarioCreate, db: Session = Depends(get_db),
          admin: Usuario = Depends(seguridad.solo_admin)) -> Usuario:
    if crud.obtenerUsuarioPorNombre(db, datos.usuario):
        raise HTTPException(status.HTTP_409_CONFLICT, f"El usuario '{datos.usuario}' ya existe")
    return crud.crearUsuario(db, datos.usuario, datos.nombre, datos.rol, seguridad.hashear(datos.password), autor=admin)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def editar(usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db),
           admin: Usuario = Depends(seguridad.solo_admin)) -> Usuario:
    usuario = _obtener(db, usuario_id)
    if datos.rol != Rol.ADMIN.value:
        _no_a_si_mismo(usuario, admin, "No puedes quitarte el rol de administrador")
    return crud.actualizarUsuario(db, usuario, autor=admin, nombre=datos.nombre, rol=datos.rol)


@router.patch("/{usuario_id}/activo", response_model=UsuarioOut)
def cambiar_activo(usuario_id: int, datos: ActivoUpdate, db: Session = Depends(get_db),
                   admin: Usuario = Depends(seguridad.solo_admin)) -> Usuario:
    usuario = _obtener(db, usuario_id)
    if not datos.activo:
        _no_a_si_mismo(usuario, admin, "No puedes desactivar tu propia cuenta")
    accion = "ACTIVAR" if datos.activo else "DESACTIVAR"
    return crud.actualizarUsuario(db, usuario, autor=admin, accion=accion, activo=datos.activo)


@router.put("/{usuario_id}/password", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def restablecer_password(usuario_id: int, datos: PasswordUpdate, db: Session = Depends(get_db),
                         admin: Usuario = Depends(seguridad.solo_admin)) -> Response:
    usuario = _obtener(db, usuario_id)
    crud.actualizarUsuario(db, usuario, autor=admin, accion="RESTABLECER_PASSWORD",
                           passwordHash=seguridad.hashear(datos.password))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
