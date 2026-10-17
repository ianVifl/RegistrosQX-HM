from datetime import date, datetime, time, timedelta
from math import ceil

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app import bitacora, config
from app.bitacora import CAMPOS_CIRUGIA, CAMPOS_USUARIO
from app.models import Bitacora, Cirugia, Usuario


def paginar(consulta: Query, pagina: int, tamano: int) -> dict:
    """Una página de resultados más los datos para navegar: {items, total, pagina, tamano, paginas}."""
    total = consulta.order_by(None).count()
    items = consulta.offset((pagina - 1) * tamano).limit(tamano).all()
    return {"items": items, "total": total, "pagina": pagina, "tamano": tamano, "paginas": ceil(total / tamano)}


# ---------- Cirugías ----------

def crearRegistroCirugia(
    db: Session,
    nombrePaciente: str,
    edad: int,
    sexo: str,
    fechaCirugia: datetime,
    procedimiento: str,
    duracionEstimada: int,
    cirujano: str,
    quirofano: str,
    aseguradora: str | None,
    serviciosEspeciales: str | None,
    diagnostico: str | None,
    autor: Usuario | None = None,
) -> Cirugia:
    nueva_cirugia = Cirugia(
        nombrePaciente=nombrePaciente,
        edad=edad,
        sexo=sexo,
        fechaCirugia=fechaCirugia,
        procedimiento=procedimiento,
        duracionEstimada=duracionEstimada,
        cirujano=cirujano,
        estatus="PROGRAMADA",  # regla de negocio: todo alta nace programada
        quirofano=quirofano,
        aseguradora=aseguradora,
        serviciosEspeciales=serviciosEspeciales,
        diagnostico=diagnostico,
        creadoPorId=autor.id if autor else None,
    )
    db.add(nueva_cirugia)
    db.flush()  # asigna el id para la bitácora sin cerrar la transacción
    bitacora.registrar(db, autor, "CREAR", "CIRUGIA", nueva_cirugia.id,
                       bitacora.instantanea(nueva_cirugia, CAMPOS_CIRUGIA))
    db.commit()
    db.refresh(nueva_cirugia)
    return nueva_cirugia


def obtenerRegistroCirugiaPorId(db: Session, cirugia_id: int) -> Cirugia | None:
    return db.get(Cirugia, cirugia_id)


def obtenerCirugiasPorRango(db: Session, desde: date, hasta: date) -> list[Cirugia]:
    """Cirugías con fecha entre `desde` y `hasta`, ambos días incluidos."""
    inicio = datetime.combine(desde, time.min)
    fin = datetime.combine(hasta, time.min) + timedelta(days=1)
    return (
        db.query(Cirugia)
        .filter(Cirugia.fechaCirugia >= inicio, Cirugia.fechaCirugia < fin)
        .order_by(Cirugia.fechaCirugia.asc())
        .all()
    )


def obtenerCirugiasPorFecha(db: Session, fecha: date) -> list[Cirugia]:
    return obtenerCirugiasPorRango(db, fecha, fecha)


def buscarCirugias(db: Session, texto: str, pagina: int, tamano: int) -> dict:
    """Busca en todo el historial por nombre de paciente o de cirujano, de la más reciente a la más antigua.

    La collation utf8mb4_unicode_ci ignora mayúsculas y acentos: "lopez" encuentra "López".
    autoescape: un "%" o "_" tecleado se busca literal, no como comodín de LIKE.
    """
    consulta = (
        db.query(Cirugia)
        .filter(or_(
            Cirugia.nombrePaciente.contains(texto, autoescape=True),
            Cirugia.cirujano.contains(texto, autoescape=True),
        ))
        .order_by(Cirugia.fechaCirugia.desc(), Cirugia.id.desc())
    )
    return paginar(consulta, pagina, tamano)


