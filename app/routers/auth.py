from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import seguridad
from app.database import get_db
from app.models import Usuario
from app.schemas import LoginIn, UsuarioOut

router = APIRouter(prefix="/auth", tags=["sesión"])


@router.post("/login", response_model=UsuarioOut)
def login(datos: LoginIn, response: Response, db: Session = Depends(get_db)) -> Usuario:
    usuario = seguridad.autenticar(db, datos.usuario, datos.password)
    if usuario is None:
        # Mismo mensaje para usuario inexistente, contraseña incorrecta o cuenta desactivada
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos")
    seguridad.abrir_sesion(response, usuario)
    return usuario


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def logout() -> Response:
    respuesta = Response(status_code=status.HTTP_204_NO_CONTENT)
    seguridad.cerrar_sesion(respuesta)
    return respuesta


@router.get("/yo", response_model=UsuarioOut)
def yo(usuario: Usuario = Depends(seguridad.usuario_actual)) -> Usuario:
    return usuario
