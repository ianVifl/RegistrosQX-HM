"""Registro de movimientos. `registrar` no hace commit: el registro se guarda en la misma
transacción que el cambio, así nunca existe un cambio sin bitácora (ni una bitácora sin cambio)."""
from datetime import date, datetime

from sqlalchemy.orm import Session

from app import config
from app.models import Bitacora, Usuario

SISTEMA = "SISTEMA"

CAMPOS_CIRUGIA = [
    "nombrePaciente", "edad", "sexo", "fechaCirugia", "procedimiento", "duracionEstimada",
    "cirujano", "quirofano", "estatus", "aseguradora", "diagnostico", "serviciosEspeciales",
]
CAMPOS_USUARIO = ["usuario", "nombre", "rol", "activo"]

ETIQUETAS = {
    "nombrePaciente": "Paciente", "edad": "Edad", "sexo": "Sexo", "fechaCirugia": "Fecha",
    "procedimiento": "Procedimiento", "duracionEstimada": "Duración (min)", "cirujano": "Cirujano",
    "quirofano": "Quirófano", "estatus": "Estatus", "aseguradora": "Aseguradora",
    "diagnostico": "Diagnóstico", "serviciosEspeciales": "Servicios especiales",
    "usuario": "Usuario", "nombre": "Nombre", "rol": "Rol", "activo": "Activo",
}


def _json(valor):
    return valor.isoformat() if isinstance(valor, (datetime, date)) else valor


def instantanea(obj, campos: list[str]) -> dict:
    return {c: _json(getattr(obj, c)) for c in campos}


def diferencias(antes: dict, despues: dict) -> dict:
    """{campo: [antes, después]} solo de los campos que cambiaron."""
    return {c: [antes[c], v] for c, v in despues.items() if antes.get(c) != v}


def registrar(db: Session, autor: Usuario | None, accion: str, entidad: str,
              entidad_id: int | None, detalle: dict | None = None) -> None:
    """`autor` None = cambio automático del sistema (scheduler)."""
    db.add(Bitacora(
        fecha=config.ahora(),
        usuarioId=autor.id if autor else None,
        usuarioNombre=autor.nombre if autor else "Sistema",
        usuarioRol=autor.rol if autor else SISTEMA,
        accion=accion, entidad=entidad, entidadId=entidad_id, detalle=detalle or None,
    ))


def autor(b: Bitacora) -> str:
    """"capturista:Andrea_Villanueva", o "sistema" para el scheduler."""
    if b.usuarioRol == SISTEMA:
        return "sistema"
    return f"{b.usuarioRol.lower()}:{b.usuarioNombre.replace(' ', '_')}"


_ORDEN = {campo: i for i, campo in enumerate(CAMPOS_CIRUGIA + CAMPOS_USUARIO)}


def resumen(b: Bitacora) -> str:
    """Texto legible del detalle, para la pantalla y los reportes.

    MySQL reordena las llaves de las columnas JSON al guardarlas, así que se reordenan aquí.
    """
    if not b.detalle:
        return ""
    partes = []
    for campo, valor in sorted(b.detalle.items(), key=lambda kv: _ORDEN.get(kv[0], len(_ORDEN))):
        etiqueta = ETIQUETAS.get(campo, campo)
        if isinstance(valor, list) and len(valor) == 2:  # [antes, después]
            partes.append(f"{etiqueta}: {_texto(valor[0])} → {_texto(valor[1])}")
        elif valor not in (None, ""):
            partes.append(f"{etiqueta}: {_texto(valor)}")
    return "; ".join(partes)


def _texto(valor) -> str:
    if valor is None or valor == "":
        return "(vacío)"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, str) and len(valor) == 19 and valor[10] == "T":  # fecha ISO de instantanea()
        try:
            return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
        except ValueError:
            pass
    return str(valor)