def buscarTraslape(
    db: Session,
    quirofano: str,
    inicio: datetime,
    duracion: int,
    excluir_id: int | None = None,
) -> Cirugia | None:
    """Devuelve la cirugía que ocupa el quirófano en [inicio, inicio + duracion), si existe.

    Dos intervalos se traslapan si A.inicio < B.fin y A.fin > B.inicio. La duración máxima
    es 720 min, así que basta traer las que empezaron en las 24 h previas y comparar el fin
    en Python. Las FINALIZADAS no cuentan: el quirófano ya quedó libre.
    """
    fin = inicio + timedelta(minutes=duracion)
    consulta = db.query(Cirugia).filter(
        Cirugia.quirofano == quirofano,
        Cirugia.fechaCirugia < fin,
        Cirugia.fechaCirugia > inicio - timedelta(days=1),
        Cirugia.estatus != "FINALIZADA",
    )
    if excluir_id is not None:
        consulta = consulta.filter(Cirugia.id != excluir_id)
    for c in consulta.order_by(Cirugia.fechaCirugia):
        if c.fechaCirugia + timedelta(minutes=c.duracionEstimada) > inicio:
            return c
    return None


def modificarRegistroCirugia(
    db: Session,
    cirugia_id: int,
    nombrePaciente: str,
    edad: int,
    sexo: str,
    fechaCirugia: datetime,
    procedimiento: str,
    duracionEstimada: int,
    cirujano: str,
    estatus: str,
    quirofano: str,
    aseguradora: str | None,
    serviciosEspeciales: str | None,
    diagnostico: str | None,
    autor: Usuario | None = None,
) -> Cirugia | None:
    cirugia = db.get(Cirugia, cirugia_id)
    if cirugia:
        antes = bitacora.instantanea(cirugia, CAMPOS_CIRUGIA)
        cirugia.nombrePaciente = nombrePaciente
        cirugia.edad = edad
        cirugia.sexo = sexo
        cirugia.fechaCirugia = fechaCirugia
        cirugia.procedimiento = procedimiento
        cirugia.duracionEstimada = duracionEstimada
        cirugia.cirujano = cirujano
        cirugia.estatus = estatus
        cirugia.quirofano = quirofano
        cirugia.aseguradora = aseguradora
        cirugia.serviciosEspeciales = serviciosEspeciales
        cirugia.diagnostico = diagnostico
        cambios = bitacora.diferencias(antes, bitacora.instantanea(cirugia, CAMPOS_CIRUGIA))
        if cambios:  # guardar sin modificar nada no deja rastro
            _marcar_actualizacion(cirugia, autor)
            bitacora.registrar(db, autor, "EDITAR", "CIRUGIA", cirugia.id, cambios)
        db.commit()
        db.refresh(cirugia)
    return cirugia


def cambiarEstatusCirugia(db: Session, cirugia_id: int, estatus: str, autor: Usuario | None = None) -> Cirugia | None:
    cirugia = db.get(Cirugia, cirugia_id)
    if cirugia:
        _cambiar_estatus(db, cirugia, estatus, autor)
        db.commit()
        db.refresh(cirugia)
    return cirugia


def _cambiar_estatus(db: Session, cirugia: Cirugia, estatus: str, autor: Usuario | None) -> None:
    if cirugia.estatus == estatus:
        return
    bitacora.registrar(db, autor, "CAMBIAR_ESTATUS", "CIRUGIA", cirugia.id, {"estatus": [cirugia.estatus, estatus]})
    cirugia.estatus = estatus
    _marcar_actualizacion(cirugia, autor)


def _marcar_actualizacion(cirugia: Cirugia, autor: Usuario | None) -> None:
    cirugia.actualizadoEn = config.ahora()
    if autor:  # el scheduler no cuenta como "actualizado por" una persona
        cirugia.actualizadoPorId = autor.id


