"""Crea un usuario administrador desde la terminal.

    python -m app.crear_admin
    docker compose run --rm api python -m app.crear_admin    (en el servidor)

No existe un admin por defecto: así no hay una contraseña conocida que alguien olvide cambiar.
"""
import sys
from getpass import getpass

from pydantic import ValidationError

from app import config, seguridad
from app.database import SessionLocal
from app.models import Usuario
from app.schemas import Rol, UsuarioCreate


def main() -> int:
    usuario = input("Usuario (para iniciar sesión): ").strip()
    nombre = input("Nombre completo: ").strip()
    password = getpass("Contraseña (mínimo 8 caracteres): ")
    if getpass("Repite la contraseña: ") != password:
        print("Las contraseñas no coinciden.", file=sys.stderr)
        return 1
    try:
        datos = UsuarioCreate(usuario=usuario, nombre=nombre, rol=Rol.ADMIN, password=password)
    except ValidationError as e:
        for error in e.errors():
            print(f"{error['loc'][-1]}: {error['msg']}", file=sys.stderr)
        return 1

    with SessionLocal() as db:
        if db.query(Usuario).filter(Usuario.usuario == datos.usuario).first():
            print(f"El usuario '{datos.usuario}' ya existe.", file=sys.stderr)
            return 1
        ahora = config.ahora()
        db.add(Usuario(
            usuario=datos.usuario, nombre=datos.nombre, rol=datos.rol,
            passwordHash=seguridad.hashear(datos.password), creadoEn=ahora, actualizadoEn=ahora,
        ))
        db.commit()
    print(f"Administrador '{datos.usuario}' creado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
