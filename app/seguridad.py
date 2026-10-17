"""Contraseñas (Argon2), tokens de sesión (JWT en cookie HttpOnly) y control de acceso por rol."""
from datetime import timedelta

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.models import Usuario
from app.schemas import Rol

COOKIE = "sesion"
ALGORITMO = "HS256"
DURACION_SESION = {
    Rol.ADMIN.value: timedelta(hours=12),
    Rol.CAPTURISTA.value: timedelta(hours=24),
    Rol.VISUALIZADOR.value: timedelta(days=30),
}

_hasher = PasswordHash.recommended()
# Si el usuario no existe se verifica contra este hash de todos modos: así la respuesta tarda lo mismo
# y no se puede averiguar qué usuarios existen midiendo el tiempo.
_HASH_SENUELO = _hasher.hash("contraseña-señuelo")


def hashear(password: str) -> str:
    return _hasher.hash(password)


def autenticar(db: Session, usuario: str, password: str) -> Usuario | None:
    u = db.query(Usuario).filter(Usuario.usuario == usuario).first()
    valida = _hasher.verify(password, u.passwordHash if u else _HASH_SENUELO)
    return u if u and valida and u.activo else None


def abrir_sesion(response: Response, usuario: Usuario) -> None:
    duracion = DURACION_SESION[usuario.rol]
    token = jwt.encode(
        {"sub": str(usuario.id), "exp": config.ahora_utc() + duracion},
        config.SECRET_KEY, algorithm=ALGORITMO,
    )
    response.set_cookie(
        COOKIE, token, max_age=int(duracion.total_seconds()),
        httponly=True, samesite="lax", secure=config.COOKIE_SECURE,
    )


def cerrar_sesion(response: Response) -> None:
    response.delete_cookie(COOKIE, httponly=True, samesite="lax", secure=config.COOKIE_SECURE)


def usuario_de_token(db: Session, token: str | None) -> Usuario | None:
    """Usuario activo dueño del token, o None si falta, expiró, está alterado o el usuario fue desactivado.

    El rol se lee de la BD en cada request (no del token): un cambio de rol o una desactivación
    aplican de inmediato, sin esperar a que el token expire.
    """
    if not token:
        return None
    try:
        datos = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITMO], options={"require": ["exp", "sub"]})
        usuario_id = int(datos["sub"])
    except (jwt.InvalidTokenError, ValueError):  # expirado, firma inválida, claims faltantes o sub no numérico
        return None
    u = db.get(Usuario, usuario_id)
    return u if u and u.activo else None


def usuario_actual(request: Request, db: Session = Depends(get_db)) -> Usuario:
    u = usuario_de_token(db, request.cookies.get(COOKIE))
    if u is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión no válida o expirada")
    return u


def requiere(*roles: Rol):
    """Dependencia: deja pasar solo a los roles indicados (401 sin sesión, 403 con otro rol)."""
    permitidos = {r.value for r in roles}

    def _verificar(u: Usuario = Depends(usuario_actual)) -> Usuario:
        if u.rol not in permitidos:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta acción")
        return u

    return _verificar


# Atajos para los routers
cualquier_rol = usuario_actual
editor = requiere(Rol.ADMIN, Rol.CAPTURISTA)
solo_admin = requiere(Rol.ADMIN)