def activarProgramadas(db: Session, ahora: datetime) -> int:
    """PROGRAMADA -> EN PROGRESO para las de HOY cuya hora de inicio ya llegó.

    Se limita al día actual para no tocar registros viejos que nadie actualizó.
    Devuelve cuántas cambió.
    """
    pendientes = db.query(Cirugia).filter(
        Cirugia.estatus == "PROGRAMADA",
        Cirugia.fechaCirugia >= datetime.combine(ahora.date(), time.min),
        Cirugia.fechaCirugia <= ahora,
    ).all()
    for c in pendientes:
        _cambiar_estatus(db, c, "EN PROGRESO", autor=None)
    db.commit()
    return len(pendientes)


def finalizarVencidas(db: Session, ahora: datetime) -> int:
    """EN PROGRESO -> FINALIZADA cuando ya pasó inicio + duración estimada. Devuelve cuántas cambió."""
    en_curso = db.query(Cirugia).filter(
        Cirugia.estatus == "EN PROGRESO", Cirugia.fechaCirugia <= ahora
    ).all()
    cambiadas = 0
    for c in en_curso:
        if c.fechaCirugia + timedelta(minutes=c.duracionEstimada) <= ahora:
            _cambiar_estatus(db, c, "FINALIZADA", autor=None)
            cambiadas += 1
    db.commit()
    return cambiadas


def eliminarRegistroCirugia(db: Session, cirugia_id: int, autor: Usuario | None = None) -> Cirugia | None:
    cirugia = db.get(Cirugia, cirugia_id)
    if cirugia:
        # La bitácora guarda qué se borró: es la única copia que queda
        bitacora.registrar(db, autor, "ELIMINAR", "CIRUGIA", cirugia.id, bitacora.instantanea(cirugia, CAMPOS_CIRUGIA))
        db.delete(cirugia)
        db.commit()
    return cirugia


# ---------- Usuarios ----------

def listarUsuarios(db: Session) -> list[Usuario]:
    return db.query(Usuario).order_by(Usuario.activo.desc(), Usuario.nombre).all()


def obtenerUsuarioPorNombre(db: Session, usuario: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.usuario == usuario).first()


def crearUsuario(db: Session, usuario: str, nombre: str, rol: str, passwordHash: str, autor: Usuario) -> Usuario:
    ahora = config.ahora()
    nuevo = Usuario(usuario=usuario, nombre=nombre, rol=rol, passwordHash=passwordHash,
                    activo=True, creadoEn=ahora, actualizadoEn=ahora)
    db.add(nuevo)
    db.flush()
    bitacora.registrar(db, autor, "CREAR", "USUARIO", nuevo.id, bitacora.instantanea(nuevo, CAMPOS_USUARIO))
    db.commit()
    db.refresh(nuevo)
    return nuevo


def actualizarUsuario(db: Session, usuario: Usuario, autor: Usuario, accion: str = "EDITAR", **campos) -> Usuario:
    """Aplica `campos` y registra solo lo que cambió. `passwordHash` nunca se copia a la bitácora."""
    antes = bitacora.instantanea(usuario, CAMPOS_USUARIO)
    for campo, valor in campos.items():
        setattr(usuario, campo, valor)
    cambios = bitacora.diferencias(antes, bitacora.instantanea(usuario, CAMPOS_USUARIO))
    if cambios or "passwordHash" in campos:
        usuario.actualizadoEn = config.ahora()
        bitacora.registrar(db, autor, accion, "USUARIO", usuario.id, cambios)
    db.commit()
    db.refresh(usuario)
    return usuario


# ---------- Bitácora ----------

def consultarBitacora(db: Session, desde: date | None = None, hasta: date | None = None) -> Query:
    """Movimientos del más reciente al más antiguo; `desde`/`hasta` son opcionales (sin límite de rango)."""
    consulta = db.query(Bitacora)
    if desde:
        consulta = consulta.filter(Bitacora.fecha >= datetime.combine(desde, time.min))
    if hasta:
        consulta = consulta.filter(Bitacora.fecha < datetime.combine(hasta, time.min) + timedelta(days=1))
    return consulta.order_by(Bitacora.fecha.desc(), Bitacora.id.desc())
